"""Export foreground CO₂ + complete root-supplier GWP contributions for Seoul.

Run in the TRAILS environment. Background matrices stay in ignored build/.
The original NPi archive is absent locally; its trusted interpolation cache is
read without mutation and the selected 2025 snapshot is reconstructed. Results
must close to the existing public static scores before they can be exported.
"""

from pathlib import Path
import csv
import json
import pickle
import struct
import zipfile
import hashlib
import sys
from datetime import datetime, timezone
import numpy as np
from scipy.sparse.linalg import spsolve
from datapackage import Package
import trails
from trails import Trails
from trails.lca import _build_direct_technosphere_for_year
from trails.characterization import get_cf_matrix
from bw2io import ExcelImporter

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from apps.setac_2026 import results

WORK = REPO / "build/seoul-cdr-root-extraction"
CACHE = Path(
    "/Users/romain/Library/Application Support/trails/cache/interp_31c40820e920"
)
FOREGROUND = (
    REPO
    / "build/setac-regeneration-20261014/data/inventories/generated/lcss2026-foreground.xlsx"
)
METHOD = "IPCC 2021 (incl. biogenic CO2) no LT - climate change: total (incl. biogenic CO2) no LT - global warming potential (GWP100) no LT"
PK_PACKAGE = REPO / "build/seoul-erw-calculation/selected-package/datapackage.json"


def mapped_npy(path, member):
    """Read a ZIP_STORED .npy member as a read-only memory map, not a giant array."""
    with zipfile.ZipFile(path) as z:
        info = z.getinfo(member)
        assert info.compress_type == zipfile.ZIP_STORED
        with path.open("rb") as raw:
            raw.seek(info.header_offset)
            header = struct.unpack("<IHHHHHIIIHH", raw.read(30))
            start = info.header_offset + 30 + header[-2] + header[-1]
        with z.open(member) as f:
            version = np.lib.format.read_magic(f)
            shape, fortran, dtype = (
                np.lib.format.read_array_header_1_0(f)
                if version == (1, 0)
                else np.lib.format.read_array_header_2_0(f)
            )
            offset = start + f.tell()
    return np.memmap(
        path,
        mode="r",
        dtype=dtype,
        offset=offset,
        shape=shape,
        order="F" if fortran else "C",
    )


