from __future__ import annotations

import csv
import json
import os
from math import isfinite
from pathlib import Path

from ..lca_model.results import ResultBundle, load_result_bundle, file_sha256

RESULT_MANIFEST = (
    Path(__file__).resolve().parents[1] / "data/processed/results_manifest.json"
)
APP_DIR = Path(__file__).resolve().parents[1]
CURRENT_STATIC_DIR = APP_DIR / "generated/results/mtx_uop_current_static"
CURRENT_SENSITIVITY_DIR = APP_DIR / "generated/results/current_static_sensitivity"


def _diagnostic_heat_bundle():
    """Explicit local preview requested by the presenter, never a release approval."""
    from collections import defaultdict
    from ..lca_model.current_sensitivity import validate_grid_payload
    folder = APP_DIR / "generated/results/mtx_gas_heat_current_static"
    background = {"background_evolution": _read_csv(APP_DIR / "generated/results/background_evolution.csv")}
    try:
        manifest = json.loads((folder / "manifest.json").read_text())
        path = folder / "grid.json"
        if not manifest.get("diagnostic_only") or not manifest.get("publication_hold"):
            raise ValueError("Missing diagnostic status")
        if file_sha256(path) != manifest["output_sha256"]:
            raise ValueError("Changed result grid")
        for name, digest in manifest["input_hashes"].items():
            target = (APP_DIR / name).resolve()
            if not target.is_relative_to(APP_DIR.resolve()) or file_sha256(target) != digest:
                raise ValueError(f"Changed calculation input: {name}")
        for check in ("exact_links", "matrix_coefficients", "forward_adjoint_all_roots", "complete_grid_and_contributions"):
            if manifest["checks"].get(check) != "passed":
                raise ValueError(f"Missing check: {check}")
        grid = json.loads(path.read_text())
        validate_grid_payload(grid)
        # Presentation labels only; retain the hashed numerical artifacts unchanged.
        for row in [*grid["baseline_contributions"], *(r for cell in grid["cells"] for r in cell["contributions"])]:
            if row.get("stage") == "synthetic_fuel" and row.get("subprocess") == "heat production, natural gas, at industrial furnace low-NOx >100kW":
                row["subprocess"] = "MTX gas-boiler heat"
        from .carbon_presentation import gross_kiln_transfer_view
        grid["baseline_contributions"] = gross_kiln_transfer_view(grid["baseline_contributions"])
        for cell in grid["cells"]:
            cell["contributions"] = gross_kiln_transfer_view(cell["contributions"])
        grid["presentation_decomposition"] = "gross kiln CO2 plus equal negative captured transfers; net scores unchanged"
        context = {"lens": "current_static", "pathway": "SSP2-NPi", "year": 2025}
        details = tuple({**r, **context} for r in grid["baseline_contributions"])
        sums = defaultdict(float)
        for row in details:
            sums[row["system"], row["stage"]] += float(row["score"])
        totals = tuple({**context, "system": s, "score": v} for s,v in grid["baseline_scores"].items())
        for row in totals:
            if abs(sum(v for (s,_),v in sums.items() if s == row["system"]) - row["score"]) > 1e-5:
                raise ValueError("Baseline contributions do not reconcile")
        return ResultBundle("candidate", "mtx-gas-heat-diagnostic",
            "Diagnostic results • cooling, equipment and carbon-source review pending",
            {"schema_version": "2.0.0", "status": "candidate", "diagnostic_only": True,
             "model_hash": manifest["model_hash"]},
            {**background, "static_totals": totals, "static_subprocesses": details,
             "static_contributions": tuple({**context, "system":s, "stage":stage, "score":v} for (s,stage),v in sums.items())},
            payloads={"current_static_sensitivity": grid})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ResultBundle("invalidated", "diagnostic-preview-invalid", str(exc), {}, background)


