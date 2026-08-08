from __future__ import annotations

import os

# Dash bakes request prefixes into its index at import time.  Set the mounted
# production prefixes before pytest imports either application, independent of
# test collection order.
os.environ.setdefault("SCENARIO_REQUESTS_PREFIX", "/scenarios/")
os.environ.setdefault("WORKSHOP_REQUESTS_PREFIX", "/workshop/")