def snapshot_package():
    out = WORK / "npi-2025"
    out.mkdir(parents=True, exist_ok=True)
    prototype = json.loads(
        (
            REPO / "build/seoul-erw-calculation/selected-package/datapackage.json"
        ).read_text()
    )
    resources = [r for r in prototype["resources"] if "/2025/" in r["path"]]
    metadata = pickle.load((CACHE / "indices.pkl").open("rb"))
    position = json.loads((CACHE / "meta.json").read_text())["scenario_labels"].index(
        "2025"
    )
    for r in resources:
        r["path"] = r["path"].replace("SSP2-PkBudg1000", "SSP2-NPi")
        p = out / r["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        fields = [f["name"] for f in r["schema"]["fields"]]
        with p.open("w", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(fields)
            if r["name"].endswith("_index"):
                key = (
                    "activity_indices"
                    if r["name"].startswith("a_")
                    else "biosphere_indices"
                )
                for idx, row in metadata[key]["2025"].items():
                    w.writerow(
                        [
                            idx if name == "index" else row.get(name, "")
                            for name in fields
                        ]
                    )
            else:
                path = CACHE / ("A.npz" if r["name"].startswith("a_") else "B.npz")
                coords = mapped_npy(path, "coords.npy")
                values = mapped_npy(path, "data.npy")
                mask = coords[0] == position
                for i, j, value in zip(coords[1, mask], coords[2, mask], values[mask]):
                    row = {
                        fields[0]: int(i),
                        fields[1]: int(j),
                        "value": float(value),
                        "uncertainty type": 0,
                        "loc": float(value),
                        "negative": int(value < 0),
                        "flip": 0,
                    }
                    w.writerow([row.get(name, "") for name in fields])
                print(r["name"], int(mask.sum()), flush=True)
    prototype["resources"] = resources
    prototype["scenarios"] = []
    prototype["name"] = "seoul-npi-2025-static-cache-extraction"
    (out / "datapackage.json").write_text(json.dumps(prototype))
    return out / "datapackage.json"


def main(year=2025):
    WORK.mkdir(parents=True, exist_ok=True)
    expected_hash = json.loads(
        (REPO / "apps/setac_2026/data/processed/system_inventory_2025.json").read_text()
    )["basis"]["foreground_sha256"]
    assert hashlib.sha256(FOREGROUND.read_bytes()).hexdigest() == expected_hash
    package = snapshot_package() if year == 2025 else PK_PACKAGE
    pathway = "SSP2-NPi" if year == 2025 else "SSP2-PkBudg1000"
    importer = ExcelImporter(str(FOREGROUND))
    importer.apply_strategies()
    imported = {
        (d["name"], d.get("reference product"), d.get("location"))
        for d in importer.data
    }
    output = {
        "scope": "Direct foreground exchanges and full static LCA per signed supplier edge at the foreground boundary. Root suppliers include their entire upstream chains; no elementary-flow disaggregation of suppliers.",
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "method": METHOD,
        "trails_version": trails.__version__,
        "trails_source": str(Path(trails.__file__).resolve()),
        "extraction_script_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "source_snapshot_hashes": {
            r["path"]: hashlib.sha256(
                (package.parent / r["path"]).read_bytes()
            ).hexdigest()
            for r in json.loads(package.read_text())["resources"]
            if f"/{year}/" in r["path"]
        },
        "foreground_sha256": expected_hash,
        "cache_source": str(CACHE) if year == 2025 else None,
        "year": year,
        "pathway": pathway,
        "cases": {},
    }
    with Trails(
        Package(str(package)), interpolate_annual=False, ei_version="3.12"
    ) as model:
        model.import_excel_inventory(str(FOREGROUND))
        meta = model.activity_indices[str(year)]
        identity = lambda m: (m["name"], m.get("reference product"), m.get("location"))
        foreground = {int(i) for i, m in meta.items() if identity(m) in imported}
        native = [
            int(i)
            for i, m in meta.items()
            if m["name"]
            == results.static_activity_contributions_per_net_tonne(
                "DACCS", "SSP2-NPi", 2025, "not applicable"
            )[0][0].split(" | ")[0]
            and m.get("location") == "ENC"
        ]
        assert len(native) == 1
        foreground.update(native)
        A, _, _ = _build_direct_technosphere_for_year(model, year)
        cf = get_cf_matrix(model, [METHOD], {}, ei_version="3.12")[0]
        B = (
            model.B[int(model._get_scenario_context(year)[2]), :, :]
            .to_scipy_sparse()
            .tocsr()
        )
        direct = np.asarray(B @ cf).ravel()
        intensity = spsolve(A.T.tocsc(), direct)
        F = np.array(sorted(foreground))
        pos = {int(i): k for k, i in enumerate(F)}
        AFF = A[F, :][:, F].tocsc()
        assert np.allclose(A.diagonal()[F], 1)
        for case in ("DACCS", "BECCS"):
            name = (
                "carbon dioxide removal, DACCS, solid sorbent, low-temperature heat pump, LCSS 2026"
                if case == "DACCS"
                else "carbon dioxide removal, BECCS, new Nordic spruce CHP with CCS vs standing forest and Northern European energy, LCSS 2026"
            )
            matches = [
                int(i)
                for i, m in meta.items()
                if m["name"] == name and m.get("location") == "ENC"
            ]
            assert len(matches) == 1
            demand = np.zeros(len(F))
            demand[pos[matches[0]]] = 1000
            supply = spsolve(AFF, demand)
            suppliers = []
            biosphere = []
            for parent, amount in zip(F, supply):
                if abs(amount) < 1e-14:
                    continue
                col = A.getcol(parent).tocoo()
                for provider, coefficient in zip(col.row, col.data):
                    if provider in foreground:
                        continue
                    value = float(-coefficient * amount * intensity[provider])
                    if abs(value) > 1e-12:
                        suppliers.append(
                            {
                                "activity": meta[int(provider)]["name"],
                                "reference_product": meta[int(provider)].get(
                                    "reference product"
                                ),
                                "location": meta[int(provider)].get("location"),
                                "foreground_parent": meta[int(parent)]["name"],
                                "score": value,
                            }
                        )
                row = B.getrow(parent).tocoo()
                for flow, coefficient in zip(row.col, row.data):
                    value = float(coefficient * amount * cf[flow])
                    if abs(value) > 1e-12:
                        biosphere.append(
                            {
                                "flow": model.biosphere_indices[str(year)][int(flow)][
                                    "name"
                                ],
                                "foreground_activity": meta[int(parent)]["name"],
                                "score": value,
                            }
                        )
            value = sum(r["score"] for r in suppliers + biosphere)
            target = results.static_score(
                case,
                pathway,
                year,
                "not applicable"
                if case == "DACCS"
                else "new CHP+CCS vs standing forest and Northern European energy",
            )
            print(
                case,
                "root total",
                value,
                "source",
                target,
                "error",
                value - target,
                flush=True,
            )
            assert abs(value - target) < 1e-4
            model.static_lca(year, matches[0], [METHOD], amount=1000, ei_version="3.12")
            assert abs(float(np.asarray(model.static_score).sum()) - value) < 1e-6
            output["cases"][case] = {
                "total": value,
                "source_total": target,
                "suppliers": suppliers,
                "foreground": biosphere,
            }
    (REPO / f"apps/seoul_2026/data/cdr_static_roots_{year}.json").write_text(
        json.dumps(output, indent=2) + "\n"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, choices=(2025, 2050), default=2025)
    parser.add_argument("--cache", type=Path, default=CACHE)
    parser.add_argument("--foreground", type=Path, default=FOREGROUND)
    parser.add_argument("--package", type=Path, default=PK_PACKAGE)
    args = parser.parse_args()
    CACHE = args.cache.resolve()
    FOREGROUND = args.foreground.resolve()
    PK_PACKAGE = args.package.resolve()
    main(args.year)
