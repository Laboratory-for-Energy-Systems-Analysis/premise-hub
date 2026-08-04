# Workshop Dashboard — Product and Technical Specification

## Product definition

A public, Heroku-deployed Dash application that functions as both the projected
presentation and an optional participant explorer. It is purpose-built for a
guided IAM-scenario workshop rather than a general-purpose data browser.

## Modes

### Presentation mode

- Full-screen, 16:9-friendly composition.
- Large typography and reduced chart density.
- Previous/next controls and keyboard navigation.
- Presenter controls for reveal, chapter jumps, clue progression, and recording
  show-of-hands counts.
- No audience submissions and no shared multi-user state.

### Explore mode

- Curated controls for model/scenario, sector, comparison view, and year.
- Narrative and provenance cards remain visible beside plots.
- Advanced cross-IAM comparisons carry comparability warnings.
- No unfiltered list of all 486 variables in the first release.

## State map

```text
Why IAMs
  ├─ Energy services and present energy/emissions trends
  ├─ Sectoral greenhouse-gas emissions
  ├─ Cumulative CO2, warming and carbon budgets
  ├─ Cross-sector mitigation coupling
  ├─ Net-zero commitments: endpoint → pathway → investment → inventory
  ├─ IAM definition and experiment types
  ├─ IAM scenario history and policy interface
  ├─ Anonymous futures
  └─ Scenario vocabulary
IAM theory
  ├─ System map and stock-flow mechanics
  ├─ Model landscape
  └─ Limitations
Scenario frameworks
  ├─ Narrative assumptions
  ├─ AR5 → AR6 → AR7
  └─ CMIP7 emission families
Read the pathways
  ├─ Detective and SSP2 comparison
  ├─ Electricity, transport, steel and CDR
  ├─ Cross-IAM comparison
  └─ R10 mapping
From IAM to premise
  ├─ Evidence chain
  └─ Sector transformations
LCIA trade-offs
  └─ Electricity, steel and DAC
Choose and report
  └─ Contrastive selection
```

## Visual system

- Discrete “PSI - Laboratory for Energy Systems Analyses” identification in a
  small header/footer area.
- Use the current official PSI logo asset; do not redraw it.
- Neutral background with one strong colour per scenario.
- Scenario colours remain fixed across every screen and chart after reveal.
- Anonymous detective colours must not encode low/medium/high before reveal.
- Colour-vision-safe palette and redundant line styles/labels.
- Minimum projected body text target: approximately 24 px at 1920×1080.
- Avoid scroll-dependent access to essential content during presentation mode.

## Curated data layers

### 1. Workshop pathway data

Derived from the untracked source CSV and, where approved, original IAM files.

Proposed schema:

```text
model
model_version
scenario
scenario_family
ssp
pathway_label
region_native
region_common
region_mapping_status
year
sector
variable
value
unit
aggregation_rule
source_file_id
source_variable
```

Store a compact, redistributable derivative under `data/processed/`, preferably
compressed CSV unless performance tests justify Parquet and its dependencies.

### 2. Narrative metadata

Tracked YAML or JSON containing:

- display name and one-sentence shorthand;
- intended SSP narrative elements;
- pathway/overshoot description;
- model-specific interpretation;
- important assumptions and absent mechanisms;
- source citations;
- scientific sign-off status and date.

Narrative metadata must not be inferred live from curve shapes.

### 3. `premise` transformation metadata

Tracked YAML or JSON containing:

- IAM sector and variable;
- transformation name;
- inventory markets, efficiencies, emissions, or learning parameters affected;
- what is not transformed;
- relevant `premise` version/source reference;
- diagram annotation text.

### 4. LCIA result data

Precomputed result schema:

```text
model
scenario
year
database_name
source_database
premise_version
region
dac_technology
functional_unit
method_family
category
indicator
score
unit
calculation_timestamp
provenance_id
```

The application reads result tables only. Brightway and ecoinvent are not part of
the deployed Heroku runtime.

### 5. Region concordance

Tracked mapping table with:

```text
model
native_region
r10_region
status            # exact | aggregated | approximate | unavailable
aggregation_group
coverage_note
source
approved
```

The app must not display a synthesized R10 aggregate unless all components and
aggregation rules are explicit. Approximate mappings remain visibly approximate.

## Curated first-release content

### Core scenarios

- IMAGE `SSP1-L`
- IMAGE `SSP2-M`
- IMAGE `SSP3-H`
- IMAGE `SSP2-VLHO`

### Optional cross-IAM comparisons

- IMAGE versus MESSAGE for a genuinely shared scenario family such as `SSP2-M`
  or `SSP1-L`.
- New GCAM RCP3.7/RCP4.5/RCP6.0 subset only, clearly labelled as an optional
  legacy-framework exploration.
- WITCH excluded.

### Core years

- 2020 baseline/context
- 2040 near-to-medium-term decision point
- 2060 longer-term transformation point

Full time series remain available for trajectory charts.

### Core sectors and variables

1. Global context: population, GDP, CO2/GHG, and GMST where definitions are clear.
2. Electricity: generation by technology and relative shares.
3. CDR/DAC: annual and cumulative quantities with definitions kept separate.
4. Steel: absolute production and route shares.
5. Transport: passenger-car and road-freight technology pathways.

