# Seoul National University · time-explicit LCA

For the complete task brief, accepted decisions, portability details and current
continuation state, read [the Codex handover](../../CODEX_HANDOVER_SEOUL_2026.md).

Deployment consumes tracked public artifacts only. Cement utility labels are
the rounded display values in `data/cement_process_display.json`; runtime does
not read the research-only CCUS capture-utility assumptions. The unused legacy
CCUS pathway SVG route has been removed. Check a clean checkout when validating
portability, so ignored local research files cannot hide missing dependencies.

Final geography decision (29 October): retain **REMIND-EU and the existing
Northern European case setup**, with each case's original documented location,
inventory and results. The proposed move to South Korea and IMAGE build are
cancelled; no Korean recalculations remain pending.

Latest sequence: **23 core + six backup slides**, **27/33-page core/full PDFs**.
New **slide 2** introduces Romain with the supplied portrait, confirmed Scientist
role at PSI, a 2012/2018/2019 education/career timeline, a Switzerland map
locating PSI near Villigen, research interests, four collaborative GitHub
projects (with the original EDGES logo) and selected publications. `bio.py`, its scoped CSS and `data/bio_sources.json` hold the content,
layout and provenance. It has one minute, taken as 15 seconds each from cover,
response, pulse-equivalence and workflow; the 70+20-minute plan is unchanged.
Later historical revision sections may use the pre-introduction numbering.
The former slides 20–22 (coastal explanation, ERW sensitivity and inventory
lenses) were removed. The redesigned workflow is slide 21, the practical
resource guide is 22, and the results/thank-you slide is 23. The separate
discussion slide was also removed; its 20-minute slot uses the final table
as a backdrop. The 70+20-minute plan is retained by
giving their 9.5 minutes to the existing clocks, metrics discussion, four-case
climate comparison and workflow.

**Slide 20** applies area matching to the four actual stored case responses.
Each solid curve has a dashed, dated CO₂ pulse with the same signed area and
an approximate kg CO₂-pulse-eq readout. Three date handles retain the default
2020–2100 window / 2030 reference pulse. **How the comparison works** opens
first, showing the four response → area → reference-pulse mappings; the second
tab contains the interactive examples. Both views are exported to PDF. These are illustrative matches of
displayed median curves, not configuration-first ensemble equivalents. ERW
uses newly generated reference curves under its own SSP2-EU21 climate variant;
the other cases use their released SSP2 reference. Existing project results
are unchanged. The thank-you slide now summarizes current/future/time-explicit
GWP100 scores and these pulse-equivalent matches for all four native services,
using the SETAC table/contact/funding composition.
The closing table uses **2025 current / 2035 prospective** scores, labels each
operation period beneath the time-explicit score, and ends with three short
takeaways; its pulse window/reference are in the column header.
Its last column gives gross capture / eventual ERW uptake needed to match the
forcing area of **1 t removed in 2030 over 2020–2100**: approximately
**1.32 / 4.67 / 1.20 / 1.44 t** for DACCS / BECCS / ERW / cement+CCS.
It scales the stored curves using unrounded pulse equivalents and accounts for
capture-to-storage losses. Cement's effect is avoided emissions relative to
equal-clinker BAU; ERW uses gross uptake potential. This remains an illustrative
linear curve match, with native project dates/backgrounds retained.

Slide 22 explains how to use each resource, with a task, purpose and first
step, plus verified links into the official premise/TRAILS/FaIR guides and the
ERW source evidence. The audience footer no longer shows the presenter link;
open `/seoul-2026/presenter` directly for speaker bullets and timing.
The first card also introduces Brightway for modelling the foreground system
and its boundaries, with a direct link to the official introductory tutorial.

**Slide 19** has a branching IAM → premise/TRAILS + climate-background diagram and a
shared two-handle calendar slider from **2030 to 2200**, initially **2030–2050**.
All four x axes and the
signed integrated-forcing values above the plots update together, with fixed
y scales. Areas use pW·year/m², exact interpolated window boundaries and the
stored plotted curves; they are not GWP100 or ensemble pulse equivalents.
A branching diagram makes the shared scenario explicit: one IAM node feeds
premise → future suppliers → TRAILS dated project emissions, and a second
branch of future background GHG emissions. Both enter FaIR, which derives gas
concentrations and compares with-project against without-project. The added
text ribbon was removed at the user's request.
Cement retains its 2035 start, while the other cases start in 2030. Native
inventories and stored climate responses are unchanged. PDFs use 2030–2050.

