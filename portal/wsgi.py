from __future__ import annotations

import os
from datetime import date

from werkzeug.middleware.dispatcher import DispatcherMiddleware

os.environ.setdefault("SCENARIO_REQUESTS_PREFIX", "/scenarios/")
os.environ.setdefault("WORKSHOP_REQUESTS_PREFIX", "/workshop/")
os.environ.setdefault("LCA_TIME_REQUESTS_PREFIX", "/lca-time/")

from apps.lca_time.app import server as lca_time_server
from apps.scenario_explorer.app import server as scenario_server
from apps.workshop.app import server as workshop_server

from .auth import PresentationPasswordGate
from .landing import create_landing_app
from .presentations import presentations


def _password_from_event_date(iso_date: str) -> str:
    return date.fromisoformat(iso_date).strftime("%d%m%Y")


def _protect_presentation(app, href: str):
    presentation = next(
        item
        for item in presentations()
        if item["kind"] == "hosted" and item["href"] == href
    )
    return PresentationPasswordGate(
        app,
        presentation_id=str(presentation["id"]),
        title=str(presentation["title"]),
        password=_password_from_event_date(str(presentation["date"])),
        mount_path=href.rstrip("/"),
    )


landing = create_landing_app()
application = DispatcherMiddleware(
    landing,
    {
        "/lca-time": lca_time_server,
        "/scenarios": scenario_server,
        "/workshop": _protect_presentation(workshop_server, "/workshop/"),
    },
)
