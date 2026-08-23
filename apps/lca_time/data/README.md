# Data contract

The deployed presentation consumes compact, reviewed derivatives written to
`data/processed/`. Licensed source inventories, IAM source files and generated
TRAILS matrix packages remain local and are ignored by Git.

The current local package paths, hashes, anchor years, annual TRAILS matrix
dimensions and unresolved temporal diagnostics are recorded in
`trails_packages_manifest.json`.

## `static_lcia.csv`

One row per static result and indicator.

```text
case
model
pathway
region
year
functional_unit
functional_unit_amount
forest_case
chp_treatment
method
indicator
score
unit
package_id
package_sha256
foreground_sha256
premise_version
trails_version
source_database
calculation_timestamp
provenance_id
```

The 2025 rows are annual matrices interpolated by TRAILS from the original IAM
anchor-year matrices. They are not separate premise exports.

## `scenario_sector_indicators.csv`

Scenario-dependent static climate intensities used in the prospective-LCA
comparison plots. The file contains the ENC medium-voltage electricity market,
district-heat market, Portland-cement production and low-alloyed-steel market
for both workshop pathways in 2025, 2030 and 2050. Each score represents one
unit of the named background activity and uses the same IPCC 2021 GWP100 method,
including biogenic CO2, as the removal-system calculations.

Recalculate the 24 reviewed values directly from the two TRAILS packages with:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/calculate_scenario_sector_indicators.py
```

## `scenario_sector_mixes.csv`

Aggregate technology shares in selected premise-generated ENC markets for both
pathways in 2025, 2030 and 2050: high-voltage electricity,
district/industrial heat, clinker, low-alloyed steel and freight-lorry
transport. The
source market exchanges are grouped into presentation-level technology
families; each sector/pathway/year group sums to one. The aggregate file
supports the stacked market-composition plots without redistributing the
underlying inventory matrices.

Rebuild it with:

```bash
python scripts/extract_scenario_sector_mixes.py
```

## `static_contributions.csv`

Contribution records associated with `static_lcia.csv`:

```text
provenance_id
contributor
contributor_type
score
unit
rank
```

Both `activity` and `biosphere flow` contribution types are retained. Each type
independently closes to the corresponding total score; the two types must not be
summed together.

## `temporal_inventory.csv`

Compact year-resolved climate inventory totals retained for diagnostics. Each
case/cohort is solved in a fresh TRAILS instance. Greenfield BECCS includes
construction from commissioning year −3 through −1, annual project harvest and
operation from year 0 through +19, end-of-life in year +20, and 83 years of
replacement-stand regrowth after every harvest. Shared pre-decision forest
history is not routed.

```text
case
model
pathway
region
commissioning_year
inventory_year
root_activity
flow
compartment
subcompartment
amount
unit
forest_case
counterfactual
chp_treatment
package_id
provenance_id
```

## `temporal_lcia.csv`

Compact year-resolved characterized diagnostics following the same schedule.
The presentation uses the root-attributed `cohort_temporal_scores.csv` artifact.

```text
case
pathway
commissioning_year
impact_year
method
indicator
score
unit
forest_case
counterfactual
chp_treatment
provenance_id
```

## `fair_results.csv`

FaIR response and CO2-pulse-equivalence results:

```text
case
pathway
commissioning_year
year
metric
statistic
value
unit
reference_pulse_year
window_start
window_end
forest_case
counterfactual
chp_treatment
provenance_id
```

Expected metrics include atmospheric CO2 perturbation, radiative forcing,
temperature change, RF-based pulse equivalence and temperature-based pulse
equivalence.

The reported FaIR time series contain the 2.5th, 25th, 50th, 75th and 97.5th
percentiles across all 841 bundled calibrated configurations. Pulse equivalents
integrate from the commissioning year through 2300 and use a scenario-consistent
CO2 pulse in the commissioning year.

For BECCS, the reference leaves the existing mature forest standing at constant
carbon stock and supplies equivalent exported electricity and heat from the
scenario-resolved Northern European markets. Shared pre-decision forest history
cancels. The project inventory contains harvest and biomass supply, replacement-
stand regrowth, new CHP+CCS construction and operation, displaced energy,
capture, transport, geological storage and end-of-life.

TRAILS 1.0.1 takes the absolute value of routed technosphere coefficients. The
analysis script applies the matrix-consistent signed rule locally so that the
foreground avoided-energy exchanges remain negative demands. This is recorded
in code and checked against the routed cohort; it does not alter either premise-
generated package.

## `system_inventory_2025.json`

Reviewed foreground quantities used in the two conventional-LCA system-boundary
slides. Values refer to the 2025 `SSP2-NPi` Northern European inventory and are
scaled to one net tonne stored after transport loss. The file keeps gross
storage, selected energy and material flows, direct carbon exchanges and the
package/foreground hashes together. For BECCS, it records the standing-forest
reference, annual project harvest and regrowth, new-CHP fuel input, gross
electricity-plus-heat output, avoided market energy, conversion losses and gross
energy efficiency so that the presentation energy and carbon balances are
auditable. Rebuild it after the static calculation with:

```bash
python scripts/build_system_inventory.py
```

## `lifetime_lcia.csv`

Annual and aggregated results for one plant of each removal system commissioned
in 2030 and operated through 2049. DACCS uses the inventory's 100 ktCO2/year
capture capacity. BECCS uses the CHP inventory's 6667 kW fuel-input capacity,
4000 operating hours/year and 20-year lifetime. The 2.8% physical loss along
the 2000 km pipeline is deducted from captured CO2 to obtain the denominator.

Each annual row uses that calendar year's interpolated REMIND-EU background.
The lifetime row sums all twenty absolute annual scores and divides once by the
lifetime physical net atmospheric CO2 stored. Supply-chain GHG emissions remain
in the numerator; the result is therefore not forced to -1000 kg CO2-eq.

Recalculate both pathways with:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/calculate_lifetime_results.py
```