The **slide 17** is a four-minute discussion of what fixed GWP100 loses
when greenhouse-gas events are dated. Two equal fossil-CO₂ emissions in 2030 and
2080 have the same score but different 100-year accounting windows around a
common 2100 endpoint. A **2 × 2 grid of four timelines** replaces the main graph
and three-box layout. Emission dates and moving assessment windows are now
combined in box 1, removing the overlap with the old box 3. The four diagrams
cover that shared-endpoint question, immediate versus delayed CO₂ removal with
the same zero aggregate, gas persistence hidden by equal GWP100 scores, and changing atmospheric
backgrounds versus fixed CH₄/N₂O GWP100 factors. All are visible in the
live lecture and PDF export. Arrows represent CO₂ pulses, and shaded bands mark
elapsed time or accounting windows. Box 3's methane-like/CO₂-like forcing shapes
have equal illustrative 100-year areas and different pulse masses; they are
schematics, not fitted gas responses, temperature curves or FaIR results.
Concentration paths are indexed illustrations, not REMIND forecasts; speaker
notes distinguish fixed-reference reporting from scenario-specific climate response.
Five speaker bullets and primary IPCC/Levasseur/Reisinger
references support the discussion. It follows the annual GWP contributions and
precedes the delayed-removal example. The old slide 16 is now slide 17.

There are now **23 core slides and six backups**. The **70-minute teaching +
20-minute open discussion** plan is unchanged: three minutes were reassigned
from the neighboring inventory/climate explanations. Core/full PDFs now have
**26/32 pages**, including all four diagrams on the new discussion page.

Slide 17 starts with **2030 · same year**, a flat forcing response and both
emission/removal annotations visible at 2030. The PDF uses the same selection;
the live controls still reveal the 20- and 50-year removal delays.

Latest structure review: BECCS now uses the integrated captured-and-stored CO₂
activity as its root, with annual displaced heat/electricity upstream. DACCS's
redundant service wrappers and cement's CCS/reference cohort wrappers are
consolidated before running TRAILS. Cement exposes readable production, capture,
fuel, material, heat and storage stages; instantaneous emission bookkeeping
nodes are folded into their activities, while distinct fuel-carbon histories
remain separately named. ERW's direct foreground structure is retained and its
spreading proxy is named explicitly. All selectors now use actual first-level
inputs. `scripts/routing_structure.py` checks dated supplier-demand equivalence
and biosphere preservation; stored LCA/FaIR results are unchanged. The new graph
expansion budget exposes additional physical tiers, so its displayed depth is
not a replacement for the original score calculation's routing settings.

Slide 14 now has a vertical split: scenario/ecoinvent → premise → year-indexed
A/B data package + encoded temporal distributions → TRAILS on the left, and
**actual TRAILS temporal-routing graphs** for all four technologies on the right.
The user explicitly requested the algorithm's output, starting with the
functional unit at **level zero** and branching through **four levels**; the
initial schematic has been removed. The active technology loads its own local
interactive viewer, with dated nodes by default, readable activity-band names
and the functional unit at the bottom. Its branch selector lists physical root suppliers/stages
rather than cohort wrappers and keeps their paths back to the functional unit.
The viewer starts at **levels 0–3** and downloads level 4 only when selected;
the complete export is retained for later switches. Edges now use width 1.25.
The viewer includes depth controls, pan, zoom, hover/click details and a full-window link. An optional activity overview
transparently groups calendar replicas. Graph exports omit coefficients and
private inventory amounts. The PDF uses an actual DACCS graph snapshot.
`data/routing/` contains portable graphs, provenance and print images;
`scripts/export_temporal_routes.py` reproduces routing in the external TRAILS
Python environment. Existing LCA/FaIR results are unchanged. The new cement
routing view uses October's REMIND-EU package because its original September
archive is unavailable; its reviewed foreground and storage normalization are
retained. ERW's graph has depth four, while reviewed scores retain depth one.
The checked manifest is hash-locked by `routing.verified_route_path`; all four
exports were matched against the in-memory graphs for topology, dates and edge
signs. The reviewed graph sizes are 32,216/65,562/44,175/34,097 nodes for
DACCS/BECCS/ERW/cement respectively. **273 repository tests pass** after the method-first/resource-guide revision; browser validation covers all 28 slides
and routing checks at desktop, laptop and mobile widths; the
26/32-page PDFs and speaker notes are refreshed. Recalculation requires external
licensed data and source helpers; runtime viewing is portable. See the latest
handover section for complete source and reproduction details.

