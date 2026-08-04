from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from portal.catalog import resources
from portal.wsgi import application


client = Client(application, Response)


def test_landing_and_health() -> None:
    landing = client.get("/")
    assert landing.status_code == 200
    assert "Premise resources" in landing.text
    assert "/scenarios/" in landing.text
    assert "/workshop/" in landing.text

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json == {
        "status": "ok",
        "services": {
            "landing": "ok",
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
        assert f'{prefix}/_dash-component-suites/' in index.text
        assert client.get(f"{prefix}/_dash-layout").status_code == 200
        assert client.get(f"{prefix}/_dash-dependencies").status_code == 200

    assert client.get("/workshop/assets/styles.css").status_code == 200
    assert client.get("/workshop/assets/psi-mark.svg").status_code == 200


def test_resource_catalog_contract() -> None:
    catalog = resources()
    assert len(catalog) == 8
    assert [item["id"] for item in catalog if item["featured"]] == [
        "scenario-explorer",
        "iam-workshop",
    ]
    assert all(str(item["href"]).startswith("https://") for item in catalog if item["kind"] == "external")

