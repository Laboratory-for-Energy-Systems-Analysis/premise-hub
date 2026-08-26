from __future__ import annotations

from pathlib import Path

from PIL import Image
from werkzeug.test import Client
from werkzeug.wrappers import Response

from portal.catalog import resources
from portal.presentations import presentations
from portal.publications import publications
from portal.wsgi import application
from apps.lca_time.workshop.config import (
    APPENDIX_SLIDE_COUNT,
    CORE_SLIDE_COUNT,
    LAST_SLIDE,
)
from apps.lca_time.workshop.slides import render_slide

client = Client(application, Response)


def unlock_presentation(test_client: Client, prefix: str, password: str) -> None:
    response = test_client.post(
        f"{prefix}/", data={"password": password}, follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["Location"] == f"{prefix}/"


def test_landing_and_health() -> None:
    landing = client.get("/")
    publication_count = sum(item["kind"] == "application" for item in publications())
    assert landing.status_code == 200
    assert "Premise resources" in landing.text
    assert "/scenarios/" in landing.text
    assert "/workshop/" in landing.text
    assert "/lca-time/" in landing.text
    assert "/ecosystem/" in landing.text
    assert 'rel="icon" href="/static/favicon.ico"' in landing.text
    assert "/static/premise-logo-transparent.png" in landing.text
    assert "premise-logo.png" not in landing.text
    assert "Presentations" in landing.text
    assert "IAM scenarios workshop" in landing.text
    assert "LCA through time" in landing.text
    assert "Interactive Brightway ecosystem" in landing.text
    assert "Research using Premise" in landing.text
    assert f"{publication_count} verified publications" in landing.text
    assert (
        "Recycling fossil infrastructure for cleaner energy transitions" in landing.text
    )
    assert "Large-scale hydrogen production via water electrolysis" in landing.text
    assert landing.text.count("data-publication-item") == publication_count
    assert "/static/publications.js" in landing.text
    assert "ecosystem-map-link" not in landing.text
    assert landing.text.count('href="/ecosystem/"') == 1
    assert 'datetime="2026-09-03"' in landing.text
    assert "3 September 2026" in landing.text
    assert 'datetime="2026-08-27"' in landing.text
    assert "27 August 2026" in landing.text

    styles = client.get("/static/styles.css")
    assert styles.status_code == 200
    assert ".presentations-list" in styles.text
    assert ".publications-list" in styles.text
    assert "overflow-y: auto" in styles.text

    publication_script = client.get("/static/publications.js")
    assert publication_script.status_code == 200
    assert "applyFilters" in publication_script.text

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json == {
        "status": "ok",
        "services": {
            "landing": "ok",
            "ecosystem": "ok",
            "lca_time": "ok",
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

    premise_logo = client.get("/static/premise-logo-transparent.png")
    assert premise_logo.status_code == 200
    assert premise_logo.data.startswith(b"\x89PNG\r\n\x1a\n")

    protected = client.get("/workshop/")
    assert protected.status_code == 401
    assert "Protected presentation" in protected.text
    assert "Enter the password to continue." in protected.text
    assert "event date" not in protected.text.casefold()
    assert "DDMMYYYY" not in protected.text

    unlock_presentation(client, "/workshop", "03092026")

    for prefix in ["/scenarios", "/workshop", "/lca-time"]:
        index = client.get(f"{prefix}/")
        assert index.status_code == 200
        assert f"{prefix}/_dash-component-suites/" in index.text
        assert f"{prefix}/assets/favicon.ico" in index.text
        assert client.get(f"{prefix}/_dash-layout").status_code == 200
        assert client.get(f"{prefix}/_dash-dependencies").status_code == 200

    assert client.get("/workshop/assets/styles.css").status_code == 200
    assert client.get("/workshop/assets/psi-mark.svg").status_code == 200
    assert (
        client.get("/workshop/assets/premise-logo-transparent.png").status_code == 200
    )
    assert client.get("/scenarios/assets/explorer.css").status_code == 200
    assert client.get("/lca-time/assets/styles.css").status_code == 200
    assert client.get("/lca-time/assets/routing/beccs-routing.html").status_code == 200


def test_workshop_password_protects_every_deck_route() -> None:
    auth_client = Client(application, Response, use_cookies=True)

    workshop_asset = auth_client.get("/workshop/assets/styles.css")
    workshop_api = auth_client.get("/workshop/_dash-layout")
    assert workshop_asset.status_code == 401
    assert workshop_api.status_code == 401
    assert workshop_asset.headers["Cache-Control"] == "no-store"
    assert workshop_asset.headers["X-Robots-Tag"] == "noindex, nofollow"

    wrong_password = auth_client.post("/workshop/", data={"password": "27082026"})
    assert wrong_password.status_code == 401
    assert "That password is not correct." in wrong_password.text

    unlock_presentation(auth_client, "/workshop", "03092026")
    assert auth_client.get("/workshop/_dash-layout").status_code == 200
    assert auth_client.get("/workshop/assets/styles.css").status_code == 200

    # The LCA-through-time presentation is public and needs no session cookie.
    assert auth_client.get("/lca-time/").status_code == 200
    assert auth_client.get("/lca-time/_dash-layout").status_code == 200
    assert auth_client.get("/lca-time/assets/styles.css").status_code == 200


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
    assert [item["id"] for item in catalog] == [
        "iam-workshop-2026-09-03",
        "lca-through-time-2026-08-27",
    ]
    assert catalog[0]["date"] == "2026-09-03"
    assert catalog[0]["date_label"] == "3 September 2026"
    assert catalog[0]["title"] == "IAM scenarios workshop"
    assert catalog[0]["href"] == "/workshop/"
    assert catalog[1]["date"] == "2026-08-27"
    assert catalog[1]["date_label"] == "27 August 2026"
    assert catalog[1]["title"] == "LCA through time"
    assert catalog[1]["href"] == "/lca-time/"


def test_lca_time_deck_contract() -> None:
    assert CORE_SLIDE_COUNT == 24
    assert APPENDIX_SLIDE_COUNT == 2
    assert LAST_SLIDE == 25

    slide_two = repr(render_slide(1))
    assert "Sacchi et al. (2026) · TRAILS preprint" in slide_two
    assert "https://www.researchsquare.com/article/rs-10139523/v1" in slide_two


def test_publication_catalog_contract() -> None:
    catalog = publications()
    foundational = [item for item in catalog if item["kind"] == "foundational"]
    applications = [item for item in catalog if item["kind"] == "application"]

    assert len(foundational) == 1
    assert len(applications) >= 49
    assert foundational[0]["doi"] == "10.1016/j.rser.2022.112311"
    assert [item["date"] for item in applications] == sorted(
        [item["date"] for item in applications], reverse=True
    )
    assert len({item["doi"] for item in catalog}) == len(catalog)
    assert all(str(item["href"]).startswith("https://doi.org/") for item in catalog)
    assert all(item["topics"] for item in applications)


def test_all_apps_use_the_same_premise_favicon() -> None:
    root = Path(__file__).resolve().parents[1]
    favicon_paths = [
        root / "portal/static/favicon.ico",
        root / "apps/scenario_explorer/assets/favicon.ico",
        root / "apps/workshop/assets/favicon.ico",
        root / "apps/lca_time/assets/favicon.ico",
    ]
    assert all(path.is_file() for path in favicon_paths)
    assert len({path.read_bytes() for path in favicon_paths}) == 1
    with Image.open(favicon_paths[0]) as favicon:
        assert favicon.convert("RGBA").getchannel("A").getextrema() == (0, 255)


def test_portal_and_workshop_use_the_same_transparent_premise_logo() -> None:
    root = Path(__file__).resolve().parents[1]
    logo_paths = [
        root / "portal/static/premise-logo-transparent.png",
        root / "apps/workshop/assets/premise-logo-transparent.png",
    ]
    assert all(path.is_file() for path in logo_paths)
    assert len({path.read_bytes() for path in logo_paths}) == 1
    with Image.open(logo_paths[0]) as logo:
        assert logo.mode == "RGBA"
        assert logo.getchannel("A").getextrema() == (0, 255)