Slide 15 now has one combined graph per case: signed **annual areas** on the
left axis and a **thick red cumulative GWP line on the right axis**. The black
annual net line and its legend entry are removed. The cumulative-view selector and separate area graphs are
removed. Axis zeros are aligned; full earlier inventory remains in the running
sum. X-axis ticks show **calendar years only**, ending at **100 years after start**
(2130 for the CDR cases, 2135 for cement).
Area outlines connect the annual points continuously, replacing stair steps
without changing the annual data. All four panels share the **annual scale
−70 to +35 kg CO₂-eq/year** and **cumulative scale −1,000 to +500 kg CO₂-eq**.
The common annual bounds are calculated from visible signed stacks and rounded
outward. The cumulative axis now uses the requested **−1,000 to +500 kg CO₂-eq**
limits, with zero aligned to the annual axis.

Slide 15's temporal palette separates **biogenic uptake**, **avoided fossil
CO₂**, and **avoided biogenic CO₂ release**. Only the direct kiln-carbon part of
the cement clinker stage uses the reviewed fossil/non-fossil score split;
complete upstream effects remain assigned to their supplier activity. Capture
operation, including its avoided-heat credit, now has its own category rather
than appearing as materials/equipment. Kiln fuels join fuel/biomass supply.
Remaining raw-material differences are net **+2.37 kg CO₂-eq/t stored** over
the lifetime, despite small negative year-specific CCS–BAU pieces. The coarse
released stage table does not identify the individual supplier behind each
such piece. All dated totals, normalization and climate results are unchanged.

Electricity/heat areas have explicit **(+)** and **(−)** labels; negatives
use a pale hatched fill. DACCS now uses a reproduced inventory to separate the
positive and negative characterized flows **inside** its electricity root each
year. The earlier sign split of annual net scores hid offsetting effects and
made the positive curve appear to collapse. In 2042, +10.16 and −10.30 kg
CO₂-eq yield the same −0.14 net, despite constant electricity demand. The
portable checked artifact is `data/daccs_energy_signed.json`, reproduced with
`scripts/extract_daccs_energy_signs.py` and validated by `daccs_energy.py`.
The activity label and all annual/net/cumulative totals are retained; upstream
CO₂ origins are not displayed as separate categories. The shared annual scale
now extends to **−70 / +35** to accommodate the opposing contributions.
Other cases retain their source root/stage aggregation. The ERW cumulative
curve has a translucent **timing-scenario range** covering 10/1, 30/5 and 100/5
years of dissolution/air–sea kernel timescale. This is an illustrative envelope,
not a confidence interval: the same total rock, full uptake potential and
supplier inventory are retained. Annual areas and the stored reference climate
curve remain unchanged. The 10/1-year case is visibly labelled **illustrative**.
The timing literature check is recorded on `/erw-review` and in
`data/erw_review.json`; a one-year exponential timescale is not completion of
air–sea equilibration within one year. Longer field timescales are documented.

The visible unit band and panel labels make the **whole-project activity per
1 t CO₂ stored** basis explicit. Source scaling was independently audited:
DACCS/BECCS already divide their lifetime scores by physical stored tonnes;
cement already uses its whole-campaign clinker/storage factor; the complete
ERW campaign totals 1.25 t rock and 1 t modelled eventual gross uptake potential.
ERW's panel retains that distinction. No second normalization or rescaling to
a −1,000 kg CO₂-eq score was applied. The separate ERW sensitivity remains
interactive, with a callback guard preventing absent controls from replacing
the combined slide 15 graphs. All 248 repository tests passed.

Slide 13 now shows **build-up before Start → operation → dismantling**, with
carbon paths below the light equipment strips and the relative-year timeline
at the bottom. ERW now has a **calculated twenty-year supply chain, 2030–2049**:
twenty equal annual batches retain the same **1.25 t total rock / 1 t eventual
gross uptake potential**. Connected amber arrows show each batch feeding
dissolution/alkalinity transport, then delayed atmospheric uptake. Equipment
stage widths and arrow extents are schematic; missing plant construction and
dismantling quantities have not been added. The axis has a break after year 30;
the diagram scrolls internally on mobile and has no tabs.

