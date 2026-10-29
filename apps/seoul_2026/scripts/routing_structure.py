"""Consolidate redundant foreground services before running temporal routing.

Only zero-lag service links are inlined. Dated supplier profiles and matrix/port
semantics are retained; this never moves an operating pulse to commissioning.
Scientific dependencies are imported only by the offline export script.
"""

from collections import defaultdict
import math


def _profile_key(model, profile):
    if profile is None:
        return ("instant",)
    offsets = tuple(model._get_td_offsets(tex=profile, debug=False))
    if offsets == ((0, 1.0),):
        return ("instant",)
    return (str(profile.amount_source), offsets)


def _row(matrix, act):
    row = matrix[:, act, :]
    return {(int(t), int(j)): float(v) for t,j,v in zip(*row.coords, row.data)}


def boundary_demands(graph, root, inlined):
    """Demands crossing from a zero-lag service tree into retained activities."""
    roots = [n for n,d in graph.nodes(data=True) if int(d["depth"]) == 0]
    assert len(roots) == 1
    result = defaultdict(float)
    stack, visited = roots[:], set()
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for _,child,edge in graph.out_edges(node, data=True):
            meta = graph.nodes[child]
            if int(meta["act_idx"]) in inlined:
                assert int(meta["year"]) == int(graph.nodes[roots[0]]["year"])
                stack.append(child)
            else:
                result[(int(meta["year"]), int(meta["act_idx"]))] += float(edge["amount"])
    return dict(result)


def compare_boundaries(expected, actual):
    keys = set(expected) | set(actual)
    errors = [abs(expected.get(k,0)-actual.get(k,0)) for k in keys]
    for key in keys:
        assert math.isclose(expected.get(key,0), actual.get(key,0), rel_tol=1e-10, abs_tol=1e-10), (
            "Dated supplier demand changed", key, expected.get(key,0), actual.get(key,0))
    return dict(dated_supplier_demands=len(keys), max_absolute_numerical_difference=max(errors, default=0),
                dated_supplier_demands_equivalent=True)


