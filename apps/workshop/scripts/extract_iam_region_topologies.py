"""Normalize premise IAM topology files for the interactive workshop map."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pycountry


MODELS = {
    "image": "IMAGE",
    "message": "MESSAGE",
    "remind": "REMIND",
    "remind-eu": "REMIND-EU",
    "tiam-ucl": "TIAM-UCL",
    "gcam": "GCAM",
}

LEGACY_ISO3 = {
    "AN": "ANT",
    "CS": "SCG",
    "XK": "XKX",
    "US-PR": "PRI",
}


def iso3(code: str) -> str | None:
    if code in LEGACY_ISO3:
        return LEGACY_ISO3[code]
    country = pycountry.countries.get(alpha_2=code)
    return country.alpha_3 if country else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    result: dict[str, dict] = {}
    for slug, display_name in MODELS.items():
        source_file = args.source / f"{slug}-topology.json"
        raw = json.loads(source_file.read_text(encoding="utf-8"))
        regions: dict[str, list[str]] = {}
        skipped: dict[str, list[str]] = {}
        for region, country_codes in raw.items():
            if region == "World":
                continue
            converted: list[str] = []
            rejected: list[str] = []
            for country_code in country_codes:
                converted_code = iso3(country_code)
                if converted_code:
                    converted.append(converted_code)
                else:
                    rejected.append(country_code)
            regions[region] = sorted(set(converted))
            if rejected:
                skipped[region] = sorted(set(rejected))
        result[slug] = {
            "model": display_name,
            "premise_version": "2.4.6",
            "source": f"premise/iam_variables_mapping/topologies/{slug}-topology.json",
            "region_count": len(regions),
            "territory_count": len(
                {country for countries in regions.values() for country in countries}
            ),
            "regions": regions,
            "skipped_iso2_codes": skipped,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
