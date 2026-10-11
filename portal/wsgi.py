from __future__ import annotations

import os

from werkzeug.middleware.dispatcher import DispatcherMiddleware

os.environ.setdefault("SCENARIO_REQUESTS_PREFIX", "/scenarios/")
os.environ.setdefault("WORKSHOP_REQUESTS_PREFIX", "/workshop/")
os.environ.setdefault("LCA_TIME_REQUESTS_PREFIX", "/lca-time/")
os.environ.setdefault("CCUS_WEBINAR_REQUESTS_PREFIX", "/ccus-webinar/")
os.environ.setdefault("SETAC_2026_REQUESTS_PREFIX", "/setac-2026/")

from apps.ccus_webinar.app import server as ccus_webinar_server
from apps.lca_time.app import server as lca_time_server
from apps.scenario_explorer.app import server as scenario_server
from apps.setac_2026.app import server as setac_2026_server
from apps.workshop.app import server as workshop_server

from .landing import create_landing_app

landing = create_landing_app()
application = DispatcherMiddleware(
    landing,
    {
        "/ccus-webinar": ccus_webinar_server,
        "/lca-time": lca_time_server,
        "/setac-2026": setac_2026_server,
        "/scenarios": scenario_server,
        "/workshop": workshop_server,
    },
)
