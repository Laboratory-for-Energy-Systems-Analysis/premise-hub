# Kent Seminar 2026 — Keep It or Replace It?

Browser-based webinar deck for the University of Kent seminar on 12 November
2026. The deck contains 12 slides paced for about 20 minutes.

The app is intentionally **carculator-only**. It uses carculator's annual
lifecycle scheduling and calendar-year characterization, but does not claim
atmospheric dynamic LCA, FaIR radiative forcing, CO2-pulse equivalence, or
recursive timing inside background suppliers.

The carculator wordmark embedded in `assets/carculator-logo.svg` is the official
transparent asset from the local carculator documentation checkout
(`docs/_static/img/mediumsmall_2.png`). The mobility lifecycle and supporting
vehicle/pathway diagrams are repository-native SVG/CSS artwork so they remain
sharp in browser and PDF output.

Interface symbols embedded in those SVG diagrams use the Lucide icon geometry
(version 0.468.0, ISC licence). They are normalized to the library's 24×24 grid,
2-unit stroke, and round caps/joins; diagram structure, labels and data graphics
remain repository-native.

## Modeling contract

- Current vehicle: generic medium gasoline car, 2020 cohort.
- Default decision: replace after calendar year 2026.
- Service: 12,000 km/year (7,456 mi/year), varied from 5,000–20,000 km/year.
- Vehicle lifetime: 200,000 km (124,274 mi), varied from 150,000–250,000 km.
- Common owner service horizon: 2060, with successor vehicles repeated as needed.
- If a vehicle reaches its mileage threshold partway through a calendar year,
  its successor supplies the remaining kilometres in that same annual bin.
  Use and maintenance scores are prorated to the allocated kilometres;
  replacement events follow the corresponding distance crossing and final
  foreground end-of-life is placed one year after the actual final-use bin.
- Transferred-car use and end-of-life after the decision leave the modeled owner.
- Historical impacts remain in both paths; batteries are assumed to survive the car.
- Country `US`, representative WLTC cycle, vehicle-kilometre functional unit,
  EF 3.1 midpoint. All 25 categories are calculated; climate and particulate
  matter are used in the core deck.
- Vehicle specifications are interpolated between supported model years. Annual
  stage profiles are calculated directly for seven cohort anchors (2020, 2025,
  2030, 2035, 2040, 2050 and 2060) and linearly interpolated by lifecycle-event
  age between anchors. For post-2050 cohorts, endpoint-only vehicle/background
  data are held where needed. The manifest records these bounds explicitly.

The three presentation pairings are interpretive, not formal scenario
equivalences: SSP2-NPi + GECO reference, SSP2-PkBudg1000 + GECO NDC/LTS, and
SSP2-PkBudg650 + GECO 1.5°C. A separate sensitivity holds SSP2-NPi fixed and
changes only the GECO electricity trajectory, so background and charging-mix
effects are not conflated.

## Rebuild results

The checked-in runtime JSON is generated, never calculated in Dash:

```sh
PYTHONPATH=/Users/tagger/github/carculator:/Users/tagger/github/carculator_utils \
  conda run --no-capture-output -n premise \
  python apps/kent_2026/scripts/generate_results.py

PYTHONPATH=/Users/tagger/github/carculator:/Users/tagger/github/carculator_utils:/Users/tagger/github/premise-hub \
  conda run --no-capture-output -n premise \
  python apps/kent_2026/scripts/generate_slide9_sensitivity.py

.venv/bin/python apps/kent_2026/scripts/generate_slide10_landscape.py
```

Use `--compose-only` to rebuild the slide-facing climate and particulate-matter
cube from already generated vehicle profiles without rerunning carculator.

`data/runtime/manifest.json` records both source commits, dirty-state disclosure,
configuration and the SHA-256 hash of `results.json`. The generator reads the
local development checkouts but never modifies them.

`data/runtime/vehicle_specs.json` is the compact slide-facing model summary for
the five 2026 US comparison vehicles. It records rounded current-checkout
outputs (curb mass, cycle-average tank-to-wheel efficiency, range and battery
storage); the full impact profiles remain in the hashed result bundle.

