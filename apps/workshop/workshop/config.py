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
IAM_REGION_TOPOLOGIES_FILE = (
    DATA_DIR / "processed" / "iam_region_topologies.json"
)

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
    "Societies demand services—not tonnes of fuel",
    "Emissions are distributed across a connected system",
    "CO₂ accumulates; warming follows the cumulative total",
    "Why integrated assessment?",
    "A deadline is not a pathway",
    "An IAM is a disciplined thought experiment",
    "Not every IAM integrates the same systems",
    "IAMs can solve the same question differently",
    "From emissions scenarios to policy evidence",
    "The SSPs diverge before climate policy is added",
    "SSP1–SSP3: from cooperation to fragmentation",
    "SSP4 and SSP5: capability is not sustainability",
    "RCPs describe radiative-forcing experiments",
    "CMIP7 families describe emissions through time",
    "A quantitative scenario combines three layers",
    "Choose before you know the assumptions",
    "From investment to system change",
    "First, compare the whole energy system",
    "Then zoom in on the electricity chain",
    "Primary energy: resources entering the system",
    "Secondary energy: carriers after conversion",
    "Final energy: what end-use sectors receive",
    "Passenger cars: electrification changes the energy arithmetic",
    "Cement: decarbonization changes the kiln fleet",
    "Steel: circular and electric routes displace blast furnaces",
    "Space heating: electrification and networks replace fossil boilers",
    "Premise sees a different level of detail in each IAM",
    "What IAMs leave outside",
    "Can you defend why the LCA result changed?",
    "Six IAMs divide the same world differently",
    "CH stays Swiss—but its IAM region depends on the model",
    "Change one dimension at a time",
    "Explore the transformation that matters",
    "Low 2100 warming can rely on large future removals",
    "Premise transforms selected levers—not the whole economy",
    "Turn a scenario result into a defensible LCA statement",
    "Unit impact, deployment and cause are different questions",
    "Match boundaries before turning intensity into total impact",
    "Trace one result from IAM signal to LCIA score",
    "Steel connects route choice, inventory intensity and total demand",
    "IAM says ‘solar’; LCA needs a module technology",
    "PV uncertainty is indicator-specific",
    "Similar warming does not mean a similar footprint",
    "Audit the chain before reporting the result",
    "Choose the scenario source that resolves the decision lever",
    "Premise is the translation layer—not the scenario model",
    "From research coupling to open scenario infrastructure",
    "A build turns scenario coordinates into inventory changes",
    "Brightway computes; Activity Browser makes scenarios explorable",
    "The same databases support three analytical scales",
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

ANONYMOUS_SLIDE = SLIDE_TITLES.index("Choose before you know the assumptions")
FIRST_SECTOR_SLIDE = SLIDE_TITLES.index("Explore the transformation that matters")
IAM_MAP_SLIDE = SLIDE_TITLES.index("Six IAMs divide the same world differently")
RESULT_TRACER_SLIDE = SLIDE_TITLES.index(
    "Trace one result from IAM signal to LCIA score"
)
LAST_SLIDE = len(SLIDE_TITLES) - 1


def chapter_for_slide(index: int) -> str:
    for chapter in CHAPTERS:
        if chapter["start"] <= index <= chapter["end"]:
            return chapter["name"]
    return CHAPTERS[-1]["name"]
