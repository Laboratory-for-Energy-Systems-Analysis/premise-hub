"""Recalculate MCV's slide data from the vintage-enabled PkBudg1000 archive."""

import argparse
import csv
from datetime import datetime, timezone
import gzip
from importlib import import_module
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from apps.mcv_2026.scripts.cohort_timing import apply_cohort_timing, extend_inventory_calendar
from apps.mcv_2026.scripts.compare_vintages import RoutingQueue, construction_routes
from apps.setac_2026.scripts.regenerate_results import sha256


def physical_branch_queue(case, model, year, config, depths):
    label = str(model._map_year_to_template_year(year))
    split = config["beccs"]
    split_names = {
        split["removal_service"]["greenfield_operation_name"],
        split["capture_module"]["generated_name"],
    }
    split_roots = {
        index for index, item in model.activity_indices[label].items()
        if item["name"] in split_names
    }

    class BranchQueue(RoutingQueue):
        def append(self, item):
            date, activity, amount, depth, root, dated = item
            # Carry the branch before paths merge or signed demands cancel.
            if (case == "DACCS" and depth in {2, 3}) or (
                case == "BECCS" and depth == 2 and root in split_roots
            ):
                root = activity
                depths.setdefault(root, depth)
            elif depth == 1:
                depths.setdefault(activity, 1)
            super().append((date, activity, amount, depth, root, dated))

    return BranchQueue


def energy_rows(model, case, temporal, denominator):
    import numpy as np
    from trails.characterization import _build_cf_matrix_flowid_space
    from trails.fair_rf import _inventory_flow_year_root
    from apps.setac_2026.figures import BECCS_TEMPORAL_GROUPS, DACCS_TEMPORAL_PRODUCTS

    cf = _build_cf_matrix_flowid_space(model, [temporal.METHOD], "3.12", {})[0]
    inventory = model.inventory
    data = _inventory_flow_year_root(
        inventory, flow_positions=np.flatnonzero(cf).tolist(),
        builder=getattr(model, "_inventory_builder", None), show_progress=False,
    ).asformat("coo")
    roots = inventory.coords["root activity"].values
    years = inventory.coords["year"].values
    activities = temporal.activity_metadata(model, temporal.START_YEAR)
    rows = []
    for f, y, r, amount in zip(*data.coords, data.data, strict=True):
        root = int(roots[r])
        metadata = activities[root]
        if case == "BECCS":
            name = temporal.beccs_temporal_category(metadata)
            group = BECCS_TEMPORAL_GROUPS[name]
        else:
            name = metadata["reference product"]
            group = DACCS_TEMPORAL_PRODUCTS.get(name)
        value = float(amount * cf[f] / denominator)
        if group == "Energy" and abs(value) >= 1e-12:
            rows.append(dict(case=case, impact_year=int(years[y]),
                             root_activity_index=root, root=name,
                             sign=1 if value > 0 else -1,
                             score_per_net_tonne_kg_co2eq=value))
    return rows


def write_routes(path, model, case, provenance):
    graph = model.graph
    ids = {node: i for i, node in enumerate(graph.nodes)}
    nodes = [
        dict(id=ids[node], depth=int(item["depth"]), year=int(item["year"]),
             name=item["name"], product=item["reference_product"],
             location=item["location"], unit=item.get("unit", ""))
        for node, item in graph.nodes(data=True)
    ]
    edges = [
        dict(source=ids[u], target=ids[v], negative=edge["amount"] < 0)
        for u, v, edge in graph.edges(data=True) if edge["amount"]
    ]
    payload = dict(metadata=dict(
        **provenance, case=case.lower(), functional_unit="1 t CO2 physically stored",
        routing=dict(max_depth=4), nodes=len(nodes), edges=len(edges),
        years=[min(item["year"] for item in nodes), max(item["year"] for item in nodes)],
        depth_counts={str(i): sum(item["depth"] == i for item in nodes) for i in range(5)},
        scenario="REMIND-EU SSP2-PkBudg1000",
    ), nodes=nodes, edges=edges)
    path.write_bytes(gzip.compress(json.dumps(payload, separators=(",", ":")).encode(), mtime=0))


