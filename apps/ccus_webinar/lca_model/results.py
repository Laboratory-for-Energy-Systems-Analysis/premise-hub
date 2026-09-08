from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import csv
import json
from pathlib import Path
from typing import Any

APPROVED = "approved"
SCHEMA_MAJOR = 2
REQUIRED_GATES = {
    "physical_carbon_routing",
    "terminal_carbon_fates",
    "hydrogen_balance",
    "heat_balance",
    "background_carbon_interfaces",
    "source_hash",
    "extraction_integrity",
    "model_contract",
    "inventory_reconciliation",
    "carbon_balance",
    "temporal_profiles",
    "brightway_import",
    "exact_linking",
    "scenario_coverage",
    "static_reconciliation",
    "trails_convergence",
    "fair_species",
    "pulse_equivalence",
    "sensitivity_grid",
}
REQUIRED_TABLES = {
    "system_flows",
    "background_evolution",
    "static_totals",
    "static_contributions",
    "temporal_totals",
    "temporal_contributions",
    "fair_responses",
    "pulse_equivalence",
    "rankings",
    "sensitivity_availability",
    "sensitivity_results",
}


@dataclass(frozen=True)
class ResultBundle:
    """Immutable, runtime-safe collection of approved presentation artifacts."""

    status: str
    bundle_id: str
    message: str
    manifest: dict
    tables: dict[str, tuple[dict, ...]]
    payloads: dict[str, Any] = field(default_factory=dict)
    arrays: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def approved(self) -> bool:
        return self.status == APPROVED


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_artifact(path: Path, artifact_format: str | None = None):
    artifact_format = (artifact_format or path.suffix.lstrip(".")).lower()
    if artifact_format == "csv":
        with path.open(newline="", encoding="utf-8") as stream:
            return "table", tuple(csv.DictReader(stream))
    if artifact_format == "json":
        return "payload", json.loads(path.read_text(encoding="utf-8"))
    if artifact_format == "npz":
        import numpy as np

        with np.load(path, allow_pickle=False) as archive:
            return "array", {name: archive[name] for name in archive.files}
    raise ValueError(f"Unsupported runtime result format: {path.name}")


def _rejected(
    status: str, bundle_id: str, message: str, manifest: dict
) -> ResultBundle:
    return ResultBundle(status, bundle_id, message, manifest, {})


def load_result_bundle(path: str | Path) -> ResultBundle:
    """Load an approved v2 bundle only after every scientific gate and hash passes.

    The Dash runtime never imports Brightway, premise, TRAILS, or FaIR. It reads
    only small, reviewed artifacts; unapproved bundles expose no scores.
    """

    from .scientific_review import publication_hold
    hold = publication_hold()
    if hold:
        return _rejected("invalidated", "carbon-audit-hold", hold, {"schema_version": "2.0.0"})
    manifest_path = Path(path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    status = str(manifest.get("status", "invalid"))
    bundle_id = str(manifest.get("bundle_id", "unknown"))
    if status != APPROVED:
        return _rejected(
            status,
            bundle_id,
            manifest.get("review", {}).get("note")
            or "The redesigned 2025/2035 result bundle is not approved.",
            manifest,
        )

    try:
        schema_major = int(str(manifest.get("schema_version", "0")).split(".")[0])
    except ValueError:
        schema_major = 0
    if schema_major != SCHEMA_MAJOR:
        return _rejected("invalid", bundle_id, "Unsupported result schema", manifest)

    gates = manifest.get("gates", {})
    if set(gates) != REQUIRED_GATES:
        return _rejected(
            "invalid",
            bundle_id,
            "Approval manifest has an incomplete gate set",
            manifest,
        )
    failed_gates = [name for name, passed in gates.items() if passed is not True]
    if failed_gates:
        return _rejected(
            "invalid",
            bundle_id,
            f"Approval manifest has failed gates: {', '.join(failed_gates)}",
            manifest,
        )

    review = manifest.get("review", {})
    if not all(review.get(key) for key in ("reviewer", "reviewed_at", "note")):
        return _rejected(
            "invalid",
            bundle_id,
            "Approval manifest has no complete review record",
            manifest,
        )

    contract = manifest.get("model_contract", {})
    contract_path_value = contract.get("path")
    expected_contract_hash = contract.get("sha256")
    if not contract_path_value or not expected_contract_hash:
        return _rejected(
            "invalid", bundle_id, "Approved bundle has no model-contract hash", manifest
        )
    contract_path = Path(contract_path_value)
    if contract_path.is_absolute() or ".." in contract_path.parts:
        return _rejected("invalid", bundle_id, "Unsafe model-contract path", manifest)
    resolved_contract = manifest_path.parent / contract_path
    if (
        not resolved_contract.is_file()
        or file_sha256(resolved_contract) != expected_contract_hash
    ):
        return _rejected(
            "stale", bundle_id, "Model contract changed after calculation", manifest
        )

    model_hash = str(manifest.get("model_hash", ""))
    if not model_hash:
        return _rejected(
            "invalid", bundle_id, "Approved bundle has no model hash", manifest
        )

    tables: dict[str, tuple[dict, ...]] = {}
    payloads: dict[str, Any] = {}
    arrays: dict[str, dict[str, Any]] = {}
    for item in manifest.get("files", []):
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            return _rejected("invalid", bundle_id, "Unsafe result path", manifest)
        file_path = manifest_path.parent / relative
        if not file_path.is_file():
            return _rejected("stale", bundle_id, f"Missing {relative}", manifest)
        if file_sha256(file_path) != item.get("sha256"):
            return _rejected(
                "stale", bundle_id, f"Hash mismatch for {relative}", manifest
            )
        try:
            kind, artifact = _read_artifact(file_path, item.get("format"))
        except (ValueError, json.JSONDecodeError) as exc:
            return _rejected("invalid", bundle_id, str(exc), manifest)
        name = item.get("table") or item.get("name") or file_path.stem
        if kind == "table":
            tables[name] = artifact
        elif kind == "payload":
            payloads[name] = artifact
        else:
            arrays[name] = artifact

    if not REQUIRED_TABLES <= set(tables):
        missing = ", ".join(sorted(REQUIRED_TABLES - set(tables)))
        return _rejected(
            "invalid",
            bundle_id,
            f"Approved result tables are incomplete: {missing}",
            manifest,
        )
    for table_name in REQUIRED_TABLES:
        rows = tables[table_name]
        if not rows:
            return _rejected("invalid", bundle_id, f"{table_name} is empty", manifest)
        for row in rows:
            if (
                row.get("evidence_status") != "recalculated"
                or row.get("model_hash") != model_hash
            ):
                return _rejected(
                    "invalid",
                    bundle_id,
                    f"{table_name} does not match the approved evidence contract",
                    manifest,
                )
    return ResultBundle(
        APPROVED,
        bundle_id,
        "Approved recalculated 2025/2035 results",
        manifest,
        tables,
        payloads,
        arrays,
    )
