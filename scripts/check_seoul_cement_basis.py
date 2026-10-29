"""Check the stored-tonne conversion against local reviewed physical evidence.

The private source artifacts are needed only to reproduce this check. Runtime
ships the derived scalar factors and hash-locked public results, not inventories.
Run from the repository root: venv/bin/python scripts/check_seoul_cement_basis.py
"""

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps/ccus_webinar"
basis = json.loads((ROOT / "apps/seoul_2026/data/cement_storage_basis.json").read_text())
manifest_path = SOURCE / "generated/releases/webinar-2026-09-08/manifest.json"
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == basis["source_manifest_sha256"]
review = json.loads(manifest_path.read_text())
for name, digest in basis["evidence_sha256"].items():
    assert review["evidence_hashes"][name] == digest, name
    assert hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == digest, name

inventory = json.loads((SOURCE / "generated/inventories/mtx_gas_heat_candidate/inventory_manifest_candidate.json").read_text())
heat = inventory["engineering_checks"]["ssp2-npi-ccs-2025"]["heat"]
assert heat["boiler_carbon_routing_integrated"]
retention = (1 - .05) * (1 - .0144)
current_stored_kg = heat["captured_throughput_t"] * 1000 * retention
assert math.isclose(basis["static_clinker_t_per_t_stored"]["2025"], 1000 / current_stored_kg, rel_tol=1e-12)

physical = json.loads((SOURCE / "generated/results/temporal_diagnostic/physical_flows.json").read_text())
assert physical["source_manifest_sha256"] == basis["evidence_sha256"]["generated/results/temporal_diagnostic/manifest.json"]
rows = [r for r in physical["rows"] if r["system"] == "CCS"]
assert [r["year"] for r in rows] == list(range(2035, 2065))
for row in rows:
    for part in row["routes"]:
        assert math.isclose(part["captured_co2_kg"] * retention, part["stored_co2_kg"], abs_tol=1e-8)
        assert math.isclose(part["gross_co2_kg"], part["uncaptured_co2_kg"] + part["storage_loss_co2_kg"] + part["stored_co2_kg"], abs_tol=1e-8)

def storage(row):
    return sum(part["stored_co2_kg"] for part in row["routes"])

for year in (2035, 2050):
    denominator = storage(next(row for row in rows if row["year"] == year))
    assert math.isclose(basis["static_clinker_t_per_t_stored"][str(year)], 1000 / denominator, rel_tol=1e-12)
campaign_mean_kg = sum(map(storage, rows)) / len(rows)
assert math.isclose(basis["campaign_clinker_t_per_t_stored"], 1000 / campaign_mean_kg, rel_tol=1e-12)
print("Cement basis verified: matching static storage, full 30-year campaign, physical carbon closure and reviewed evidence hashes.")
