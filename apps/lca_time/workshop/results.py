from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC_RESULTS = ROOT / "data" / "processed" / "static_lcia.csv"
STATIC_CONTRIBUTIONS = ROOT / "data" / "processed" / "static_contributions.csv"
PROCESS_STEP_ATTRIBUTION = (
    ROOT / "data" / "processed" / "process_step_attribution_2025.json"
)
TEMPORAL_RESULTS = ROOT / "data" / "processed" / "temporal_lcia.csv"
FAIR_RESULTS = ROOT / "data" / "processed" / "fair_results.csv"
SCENARIO_SECTOR_INDICATORS = (
    ROOT / "data" / "processed" / "scenario_sector_indicators.csv"
)
SCENARIO_SECTOR_MIXES = ROOT / "data" / "processed" / "scenario_sector_mixes.csv"
LIFETIME_RESULTS = ROOT / "data" / "processed" / "lifetime_lcia.csv"
LIFETIME_CONTRIBUTIONS = ROOT / "data" / "processed" / "lifetime_contributions.csv"
COHORT_TEMPORAL_SCORES = ROOT / "data" / "processed" / "cohort_temporal_scores.csv"
COHORT_FAIR_RESPONSES = ROOT / "data" / "processed" / "cohort_fair_responses.csv"
CO2_REFERENCE_PULSE = ROOT / "data" / "processed" / "co2_reference_pulse.csv"
COHORT_PULSE_EQUIVALENCE_GRID = (
    ROOT / "data" / "processed" / "cohort_pulse_equivalence_grid.npz"
)
FOREST_POOL_SENSITIVITY = ROOT / "data" / "forest_pool_sensitivity.json"
NET_REMOVAL_KG = 1000.0


@lru_cache(maxsize=1)
def static_rows() -> tuple[dict[str, str], ...]:
    with STATIC_RESULTS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=1)
def static_contribution_rows() -> tuple[dict[str, str], ...]:
    with STATIC_CONTRIBUTIONS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=1)
def process_step_attribution() -> dict:
    """Return reviewed foreground-service attribution for the 2025 step view."""

    with PROCESS_STEP_ATTRIBUTION.open(encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def forest_pool_sensitivity_settings() -> dict:
    """Return the documented presentation-level forest-pool assumptions."""

    with FOREST_POOL_SENSITIVITY.open(encoding="utf-8") as stream:
        settings = json.load(stream)
    fraction = float(settings["stress_test_fraction_of_gross_regrowth"])
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(
            "Forest-pool stress-test fraction must be between zero and one."
        )
    return settings


def static_score(
    case: str,
    pathway: str,
    year: int,
    chp_treatment: str,
) -> float:
    matches = [
        row
        for row in static_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and int(row["year"]) == int(year)
        and row["chp_treatment"] == chp_treatment
    ]
    if len(matches) != 1:
        raise LookupError(
            "Expected one static result for "
            f"{case}, {pathway}, {year}, {chp_treatment}; found {len(matches)}"
        )
    return float(matches[0]["score"])


def net_removal_scale(case: str, pathway: str, year: int) -> float:
    """Return the scale for one physical net tonne stored from the atmosphere.

    The foreground reference product is already one kilogram reaching storage
    after the modeled transport loss, and the static calculation demands 1000
    kilograms. Supply-chain GHGs remain in the LCIA numerator and must not alter
    this physical denominator.
    """

    treatment = (
        "not applicable"
        if case == "DACCS"
        else "new CHP+CCS vs standing forest and Northern European energy"
    )
    score = static_score(case, pathway, year, treatment)
    if score >= 0:
        raise ValueError(
            "A net-removal functional unit requires a negative static climate "
            f"balance; got {score} for {case}, {pathway}, {year}."
        )
    return 1.0


def gross_storage_per_net_tonne(case: str, pathway: str, year: int) -> float:
    """Return physical tonnes stored per net tonne stored from the atmosphere."""

    return net_removal_scale(case, pathway, year)


def static_score_per_net_tonne(
    case: str,
    pathway: str,
    year: int,
    chp_treatment: str,
) -> float:
    """Return static LCIA per physical net tonne stored from the atmosphere."""

    return static_score(case, pathway, year, chp_treatment) * net_removal_scale(
        case, pathway, year
    )


def static_activity_contributions_per_net_tonne(
    case: str,
    pathway: str,
    year: int,
    chp_treatment: str,
) -> tuple[tuple[str, float], ...]:
    """Return contributions per physical net tonne stored from the atmosphere."""

    matches = [
        row
        for row in static_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and int(row["year"]) == int(year)
        and row["chp_treatment"] == chp_treatment
    ]
    if len(matches) != 1:
        raise LookupError(
            "Expected one static result for activity contributions: "
            f"{case}, {pathway}, {year}, {chp_treatment}; found {len(matches)}"
        )
    provenance_id = matches[0]["provenance_id"]
    scale = net_removal_scale(case, pathway, year)
    contributions = [
        (row["contributor"], float(row["score"]) * scale)
        for row in static_contribution_rows()
        if row["provenance_id"] == provenance_id
        and row["contributor_type"] == "activity"
    ]
    if not contributions:
        raise LookupError(f"No activity contributions for {provenance_id}.")
    return tuple(contributions)


@lru_cache(maxsize=1)
def temporal_rows() -> tuple[dict[str, str], ...]:
    with TEMPORAL_RESULTS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=1)
