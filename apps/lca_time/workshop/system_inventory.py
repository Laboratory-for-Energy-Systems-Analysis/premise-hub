from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_INVENTORY = ROOT / "data" / "processed" / "system_inventory_2025.json"


@lru_cache(maxsize=1)
def system_inventory() -> dict:
    """Return the reviewed 2025 inventory values used by the system slides."""

    with SYSTEM_INVENTORY.open(encoding="utf-8") as stream:
        return json.load(stream)


def case_inventory(case: str) -> dict:
    """Return one reviewed case, failing loudly for an unknown system."""

    try:
        return system_inventory()[case]
    except KeyError as error:
        raise LookupError(f"Unknown system inventory case: {case}") from error
