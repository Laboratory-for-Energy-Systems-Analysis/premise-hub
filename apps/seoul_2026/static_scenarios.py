"""Checked, year-matched scenario extensions for the prospective-static lesson."""

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
SCENARIOS = ("SSP2-NPi", "SSP2-PkBudg1000")
DEFAULT_SCENARIO = "SSP2-PkBudg1000"
RESULT_SHA256 = "fe8589702232a54175bb38029152fd04f9efaff29b865adc1427927831d2584e"


@lru_cache(maxsize=1)
def scenario_results():
    raw = (ROOT / "data/static_scenario_results.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != RESULT_SHA256:
        raise ValueError("Static scenario results changed; recheck calculations")
    data = json.loads(raw)
    cdr = json.loads((ROOT.parent / "setac_2026/data/processed/system_inventory_2025.json").read_text())
    if data["cdr_foreground_sha256"] != cdr["basis"]["foreground_sha256"]:
        raise ValueError("Scenario extension uses a different CDR foreground")
    if data["erw_foreground_sha256"] != hashlib.sha256((ROOT / "data/coastal_erw_ei312.xlsx").read_bytes()).hexdigest():
        raise ValueError("Scenario extension uses a different ERW foreground")
    expected = {(p, y) for p in SCENARIOS for y in (2035, 2050)}
    if {(r["pathway"], r["year"]) for r in data["records"]} != expected:
        raise ValueError("Missing static scenario/year")
    for record in data["records"]:
        if set(record["cases"]) != {"DACCS", "BECCS", "ERW"}:
            raise ValueError("Missing scenario case")
        for case in record["cases"].values():
            total = sum(r["score"] for r in case["foreground"] + case["suppliers"])
            if not (math.isfinite(total) and math.isclose(total, case["total"], abs_tol=1e-6, rel_tol=0)
                    and math.isclose(total, case["forward_static_total"], abs_tol=1e-6, rel_tol=0)):
                raise ValueError("Static scenario root/forward scores do not reconcile")
    return data


def case_result(case, year, pathway=DEFAULT_SCENARIO):
    if pathway not in SCENARIOS or year not in (2035, 2050):
        raise ValueError("Unsupported static scenario/year")
    record = next(r for r in scenario_results()["records"]
                  if r["year"] == year and r["pathway"] == pathway)
    return record["cases"][case]
