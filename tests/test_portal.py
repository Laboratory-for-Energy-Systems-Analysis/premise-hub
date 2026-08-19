from __future__ import annotations

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
    assert "Presentations" in landing.text
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
    assert client.get("/missing-page").status_code == 404

    for prefix in ["/scenarios", "/workshop"]:
        index = client.get(f"{prefix}/")
        assert index.status_code == 200
        assert f"{prefix}/_dash-component-suites/" in index.text
        assert client.get(f"{prefix}/_dash-layout").status_code == 200
        assert client.get(f"{prefix}/_dash-dependencies").status_code == 200

    assert client.get("/workshop/assets/styles.css").status_code == 200
    assert client.get("/workshop/assets/psi-mark.svg").status_code == 200
    assert client.get("/scenarios/assets/explorer.css").status_code == 200


def test_resource_catalog_contract() -> None:
    catalog = resources()
    assert len(catalog) == 7
    assert [item["id"] for item in catalog if item["featured"]] == [
        "scenario-explorer",
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
    assert catalog[0]["href"] == "/workshop/"