def fair_rows() -> tuple[dict[str, str], ...]:
    with FAIR_RESULTS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=1)
def scenario_sector_rows() -> tuple[dict[str, str], ...]:
    """Return reviewed Northern European background intensities for the slides."""

    with SCENARIO_SECTOR_INDICATORS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


def scenario_sector_series(sector: str, pathway: str) -> tuple[tuple[int, float], ...]:
    """Return one scenario trajectory for a named background sector."""

    matches = [
        (int(row["year"]), float(row["score"]))
        for row in scenario_sector_rows()
        if row["sector"] == sector and row["pathway"] == pathway
    ]
    if not matches:
        raise LookupError(f"No prospective sector result for {sector}, {pathway}.")
    return tuple(sorted(matches))


@lru_cache(maxsize=1)
def scenario_sector_mix_rows() -> tuple[dict[str, str], ...]:
    """Return aggregate premise-generated shares for Northern European markets."""

    with SCENARIO_SECTOR_MIXES.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


def scenario_sector_mix(
    sector: str, pathway: str, year: int
) -> tuple[tuple[str, float], ...]:
    """Return ordered technology shares for one sector, pathway and year."""

    matches = [
        (row["category"], float(row["share"]))
        for row in scenario_sector_mix_rows()
        if row["sector"] == sector
        and row["pathway"] == pathway
        and int(row["year"]) == int(year)
    ]
    if not matches:
        raise LookupError(f"No sector mix for {sector}, {pathway}, {year}.")
    return tuple(matches)


@lru_cache(maxsize=1)
def lifetime_rows() -> tuple[dict[str, str], ...]:
    """Return annual and lifetime-normalized 2030 plant-cohort results."""

    with LIFETIME_RESULTS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=1)
def lifetime_contribution_rows() -> tuple[dict[str, str], ...]:
    with LIFETIME_CONTRIBUTIONS.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


def lifetime_annual_series(case: str, pathway: str) -> tuple[tuple[int, float], ...]:
    """Return annual GWP100 per physical net tonne stored for one plant cohort."""

    matches = [
        (int(row["operation_year"]), float(row["score_per_net_tonne_kg_co2eq"]))
        for row in lifetime_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and row["period"] == "annual"
    ]
    if not matches:
        raise LookupError(f"No lifetime annual series for {case}, {pathway}.")
    return tuple(sorted(matches))


