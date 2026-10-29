"""Export signed first-tier ERW attribution, without changing inventories.

Use the same selected scenario package and reviewed foreground as the main
calculation. Adjoint static activity intensities are checked against the
public static_lca score. Temporal roots use the existing fixed-depth-one model.
"""

from pathlib import Path
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import sys
import numpy as np
from datapackage import Package
from trails import Trails, search_activity
from trails.static_activity_scores import _ensure_static_activity_scores
import trails

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from apps.seoul_2026.scripts.calculate_erw_comparison import METHOD


def main(package, foreground, output):
    source = json.loads((REPO / "apps/seoul_2026/data/erw_comparison.json").read_text())
    assert (
        hashlib.sha256(foreground.read_bytes()).hexdigest()
        == source["ei312_foreground_sha256"]
    )
    record = dict(
        calculated_at=datetime.now(timezone.utc).isoformat(),
        trails=trails.__version__,
        package_sha256=source["package_sha256"],
        foreground_sha256=source["ei312_foreground_sha256"],
        method=METHOD,
        static=[],
        temporal=[],
        scope="Static first-tier supplier intensities; temporal fixed-depth-one responsible roots. Full residual background solves retained.",
    )
    with Trails(
        Package(str(package)), interpolate_annual=False, ei_version="3.12"
    ) as model:
        model.import_excel_inventory(str(foreground))
        metadata = {
            int(i): m
            for mapping in model.activity_indices.values()
            for i, m in mapping.items()
        }
        static = search_activity(
            model,
            name="coastal olivine weathering deployment, static reference",
            reference_product="coastal weathering deployment, 1.25 kg rock",
            location="RER",
            match="exact",
        )
        assert len(static.rows) == 1
        idx = int(static.rows[0][0])
        scores = _ensure_static_activity_scores(
            model,
            methods=[METHOD],
            years=[2025, 2050],
            ei_version="3.12",
            use_cache=False,
        )
        print("Static intensity shape", scores.scores.shape, flush=True)
        for yi, year in enumerate((2025, 2050)):
            model.static_lca(year, idx, [METHOD], amount=1000, ei_version="3.12")
            total = float(np.asarray(model.static_score).sum())
            assert (
                abs(
                    total
                    - next(
                        r["net_kg_co2eq"]
                        for r in source["snapshots"]
                        if r["year"] == year
                    )
                )
                < 1e-5
            )
            rows = []
            for demand_year, demands in model.expand_temporal_exchanges(
                year, idx, 1000, use_temporal_distributions=False
            ).items():
                assert demand_year == year
                for root, amount in demands.items():
                    meta = metadata[root]
                    rows.append(
                        dict(
                            activity=meta["name"],
                            reference_product=meta.get("reference product"),
                            score=float(amount * scores.scores[0, yi, root]),
                        )
                    )
            direct = total - sum(r["score"] for r in rows)
            assert abs(direct + 1000) < 1e-5
            rows.append(
                dict(
                    activity="Atmospheric CO₂ uptake",
                    reference_product="direct foreground biosphere",
                    score=direct,
                )
            )
            record["static"].append(dict(year=year, contributions=rows, total=total))
            print(
                "Static",
                year,
                total,
                [(r["activity"], r["score"]) for r in rows],
                flush=True,
            )
        dated = search_activity(
            model,
            name="coastal olivine weathering deployment, dated reference",
            reference_product="coastal weathering deployment, 1.25 kg rock",
            location="RER",
            match="exact",
        )
        assert len(dated.rows) == 1
        model.temporal_routing(
            start_year=2030,
            start_act_idx=int(dated.rows[0][0]),
            amount=1000,
            max_depth=1,
            adaptive_relative_score_cutoff=None,
            attribute_to_roots=True,
            show_progress=False,
        )
        model.lci(
            show_progress=False, solver_mode="direct", inventory_backend="factorized"
        )
        model.lcia(methods=[METHOD], ei_version="3.12")
        score = model.scores
        reduced = score.sum(
            dim=[d for d in score.dims if d not in ("year", "root activity")]
        ).transpose("root activity", "year")
        values = (
            reduced.data.todense()
            if hasattr(reduced.data, "todense")
            else np.asarray(reduced.data)
        )
        for root, vals in zip(reduced["root activity"].values, values):
            if not np.any(vals):
                continue
            meta = metadata[int(root)]
            record["temporal"].append(
                dict(
                    activity=meta["name"],
                    reference_product=meta.get("reference product"),
                    series=[
                        dict(age=int(y) - 2030, score=float(v))
                        for y, v in zip(reduced.year.values, vals)
                        if v != 0
                    ],
                )
            )
        actual = defaultdict(float)
        for row in record["temporal"]:
            for p in row["series"]:
                actual[p["age"]] += p["score"]
        expected = {r["age"]: r["score"] for r in source["routed_temporal"]}
        error = max(
            abs(actual[y] - expected.get(y, 0)) for y in actual.keys() | expected.keys()
        )
        assert error < 1e-3, error
        record["max_annual_closure_error_kg"] = error
        print("Temporal roots", len(record["temporal"]), "closure", error, flush=True)
    output.write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package",
        type=Path,
        default=REPO / "build/seoul-erw-calculation/selected-package/datapackage.json",
    )
    parser.add_argument(
        "--foreground",
        type=Path,
        default=REPO / "apps/seoul_2026/data/coastal_erw_ei312.xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "apps/seoul_2026/data/erw_contributions.json",
    )
    args = parser.parse_args()
    main(args.package, args.foreground, args.output)
