"""Extract the MCV annex stock series from an iam-preprocessor vintage archive."""

import argparse
from bisect import bisect_left
from hashlib import file_digest, sha256
import json
from math import fsum
from pathlib import Path
from zipfile import ZipFile


ASSETS = {
    "photovoltaic": ("pv", "ENC", "GW"),
    "hydropower": ("hydro", "ENC", "GW"),
    "electric_cars": ("passenger-ldv-4w-bev", "FRA", "million veh"),
    "heat_pumps": ("heat-pump", "FRA", "GW"),
}
BANDS = [2004, 2029, 2049, 2069, 2089, 2100]
SUMMARY_YEAR = 2050


def extract(archive):
    from pyarrow import BufferReader
    from pyarrow.parquet import read_table

    with ZipFile(archive) as package:
        manifest = json.loads(package.read("datapackage.json"))
        assert manifest["profile"] == "iam-preprocessor-stock-vintages"
        assert (manifest["model"], manifest["scenario"]) == ("REMIND", "SSP2-EU21-PkBudg1000")
        assert manifest["timing"]["stock"] == "end_of_year"
        assert json.loads(package.read("validation.json"))["status"] == "pass"
        parquet = package.read("vintages.parquet")
    resource, = [r for r in manifest["resources"] if r["path"] == "vintages.parquet"]
    assert sha256(parquet).hexdigest() == resource["sha256"]
    years = list(range(manifest["reference_year"], manifest["end_year"] + 1))
    assert years[-1] == BANDS[-1] and SUMMARY_YEAR in years
    cases = {}
    for key, (asset, region, unit) in ASSETS.items():
        table = read_table(
            BufferReader(parquet),
            columns=["year", "cohort_year", "unit", "value"],
            filters=[("asset", "=", asset), ("region", "=", region), ("metric", "=", "stock")],
        )
        annual_stock = {year: [[] for _ in BANDS] for year in years}
        weighted_ages = []
        observed_years = set()
        for row in table.to_pylist():
            year, cohort, value = row["year"], row["cohort_year"], row["value"]
            assert row["unit"] == unit and cohort <= year and value >= 0
            annual_stock[year][bisect_left(BANDS, cohort)].append(value)
            observed_years.add(year)
            if year == SUMMARY_YEAR:
                weighted_ages.append((year - cohort) * value)
        assert observed_years == set(years)
        total = fsum(value for band in annual_stock[SUMMARY_YEAR] for value in band)
        cases[key] = {
            "asset": asset, "region": region, "unit": unit,
            "stock": [[fsum(annual_stock[year][i]) for year in years] for i in range(len(BANDS))],
            "mean_age_at_summary_year": fsum(weighted_ages) / total,
        }
    with Path(archive).open("rb") as stream:
        archive_sha = file_digest(stream, "sha256").hexdigest()
    return {
        "model": manifest["model"], "scenario": manifest["scenario"], "metric": "stock",
        "archive": Path(archive).name, "archive_sha256": archive_sha, "parquet_sha256": resource["sha256"],
        "years": years, "build_band_end_years": BANDS, "summary_year": SUMMARY_YEAR, "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data/stock_vintage_examples.json")
    args = parser.parse_args()
    args.output.write_text(json.dumps(extract(args.archive), indent=2, allow_nan=False) + "\n")
