from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

SYSTEMS = ("BAU", "CCS", "CCUS")
PATHWAYS = ("SSP2-NPi", "SSP2-PkBudg1000")
CAMPAIGN_TONNES = 49_275_000.0


@dataclass(frozen=True)
class ResultState:
    pathway: str = "SSP2-NPi"
    grouping: str = "stage"
    area_mode: str = "stacked"
    normalization: str = "per_tonne"
    fair_metric: str = "radiative_forcing"
    pulse_metric: str = "forcing"
    uncertainty: bool = False
    window_start: int = 2025
    window_end: int = 2100


DEFAULT_RESULT_STATE = asdict(ResultState())


def normalize_result_state(payload: dict | None = None) -> dict:
    values = {**DEFAULT_RESULT_STATE, **(payload or {})}
    pathway = str(values["pathway"])
    grouping = str(values["grouping"])
    area_mode = str(values["area_mode"])
    normalization = str(values["normalization"])
    fair_metric = str(values["fair_metric"])
    pulse_metric = str(values["pulse_metric"])
    start = int(values["window_start"])
    end = int(values["window_end"])
    return {
        "pathway": pathway if pathway in PATHWAYS else "SSP2-NPi",
        "grouping": grouping if grouping in {"stage", "flow"} else "stage",
        "area_mode": area_mode if area_mode in {"stacked", "unstacked"} else "stacked",
        "normalization": (
            normalization if normalization in {"per_tonne", "absolute"} else "per_tonne"
        ),
        "fair_metric": (
            fair_metric
            if fair_metric in {"radiative_forcing", "temperature"}
            else "radiative_forcing"
        ),
        "pulse_metric": (
            pulse_metric if pulse_metric in {"forcing", "temperature"} else "forcing"
        ),
        "uncertainty": bool(values["uncertainty"]),
        "window_start": max(1995, min(2035, start)),
        "window_end": max(2040, min(2200, end)),
    }


def project_timeline(stage: str) -> tuple[dict, ...]:
    root = Path(__file__).resolve().parents[1] / "data/assumptions"
    components = json.loads((root / "component_lifetimes.json").read_text())[
        "components"
    ]
    replacements = sorted(
        {
            year
            for component in components
            if component["column"] != 100
            for year in range(
                component["first_year"] + component["lifetime_years"],
                2065,
                component["lifetime_years"],
            )
        }
    )
    profiles = json.loads((root / "non_fossil_uptake_profiles.json").read_text())[
        "profiles"
    ]
    rows = [
        {
            "label": "Historical uptake",
            "start": 2035 + min(min(p["offsets"]) for p in profiles),
            "end": 2064 + max(max(p["offsets"]) for p in profiles),
            "kind": "uptake",
            "visible": stage in {"trails", "fair", "pulse"},
        },
        {
            "label": "Construction",
            "start": 2035,
            "end": 2035,
            "kind": "construction",
            "visible": stage in {"trails", "fair", "pulse"},
        },
        {
            "label": "Operation",
            "start": 2035,
            "end": 2064,
            "kind": "operation",
            "visible": stage in {"trails", "fair", "pulse"},
        },
        {
            "label": "Replacements",
            "start": min(replacements, default=2035),
            "end": max(replacements, default=2035),
            "events": replacements,
            "kind": "replacement",
            "visible": stage in {"trails", "fair", "pulse"},
        },
        {
            "label": "Annual fuel use (+1 y); final EOL",
            "start": 2036,
            "end": 2065,
            "kind": "fuel",
            "visible": stage in {"trails", "fair", "pulse"},
        },
        {
            "label": "Climate response",
            "start": 2035,
            "end": 2200,
            "kind": "climate",
            "visible": stage in {"fair", "pulse"},
        },
    ]
    if stage == "current":
        return (
            {
                "label": "All inventory",
                "start": 2025,
                "end": 2025,
                "kind": "collapsed",
                "visible": True,
            },
        )
    if stage == "prospective":
        return (
            {
                "label": "All inventory",
                "start": 2035,
                "end": 2035,
                "kind": "collapsed",
                "visible": True,
            },
        )
    return tuple(row for row in rows if row["visible"])


SYSTEM_COPY = {
    "BAU": {
        "verb": "emit",
        "destination": "Atmosphere",
        "service": "Recovered heat exported",
    },
    "CCS": {
        "verb": "capture both fractions",
        "destination": "North Sea storage",
        "service": "Permanent storage",
    },
    "CCUS": {
        "verb": "split by origin",
        "destination": "Storage + jet fuel",
        "service": "Storage and fuel substitution",
    },
}
