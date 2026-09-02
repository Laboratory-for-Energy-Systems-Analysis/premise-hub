from __future__ import annotations

import unittest
from pathlib import Path

from dash import dcc, html

from apps.workshop.app import _make_print_safe, app, server
from apps.workshop.workshop.config import (
    ANONYMOUS_ORDER,
    ANONYMOUS_SLIDE,
    APPENDIX_SLIDE_COUNT,
    APPENDIX_SLIDE_TITLES,
    APPENDIX_START_SLIDE,
    BACKUP_LINKS,
    CHAPTERS,
    CORE_SCENARIOS,
    CORE_LAST_SLIDE,
    CORE_SLIDE_COUNT,
    CORE_SLIDE_TITLES,
    LAST_SLIDE,
    RESULT_TRACER_SLIDE,
    SLIDE_TITLES,
)
from apps.workshop.workshop.data import (
    context_series,
    iam_region_topologies,
    image_region_mapping,
    image_electricity_chain,
    image_energy_layers,
    image_end_use_transformations,
    image_total_energy_chain,
    lcia_contributions,
    lcia_results,
    mechanics_series,
    pathways,
    premise_mapping_counts,
    remind_eu_region_mapping,
    sector_mix,
)
from apps.workshop.workshop.figures import (
    CAPSTONE_CASE_SPECS,
    CAPSTONE_INDICATOR_SPECS,
    carbon_budget_figure,
    capstone_contribution_figure,
    capstone_lcia_trajectory_figure,
    capstone_signal_figure,
    cdr_overshoot_summary_figure,
    cmip7_gmst_trajectory_figure,
    commodity_gwp_figure,
    controlled_comparison_figure,
    energy_emissions_change_figure,
    energy_accounting_example_figure,
    end_use_transformation_figure,
    final_energy_layer_figure,
    ghg_gas_figure,
    ghg_region_figure,
    ghg_sector_figure,
    iam_mechanics_figure,
    image_geography_figure,
    lcia_evidence_figure,
    model_coverage_figure,
    premise_mapping_counts_figure,
    primary_energy_layer_figure,
    rcp_gmst_trajectory_figure,
    remind_eu_geography_figure,
    same_net_zero_date_figure,
    sector_mitigation_potential_figure,
    sector_snapshot,
    secondary_energy_layer_figure,
    ssp_baseline_comparison_figure,
    steel_causal_chain_figure,
    total_energy_system_figure,
)
from apps.workshop.workshop.slides import render_slide, slide_number


class WorkshopSmokeTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        response = server.test_client().get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_pdf_export_controls_are_present(self) -> None:
        component_ids = set()

        def collect_ids(component) -> None:
            component_id = getattr(component, "id", None)
            if component_id is not None:
                component_ids.add(str(component_id))
            children = getattr(component, "children", None)
            if isinstance(children, (list, tuple)):
                for child in children:
                    collect_ids(child)
            elif children is not None:
                collect_ids(children)

        collect_ids(app.layout)
        self.assertTrue(
            {
                "backup-return-store",
                "pdf-export-button",
                "pdf-export-trigger",
                "print-deck",
                "slide-number",
            }
            <= component_ids
        )

        header = next(
            child
            for child in app.layout.children
            if getattr(child, "className", None) == "app-header"
        )
        footer = next(
            child
            for child in app.layout.children
            if getattr(child, "className", None) == "app-footer"
        )
        self.assertFalse(
            any(
                getattr(child, "id", None) == "pdf-export-button"
                for child in header.children
            )
        )
        self.assertTrue(
            any(
                getattr(child, "id", None) == "pdf-export-button"
                for child in footer.children
            )
        )

    def test_slide_numbers_distinguish_core_and_backup_decks(self) -> None:
        self.assertEqual(slide_number(0), "01 / 33")
        self.assertEqual(slide_number(CORE_LAST_SLIDE), "33 / 33")
        self.assertEqual(slide_number(APPENDIX_START_SLIDE), "B01 / 18")
        self.assertEqual(slide_number(LAST_SLIDE), "B18 / 18")

    def test_ssp_baseline_legend_and_challenge_labels(self) -> None:
        figure = ssp_baseline_comparison_figure("population")
        self.assertEqual(figure.layout.legend.y, 1.06)

        rendered = render_slide(9, 1, {"A": 0, "B": 0, "C": 0, "D": 0})

        def text_content(component) -> str:
            if isinstance(component, str):
                return component
            children = getattr(component, "children", None)
            if isinstance(children, (list, tuple)):
                return " ".join(text_content(child) for child in children)
            if children is None:
                return ""
            return text_content(children)

        text = text_content(rendered)
        self.assertIn("mitigation challenge low", text)
        self.assertIn("adaptation challenge high", text)

    def test_cmip7_slide_links_to_recommended_reading(self) -> None:
        rendered = render_slide(12, 1, {"A": 0, "B": 0, "C": 0, "D": 0})
        links = []

        def collect_links(component) -> None:
            href = getattr(component, "href", None)
            if href:
                links.append(href)
            children = getattr(component, "children", None)
            if not isinstance(children, (list, tuple)):
                children = [] if children is None else [children]
            for child in children:
                collect_links(child)

        collect_links(rendered)
        self.assertIn(
            "https://www.carbonbrief.org/explainer-the-cmip7-emissions-"
            "scenarios-and-how-they-explore-future-climate-change",
            links,
        )

    def test_print_slide_trees_do_not_duplicate_callback_ids(self) -> None:
        tree = html.Div(
            [
                html.Button("Choice", id={"type": "choice", "value": "A"}),
                dcc.Graph(id="chart"),
            ]
        )
        _make_print_safe(tree)
        self.assertIsNone(tree.children[0].id)
        self.assertTrue(tree.children[0].disabled)
        self.assertIsNone(tree.children[1].id)

    def test_core_scenario_contract(self) -> None:
        self.assertEqual(CORE_SCENARIOS, ["SSP1-L", "SSP2-VLHO", "SSP2-M", "SSP3-H"])
        self.assertEqual(ANONYMOUS_ORDER, CORE_SCENARIOS)
        frame = pathways()
        image = frame[frame["model"] == "image"]
        self.assertTrue(set(ANONYMOUS_ORDER) <= set(image["scenario"]))
        for sector in [
            "Population",
            "Gross Domestic Product",
            "Carbon Dioxide emissions",
            "GMST increase",
            "Electricity",
            "Steel",
        ]:
            series = context_series(sector, ANONYMOUS_ORDER)
            for scenario in ANONYMOUS_ORDER:
                years = set(series.loc[series["scenario"] == scenario, "year"])
                self.assertTrue({2020, 2040, 2060} <= years, (scenario, sector))

    def test_missing_cdr_is_not_zero_filled(self) -> None:
        cdr = context_series("Carbon Dioxide Removal", ANONYMOUS_ORDER)
        self.assertNotIn("SSP3-H", set(cdr["scenario"]))

    def test_all_presenter_states_render(self) -> None:
        votes = {"A": 1, "B": 2, "C": 3, "D": 4}
        for slide in range(LAST_SLIDE + 1):
            rendered = render_slide(
                slide,
                1,
                votes,
                {"sector": "Electricity", "year": 2060, "mode": "share"},
                {
                    "case": "steel",
                    "scenario": "SSP2-VLHO",
                    "year": 2060,
                    "indicator": "climate",
                },
            )
            self.assertIsNotNone(rendered)

    def test_backup_links_have_a_reversible_navigation_control(self) -> None:
        def has_pattern_id(component, pattern_type: str) -> bool:
            component_id = getattr(component, "id", None)
            if (
                isinstance(component_id, dict)
                and component_id.get("type") == pattern_type
            ):
                return True
            children = getattr(component, "children", None)
            if children is None:
                return False
            if not isinstance(children, (list, tuple)):
                children = [children]
            return any(
                has_pattern_id(child, pattern_type)
                for child in children
                if hasattr(child, "to_plotly_json")
            )

        votes = {"A": 0, "B": 0, "C": 0, "D": 0}
        self.assertEqual(len(BACKUP_LINKS), 10)
        for origin_title, link in BACKUP_LINKS.items():
            origin = SLIDE_TITLES.index(origin_title)
            target = SLIDE_TITLES.index(link["target"])
            self.assertLess(origin, APPENDIX_START_SLIDE)
            self.assertGreaterEqual(target, APPENDIX_START_SLIDE)
            core_slide = render_slide(origin, 1, votes)
            self.assertIn("has-backup-link", core_slide.className)
            self.assertTrue(has_pattern_id(core_slide, "backup-button"))

        backup_slide = render_slide(APPENDIX_START_SLIDE, 1, votes)
        self.assertIn("backup-slide", backup_slide.className)
        self.assertTrue(has_pattern_id(backup_slide, "return-from-backup"))

    def test_climate_introduction_contract(self) -> None:
        self.assertEqual(len(SLIDE_TITLES), 51)
        self.assertEqual(CORE_SLIDE_COUNT, 33)
        self.assertEqual(APPENDIX_SLIDE_COUNT, 18)
        self.assertEqual(CORE_LAST_SLIDE, 32)
        self.assertEqual(APPENDIX_START_SLIDE, 33)
        self.assertEqual(SLIDE_TITLES, CORE_SLIDE_TITLES + APPENDIX_SLIDE_TITLES)
        self.assertFalse(set(CORE_SLIDE_TITLES) & set(APPENDIX_SLIDE_TITLES))
        self.assertEqual(CORE_SLIDE_TITLES[0], "IAM scenarios for prospective LCA")
        self.assertEqual(
            CORE_SLIDE_TITLES[-1],
            "Resources for building and documenting scenarios",
        )
        self.assertEqual(CHAPTERS[-1]["name"], "Backup")
        self.assertEqual(CHAPTERS[-1]["start"], APPENDIX_START_SLIDE)
        self.assertEqual(sum(chapter["minutes"] for chapter in CHAPTERS), 75)

        required_core = {
            "A target date is not a pathway",
            "An IAM is a structured thought experiment",
            "IAMs represent different parts of the system",
            "SSPs differ before climate policy is added",
            "RCPs define radiative-forcing experiments",
            "CMIP7 families describe how emissions change over time",
            "A quantitative scenario combines three layers",
            "Choose a pathway before seeing its assumptions",
            "Investment changes the system over time",
            "First, compare the whole energy system",
            "Premise gets different levels of detail from each IAM",
            "What IAMs leave out",
            "Explore how scenarios change each sector",
            "Premise updates selected parts of the background database",
            "Trace an LCA result back to the scenario data",
            "The IAM says solar; the LCA needs a specific module technology",
            "Premise translates scenarios; it is not a scenario model",
            "Premise changes inventories; Brightway calculates results",
        }
        self.assertTrue(required_core <= set(CORE_SLIDE_TITLES))

        expected_backup = {
            "From emissions scenarios to policy evidence",
            "Fast innovation does not guarantee sustainability",
            "Then examine the electricity chain",
            "Primary energy: resources entering the system",
            "Passenger cars: electrification reduces energy per kilometre",
            "Cement: lower emissions require a different kiln mix",
            "Low warming in 2100 can depend on large future removals",
            "PV uncertainty affects indicators differently",
        }
        self.assertTrue(expected_backup <= set(APPENDIX_SLIDE_TITLES))
        self.assertEqual(
            CORE_SLIDE_TITLES[15], "Investment changes the system over time"
        )
        self.assertEqual(
            CORE_SLIDE_TITLES[16], "First, compare the whole energy system"
        )
        self.assertEqual(
            BACKUP_LINKS["First, compare the whole energy system"]["target"],
            "Then examine the electricity chain",
        )
        self.assertNotIn("Investment changes the system over time", BACKUP_LINKS)
        self.assertEqual(
            CORE_SLIDE_TITLES[27],
            "The IAM says solar; the LCA needs a specific module technology",
        )
        self.assertEqual(
            CORE_SLIDE_TITLES[28],
            "Similar warming can still have very different impacts",
        )
        self.assertEqual(
            BACKUP_LINKS[
                "The IAM says solar; the LCA needs a specific module technology"
            ]["target"],
            "PV uncertainty affects indicators differently",
        )
        self.assertNotIn(
            "Similar warming can still have very different impacts", BACKUP_LINKS
        )
        self.assertNotIn(
            "From one-off research links to shared scenario tools", SLIDE_TITLES
        )
        self.assertEqual(
            CORE_SLIDE_TITLES[-2],
            "Premise changes inventories; Brightway calculates results",
        )
        self.assertEqual(
            BACKUP_LINKS["Premise changes inventories; Brightway calculates results"][
                "target"
            ],
            "One set of databases supports three scales of analysis",
        )
        self.assertNotIn("Mapped IAM detail varies by model and sector", SLIDE_TITLES)
        self.assertEqual(
            SLIDE_TITLES[RESULT_TRACER_SLIDE],
            "Trace an LCA result back to the scenario data",
        )
        self.assertEqual(
            SLIDE_TITLES[ANONYMOUS_SLIDE],
            "Choose a pathway before seeing its assumptions",
        )
        self.assertLess(ANONYMOUS_SLIDE, APPENDIX_START_SLIDE)
        self.assertLess(RESULT_TRACER_SLIDE, APPENDIX_START_SLIDE)
        population = ssp_baseline_comparison_figure("population")
        self.assertEqual(len(population.data), 5)
        self.assertAlmostEqual(float(population.data[2].y[-1]), 12.6)
        rcp_gmst = rcp_gmst_trajectory_figure(compact=True)
        self.assertEqual(len(rcp_gmst.data), 5)
        self.assertAlmostEqual(float(rcp_gmst.data[0].y[-1]), 4.3)
        self.assertEqual(rcp_gmst.data[-1].name, "SSP1-1.9")
        self.assertAlmostEqual(float(rcp_gmst.data[-1].y[-1]), 1.4)
        cmip7_gmst = cmip7_gmst_trajectory_figure(compact=True)
        self.assertEqual(len(cmip7_gmst.data), 7)
        self.assertAlmostEqual(float(cmip7_gmst.data[0].y[-1]), 3.8)
        energy_figure = energy_emissions_change_figure()
        self.assertEqual(len(energy_figure.data), 2)
        self.assertAlmostEqual(float(energy_figure.data[0].y[-1]), 160.1, places=1)
        self.assertAlmostEqual(float(energy_figure.data[1].y[-1]), 151.3, places=1)
        self.assertAlmostEqual(sum(ghg_sector_figure().data[0].x), 59.0)
        self.assertAlmostEqual(sum(ghg_gas_figure().data[0].values), 59.7)
        self.assertEqual(sum(ghg_region_figure().data[0].x), 99)
        mitigation = sector_mitigation_potential_figure()
        self.assertEqual(list(mitigation.data[1].y), [5.4, 3.8, 2.0])
        self.assertEqual(list(mitigation.data[2].y), [4.4, 4.6, 6.8])
        for index, total in enumerate(mitigation.data[0].y):
            self.assertAlmostEqual(
                float(mitigation.data[1].base[index] + mitigation.data[1].y[index]),
                total,
            )
            self.assertAlmostEqual(
                float(mitigation.data[2].base[index] + mitigation.data[2].y[index]),
                total,
            )
        budget = carbon_budget_figure()
        self.assertEqual(list(budget.data[0].x), [2400, 2400])
        self.assertEqual(list(budget.data[1].x), [500, 1150])
        timing = same_net_zero_date_figure()
        self.assertEqual(len(timing.data), 2)
        self.assertEqual(float(timing.data[0].y[-1]), 0.0)
        self.assertEqual(float(timing.data[1].y[-1]), 0.0)
        self.assertAlmostEqual(sum(timing.data[0].y) - 20, 600.0)
        self.assertAlmostEqual(sum(timing.data[1].y) - 20, 800.0)
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "assets/net-zero-commitments-map.png").is_file())

    def test_capstone_cases_render_from_calculated_evidence(self) -> None:
        for case_key in CAPSTONE_CASE_SPECS:
            signal = capstone_signal_figure(case_key, 2060, "SSP2-M")
            self.assertGreater(len(signal.data), 1, case_key)
            for trace in signal.data:
                self.assertEqual(list(trace.x), CORE_SCENARIOS)
                self.assertEqual(list(trace.marker.opacity), [0.3, 0.3, 1, 0.3])
            for indicator_key in CAPSTONE_INDICATOR_SPECS:
                trajectory = capstone_lcia_trajectory_figure(
                    case_key, indicator_key, "SSP2-M", 2040
                )
                contribution = capstone_contribution_figure(
                    case_key, 2040, indicator_key, "SSP2-M"
                )
                self.assertEqual(len(trajectory.data), 4, (case_key, indicator_key))
                self.assertEqual(len(contribution.data), 1, (case_key, indicator_key))
                self.assertGreater(len(contribution.data[0].x), 1)
                selected = next(
                    trace for trace in trajectory.data if trace.name == "SSP2-M"
                )
                self.assertEqual(selected.opacity, 1)
                self.assertEqual(selected.line.width, 4)
                selected_index = list(selected.x).index(2040)
                self.assertEqual(selected.marker.size[selected_index], 13)
                for trace in trajectory.data:
                    if trace.name != "SSP2-M":
                        self.assertEqual(trace.opacity, 0.24)
                self.assertIn("SSP2-M · 2040", contribution.layout.title.text)
        steel_chain = steel_causal_chain_figure()
        route_traces = [
            trace
            for trace in steel_chain.data
            if str(trace.legendgroup).startswith("route-")
        ]
        self.assertEqual(len(route_traces), 4)
        for year_index in range(3):
            self.assertAlmostEqual(
                sum(float(trace.y[year_index]) for trace in route_traces), 1.0
            )
        self.assertIn("IMAGE WEU route mix", steel_chain.layout.annotations[0].text)
        self.assertEqual(len(steel_chain.data), 9)

    def test_capstone_source_figures_are_packaged(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for name in [
            "pv-module-efficiency-premise.png",
            "pv-system-uncertainty.png",
            "pv-subtechnology-market-shares.png",
            "system-lca-tradeoffs.png",
        ]:
            self.assertTrue((root / "assets" / name).is_file(), name)

    def test_controlled_comparison_contains_two_experiments(self) -> None:
        figure = controlled_comparison_figure()
        self.assertEqual(
            [trace.name for trace in figure.data],
            [
                "SSP2-VL",
                "SSP2-L",
                "SSP2-ML",
                "SSP2-M",
                "IMAGE",
                "MESSAGE",
                "REMIND",
            ],
        )
        self.assertEqual(sum(bool(trace.showlegend) for trace in figure.data), 7)
        self.assertEqual(sum(trace.xaxis == "x" for trace in figure.data), 4)
        self.assertEqual(sum(trace.xaxis == "x2" for trace in figure.data), 3)
        remind = next(trace for trace in figure.data if trace.name == "REMIND")
        self.assertGreater(float(remind.y[0]), 30)
        self.assertLess(float(remind.y[0]), 40)

    def test_applied_geography_is_auditable(self) -> None:
        mapping = image_region_mapping()
        self.assertEqual(mapping["inventory_location"], "CH")
        self.assertEqual(mapping["iam_region"], "WEU")
        self.assertIn("CH", mapping["regions"]["WEU"])
        self.assertNotIn("CH", mapping["regions"]["CEU"])
        self.assertEqual(mapping["teaching_aggregation"], ["WEU", "CEU"])
        figure = image_geography_figure()
        self.assertEqual(len(figure.data), 2)
        self.assertEqual(
            list(figure.data[0].colorbar.ticktext), ["WEU", "CEU", "TUR", "UKR", "RUS"]
        )
        self.assertEqual(figure.data[1].name, "CH → WEU")

        remind_mapping = remind_eu_region_mapping()
        self.assertEqual(remind_mapping["inventory_location"], "CH")
        self.assertEqual(remind_mapping["iam_region"], "NEN")
        self.assertIn("CH", remind_mapping["regions"]["NEN"])
        remind_figure = remind_eu_geography_figure()
        self.assertEqual(len(remind_figure.data), 2)
        self.assertEqual(len(remind_figure.data[0].colorbar.ticktext), 11)
        self.assertEqual(remind_figure.data[1].name, "CH → NEN")

    def test_interactive_iam_geographies_cover_six_models(self) -> None:
        topologies = iam_region_topologies()
        self.assertEqual(
            set(topologies),
            {"image", "message", "remind", "remind-eu", "tiam-ucl", "gcam"},
        )
        self.assertEqual(topologies["image"]["region_count"], 26)
        self.assertEqual(topologies["message"]["region_count"], 12)
        self.assertEqual(topologies["remind-eu"]["region_count"], 21)

    def test_expanded_extract_contract(self) -> None:
        frame = pathways()
        self.assertEqual(
            set(frame["model"]),
            {"image", "message", "remind", "remind-eu", "tiam-ucl", "gcam"},
        )
        self.assertTrue(
            {
                "Final Energy",
                "Transport Passenger Cars",
                "Transport Road Freight",
                "Cement",
                "Hydrogen",
                "Biomass",
            }
            <= set(frame["sector"])
        )
        self.assertGreater(len(frame), 100_000)

    def test_sector_views_have_four_core_scenarios(self) -> None:
        for sector in ["Electricity", "Transport Passenger Cars", "Cement", "Steel"]:
            data = sector_mix(sector, ANONYMOUS_ORDER, 2060)
            self.assertEqual(set(data["scenario"]), set(ANONYMOUS_ORDER), sector)
            figure = sector_snapshot(sector, 2060, "share")
            self.assertGreater(len(figure.data), 0)
            self.assertEqual(list(figure.data[0].x), CORE_SCENARIOS)

    def test_sector_explorer_technology_colours_are_stable_across_years(self) -> None:
        for sector in ["Electricity", "Transport Passenger Cars", "Cement", "Steel"]:
            colour_maps = []
            for year in [2020, 2040, 2060]:
                figure = sector_snapshot(sector, year, "share")
                colour_maps.append(
                    {trace.name: trace.marker.color for trace in figure.data}
                )
            technologies = set().union(*(mapping.keys() for mapping in colour_maps))
            for technology in technologies:
                observed = {
                    mapping[technology]
                    for mapping in colour_maps
                    if technology in mapping
                }
                self.assertEqual(len(observed), 1, (sector, technology, observed))

    def test_sector_commodity_gwp_uses_built_database_years(self) -> None:
        cases = {
            "Electricity": "electricity",
            "Transport Passenger Cars": "passenger_cars",
            "Cement": "cement",
            "Steel": "steel",
        }
        results = lcia_results()
        climate = results.loc[
            results["method_family"].eq("IPCC 2021")
            & results["case"].isin(cases.values())
        ]
        for sector, case in cases.items():
            case_results = climate.loc[climate["case"].eq(case)]
            self.assertEqual(len(case_results), 12, sector)
            self.assertEqual(set(case_results["scenario"]), set(CORE_SCENARIOS))
            self.assertEqual(set(case_results["year"]), {2020, 2040, 2060})
            figure = commodity_gwp_figure(sector)
            self.assertEqual([trace.name for trace in figure.data], CORE_SCENARIOS)
            for trace in figure.data:
                self.assertEqual(list(trace.x), [2020, 2040, 2060])
                self.assertTrue(all(float(value) == float(value) for value in trace.y))

    def test_absolute_gwp_scales_only_unit_compatible_activity(self) -> None:
        cases = {
            "Electricity": ("electricity", 1 / 3.6),
            "Cement": ("cement", 1 / 1_000),
            "Steel": ("steel", 1 / 1_000),
        }
        results = lcia_results()
        for sector, (case, factor) in cases.items():
            figure = commodity_gwp_figure(sector, "absolute")
            self.assertEqual([trace.name for trace in figure.data], CORE_SCENARIOS)
            trace = next(trace for trace in figure.data if trace.name == "SSP2-VLHO")
            self.assertEqual(list(trace.x), [2020, 2040, 2060])
            score = results.loc[
                results["case"].eq(case)
                & results["scenario"].eq("SSP2-VLHO")
                & results["year"].eq(2060)
                & results["method_family"].eq("IPCC 2021"),
                "score",
            ].iloc[0]
            activity = (
                context_series(sector, CORE_SCENARIOS)
                .loc[
                    lambda frame: frame["scenario"].eq("SSP2-VLHO")
                    & frame["year"].eq(2060),
                    "display_value",
                ]
                .iloc[0]
            )
            self.assertAlmostEqual(float(trace.y[-1]), float(score * activity * factor))

        passenger = commodity_gwp_figure("Transport Passenger Cars", "absolute")
        self.assertEqual(len(passenger.data), 0)
        annotation_text = " ".join(
            str(annotation.text) for annotation in passenger.layout.annotations
        )
        self.assertIn("vehicle-km", annotation_text)

    def test_cdr_summary_preserves_missing_series(self) -> None:
        figure = cdr_overshoot_summary_figure()
        annual_names = [trace.name for trace in figure.data if trace.xaxis == "x"]
        self.assertEqual(annual_names, ["SSP1-L", "SSP2-VLHO", "SSP2-M"])
        self.assertNotIn("SSP3-H", annual_names)

    def test_lcia_evidence_reconciles_contributions(self) -> None:
        figure = lcia_evidence_figure()
        self.assertEqual(list(figure.data[0].x), CORE_SCENARIOS)
        self.assertEqual(list(figure.data[1].x), CORE_SCENARIOS)
        contribution_total = sum(float(value) for value in figure.data[2].x)
        results = lcia_contributions()
        self.assertFalse(results.empty)
        self.assertAlmostEqual(contribution_total, -0.0548101076362435, places=10)

    def test_model_coverage_renders(self) -> None:
        figure = model_coverage_figure()
        self.assertEqual(len(figure.data), 1)
        self.assertEqual(len(figure.layout.annotations), 48)
        self.assertEqual(int(figure.data[0].z[0][1]), 314)
        self.assertEqual(int(figure.data[0].z[1][5]), 0)

    def test_premise_mapping_counts_are_auditable(self) -> None:
        frame = premise_mapping_counts()
        self.assertEqual(len(frame), 60)
        self.assertEqual(set(frame["premise_version"]), {"2.4.6"})
        self.assertEqual(
            set(frame["model"]),
            {"image", "message", "remind", "remind-eu", "tiam-ucl", "gcam"},
        )
        image_final = frame.loc[
            frame["model"].eq("image") & frame["sector"].eq("Final energy"),
            "mapped_variable_count",
        ].iloc[0]
        message_cars = frame.loc[
            frame["model"].eq("message") & frame["sector"].eq("Passenger cars"),
            "mapped_variable_count",
        ].iloc[0]
        self.assertEqual(int(image_final), 314)
        self.assertEqual(int(message_cars), 0)
        self.assertTrue(frame["source_file"].str.endswith(".yaml").all())
        self.assertTrue(frame["counting_rule"].str.len().gt(0).all())
        figure = premise_mapping_counts_figure()
        self.assertEqual(len(figure.data), 6)
        self.assertEqual(figure.layout.barmode, "group")
        self.assertEqual(len(figure.data[0].x), 8)

    def test_mechanics_example_uses_reported_remind_data(self) -> None:
        frame = mechanics_series()
        self.assertEqual(len(frame), 27)
        self.assertEqual(set(frame["scenario"]), {"SSP2-PkBudg650"})
        investment = frame[frame["metric"] == "annual_investment"]
        peak = investment.loc[investment["value"].idxmax()]
        self.assertEqual(int(peak["year"]), 2035)
        self.assertAlmostEqual(float(peak["value"]), 115.745022)
        output_2060 = frame.loc[
            (frame["metric"] == "hydrogen_output") & (frame["year"] == 2060),
            "value",
        ].iloc[0]
        self.assertAlmostEqual(float(output_2060), 32.087371)
        efficiency = frame[frame["metric"] == "conversion_efficiency"]
        self.assertEqual(float(efficiency.iloc[-1]["value"]), 75.0)
        figure = iam_mechanics_figure()
        self.assertEqual(len(figure.data), 3)

    def test_image_energy_layers_are_auditable(self) -> None:
        frame = image_energy_layers()
        self.assertEqual(len(frame), 1368)
        self.assertEqual(
            set(frame["scenario"]), {"SSP1-L", "SSP2-M", "SSP3-H", "SSP2-VLHO"}
        )
        self.assertEqual(
            set(frame["layer"]),
            {"Primary energy", "Secondary electricity", "Final energy"},
        )
        self.assertEqual(set(frame["region"]), {"World", "Europe (WEU + CEU)"})
        fossil = frame[
            frame["scenario"].eq("SSP1-L")
            & frame["region"].eq("World")
            & frame["layer"].eq("Primary energy")
            & frame["group"].isin(["Coal", "Oil", "Gas"])
            & frame["year"].eq(2060)
        ]["value"].sum()
        self.assertAlmostEqual(float(fossil), 214.1, places=1)
        self.assertTrue(frame["source_regions"].str.len().gt(0).all())
        self.assertTrue(frame["source_variables"].str.len().gt(0).all())
        primary = primary_energy_layer_figure()
        secondary = secondary_energy_layer_figure()
        final = final_energy_layer_figure()
        self.assertEqual(len(primary.data), 48)
        self.assertEqual(len(secondary.data), 72)
        self.assertEqual(len(final.data), 32)
        self.assertEqual(
            [annotation.text for annotation in primary.layout.annotations[:4]],
            CORE_SCENARIOS,
        )
        self.assertEqual([trace.name for trace in final.data[:4]], CORE_SCENARIOS)

    def test_image_electricity_chain_is_auditable_and_balanced(self) -> None:
        frame = image_electricity_chain()
        self.assertEqual(len(frame), 72)
        self.assertEqual(set(frame["scenario"]), {"SSP2-VLHO"})
        self.assertEqual(set(frame["region"]), {"Europe (WEU + CEU)"})
        self.assertEqual(set(frame["unit"]), {"EJ/yr", "billion pkm/yr"})
        year = frame[frame["year"].eq(2060)]
        primary = year[year["stage"].eq("Primary input to electricity")]["value"].sum()
        secondary = year.loc[year["stage"].eq("Secondary electricity"), "value"].iloc[0]
        service = year.loc[year["stage"].eq("Energy service"), "value"].iloc[0]
        self.assertAlmostEqual(float(primary), 30.592317, places=6)
        self.assertAlmostEqual(float(secondary), 23.014061, places=6)
        self.assertAlmostEqual(float(service), 14072.941, places=3)
        self.assertTrue(frame["source_regions"].str.len().gt(0).all())
        self.assertTrue(frame["source_variables"].str.len().gt(0).all())

        figure = energy_accounting_example_figure()
        self.assertEqual(len(figure.data), 1)
        sankey = figure.data[0]
        self.assertEqual(sankey.type, "sankey")
        link_values = list(sankey.link.value)
        self.assertAlmostEqual(sum(link_values[:4]), sum(link_values[4:6]), places=6)
        self.assertAlmostEqual(link_values[4], sum(link_values[6:9]), places=6)
        baseline = energy_accounting_example_figure(2020, 30.592317)
        baseline_links = list(baseline.data[0].link.value)
        self.assertEqual(len(baseline_links), 10)
        self.assertAlmostEqual(
            sum(baseline_links[:4]) + baseline_links[-1], 30.592317, places=6
        )

    def test_image_total_energy_chain_is_auditable(self) -> None:
        frame = image_total_energy_chain()
        self.assertEqual(len(frame), 243)
        self.assertEqual(set(frame["scenario"]), {"SSP2-VLHO"})
        self.assertEqual(set(frame["region"]), {"World"})
        self.assertEqual(set(frame["unit"]), {"EJ/yr"})
        self.assertEqual(
            set(frame["stage"]),
            {
                "Primary energy supply",
                "Secondary carrier indicator",
                "Final energy flow",
            },
        )
        self.assertEqual(
            set(frame.loc[frame["stage"].eq("Final energy flow"), "destination"]),
            {"Industry", "Transport", "Buildings", "Other + carbon management"},
        )
        year_2020 = frame[frame["year"].eq(2020)]
        year_2060 = frame[frame["year"].eq(2060)]
        primary_2020 = year_2020.loc[
            year_2020["stage"].eq("Primary energy supply"), "value"
        ].sum()
        primary_2060 = year_2060.loc[
            year_2060["stage"].eq("Primary energy supply"), "value"
        ].sum()
        final_2020 = year_2020.loc[
            year_2020["stage"].eq("Final energy flow"), "value"
        ].sum()
        final_2060 = year_2060.loc[
            year_2060["stage"].eq("Final energy flow"), "value"
        ].sum()
        self.assertAlmostEqual(float(primary_2020), 555.509113, places=6)
        self.assertAlmostEqual(float(primary_2060), 670.930754, places=6)
        self.assertAlmostEqual(float(final_2020), 338.527373, places=6)
        self.assertAlmostEqual(float(final_2060), 396.335565, places=6)
        self.assertTrue(frame["source_regions"].str.len().gt(0).all())
        self.assertTrue(frame["source_variables"].str.len().gt(0).all())
        self.assertTrue(frame["allocation_method"].str.len().gt(0).all())

        figure = total_energy_system_figure(2020, primary_2020)
        self.assertEqual(len(figure.data), 1)
        self.assertEqual(figure.data[0].type, "sankey")
        links = list(figure.data[0].link.value)
        self.assertAlmostEqual(sum(links[:4]), sum(links[4:11]), places=6)
        self.assertAlmostEqual(sum(links[4:10]), sum(links[11:]), places=6)

    def test_image_end_use_transformations_are_auditable(self) -> None:
        frame = image_end_use_transformations()
        self.assertEqual(len(frame), 282)
        self.assertEqual(set(frame["scenario"]), {"SSP2-VLHO"})
        self.assertEqual(set(frame["region"]), {"World"})
        self.assertEqual(
            set(frame["domain"]),
            {"Passenger cars", "Cement", "Steel", "Space heating"},
        )
        self.assertEqual(
            set(frame["metric"]),
            {"technology mix", "specific energy", "context total"},
        )
        self.assertTrue(frame["source_variables"].str.len().gt(0).all())
        self.assertTrue(frame["derivation"].str.len().gt(0).all())
        passenger_intensity = frame.loc[
            frame["domain"].eq("Passenger cars")
            & frame["metric"].eq("specific energy")
            & frame["year"].eq(2060),
            "value",
        ].iloc[0]
        self.assertAlmostEqual(float(passenger_intensity), 0.403617, places=6)
        for domain in ["Passenger cars", "Cement", "Steel", "Space heating"]:
            figure = end_use_transformation_figure(domain)
            self.assertGreaterEqual(len(figure.data), 6)
            self.assertEqual(figure.data[-3].name, "Specific energy use")

    def test_removed_presentation_labels_do_not_return(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = "\n".join(
            (root / path).read_text(encoding="utf-8")
            for path in [
                "app.py",
                "workshop/config.py",
                "workshop/slides.py",
                "README.md",
            ]
        ).lower()
        for phrase in [
            "60-minute core",
            "+ 30-minute extension",
            "instructor notes",
            "provisional choice",
            "iam theory · system boundary",
            "what happens inside an iam?",
            "decision exercise · passenger mobility",
            "choose the contrast that tests your decision",
        ]:
            self.assertNotIn(phrase, text)

    def test_slide_copy_has_no_em_dashes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in [
            "workshop/config.py",
            "workshop/slides.py",
            "workshop/figures.py",
            "data/narratives.json",
            "data/premise_transformations.json",
            "assets/premise-transformation-engine.svg",
            "assets/premise-library-bridge.svg",
            "assets/premise-ecosystem-network.svg",
        ]:
            self.assertNotIn("—", (root / path).read_text(encoding="utf-8"), path)

    def test_lcia_schema_is_auditable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        header = (
            (root / "data/processed/lcia_results.csv")
            .read_text(encoding="utf-8")
            .splitlines()[0]
            .split(",")
        )
        required = {
            "scenario",
            "year",
            "database_name",
            "activity_key",
            "functional_unit",
            "indicator",
            "unit",
            "provenance_id",
            "score",
        }
        self.assertTrue(required <= set(header))


if __name__ == "__main__":
    unittest.main()
