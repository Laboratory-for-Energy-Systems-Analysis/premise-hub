#!/usr/bin/env python3
"""Calculate auditable EF 3.1 scores for the workshop scenario databases."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import numpy.testing

# scikit-umfpack 0.3.3 is the last conda-forge osx-arm64 build compatible
# with this Python 3.11 / NumPy 1.x premise environment. Its only obsolete
# NumPy reference is the removed test helper; provide a process-local shim so
# Brightway can import the accelerated solver without patching site-packages.
if not hasattr(np.testing, "Tester"):
    setattr(
        np.testing,
        "Tester",
        type("Tester", (), {"test": lambda self, *args, **kwargs: None}),
    )

import bw2calc as bc
import bw2data as bd
from premise_gwp import add_premise_gwp

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "processed" / "premise_databases.json"
CONTRACT = ROOT / "data" / "lcia_activity_contract.json"
RESULTS = ROOT / "data" / "processed" / "lcia_results.csv"
CONTRIBUTIONS = ROOT / "data" / "processed" / "lcia_contributions.csv"

METHODS = [
    (
        "IPCC 2021",
        "climate change",
        "GWP 100a, incl. H and bio CO2",
    ),
    (
        "ecoinvent-3.12",
        "EF v3.1",
        "material resources: metals/minerals",
        "abiotic depletion potential (ADP): elements (ultimate reserves)",
    ),
    ("ecoinvent-3.12", "EF v3.1", "land use", "soil quality index"),
    (
        "ecoinvent-3.12",
        "EF v3.1",
        "water use",
        "user deprivation potential (deprivation-weighted water consumption)",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        help="Calculate only these manifest years and merge them into existing outputs",
    )
    return parser.parse_args()


def matches(activity, spec: dict) -> bool:
    name = activity.get("name", "").lower()
    product = activity.get("reference product", "").lower()
    if spec.get("name") and name != spec["name"].lower():
        return False
    if spec.get("product") and product != spec["product"].lower():
        return False
    if any(token.lower() not in name for token in spec.get("name_contains", [])):
        return False
    if spec.get("product_contains") and spec["product_contains"].lower() not in product:
        return False
    return True


def find_activity(database: bd.Database, spec: dict):
    candidates = [activity for activity in database if matches(activity, spec)]
    for location in spec["location_priority"]:
        located = [
            activity for activity in candidates if activity.get("location") == location
        ]
        if len(located) == 1:
            return located[0]
        if len(located) > 1:
            details = [
                (a.get("name"), a.get("reference product"), a.get("location"), a.key)
                for a in located
            ]
            raise ValueError(
                f"Ambiguous activity contract for {spec['technology']} at {location}: {details}"
            )
    details = [
        (a.get("name"), a.get("reference product"), a.get("location"), a.key)
        for a in candidates[:30]
    ]
    raise ValueError(
        f"No contracted location found for {spec['technology']}; candidates: {details}"
    )


def contribution_rows(lca, metadata: dict, limit: int = 10) -> list[dict]:
    values = lca.characterized_inventory.sum(axis=0)
    array = values.A1 if hasattr(values, "A1") else np.asarray(values).ravel()
    difference = float(lca.score) - float(array.sum())
    if abs(difference) > max(1e-9, abs(float(lca.score)) * 1e-6):
        raise ValueError(f"Contribution reconciliation failed: {difference}")
    indices = np.argsort(np.abs(array))[::-1][:limit]
    rows = []
    for index in indices:
        if abs(array[index]) < 1e-30:
            continue
        node_id = lca.dicts.activity.reversed[int(index)]
        activity = bd.get_node(id=node_id)
        rows.append(
            {
                **metadata,
                "contribution": float(array[index]),
                "contributor_name": activity.get("name"),
                "contributor_product": activity.get("reference product"),
                "contributor_location": activity.get("location"),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    bd.projects.set_current(manifest["brightway_project"])
    climate_method = METHODS[0]
    if climate_method not in bd.methods:
        add_premise_gwp()
    missing_methods = [method for method in METHODS if method not in bd.methods]
    if missing_methods:
        raise SystemExit(f"Missing LCIA methods: {missing_methods}")

    timestamp = datetime.now(timezone.utc).isoformat()
    scores: list[dict] = []
    contributions: list[dict] = []
    database_metas = manifest["databases"]
    if args.years:
        selected_years = set(args.years)
        database_metas = [
            metadata
            for metadata in database_metas
            if metadata["year"] in selected_years
        ]
        if not database_metas:
            raise ValueError(f"No manifest databases found for years {args.years}")
    for database_meta in database_metas:
        database_name = database_meta["database"]
        if database_name not in bd.databases:
            raise ValueError(f"Missing scenario database: {database_name}")
        database = bd.Database(database_name)
        for spec in contract["cases"]:
            activity = find_activity(database, spec)
            for method in METHODS:
                lca = bc.LCA({activity.id: 1}, method)
                lca.lci()
                lca.lcia()
                method_unit = bd.Method(method).metadata.get("unit", "")
                provenance_id = f"{database_name}:{activity.id}:{method[-1]}"
                if len(method) == 4:
                    method_family, category, indicator = method[1], method[2], method[3]
                else:
                    method_family, category, indicator = method
                metadata = {
                    "model": database_meta["model"],
                    "scenario": database_meta["pathway"],
                    "year": database_meta["year"],
                    "database_name": database_name,
                    "source_database": manifest["source_database"],
                    "premise_version": manifest["premise_version"],
                    "case": spec["case"],
                    "technology": spec["technology"],
                    "region": activity.get("location"),
                    "r10_mapping_status": spec["mapping_status"],
                    "activity_key": str(activity.key),
                    "functional_unit": spec["functional_unit"],
                    "method_family": method_family,
                    "category": category,
                    "indicator": indicator,
                    "unit": method_unit,
                    "calculation_timestamp": timestamp,
                    "provenance_id": provenance_id,
                }
                scores.append({**metadata, "score": float(lca.score)})
                contributions.extend(contribution_rows(lca, metadata))

    calculated_scores = len(scores)
    calculated_contributions = len(contributions)
    if args.years:
        selected_databases = {metadata["database"] for metadata in database_metas}
        if RESULTS.exists():
            with RESULTS.open(newline="", encoding="utf-8") as handle:
                existing_scores = [
                    row
                    for row in csv.DictReader(handle)
                    if row["database_name"] not in selected_databases
                ]
            scores = existing_scores + scores
        if CONTRIBUTIONS.exists():
            with CONTRIBUTIONS.open(newline="", encoding="utf-8") as handle:
                existing_contributions = [
                    row
                    for row in csv.DictReader(handle)
                    if row["database_name"] not in selected_databases
                ]
            contributions = existing_contributions + contributions

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(scores[0]))
        writer.writeheader()
        writer.writerows(scores)
    with CONTRIBUTIONS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(contributions[0]))
        writer.writeheader()
        writer.writerows(contributions)
    print(
        f"Calculated {calculated_scores} scores and {calculated_contributions} "
        f"contribution rows; wrote {len(scores)} scores and {len(contributions)} "
        "contribution rows"
    )


if __name__ == "__main__":
    main()