The new campaign workbook is `data/coastal_erw_campaign.xlsx`, calculated by
`scripts/calculate_erw_campaign.py`. Pinned aggregate results in
`data/erw_campaign.json` feed dated GWP/root contributions, uptake sensitivities,
the backup uptake chart and newly rerun FaIR curves through `erw_campaign.py`.
Each year uses interpolated REMIND-EU SSP2-PkBudg1000 suppliers, with the full
residual background solve at fixed routing depth one. The campaign GWP total is
**−983.7409 kg CO₂-eq** per normalized service; its sum matches twenty independent
annual static calculations within **0.000005 kg CO₂-eq**. Static 2025/2035/2050
snapshots retain the same total rock demand collapsed into the selected year;
other case results are unchanged. Original single-batch files remain provenance.
The review page offers both inventories; the active campaign download is
`/erw-campaign-inventory.xlsx`. Full source/hash and validation details are in
the handover. Speaker notes retain five bullets.

Slide 12's discussion now links both reasons to retain time: emission/removal
dates and an evolving background economy. Its early → later operation band
highlights changing electricity/heat suppliers for the same plant demand; five
speaker bullets move from the fixed-background thought experiment to matching
dated demands with year-specific suppliers. The hint is conceptual, with no
changes to results or the three-minute discussion duration.

Slide 11 now includes **2025, 2035 and 2050**. Contribution bars default to
**PkBudg1000**, labelled beside the selector; selecting NPi changes future bars
and the 2050 totals. Both future scenario nets remain visible as diamonds:
hollow grey for NPi and filled teal for PkBudg1000. The single 2025 reference
retains its documented case-specific source. New points use independently
checked static calculations in `data/static_scenario_results.json`, loaded by
`static_scenarios.py`; reproduction and local source/cache dependencies are
documented in the handover. Existing foreground inventories, temporal cohorts
and climate-response curves are unchanged. Cement remains CCS minus equal-output
BAU per tonne of CO₂ physically stored. All 243 repository tests and the full
31-slide browser/PDF review passed; PDF exports show the labelled default.

Slides 4 and 10 now identify the ecoinvent background visually. All four process
maps shade selected supplier inputs and include an ecoinvent/database key;
foreground design and carbon-routing assumptions remain distinct. Slide 10’s
premise transformation block uses the premise logo and an ecoinvent database →
scenario-updated-suppliers diagram. Original marks are embedded locally, with
source hashes in `data/background_branding.json`. No scientific quantities or
results changed.

Slide 9 now lists all five socioeconomic SSP stories and the five illustrative
AR6 WGI emissions pathways, with short descriptions. A one-to-many example keeps
these two lists distinct; a separate box retains the actual SSP2/REMIND-EU/
NPi–PkBudg1000 lecture settings. The slide introduces the IPCC's assessment role
and its three working groups, with linked primary references. Forcing suffixes
are labelled in W/m², rather than interpreted as temperatures.

Slide 8 now broadens the IAM centre to economy/investment, energy/industry,
land/food/forestry, transport/buildings, water/resources and environmental response.
Coverage and linkages vary by model. A local logo strip identifies REMIND–MAgPIE,
IMAGE, MESSAGEix–GLOBIOM, GCAM, AIM/CGE and WITCH with explicitly labelled model
or team marks. Provenance and exact source hashes are in `data/iam_logos.json`;
no scenario model or project result was changed. The lecture retains REMIND-EU.

Slides 7–8 now separate pathway evidence from IAM mechanics. Slide 7 shows the
stored 2050 emissions comparison, policy cards and concrete supplier implications
for the four technologies. Slide 8 has an icon-based economy–energy linkage,
the shared SSP2 population input and stored MAGICC7 climate-background outputs.
The graphs reuse the original scenario extract; they do not recalculate project
impacts or substitute a newer scenario release. Source-vintage and scope details
are in the notes and handover.

Slide 2 now presents three motivations for retaining time: changing suppliers,
climate timing, and delayed impacts such as potential human toxicity from landfill
leachate centuries after disposal. The third card cites Turner et al. (2017) and
ecoinvent LT guidance. Short horizons or explicit exclusion of long-term flows
can omit these effects; conventional LCA can also include them. The distinction
is preserved in the speaker notes.

Presenter view (`/presenter`) is now limited to timer controls, the slide time
plan and **four or five bullet sentences per slide**, including backups. Click
a row in the plan to select notes without changing the audience presentation;
audience navigation still updates them automatically. The plan shows each
duration and target time range, while the teaching/discussion timer survives
reloads. Authored bullets live in `speaker.py`; detailed scientific context
remains in `deck.py` and the handover rather than being appended to the visible
notes. Separate cues, next-slide text and the notes dropdown were removed.

Slide 4 uses a common electricity / delivered-heat / materials-and-fuels / CO₂
legend, with units and cement's fossil/non-fossil variants. Its DACCS map now
identifies low-temperature solid-sorbent TVSA and separates direct capture
electricity, heat-pump electricity and delivered capture heat. Every diagram
has linked inventory sources, retained on the four separate process PDF pages.

