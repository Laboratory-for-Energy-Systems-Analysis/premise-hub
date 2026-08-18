from __future__ import annotations

from copy import deepcopy

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from portal.ecosystem import ecosystem, validate_ecosystem
from portal.wsgi import application

client = Client(application, Response)


def test_ecosystem_page_and_assets() -> None:
    response = client.get("/ecosystem/")
    assert response.status_code == 200
    assert "The Brightway ecosystem, connected." in response.text
    assert 'id="ecosystem-data"' in response.text
    assert 'data-tool-id="premise"' in response.text
    assert 'data-tool-id="dynamic-characterization"' in response.text
    assert 'data-tool-id="pulpo"' in response.text
    assert 'data-tool-id="prosperdyn"' in response.text
    assert 'data-tool-id="regioinvent"' in response.text
    assert 'data-tool-id="shrecc"' in response.text
    assert 'data-tool-id="pylcaio"' in response.text
    assert 'data-tool-id="optimex"' in response.text
    assert 'data-tool-id="carculator"' in response.text
    assert 'data-tool-id="firefly"' in response.text
    assert client.get("/ecosystem").status_code == 308
    assert client.get("/static/ecosystem.css").status_code == 200
    assert client.get("/static/ecosystem.js").status_code == 200


def test_ecosystem_catalog_contract() -> None:
    catalog = ecosystem()
    tool_ids = {tool["id"] for tool in catalog["tools"]}
    relationship_type_ids = {
        relationship_type["id"] for relationship_type in catalog["relationship_types"]
    }

    assert catalog["metadata"]["verified_on"] == "2026-08-18"
    assert len(tool_ids) >= 65
    assert {
        "bw2data",
        "bw2calc",
        "bw-processing",
        "activity-browser",
        "premise",
        "trails",
        "edges",
        "flodym",
        "pulpo",
        "prosperdyn",
        "regioinvent",
        "regiopremise",
        "enbios",
        "bw-hestia-bridge",
        "brightway-ef4lca",
        "bw2parameters",
        "shrecc",
        "openlca2bw",
        "brightway-olca",
        "aligned-converter",
        "fauldier",
        "pylcaio",
        "simodin",
        "pandarus",
        "moca",
        "optimex",
        "pbaesa",
        "iwp-reborn",
        "premise-gwp",
        "lcpy",
        "relics",
        "bw-matchbox",
        "firefly",
        "lcopt",
        "carculator",
        "carculator-truck",
        "carculator-bus",
        "carculator-two-wheeler",
        "sense",
        "pelca",
    } <= tool_ids
    assert all(
        tool["links"]["source"].startswith("https://") for tool in catalog["tools"]
    )
    assert all(
        relationship["source"] in tool_ids
        and relationship["target"] in tool_ids
        and relationship["type"] in relationship_type_ids
        for relationship in catalog["relationships"]
    )


def test_ecosystem_validation_rejects_unknown_relationship_endpoint() -> None:
    catalog = deepcopy(ecosystem())
    catalog["relationships"][0]["target"] = "missing-tool"

    with pytest.raises(ValueError, match="endpoint is unknown"):
        validate_ecosystem(catalog)