`data/runtime/replacement_vehicle_specs.json` records the cohort-specific
physical specifications shown on slide 7 for the 2020 gasoline car and its
2027–2053+ BEV successors: rated power, nominal battery capacity, curb mass and
WLTC energy use. Post-2050 vehicle specifications follow the same held-endpoint
rule as the impact profiles.

`data/runtime/slide6_results.json` records the six-panel 2025 US mobility
comparison. It combines current local outputs from carculator,
carculator_two_wheeler, carculator_bus and carculator_truck. Passenger modes use
passenger-kilometres; trucks use tonne-kilometres. Its electricity sensitivity
uses explicit wind-to-coal custom mixes, synthetic gasoline made with
electrolytic hydrogen and cement-plant CO2, and a PEM-electrolysis FCEV. Source
commits and the remaining documentation-only dirty states are recorded in the
artifact.

`data/runtime/slide9_sensitivity.json` records the 256 precomputed cumulative
comparisons behind slide 9: four total lifetimes, four annual mileages, four
future energy-system pathways and four gasoline blends. The pathways combine
REMIND backgrounds with their calendar-year GECO charging mixes: SSP2-NPi plus
Reference, an explicit 50/50 midpoint, SSP2-PkBudg1000 plus NDC/LTS, and
SSP2-PkBudg650 plus 1.5°C. The gasoline choices are the carculator
reference blend, E20, E50 and E85; all ethanol cases use first-generation
corn-starch ethanol. The displayed crossing is the
first year after which replacement remains lower through 2060, so a temporary
crossing before a later production pulse is not reported as payback.
Each configuration stores both EF 3.1 climate-change and particulate-matter
formation trajectories. The latter is displayed in thousandths of a disease
incidence; it is an LCIA health-impact result, not a mass of emitted particles.

`data/runtime/slide10_landscape.json` stores the climate decision landscape.
The main slide presents four synchronized replacement-year × charging-carbon-
intensity maps, one for each annual mileage; vehicle lifetime and evaluation
year select among 16 precomputed states. The
intensity axis is a transparent stress test: BEV use-stage climate impacts from
the annual GECO reference profile are scaled around its 449 g CO2-eq/kWh anchor,
while vehicle production and all other non-use impacts remain unchanged. Cases
within ±2 t CO2-eq are hidden rather than assigned to KEEP or REPLACE.

The bundle-level audit does not require the Dash environment:

```sh
python apps/kent_2026/scripts/audit_results.py
```

Fuel routes shown in the deck are explicit bundled carculator recipes: the
default petrol blend, E20, E50 and E85 represented as 20%, 50% and 85% corn-starch ethanol by volume,
synthetic petrol from methanol/electrolytic hydrogen/cement-plant CO2 with energy
allocation, and FCEV hydrogen from natural-gas SMR. Fuel shares remain fixed for
the cohort. These routes are composed into complete owner-level keep/replacement
sequences through 2060, alongside BEV and future efficient-gasoline successors.
Unsupported DAC-synthetic petrol and dedicated-PV charging claims are omitted.

## Run

Create the project-local environment once:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
```

Then start the mounted portal from the repository root:

```sh
.venv/bin/python -m gunicorn portal.wsgi:application \
  --bind 127.0.0.1:8050 --workers 1 --threads 4
```

Open `http://127.0.0.1:8050/` standalone or `/kent-2026/` through the portal.
Arrow keys, Page Up/Down and space navigate. `/presenter` contains notes and a
21:45 timer. Export PDF produces all 12 pages.

After starting the combined portal, run the visual and PDF regression check:

```sh
.venv/bin/python apps/kent_2026/scripts/browser_check.py \
  --url http://127.0.0.1:8050/kent-2026/ \
  --output build/kent-2026
```

It walks all core slides, records overflow and request errors, exercises the
precomputed map transition, captures screenshots, and writes the landscape PDF.
On a restricted host that cannot open a local TCP listener, use `--in-process`;
the checker routes Chromium requests through the same mounted WSGI application.

