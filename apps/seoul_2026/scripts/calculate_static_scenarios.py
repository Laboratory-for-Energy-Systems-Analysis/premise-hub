"""Add 2035/2050 scenario comparisons without changing the source lectures.

Run in the TRAILS environment. Licensed matrices stay under ignored build/.
NPi uses the same read-only annual cache as the source SETAC calculations;
its original archive is absent. The unrelated older REMIND archive is not used.
Forward static LCAs independently check adjoint/root decompositions. Existing
2050 CDR and PK ERW scores must match before the new public JSON is written.
"""

from copy import deepcopy
from datetime import datetime, timezone
import csv
import gc
import hashlib
import json
from pathlib import Path
import pickle
import sys
from zipfile import ZipFile

import bw2data as bd
from bw2io import ExcelImporter
from datapackage import Package
import numpy as np
from scipy.sparse.linalg import spsolve
import trails
from trails import Trails
from trails.characterization import get_cf_matrix
from trails.lca import _build_direct_technosphere_for_year

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from apps.setac_2026 import results
from apps.seoul_2026.scripts.extract_cdr_static_roots import (
    mapped_npy, CACHE, FOREGROUND, METHOD as CDR_METHOD,
)
from apps.seoul_2026.scripts.calculate_erw_comparison import (
    ARCHIVE, METHOD as ERW_METHOD,
)

