from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
CATALOG_FILE = ROOT / "resources.yaml"
REQUIRED_FIELDS = {
    "id",
    "title",
    "summary",
    "href",
    "category",
    "kind",
    "featured",
}


@lru_cache(maxsize=1)
def resources() -> list[dict[str, object]]:
    payload = yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8")) or []
    if not isinstance(payload, list):
        raise ValueError("The resource catalog must be a list")
    seen: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Every resource must be a mapping")
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"Resource {item.get('id', '<unknown>')} misses {sorted(missing)}")
        resource_id = str(item["id"])
        if resource_id in seen:
            raise ValueError(f"Duplicate resource id: {resource_id}")
        seen.add(resource_id)
        kind = str(item["kind"])
        href = str(item["href"])
        if kind not in {"hosted", "external"}:
            raise ValueError(f"Unsupported resource kind: {kind}")
        if kind == "hosted" and not href.startswith("/"):
            raise ValueError(f"Hosted resource must use an absolute local path: {href}")
        if kind == "external" and urlparse(href).scheme != "https":
            raise ValueError(f"External resource must use HTTPS: {href}")
    return payload
