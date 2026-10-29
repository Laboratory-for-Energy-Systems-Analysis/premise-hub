"""Transparent temporal screening model; no background LCIA is calculated here.

Physical deployment is 1.25 t rock. Its reference eventual uptake is 1 t CO2.
The shrinking-core curve is a paper-inspired assumption, not a field forecast.
The air-sea delay is a sensitivity kernel, not a site-calibrated ocean model.
"""

from __future__ import annotations

import math

import numpy as np

REFERENCE_UPTAKE_KG = 1000.0
ROCK_KG = 1250.0
NICKEL_KG = ROCK_KG * 0.00263
CAMPAIGN_START = 2030
CAMPAIGN_YEARS = 20


def dissolution_cdf(age, duration=10):
    age = np.asarray(age, dtype=float)
    return 1 - np.maximum(0, 1 - np.clip(age / duration, 0, 1)) ** 3


def temporal_profile(duration=10, lag=1, efficiency=1, years=500):
    """Annual end-of-bin pulses; retain the uncredited tail, never normalize it.

    The discrete exponential delay uses the survival probability exp(-1/lag).
    All dissolved material enters the first annual uptake bin before survival
    is propagated to later bins. lag=0 reproduces instantaneous equilibration.
    """
    if duration <= 0 or lag < 0 or not 0 <= efficiency <= 1:
        raise ValueError("Invalid temporal scenario")
    edges = np.arange(years + 1, dtype=float)
    dissolved = np.diff(dissolution_cdf(edges, duration))
    if lag == 0:
        uptake = dissolved.copy()
    else:
        survival = math.exp(-1 / lag)
        kernel = (1 - survival) * survival ** np.arange(years)
        uptake = np.convolve(dissolved, kernel)[:years]
    return {
        "age": edges[1:],
        "dissolved": dissolved,
        "uptake_kg": uptake * efficiency * REFERENCE_UPTAKE_KG,
        "nickel_upper_bound_kg": dissolved * NICKEL_KG,
        "tail_kg": efficiency * REFERENCE_UPTAKE_KG
        - float(uptake.sum()) * efficiency * REFERENCE_UPTAKE_KG,
    }


def campaign_profile(duration=10, lag=1, efficiency=1, years=500, campaign_years=CAMPAIGN_YEARS):
    """Equal annual rock batches, normalized to the same total rock and uptake.

    The returned support includes the last batch's full original tail. This
    convolves physical foreground profiles, never characterized LCA scores.
    """
    if not isinstance(campaign_years, int) or campaign_years < 1:
        raise ValueError("Campaign years must be a positive integer")
    batch = temporal_profile(duration, lag, efficiency, years)
    weights = np.full(campaign_years, 1 / campaign_years)
    uptake = np.convolve(batch["uptake_kg"], weights)
    return {
        "age": np.arange(1, len(uptake) + 1),
        "dissolved": np.convolve(batch["dissolved"], weights),
        "uptake_kg": uptake,
        "nickel_upper_bound_kg": np.convolve(batch["nickel_upper_bound_kg"], weights),
        "tail_kg": batch["tail_kg"],
        "campaign_years": campaign_years,
    }
