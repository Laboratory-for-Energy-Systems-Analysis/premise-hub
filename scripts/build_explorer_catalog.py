#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "apps" / "scenario_explorer" / "data"


def main() -> None:
    entries = yaml.safe_load((DATA_DIR / "datasets.yaml").read_text(encoding="utf-8"))
    variables: set[str] = set()
    for entry in entries:
        path = (DATA_DIR / entry["filename"]).resolve()
        if path.parent != DATA_DIR.resolve() or not path.is_file():
            raise FileNotFoundError(path)
        column = pd.read_csv(path, usecols=["variables"], dtype={"variables": "string"})
        variables.update(column["variables"].dropna().tolist())
    output = DATA_DIR / "variable_catalog.json"
    output.write_text(
        json.dumps(sorted(variables), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(variables)} variables to {output}")


if __name__ == "__main__":
    main()
