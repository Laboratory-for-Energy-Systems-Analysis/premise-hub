from __future__ import annotations

CORE_SLIDES = (
    ("LCA of CCS and CCUS applied to cement production", 30),
    (
        "We adapt a published cement CCUS inventory.",
        90,
    ),
    (
        "The three systems produce the same clinker but handle carbon differently.",
        60,
    ),
    (
        "Without capture, kiln carbon reaches the atmosphere.",
        60,
    ),
    ("CCS stores captured fossil and non-fossil CO₂ permanently.", 60),
    (
        "CCUS stores fossil carbon and turns non-fossil carbon into jet fuel.",
        75,
    ),
    ("How does the LCA approach change the case for investing in CCS or CCUS?", 45),
    (
        "How do CCS and CCUS compare under 2025 conditions?",
        300,
    ),
    (
        "Electricity, heat and material production change by 2035.",
        150,
    ),
    (
        "Do future conditions change which option has the lowest climate impact?",
        240,
    ),
    (
        "We assign dates to construction, carbon uptake and emissions.",
        120,
    ),
    ("Emissions and avoided emissions contribute in different years.", 300),
    (
        "A CO₂ pulse affects the climate long after it is emitted.",
        120,
    ),
    (
        "When do CCS and CCUS reduce the climate impact compared with BAU?",
        330,
    ),
    (
        "We find the CO₂ pulse with the same integrated climate response.",
        90,
    ),
    ("How does the chosen time window change the CO₂-pulse equivalent?", 330),
    ("The default comparisons favour CCS, followed by CCUS.", 180),
    (
        "These studies, datasets and tools support the analysis.",
        60,
    ),
    ("What else could change the investment decision?", 60),
)

APPENDIX_SLIDE_TITLES = (
    "We convert emissions and CO₂ uptake into a climate impact score.",
    "Inventory records describe the plant’s inputs and outputs.",
    "Energy supply and carbon timing are explicit modelling assumptions.",
    "Different components are replaced on different dates.",
    "These records identify the data and software used for the results.",
)

# Retained appendix content IDs. Sensitivities (4) and other sectors (5)
# are not part of navigation or PDF export; their underlying data is preserved.
APPENDIX_SECTION_IDS = (0, 1, 2, 3, 6)

CORE_SLIDE_TITLES = tuple(title for title, _seconds in CORE_SLIDES)
CORE_SLIDE_SECONDS = tuple(seconds for _title, seconds in CORE_SLIDES)
SLIDE_TITLES = CORE_SLIDE_TITLES + APPENDIX_SLIDE_TITLES

CHAPTERS = (
    {"name": "The case", "start": 0, "end": 6, "minutes": 7},
    {"name": "Current (static) LCA", "start": 7, "end": 7, "minutes": 5},
    {"name": "Prospective (static) LCA", "start": 8, "end": 9, "minutes": 7},
    {"name": "Time-explicit LCA", "start": 10, "end": 15, "minutes": 21},
    {"name": "What changes", "start": 16, "end": 18, "minutes": 4},
    {"name": "Appendix", "start": 19, "end": 23, "minutes": 0},
)

CORE_SLIDE_COUNT = len(CORE_SLIDE_TITLES)
APPENDIX_SLIDE_COUNT = len(APPENDIX_SLIDE_TITLES)
CORE_LAST_SLIDE = CORE_SLIDE_COUNT - 1
APPENDIX_START_SLIDE = CORE_SLIDE_COUNT
LAST_SLIDE = len(SLIDE_TITLES) - 1
DISCUSSION_SLIDE = CORE_LAST_SLIDE
PRESENTATION_SECONDS = sum(CORE_SLIDE_SECONDS)

for chapter in CHAPTERS:
    chapter["minutes"] = (
        sum(CORE_SLIDE_SECONDS[chapter["start"] : chapter["end"] + 1]) / 60
    )

assert CORE_SLIDE_COUNT == 19
assert PRESENTATION_SECONDS == 45 * 60


def chapter_for_slide(index: int) -> dict:
    for chapter in CHAPTERS:
        if chapter["start"] <= index <= chapter["end"]:
            return chapter
    return CHAPTERS[-1]


def slide_seconds(index: int) -> int:
    return CORE_SLIDE_SECONDS[index] if 0 <= index < CORE_SLIDE_COUNT else 0
