from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PATHWAY_FILE = DATA_DIR / "processed" / "workshop_pathways.csv.gz"
LCIA_FILE = DATA_DIR / "processed" / "lcia_results.csv"
LCIA_CONTRIBUTIONS_FILE = DATA_DIR / "processed" / "lcia_contributions.csv"
IMAGE_REGION_MAPPING_FILE = DATA_DIR / "image_region_mapping.json"
REMIND_EU_REGION_MAPPING_FILE = DATA_DIR / "remind_eu_region_mapping.json"
MECHANICS_FILE = DATA_DIR / "processed" / "remind_hydrogen_mechanics.csv"
IMAGE_ENERGY_LAYERS_FILE = DATA_DIR / "processed" / "image_energy_layers.csv"
IMAGE_ELECTRICITY_CHAIN_FILE = (
    DATA_DIR / "processed" / "image_electricity_chain_example.csv"
)
IMAGE_TOTAL_ENERGY_CHAIN_FILE = DATA_DIR / "processed" / "image_total_energy_chain.csv"
IMAGE_END_USE_TRANSFORMATIONS_FILE = (
    DATA_DIR / "processed" / "image_end_use_transformations.csv"
)
PREMISE_MAPPING_COUNTS_FILE = DATA_DIR / "processed" / "premise_mapping_counts.csv"
IAM_REGION_TOPOLOGIES_FILE = DATA_DIR / "processed" / "iam_region_topologies.json"

with (DATA_DIR / "narratives.json").open(encoding="utf-8") as stream:
    NARRATIVES = json.load(stream)

with (DATA_DIR / "premise_transformations.json").open(encoding="utf-8") as stream:
    PREMISE_TRANSFORMATIONS = json.load(stream)

with (DATA_DIR / "region_mapping.json").open(encoding="utf-8") as stream:
    REGION_MAPPING = json.load(stream)

CORE_SCENARIOS = ["SSP1-L", "SSP2-VLHO", "SSP2-M", "SSP3-H"]
ANONYMOUS_ORDER = CORE_SCENARIOS.copy()
CORE_YEARS = [2020, 2040, 2060]

CORE_SLIDE_TITLES = [
    "IAM scenarios for prospective LCA",
    "People need services, not fuel",
    "Emissions come from a connected system",
    "CO₂ accumulates, so the full pathway matters",
    "Why do we need integrated assessment?",
    "A target date is not a pathway",
    "An IAM is a structured thought experiment",
    "IAMs represent different parts of the system",
    "IAMs can answer the same question differently",
    "SSPs differ before climate policy is added",
    "SSP1–SSP3: from cooperation to fragmentation",
    "RCPs define radiative-forcing experiments",
    "CMIP7 families describe how emissions change over time",
    "A quantitative scenario combines three layers",
    "Choose a pathway before seeing its assumptions",
    "Investment changes the system over time",
    "First, compare the whole energy system",
    "Steel: recycled and electric routes replace blast furnaces",
    "Premise gets different levels of detail from each IAM",
    "What IAMs leave out",
    "A Swiss inventory can map to different IAM regions",
    "Change one dimension at a time",
    "Explore how scenarios change each sector",
    "Premise updates selected parts of the background database",
    "Turn a scenario result into a well-supported LCA statement",
    "Unit impact, deployment and causes are different questions",
    "Trace an LCA result back to the scenario data",
    "Similar warming can still have very different impacts",
    "Premise translates scenarios; it is not a scenario model",
    "A build converts scenario choices into inventory changes",
    "Resources for building and documenting scenarios",
]

APPENDIX_SLIDE_TITLES = [
    # Framework and policy history.
    "From emissions scenarios to policy evidence",
    "Fast innovation does not guarantee sustainability",
    # Energy-accounting detail.
    "Then examine the electricity chain",
    "Primary energy: resources entering the system",
    "Secondary energy: carriers produced after conversion",
    "Final energy: energy delivered to users",
    # Additional sector examples.
    "Passenger cars: electrification reduces energy per kilometre",
    "Cement: lower emissions require a different kiln mix",
    "Space heating: electricity and heat networks replace fossil boilers",
    # Model, narrative and geography detail.
    "Can you explain why the LCA result changed?",
    "Six IAMs group countries into different regions",
    # Additional interpretation and applied cases.
    "Low warming in 2100 can depend on large future removals",
    "Match boundaries before calculating total impact",
    "Steel links production routes, unit impact and total output",
    "The IAM says solar; the LCA needs a specific module technology",
    "PV uncertainty affects indicators differently",
    "Check the full chain before reporting a result",
    "Choose a scenario source with the detail your decision needs",
    # Premise history and extended workflow context.
    "From one-off research links to shared scenario tools",
    "Premise changes inventories; Brightway calculates results",
    "One set of databases supports three scales of analysis",
]

