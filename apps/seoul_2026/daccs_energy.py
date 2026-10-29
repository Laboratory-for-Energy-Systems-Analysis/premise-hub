"""Checked positive/negative flow contributions within DACCS electricity."""

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULT_SHA256="b7d761fee715db86137f54776681f28e35057a1fbe3f6cf06d17b10e5eb69f6b"


@lru_cache(maxsize=1)
def signed_energy():
    from apps.setac_2026 import results

    path=ROOT/"data/daccs_energy_signed.json"
    if hashlib.sha256(path.read_bytes()).hexdigest()!=RESULT_SHA256:
        raise ValueError("DACCS signed-energy results changed")
    record=json.loads(path.read_text())
    source=ROOT.parent/"setac_2026/data/processed/cohort_temporal_scores.csv"
    if hashlib.sha256(source.read_bytes()).hexdigest()!=record["source_scores_sha256"]:
        raise ValueError("DACCS signed energy and reviewed source table differ")
    expected=defaultdict(float)
    for row in results.cohort_temporal_score_rows():
        if row["case"]=="DACCS" and row["contributor"]=="market group for electricity, medium voltage" and row["location"]=="ENC":
            if float(row["denominator_net_stored_tonnes"])!=record["cohort_storage_tonnes"]:
                raise ValueError("DACCS energy normalization changed")
            expected[int(row["impact_year"])]+=float(row["score_per_net_tonne_kg_co2eq"])
    actual={}
    for point in record["annual"]:
        if point["positive"]<0 or point["negative"]>0:
            raise ValueError("DACCS energy signs are inconsistent")
        year=point["year"]
        if year in actual:
            raise ValueError("Duplicate DACCS electricity year")
        actual[year]=point["positive"]+point["negative"]
    if any(abs(actual.get(y,0)-expected.get(y,0))>1e-9 for y in actual.keys()|expected.keys()):
        raise ValueError("Signed DACCS electricity fails annual source closure")
    return record
