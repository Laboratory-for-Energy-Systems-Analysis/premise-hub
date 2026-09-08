from __future__ import annotations

from dataclasses import dataclass
import csv
from pathlib import Path
from typing import Iterable

HEADER_ROW = 7
UNIT_ROW = 8
DATA_START_ROW = 9
SELECTOR_END = 17
LCI_END = 139


STAGE_RANGES: tuple[tuple[str, int, int], ...] = (
    ("clinker", 17, 29),
    ("raw_materials", 29, 51),
    ("kiln_fuels", 51, 67),
    ("heat_recovery", 67, 71),
    ("capture", 71, 87),
    ("storage", 87, 106),
    ("hydrogen", 106, 122),
    ("methanol", 122, 132),
    ("synthetic_fuel", 132, 139),
)


SELECTOR_NAMES = (
    "full_name",
    "background",
    "fuel_mix",
    "system",
    "capture_performance",
    "clinker_type",
    "multi_output_policy",
    "year",
    "electricity_mix",
    "marginal_heat",
    "capture_technology",
    "storage_location",
    "storage_site_status",
    "hydrogen_pathway",
    "electrolysis_electricity",
    "marginal_fuel",
    "allocation_key",
)


def excel_column(index: int) -> str:
    """Convert a zero-based column number to an Excel column label."""

    value = index + 1
    parts: list[str] = []
    while value:
        value, remainder = divmod(value - 1, 26)
        parts.append(chr(65 + remainder))
    return "".join(reversed(parts))


def _number(value: str | float | int | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def stage_for_column(index: int) -> str:
    for name, start, end in STAGE_RANGES:
        if start <= index < end:
            return name
    raise KeyError(index)


@dataclass(frozen=True)
class InventoryValue:
    column: int
    name: str
    unit: str
    amount: float
    stage: str
    source_cell: str

    @property
    def key(self) -> str:
        return f"{self.stage}.{self.column:03d}.{self.name}"


@dataclass(frozen=True)
class ScenarioRecord:
    source_row: int
    selectors: dict[str, str | float]
    inventory: tuple[InventoryValue, ...]

    @property
    def system(self) -> str:
        return str(self.selectors["system"])

    @property
    def year(self) -> int:
        return int(float(self.selectors["year"]))

    def amount(self, column: int) -> float:
        for value in self.inventory:
            if value.column == column:
                return value.amount
        raise KeyError(column)

    def fingerprint(self) -> tuple:
        return tuple(round(value.amount, 12) for value in self.inventory)


def load_scenario_records(path: str | Path) -> list[ScenarioRecord]:
    """Load the cached `Scenarios` CSV produced by ``extract_workbook.py``."""

    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    if len(rows) <= DATA_START_ROW:
        raise ValueError("Scenarios CSV is shorter than the expected workbook layout")
    headers = rows[HEADER_ROW]
    units = rows[UNIT_ROW]
    if headers[:4] != [
        "Full scenario name",
        "Background scenario",
        "Fuel mix",
        "Case study",
    ]:
        raise ValueError("Unexpected Scenarios header; source layout has changed")

    records: list[ScenarioRecord] = []
    for row_index, row in enumerate(rows[DATA_START_ROW:], start=DATA_START_ROW + 1):
        padded = row + [""] * max(0, LCI_END - len(row))
        if not padded[0] or padded[3] not in {"BAU", "CCS", "CCUS"}:
            continue
        selectors: dict[str, str | float] = dict(zip(SELECTOR_NAMES, padded[:17]))
        selectors["year"] = _number(selectors["year"])
        selectors["allocation_key"] = _number(selectors["allocation_key"])
        inventory = tuple(
            InventoryValue(
                column=column,
                name=headers[column],
                unit=units[column],
                amount=_number(padded[column]),
                stage=stage_for_column(column),
                source_cell=f"{excel_column(column)}{row_index}",
            )
            for column in range(SELECTOR_END, LCI_END)
        )
        records.append(
            ScenarioRecord(
                source_row=row_index,
                selectors=selectors,
                inventory=inventory,
            )
        )
    return records


def central_source_records(
    records: Iterable[ScenarioRecord],
    *,
    capture_technology: str = "Heat pumps",
) -> list[ScenarioRecord]:
    """Select de-duplicated source fixtures for the two locked pathways.

    BAU always uses the source workbook's ``None`` capture technology. The
    investment cases use ``capture_technology`` so the 2025 current-static view
    can retain the gas-boiler configuration while 2035 and time-explicit views
    use the heat-pump configuration.
    """

    backgrounds = {"Baseline (+3.5C)", "Paris Agreement (<1.5C)"}
    selected: list[ScenarioRecord] = []
    seen: set[tuple] = set()
    for record in records:
        s = record.selectors
        capture_ok = (
            s["capture_technology"] == capture_technology
            if record.system != "BAU"
            else s["capture_technology"] == "None"
        )
        if not (
            s["background"] in backgrounds
            and s["fuel_mix"] == "100% alternative fuel"
            and s["capture_performance"] == "Best-guess"
            and record.year == 2050
            and s["multi_output_policy"] == "Substitution"
            and capture_ok
        ):
            continue
        key = (s["background"], record.system, record.fingerprint())
        if key not in seen:
            selected.append(record)
            seen.add(key)
    expected = {
        (background, system)
        for background in backgrounds
        for system in ("BAU", "CCS", "CCUS")
    }
    actual = {(r.selectors["background"], r.system) for r in selected}
    if actual != expected:
        raise ValueError(
            f"Central source coverage mismatch: missing {sorted(expected-actual)}"
        )
    return selected


def reference_bau_records(
    records: Iterable[ScenarioRecord],
) -> dict[str, ScenarioRecord]:
    """Return one 2020, 60%-alternative-fuel BAU reference per pathway."""

    pathway_by_background = {
        "Baseline (+3.5C)": "SSP2-NPi",
        "Paris Agreement (<1.5C)": "SSP2-PkBudg1000",
    }
    selected: dict[str, ScenarioRecord] = {}
    for record in records:
        selectors = record.selectors
        pathway = pathway_by_background.get(str(selectors["background"]))
        if (
            pathway
            and record.system == "BAU"
            and record.year == 2020
            and selectors["fuel_mix"] == "60% alternative fuel"
            and selectors["capture_performance"] == "Best-guess"
            and selectors["multi_output_policy"] == "Substitution"
        ):
            selected.setdefault(pathway, record)
    if set(selected) != set(pathway_by_background.values()):
        raise ValueError("Missing a 2020 BAU reference for one or more pathways")
    return selected