WORK = REPO / "build/seoul-static-scenarios"
ERW_FG = REPO / "apps/seoul_2026/data/coastal_erw_ei312.xlsx"
PUBLIC = REPO / "apps/seoul_2026/data/static_scenario_results.json"
CASES = {
    "DACCS": (
        "carbon dioxide removal, DACCS, solid sorbent, low-temperature heat pump, LCSS 2026",
        "ENC", CDR_METHOD,
    ),
    "BECCS": (
        "carbon dioxide removal, BECCS, new Nordic spruce CHP with CCS vs standing forest and Northern European energy, LCSS 2026",
        "ENC", CDR_METHOD,
    ),
    "ERW": (
        "coastal olivine weathering deployment, static reference", "RER", ERW_METHOD,
    ),
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare_pk(year):
    target = WORK / f"{year}-SSP2-PkBudg1000"
    target.mkdir(parents=True, exist_ok=True)
    with ZipFile(ARCHIVE) as archive:
        descriptor = json.loads(archive.read("datapackage.json"))
        descriptor["resources"] = [r for r in descriptor["resources"]
                                   if f"/{year}/" in r["path"]]
        assert len(descriptor["resources"]) == 4
        for resource in descriptor["resources"]:
            member = Path(resource["path"])
            assert not member.is_absolute() and ".." not in member.parts
            path = target / member
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(archive.read(str(member)))
    path = target / "datapackage.json"
    path.write_text(json.dumps(descriptor))
    return path


def prepare_npi(year, metadata):
    target = WORK / f"{year}-SSP2-NPi"
    target.mkdir(parents=True, exist_ok=True)
    prototype = json.loads((WORK / "2035-SSP2-PkBudg1000/datapackage.json").read_text())
    resources = deepcopy(prototype["resources"])
    labels = json.loads((CACHE / "meta.json").read_text())["scenario_labels"]
    position = labels.index(str(year))
    for resource in resources:
        resource["path"] = resource["path"].replace("SSP2-PkBudg1000", "SSP2-NPi").replace("/2035/", f"/{year}/")
        resource["name"] = resource["name"].replace("2035", str(year))
        path = target / resource["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            continue
        fields = [f["name"] for f in resource["schema"]["fields"]]
        with path.open("w", newline="") as stream:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(fields)
            if resource["name"].endswith("_index"):
                key = "activity_indices" if resource["name"].startswith("a_") else "biosphere_indices"
                for index, row in metadata[key][str(year)].items():
                    writer.writerow([index if f == "index" else row.get(f, "") for f in fields])
            else:
                matrix = CACHE / ("A.npz" if resource["name"].startswith("a_") else "B.npz")
                coordinates = mapped_npy(matrix, "coords.npy")
                values = mapped_npy(matrix, "data.npy")
                mask = coordinates[0] == position
                for row_index, column, value in zip(coordinates[1, mask], coordinates[2, mask], values[mask]):
                    row = {fields[0]: int(row_index), fields[1]: int(column),
                           "value": float(value), "uncertainty type": 0,
                           "loc": float(value), "negative": int(value < 0), "flip": 0}
                    writer.writerow([row.get(f, "") for f in fields])
                print("Reconstructed NPi", year, resource["name"], int(mask.sum()), flush=True)
    prototype.update(resources=resources, scenarios=[], name=f"seoul-npi-{year}-static-cache-extraction")
    path = target / "datapackage.json"
    path.write_text(json.dumps(prototype))
    return path


def compute(package, year, pathway, identities):
    print("Loading", pathway, year, flush=True)
    output = {"year": year, "pathway": pathway,
              "snapshot_resource_sha256": {
                  r["path"]: digest(package.parent / r["path"])
                  for r in json.loads(package.read_text())["resources"]},
              "cases": {}}
    with Trails(Package(str(package)), interpolate_annual=False, ei_version="3.12") as model:
        model.import_excel_inventory([str(FOREGROUND), str(ERW_FG)], year=year)
        meta = model.activity_indices[str(year)]
        identity = lambda m: (m["name"], m.get("reference product"), m.get("location"))
        foreground = {int(i) for i, m in meta.items() if identity(m) in identities}
        native_name = results.static_activity_contributions_per_net_tonne(
            "DACCS", "SSP2-NPi", 2025, "not applicable")[0][0].split(" | ")[0]
        native = [int(i) for i, m in meta.items() if m["name"] == native_name and m.get("location") == "ENC"]
        assert len(native) == 1
        foreground.update(native)
        A, _, _ = _build_direct_technosphere_for_year(model, year)
        B = model.B[int(model._get_scenario_context(year)[2]), :, :].to_scipy_sparse().tocsr()
        methods = [CDR_METHOD, ERW_METHOD]
        factors = [get_cf_matrix(model, [method], {}, ei_version="3.12")[0] for method in methods]
        direct = np.column_stack([np.asarray(B @ cf).ravel() for cf in factors])
        intensities = spsolve(A.T.tocsc(), direct)
        F = np.array(sorted(foreground))
        positions = {int(i): k for k, i in enumerate(F)}
        assert np.allclose(A.diagonal()[F], 1)
        AFF = A[F, :][:, F].tocsc()
        for case, (name, location, method) in CASES.items():
            matches = [int(i) for i, m in meta.items() if m["name"] == name and m.get("location") == location]
            assert len(matches) == 1, (case, matches)
            root = matches[0]
            demand = np.zeros(len(F))
            demand[positions[root]] = 1000
            supply = spsolve(AFF, demand)
            method_index = methods.index(method)
            cf = factors[method_index]
            suppliers, biosphere = [], []
            for parent, amount in zip(F, supply):
                if abs(amount) < 1e-14:
                    continue
                column = A.getcol(parent).tocoo()
                for provider, coefficient in zip(column.row, column.data):
                    if provider in foreground:
                        continue
                    score = float(-coefficient * amount * intensities[provider, method_index])
                    if abs(score) > 1e-12:
                        suppliers.append({"activity": meta[int(provider)]["name"],
                            "reference_product": meta[int(provider)].get("reference product"),
                            "location": meta[int(provider)].get("location"),
                            "foreground_parent": meta[int(parent)]["name"], "score": score})
                flows = B.getrow(parent).tocoo()
                for flow, coefficient in zip(flows.col, flows.data):
                    score = float(coefficient * amount * cf[flow])
                    if abs(score) > 1e-12:
                        biosphere.append({"flow": model.biosphere_indices[str(year)][int(flow)]["name"],
                                          "foreground_activity": meta[int(parent)]["name"], "score": score})
            total = sum(row["score"] for row in suppliers + biosphere)
            model.static_lca(year, root, [method], amount=1000, ei_version="3.12")
            forward = float(np.asarray(model.static_score).sum())
            assert abs(total - forward) < 1e-6, (case, total, forward)
            known = None
            if year == 2050 and case in ("DACCS", "BECCS"):
                known = results.static_score(case, pathway, year, "not applicable" if case == "DACCS"
                    else "new CHP+CCS vs standing forest and Northern European energy")
            elif year == 2050 and case == "ERW" and pathway == "SSP2-PkBudg1000":
                data = json.loads((REPO / "apps/seoul_2026/data/erw_comparison.json").read_text())
                known = next(r["net_kg_co2eq"] for r in data["snapshots"] if r["year"] == year)
            if known is not None:
                assert abs(total - known) < 1e-4, (case, pathway, year, total, known)
            output["cases"][case] = {"total": total, "forward_static_total": forward,
                "existing_source_total": known, "method": method,
                "foreground": biosphere, "suppliers": suppliers}
            print(pathway, year, case, "net", total, "forward error", total - forward,
                  "source error", None if known is None else total - known, flush=True)
    return output


def main():
    bd.projects.set_current("ecoinvent-3.12-cutoff")
    WORK.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((REPO / "apps/setac_2026/data/processed/system_inventory_2025.json").read_text())
    erw = json.loads((REPO / "apps/seoul_2026/data/erw_comparison.json").read_text())
    assert digest(FOREGROUND) == inventory["basis"]["foreground_sha256"]
    assert digest(ERW_FG) == erw["ei312_foreground_sha256"]
    assert digest(ARCHIVE) == erw["package_sha256"]
    identities = set()
    for workbook in (FOREGROUND, ERW_FG):
        importer = ExcelImporter(str(workbook))
        importer.apply_strategies()
        identities.update((d["name"], d.get("reference product"), d.get("location")) for d in importer.data)
    prepare_pk(2035)
    metadata = pickle.load((CACHE / "indices.pkl").open("rb"))
    records = []
    for pathway in ("SSP2-PkBudg1000", "SSP2-NPi"):
        for year in (2035, 2050):
            package = prepare_pk(year) if pathway.endswith("PkBudg1000") else prepare_npi(year, metadata)
            record = compute(package, year, pathway, identities)
            (WORK / f"results-{year}-{pathway}.json").write_text(json.dumps(record, indent=2) + "\n")
            records.append(record)
            gc.collect()
    output = {"schema_version": 1, "calculated_at": datetime.now(timezone.utc).isoformat(),
        "status": "static forward and signed-root reconciliation passed; existing 2050 scores reproduced",
        "scope": "Year-matched static calculations, not interpolation of LCIA scores. Foreground CO2 and complete signed root-supplier contributions. No temporal or climate recalculation.",
        "trails_version": trails.__version__, "trails_source": str(Path(trails.__file__).resolve()),
        "script_sha256": digest(Path(__file__)), "cdr_foreground_sha256": digest(FOREGROUND),
        "erw_foreground_sha256": digest(ERW_FG), "pk_archive_sha256": digest(ARCHIVE),
        "npi_source": "Read-only original SETAC annual interpolation cache; original archive unavailable. 2050 CDR results independently reproduce released source scores.",
        "npi_cache_sha256": {n: digest(CACHE / n) for n in ("meta.json", "indices.pkl", "A.npz", "B.npz")},
        "brightway_project": bd.projects.current, "ecoinvent_version": "3.12", "records": records}
    PUBLIC.write_text(json.dumps(output, indent=2) + "\n")
    print("Wrote", PUBLIC, flush=True)


if __name__ == "__main__":
    main()
