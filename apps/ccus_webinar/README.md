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

Open `http://127.0.0.1:8050/`. The webinar opens directly without a password.
The companion `/presenter` page shows notes and timers. The main
portal serves the application at `/ccus-webinar/` and lists it under Talks & workshops.

## App-only release

`data/runtime/manifest.json` describes the reviewed 8 September 2026 release.
The five compressed result bundles contain the unchanged precomputed tables.
No Brightway, premise or TRAILS calculation runs during a presentation.
The public release omits private physical-inventory payloads. Climate-result
tables, including their contribution scores, remain unchanged.

The original calculation evidence was hash-checked before packaging. At runtime,
the application checks the hashes of the distributed data and result bundles.
`data/runtime/review-record.json` retains the review statuses, not private
source records or their derivations. Accepted assumptions are distinct
from verified checks. Routing convergence was **not tested**: the reviewer
accepted the default cutoff of 1e-4. Changed release artifacts fail closed.

The Git allowlist excludes internal Excel files, full inventories, licensed
background databases, local calculation scripts, diagnostic exports and tests.
Only app modules, referenced visual assets, display data and result bundles are
distributed. Input illustrations use published SI data and explicit public
webinar assumptions. The appendix does not export private utility coefficients,
heat-pump derivations or engineering flow tables. Rounding is not a privacy measure.

The permission to publish calculated climate results is separate from permission
to publish input data. Detailed results can still support inferences about a
system; this is not a guarantee against reverse engineering. A privacy regression test
checks distributed data and compressed payloads before release.

The process model is adapted from Gallego Dávila, Sacchi and Pizzol (2023),
*Preconditions for achieving carbon neutrality in cement production through CCUS*,
[Journal of Cleaner Production 425, 138935](https://doi.org/10.1016/j.jclepro.2023.138935).
The numerical climate results were recalculated for this webinar.
