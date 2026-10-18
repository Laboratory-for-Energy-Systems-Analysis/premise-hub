"""Read the regenerated SETAC dataset with the shared, unchanged result API.

An isolated module instance keeps paths and LRU caches separate from lca_time.
Changing this deck's data must never change the longer presentation's results.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from functools import lru_cache
import csv
import json

from apps.lca_time.workshop import results as shared_results

ROOT = Path(__file__).resolve().parent
_spec = spec_from_file_location(f"{__name__}._reader", shared_results.__file__)
_reader = module_from_spec(_spec)
_spec.loader.exec_module(_reader)
for _name, _path in list(vars(_reader).items()):
    if isinstance(_path, Path) and _path.is_relative_to(shared_results.ROOT / "data"):
        setattr(_reader, _name, ROOT / _path.relative_to(shared_results.ROOT))
_reader.SCENARIO_SECTOR_MIXES = ROOT / "data/sector_mixes.csv"


def __getattr__(name):
    return getattr(_reader, name)


def case_inventory(case):
    with (ROOT / "data/processed/system_inventory_2025.json").open() as stream:
        return json.load(stream)[case]


@lru_cache(maxsize=1)
def energy_flow_rows():
    with (ROOT / "data/processed/energy_flow_signs.csv").open(newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=None)
def cohort_fair_total_series(case, metric, contribution_view="total", quantile=50.0):
    """Pointwise quantile of total responses, preserving FaIR's half-year times.

    The shared contribution reader coerces dates to integers. SETAC's total
    response uses the exact time coordinates also used for pulse integration.
    """
    if contribution_view != "total":
        raise ValueError(
            "SETAC publishes total ensemble responses, not process quantiles"
        )
    values = tuple(
        sorted(
            (float(row["response_year"]), float(row["value_per_net_tonne"]))
            for row in _reader.cohort_fair_response_rows()
            if row["case"] == case
            and row["metric"] == metric
            and row["contribution_view"] == "total"
            and float(row["quantile"]) == float(quantile)
        )
    )
    if not values:
        raise LookupError(f"No total response for {case}, {metric}, q={quantile}")
    return values