SLIDE_TITLES = CORE_SLIDE_TITLES + APPENDIX_SLIDE_TITLES

# Keep the live narrative lean while preserving a direct route to the most useful
# supporting material. Each core slide exposes at most one compact detail link;
# related backup slides remain sequential once the presenter opens that section.
BACKUP_LINKS = {
    "IAMs can answer the same question differently": {
        "label": "Policy-history detail",
        "target": "From emissions scenarios to policy evidence",
    },
    "SSP1–SSP3: from cooperation to fragmentation": {
        "label": "SSP4–SSP5 detail",
        "target": "Fast innovation does not guarantee sustainability",
    },
    "First, compare the whole energy system": {
        "label": "Energy-chain detail",
        "target": "Then examine the electricity chain",
    },
    "Steel: recycled and electric routes replace blast furnaces": {
        "label": "More sector examples",
        "target": "Passenger cars: electrification reduces energy per kilometre",
    },
    "A Swiss inventory can map to different IAM regions": {
        "label": "Six-IAM region detail",
        "target": "Six IAMs group countries into different regions",
    },
    "Explore how scenarios change each sector": {
        "label": "Carbon-removal detail",
        "target": "Low warming in 2100 can depend on large future removals",
    },
    "Unit impact, deployment and causes are different questions": {
        "label": "Boundary-matching detail",
        "target": "Match boundaries before calculating total impact",
    },
    "Trace an LCA result back to the scenario data": {
        "label": "Steel causal chain",
        "target": "Steel links production routes, unit impact and total output",
    },
    "Similar warming can still have very different impacts": {
        "label": "PV uncertainty case",
        "target": "The IAM says solar; the LCA needs a specific module technology",
    },
    "Premise translates scenarios; it is not a scenario model": {
        "label": "Premise history",
        "target": "From one-off research links to shared scenario tools",
    },
    "A build converts scenario choices into inventory changes": {
        "label": "Brightway hand-off",
        "target": "Premise changes inventories; Brightway calculates results",
    },
}

CHAPTERS = [
    {"name": "Why IAMs", "start": 0, "end": 8, "minutes": 16},
    {"name": "Scenario frameworks", "start": 9, "end": 14, "minutes": 15},
    {"name": "Read the pathways", "start": 15, "end": 22, "minutes": 18},
    {"name": "From IAM to Premise", "start": 23, "end": 24, "minutes": 8},
    {"name": "LCIA and interpretation", "start": 25, "end": 27, "minutes": 11},
    {"name": "Build and report", "start": 28, "end": 30, "minutes": 7},
    {"name": "Backup", "start": 31, "end": 51, "minutes": 0},
]

ANONYMOUS_SLIDE = SLIDE_TITLES.index("Choose a pathway before seeing its assumptions")
FIRST_SECTOR_SLIDE = SLIDE_TITLES.index("Explore how scenarios change each sector")
IAM_MAP_SLIDE = SLIDE_TITLES.index("Six IAMs group countries into different regions")
RESULT_TRACER_SLIDE = SLIDE_TITLES.index(
    "Trace an LCA result back to the scenario data"
)
CORE_SLIDE_COUNT = len(CORE_SLIDE_TITLES)
APPENDIX_SLIDE_COUNT = len(APPENDIX_SLIDE_TITLES)
CORE_LAST_SLIDE = CORE_SLIDE_COUNT - 1
APPENDIX_START_SLIDE = CORE_SLIDE_COUNT
LAST_SLIDE = len(SLIDE_TITLES) - 1


def chapter_for_slide(index: int) -> str:
    for chapter in CHAPTERS:
        if chapter["start"] <= index <= chapter["end"]:
            return chapter["name"]
    return CHAPTERS[-1]["name"]
