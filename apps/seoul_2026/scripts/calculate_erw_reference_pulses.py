"""Generate aggregate CO2 reference curves under the reviewed ERW FaIR background.

Run with the TRAILS scientific environment. No inventories or project results
are changed. Checkpoint each pulse year so interrupted runs can be resumed.
"""

import argparse
from datetime import datetime, timezone
import gc
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import time

import numpy as np
import trails
from trails.fair_io import (
    DEFAULT_CONFIGS_CSV, DEFAULT_EMISSIONS_CSV, DEFAULT_MAPPING_YAML,
    DEFAULT_PROPERTIES_CSV, load_emissions_csv,
)
from trails.fair_rf import (
    _all_config_names_from_csv, _run_fair_emissions, _total_response_by_config,
    make_reference_co2_pulse_emissions,
)

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = "REMIND|SSP2-EU21-PkBudg1000"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/erw_reference_pulses.json")
    parser.add_argument("--years", type=int, nargs="+", default=list(range(2005, 2200, 5)))
    args = parser.parse_args()
    reviewed = json.loads((ROOT / "data/erw_campaign.json").read_text())
    inputs = {"emissions_csv": DEFAULT_EMISSIONS_CSV, "mapping_yaml": DEFAULT_MAPPING_YAML,
              "config_csv": DEFAULT_CONFIGS_CSV, "properties_csv": DEFAULT_PROPERTIES_CSV}
    hashes = {k: hashlib.sha256(Path(v).read_bytes()).hexdigest() for k,v in inputs.items()}
    if hashes != reviewed["fair_input_hashes"] or trails.__version__ != reviewed["trails"]:
        raise ValueError("FaIR inputs/version differ from the reviewed ERW campaign")
    settings = dict(config_csv=DEFAULT_CONFIGS_CSV, properties_csv=DEFAULT_PROPERTIES_CSV,
                    config_names=_all_config_names_from_csv(DEFAULT_CONFIGS_CSV, None, None),
                    ghg_method="myhre1998", temperature_prescribed=False, progress=False)
    record = dict(schema_version=1, scenario=SCENARIO, trails_version=trails.__version__,
                  trails_source=str(trails.__file__), fair_version=version("fair"),
                  fair_input_hashes=hashes, reference_run_mass_kg=1e9,
                  config_count=len(settings["config_names"]),
                  ghg_method="myhre1998", temperature_prescribed=False,
                  unit="W/m² per kg CO2 pulse", summary="pointwise median of marginal reference response",
                  project_results_unchanged=True, pulses={})
    if args.output.exists():
        old = json.loads(args.output.read_text())
        if any(old.get(k) != record[k] for k in ("scenario", "fair_input_hashes", "config_count")):
            raise ValueError("Checkpoint has incompatible inputs")
        record["pulses"] = old["pulses"]
    pending = [y for y in args.years if str(y) not in record["pulses"]]
    if not pending:
        print("All requested pulse years already exist", flush=True)
        return
    started = time.monotonic()
    emissions = load_emissions_csv()
    base_model = _run_fair_emissions(emissions, SCENARIO, **settings)
    base = _total_response_by_config(base_model.forcing, scenario=SCENARIO, sum_species=True)
    years = np.asarray(base.coords["timebounds"].values, dtype=float)
    baseline = np.asarray(base.values).copy()
    keep = (years >= 1995) & (years <= 2201)
    del base_model, base
    gc.collect()
    print(f"Baseline ready: {len(settings['config_names'])} configs, {time.monotonic()-started:.1f}s", flush=True)
    for pulse_year in pending:
        perturbed = make_reference_co2_pulse_emissions(
            emissions, scenario=SCENARIO, pulse_year=pulse_year, pulse_mass_kg=1e9)
        model = _run_fair_emissions(perturbed, SCENARIO, **settings)
        response = _total_response_by_config(model.forcing, scenario=SCENARIO, sum_species=True)
        if not np.array_equal(response.coords["timebounds"].values, years):
            raise ValueError("Reference time coordinates changed")
        delta = np.median((np.asarray(response.values)-baseline)/1e9, axis=0)
        record["pulses"][str(pulse_year)] = [[float(y),float(v)] for y,v in zip(years[keep],delta[keep])]
        record["calculated_at"] = datetime.now(timezone.utc).isoformat()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, separators=(",", ":"))+"\n")
        del model, response, delta
        gc.collect()
        print(f"Pulse {pulse_year}: {len(record['pulses'])} saved, {time.monotonic()-started:.1f}s elapsed", flush=True)


if __name__ == "__main__":
    main()
