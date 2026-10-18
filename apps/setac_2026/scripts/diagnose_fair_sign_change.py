"""Isolate the effect of TRAILS' September 2026 signed-uptake correction.

Diagnostic only: run the new inventory with the former uptake-sign mapping in
a separate process. Never use this output as the presentation's result data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    sys.path.insert(0, str(workspace))
    import numpy as np
    import trails.fair_rf as fair_rf
    from scripts import validate_cohort_pulse_equivalence as validation

    # Reproduce only the pre-de32b19 inventory aggregation behavior. All other
    # inputs and FaIR settings remain those of the regenerated calculation.
    def legacy_mapping(values, direction_factors):
        values = np.asarray(values, dtype=float)
        directions = np.asarray(direction_factors, dtype=float)
        return np.where(directions == 1.0, values, np.abs(values) * directions)

    fair_rf._as_atmospheric_emissions = legacy_mapping
    output = workspace / "data/processed/diagnostic_legacy_uptake_sign.json"
    sys.argv = [
        str(validation.__file__),
        "--package",
        str(args.package.resolve()),
        "--window-start",
        "2020",
        "--window-end",
        "2100",
        "--reference-year",
        "2030",
        "--output",
        str(output),
    ]
    validation.main()
    diagnostic = json.loads(output.read_text())
    diagnostic["diagnostic_only"] = True
    diagnostic["mapping_override"] = (
        "Legacy abs(inventory amount) for resource uptake; known incorrect for "
        "avoided uptake. This is a controlled comparison, not a valid result."
    )
    current = json.loads(
        (output.parent / "cohort_pulse_equivalence_validation.json").read_text()
    )
    for case, case_values in diagnostic["cases"].items():
        case_values["corrected_rf_kg_co2_per_net_tonne"] = current["cases"][case][
            "radiative forcing"
        ]["trails_config_first_kg_co2_per_net_tonne"]["median"]
    output.write_text(json.dumps(diagnostic, indent=2) + "\n")


if __name__ == "__main__":
    main()
