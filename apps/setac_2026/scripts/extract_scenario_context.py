"""Extract the SETAC scenario indicators from the existing premise 2.4.9 export."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scenario_explorer/data/structured_data (2, 4, 9).csv.gz"
OUTPUT = Path(__file__).resolve().parents[1] / "data/scenario_context.csv"
VARIABLES = {
    "GMST": ("GMST", "degC above 1850-1900"),
    "CO2": ("CO2", "t CO2/yr"),
    "population": ("Population", "million people"),
}


def extract_rows(source=SOURCE):
    rows = []
    with gzip.open(source, "rt", newline="") as stream:
        for row in csv.DictReader(stream):
            if (
                row["model"] != "remind-eu"
                or row["scenario"] not in ("SSP2-NPi", "SSP2-PkBudg1000")
                or row["region"] not in ("World", "ENC")
                or row["variables"] not in VARIABLES
                or not 2020 <= int(row["year"]) <= 2100
            ):
                continue
            indicator, unit = VARIABLES[row["variables"]]
            rows.append(
                dict(
                    pathway=row["scenario"],
                    region=row["region"],
                    indicator=indicator,
                    year=row["year"],
                    value=row["val"],
                    unit=unit,
                )
            )
    keys = [(r["pathway"], r["region"], r["indicator"], int(r["year"])) for r in rows]
    if not rows or len(keys) != len(set(keys)):
        raise ValueError("Missing or duplicate scenario context records")
    return [r for _, r in sorted(zip(keys, rows))]


def main():
    rows = extract_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    OUTPUT.with_suffix(".json").write_text(
        json.dumps(
            {
                "source": str(SOURCE.relative_to(ROOT.parent)),
                "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                "premise_version": "2.4.9",
                "premise_source_commit": "50ea06e40466f185b0b1c77de9f4bbbd6288f19a",
                "model": "REMIND-EU",
                "rows": len(rows),
                "notes": [
                    "Source values and units are retained without interpolation or filling.",
                    "GMST is available only for World (MAGICC7 median).",
                    "ENC SSP2-NPi CO2 has no 2100 row in the source export.",
                ],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote {len(rows)} records to {OUTPUT}")


if __name__ == "__main__":
    main()