The 29 October teaching revision reuses explanations from all four source
lectures. The standalone reference-system slide (formerly slide 6) was removed
at the presenter’s request; references remain on the process maps and result
panels. Its two minutes were split between those two slides. The deck now has
**23 core slides and six backups**, with a **70-minute teaching plan and a
separate 20-minute discussion**. The teaching material includes IAM-to-inventory
tracing, equipment and carbon clocks, dated supplier inputs, the TRAILS-to-FaIR
handoff, four-case pulse matching and the workflow synthesis.

Cement + CCS now uses **1 tonne of CO₂ physically stored**, after conditioning
and transport losses. Its full stream includes calcination, fuel and capture-
boiler carbon. The 2025 case produces **1.135 tonnes of associated clinker**;
CCS is compared with BAU producing that same clinker output. All cement static
scores, signed contributions, temporal histories and forcing curves have the
matching physical normalization. Each static snapshot uses its own storage
amount; temporal/FaIR use mean storage per tonne clinker across the complete
2035–2064 production campaign. This is unit conversion of the reviewed results,
not a new LCA or FaIR run. `cement_basis.py` validates the derived factors and
public source hashes; `scripts/check_seoul_cement_basis.py` reproduces the
physical-denominator check when local private evidence is available. No private
inventory or engineering workbook is distributed.

All four process diagrams now have outgoing CO₂ arrows leading to an explicit
atmosphere destination. ERW machinery/haulage exhaust is unquantified rather
than inferred from diesel energy or a GWP score. Its service remains 1.25 tonnes
of rock deployed with 1 tonne eventual **gross uptake potential**, not a promise
of net atmospheric removal or geological storage.

The pulse explorer is an explicitly illustrative superposition of +1 t CO₂ in
2030 and −1 t in 2080 using stored median marginal responses. Three dates change
the comparison window and reference pulse, never the physical inventory. It is
not a new four-case configuration-first ensemble calculation. Do not copy the
older `lca_time` full-project climate numbers or long-horizon ranking into Seoul.

Current contribution rule: only **direct foreground CO₂** is labelled fossil or
non-fossil. Supply-chain impacts, including biomass uptake in electricity supply,
are grouped by complete root-supplier LCIA contribution. The displayed result
slides no longer offer all-supply-chain CO₂-origin views. Current/prospective
CDR decompositions use `cdr_static_roots_2025.json` / `_2050.json`; their script
and local-input requirements are documented at the end of the handover.

Guest lecture for Jooyoung Park's graduate LCA course and research group,
30 October 2026. Teaching totals exactly 70 minutes, including three short
discussion pauses. The final results/thank-you slide supports the separate
20-minute open discussion. Six backup slides contain equations and evidence detail.

The same four cases recur in the same order and colours across current-static,
prospective-static, dated-inventory and climate-response views:

| Case | Colour | Native service and reference |
| --- | --- | --- |
| DACCS | Blue | One net physical tonne stored after transport loss |
| BECCS | Green | One net physical tonne stored; standing forest + equivalent market energy |
| Coastal ERW | Amber | Fixed 1.25 t rock total; 20 annual batches in the dated case; 1 t reference uptake potential |
| Cement + CCS | Purple | One tonne CO₂ physically stored; CCS minus BAU for the same associated clinker output |

These are cross-study teaching examples. Their services, references, package
vintages and cohort dates remain explicit. The slides compare what each lens
reveals within each case; they do not present a harmonized technology ranking.

## Run and present

The portal mounts the lecture at `/seoul-2026/`. `/presenter` contains slide-following
speaker notes, pacing, and persistent 70-minute teaching / 20-minute discussion
timers. It is a separate public page, without access control. Notes selection
is passive and does not control the audience deck.

```sh
venv/bin/gunicorn portal.wsgi:application --workers 1 --threads 4 --bind 127.0.0.1:8057
```

Use arrows, Page Up/Down and Space to navigate. The full-screen button uses the
browser's native control. Hash links retain the displayed slide after reload.

The core avoids formal equation slides. Static and temporal matrix equations
and dynamic characterization are in backup. The three discussion pauses ask why
current production conditions are insufficient, why a future snapshot still
misses event timing, and why fixed GWP100 scores do not determine a climate
history. Interactive views compare annual/cumulative inventory,
move a removal pulse, select a shared climate calendar window, and match each
of the four project curves with a dated CO₂ reference pulse.