def consolidate_root(model, *, root, year, amount, inlined, name, helpers):
    """Inline zero-lag services and normalize the integrated root to kg stored.

    An inlined service is called at the root year. Its coefficient at that
    anchor is therefore fixed, while a leaf marked ``matrix`` retains the
    original caller's complete annual coefficient series.
    """
    import numpy as np
    import sparse

    t0 = int(model.scenario_index[str(year)])
    root_scale = float(amount) / 1000
    components = []
    a_rows, b_rows = {}, {}

    def rows(act):
        if act not in a_rows:
            a_rows[act], b_rows[act] = _row(model.A, act), _row(model.B, act)
        return a_rows[act], b_rows[act]

    def expand(act, factor, trail):
        assert act not in trail, "Cyclic foreground service"
        a,b = rows(act)
        production = a.get((t0,act),0)
        assert production > 0, "Foreground service needs positive reference production"
        factor /= production
        components.append((act, factor))
        for (t,child),v in a.items():
            if t != t0 or child == act or child not in inlined:
                continue
            profile = model._get_tech_temporal_exchange(year, act, child)
            assert _profile_key(model, profile) == ("instant",), "Cannot inline a time-shifted service"
            expand(child, factor * -v, trail | {act})

    expand(root, root_scale, set())
    new_a, new_b = defaultdict(float), defaultdict(float)
    a_profiles, b_profiles = {}, {}

    def collect(target, profiles, values, act, factor, biosphere):
        for (t,j),v in values.items():
            if not biosphere and (j == act or j in inlined):
                continue
            profile = (model._get_bio_temporal_exchange(year,act,j) if biosphere
                       else model._get_tech_temporal_exchange(year,act,j))
            key = _profile_key(model, profile)
            if j in profiles:
                assert profiles[j][0] == key, ("Different temporal profiles need separate services", act,j)
            else:
                profiles[j] = (key,profile)
            target[(t,j)] += factor*v

    for act,factor in components:
        collect(new_a,a_profiles,a_rows[act],act,factor,False)
        collect(new_b,b_profiles,b_rows[act],act,factor,True)
    for t in range(model.A.shape[0]):
        new_a[(t,root)] = 1

    # Cement's elementary-flow carriers are software encodings of direct
    # emissions, not physical supply activities. Fold only instantaneous,
    # biosphere-only carriers whose profiles match the owning annual stage.
    carrier_edges, extra_b = set(), defaultdict(float)
    carrier_count = 0
    metadata = model.activity_indices[str(model._map_year_to_template_year(year))]
    stage_ids = [int(i) for i,m in metadata.items()
        if str(m.get("name","")).startswith("ccus | ")
        and any(f"| {s} |" in str(m.get("name","")) for s in ("BAU","CCS"))
        and str(m.get("name","")).split(" | ")[-1].isdigit()]
    for stage in stage_ids:
        stage_year = int(metadata[stage]["name"].split(" | ")[-1])
        sa,sb = rows(stage)
        children = {j for _,j in sa if j != stage and metadata.get(j,{}).get("reference product") == "dated elementary flow service"}
        for child in children:
            if _profile_key(model,model._get_tech_temporal_exchange(stage_year,stage,child)) != ("instant",):
                continue
            ca,cb = rows(child)
            if any(j != child and v for (_,j),v in ca.items()):
                continue
            flows = {j for _,j in cb}
            if any(_profile_key(model,model._get_bio_temporal_exchange(stage_year,child,f)) !=
                   _profile_key(model,model._get_bio_temporal_exchange(stage_year,stage,f)) for f in flows):
                continue
            for (t,f),v in cb.items():
                assert math.isclose(ca.get((t,child),0),1)
                extra_b[(t,stage,f)] += -sa.get((t,child),0)*v
            carrier_edges.add((stage,child))
            carrier_count += 1

    a = model.A
    keep = a.coords[1] != root
    if carrier_edges:
        width = int(a.shape[2])
        pairs = np.array([s*width+c for s,c in carrier_edges], dtype=np.int64)
        keep &= ~np.isin(a.coords[1].astype(np.int64)*width+a.coords[2], pairs)
    a_coords = [(t,root,j) for (t,j),v in new_a.items() if v]
    a_data = [v for v in new_a.values() if v]
    model.A = sparse.COO(np.concatenate([a.coords[:,keep],np.array(a_coords,dtype=a.coords.dtype).T],axis=1),
                         np.concatenate([a.data[keep],np.array(a_data)]),shape=a.shape)
    b = model.B
    b_coords = [(t,root,j) for (t,j),v in new_b.items() if v] + [k for k,v in extra_b.items() if v]
    b_data = [v for v in new_b.values() if v] + [v for v in extra_b.values() if v]
    keep = b.coords[1] != root
    if b_coords:
        model.B = sparse.COO(np.concatenate([b.coords[:,keep],np.array(b_coords,dtype=b.coords.dtype).T],axis=1),
                             np.concatenate([b.data[keep],np.array(b_data)]),shape=b.shape)
    else:
        model.B = sparse.COO(b.coords[:,keep],b.data[keep],shape=b.shape)

    for attr,profiles in (("temporal_technosphere_exchanges",a_profiles),("temporal_biosphere_exchanges",b_profiles)):
        mapping = getattr(model,attr)
        for k in list(mapping):
            if k[1] == root:
                del mapping[k]
        for label in model.template_labels:
            for j,(_,profile) in profiles.items():
                if profile is not None:
                    mapping[(str(label),root,j)] = profile
    # All template metadata maps must describe the integrated stored-CO2 unit.
    for mapping in model.activity_indices.values():
        mapping[root] = {**mapping[root],"name":name,"reference product":"carbon dioxide, captured and permanently stored","unit":"kilogram"}
    for cache_name in ("_A_row_cache","_tech_td_cache","_tech_td_expanded_cache","_tech_expansion_template_cache",
                       "_production_amount_cache","_production_amount_vector_cache","_direct_bio_cache_by_year",
                       "_B_csr_cache","_B_row_cache","_B_row_index_map"):
        cache = getattr(model,cache_name,None)
        if hasattr(cache,"clear"):
            cache.clear()

    # Check the inserted root against the compiled dated series and direct
    # biosphere coefficients, without solving or densifying the background.
    actual_a,actual_b = _row(model.A,root),_row(model.B,root)
    for expected,actual in ((new_a,actual_a),(new_b,actual_b)):
        for k in set(expected)|set(actual):
            assert math.isclose(expected.get(k,0),actual.get(k,0),rel_tol=1e-12,abs_tol=1e-12)
    for stage in {s for s,_ in carrier_edges}:
        expected = dict(b_rows[stage])
        for (t,s,f),v in extra_b.items():
            if s == stage:
                expected[(t,f)] = expected.get((t,f),0)+v
        actual = _row(model.B,stage)
        for k in set(expected)|set(actual):
            assert math.isclose(expected.get(k,0),actual.get(k,0),rel_tol=1e-12,abs_tol=1e-12)
    identity = dict(name=name,**{"reference product":"carbon dioxide, captured and permanently stored"},location=metadata[root]["location"])
    return identity,dict(inlined_services=len(components)-1,root_normalized_kg_stored=True,
        root_amount=1000,instantaneous_emission_carriers_folded=carrier_count,
        annual_root_coefficients_checked=True,direct_biosphere_profiles_preserved=True,
        emission_carrier_biosphere_equivalent=True)
