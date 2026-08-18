from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
ECOSYSTEM_FILE = ROOT / "ecosystem.yaml"

REQUIRED_COLLECTIONS = {
    "stages",
    "groups",
    "statuses",
    "relationship_types",
    "tools",
    "relationships",
}
REQUIRED_TOOL_FIELDS = {
    "id",
    "name",
    "summary",
    "description",
    "stage",
    "group",
    "status",
    "order",
    "links",
    "tags",
}
REQUIRED_RELATIONSHIP_FIELDS = {"source", "target", "type", "summary"}


def _collection_ids(payload: dict[str, object], field: str) -> set[str]:
    collection = payload[field]
    if not isinstance(collection, list) or not collection:
        raise ValueError(f"Ecosystem {field} must be a non-empty list")
    ids: set[str] = set()
    for item in collection:
        if not isinstance(item, dict) or not item.get("id") or not item.get("label"):
            raise ValueError(f"Every ecosystem {field} entry needs an id and label")
        item_id = str(item["id"])
        if item_id in ids:
            raise ValueError(f"Duplicate ecosystem {field} id: {item_id}")
        ids.add(item_id)
    return ids


def _validate_url(url: object, context: str) -> None:
    parsed = urlparse(str(url))
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{context} must be an absolute HTTPS URL: {url}")


def validate_ecosystem(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("The ecosystem catalog must be a mapping")

    missing_collections = REQUIRED_COLLECTIONS - set(payload)
    if missing_collections:
        raise ValueError(f"The ecosystem catalog misses {sorted(missing_collections)}")

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict) or not metadata.get("verified_on"):
        raise ValueError("Ecosystem metadata must include verified_on")

    stage_ids = _collection_ids(payload, "stages")
    group_ids = _collection_ids(payload, "groups")
    status_ids = _collection_ids(payload, "statuses")
    relationship_type_ids = _collection_ids(payload, "relationship_types")

    tools = payload["tools"]
    if not isinstance(tools, list) or not tools:
        raise ValueError("Ecosystem tools must be a non-empty list")

    tool_ids: set[str] = set()
    for tool in tools:
        if not isinstance(tool, dict):
            raise ValueError("Every ecosystem tool must be a mapping")
        missing = REQUIRED_TOOL_FIELDS - set(tool)
        if missing:
            raise ValueError(
                f"Ecosystem tool {tool.get('id', '<unknown>')} misses {sorted(missing)}"
            )
        tool_id = str(tool["id"])
        if tool_id in tool_ids:
            raise ValueError(f"Duplicate ecosystem tool id: {tool_id}")
        tool_ids.add(tool_id)
        if tool["stage"] not in stage_ids:
            raise ValueError(f"Unknown stage for {tool_id}: {tool['stage']}")
        if tool["group"] not in group_ids:
            raise ValueError(f"Unknown group for {tool_id}: {tool['group']}")
        if tool["status"] not in status_ids:
            raise ValueError(f"Unknown status for {tool_id}: {tool['status']}")
        if not isinstance(tool["order"], int):
            raise ValueError(f"Tool order must be an integer for {tool_id}")
        if not isinstance(tool["tags"], list) or not tool["tags"]:
            raise ValueError(f"Tool tags must be a non-empty list for {tool_id}")
        links = tool["links"]
        if not isinstance(links, dict) or "source" not in links:
            raise ValueError(f"Tool links must include source for {tool_id}")
        for label, url in links.items():
            _validate_url(url, f"{tool_id} {label} link")

    relationships = payload["relationships"]
    if not isinstance(relationships, list):
        raise ValueError("Ecosystem relationships must be a list")
    seen_relationships: set[tuple[str, str, str]] = set()
    for relationship in relationships:
        if not isinstance(relationship, dict):
            raise ValueError("Every ecosystem relationship must be a mapping")
        missing = REQUIRED_RELATIONSHIP_FIELDS - set(relationship)
        if missing:
            raise ValueError(f"Ecosystem relationship misses {sorted(missing)}")
        source = str(relationship["source"])
        target = str(relationship["target"])
        relationship_type = str(relationship["type"])
        if source not in tool_ids or target not in tool_ids:
            raise ValueError(f"Relationship endpoint is unknown: {source} -> {target}")
        if source == target:
            raise ValueError(f"Self-referential ecosystem relationship: {source}")
        if relationship_type not in relationship_type_ids:
            raise ValueError(
                f"Unknown relationship type {relationship_type}: {source} -> {target}"
            )
        key = (source, target, relationship_type)
        if key in seen_relationships:
            raise ValueError(f"Duplicate ecosystem relationship: {key}")
        seen_relationships.add(key)

    return payload


@lru_cache(maxsize=1)
def ecosystem() -> dict[str, object]:
    payload = yaml.safe_load(ECOSYSTEM_FILE.read_text(encoding="utf-8")) or {}
    return validate_ecosystem(payload)
