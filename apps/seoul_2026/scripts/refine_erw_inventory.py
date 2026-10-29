"""Reproduce a separate, literature-reviewed temporal coastal ERW foreground.

Run with the premise environment (openpyxl, numpy and bw2io). No Brightway
database or source workbook is modified. The generated workbook is an input,
not evidence that linking or a full-background LCA has been performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import openpyxl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from apps.seoul_2026.erw import NICKEL_KG, temporal_profile

DEFAULT_SOURCE = Path(
    "/Users/romain/GitHub/premise/premise/data/additional_inventories/lci-coastal-enhanced-weathering.xlsx"
)
OUTPUT = Path(__file__).resolve().parents[1] / "data"
HEADERS = [
    "name",
    "amount",
    "database",
    "location",
    "unit",
    "categories",
    "type",
    "reference product",
    "comment",
    "temporal_distribution",
    "temporal_loc",
    "temporal_amount_source",
    "temporal_offsets",
    "temporal_weights",
]
SCENARIOS = [
    ("static reference", 0, 0, 1),
    ("dated reference", 10, 1, 1),
    ("slower limited uptake sensitivity", 30, 5, 0.8),
]
SOURCES = [
    {
        "title": "Foteinis, Campbell & Renforth (2023), coastal enhanced weathering LCA",
        "url": "https://doi.org/10.1021/acs.est.2c08633",
    },
    {
        "title": "Supporting inventory, Table S1 (2023)",
        "url": "https://doi.org/10.1021/acs.est.2c08633.s001",
    },
    {
        "title": "Geerts, Hylén & Meysman (2025), marine enhanced rock weathering synthesis",
        "url": "https://doi.org/10.5194/bg-22-355-2025",
    },
    {
        "title": "Zhou et al. (2024 online; 2025 issue), air–sea equilibration",
        "url": "https://doi.org/10.1038/s41558-024-02179-9",
    },
    {
        "title": "TRAILS, supported temporal exchange fields",
        "url": "https://trails.readthedocs.io/en/latest/",
    },
]


def build(source=DEFAULT_SOURCE, output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    original_bytes = source.read_bytes()
    source_hash = hashlib.sha256(original_bytes).hexdigest()
    sheet = openpyxl.load_workbook(source, data_only=True).active
    raw = list(sheet.iter_rows(values_only=True))
    header_index = next(
        i for i, row in enumerate(raw) if row[0] == "name" and row[1] == "amount"
    )
    headers = list(raw[header_index])
    exchanges = [dict(zip(headers, row)) for row in raw[header_index + 1 :] if row[0]]
    ni = [e for e in exchanges if e["name"] == "Nickel II"]
    assert len(ni) == 2 and {e["categories"] for e in ni} == {
        "water::ocean",
        "water::ground-, long-term",
    }
    grinding = next(
        e for e in exchanges if e["name"] == "market group for electricity, low voltage"
    )
    assert abs(grinding["amount"] - 0.09307) < 1e-12
    assert abs(sum(e["amount"] for e in ni) - 0.00329) < 1e-12
    workbook = openpyxl.Workbook()
    ws = workbook.active
    ws.title = "coastal_erw"
    database = "snu_coastal_erw_2026"
    ws.append(["Database", database])
    timing_checks = []
    for label, duration, lag, efficiency in SCENARIOS:
        name = f"coastal olivine weathering deployment, {label}"
        product = "coastal weathering deployment, 1.25 kg rock"
        ws.append([])
        ws.append(["Activity", name])
        ws.append(
            [
                "comment",
                "Fixed deployment of 1.25 kg olivine-rich rock. Source potential 0.8 kg eventual CO2/kg rock; not a guaranteed net-removal service. Based on Foteinis et al. 2023, DOI 10.1021/acs.est.2c08633 and SI Table S1. Medium-voltage grinding correction. Ocean Ni upper-bound release follows dissolution; mobile fraction and site performance unvalidated. Temporal assumptions are analyst scenarios, not field fits.",
            ]
        )
        for key, value in (
            ("location", "RER"),
            ("reference product", product),
            ("type", "process"),
            ("unit", "unit"),
        ):
            ws.append([key, value])
        ws.append(["Exchanges"])
        ws.append(HEADERS)
        profile = temporal_profile(duration or 10, lag, efficiency, years=500)
        for e in exchanges:
            e = dict(e)
            if e["name"] == "Nickel II":
                continue
            e["temporal_amount_source"] = "port"
            e["temporal_distribution"] = 1
            e["temporal_loc"] = 0
            if e["type"] == "production":
                e.update(
                    name=name,
                    database=database,
                    unit="unit",
                    **{"reference product": product},
                )
                for key in (
                    "temporal_amount_source",
                    "temporal_distribution",
                    "temporal_loc",
                ):
                    e.pop(key)
            elif e["name"] == "market group for electricity, low voltage":
                e.update(
                    name="market group for electricity, medium voltage",
                    **{"reference product": "electricity, medium voltage"},
                )
                e["comment"] = (
                    "Corrected voltage to source SI Table S1: Europe medium voltage; (92.3+0.22+0.33+0.22) kWh/tCO2 = 0.09307 kWh per deployment unit. No change to physical energy demand."
                )
            elif e["name"] == "Carbon dioxide, in air":
                e["amount"] = float(efficiency)
                e["comment"] = (
                    "Eventual uptake: 1.25 kg rock * 0.8 kg CO2/kg rock * realization fraction. Resource-flow positive amount; the LCIA method determines its sign. Do not credit dissolution and uptake twice."
                )
                if duration:
                    weights = profile["uptake_kg"] / (1000 * efficiency)
                    e.update(
                        temporal_distribution=6,
                        temporal_loc=None,
                        temporal_offsets=json.dumps(
                            profile["age"].astype(int).tolist()
                        ),
                        temporal_weights=json.dumps(weights.tolist()),
                    )
                    e["comment"] += (
                        f" Shrinking-core completion {duration} years; discrete exponential air–sea lag scale {lag} years. Annual end-of-bin pulses over 500 years. Scenario, not site calibration. Residual tail below numerical tolerance."
                    )
            elif e["type"] != "production":
                e["comment"] = (
                    (e.get("comment") or "")
                    + " Retained source/proxy quantity. Assigned to deployment year for the foreground timing scenario; supplier life-cycle timing remains a separate background-model concern."
                )
            ws.append([e.get(h) for h in HEADERS])
        nickel = dict(
            name="Nickel II",
            amount=NICKEL_KG / 1000,
            database="biosphere3",
            unit="kilogram",
            categories="water::ocean",
            type="biosphere",
            comment="Conservative congruent-dissolution mobile-Ni upper bound: 1.25 kg rock * 0.263 wt.% = 0.0032875 kg Ni. Receiving environment remains ocean at every date. This is not evidence that all mineral Ni becomes dissolved/bioavailable; sediment retention is unresolved.",
            temporal_amount_source="port",
            temporal_distribution=1,
            temporal_loc=0,
        )
        if duration:
            nickel.update(
                temporal_distribution=6,
                temporal_loc=None,
                temporal_offsets=json.dumps(profile["age"].astype(int).tolist()),
                temporal_weights=json.dumps(profile["dissolved"].tolist()),
            )
        ws.append([nickel.get(h) for h in HEADERS])
        timing_checks.append(
            dict(
                scenario=label,
                dissolution_years=duration,
                lag_scale_years=lag,
                realization=efficiency,
                total_uptake_kg_per_unit=efficiency,
                uptake_tail_kg_per_unit=profile["tail_kg"] / 1000,
            )
        )
    ws.freeze_panes = "B12"
    ws.column_dimensions["A"].width = 65
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["I"].width = 100
    output_path = output / "coastal_erw_temporalized.xlsx"
    workbook.save(output_path)
    assert source.read_bytes() == original_bytes
    review = dict(
        scope="A separate literature-reviewed temporal foreground derived from premise's coastal olivine inventory. Original workbook unchanged. This review does not certify coastal field performance.",
        reviewed_on="2026-10-25",
        source_file=source.name,
        source_sha256=source_hash,
        workbook_sha256=hashlib.sha256(output_path.read_bytes()).hexdigest(),
        functional_unit="One deployment unit = 1.25 kg olivine-rich rock. Source-based eventual gross uptake potential is 1 kg CO2 before an additional realization sensitivity. It is not a guaranteed kilogram of net removal. Slides scale deployment by 1000.",
        findings=[
            dict(
                title="Reference-product description",
                evidence="The old description calls this a kilogram of rock although the reference exchange is a kilogram of captured CO2 and uses 1.25 kg rock.",
                action="Use a deployment service in units, explicitly linked to fixed rock mass and eventual potential.",
                status="Corrected without rescaling physical inputs.",
            ),
            dict(
                title="Comminution electricity voltage",
                evidence="Table S1 specifies European medium-voltage electricity. The workbook names a low-voltage market. The 10 µm total is 92.3+0.22+0.33+0.22 = 93.07 kWh/tCO2.",
                action="Change the grinding supplier and reference product to medium voltage; retain 0.09307 kWh per deployment unit.",
                status="Source-supported mapping correction; linking to a selected database remains to be checked.",
            ),
            dict(
                title="Nickel compartment and amount",
                evidence="The workbook splits Ni between ocean and long-term groundwater using a first-year dissolution fraction. A delayed release to seawater does not establish a groundwater emission. Exact source mass arithmetic gives 1.25 × 0.00263 = 0.0032875 kg Ni/unit, versus rounded 0.00329.",
                action="Keep one ocean Ni exchange; attach its dated release as a conservative congruent-dissolution upper bound. Do not infer a measured mobile fraction.",
                status="Compartment corrected; temporal mobility remains an explicit upper-bound scenario.",
            ),
            dict(
                title="Atmospheric uptake timing",
                evidence="The source paper models delayed dissolution. The later marine-weathering review distinguishes mineral reaction, alkalinity transfer and atmospheric equilibration.",
                action="Distribute resource CO2 uptake using a shrinking-core dissolution curve convolved with an air–sea delay kernel. Never add a second negative credit for alkalinity production.",
                status="Mechanistically motivated temporal scenario; 10/30-year durations and 1/5-year lag choices are not site-calibrated estimates.",
            ),
            dict(
                title="Water and transport arithmetic",
                evidence="The workbook totals 0.00049612 m3 water per unit, consistent with the SI's cooling, dust suppression and drilling water combined. Coastal haulage is 1.25 kg × 50 km /1000 = 0.0625 tkm per unit.",
                action="Retain these quantities and their existing aggregation; do not add the source rows a second time.",
                status="Arithmetic checked against source SI.",
            ),
        ],
        temporal_scenario="Deployment-year foreground inputs are retained. Three variants: static reference, 10-year shrinking-core dissolution with a 1-year exponential air–sea lag and full reference realization, and a slower 30-year/5-year/80% realization sensitivity. These are fixed-deployment scenarios; they are not paired particle-size/energy variants. Ni is a separate conservative upper bound and is not reduced with atmospheric realization.",
        limitations=[
            "No new full-background LCIA or TRAILS solve is represented by the lecture's ERW screening chart. It holds the published 51 kg CO2-eq/tCO2 footprint fixed to isolate timing.",
            "The 2023 paper's 0.8 kg CO2/kg rock potential already accounts conservatively for composition/buffering; the additional realization sensitivity must not be interpreted as a second universal carbonate correction.",
            "The hydraulic manure-spreader substitution is retained as a spreading proxy. Its loading overlap and suitability are unresolved; do not present it as a verified lime-spreading inventory.",
            "The extra 0.0125 tkm quarry-to-crusher proxy is retained. The source SI lists an ELCD mining-truck proxy in kg rather than a verified equivalent transport distance.",
            "Source SI land-restoration rows are absent from the inherited workbook. No restoration or associated carbon credit has been invented without a quarry life and site plan.",
            "Site hydrodynamics, sediment reactions, secondary minerals, alkalinity additionality, biological responses and site-specific air–sea exchange require further evidence.",
            "The Ni mass is a total mobilization upper bound, not observed dissolved concentration or proof of ecological safety. Other metal releases and turbidity remain unquantified.",
            "Original supplier database labels are retained as provenance. A selected background must resolve exact activity/product/location identities before calculation; no successful 3.12 import is implied.",
        ],
        sources=SOURCES,
        temporal_checks=timing_checks,
        validation="Source hash and immutability checked; workbook parsed by bw2io; amounts, normalization, ocean compartment, water/transport arithmetic and temporal weight closure checked. Background linking and full-background LCA have not been run.",
    )
    # Parse the actual generated artifact with the intended importer, no writes.
    from bw2io import ExcelImporter

    importer = ExcelImporter(str(output_path))
    assert len(importer.data) == len(SCENARIOS)
    for ds in importer.data:
        assert sum(e["type"] == "production" for e in ds["exchanges"]) == 1
        for e in ds["exchanges"]:
            if e.get("temporal_distribution") == 6:
                weights = json.loads(e["temporal_weights"])
                offsets = json.loads(e["temporal_offsets"])
                assert len(weights) == len(offsets) and abs(sum(weights) - 1) < 1e-12
                assert all(w >= 0 for w in weights)
    (output / "erw_review.json").write_text(json.dumps(review, indent=2) + "\n")
    print(
        json.dumps(
            {
                "workbook": str(output_path),
                "scenarios": len(importer.data),
                "source_unchanged": True,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.source, args.output)
