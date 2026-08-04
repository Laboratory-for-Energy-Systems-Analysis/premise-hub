#!/usr/bin/env python3
"""Read-only audit of the local prospective DAC Brightway superstructure."""

from __future__ import annotations

import json

import bw2data as bd

PROJECT = "pLCA course 2026"
DATABASE = "pLCA-course-2026-all-sectors-superstructure"
ACTIVITY_NAME = (
    "carbon dioxide, captured and stored, with a sorbent-based direct air "
    "capture system, 100ktCO2"
)


def compact(value):
    try:
        return json.loads(json.dumps(value, default=str))
    except TypeError:
        return str(value)


def main() -> None:
    bd.projects.set_current(PROJECT)
    print("project", bd.projects.current)
    print("project_dir", bd.projects.dir)
    print("database_metadata", compact(bd.databases[DATABASE]))
    database = bd.Database(DATABASE)
    matches = [
        activity
        for activity in database
        if activity.get("name") == ACTIVITY_NAME
        and activity.get("reference product") == "carbon dioxide, captured"
        and activity.get("location") == "World"
    ]
    print("exact_world_sorbent_matches", len(matches))
    if not matches:
        return
    activity = matches[0]
    print("activity_key", activity.key)
    print("activity_fields", sorted(activity.as_dict()))
    print(
        "activity_scenario_fields",
        compact(
            {
                key: value
                for key, value in activity.as_dict().items()
                if "scenario" in key.lower()
                or "pathway" in key.lower()
                or "year" in key.lower()
            }
        ),
    )
    exchanges = list(activity.exchanges())
    print("exchange_count", len(exchanges))
    field_names = sorted({key for exchange in exchanges for key in exchange.as_dict()})
    print("exchange_fields", field_names)
    scenario_exchange_fields = sorted(
        key
        for key in field_names
        if "scenario" in key.lower() or "pathway" in key.lower()
    )
    print("scenario_exchange_fields", scenario_exchange_fields)


if __name__ == "__main__":
    main()
