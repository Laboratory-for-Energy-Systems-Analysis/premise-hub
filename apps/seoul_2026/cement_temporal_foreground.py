"""Split only the kiln's direct CO2 contribution, retaining supplier roots."""

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "ccus_webinar/data/public"
SOURCE_SHA256 = "eed60aa0f8abdf50dd7f845363c2604ddae833d3f33e75ad4471906984c5a313"


@lru_cache(maxsize=1)
def kiln_co2_differences():
    """Year-wise fossil/biogenic CCS−BAU GWP scores from reviewed direct flows.

    This replaces the clinker stage alone; it does not mix whole-system flow
    attribution into upstream activity roots. The caller retains the small
    remaining clinker-root contribution separately, including pre-operation years.
    """
    from .comparison import cement_bundle
    from .cement_basis import cement_scale

    path = DATA / "temporal_carbon_display.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Cement foreground carbon display changed")
    data = json.loads(path.read_text())
    bundle = cement_bundle()
    if data["source_bundle_sha256"] != bundle.manifest["bundles"]["main"]["sha256"]:
        raise ValueError("Cement direct carbon and temporal results differ")
    physical = {(r["system"],int(r["year"])):r for r in data["rows"]}
    stages = defaultdict(float)
    for row in bundle.tables["temporal_contributions"]:
        if row["grouping"]=="stage" and row["contributor"]=="clinker" and row["system"] in ("CCS","BAU"):
            stages[row["system"],int(float(row["year"]))] += float(row["score"])
    result={}
    for year in sorted({y for system,y in physical if system in ("CCS","BAU")}):
        parts={"fossil":0.0,"non_fossil":0.0}
        for system,sign in (("CCS",1),("BAU",-1)):
            row=physical[system,year]
            subtotal=sum(row["gross_score_"+origin]-row["captured_score_"+origin]
                         for origin in parts)
            if abs(subtotal-stages[system,year])>1e-4:
                raise ValueError("Kiln direct CO2 does not reproduce its stage")
            for origin in parts:
                parts[origin] += sign*(row["gross_score_"+origin]-row["captured_score_"+origin])
        total=stages["CCS",year]-stages["BAU",year]
        if abs(sum(parts.values())-total)>1e-4:
            raise ValueError("Cement direct carbon difference does not close")
        result[year]={"Avoided fossil CO₂":parts["fossil"]*cement_scale(),
                      "Avoided biogenic CO₂":parts["non_fossil"]*cement_scale()}
    return result