Export PDF prepares the 23 core slides as 27 pages at their default states, waits for charts
and images, then opens the print dialog. **Include backup** exports 33 pages. Slide 5 expands to four full-size process-diagram pages; slide 20 exports its explanation and worked examples as two pages.
Select Save as PDF, landscape, no headers/footers. The print stylesheet defines
16:9 pages. Live selections reset to the documented PDF defaults.

## Reused teaching material

- IAM workshop: pathway/target-date figure, connected human/natural systems,
  scenario-layer diagram and the premise inventory bridge.
- SETAC: scenario market extracts, reviewed BECCS/DACCS snapshot, temporal and
  total FaIR results, plus TRAILS annual-matrix and routing diagrams.
- LCA-through-time: shell, palette and pulse-response data for the illustrative
  delayed-removal comparison.
- Cement CCS/CCUS webinar: reviewed BAU and CCS results and reusable process icons.
  CCUS remains a source lecture, while the Seoul comparison uses cement + CCS.

Source applications and result bundles are unchanged. `reused.py` selects their
components; `visuals.py` gives the recurring cases a consistent identity;
`comparison.py` reads the source contracts and native services. No scientific
stack is imported by the presentation runtime.

## ERW foreground and new calculations

`data/coastal_erw_temporalized.xlsx` preserves the initial source-normalized
foreground variants. `data/coastal_erw_ei312.xlsx` is the linked calculation
variant: current supplier names and database bindings, medium-voltage grinding,
and duplicate supplier quantities aggregated without losing physical inputs.
The source premise workbook is unchanged.

Nickel remains in ocean water. Its time profile is a conservative
congruent-dissolution mobility upper bound, not a measured mobile fraction.
The assumed atmospheric-uptake profile separates dissolution and air–sea delay.
Retained spreading, haulage, reclamation and site-chemistry limits are recorded
in `data/erw_review.json`, readable at `/erw-review`.

`data/erw_comparison.json` preserves the source 2025/2030/2050 static scores and
original 2030 single-batch inventory/FaIR response using a local ecoinvent 3.12 cut-off
REMIND-EU SSP2-PkBudg1000 package. The foreground import has zero unlinked
exchanges. Fixed-depth-one routing retains complete residual background solves;
static/temporal GWP totals close within 0.001 kg CO2-eq per deployment.
The active dated charts instead use the subsequently calculated twenty-year
campaign described above. Full upstream temporal-routing convergence and coastal
field performance have not been established. Uptake kinetics remain explicit
scenario assumptions.

The ERW live controls perturb only foreground uptake around this calculated
baseline; they do not rerun LCA or FaIR. Changing dissolution duration at fixed
upstream inputs is a timing sensitivity, not a particle-size optimization.
The earlier illustrative fixed 51 kg footprint is no longer used in the deck.

Reproduce with local licensed inputs and the existing environments:

```sh
/opt/homebrew/Caskroom/miniforge/base/envs/premise/bin/python \
  apps/seoul_2026/scripts/refine_erw_inventory.py
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  apps/seoul_2026/scripts/calculate_erw_comparison.py --climate
```

Only compact aggregate results and public foreground quantities are distributed.
The extracted background remains under ignored `build/`. The calculation records
package/workbook hashes, LCIA method, software versions, FaIR input hashes,
linking checks, closure error and temporal scope. No Brightway database is written.

## Verification

```sh
venv/bin/pytest -q
venv/bin/python scripts/visual_check_seoul.py --url http://127.0.0.1:8057/seoul-2026/
```

The browser check visits every slide at 1600×900, checks the four-case order,
notes and timer synchronization, annual/cumulative mode, removal-pulse delay,
response horizon, ERW controls, keyboard navigation and PDF export. It captures
laptop/mobile views and writes the 26-page core PDF under ignored
`build/seoul-review/`. Tests cover mass closure, complete tails, native
references, fixed case order, unchanged comparison cases under ERW controls,
fixed response scales, source hashes and formal equations confined to backup.

## Earlier revision records

The sections below record earlier checks and designs. Their slide counts and
cement units are historical; the current state at the top of this file and the
latest handover section take precedence. Earlier checks: **233 repository tests**
passed; all **31 audience/backup slides** passed browser checks; core/full PDFs
have **28/34 pages**. All 31 presenter note lists fit at 1280×720.

## Visual and metric revision

The core uses a four-case process carousel, one dated timeline and one tool workflow.
Repeated service cards and chart-only pages are consolidated. A carbon-route
atlas introduces native services and references; a qualitative ledger separates
removal from avoided release; the ERW cross-section separates dissolution,
alkalinity transport and air–sea uptake.

