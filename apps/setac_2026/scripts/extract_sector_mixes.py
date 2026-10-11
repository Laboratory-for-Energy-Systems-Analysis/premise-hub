"""Extend the reviewed sector mixes using the original local scenario packages.

Run with --source-project pointing to FSLCI_workshop_2026. Only aggregate market
shares and provenance are exported; the inventory packages remain local.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import zipfile

APP = Path(__file__).resolve().parents[1]
BASELINE = APP.parent / "lca_time/data/processed/scenario_sector_mixes.csv"
OUTPUT = APP / "data/sector_mixes.csv"
YEARS = (2025, 2030, 2035, 2040, 2045, 2050)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-project", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_project.resolve()
    manifest = json.loads((source / "data/trails_packages_manifest.json").read_text())
    extractor_path = source / "scripts/extract_scenario_sector_mixes.py"
    spec = importlib.util.spec_from_file_location(
        "reviewed_mix_extractor", extractor_path
    )
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)

    rows, packages = [], []
    for record in manifest["packages"]:
        package_path = source / record["path"]
        digest = sha256(package_path)
        if digest != record["sha256"]:
            raise ValueError(f"Source package hash mismatch: {record['pathway']}")
        with zipfile.ZipFile(package_path) as package:
            for year in YEARS:
                rows.extend(extractor.extract_year(package, record["pathway"], year))
                print(f"Extracted {record['pathway']} {year}", flush=True)
        packages.append(
            {"pathway": record["pathway"], "file": package_path.name, "sha256": digest}
        )

    key = lambda row: (row["pathway"], int(row["year"]), row["sector"], row["category"])
    indexed = {key(row): row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("Duplicate sector mix records")
    if any(not math.isfinite(row["share"]) or row["share"] < 0 for row in rows):
        raise ValueError("Invalid sector mix share")
    with BASELINE.open(newline="") as stream:
        baseline = list(csv.DictReader(stream))
    for previous in baseline:
        current = indexed[key(previous)]
        if not math.isclose(float(previous["share"]), current["share"], abs_tol=1e-12):
            raise ValueError(f"Reviewed share changed: {key(previous)}")
        for field in ("market_name", "reference_product", "market_unit", "location"):
            if previous[field] != current[field]:
                raise ValueError(f"Reviewed market identity changed: {key(previous)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    generation = manifest["generation"]
    OUTPUT.with_suffix(".json").write_text(
        json.dumps(
            {
                "source_project": source.name,
                "extractor": "scripts/extract_scenario_sector_mixes.py",
                "extractor_sha256": sha256(extractor_path),
                "packages": packages,
                "model": generation["iam_model"],
                "premise_version": generation["premise_version"],
                "premise_source_commit": generation["premise_git_commit"],
                "source_package_validation_trails_version": generation[
                    "trails_version_used_for_validation"
                ],
                "years": YEARS,
                "location": "ENC",
                "rows": len(rows),
                "reviewed_baseline_sha256": sha256(BASELINE),
                "reviewed_rows_verified": len(baseline),
                "notes": [
                    "Technology shares extracted directly from each package's anchor-year market exchanges; no interpolation.",
                    "Uses the original extractor's market selection and technology grouping.",
                    "All 2025, 2030 and 2050 shares and market identities verified against the reviewed lca_time export.",
                    "Each sector/pathway/year sums to one. No LCA or climate calculations were rerun.",
                ],
            },
            indent=2,
        )
        + "\n"
    )
    print(
        f"Wrote {len(rows)} rows to {OUTPUT}; verified {len(baseline)} reviewed rows."
    )


if __name__ == "__main__":
    main()