Initial availability checks confirm that population, GDP, CO2, GMST,
electricity, and steel have 2020/2040/2060 coverage for the four IMAGE scenarios.
CDR/DAC is sparse: absent rows cannot be assumed to be zero without validation
against the original IMAGE workbook. Electricity and steel also expose different
numbers of nonzero technology rows across scenarios, so the curated layer needs a
documented common technology taxonomy and explicit zero/missing semantics.

## Chart patterns

### Trajectory chart

- Fixed historical/scenario transition marker.
- Direct line labels at the right edge.
- Scenario and model shown separately.
- Unit and system boundary always visible.
- Hover text includes source variable and mapping status.

### Technology mix

- Absolute stacked areas/bars only for additive variables with aligned units.
- 100% stacked view for relative shares.
- Explicit “other” category rule.
- Toggle between 2020, 2040, and 2060 snapshots and full trajectory.

### Difference and cumulative views

Not part of the first presenter path unless validation confirms that the selected
variables support them without mixing incompatible boundaries.

### LCIA comparison

- Group by DAC technology, then scenario/year.
- Absolute results with units; avoid index-only charts as the primary view.
- Highlight rank reversals and burden shifting rather than declaring a winner.
- Link each bar/point back to its scenario database and transformation note.

## Presenter interactions

- `Next`, `Back`, and a progress indicator.
- `Reveal next clue` during the detective sequence.
- `Reveal scenario names` with a transition that preserves curve positions.
- Four count buttons for show-of-hands responses; counts remain local to the
  presenter browser session.
- `Compare opening vote` on the final screen.
- `Reset session` with a confirmation step.

## Technology stack

- Python Dash and Plotly, reusing proven patterns from the existing explorer but
  not inheriting its general-purpose layout.
- Dash Bootstrap Components or a small custom CSS layer for responsive layout.
- Pandas for compact curated data; avoid loading the 79 MB raw CSV in production.
- Flask-Caching only if profiling demonstrates a need.
- Gunicorn for Heroku.
- No Brightway, ecoinvent, or IAM source workbooks in the deployed application.
- No database required for the first release because responses are local and
  ephemeral.

## Heroku deployment

- `Procfile` starts Gunicorn against the Dash server.
- Pin a supported Python runtime and dependencies.
- Load only processed public data committed with the application or downloaded
  from a versioned public release at build time.
- Add a health endpoint.
- Configure one worker initially to minimise memory duplication; profile before
  increasing concurrency.
- Test first-load time, memory use, and cold-start behaviour with the final slug.

## Scientific and UX guardrails

- Never call a scenario “business as usual” without a precise policy definition.
- Never order scenarios by probability unless an external probability assessment
  is explicitly sourced.
- Never imply that equal warming means equal technology backgrounds.
- Never sum variables across a hierarchy without selecting leaf nodes and checking
  units.
- Never coerce a missing technology or CDR row to zero without confirming that the
  source format uses sparse zero encoding.
- Never compare native regions as if their boundaries were identical.
- Never use temperature alone to select a `premise` database.
- Always show model, scenario, year, region, unit, and data provenance.
- Label generated interpretation separately from source narrative.

## Validation and acceptance criteria

### Scientific

- Every plotted series maps to a source variable and unit.
- Additive charts pass hierarchy/double-counting checks.
- The four IMAGE narratives receive owner sign-off.
- `premise` transformation diagrams match the selected version's implementation.
- DAC result databases and functional units are reproducibly documented.
- R10 concordance has no unlabelled approximate mappings.

### Functional

- Presentation path can be completed without page reloads or scrolling failures.
- Presenter state survives a browser refresh through URL/local session state.
- Reveal/reset logic is deterministic.
- Explore controls cannot create scientifically invalid comparisons.
- App starts from a clean Heroku dyno.

### Visual

- Projected content is readable at 1920×1080.
- No chart legend obscures data.
- Scenario encodings are consistent after reveal.
- Layout works at common laptop widths.
- PSI branding remains visible but secondary to workshop content.

### Performance

- Target first meaningful render below 3 seconds on a warm dyno.
- Presenter interactions should feel immediate and avoid full-data recomputation.
- Production memory remains comfortably below the selected dyno limit.

## Implementation sequence

1. Produce the curated multi-IAM scenario table and source manifest.
2. Validate units, hierarchy, and the four narrative cards.
3. Implement the seven-chapter presenter shell and interactions.
4. Add the theory, framework, pathway and transformation views.
5. Build ecoinvent 3.12 cutoff scenario databases with `premise` 2.4.6.
6. Generate electricity, steel and DAC LCIA results and provenance.
7. Test locally, deploy to Heroku, rehearse and revise.

## Open implementation dependencies

- Scenario databases use `premise` 2.4.6 and ecoinvent 3.12 cutoff.
- EF 3.1 method and activity contracts are recorded with the calculated results.
- Obtain the official current PSI logo asset.
- Owner review of curated units and narrative cards.
- The applied LCIA comparison uses Switzerland for electricity and WEU for steel
  and DAC, with mapping quality shown explicitly.