The climate section introduces **fixed-window, integrated-radiative-forcing
CO₂-pulse-equivalence**: compare the complete dated inventory response with a
reference CO₂ pulse in the same background scenario over the same calendar
window. Ordinary aggregate GWP100 gives each event its own 100-year horizon;
a common window retains the time remaining after each dated event. Sources:
[Levasseur et al. (2010)](https://doi.org/10.1021/es9030003) and
[TRAILS theory](https://trails.readthedocs.io/en/latest/theory.html#fixed-window-co2-pulse-equivalence).

The interactive +1 t / −1 t toy example shows the area ratio over 2020–2100
against a 2030 pulse: approximately +232 kg for a 20-year delay and +632 kg
for a 50-year delay, despite a zero aggregate CO₂-only GWP100 total. These are
ratios of stored median marginal-response areas, **not** ensemble-quantile
pulse equivalents or new four-project calculations. A full TRAILS equivalent
uses configuration-level ratios before quantile reduction. The four-case
metric diagram is explicitly schematic. Equal integrated forcing need not
mean equal forcing or temperature trajectories, physical tonnes removed, or
permanent storage; background, pulse year and window must accompany the score.

## 27 October review

Slides 7 and 9 now connect actual stored scenario trajectories to project
suppliers and explain Society / Model / Policy with explicit bullets. Slide 11
shows signed activity-type stacks for 2025 and 2050, with net diamonds. Slide 15
shows root-attributed positive/negative GWP100 series using the same colour key.
`contributions.py` preserves signs and checks closure against each source total.

`data/erw_contributions.json` is a new compact extraction from the same ERW
package and reviewed workbook. Static first-tier supplier intensities close to
the original 2025/2050 totals. Depth-one temporal root attribution reproduces
each stored annual total (maximum error about 2.84e-14 kg CO₂-eq). Reproduce
with `scripts/extract_erw_contributions.py` in the TRAILS environment; use its
`--package`, `--foreground` and `--output` flags on another machine. This does
not rerun FaIR or modify the source inventory.

ERW no longer has an apparent twenty-year operating/uptake cutoff. The timeline
shows open-ended dissolution and atmospheric uptake. The main stored reference
remains explicitly labelled as the fast illustrative 10-year / 1-year clock;
the live sensitivity page opens with 100-year dissolution / 5-year lag and a
170-year display. Neither is field-calibrated, and the slow sensitivity does
not change the stored FaIR response. A new technical backup shows the 10/30/100
year profiles and their year-20 uptake fractions, citing Geerts et al. and
He & Tyka (2023), DOI 10.5194/bg-20-27-2023.

Slide 16 separates the CO₂ mass balance from the forcing history, using calendar
years, signed area colours and full axes. Its pulse-equivalent value appears
only with the definition on slide 18. Slide 22 follows evidence → suppliers →
premise → TRAILS → FaIR/metric; slide 25 is the closing thank-you.

The browser script also exports a 31-page `_with_backup.pdf` and captures every
backup page. The presenter identifies discussion/closing by stable key, rather
than assuming the final core page is the discussion.

Final verification of this review: **212 tests passed**; focused Seoul suite
contains 87 tests. Browser QA passed all 31 pages with no page errors, failed
requests or slide-boundary overflow. Both the 25-page core and 31-page full
PDFs were regenerated.

The final thank-you page reuses SETAC's actual `_closing()` composition: the
two-column summary/contact layout, PSI contact block and UPTAKE/EU funding
acknowledgement. Its summary is adapted to the four Seoul cases and teaching
conclusions; the event header thanks Jooyoung Park and the course participants.
The original two-case scaling table, ranking and future-CDR outlook are replaced
with the Seoul material. The source SETAC app remains unchanged.

## 28 October introduction

The new second audience slide, `why-time`, sets up the lecture before the case
studies. It shows life-cycle stages being aggregated and explains why changing
suppliers over a long lifetime and dated climate effects can require temporal
modelling. On-slide references link to Beloin-Saint-Pierre et al. (2014), Müller
et al. (2025), and Levasseur et al. (2010). Speaker notes distinguish event dates
from data vintages and GWP100's existing characterization horizon.

There are now 26 core pages and six backups (32 total). The introduction has
150 seconds; other allocations are shortened to preserve 70 + 20 minutes.
Navigation uses stable slide keys, so subsequent pages shift by one without
misaligning chapters. Current exports are 26-page core and 32-page full PDFs.

28 October verification: **213 full-suite tests passed** (88 focused Seoul tests).
Browser QA passed all **32 pages**; core/full PDFs have **26/32 pages**.

The opening now links directly into the case atlas: slide 3 is “Changing supply
systems and carbon timing: four cases”, with a supply-system/timing pair under
each carbon route. The user-requested sentence below slide 2's references was
removed; the three references are retained.

## Audience footer cleanup

Small explanatory footer sentences are removed across screen and PDF slides by
`editorial.clean_audience_footer`. Bibliographic links, units, chart legends and
compact cohort/timing/reference headers remain. `deck.presenter_slides` carries
the removed context into the speaker notes. A hidden reused `context-note`
output preserves scenario callback functionality. Print selection values use
readable header labels. Scientific result data and pacing are unchanged.

## Slide 4 process carousel

`processes.py` replaces the supply-network map with five-stage foreground maps
for DACCS, BECCS, coastal ERW and cement + CCS. Shared flow keys distinguish
CO₂, materials/alkalinity and energy. Side streams include energy and capture
materials, BECCS energy exports, clinker production and residual CO₂. ERW
separates rock deployment, dissolution/alkalinity and atmospheric ocean uptake.
Diagrams are qualitative; arrow width encodes no quantity. Qualifications remain
in speaker notes. Case tabs, previous/next controls and tab arrow/Home/End keys
work locally without recalculation. PDF export renders one case per page, so
audience navigation now has 25 core slides while core/full PDFs have 28/34 pages.

Process-carousel verification: **89 focused tests passed**; browser QA passed all
32 audience/backup slides with no page errors, failed requests or slide-boundary
overflow. Core/full exports were regenerated and confirmed at **29 / 35 pages**.

Slide 4 now labels physical flow amounts using `process_quantities()`. DACCS
and BECCS reuse SETAC's physical inventory. ERW uses a hash-checked selected
workbook extraction (`scripts/extract_process_quantities.py`). Cement combines
published SI fuel/utility coefficients with the reviewed physical storage
normalization to show a complete stored tonne, including calcination and boiler
carbon. Every material, fuel and capture-utility amount on its diagram uses the
same 2025 stored-tonne basis; associated clinker is an output. Flow widths are
schematic. No scientific LCA/FaIR solve was repeated.

Cement now distinguishes fossil/mineral CO₂ (brown) from non-fossil CO₂ (green),
with atmospheric uptake (teal) and other/unassigned effects (grey) separate.
Process arrows and the carbon atlas use the same colours. Cement result plots
open in the **CO₂ origins** view; **Activities** / **Net only** restore previous
views. These are alternative partitions, never additive. Static origin labels
cover named foreground CO₂; dated labels cover the full released CO₂-flow view.
The combined purple FaIR response remains unsplit because its source has no
origin-resolved curves. Notes document the scopes and unchanged net totals.

Carbon-origin verification: 95 focused tests passed; all 32 audience/backup
slides passed browser checks, including view switches, with no page errors,
failed requests or slide-boundary overflow. Refreshed PDFs contain 29/35 pages.

Slide 5 now presents all four **2025** results as positive/negative activity-type
stacks using one shared palette, common scale and net diamonds. It reuses the
signed contribution reader behind the prospective slide. Cement defaults to
**Activities** on this page, with **CO₂ origins** still selectable; its other
result pages retain their origin-view defaults. Scores and native services are
unchanged. The focused suite contains 96 tests.

Slide 5's CO₂ flow names are now restricted to **fossil CO₂** and **non-fossil
CO₂**, including its cement alternative view. `CURRENT_TYPES` gives these
shared colours; other contributions retain activity/supplier names. Known
foreground CO₂ is separated from activity remainders without double counting.
The original net scores, signs and common scale are preserved. Other slides'
terminology is unchanged; speaker notes document the selected-flow scope.

DACCS on slide 5 now uses its stored full biosphere-flow attribution, so
biomass-related uptake and emissions are both non-fossil CO₂. The former brown
net biomass-supplier segment is replaced by explicit CO₂-flow contributions and
other GHG effects, with no double counting and the same −831 kg net score.
Current chart headings show Northern Europe / generic European coast / Aalborg
and the 2025 snapshot year. Time-explicit operation remains 2030–2049 for
DACCS/BECCS and ERW, and 2035–2064 for cement.

Foreground/root verification: 228 full-suite tests passed (103 focused), and
browser QA passed all 32 slides. Net scores are unchanged; the current and
prospective charts use the same foreground/root boundary and shared palette.