def lifetime_score_per_net_tonne(case: str, pathway: str) -> float:
    matches = [
        float(row["score_per_net_tonne_kg_co2eq"])
        for row in lifetime_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and row["period"] == "lifetime"
    ]
    if len(matches) != 1:
        raise LookupError(
            f"Expected one lifetime score for {case}, {pathway}; found {len(matches)}."
        )
    return matches[0]


def lifetime_net_storage_tonnes(case: str) -> float:
    matches = {
        float(row["denominator_net_stored_tonnes"])
        for row in lifetime_rows()
        if row["case"] == case and row["period"] == "lifetime"
    }
    if len(matches) != 1:
        raise LookupError(f"Expected one physical lifetime storage value for {case}.")
    return matches.pop()


def lifetime_process_contributions(
    case: str, pathway: str, operation_year: int | None = None
) -> tuple[tuple[str, float], ...]:
    """Return closing process contributions per physical net tonne stored."""

    period = "annual" if operation_year is not None else "lifetime"
    matches = [
        (row["contributor"], float(row["score_per_net_tonne_kg_co2eq"]))
        for row in lifetime_contribution_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and row["period"] == period
        and row["view"] == "process"
        and (
            operation_year is None or int(row["operation_year"]) == int(operation_year)
        )
    ]
    if not matches:
        label = "lifetime" if operation_year is None else str(operation_year)
        raise LookupError(f"No process contributions for {case}, {pathway}, {label}.")
    return tuple(matches)


@lru_cache(maxsize=1)
def cohort_temporal_score_rows() -> tuple[dict[str, str], ...]:
    """Return root-attributed GWP100 scores for the routed 2030 cohorts."""

    with COHORT_TEMPORAL_SCORES.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


def cohort_temporal_score_series(
    case: str, normalization: str = "cohort"
) -> tuple[tuple[str, tuple[tuple[int, float], ...]], ...]:
    """Return year-resolved scores by TRAILS responsible root activity."""

    value_field = {
        "cohort": "score_total_kg_co2eq",
        "per_tonne": "score_per_net_tonne_kg_co2eq",
    }.get(normalization)
    if value_field is None:
        raise ValueError(f"Unknown temporal-score normalization: {normalization}.")
    grouped: dict[str, dict[int, float]] = {}
    for row in cohort_temporal_score_rows():
        if row["case"] != case:
            continue
        contributor = " | ".join(
            value
            for value in (
                row["contributor"],
                row["reference_product"],
                row["location"],
            )
            if value
        )
        year = int(row["impact_year"])
        annual = grouped.setdefault(contributor, {})
        annual[year] = annual.get(year, 0.0) + float(row[value_field])
    if not grouped:
        raise LookupError(f"No routed cohort temporal scores for {case}.")
    ordered = sorted(
        grouped.items(),
        key=lambda item: sum(abs(value) for value in item[1].values()),
        reverse=True,
    )
    return tuple(
        (contributor, tuple(sorted(values.items()))) for contributor, values in ordered
    )


def cohort_temporal_total(case: str, normalization: str = "cohort") -> float:
    """Return the time-integrated GWP100 score for one routed plant cohort."""

    return sum(
        value
        for _, series in cohort_temporal_score_series(case, normalization)
        for _, value in series
    )


def cohort_temporal_contributor_total(
    case: str, contributor: str, normalization: str = "cohort"
) -> float:
    """Return one exact routed contributor total without altering source results."""

    matches = [
        sum(value for _year, value in series)
        for label, series in cohort_temporal_score_series(case, normalization)
        if label == contributor
    ]
    if len(matches) != 1:
        raise LookupError(
            f"Expected one routed contributor named {contributor!r} for {case}; "
            f"found {len(matches)}."
        )
    return matches[0]


