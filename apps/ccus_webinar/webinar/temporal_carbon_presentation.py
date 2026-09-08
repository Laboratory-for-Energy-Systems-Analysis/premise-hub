"""Zero-sum temporal display decomposition; never modifies stored LCIA results."""
import json
from pathlib import Path
from math import isclose
from ..lca_model.results import file_sha256

def split_carbon(by_contributor, *, system, grouping, factor, payload):
    """CO₂ CF=1 in the selected IPCC GWP100 incl. non-fossil CO₂ method.

    Remove uncaptured kiln CO₂ from its parent, show gross and subtract capture.
    Move existing releases out of parents, not add a second release or uptake.
    All quantities use the original uniform one-thirtieth cohort normalization.
    """
    before = {y:sum(v.get(y,0) for v in by_contributor.values())
        for values in by_contributor.values() for y in values}
    def add(label,year,value):
        values=by_contributor.setdefault(label,{})
        values[year]=values.get(year,0)+value
    for row in payload['rows']:
        if row['system']!=system:
            continue
        for origin in ('fossil','non_fossil'):
            flow='Carbon dioxide, '+origin.replace('_','-')
            parent='clinker' if grouping=='stage' else flow
            gross=row['kiln_gross_'+origin]/30*factor
            captured=gross*row['capture_efficiency']
            year=row['year']
            add(parent,year,-(gross-captured))
            add('Kiln CO₂ · '+origin.replace('_','-'),year,gross)
            add('Captured CO₂ · '+origin.replace('_','-'),year,-captured)
    for row in payload['releases']:
        if row['system']!=system:
            continue
        parent=row['stage'] if grouping=='stage' else row['flow']
        add(parent,row['year'],-row['score']*factor)
        add(row['label'],row['year'],row['score']*factor)
    years=set(before)|{y for values in by_contributor.values() for y in values}
    for year in years:
        assert isclose(before.get(year,0),sum(v.get(year,0) for v in by_contributor.values()),abs_tol=1e-7,rel_tol=1e-10), 'Carbon display changed an annual total'
    return by_contributor

def load_carbon_display(bundle):
    if bundle.approved:
        # Public results never load private physical inventory exports, even
        # when a developer's local calculation files happen to be present.
        return None
    if not bundle.payloads.get('temporal_diagnostic_manifest'):
        return None
    folder=Path(__file__).resolve().parents[1]/'generated/results/temporal_diagnostic'
    if not (folder/'manifest.json').is_file() or not (folder/'physical_flows.json').is_file():
        return None  # Optional visual decomposition may still be rebuilding.
    manifest=json.loads((folder/'manifest.json').read_text())
    if bundle.payloads['temporal_diagnostic_manifest'].get('run_id') != manifest['run_id']:
        return None
    path=folder/'physical_flows.json'
    if file_sha256(path)!=path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Changed carbon display export')
    payload=json.loads(path.read_text())
    if payload['source_manifest_sha256']!=file_sha256(folder/'manifest.json'):
        raise ValueError('Carbon display does not match temporal results')
    return payload
