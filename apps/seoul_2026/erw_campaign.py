"""Checked, portable aggregate results for the twenty-year ERW supply chain."""

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
RESULT_SHA256 = "793c6300f1467f336430a3a60e43a04974b934bdc9d5c41314d91417c81ff007"


@lru_cache(maxsize=1)
def campaign_results():
    path = DATA / "erw_campaign.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != RESULT_SHA256:
        raise ValueError("ERW campaign results differ from the reviewed calculation")
    data = json.loads(path.read_text())
    for name, key in (("coastal_erw_ei312.xlsx", "source_foreground_sha256"),
                      ("coastal_erw_campaign.xlsx", "foreground_sha256")):
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest() != data[key]:
            raise ValueError(f"ERW campaign no longer matches {name}")
    campaign = data["campaign"]
    if (campaign["start"],campaign["end"],campaign["years"]) != (2030,2049,20):
        raise ValueError("Unexpected ERW operating period")
    if campaign["total_rock_kg"] != 1250 or campaign["eventual_gross_uptake_kg"] != 1000:
        raise ValueError("ERW campaign functional unit changed")
    actual = defaultdict(float)
    for root in data["temporal_roots"]:
        for point in root["series"]:
            actual[point["age"]] += point["score"]
    expected = {r["age"]:r["score"] for r in data["temporal"]}
    if any(abs(actual[y]-expected.get(y,0))>1e-7 for y in actual.keys()|expected.keys()):
        raise ValueError("ERW campaign root contributions do not close")
    if abs(sum(expected.values())-sum(r["total"] for r in data["annual_static_checks"]))>1e-3:
        raise ValueError("ERW campaign fails independent annual static closure")
    return data
