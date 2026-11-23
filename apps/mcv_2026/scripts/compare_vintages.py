"""Measure 2030 cohort routing and climate results for one TRAILS background."""

from __future__ import annotations

import argparse
from collections import OrderedDict, defaultdict
from dataclasses import replace
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from apps.mcv_2026.scripts.cohort_timing import (
    apply_cohort_timing,
    extend_inventory_calendar,
)
from apps.setac_2026.scripts.regenerate_results import sha256


def activity_identity(model, year, index):
    label = str(model._map_year_to_template_year(year))
    item = model.activity_indices[label][index]
    return {key: item[key] for key in ("name", "reference product", "location")}


class RoutingQueue:
    """Combine demands for identical states during fixed-depth, unpruned routing."""

    def __init__(self):
        self.pending = OrderedDict()

    def append(self, item):
        year, activity, amount, depth, root, dated = item
        key = year, activity, depth, root, dated
        self.pending[key] = self.pending.get(key, 0.0) + amount

    def popleft(self):
        (year, activity, depth, root, dated), amount = self.pending.popitem(last=False)
        return year, activity, amount, depth, root, dated

    def __bool__(self):
        return bool(self.pending)


def construction_routes(model):
    """Summarize graph links that actually use a supplier build-year profile."""
    dated_pairs = {
        (activity, supplier)
        for (_, activity, supplier), exchange in model.temporal_technosphere_exchanges.items()
        if getattr(exchange, "has_build_year_weights", False)
    }
    years = defaultdict(set)
    depths = {}
    seen = 0
    for source, target, edge in model.graph.edges(data=True):
        if not edge["amount"]:
            continue
        service_year, depth, activity = source[0], source[1], source[-1]
        supplier = target[-1]
        key = activity, supplier
        if key not in dated_pairs:
            continue
        exchange = model._get_tech_temporal_exchange(service_year, activity, supplier)
        if not getattr(exchange, "has_build_year_weights", False):
            continue
        seen += 1
        years[key].add(int(target[0]))
        depths[key] = min(depths.get(key, depth + 1), depth + 1)

    examples = [
        {
            "activity": activity_identity(model, 2030, activity),
            "construction_supplier": activity_identity(model, 2030, supplier),
            "first_build_year": min(years[activity, supplier]),
            "last_build_year": max(years[activity, supplier]),
            "build_years": len(years[activity, supplier]),
            "first_routing_depth": depths[activity, supplier],
        }
        for activity, supplier in sorted(
            years, key=lambda key: (-len(years[key]), depths[key], key)
        )[:12]
    ]
    return {
        "edges": seen,
        "activity_supplier_pairs": len(years),
        "first_build_year": min((min(value) for value in years.values()), default=None),
        "last_build_year": max((max(value) for value in years.values()), default=None),
        "examples": examples,
    }


def first_reachable_construction(model, year, root, amount, cutoff, max_depth):
    """Find the first dated supplier without building a deeper full cohort graph."""
    start_index = model.scenario_index[str(year)]
    amount = model._activity_amount_from_product_demand(start_index, root, amount)
    frontier = {(year, root): (amount, ((year, root),))}
    visited = set(frontier)
    for depth in range(1, max_depth + 1):
        next_frontier = {}
        for (source_year, activity), (demand, path) in frontier.items():
            children = model._expand_temporal_child_demands_fast(
                year=source_year,
                act_idx=activity,
                amount=demand,
                use_temporal_distributions=True,
                debug=False,
                track_build_date=True,
            )
            for (raw_year, supplier, dated), child_amount in children.items():
                if abs(child_amount) < cutoff:
                    continue
                child = (model._map_year_to_scenario_year(raw_year), supplier)
                child_path = path + (child,)
                if dated:
                    return {
                        "depth": depth,
                        "path": [
                            {
                                "year": event_year,
                                **activity_identity(model, event_year, index),
                            }
                            for event_year, index in child_path
                        ],
                    }
                if child not in visited and (
                    child not in next_frontier
                    or abs(child_amount) > abs(next_frontier[child][0])
                ):
                    next_frontier[child] = child_amount, child_path
        frontier = next_frontier
        visited.update(frontier)
    return None


def clear_vintage_construction(model):
    """Use service-year construction for exchanges with IAM build-year profiles."""
    exchanges = model.temporal_technosphere_exchanges
    for key, exchange in list(exchanges.items()):
        role = getattr(exchange, "construction_timing", "")
        if role in {"dated", "zero_fleet"}:
            del exchanges[key]
        elif role == "pass_through":
            exchanges[key] = replace(exchange, construction_timing="")
    model._has_construction_timing = False


