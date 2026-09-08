# LCA of CCS and CCUS applied to cement production

**What Integrating Time Reveals About Climate Benefits of CCS and CCUS**

Dr. Romain Sacchi · Paul Scherrer Institut · COST Action TrANsMIT · 11 September 2026

Dash presentation with 19 core slides and five appendices. The same BAU, CCS and
CCUS systems are compared through current and prospective static LCA, time-explicit
GWP100, FaIR radiative forcing and temperature, and CO₂-pulse equivalence.

## Run

Install the repository's root requirements, then run from the repository root:

```sh
gunicorn apps.ccus_webinar.app:server --bind 127.0.0.1:8050 --workers 1 --threads 4
```

Open `http://127.0.0.1:8050/`. The password-only screen uses the webinar date,
`2026-09-11`. The companion `/presenter` page shows notes and timers. The main
portal serves the application at `/ccus-webinar/` and lists it under Talks & workshops.

Set `CCUS_WEBINAR_PASSWORD` to override the shared password. Set a long random
`CCUS_WEBINAR_SECRET_KEY` consistently across deployment instances. Local runs
generate a private signing key under the ignored `generated/access/` directory.
Cookies expire after 12 hours. Changing the password invalidates existing access.
Use HTTPS for public deployment. A date password is an event access gate, not
protection for confidential data. No username is required.

## App-only release

`data/runtime/manifest.json` describes the reviewed 8 September 2026 release.
The five compressed result bundles contain the unchanged precomputed tables.
No Brightway, premise or TRAILS calculation runs during a presentation.
The physical-carbon decomposition is included for the optional chart view.

The original calculation evidence was hash-checked before packaging. At runtime,
the application checks the hashes of the distributed data and result bundles.
`data/runtime/review-record.json` retains the historical review and evidence
fingerprints, not the private source files. Accepted assumptions are distinct
from verified checks. Routing convergence was **not tested**: the reviewer
accepted the default cutoff of 1e-4. Changed release artifacts fail closed.

The Git allowlist excludes internal Excel files, full inventories, licensed
background databases, local calculation scripts, diagnostic exports and tests.
Only app modules, referenced visual assets, display data and result bundles are
distributed. Engineering display tables are rounded to the precision shown on
the slides and omit internal workbook column references.

The process model is adapted from Gallego Dávila, Sacchi and Pizzol (2023),
*Preconditions for achieving carbon neutrality in cement production through CCUS*,
[Journal of Cleaner Production 425, 138935](https://doi.org/10.1016/j.jclepro.2023.138935).
The numerical climate results were recalculated for this webinar.