def forest_pool_sensitivity(scope: str = "routed") -> dict[str, float | str]:
    """Screen omitted post-harvest forest pools against the BECCS/DACCS gap.

    The positive correction is expressed as a fraction of the magnitude of the
    modeled forest-regrowth benefit. It is a transparent perturbation of the
    reviewed results, not a claim about the size of residue, root or soil-carbon
    losses at a particular site.
    """

    fraction = float(
        forest_pool_sensitivity_settings()["stress_test_fraction_of_gross_regrowth"]
    )
    if scope == "static":
        treatment = "new CHP+CCS vs standing forest and Northern European energy"
        baseline_beccs = static_score("BECCS", "SSP2-NPi", 2025, treatment)
        comparator_daccs = static_score("DACCS", "SSP2-NPi", 2025, "not applicable")
        gross_regrowth = abs(
            float(
                process_step_attribution()["BECCS"][
                    "process_groups_kg_co2eq_per_net_tonne"
                ]["Forest regrowth"]
            )
        )
    elif scope == "routed":
        baseline_beccs = cohort_temporal_total("BECCS", "per_tonne")
        comparator_daccs = cohort_temporal_total("DACCS", "per_tonne")
        gross_regrowth = abs(
            cohort_temporal_contributor_total("BECCS", "Forest regrowth", "per_tonne")
        )
    else:
        raise ValueError(f"Unknown forest-pool sensitivity scope: {scope}.")

    break_even_correction = max(comparator_daccs - baseline_beccs, 0.0)
    stress_test_correction = fraction * gross_regrowth
    return {
        "scope": scope,
        "baseline_beccs": baseline_beccs,
        "comparator_daccs": comparator_daccs,
        "gross_regrowth": gross_regrowth,
        "break_even_correction": break_even_correction,
        "break_even_fraction": break_even_correction / gross_regrowth,
        "stress_test_fraction": fraction,
        "stress_test_correction": stress_test_correction,
        "stress_test_beccs": baseline_beccs + stress_test_correction,
    }


@lru_cache(maxsize=1)
def cohort_fair_response_rows() -> tuple[dict[str, str], ...]:
    """Return FaIR responses attributed by process and elementary flow."""

    with COHORT_FAIR_RESPONSES.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=1)
def _cohort_fair_response_index() -> (
    dict[tuple[str, str, str, float], dict[str, dict[int, float]]]
):
    """Index the larger response table once so slide toggles stay immediate."""

    indexed: dict[tuple[str, str, str, float], dict[str, dict[int, float]]] = {}
    for row in cohort_fair_response_rows():
        key = (
            row["case"],
            row["metric"],
            row["contribution_view"],
            float(row["quantile"]),
        )
        contributor = row["contributor"]
        year = int(row["response_year"])
        annual = indexed.setdefault(key, {}).setdefault(contributor, {})
        annual[year] = annual.get(year, 0.0) + float(row["value_per_net_tonne"])
    return indexed


@lru_cache(maxsize=None)
def cohort_fair_response_series(
    case: str,
    metric: str,
    contribution_view: str,
    quantile: float = 50.0,
) -> tuple[tuple[str, tuple[tuple[int, float], ...]], ...]:
    """Return one cohort's per-net-tonne FaIR response by contributor."""

    grouped = _cohort_fair_response_index().get(
        (case, metric, contribution_view, float(quantile)), {}
    )
    if not grouped:
        raise LookupError(
            "No cohort FaIR response for "
            f"{case}, {metric}, {contribution_view}, q={quantile}."
        )
    ordered = sorted(
        grouped.items(),
        key=lambda item: sum(abs(value) for value in item[1].values()),
        reverse=True,
    )
    return tuple(
        (contributor, tuple(sorted(values.items()))) for contributor, values in ordered
    )


@lru_cache(maxsize=None)
def cohort_fair_total_series(
    case: str,
    metric: str,
    contribution_view: str,
    quantile: float = 50.0,
) -> tuple[tuple[int, float], ...]:
    """Return the net FaIR trajectory after summing all contributors."""

    totals: dict[int, float] = {}
    for _contributor, series in cohort_fair_response_series(
        case, metric, contribution_view, quantile
    ):
        for year, value in series:
            totals[year] = totals.get(year, 0.0) + value
    return tuple(sorted(totals.items()))


