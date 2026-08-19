from __future__ import annotations

from pathlib import Path

from werkzeug.test import Client
from werkzeug.wrappers import Response

from portal.catalog import resources
from portal.presentations import presentations
from portal.wsgi import application

client = Client(application, Response)


def test_landing_and_health() -> None:
    landing = client.get("/")
    assert landing.status_code == 200
    assert "Premise resources" in landing.text
    assert "/scenarios/" in landing.text
    assert "/workshop/" in landing.text
    assert "/ecosystem/" in landing.text
    assert 'rel="icon" href="/static/favicon.ico"' in landing.text
    assert "Presentations" in landing.text
    assert "IAM scenarios workshop" in landing.text
    assert "Interactive Brightway ecosystem" in landing.text
    assert "ecosystem-map-link" not in landing.text
    assert landing.text.count('href="/ecosystem/"') == 1
    assert 'datetime="2026-09-03"' in landing.text
    assert "3 September 2026" in landing.text

    styles = client.get("/static/styles.css")
    assert styles.status_code == 200
    assert ".presentations-list" in styles.text
    assert "overflow-y: auto" in styles.text

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json == {
        "status": "ok",
        "services": {
            "landing": "ok",
            "ecosystem": "ok",
            "scenarios": "ok",
            "workshop": "ok",
        },
    }


def test_public_routes_and_prefixes() -> None:
    assert client.get("/dashboard").status_code == 308
    assert client.get("/dashboard").headers["Location"].endswith("/scenarios/")
    assert client.get("/robots.txt").status_code == 200
    missing = client.get("/missing-page")
    assert missing.status_code == 404
    assert 'rel="icon" href="/static/favicon.ico"' in missing.text

    ecosystem_page = client.get("/ecosystem/")
    assert ecosystem_page.status_code == 200
    assert 'rel="icon" href="/static/favicon.ico"' in ecosystem_page.text

    favicon = client.get("/static/favicon.ico")
    assert favicon.status_code == 200
    assert favicon.data.startswith(b"\x00\x00\x01\x00")

    for prefix in ["/scenarios", "/workshop"]:
        index = client.get(f"{prefix}/")
        assert index.status_code == 200
        assert f"{prefix}/_dash-component-suites/" in index.text
        assert f"{prefix}/assets/favicon.ico" in index.text
        assert client.get(f"{prefix}/_dash-layout").status_code == 200
        assert client.get(f"{prefix}/_dash-dependencies").status_code == 200

    assert client.get("/workshop/assets/styles.css").status_code == 200
    assert client.get("/workshop/assets/psi-mark.svg").status_code == 200
    assert client.get("/scenarios/assets/explorer.css").status_code == 200


def test_resource_catalog_contract() -> None:
    catalog = resources()
    assert len(catalog) == 8
    assert [item["id"] for item in catalog if item["featured"]] == [
        "scenario-explorer",
        "interactive-ecosystem",
    ]
    assert all(
        str(item["href"]).startswith("https://")
        for item in catalog
        if item["kind"] == "external"
    )


def test_presentation_catalog_contract() -> None:
    catalog = presentations()
    assert [item["id"] for item in catalog] == ["iam-workshop-2026-09-03"]
    assert catalog[0]["date"] == "2026-09-03"
    assert catalog[0]["date_label"] == "3 September 2026"
    assert catalog[0]["title"] == "IAM scenarios workshop"
    assert catalog[0]["href"] == "/workshop/"


def test_all_apps_use_the_same_premise_favicon() -> None:
    root = Path(__file__).resolve().parents[1]
    favicon_paths = [
        root / "portal/static/favicon.ico",
        root / "apps/scenario_explorer/assets/favicon.ico",
        root / "apps/workshop/assets/favicon.ico",
    ]
    assert all(path.is_file() for path in favicon_paths)
    assert len({path.read_bytes() for path in favicon_paths}) == 1