def _current_static_candidate_bundle() -> ResultBundle | None:
    """Expose only the newly recalculated lens, with no legacy climate tables."""
    from ..lca_model.scientific_review import publication_hold
    hold = publication_hold()
    if hold:
        return ResultBundle("invalidated", "carbon-audit-hold", hold, {"schema_version": "2.0.0"}, {
            "background_evolution": _read_csv(APP_DIR / "generated/results/background_evolution.csv")
        })
    path = CURRENT_STATIC_DIR / "current_static_run.json"
    if not path.is_file():
        return None
    background = {
        "background_evolution": _read_csv(
            APP_DIR / "generated/results/background_evolution.csv"
        )
    }
    try:
        from ..lca_model.pipeline import (
            METHOD,
            require_inventory_status,
            validate_static_contribution_reconciliation,
        )

        run = json.loads(path.read_text(encoding="utf-8"))
        if (
            run.get("checks", {}).get("duplicate_coordinates")
            != "rejected by explicit-year importer"
        ):
            raise ValueError(
                "Current-static import lacks duplicate-coordinate protection"
            )
        if (
            run["reference_year"] != 2025
            or run["reference_package_pathway"] != "SSP2-NPi"
            or run["method"] != METHOD
        ):
            raise ValueError("Unexpected current-static year, pathway or method")
        inventory = Path(run["inventory"])
        manifest = Path(run["inventory_manifest"])
        for file, key in (
            (inventory, "inventory_sha256"),
            (manifest, "inventory_manifest_sha256"),
            (APP_DIR / "data/model_contract.json", "model_contract_sha256"),
            (
                APP_DIR / "data/assumptions/methanol_to_jet.json",
                "fuel_assumption_sha256",
            ),
        ):
            if file_sha256(file) != run[key]:
                raise ValueError(f"Stale current-static input: {key}")
        meta = require_inventory_status(inventory, manifest, allow_candidate=True)
        if meta["model_hash"] != run["model_hash"]:
            raise ValueError("Current-static model hash mismatch")
        tables = dict(background)
        for table, name, hash_key in (
            ("static_totals", "output", "output_sha256"),
            ("static_contributions", "contributions", "contributions_sha256"),
        ):
            artifact = CURRENT_STATIC_DIR / run[name]
            if (
                artifact.parent.resolve() != CURRENT_STATIC_DIR.resolve()
                or file_sha256(artifact) != run[hash_key]
            ):
                raise ValueError(f"Invalid current-static artifact: {table}")
            tables[table] = _read_csv(artifact)
            for row in tables[table]:
                if (
                    row.get("lens") != "current_static"
                    or row.get("pathway") != "SSP2-NPi"
                    or row.get("year") != "2025"
                    or row.get("system") not in {"BAU", "CCS", "CCUS"}
                    or row.get("model_hash") != run["model_hash"]
                    or row.get("run_id") != run["run_id"]
                    or not isfinite(float(row["score"]))
                ):
                    raise ValueError("Inconsistent current-static result row")
        if len(tables["static_totals"]) != 3 or {
            r["system"] for r in tables["static_totals"]
        } != {"BAU", "CCS", "CCUS"}:
            raise ValueError("Current-static comparison is incomplete")
        validate_static_contribution_reconciliation(
            tables["static_totals"], tables["static_contributions"]
        )
        detail_manifest = CURRENT_STATIC_DIR / "static_subprocesses_run.json"
        if detail_manifest.is_file():
            from ..lca_model.subprocesses import validate_subprocesses

            detail = json.loads(detail_manifest.read_text())
            detail_path = CURRENT_STATIC_DIR / detail["output"]
            if (
                detail["parent_run_sha256"] != file_sha256(path)
                or detail_path.parent.resolve() != CURRENT_STATIC_DIR.resolve()
                or detail["output_sha256"] != file_sha256(detail_path)
            ):
                raise ValueError("Stale or altered sub-process breakdown")
            detail_rows = _read_csv(detail_path)
            if any(
                r["run_id"] != run["run_id"]
                or r["model_hash"] != run["model_hash"]
                or r["lens"] != "current_static"
                or r["pathway"] != "SSP2-NPi"
                or r["year"] != "2025"
                for r in detail_rows
            ):
                raise ValueError("Sub-process provenance mismatch")
            validate_subprocesses(detail_rows, tables["static_contributions"])
            tables["static_subprocesses"] = detail_rows
        payloads = {}
        sensitivity_manifest = CURRENT_SENSITIVITY_DIR / "manifest.json"
        if sensitivity_manifest.is_file():
            from ..lca_model.current_sensitivity import validate_grid_payload

            sensitivity = json.loads(sensitivity_manifest.read_text())
            result_path = CURRENT_SENSITIVITY_DIR / sensitivity["output"]
            if (
                sensitivity["status"] != "candidate"
                or result_path.parent.resolve() != CURRENT_SENSITIVITY_DIR.resolve()
                or sensitivity["parent_run_sha256"] != file_sha256(path)
                or sensitivity["model_hash"] != run["model_hash"]
                or sensitivity["package_sha256"] != run["package_sha256"]
                or sensitivity["output_sha256"] != file_sha256(result_path)
                or sensitivity["combinations"] != 55
                or sensitivity["scenario_scores"] != 165
                or not 0 <= sensitivity.get("max_contribution_rescaling", 1) <= 1e-4
            ):
                raise ValueError("Stale or incomplete current-static sensitivity grid")
            expected_hashes = {
                "data/current_static_sensitivity_contract.json": APP_DIR
                / "data/current_static_sensitivity_contract.json",
                "data/mappings/provider_crosswalk.csv": APP_DIR
                / "data/mappings/provider_crosswalk.csv",
                "generated/extracted/scenarios.csv": APP_DIR
                / "generated/extracted/scenarios.csv",
                "data/assumptions/non_fossil_uptake_profiles.json": APP_DIR
                / "data/assumptions/non_fossil_uptake_profiles.json",
                "lca_model/current_sensitivity.py": APP_DIR
                / "lca_model/current_sensitivity.py",
                "lca_model/sensitivity.py": APP_DIR / "lca_model/sensitivity.py",
                "dev/precompute_current_sensitivity.py": APP_DIR
                / "dev/precompute_current_sensitivity.py",
            }
            if set(sensitivity["input_hashes"]) != set(expected_hashes) or any(
                sensitivity["input_hashes"][key] != file_sha256(value)
                for key, value in expected_hashes.items()
            ):
                raise ValueError("Current-static sensitivity inputs changed")
            if not all(value == "passed" for key, value in sensitivity["checks"].items()
                       if key not in {"trails_static_checks", "contribution_root_normalization"}):
                raise ValueError("Current-static sensitivity validation failed")
            grid = json.loads(result_path.read_text())
            if (
                grid["year"] != 2025
                or grid["pathway"] != "SSP2-NPi"
                or grid["method"] != METHOD
                or grid["unit"] != "kg CO2-eq/t clinker"
            ):
                raise ValueError("Unexpected current-static sensitivity scope")
            validate_grid_payload(grid)
            payloads["current_static_sensitivity"] = grid
        carbon_manifest = CURRENT_STATIC_DIR / "static_carbon_balance_run.json"
        if carbon_manifest.is_file():
            from ..lca_model.carbon_balance import validate_carbon_balance

            carbon_meta = json.loads(carbon_manifest.read_text())
            carbon_path = CURRENT_STATIC_DIR / carbon_meta["output"]
            if (carbon_path.parent.resolve() != CURRENT_STATIC_DIR.resolve()
                or carbon_meta["parent_run_sha256"] != file_sha256(path)
                or carbon_meta["output_sha256"] != file_sha256(carbon_path)):
                raise ValueError("Stale or altered carbon balance")
            carbon = json.loads(carbon_path.read_text())
            if (any(carbon[k] != run[k] for k in ("run_id", "model_hash", "inventory_sha256"))
                or carbon["parent_run_sha256"] != file_sha256(path)):
                raise ValueError("Carbon-balance provenance mismatch")
            validate_carbon_balance(carbon)
            payloads["static_carbon_balance"] = carbon
        return ResultBundle(
            "candidate",
            run["run_id"],
            "Recalculated 2025 · provisional co-product and energy assumptions; public-SI foreground reconciliation pending",
            run,
            tables,
            payloads=payloads,
        )
    except (OSError, ValueError, KeyError, AssertionError, SystemExit) as exc:
        return ResultBundle(
            "invalid", "current-static-candidate", str(exc), {}, background
        )