@lru_cache(maxsize=1)
def co2_reference_pulse_rows() -> tuple[dict[str, str], ...]:
    """Return scenario-specific FaIR responses to the reference CO2 pulse."""

    with CO2_REFERENCE_PULSE.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream))


@lru_cache(maxsize=None)
def co2_reference_pulse_series(
    metric: str,
    quantile: float = 50.0,
    pulse_year: int = 2030,
) -> tuple[tuple[int, float], ...]:
    """Return the response to one kilogram of CO2 in one reference year."""

    values = {
        int(row["response_year"]): float(row["value_per_kg_co2_pulse"])
        for row in co2_reference_pulse_rows()
        if row["metric"] == metric
        and float(row["quantile"]) == float(quantile)
        and int(row["pulse_year"]) == int(pulse_year)
    }
    if not values:
        raise LookupError(
            "No reference-pulse response for "
            f"{metric}, quantile {quantile}, pulse year {pulse_year}."
        )
    return tuple(sorted(values.items()))


def _integrate_annual_window(
    series: tuple[tuple[int, float], ...],
    start_year: int,
    end_year: int,
) -> float:
    values = dict(series)
    if end_year <= start_year:
        raise ValueError("The pulse-equivalence window must span at least one year.")
    if not values:
        raise LookupError("Response series is empty.")
    first_year, last_year = min(values), max(values)
    missing_inside_series = [
        year
        for year in range(max(start_year, first_year), min(end_year, last_year) + 1)
        if year not in values
    ]
    if missing_inside_series:
        raise LookupError(
            "Response series is missing internal years "
            f"{missing_inside_series[0]} through {missing_inside_series[-1]}."
        )
    # Sparse response exports begin with their first non-zero year. Years before
    # project construction (and any years beyond a completed response) are
    # physically zero rather than missing data.
    return sum(
        (values.get(year, 0.0) + values.get(year + 1, 0.0)) / 2.0
        for year in range(start_year, end_year)
    )


@lru_cache(maxsize=None)
def cohort_co2_pulse_equivalent_median_trajectory(
    case: str,
    metric: str,
    start_year: int,
    end_year: int,
    quantile: float = 50.0,
    reference_year: int = 2030,
) -> float:
    """Return a diagnostic ratio of the median response trajectories.

    The dashboard uses TRAILS' configuration-first summary from the pulse grid.
    This alternate ratio is retained only to quantify the effect of taking a
    ratio after first summarizing each response trajectory.
    """

    system_integral = _integrate_annual_window(
        cohort_fair_total_series(case, metric, "process", quantile),
        int(start_year),
        int(end_year),
    )
    reference_integral = _integrate_annual_window(
        co2_reference_pulse_series(metric, quantile, int(reference_year)),
        int(start_year),
        int(end_year),
    )
    if reference_integral == 0.0:
        raise ZeroDivisionError("Reference CO2-pulse response integrates to zero.")
    return system_integral / reference_integral


@lru_cache(maxsize=1)
def cohort_pulse_equivalence_grid():
    """Return the TRAILS configuration-first pulse-equivalence grid."""

    import numpy as np

    with np.load(COHORT_PULSE_EQUIVALENCE_GRID) as source:
        return {
            "years": tuple(int(value) for value in source["years"].tolist()),
            "cases": tuple(str(value) for value in source["cases"].tolist()),
            "metrics": tuple(str(value) for value in source["metrics"].tolist()),
            "values": source["median_kg_co2_per_net_tonne"].copy(),
            "metadata_json": str(source["metadata_json"].item()),
        }


