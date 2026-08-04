#!/usr/bin/env python3
"""Build the IMAGE workshop databases from ecoinvent 3.12 cutoff.

The script copies the clean source Brightway project into an isolated workshop
project, performs full premise updates, and writes deterministic database names.
It never deletes an existing database unless --overwrite is given explicitly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import bw2data as bd
from premise import NewDatabase

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "processed" / "premise_databases.json"
SOURCE_PROJECT = "ecoinvent-3.12-cutoff"
TARGET_PROJECT = "esd-workshop-ei312-cutoff"
SOURCE_DB = "ecoinvent-3.12-cutoff"
BIOSPHERE_DB = "ecoinvent-3.12-biosphere"
PATHWAYS = ["SSP1-L", "SSP2-M", "SSP3-H", "SSP2-VLHO"]
YEARS = [2020, 2040, 2060]


def database_name(pathway: str, year: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", pathway.lower()).strip("-")
    return f"esd-ei312-cutoff-image-{slug}-{year}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke", action="store_true", help="Build only IMAGE SSP2-M 2040"
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run premise transformations without writing databases",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete matching target databases before writing",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=YEARS,
        help="Scenario years to build (default: 2020 2040 2060)",
    )
    parser.add_argument("--source-project", default=SOURCE_PROJECT)
    parser.add_argument("--target-project", default=TARGET_PROJECT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    key = os.environ.get("PREMISE_KEY") or os.environ.get("IAM_FILES_KEY")
    if not key:
        raise SystemExit(
            "Set PREMISE_KEY (or IAM_FILES_KEY) to the encrypted premise IAM-data key"
        )

    bd.projects.set_current(args.source_project)
    missing = [name for name in (SOURCE_DB, BIOSPHERE_DB) if name not in bd.databases]
    if missing:
        raise SystemExit(
            f"Missing source Brightway databases in {args.source_project}: {missing}"
        )

    project_names = {project.name for project in bd.projects}
    if args.target_project not in project_names:
        bd.projects.copy_project(args.target_project, switch=True)
    else:
        bd.projects.set_current(args.target_project)

    pairs = (
        [("SSP2-M", 2040)]
        if args.smoke
        else [(pathway, year) for pathway in PATHWAYS for year in args.years]
    )
    scenarios = [
        {"model": "image", "pathway": pathway, "year": year} for pathway, year in pairs
    ]
    names = [database_name(pathway, year) for pathway, year in pairs]

    existing = [name for name in names if name in bd.databases]
    if existing and not args.overwrite:
        raise SystemExit(
            f"Target databases already exist; use --overwrite only after reviewing them: {existing}"
        )
    if args.overwrite:
        for name in existing:
            del bd.databases[name]

    print(
        json.dumps(
            {
                "project": bd.projects.current,
                "source_db": SOURCE_DB,
                "scenarios": scenarios,
                "targets": names,
                "write": not args.no_write,
            },
            indent=2,
        )
    )
    ndb = NewDatabase(
        scenarios=scenarios,
        source_db=SOURCE_DB,
        source_version="3.12",
        source_type="brightway",
        system_model="cutoff",
        biosphere_name=BIOSPHERE_DB,
        key=key.encode(),
        keep_imports_uncertainty=True,
        keep_source_db_uncertainty=False,
    )
    ndb.update()

    if args.no_write:
        print("Transformations completed; --no-write requested")
        return
    ndb.write_db_to_brightway(names)

    rows = []
    for (pathway, year), name in zip(pairs, names, strict=True):
        if name not in bd.databases:
            raise RuntimeError(f"premise did not write expected database: {name}")
        rows.append(
            {
                "model": "image",
                "pathway": pathway,
                "year": year,
                "database": name,
                "datasets": len(bd.Database(name)),
            }
        )
    previous_rows = []
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest_contract = {
            "brightway_project": args.target_project,
            "source_project": args.source_project,
            "source_database": SOURCE_DB,
            "source_version": "3.12",
            "system_model": "cutoff",
            "premise_version": "2.4.6",
        }
        mismatches = {
            key: (previous.get(key), value)
            for key, value in manifest_contract.items()
            if previous.get(key) != value
        }
        if mismatches:
            raise ValueError(f"Existing manifest contract differs: {mismatches}")
        previous_rows = previous.get("databases", [])

    rows_by_database = {row["database"]: row for row in previous_rows}
    rows_by_database.update({row["database"]: row for row in rows})
    pathway_order = {pathway: index for index, pathway in enumerate(PATHWAYS)}
    merged_rows = sorted(
        rows_by_database.values(),
        key=lambda row: (pathway_order.get(row["pathway"], 999), row["year"]),
    )
    payload = {
        "brightway_project": args.target_project,
        "source_project": args.source_project,
        "source_database": SOURCE_DB,
        "source_version": "3.12",
        "system_model": "cutoff",
        "premise_version": "2.4.6",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "databases": merged_rows,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
