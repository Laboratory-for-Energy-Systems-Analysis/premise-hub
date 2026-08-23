from __future__ import annotations

CORE_SLIDE_TITLES = [
    "How time changes LCA results",
    "One study, three treatments of time",
    "Two routes to permanent CO₂ storage",
    "One functional unit: 1 net tonne of atmospheric CO₂ stored",
    "BECCS greenfield: project versus standing forest",
    "DACCS: electricity powers capture; heat regenerates the sorbent",
    "One storage service, different GWP100 contributions",
    "SSP2 and REMIND-EU scenarios",
    "From IAM pathways to LCI backgrounds",
    "Changes in electricity, heat and materials",
    "Each plant cohort is evaluated against twenty annual backgrounds",
    "Why event timing matters",
    "From scenario snapshots to annual matrices",
    "Project timeline",
    "BECCS routing network",
    "DACCS routing network",
    "Temporal GWP100",
    "FaIR climate response",
    "Pulse-equivalence concept",
    "Interactive pulse-equivalence window",
    "GWP100 versus pulse equivalence",
    "Choosing the treatment of time",
    "Open-source workflow",
    "Discussion and contact",
]

APPENDIX_SLIDE_TITLES = [
    "Appendix A — Accounting and temporal equations",
    "Appendix B — Sources and reproducibility",
]

SLIDE_TITLES = CORE_SLIDE_TITLES + APPENDIX_SLIDE_TITLES

CHAPTERS = [
    {"name": "Opening", "start": 0, "end": 1, "minutes": 4},
    {"name": "Conventional LCA", "start": 2, "end": 6, "minutes": 14},
    {"name": "Prospective LCA", "start": 7, "end": 10, "minutes": 12},
    {"name": "Time-explicit LCA", "start": 11, "end": 19, "minutes": 15},
    {"name": "Synthesis", "start": 20, "end": 23, "minutes": 15},
    {"name": "Appendix", "start": 24, "end": 25, "minutes": 0},
]

CORE_SLIDE_COUNT = len(CORE_SLIDE_TITLES)
APPENDIX_SLIDE_COUNT = len(APPENDIX_SLIDE_TITLES)
CORE_LAST_SLIDE = CORE_SLIDE_COUNT - 1
APPENDIX_START_SLIDE = CORE_SLIDE_COUNT
LAST_SLIDE = len(SLIDE_TITLES) - 1


def chapter_for_slide(index: int) -> dict:
    for chapter in CHAPTERS:
        if chapter["start"] <= index <= chapter["end"]:
            return chapter
    return CHAPTERS[-1]
