# Premise Hub

Premise Hub is the public portal for tools and teaching resources maintained by
the PSI Laboratory for Energy Systems Analyses around integrated assessment
models and prospective life-cycle assessment.

The deployed service exposes:

- `/` — resource landing page;
- `/ecosystem/` — interactive map of open-source Brightway tools;
- `/scenarios/` — the IAM scenario explorer;
- `/workshop/` — the interactive IAM workshop;
- `/lca-time/` — the LCSS presentation comparing conventional, prospective,
  and time-explicit LCA;
- `/health` — a lightweight service health endpoint.

Both presentations are public. Their dates and routes are defined in
`portal/presentations.yaml`.

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
The LCA-through-time presentation is deployed from `apps/lca_time/`; its
processed result contract and provenance are documented in that app's data
README.

## Publication catalog maintenance

The scrollable publication list on the landing page is driven by
`portal/publications.yaml`. Include peer-reviewed papers whose methods or data
workflow explicitly report using Premise; papers that only cite, review, or
discuss Premise do not belong in the application list. The foundational
Premise paper is retained as the catalog's single `foundational` entry and is
displayed separately.

Each entry needs a stable identifier, full title and author list, journal,
ISO publication date, DOI, matching `https://doi.org/` link, topic tags, and a
kind of either `application` or `foundational`. The loader validates these
fields, rejects duplicate identifiers and DOIs, and sorts applications newest
first. After adding a paper, run the unit and browser smoke tests described
above.

## Ecosystem catalog maintenance

The interactive Brightway ecosystem is driven by `portal/ecosystem.yaml`.
Each project has a workflow stage, project family, editorial status, source
links, tags, and a stable identifier. Relationships use the controlled types
defined at the top of the same file. The loader rejects duplicate identifiers,
unknown relationship endpoints, and non-HTTPS external links.

Projects belong in the main catalog when they are reusable open-source
software, expose a documented Brightway data or calculation path, and have a
public source repository or primary documentation. Datasets, publications,
teaching repositories, one-off study code, metadata-only packages, and
superseded utilities are normally excluded. Historically important projects
can be retained as `legacy`; they remain searchable but are hidden by the
default status filter.

Project identifiers are also URL fragment identifiers (for example,
`/ecosystem/#premise`) and should not be renamed after publication. Workflow
stages describe the project's primary entry point, while families distinguish
Brightway core, extensions, cross-framework integrations, and domain models.
Statuses are editorial classifications: `active`, `experimental`,
`maintenance`, or `legacy`.

When adding or revising a project:

1. verify its role and status against official documentation or its source
   repository;
2. update the catalog-level `verified_on` date;
3. keep summaries factual and describe every relationship explicitly;
4. add regression coverage for important additions;
5. run `pytest -q` and the browser smoke test at desktop and mobile widths.

The status labels are catalog-maintainer classifications, not guarantees of
support from the individual projects.

## Data and licensing

Application code is licensed under the BSD 3-Clause License. Scenario data,
logos, figures, and other third-party material retain their original terms; see
`THIRD_PARTY_NOTICES.md` and the data READMEs before redistribution.
