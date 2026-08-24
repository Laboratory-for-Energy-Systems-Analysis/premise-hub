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

SLIDE_TITLES = [
    "IAM scenarios for prospective LCA",
    "People need services, not fuel",
    "Emissions come from a connected system",
    "CO₂ accumulates, so the full pathway matters",
    "Why do we need integrated assessment?",
    "A target date is not a pathway",
    "An IAM is a structured thought experiment",
    "IAMs represent different parts of the system",
    "IAMs can answer the same question differently",
    "From emissions scenarios to policy evidence",
    "SSPs differ before climate policy is added",
    "SSP1–SSP3: from cooperation to fragmentation",
    "Fast innovation does not guarantee sustainability",
    "RCPs define radiative-forcing experiments",
    "CMIP7 families describe how emissions change over time",
    "A quantitative scenario combines three layers",
    "Choose a pathway before seeing its assumptions",
    "Investment changes the system over time",
    "First, compare the whole energy system",
    "Then examine the electricity chain",
    "Primary energy: resources entering the system",
    "Secondary energy: carriers produced after conversion",
    "Final energy: energy delivered to users",
    "Passenger cars: electrification reduces energy per kilometre",
    "Cement: lower emissions require a different kiln mix",
    "Steel: recycled and electric routes replace blast furnaces",
    "Space heating: electricity and heat networks replace fossil boilers",
    "Premise gets different levels of detail from each IAM",
    "What IAMs leave out",
    "Can you explain why the LCA result changed?",
    "Six IAMs group countries into different regions",
    "A Swiss inventory can map to different IAM regions",
    "Change one dimension at a time",
    "Explore how scenarios change each sector",
    "Low warming in 2100 can depend on large future removals",
    "Premise updates selected parts of the background database",
    "Turn a scenario result into a well-supported LCA statement",
    "Unit impact, deployment and causes are different questions",
    "Match boundaries before calculating total impact",
    "Trace an LCA result back to the scenario data",
    "Steel links production routes, unit impact and total output",
    "The IAM says solar; the LCA needs a specific module technology",
    "PV uncertainty affects indicators differently",
    "Similar warming can still have very different impacts",
    "Check the full chain before reporting a result",
    "Choose a scenario source with the detail your decision needs",
    "Premise translates scenarios; it is not a scenario model",
    "From one-off research links to shared scenario tools",
    "A build converts scenario choices into inventory changes",
    "Premise changes inventories; Brightway calculates results",
    "One set of databases supports three scales of analysis",
    "Resources for building and documenting scenarios",
]

CHAPTERS = [
    {"name": "Why IAMs", "start": 0, "end": 16},
    {"name": "IAM theory", "start": 17, "end": 29},
    {"name": "Scenario frameworks", "start": 30, "end": 32},
    {"name": "Read the pathways", "start": 33, "end": 34},
    {"name": "From IAM to Premise", "start": 35, "end": 36},
    {"name": "LCIA trade-offs", "start": 37, "end": 37},
    {"name": "Applied cases", "start": 38, "end": 51},
]

ANONYMOUS_SLIDE = SLIDE_TITLES.index("Choose a pathway before seeing its assumptions")
FIRST_SECTOR_SLIDE = SLIDE_TITLES.index("Explore how scenarios change each sector")
IAM_MAP_SLIDE = SLIDE_TITLES.index("Six IAMs group countries into different regions")
RESULT_TRACER_SLIDE = SLIDE_TITLES.index(
    "Trace an LCA result back to the scenario data"
)
LAST_SLIDE = len(SLIDE_TITLES) - 1


def chapter_for_slide(index: int) -> str:
    for chapter in CHAPTERS:
        if chapter["start"] <= index <= chapter["end"]:
            return chapter["name"]
    return CHAPTERS[-1]["name"]
