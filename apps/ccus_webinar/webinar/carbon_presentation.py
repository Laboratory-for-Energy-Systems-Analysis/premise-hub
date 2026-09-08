"""Zero-sum chart decomposition, not an inventory or LCIA transformation."""
from collections import defaultdict
from math import isclose, isfinite

KILN_CO2 = {
    "Limestone calcination": "calcination CO₂",
    "Fossil kiln-fuel combustion": "fossil-fuel CO₂",
    "Non-fossil kiln-fuel combustion": "non-fossil CO₂",
}


def gross_kiln_transfer_view(rows):
    """Use the same-blend BAU kiln as the gross-CO2 reference in one comparison.

    Baseline and each sensitivity cell must be passed separately. Add the
    gross-minus-uncaptured difference to clinker and subtract exactly the same
    characterized amount at its destination. Leave losses, uptake, boiler
    emissions and fuel combustion untouched. Output is kg CO2-eq, not kg C.
    """
    result = [dict(row) for row in rows]
    gross = {}
    before = defaultdict(float)
    for row in rows:
        value = float(row["score"])
        if not isfinite(value):
            raise ValueError("Nonfinite contribution")
        before[row["system"]] += value
        if row["system"] == "BAU" and row["stage"] == "clinker" and row["subprocess"] in KILN_CO2:
            label = row["subprocess"]
            if label in gross:
                raise ValueError("Ambiguous gross kiln reference")
            gross[label] = value
    required = {r["subprocess"] for r in rows if r["stage"] == "clinker" and r["subprocess"] in KILN_CO2}
    if "Limestone calcination" not in gross or not required.issubset(gross):
        raise ValueError("Complete same-blend BAU kiln reference is required")
    for row in list(result):
        label = row["subprocess"]
        if row["system"] not in ("CCS", "CCUS") or row["stage"] != "clinker" or label not in KILN_CO2:
            continue
        transfer = gross[label] - float(row["score"])
        if transfer < -1e-7:
            raise ValueError("Uncaptured contribution exceeds gross kiln reference")
        if transfer <= 0:
            continue
        row["score"] = gross[label]
        row["sign"] = "positive"
        utilisation = row["system"] == "CCUS" and label == "Non-fossil kiln-fuel combustion"
        result.append({**row, "stage": "methanol" if utilisation else "storage",
                       "subprocess": f"Captured {KILN_CO2[label]} → {'utilisation' if utilisation else 'storage'}",
                       "sign": "negative", "score": -transfer,
                       "presentation_only": True})
    after = defaultdict(float)
    for row in result:
        after[row["system"]] += float(row["score"])
    if any(not isclose(before[s], after[s], abs_tol=1e-8, rel_tol=1e-12) for s in before):
        raise ValueError("Presentation decomposition changed a scenario total")
    return result
