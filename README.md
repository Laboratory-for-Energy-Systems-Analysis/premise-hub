# Premise Hub

Premise Hub is the public portal for tools and teaching resources maintained by
the PSI Laboratory for Energy Systems Analyses around integrated assessment
models and prospective life-cycle assessment.

The deployed service exposes:

- `/` — resource landing page;
- `/scenarios/` — the IAM scenario explorer;
- `/workshop/` — the interactive IAM workshop;
- `/health` — a lightweight service health endpoint.

## Local development

Create a Python 3.13 environment, install the runtime and development
dependencies, and start the combined WSGI application:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
gunicorn portal.wsgi:application --workers 1 --threads 4 --bind 127.0.0.1:8050
```

Open <http://127.0.0.1:8050>. The individual Dash applications can also be
started as modules for focused development.

## Tests

```bash
pytest -q
python scripts/browser_smoke.py --url http://127.0.0.1:8050
```

Workshop-specific visual checks remain under `apps/workshop/scripts/` and must
be pointed at `http://127.0.0.1:8050/workshop/` when the portal is running.

## Data and licensing

Application code is licensed under the BSD 3-Clause License. Scenario data,
logos, figures, and other third-party material retain their original terms; see
`THIRD_PARTY_NOTICES.md` and the data READMEs before redistribution.

