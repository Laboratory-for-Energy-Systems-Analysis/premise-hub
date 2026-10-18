# SETAC Europe LCA Case Study Symposium 2026

**How time integration changes LCA: the case of CDR**

Romain Sacchi (presenter), Tom Terlouw, Karin Treyer, Alvaro Hahn Menacho,
Arthur Jakobs and Christian Bauer. Romain's name is underlined on the cover.

19 October 2026, 14:05, Foyer 3, Bruges. Presentation **1.01.T01** in session
*Advancing Life Cycle Assessment for Carbon Dioxide Removal (CDR)*.

Twelve main slides, planned for **10:25**, leaving 1:35 within the 12-minute
speaking slot. Questions are separate. Two optional backup slides cover
accounting and the existing forest-carbon sensitivity. References form the final
main slide, with no separate speaking segment.

The app reuses `lca_time`'s stylesheet directly, including its PSI header,
chapter navigation, progress bar, rounded slide canvas, typography and footer.
The cover artwork and CDR system diagram are the original shared SVG assets.
SETAC-specific CSS only adapts the shorter slide content and print layout.
The SETAC logo is the unmodified [official website SVG](https://www.setac.org/assets/img/logo.svg),
stored locally for offline use and shown at the top right of the app and PDF pages.
Slide five reuses the original PIK and premise logos from `lca_time` in the
REMIND-EU and premise workflow boxes.

## Run and present

From the repository root, using the root requirements:

```sh
venv/bin/gunicorn apps.setac_2026.app:server --bind 127.0.0.1:8050 --workers 1 --threads 4
```

Open `http://127.0.0.1:8050/`. The portal mounts the app at `/setac-2026/`.
Enter the presentation password to unlock the deck. The password gate also covers
presenter notes, Dash callbacks, assets and exports, including standalone mode.
The deployment stores a salted scrypt verifier; `SETAC_2026_PASSWORD_HASH` can
override it. Session cookies are scoped to this presentation, HttpOnly and Secure
over HTTPS. The single-worker server renews sessions after a restart or deployment.
Use the arrow keys, Page Up/Down, space bar, or navigation buttons. Navigation
stops at main slide twelve; **Backup slides** opens the appendix separately.
Keyboard navigation yields to focused inputs, sliders, buttons and links.

The `/presenter` route opens notes, the speaking plan and a 12-minute timer
in another tab; its footer button has been removed. Notes follow slide changes in the same browser. The timer starts manually.
Each main slide has a short audience-guidance cue; detailed assumptions remain
available in an expandable section. The cues specify one visual comparison or
interaction to prioritize on each of the detailed slides.
Direct slide links use zero-based fragments, e.g. `#slide-9` for pulse equivalence.

Slide two combines the research question with the broader CDR motivation:
different uptake schedules, storage duration and possible re-release, and
life-cycle emission dates. The qualitative examples are based on
[IPCC AR6 WG III, Chapter 12](https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-12/),
Cross-Chapter Box 8 and Section 12.3. BECCS and DACCS remain the only quantified
cases. This replaces the repeated system diagram without adding a slide.

Slide five has four plots. The left panel selects GMST, CO₂ emissions or
population and World or Northern Europe (ENC). GMST is global, so selecting it
resets the region to World and disables the regional option. The two scenario
trajectories span 2020–2100. Switching SSP2-NPi / SSP2-PkBudg1000 highlights that
trajectory and updates the three market-mix plots to its right. The rightmost
selector chooses steel, cement clinker or truck transport. Hover for exact
values. Mixes show Northern European snapshots every five years from 2025 to 2050,
including 2035, 2040 and 2045 extracted from the original scenario packages.
Technology shares are not interpolated.

Slide seven introduces TRAILS with 3D annual technosphere and biosphere stacks,
and a dated supply-graph schematic adapted from the original `lca_time` artwork.
It explains that remaining demand at the routing frontier is solved in the annual
background, and that the result retains activity, elementary flow and year.

Slide eight stacks uptake, energy, CO₂ and stack emissions, materials and other
supply-chain contributions. Both panels start at 2000 and include the complete
regrowth profile through its final annual bin. Each has a red cumulative net GWP100 line on a
secondary right-hand axis, including upstream contributions before 2000. Both
cases use the same annual and cumulative scales, with their zeros aligned.

Slide ten uses a three-handle slider spanning **2000–2300**. The handles select
the window start, reference-pulse year and window end, initially **2020, 2030
and 2100**. They move in five-year steps and stay at least five years apart.
The curve, scores, settings, interpretation sentences and 2100/2300 comparison
update together. One sentence for each CDR system expresses its score as a
one-off CO₂ removal in tonnes, for the selected window and reference year.
Positive scores are described as warming equivalent to an emission.
A comparison
endpoint at or before the selected reference pulse is marked unavailable.

Slide eleven concludes with four takeaway sentences on the left. The right
returns to uptake, storage and emissions with an outlook for biochar, enhanced
weathering and ocean alkalinization, followed by the thank-you message,
Romain Sacchi’s name, PSI affiliation and email address. These future applications
would require their own inventories and uptake/release profiles; they are not
new results or changes to the current storage assumptions.
A frame above the takeaways reports net tonnes of CO₂ stored needed for three
assessments: current static LCA (2025, SSP2-NPi) and prospective static LCA
(2030, SSP2-PkBudg1000), each targeting −1 t CO₂-eq GWP100, then time-explicit
LCA targeting −1 t CO₂-pulse-eq, for both systems. It divides −1000 by the
corresponding kg-equivalent-per-net-tonne scores.
All scores include life-cycle GHG emissions and the modeled credits; the
reported tonnes measure physical CO₂ storage needed to meet those climate targets.
GWP100 uses the two static snapshots; pulse equivalence uses the 2030 cohort
with the default 2020–2100 window and 2030 reference pulse. These are linearly scaled net-storage
amounts after transport loss, not gross capture or forest uptake.

## PDF fallback

**Export PDF** prepares all twelve slides with fully rendered figures and opens
the browser print dialog. Select Save as PDF, landscape, no headers/footers,
and background graphics enabled. The document uses the same 16 × 9 inch page
format as `lca_time`.
The suggested upload filename is **`1.01.T01_Romain Sacchi.pdf`**.

The export uses curated default views, independent of live controls. In
particular, the pulse slide uses a 2020 window start and 2030 reference pulse,
with the selected 2100 endpoint and a 2300 comparison. The premise slide shows
World GMST and electricity, district/industrial heat and steel mixes under
SSP2-PkBudg1000. The default PDF contains twelve
pages; select **Include backup** for fourteen. Forest sensitivity is absent from
the main deck and default export.

For a reproducible browser check and PDF artifact:

Set `SETAC_2026_PASSWORD` in the shell before running the browser check; the
script reads it to authenticate and does not write it to the report.

```sh
venv/bin/python apps/setac_2026/scripts/browser_check.py \
  --url http://127.0.0.1:8050/setac-2026/ --output build/setac-2026
```

Use `/` as the URL path when running this app alone. If Playwright's bundled
Chromium is unavailable, the script can use an installed Brave browser or an
explicit `--browser` executable.

## Narrative and pacing

| Slide | Content | Time |
| --- | --- | --- |
| 1 | Title and motivation | 0:20 |
| 2 | Can including time change LCA conclusions? | 0:40 |
| 3 | BECCS and DACCS: material, energy and CO₂ flows | 0:45 |
| 4 | BECCS has the lower GWP100 score in 2025 | 0:55 |
| 5 | Future electricity, heat and material supply | 0:40 |
| 6 | CDR scores with 2025, 2030 and 2050 backgrounds | 0:40 |
| 7 | TRAILS: matrices and supply chains through time | 0:35 |
| 8 | When do emissions and CO₂ removals occur? | 1:10 |
| 9 | GWP100 does not distinguish emission dates, but radiative forcing does | 1:20 |
| 10 | Comparing CDR with CO₂-pulse equivalents | 2:25 |
| 11 | Conclusions: timing matters for CDR | 0:55 |
| 12 | Data sources and model versions | — |

The planned live interaction is the slide-10 endpoint, from 2100 to 2300;
all other controls remain available for questions. Slide 3 follows the two
physical routes, slide 5 uses electricity as its single worked example, slide 6
follows net-score diamonds, and slide 7 follows one dated supply-chain path.
These timings remain a rehearsal target rather than a measured delivery time.

Slide 8 explicitly annotates the standing-forest reference and regrowth timing,
and labels cumulative GWP100 as an accounting sum with its final totals. The
conclusion distinguishes the temporal inventory from the climate criterion:
for the same dated inventories, GWP100 favours BECCS, while integrated forcing
over 2020–2100 favours DACCS. The closing storage table names the 2030 reference
pulse and describes metric scores rather than a common physical-removal target.

The GWP claim is scoped to a fixed-calendar climate question. Standard GWP100
remains calculable, but its total does not distinguish the dates of emissions
and removals. Slide nine explicitly shows the coupling from annual TRAILS gas
inventories to the FaIR climate model and the resulting radiative forcing.
Gas identities and emission/removal years are retained; FaIR evaluates the
project inventory alongside the background scenario. The response is shown
under the title “GWP100 does not distinguish emission dates, but radiative
forcing does”. Pulse equivalence matches integrated forcing over a declared window, not the full response trajectory or
physical storage. See [IPCC AR6 WG I, §7.6](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/)
and [FaIR's model description](https://doi.org/10.5194/gmd-14-3007-2021).

## Regenerated results

The SETAC results were regenerated on 14 October 2026 using
`trails_remind-eu_SSP2-PkBudg1000.zip` from premise 2.5.4 and TRAILS 1.1.1.
The original premise 2.4.9.1 NPi background remains the comparison; both sets
of static scores use the regenerated foreground. The package, input and output
hashes, versions and source commits are recorded in `data/regeneration.json`.

`results.py` loads the shared result reader into an isolated module with its own
paths and caches, reading SETAC's `data/processed/`. The longer `lca_time`
presentation and its data remain separate. The original
[data contract](../lca_time/data/README.md) documents the inherited accounting
and file schemas. Licensed matrices and foreground workbooks remain local.

The new package already dates spruce uptake after harvest. Its native annual
offsets and weights are retained without the old additional 83-year shift.
TRAILS rounds the package's half-year offsets to calendar-year bins; the final
BECCS bin is 2131. The physical functional unit, standing-forest reference,
construction/operation/end-of-life schedule and routing depth remain as in the
reviewed comparison. BECCS retains its explicit foreground timing treatment;
DACCS retains generic background distributions from the new package.
Its nonzero inventory extends to 2173; both timeline panels now extend to 2180.
The annual and cumulative vertical scales retain aligned zeros and show the
complete positive and negative stacks.

This rebuild also incorporates TRAILS' signed-uptake correction
(`de32b19`, 8 September 2026). Previously, the FaIR inventory mapping took the
absolute value of resource uptake, incorrectly treating avoided uptake as
additional removal. A controlled comparison using the **same new inventory**
and changing only that mapping gives BECCS −427.61 with the legacy mapping
versus −219.01 kg CO₂-pulse-eq with the correction. For DACCS the corresponding
values are −792.54 and −792.05. This explains nearly all of BECCS's change from
the previous deck; the changes must not be attributed solely to the new package.
The diagnostic script is `scripts/diagnose_fair_sign_change.py` and its results
are recorded separately in `data/regeneration.json`. The presentation uses only
the corrected calculation.

At the default 2020–2100 window and 2030 reference pulse, the new pulse
equivalents are −219 (BECCS) and −792 (DACCS) kg per net tonne stored.
Extending the window to 2300 gives −823 and −889. The former ranking reversal
at 2300 no longer occurs; DACCS has the lower pulse equivalent at both endpoints,
while full-cohort GWP100 favours BECCS (−976 versus −911 kg CO₂-eq).
The speaker cues and conclusions follow these regenerated results.

The slide-8 audit separates energy contributions by the sign of each
characterized flow/year/root, before those flows are netted into a root score.
Activities have already been summed within each flow, so these are not gross
activity-level emissions. `data/processed/energy_flow_signs.csv` retains the
audited flow contributions; annual root totals reproduce the published energy
scores within 0.000002 kg CO₂-eq per net tonne. DACCS energy totals +236.69 and
−189.59 kg CO₂-eq, net +47.10. The negative electricity contribution in 2050
is entirely `Carbon dioxide, in air`: upstream uptake can occur after DACCS
operation ends. The chart distinguishes Energy (+) and hatched Energy (−).

`pulse_integration_audit.json` records an additional check using direct
trapezoidal integration of fresh FaIR ensemble runs, independently of TRAILS'
pulse-metric and grid helpers. It reproduces BECCS −219.005 at a 2100 endpoint
and −537.828 at 2140. A tenfold smaller inventory perturbation changes these
by just 0.014 and 0.036 kg. The old deck gave −428.696 and −756.828 at those
respective endpoints; comparisons must hold the endpoint fixed. The 2030
reference pulse and 2020 window start are the same in this check.

The subsequent `beccs_carbon_balance_audit.json` checks the physical explanation
using fresh FaIR runs for separate inventory components. Per net tonne stored,
forest uptake is −1,143.118 kg CO₂, residual stack CO₂ is +114.312 kg, and
transport loss is +28.807 kg: the direct balance closes to −1,000 kg. The full
inventory's net CO₂ is −987.369 kg, while GWP100 is −975.692 kg CO₂-eq.
Foreground regrowth has a mass-weighted year of 2080.58, with 89.06% occurring
by 2100. Under the standing-forest reference, historical growth cancels; the
additional atmospheric withdrawal is represented by future regrowth.

For the FaIR configuration giving the median full result in 2020–2100,
the pulse-equivalent components are −392.131 (regrowth), +127.217 (residual
stack/transport CO₂), +14.573 (other CO₂), and +31.327 (other climate-active
species), in kg CO₂-pulse-eq per net tonne stored. Their sum differs from the
full −219.005 result by only 0.008 kg due to nonlinearity. This uses a common
configuration, not a sum of independent component medians. A diagnostic that
moves the same regrowth mass into 2030–2049 gives −843.066; it changes the
physical timing assumption and is not used in the presentation. Thus the low
default equivalent reflects delayed uptake within the chosen window, rather
than a missing capture quantity or an incorrect tonne normalization.

Slide 8 offers **Stacked areas / Unstacked lines** for both cases. The data,
axis ranges and cumulative GWP curves are identical in both views. The PDF
defaults to stacked areas. Explanatory text below the plots has been removed;
the scientific explanation remains in the presenter notes.

Reproduce with a Python environment containing TRAILS and the original local
calculation project (source commit recorded in the manifest):

```sh
python apps/setac_2026/scripts/regenerate_results.py \
  --source-project /path/to/FSLCI_workshop_2026 \
  --package /path/to/trails_remind-eu_SSP2-PkBudg1000.zip \
  --workspace build/setac-regeneration
```

The script stages an isolated calculation workspace, rebuilds the foreground,
static contributions, temporal inventories, FaIR responses, reference pulse,
pulse-equivalence grid and market mixes, then validates and copies aggregate
outputs into the app. `--steps` supports resuming stages. Each cohort's GWP and
FaIR outputs use one LCI solve; the grid reuses a hashed species inventory.
The default pulse equivalents are independently checked against TRAILS'
public `run_fair_co2_pulse_equivalents` function. Browser/PDF checks follow.

- System-flow slide: original `case-pathways.svg` artwork annotated with selected
  operating flows from the rebuilt `system_inventory_2025.json`. Physical
  storage is distinct from the subsequent life-cycle GHG score.
- Static snapshots: 2025, 2030 and 2050; SSP2-NPi and SSP2-PkBudg1000.
- IAM context: `data/scenario_context.csv`, a 129-row extract of REMIND-EU
  indicators from the existing scenario explorer's premise 2.4.9 export.
  The adjacent JSON records its source path, hash and premise commit. Source
  values retain °C above 1850–1900, tonnes CO₂/year and million people; chart
  units convert emissions to Gt (World) or Mt (ENC), and World population to
  billions. GMST is the global MAGICC7 median, distinct from the project-level
  FaIR responses later in the talk. The ENC NPi CO₂ series has no 2100 source
  row: it ends at 2090 and is not extrapolated or filled with zero.
  The regenerated package's encrypted IAM input hash matches the audited
  original input, so these scenario indicators remain applicable.
  Regenerate with `python apps/setac_2026/scripts/extract_scenario_context.py`.
- Mixes: `data/sector_mixes.csv`, from premise-generated ENC markets at
  2025, 2030, 2035, 2040, 2045 and 2050. The original source-project extractor
  reads each year directly from the reviewed packages; it preserves the original
  market selection and technology classification. All 360 shares were checked
  against the previous extract and are unchanged in the regenerated package.
  `data/sector_mixes.json` records package and extractor hashes, version metadata
  and provenance. Regenerate using the `mixes` step above.
  Display categories below 1% in every sector snapshot across both pathways are
  combined into Other, retaining all shares. Electricity uses high-voltage supply;
  heat uses the single `market for heat, district or industrial` with reference
  product `heat, district or industrial`, in MJ. The export does not distinguish
  the two uses. This is not the DAC heat-pump inventory.
  The steel check in `data/steel_mix_audit.json` traces the ENC PkBudg1000
  gas-based DRI share from the encrypted IAM production file through the original
  premise mapping and exported market: 0% in 2025 and 17.894% in 2030
  (1.5893214 / 8.8817016 Mt/year). NPi remains at zero in both years. The jump
  is present in the source scenario; it is not interpolation or a plotting error.
  These modelled shares do not establish a plant-level deployment forecast.
- The current-static bars stack process contributions on either side of zero,
  with diamonds marking the net GWP100 scores. BECCS uses the reviewed
  foreground-step attribution; DACCS uses regenerated activity contributions
  and the long deck's process classification. Each bar sums to its source score;
  activity and biosphere-flow attributions are never added together.
- Prospective bars: separate BECCS / DACCS panels, with two scenario stacks per
  background year (NPi hatched, PkBudg1000 solid). These use the static activity
  attributions for every year, since the detailed foreground-step attribution
  is only available for 2025. Each grouped category preserves positive and negative
  entries separately; the source Other remainder is included. Every stack closes
  to its static score. These are snapshots, not lifetime plant-cohort results.
- TRAILS introduction: vector cube and network geometry adapted from
  `lca_time/assets/premise-trails-handoff.svg`; the graph remains schematic.
  Rebuild the two standalone SVGs with
  `python apps/setac_2026/scripts/build_trails_visuals.py`. The concepts were
  checked against `/Users/romain/GitHub/trails` (source 1.1.1), also used for
  the regenerated calculations.
- Temporal and FaIR: complete 2030 cohorts; SSP2-PkBudg1000.
  Energy retains positive and negative elementary-flow scores separately;
  other categories retain positive and negative annual root scores separately.
  Uptake contains only explicit forest regrowth and DAC; energy includes biomass,
  electricity, compression and avoided energy. CO₂ and stack emissions includes the whole
  residual stack branch and CO₂ transport losses; individual stack gases are not
  separated in this branch-level GWP table. Materials includes chemicals, sorbent, construction and
  related end-of-life branches. Bundled pipeline/storage and remaining branches
  stay in Other supply chain. Upstream biogenic uptake stays in its source category.
  The forcing display uses the pointwise median of total all-gas perturbations
  across the same 841 FaIR configurations used for pulse equivalence. Gases are
  combined within each configuration before taking quantiles. The pulse metric
  integrates and divides within each configuration before taking the median;
  it remains distinct from a ratio of areas under the displayed median curves.
  FaIR's actual half-year time coordinates are preserved (1940.5–2299.5 for
  this display), without integer rounding or an artificial zero at 2300.
  `scripts/audit_energy_and_pulse.py --step pulse` writes the total-response CSV
  and its provenance alongside the independent pulse checks. Raw configuration
  arrays remain in the local calculation workspace for verification.
- Normalization: one physical net tonne stored after transport loss, with
  supply-chain GHG emissions retained in the numerator.
- Pulse equivalents: selectable window start, reference-pulse year and window
  end in five-year steps within 2000–2300, defaulting to 2020 / 2030 / 2100.
  The reference pulse stays strictly inside the window. The underlying FaIR
  trajectories span 1940–2300; choosing a later window excludes earlier response from the metric,
  without modifying the inventory or trajectory. Pre-operation contributions
  are inherited upstream timing, not early plant operation.
- Pulse values come from the regenerated configuration-first 841-member ensemble
  grid, not ratios of the median display trajectories.
- The forest sensitivity is the existing illustrative GWP-only screen. It is
  available in backup and is not propagated to FaIR or pulse equivalence.

The closing and sources slides acknowledge the Horizon Europe UPTAKE project,
[grant agreement 101081521](https://cordis.europa.eu/project/id/101081521).
The adjacent EU emblem is the unmodified high-resolution colour reproduction
from the [European Union's official flag downloads](https://european-union.europa.eu/principles-countries-history/symbols/european-flag_en),
stored locally as `assets/eu-emblem.jpg` for offline PDF export.