def run(workspace, package, case):
    sys.path.insert(0, str(workspace))
    from datapackage import Package
    from trails import Trails
    from trails.fair_io import load_species_mapping
    from trails.fair_rf import _inventory_delta_by_fair_species_for_trails
    from scripts import calculate_cohort_temporal_scores as temporal
    from scripts import generate_routing_graphs as routing
    from workshop.lifetime import cohort_cases
    from workshop.temporal import enable_signed_technosphere_routing

    config_path = workspace / "data/inventories/parameters.json"
    config = json.loads(config_path.read_text())
    foreground = config_path.parent / "generated/lcss2026-foreground.xlsx"
    cohort = foreground.with_name("lcss2026-routing-cohorts.xlsx")
    output = workspace / "data/processed"
    year = temporal.START_YEAR
    denominator = cohort_cases(config, commissioning_year=year)[case].lifetime_net_stored_kg / 1000
    provenance = dict(package_sha256=sha256(package), foreground_sha256=sha256(foreground),
                      cohort_foreground_sha256=sha256(cohort))
    with Trails(Package(str(package)), interpolate_annual=True, cache_interpolation=False,
                interpolation_start_year_offset=0, interpolation_end_year_offset=0,
                ei_version="3.12") as model:
        model.import_excel_inventory([foreground, cohort])
        assert not model.import_diagnostics.get("unlinked")
        assert not model.import_diagnostics.get("new_flows")
        extend_inventory_calendar(model, 1880, model.max_year + routing.TECHNOSPHERE_END_YEAR_OFFSETS[case])
        apply_cohort_timing(model, case, year, config, routing)
        enable_signed_technosphere_routing(model)
        depths = {}
        with patch.object(import_module("trails.trails"), "deque",
                          physical_branch_queue(case, model, year, config, depths)):
            model.temporal_routing(start_year=year,
                                   start_act_idx=routing.find_activity(model, year, routing.ROOTS[case]),
                                   amount=routing.cohort_root_amount(case, config, year),
                                   max_depth=4, adaptive_relative_score_cutoff=None,
                                   min_amount=0.0, attribute_to_roots=True, show_progress=False)
        print(f"{case} IAM-dated edges: {construction_routes(model)['edges']}", flush=True)
        write_routes(output / f"{case.lower()}-routing.json.gz", model, case, provenance)
        model.lci(show_progress=True, attribute_to_roots=True, solver_mode="iterative",
                  iterative_rtol=1e-5, iterative_maxiter=500, inventory_backend="factorized")
        model.lcia(methods=[temporal.METHOD], ei_version="3.12")
        rows = temporal.root_score_rows(model, case=case, denominator_tonnes=denominator,
                                        provenance=provenance, root_depths=depths, config=config)
        temporal.write_csv(output / f"temporal-{case}.csv", rows)
        energy = energy_rows(model, case, temporal, denominator)
        with (output / f"energy-{case}.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(energy[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(energy)
        mapping, signs = load_species_mapping()
        delta, _ = _inventory_delta_by_fair_species_for_trails(model, mapping, signs, show_progress=False)
        species = output / f"fair-species-{case}.csv"
        delta.to_csv(species)
        species.with_suffix(".json").write_text(json.dumps(dict(
            **provenance, config_sha256=sha256(config_path), csv_sha256=sha256(species),
            denominator_net_stored_tonnes=denominator), indent=2) + "\n")
        print(f"Saved timing, energy and FaIR species for {case}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--case", choices=("BECCS", "DACCS"), required=True)
    args = parser.parse_args()
    run(args.workspace.resolve(), args.package.resolve(), args.case)


if __name__ == "__main__":
    main()
