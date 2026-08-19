from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
PUBLICATIONS_FILE = ROOT / "publications.yaml"
REQUIRED_FIELDS = {
    "id",
    "title",
    "authors",
    "venue",
    "date",
    "doi",
    "href",
    "topics",
    "kind",
}
VALID_KINDS = {"application", "foundational"}


def _authors_label(authors: list[str]) -> str:
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} & {authors[1]}"
    if len(authors) == 3:
        return f"{authors[0]}, {authors[1]} & {authors[2]}"
    return f"{authors[0]} et al."


@lru_cache(maxsize=1)
def publications() -> list[dict[str, object]]:
    payload = yaml.safe_load(PUBLICATIONS_FILE.read_text(encoding="utf-8")) or []
    if not isinstance(payload, list):
        raise ValueError("The publication catalog must be a list")

    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
    normalized: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Every publication must be a mapping")
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(
                f"Publication {item.get('id', '<unknown>')} misses {sorted(missing)}"
            )

        publication_id = str(item["id"]).strip()
        if not publication_id or publication_id in seen_ids:
            raise ValueError(f"Duplicate or empty publication id: {publication_id}")
        seen_ids.add(publication_id)

        doi = str(item["doi"]).strip().lower()
        if not doi or doi in seen_dois:
            raise ValueError(f"Duplicate or empty publication DOI: {doi}")
        seen_dois.add(doi)

        href = str(item["href"]).strip()
        parsed_href = urlparse(href)
        if parsed_href.scheme != "https" or parsed_href.netloc != "doi.org":
            raise ValueError(
                f"Publication {publication_id} must use an https://doi.org/ link"
            )
        if parsed_href.path.lstrip("/").lower() != doi:
            raise ValueError(
                f"Publication {publication_id} href does not match DOI {doi}"
            )

        kind = str(item["kind"]).strip()
        if kind not in VALID_KINDS:
            raise ValueError(f"Unsupported publication kind: {kind}")

        authors = item["authors"]
        if not isinstance(authors, list) or not authors:
            raise ValueError(f"Publication {publication_id} needs at least one author")
        author_names = [str(author).strip() for author in authors]
        if not all(author_names):
            raise ValueError(f"Publication {publication_id} has an empty author")

        topics = item["topics"]
        if not isinstance(topics, list) or not topics:
            raise ValueError(f"Publication {publication_id} needs at least one topic")
        topic_names = [str(topic).strip() for topic in topics]
        if not all(topic_names):
            raise ValueError(f"Publication {publication_id} has an empty topic")

        raw_date = item["date"]
        try:
            publication_date = (
                raw_date if isinstance(raw_date, date) else date.fromisoformat(str(raw_date))
            )
        except ValueError as error:
            raise ValueError(
                f"Publication {publication_id} has an invalid ISO date: {raw_date}"
            ) from error

        title = str(item["title"]).strip()
        venue = str(item["venue"]).strip()
        if not title or not venue:
            raise ValueError(f"Publication {publication_id} needs a title and venue")

        normalized.append(
            {
                **item,
                "id": publication_id,
                "title": title,
                "authors": author_names,
                "authors_label": _authors_label(author_names),
                "venue": venue,
                "date": publication_date.isoformat(),
                "year": publication_date.year,
                "doi": doi,
                "href": href,
                "topics": topic_names,
                "kind": kind,
                "search_text": " ".join(
                    [title, *author_names, venue, doi, *topic_names]
                ).casefold(),
                "_sort_date": publication_date,
            }
        )

    foundational = [item for item in normalized if item["kind"] == "foundational"]
    if len(foundational) != 1:
        raise ValueError("The publication catalog must contain one foundational paper")

    normalized.sort(key=lambda item: item["_sort_date"], reverse=True)
    for item in normalized:
        item.pop("_sort_date")
    return normalized
