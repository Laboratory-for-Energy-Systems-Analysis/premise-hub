from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
PRESENTATIONS_FILE = ROOT / "presentations.yaml"
REQUIRED_FIELDS = {"id", "title", "summary", "date", "href", "kind"}


@lru_cache(maxsize=1)
def presentations() -> list[dict[str, object]]:
    payload = yaml.safe_load(PRESENTATIONS_FILE.read_text(encoding="utf-8")) or []
    if not isinstance(payload, list):
        raise ValueError("The presentation catalog must be a list")

    seen: set[str] = set()
    normalized: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Every presentation must be a mapping")
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(
                f"Presentation {item.get('id', '<unknown>')} misses {sorted(missing)}"
            )

        presentation_id = str(item["id"])
        if presentation_id in seen:
            raise ValueError(f"Duplicate presentation id: {presentation_id}")
        seen.add(presentation_id)

        kind = str(item["kind"])
        href = str(item["href"])
        if kind not in {"hosted", "external"}:
            raise ValueError(f"Unsupported presentation kind: {kind}")
        if kind == "hosted" and not href.startswith("/"):
            raise ValueError(f"Hosted presentation must use a local path: {href}")
        if kind == "external" and urlparse(href).scheme != "https":
            raise ValueError(f"External presentation must use HTTPS: {href}")

        raw_date = item["date"]
        try:
            presentation_date = (
                raw_date
                if isinstance(raw_date, date)
                else date.fromisoformat(str(raw_date))
            )
        except ValueError as error:
            raise ValueError(
                f"Presentation {presentation_id} has an invalid ISO date: {raw_date}"
            ) from error

        normalized.append(
            {
                **item,
                "id": presentation_id,
                "href": href,
                "kind": kind,
                "date": presentation_date.isoformat(),
                "date_label": (
                    f"{presentation_date.day} " f"{presentation_date.strftime('%B %Y')}"
                ),
                "day": presentation_date.strftime("%d"),
                "month": presentation_date.strftime("%b"),
                "year": presentation_date.strftime("%Y"),
                "_sort_date": presentation_date,
            }
        )

    normalized.sort(key=lambda item: item["_sort_date"], reverse=True)
    for item in normalized:
        item.pop("_sort_date")
    return normalized
