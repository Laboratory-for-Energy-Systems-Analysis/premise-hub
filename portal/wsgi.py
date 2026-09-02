from __future__ import annotations

import os

from werkzeug.middleware.dispatcher import DispatcherMiddleware

os.environ.setdefault("SCENARIO_REQUESTS_PREFIX", "/scenarios/")
os.environ.setdefault("WORKSHOP_REQUESTS_PREFIX", "/workshop/")
os.environ.setdefault("LCA_TIME_REQUESTS_PREFIX", "/lca-time/")

from apps.lca_time.app import server as lca_time_server
from apps.scenario_explorer.app import server as scenario_server
from apps.workshop.app import server as workshop_server

from .landing import create_landing_app

landing = create_landing_app()
application = DispatcherMiddleware(
    landing,
    {
        "/lca-time": lca_time_server,
        "/scenarios": scenario_server,
        "/workshop": workshop_server,
    },
)