def run(
    workspace,
    package,
    output,
    cases,
    depth,
    first_year,
    routing_only,
    probe_depth,
    without_vintages,
):
    from importlib import import_module

    sys.path.insert(0, str(workspace))
    from datapackage import Package
    import trails
    from trails import Trails
    from trails.fair_rf import run_fair_co2_pulse_equivalents

    from scripts import calculate_cohort_temporal_scores as temporal
    from scripts import generate_routing_graphs as routing
    from workshop.lifetime import cohort_cases
    from workshop.temporal import enable_signed_technosphere_routing

    config_path = workspace / "data/inventories/parameters.json"
    config = json.loads(config_path.read_text())
    foreground = config_path.parent / "generated/lcss2026-foreground.xlsx"
    cohort = foreground.with_name("lcss2026-routing-cohorts.xlsx")
    year = temporal.START_YEAR
    cohorts = cohort_cases(config, commissioning_year=year)
    background = Package(str(package))
    identities = {
        (scenario["model"], scenario["pathway"])
        for scenario in background.descriptor["scenarios"]
    }
    if len(identities) != 1:
        raise ValueError("The TRAILS package must contain one IAM pathway")
    model_name, pathway = identities.pop()
    if model_name != "remind-eu" or pathway not in {"SSP2-NPi", "SSP2-PkBudg1000"}:
        raise ValueError(f"Unexpected MCV background: {model_name}/{pathway}")
    fair_scenario = f"REMIND|{pathway}"
    router = import_module("trails.trails")
    report = {
        "package_sha256": sha256(package),
        "pathway": pathway,
        "foreground_sha256": sha256(foreground),
        "cohort_foreground_sha256": sha256(cohort),
        "config_sha256": sha256(config_path),
        "trails_version": trails.__version__,
        "trails_routing_source_sha256": sha256(
            Path(trails.__file__).with_name("trails.py")
        ),
        "cohort_year": year,
        "maximum_routing_depth": depth,
        "minimum_routing_amount": 0.0,
        "routing_calendar_first_year": first_year,
        "fair_scenario": fair_scenario,
        "pulse_window": [2020, 2100],
        "reference_pulse_year": 2030,
        "iam_construction_profiles": not without_vintages,
        "attribution": "TRAILS native root attribution",
        "cases": {},
    }
    for case in cases:
        print(f"{case} at depth {depth}", flush=True)
        with Trails(
            background,
            interpolate_annual=True,
            cache_interpolation=False,
            interpolation_start_year_offset=0,
            interpolation_end_year_offset=0,
            ei_version="3.12",
        ) as model:
            model.import_excel_inventory([foreground, cohort])
            diagnostics = model.import_diagnostics
            if diagnostics.get("unlinked") or diagnostics.get("new_flows"):
                raise ValueError(f"Foreground import failed for {case}: {diagnostics}")
            extend_inventory_calendar(
                model,
                first_year,
                model.max_year + routing.TECHNOSPHERE_END_YEAR_OFFSETS[case],
            )
            if without_vintages:
                clear_vintage_construction(model)
            apply_cohort_timing(model, case, year, config, routing)
            enable_signed_technosphere_routing(model)
            root = routing.find_activity(model, year, routing.ROOTS[case])
            root_amount = routing.cohort_root_amount(case, config, year)
            print(f"Routing {case} from {year}", flush=True)
            # A full depth is consumed before the next starts. With pruning
            # disabled, the contributions entering each state sum linearly.
            with patch.object(router, "deque", RoutingQueue):
                model.temporal_routing(
                    start_year=year,
                    start_act_idx=root,
                    amount=root_amount,
                    max_depth=depth,
                    adaptive_relative_score_cutoff=None,
                    min_amount=0.0,
                    attribute_to_roots=True,
                    show_progress=False,
                )
            result = {"construction_routes": construction_routes(model)}
            report["cases"][case] = result
            print(
                json.dumps(
                    {
                        key: value
                        for key, value in result["construction_routes"].items()
                        if key != "examples"
                    }
                ),
                flush=True,
            )
            output.write_text(json.dumps(report, indent=2) + "\n")
            if (
                probe_depth
                and model._has_construction_timing
                and not result["construction_routes"]["edges"]
            ):
                result["first_reachable_construction"] = first_reachable_construction(
                    model, year, root, root_amount, routing.ROUTING_MIN_AMOUNT, probe_depth
                )
                result["maximum_probe_depth"] = probe_depth
                output.write_text(json.dumps(report, indent=2) + "\n")
            if routing_only:
                continue

            model.lci(
                attribute_to_roots=True,
                solver_mode="iterative",
                iterative_rtol=1e-5,
                iterative_maxiter=500,
                inventory_backend="factorized",
                show_progress=True,
            )
            model.lcia(methods=[temporal.METHOD], ei_version="3.12")
            denominator = cohorts[case].lifetime_net_stored_kg / 1000
            result["gwp100_kg_per_net_tonne"] = float(model.scores.sum()) / denominator
            pulse = run_fair_co2_pulse_equivalents(
                model,
                scenario=fair_scenario,
                reference_pulse_year=2030,
                window_start=2020,
                window_end=2100,
                show_progress=True,
            )["co2_pulse_equivalent"]
            result["pulse_kg_per_net_tonne"] = {
                key: float(pulse["integrated_rf"][key]) / denominator
                for key in ("median", "p025", "p975")
            }
            result["fair_configurations"] = len(pulse["diagnostics"]["config"])
            output.write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--cases", nargs="+", choices=("BECCS", "DACCS"), default=("DACCS", "BECCS")
    )
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--first-year", type=int, default=1880)
    parser.add_argument("--routing-only", action="store_true")
    parser.add_argument("--probe-depth", type=int, default=8)
    parser.add_argument("--without-vintages", action="store_true")
    args = parser.parse_args()
    if args.depth < 1:
        parser.error("--depth must be positive")
    run(
        args.workspace.resolve(),
        args.package.resolve(),
        args.output.resolve(),
        args.cases,
        args.depth,
        args.first_year,
        args.routing_only,
        args.probe_depth,
        args.without_vintages,
    )


if __name__ == "__main__":
    main()