@lru_cache(maxsize=None)
def cohort_co2_pulse_equivalent(
    case: str,
    metric: str,
    start_year: int,
    end_year: int,
    quantile: float = 50.0,
    reference_year: int = 2030,
) -> float:
    """Return TRAILS-convention kg CO2-equivalent per net tonne.

    Ratios are calculated for each of the 841 calibrated FaIR configurations
    before taking the median, matching
    ``trails.fair_rf.run_fair_co2_pulse_equivalents``.
    """

    import numpy as np

    if float(quantile) != 50.0:
        raise ValueError("The interactive TRAILS grid currently stores its median.")
    grid = cohort_pulse_equivalence_grid()
    try:
        case_index = grid["cases"].index(str(case))
        metric_index = grid["metrics"].index(str(metric))
        start_index = grid["years"].index(int(start_year))
        reference_index = grid["years"].index(int(reference_year))
        end_index = grid["years"].index(int(end_year))
    except ValueError as error:
        raise LookupError(
            "No TRAILS pulse-equivalence grid entry for "
            f"{case}, {metric}, {start_year}, {reference_year}, {end_year}."
        ) from error
    value = float(
        grid["values"][
            case_index,
            metric_index,
            start_index,
            reference_index,
            end_index,
        ]
    )
    if not np.isfinite(value):
        raise LookupError(
            "The pulse year must lie strictly inside the integration window."
        )
    return value


def temporal_total(
    case: str,
    pathway: str,
    commissioning_year: int,
    forest_case: str,
) -> float:
    matches = [
        row
        for row in temporal_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and int(row["commissioning_year"]) == int(commissioning_year)
        and row["forest_case"] == forest_case
    ]
    if not matches:
        raise LookupError(
            "No temporal result for "
            f"{case}, {pathway}, {commissioning_year}, {forest_case}."
        )
    return sum(float(row["score"]) for row in matches)


def fair_series(
    case: str,
    pathway: str,
    commissioning_year: int,
    forest_case: str,
    metric: str,
    statistic: str = "median",
) -> tuple[tuple[int, float], ...]:
    matches = [
        (int(row["year"]), float(row["value"]))
        for row in fair_rows()
        if row["case"] == case
        and row["pathway"] == pathway
        and int(row["commissioning_year"]) == int(commissioning_year)
        and row["forest_case"] == forest_case
        and row["metric"] == metric
        and row["statistic"] == statistic
    ]
    if not matches:
        raise LookupError(
            "No FaIR result for "
            f"{case}, {pathway}, {commissioning_year}, {forest_case}, {metric}."
        )
    return tuple(sorted(matches))


def fair_series_per_net_tonne(
    case: str,
    pathway: str,
    commissioning_year: int,
    forest_case: str,
    metric: str,
    statistic: str = "median",
) -> tuple[tuple[int, float], ...]:
    """Return a FaIR trajectory normalized to one net tonne removed."""

    scale = net_removal_scale(case, pathway, commissioning_year)
    return tuple(
        (year, value * scale)
        for year, value in fair_series(
            case,
            pathway,
            commissioning_year,
            forest_case,
            metric,
            statistic,
        )
    )


def fair_value(
    case: str,
    pathway: str,
    commissioning_year: int,
    forest_case: str,
    metric: str,
    *,
    statistic: str = "median",
    year: int = 2100,
) -> float:
    matches = [
        value
        for result_year, value in fair_series(
            case,
            pathway,
            commissioning_year,
            forest_case,
            metric,
            statistic,
        )
        if result_year == int(year)
    ]
    if len(matches) != 1:
        raise LookupError(f"Expected one FaIR value at {year}; found {len(matches)}.")
    return matches[0]


def fair_value_per_net_tonne(
    case: str,
    pathway: str,
    commissioning_year: int,
    forest_case: str,
    metric: str,
    *,
    statistic: str = "median",
    year: int = 2100,
) -> float:
    """Return one FaIR result normalized to one net tonne removed."""

    return fair_value(
        case,
        pathway,
        commissioning_year,
        forest_case,
        metric,
        statistic=statistic,
        year=year,
    ) * net_removal_scale(case, pathway, commissioning_year)