## `lifetime_contributions.csv`

Closing annual and lifetime contribution views associated with
`lifetime_lcia.csv`. Activity and location views identify emitting activities.
The process view separately resolves forest regrowth, residual biogenic stack
emissions, harvest and biomass supply, new-CHP burdens, avoided Northern
European electricity and heat, direct DAC electricity, heat-pump electricity,
compression, CO2 transport/loss/storage, and remaining capture-material
burdens. Each view closes independently to the corresponding result.

## `cohort_temporal_scores.csv`

Root-attributed, year-resolved GWP100 scores for one complete 2030 plant cohort
under `SSP2-PkBudg1000`. BECCS starts from the greenfield project service:
avoided electricity and heat are attributed at depth one, and the direct
children of the new-CHP operation and capture containers at depth two. DACCS
retains its depth-three physical fan-out. Branch amounts are audited to close at
every routed frontier and direct-biosphere node.

The table uses the same reviewed timing corrections as the routing-graph slides:
construction in 2027--2029, operation in 2030--2049, and one end-of-life event
in 2050. Each BECCS harvest starts 83 years of replacement-stand regrowth, so
the last annual branch closes in 2132. Greenfield BECCS has no score before
2027. The chart spans 1940–2140 so the cancelled shared forest history and the
complete regrowth tail are both visible.

DACCS retains generic background temporal distributions from the TRAILS
package. Its electricity root can therefore carry pre-2030 negative scores from
time-shifted biogenic uptake in the upstream power mix; this is not early DAC
operation.

Both the absolute score for the complete physical plant cohort and the score
divided by lifetime net atmospheric CO2 stored are retained. Recalculate with:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/calculate_cohort_temporal_scores.py --show-progress
```

## `cohort_fair_responses.csv`

Median and 2.5th/97.5th-percentile FaIR radiative-forcing and temperature-
anomaly trajectories for the same complete 2030 cohorts. Results retain the
`run_fair_delta_rf` elementary-flow and root-activity attribution, then provide
two closing views: the physical process groups used on slide 16 and mapped
elementary flows grouped by name. Values are normalized to one net tonne stored
only after the full cohort response has been calculated. The response is
reported through 2300, using the post-2100 REMIND trajectories included in
TRAILS' scenario emissions file. Recalculate with:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/calculate_cohort_fair_responses.py --show-progress
```

## `co2_reference_pulse.csv`

Median and 2.5th/97.5th-percentile FaIR radiative-forcing and temperature-
anomaly responses to scenario-consistent positive CO2 pulses every five years
from 1940 through 2295. Each numerical run uses a 1 Mt pulse for stability and
exports the 1940–2300 response per kilogram of CO2. Slide 18 constrains the
selected pulse year to sit inside the interactive integration window, then
integrates the selected reference and the corresponding cohort response over
the same years. Their ratio is therefore in kg CO2 pulse-equivalent per net
tonne stored. Recalculate with:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/calculate_co2_reference_pulse.py
```

## `cohort_pulse_equivalence_grid.npz`

Median CO2-pulse equivalents for every valid five-year combination of window
start, reference-pulse year and window end from 1940 through 2300. Unlike a
ratio of median trajectories, each value follows
`trails.fair_rf.run_fair_co2_pulse_equivalents`: the system/reference ratio is
calculated for each of 841 calibrated FaIR configurations before taking the
median. The compressed five-dimensional array retains case, metric, start,
reference and end axes. Recalculate with:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/calculate_cohort_pulse_equivalence_grid.py
```

The default 2025–2140 window with a 2030 pulse is independently reproduced by
calling TRAILS' public function on both complete routed cohort inventories:

```bash
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  scripts/validate_cohort_pulse_equivalence.py
```

That validation is recorded in
`cohort_pulse_equivalence_validation.json`, including the 841-configuration
uncertainty summaries and input hashes.

## Validation

Before a file is used by the dashboard, validation must confirm:

- unique keys and non-empty units;
- scores for both cases and both pathways where required;
- 2025, 2030 and 2050 static coverage;
- greenfield temporal GWP coverage through the final regrowth year and FaIR
  response coverage bounded at 2300, both without renormalization;
- consistent package hashes and software versions within a run; and
- explicit labels for the `new CHP+CCS vs standing forest and Northern European
  energy` BECCS system.
