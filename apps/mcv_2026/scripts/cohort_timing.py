"""Combine the reviewed project schedules with IAM-dated supplier construction."""

from math import isclose


def apply_cohort_timing(model, case, year, config, routing):
    dated = model.temporal_technosphere_exchanges
    first_construction_year = min(
        (
            int(key[0]) + int(min(exchange.offsets))
            for key, exchange in dated.items()
            if getattr(exchange, "has_build_year_weights", False)
        ),
        default=model.min_year,
    )
    if first_construction_year < model.min_year:
        extend_inventory_calendar(model, first_construction_year, model.max_year)

    if case == "DACCS":
        routing.apply_daccs_cohort_timing(model, year, config)
        return

    from trails.temporal_distributions import TemporalExchange

    vintages = {}
    for key, exchange in dated.items():
        role = getattr(exchange, "construction_timing", "")
        if role in {"dated", "zero_fleet"}:
            vintages[key] = exchange
        elif role == "pass_through":
            # Preserve the route marker and BECCS's same-year background rule.
            # A pass-through exchange can also carry a generic age distribution.
            vintages[key] = TemporalExchange(
                1, 0.0, None, 0, 0, construction_timing="pass_through"
            )
    forest = config["beccs"]["forest_feedstock"]
    routing.reset_background_temporal_exchanges(
        model, preserve_activity_names={forest["name"], forest["regrowth_name"]}
    )
    for key, exchange in vintages.items():
        dated.setdefault(key, exchange)
    routing.apply_beccs_cohort_timing(model, year, config)
    profile = forest.get("post_harvest_uptake_profile")
    if profile is not None:
        label = str(model._map_year_to_template_year(year))
        regrowth = routing.find_activity(model, year, {
            "name": forest["regrowth_name"],
            "reference product": forest["regrowth_reference_product"],
            "location": forest["location"],
        })
        exchange, = [
            exchange for (snapshot, activity, _), exchange
            in model.temporal_biosphere_exchanges.items()
            if snapshot == label and activity == regrowth
        ]
        offsets, weights = zip(*model._get_td_offsets(tex=exchange, debug=False), strict=True)
        if list(offsets) != profile["offsets"] or any(
            not isclose(actual, expected, rel_tol=1e-12)
            for actual, expected in zip(weights, profile["weights"], strict=True)
        ):
            raise ValueError("TRAILS altered the annual BECCS regrowth profile")


def extend_inventory_calendar(model, first_year, last_year):
    """Keep event dates outside the IAM anchors using the endpoint matrices."""
    import numpy as np

    if first_year > model.min_year or last_year < model.max_year:
        raise ValueError("The routing calendar must contain all IAM inventory years")
    first_index = model.scenario_index[str(model.min_year)]
    last_index = model.scenario_index[str(model.max_year)]
    for year in range(first_year, model.min_year):
        model.scenario_index[str(year)] = first_index
    for year in range(model.max_year + 1, last_year + 1):
        model.scenario_index[str(year)] = last_index
    model.min_year, model.max_year = first_year, last_year
    model.years_int = np.arange(first_year, last_year + 1)
    model.scenario_labels = [str(year) for year in model.years_int]
    model._scenario_year_map_cache.clear()