def _read_csv(path: Path) -> tuple[dict, ...]:
    if not path.is_file():
        return ()
    with path.open(newline="", encoding="utf-8") as stream:
        return tuple(csv.DictReader(stream))


def _development_bundle() -> ResultBundle | None:
    """Load visibly provisional local calculation outputs when explicitly enabled.

    This path is for presenter development only. Deployment continues to load
    exclusively from the reviewed, hash-checked processed manifest.
    """

    if os.getenv("CCUS_WEBINAR_SHOW_CANDIDATE_RESULTS") != "1":
        return None
    if os.getenv("CCUS_WEBINAR_DIAGNOSTIC_PREVIEW") == "mtx-gas-heat":
        from .temporal_results import attach_temporal_preview
        from .fair_results import attach_fair_preview
        from .pulse_results import attach_pulse_preview
        return attach_pulse_preview(attach_fair_preview(attach_temporal_preview(_diagnostic_heat_bundle())))
    current = _current_static_candidate_bundle()
    if current is not None:
        return current
    root = APP_DIR / "generated/results"
    inventory_manifest = (
        APP_DIR / "generated/inventories/inventory_manifest_reviewed.json"
    )
    if not inventory_manifest.is_file():
        return None
    inventory_meta = json.loads(inventory_manifest.read_text(encoding="utf-8"))
    if inventory_meta.get("model_contract_sha256") != file_sha256(
        APP_DIR / "data/model_contract.json"
    ) or inventory_meta.get("fuel_assumption_sha256") != file_sha256(
        APP_DIR / "data/assumptions/methanol_to_jet.json"
    ):
        return ResultBundle(
            "stale",
            "previous-single-output-results",
            "Methanol-to-X now includes diesel and naphtha. Previous climate results are withdrawn until the revised inventory is completed and recalculated.",
            {
                "status": "stale",
                "workflow": [
                    {
                        "step": "Multi-output recalculation",
                        "status": "pending",
                        "detail": "Resolve co-product use, residual carbon and process energy before release",
                    }
                ],
            },
            {"background_evolution": _read_csv(root / "background_evolution.csv")},
        )
    current_model_hash = str(inventory_meta.get("model_hash", ""))
    if not current_model_hash:
        return None
    table_files = {
        "system_flows": "system_flows.csv",
        "background_evolution": "background_evolution.csv",
        "static_totals": "static_totals.csv",
        "static_contributions": "static_contributions.csv",
        "temporal_totals": "temporal_totals.csv",
        "temporal_contributions": "temporal_contributions.csv",
        "fair_responses": "fair_responses.csv",
        "pulse_equivalence": "pulse_equivalence.csv",
        "rankings": "rankings.csv",
        "sensitivity_availability": "sensitivity_availability.csv",
        "sensitivity_results": "sensitivity_results.csv",
    }
    tables = {
        name: _read_csv(root / filename) for name, filename in table_files.items()
    }
    # Transitional aliases are accepted only in this explicitly enabled local mode.
    tables["static_totals"] = tables["static_totals"] or _read_csv(
        root / "static_results.csv"
    )
    tables["temporal_totals"] = tables["temporal_totals"] or _read_csv(
        root / "annual_results.csv"
    )
    tables["fair_responses"] = tables["fair_responses"] or _read_csv(
        root / "climate_results.csv"
    )
    legacy_contributions = _read_csv(root / "contributions.csv")
    tables["static_contributions"] = (
        tables["static_contributions"] or legacy_contributions
    )
    tables["temporal_contributions"] = (
        tables["temporal_contributions"] or legacy_contributions
    )
    # Local work often contains artifacts from earlier model revisions. Never
    # combine these with the current foreground, even in candidate mode.
    tables = {
        name: tuple(
            row
            for row in rows
            if not row.get("model_hash") or row.get("model_hash") == current_model_hash
        )
        for name, rows in tables.items()
    }
    if not any(tables.values()):
        return None
    hashes = {
        row.get("model_hash", "")
        for rows in tables.values()
        for row in rows
        if row.get("model_hash")
    }
    message = "Provisional TRAILS calculation · routing convergence and scientific approval pending"
    if len(hashes) > 1:
        message = "Provisional result files use inconsistent model hashes"
    return ResultBundle(
        status="candidate",
        bundle_id="local-trails-development",
        message=message,
        manifest={
            "schema_version": "2.0.0",
            "status": "candidate",
            "model_hash": current_model_hash,
            "workflow": [
                {
                    "step": "TRAILS calculations",
                    "status": "pending",
                    "detail": "Local provisional outputs; not a release bundle",
                }
            ],
        },
        tables=tables,
    )


from .release import load_release_bundle

RESULT_BUNDLE: ResultBundle = load_release_bundle() or ResultBundle(
    'stale', 'public-release-missing', 'The public result bundle is unavailable.', {}, {}
)


def result_status_label(bundle: ResultBundle = RESULT_BUNDLE) -> str:
    labels = {
        "approved": "Recalculated · reviewed",
        "not_calculated": "Calculation pending",
        "candidate": "Candidate · not reviewed",
        "invalid": "Result bundle invalid",
        "invalidated": "Results withdrawn · carbon audit",
        "stale": "Result bundle stale",
        "contract_migrated_recalculation_required": "Recalculation required",
    }
    return labels.get(bundle.status, bundle.status.replace("_", " ").title())
