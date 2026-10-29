"""Presenter-requested unit conversion, separate from the immutable source study."""

from functools import lru_cache
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASIS_SHA256 = "48ad8c54ea95d20d833ef8eb2f1fa4384ae653cbb0b6dd8ca9a69d3a1c83d3d9"


@lru_cache(maxsize=1)
def storage_basis():
    raw = (ROOT / "data/cement_storage_basis.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASIS_SHA256:
        raise ValueError("Cement storage normalization changed; recheck its provenance")
    data = json.loads(raw)
    from apps.ccus_webinar.webinar.release import release_manifest

    release = release_manifest()
    if data["source_bundle_id"] != release["bundle_id"]:
        raise ValueError("Cement normalization and reviewed source differ")
    for key, digest in data["source_public_bundle_sha256"].items():
        if release["bundles"][key]["sha256"] != digest:
            raise ValueError("Cement results and normalization differ: " + key)
    return data


def cement_scale(year=None):
    """Tonnes associated clinker per stored tonne; None means the full campaign."""
    data = storage_basis()
    return (
        data["campaign_clinker_t_per_t_stored"]
        if year is None
        else data["static_clinker_t_per_t_stored"][str(year)]
    )
