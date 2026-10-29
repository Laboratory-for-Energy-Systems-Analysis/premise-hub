# Codex handover: Seoul National University lecture

Updated 29 October 2026. This records the task, accepted decisions and working
state so another Codex instance can continue without the previous conversation.
Read this file, then [the app README](apps/seoul_2026/README.md), before editing.

## Latest addition: presenter introduction after the cover

New slide **2**, stable key `about`, introduces Romain Sacchi with his supplied
smaller portrait, user-confirmed **Scientist** position in PSI's Technology Assessment
Group / Laboratory for Energy Systems Analysis, research interests, collaborative
open-source projects **premise / TRAILS / carculator / EDGES**, and three selected
coauthored publications. GitHub repositories, PSI profile, paper DOIs and full
ORCID record are clickable. User explicitly approved those projects/interests;
no personal hobbies or bibliometric counts were invented. The left pane now has a smaller portrait
and a Switzerland map marking PSI near Villigen, with Basel/Zürich references.
A dated middle column shows **2012 MSc / 2018 industrial PhD** (Aalborg) and
**2019 joined PSI**, from the PSI biography. EDGES uses its original unchanged
logo from `edges/assets/permanent/edges_logo_tight_frame.png`. The country
outline is a simplified public-domain Natural Earth boundary. `bio.py` and
`assets/zzzzzzzzzz_bio.css` implement the page. The unmodified supplied portrait
is copied to `assets/romain-sacchi-portrait.png` and embedded for offline PDF
export. Provenance and the older PSI-page PostDoc/current confirmed Scientist
distinction are in `data/bio_sources.json`.

The introduction has **60 seconds**; cover, response, pulse-equivalence and
workflow each give up 15 seconds to keep **70 minutes teaching + 20 discussion**.
Every former slide 2 onward moves forward one number: why-time 3, process maps 5,
TRAILS routing 15, inventory 16, GWP discussion 17, pulse timing 18, climate
response 19, pulse-equivalence 20, workflow 21, resources 22, thanks/results 23.
Counts below are current; numbered descriptions in later historical revision
sections may still refer to the pre-introduction sequence. Stable keys are
unchanged. The new slide fits desktop/laptop/mobile; 153 lecture tests pass.
The full **29-slide** browser/navigation/presenter check passed with zero page
errors or failed requests. After the smaller portrait/map/timeline/logo edits,
31 focused render/timing checks and three responsive browser checks passed.
Both refreshed PDFs (**27/33 pages**) include the completed introduction as
page two, with embedded portrait, map and EDGES logo; speaker notes are current.
Evidence: `build/seoul-review/about-layout-check.json`, `about-export-check.json`
and `about-{1600,1280,390}.png`.

## Current state: four-case pulse matching and closing score table

Current deck: **23 core slides + six backups = 29 total**, with **27/33-page
core/full PDFs** (process diagrams add three pages; both slide-20 views add one).
User removed the
former slides **20–22**: stable keys `coast`, `erw-sensitivity`, `lenses` are no
longer in `SLIDES`. The former slide 23, `workflow`, is now **slide 21**, followed
by the practical resource guide 22 and thanks/results 23. The separate discussion
slide was subsequently removed; its 20-minute timing slot now belongs to the
thanks/results backdrop, with `timing_phase="discussion"`. Synthesis navigation targets
`workflow`. Supporting ERW data/functions remain available for evidence; these
three audience slides have not been moved to backups. Preserve 70+20 minutes:
their 570 seconds were reassigned to clocks +60, GWP discussion +60, four-case
response +120, pulse matching +180, workflow +105 and resources +45. Earlier counts/timings
below describe preceding revisions.

**Slide 20** now shows all four actual stored case responses and an overlaid
dashed CO₂ pulse with the same signed area. The three-date control remains,
default **2020 / 2030 reference pulse / 2100**, now within 2000–2200 to fit all
native releases. Readouts use **approximate ratios of areas of displayed median
curves**, explicitly labelled as illustrative, **not configuration-first
ensemble equivalents**. Their native services and project dates are unchanged.
Moving a reference date changes only the scaled pulse; moving the window
changes both integrated areas and the mass, never the project inventory.
`case_pulse.py` supplies this view and the eight figure/readout callback outputs
plus the shared date label. The older generic `pulse.py` helper remains as
unmodified methodology regression evidence but is no longer the audience view.
The first tab is now **How the comparison works**: a rebuilt Plotly diagram with
four actual project curves → signed-area readouts → four scaled dated pulses.
Each row shares its own vertical scale between the two curves. The second tab,
**Match the four case areas**, provides the interactive overlays and date controls.
PDF exports explicitly include **both views**, explanation first, rather than
dropping the examples after the tab order change. `render_slide(...,pulse_view=)`
and `data-pulse-view` distinguish these two export pages.

Reference consistency is checked rather than assumed:
- DACCS, BECCS and cement use the released `pulse_reference` curves under
  REMIND SSP2-PkBudg1000. Their native half-year coordinates and +1 t mass are
  retained, then normalized per kg. The 2030 curve is checked against **206**
  SETAC per-kg samples after recovering that CSV's truncated half-year labels.
- ERW's reviewed FaIR calculation uses **REMIND SSP2-EU21-PkBudg1000**, a
  genuinely different atmosphere. `scripts/calculate_erw_reference_pulses.py`
  generated **39** matching reference curves (2005–2195 every five years), with
  TRAILS 1.1.1, 841 configurations, Myhre1998, unprescribed temperature, a 1e9 kg
  perturbation, and all four input hashes matching `erw_campaign.json` exactly.
  Only these reference responses were newly simulated; project LCI/FaIR outputs
  are unchanged. Runtime reads the portable aggregate JSON, not a scientific env.
- `data/erw_reference_pulses.json` SHA-256:
  `449ad8f97208481d3377fb60c9fea16f3d169e0f2f04b5180b9ca6a482f6f99d`.
  `data/case_pulse_validation.json` records default areas/masses and conventions.
  All displayed reference/project integration uses exact interpolated boundaries.

**Slide 21 workflow** was rebuilt in `workflow.py` and
`assets/zzzzzzzzzz_workflow.css`: four analyst choices above five connected
stages with native icons and existing ecoinvent/premise/TRAILS marks. It
distinguishes defining, transforming suppliers, dating/solving, simulating
climate, and interpreting the trajectory/metric.

**Thank-you slide 23:** checked the original SETAC conclusion/table in source
and visually (`build/seoul-review/setac-closing-reference.png`). Its right-hand
contact/funding composition is retained. The left pane now has the four cases
and five numerical columns: current 2025 GWP100, prospective **2035** GWP100,
time-explicit lifetime GWP100, approximate CO₂-pulse-eq from slide 20's
default 2020–2100 window / 2030 pulse, and gross CO₂ required for its −1 t
removal match. `closing_scores.py` uses the actual
readers used on each result slide, rather than copied numbers. All GWP values
are kg CO₂-eq per native service; the pulse column is kg CO₂-pulse-eq with ≈ and
“curve match” labels. Cement remains CCS minus equal-clinker BAU; ERW retains
its one-tonne eventual uptake-potential basis and EU21 climate variant. This is
not a controlled technology ranking or a table of configuration-first ensemble
quantiles. `reused.thank_you()` still adapts SETAC without changing source apps.
The time-explicit column now labels **2030–2049 operation** for DACCS/BECCS/ERW
and **2035–2064** for cement, without truncating full life-cycle scores. Three
short takeaway bullets replace the pulse-window context box. The pulse window
2020–2100 and reference year 2030 remain in the column header. Only this closing
table changed its prospective snapshot to 2035; other result views retain their
own defaults and controls.

**Latest closing-table column: gross CO₂ needed.** Match the integrated forcing of
a **−1 t CO₂ pulse in 2030 over 2020–2100**, using each case's existing signed
median-curve equivalent and native background. For pulse equivalent `E` in kg
per native service, scale the complete project by `−1000 / E`; then multiply by
its physical gross captured tonnes per service. DACCS/BECCS use
`process_quantities(...)["gross_capture_t_co2"]` = 1.02880658436214 t, cement uses
`captured_co2_kg / 1000` = 1.068010936431989 t (not the flue-gas inlet), and ERW
uses eventual gross uptake = 1 t (not 1.25 t rock). Retention ratios include
downstream conditioning/transport losses. Display **≈1.32 / 4.67 / 1.20 / 1.44 t**
for DACCS/BECCS/ERW/cement. Use unrounded equivalents for calculation. A positive
project response cannot match removal through positive scaling (`None` →
“Cannot match”). This is linear scaling of stored displayed curves, not a new
FaIR run or configuration-first ensemble statistic. Dates and background variants
remain unchanged. Cement provides avoided-emission benefit relative to
equal-clinker BAU; its captured mass is not atmospheric removal. Labels and
speaker notes preserve this distinction. The left pane is slightly wider for
the six-column table; mobile scrolls the table internally. Numerical evidence:
`build/seoul-review/gross-capture-validation.json`; responsive screenshots and
checks: `gross-capture-{1600,1280,390}.png`, `gross-capture-layout-check.json`.
Verification: **152 lecture tests pass**, including four physical-mass/forcing
area checks; desktop/laptop/mobile layouts pass. Both refreshed PDFs have the
new column (**26/32 pages**), with export evidence in
`gross-capture-export-check.json`; speaker notes are refreshed.

**Resource guide 22** now groups references by four practical tasks: define the
system boundaries/foreground and temporal/climate question, build future suppliers, calculate timing effects,
and adapt an ERW inventory. Every card states the resource's purpose and a
concrete first step. Deep links to premise's first-scenario guide, TRAILS'
quickstart and FaIR's calibrated example were verified against official docs.
Four source-lecture links remain as worked examples. Implemented in
`resources.py` and `assets/zzzzzzzzzz_method_resources.css`.
Its first card now explicitly says to start modelling the system and its
boundaries with **Brightway**, and links directly to the official Brightway25
foreground-modelling introduction alongside Levasseur/IPCC.

The audience footer no longer contains the **Speaker notes + timer** link.
The presenter remains available directly at `/seoul-2026/presenter`; its plan
uses `timing_phase` so the final results slide carries the separate 20-minute
discussion target. Teaching still totals 70 minutes; the final results slide
has the separate 20-minute discussion phase.

Latest verification: **273 repository tests pass** (148 lecture tests). The full
**28-slide** browser check passed with zero page errors, failed requests or
desktop overflow, including the first-tab method view, interactive case matches,
resource guide and closing table. Nine targeted checks at 1600×900, 1280×720
and 390×844 passed; the method diagram and closing table scroll internally on
mobile (`build/seoul-review/final-layout-check.json`). Checks also confirm the
four 2035 prospective values, operation labels, three takeaways, absence of the
audience presenter link, and the final slide's separate discussion target.
Core/full PDFs are refreshed at **26/32 pages**, with both slide-19 views in
order, and `speaker-notes.html` is current. Final screenshots are
`final-pulse-equivalence-1600.png`, `final-sources-1600.png` and
`final-thanks-1600.png` under `build/seoul-review/`.

## Climate response: current slide 19 calendar window and integrated forcing

Slide 19 (`response`) now uses **one branching diagram**, replacing the
rejected added text ribbon. A single **IAM scenario** node splits into:

- **premise → future LCA suppliers → TRAILS → dated project emissions**;
- **future background GHG emissions**, explicitly from that same scenario.

Both arrows enter **FaIR**, which calculates **gas concentrations** and compares
with-project against without-project, then outputs the climate response.
`methods.fair_handoff()` builds a native SVG with unchanged embedded premise
and TRAILS marks; `assets/zzzzzzzzzz_climate_response.css` styles this slide.
The SVG scrolls internally on mobile. Compact laptop spacing and smaller plot
axis titles preserve chart space. Scenario backgrounds remain emissions-driven,
not prescribed-concentration runs. Notes distinguish this consistency rule from
the retained native case variants, including ERW's EU21 climate background.
No inventories or project climate outputs were rerun or silently harmonized.

Branching-diagram update: **30 focused tests pass**; live slide 18 fits
1600×900, 1280×720 and 390×844 without horizontal page overflow. Evidence:
`build/seoul-review/fair-branches-check.json` and `fair-branches-{1600,1280,390}.png`.
Both refreshed PDFs (**26/32 pages**) contain the diagram and no added ribbon;
the default dates and integrated-forcing readouts remain intact. Speaker notes
are refreshed.

A two-handle `dcc.RangeSlider` replaces the project-age radio buttons. Both
handles select one shared **calendar window from 2030 to 2200**, defaulting to
**2030–2050** at the user's request, with one-year steps and minimum separation of one year. The
four x axes now use actual calendar years; cement keeps its **2035** start and
the other three keep **2030**. `forcing_series()` retains its existing native
age API; `forcing_figure()` adds the appropriate native calendar anchor. No
inventory, stored FaIR response, source date or case normalization changes.

Above every plot is the **signed integrated forcing in pW·year/m²** over that
selected window, with matching translucent fill under the curve. Boundaries
are linearly interpolated on the stored half-year data before trapezoidal
integration. Each y scale stays fixed as either handle moves. These are areas
of the plotted stored curves, not GWP100 scores, CO₂-pulse-equivalents or
ensemble quantiles of integrated responses (cement is CCS median minus BAU
median). Full source trajectories remain present in Plotly; the control changes
the view and integration window. The following slide still introduces proper
configuration-level pulse equivalence.

Implementation: `comparison.response_window`, `integrated_forcing`,
`forcing_figure`, `forcing_area_readout`, `forcing_panels`; `_horizon()` in
`deck.py`; `update_response()` in `app.py` now returns four figures, four area
readouts and the shared window label. Print exports use the default 2030–2050
window. Five speaker bullets and detailed notes are updated. The existing
browser check now uses the range slider rather than the removed radio labels.
The new signed-integration test checks fractional boundaries against known
linear functions, cancellation and rejection of uncovered windows.

Validation: **261 repository tests pass** (136 in the lecture module). The full
32-slide browser run passed with zero page errors or failed requests, and
core/full PDFs were refreshed at 29/35 pages. Targeted checks moved both slider
handles to 2031–2199, verified all four axes/readouts changed while full source
curves and y scales stayed identical, and checked desktop/laptop/mobile layouts
(`build/seoul-review/response-calendar-check.json`). All four area readouts and
the then-default 2030–2200 axes were also checked in the generated print deck;
`response-calendar-print.png` records the print layout. Speaker notes are
refreshed. Local slide link: `http://127.0.0.1:8057/seoul-2026/#slide-17`.
The default was subsequently changed to **2030–2050**: focused integration and
callback tests pass, all four initial axes/areas and both PDFs were verified,
and the slider still reaches 2200 (`response-default-check.json`).

## Latest addition: discussion slide after annual GWP results

Inserted new **slide 16**, stable key `pause-gwp`, exactly between `inventory`
(slide 15) and `delay` (now slide 17). Title: **Same GWP100. Same climate outcome?**
This starts the Climate navigation chapter. Subsequent core/backup slide numbers
advance by one; use stable keys for implementation. Current counts are **26 core,
32 total, 29 core-PDF pages and 35 full-PDF pages**. The unchanged process-carousel
export accounts for three additional PDF pages.

`metric_discussion.py` now uses a **2 × 2 grid of four native SVG timeline
diagrams**. The separate large graph above the cards was removed at the user's
request. All four are visible immediately in live and PDF views:
1. **Same score, different assessment window?** Alternative +1 t CO₂ pulses in
   2030 or 2080, each with +1,000 kg CO₂-eq, now combined with moving 2030–2130
   and 2080–2180 accounting windows, a shared 2100 target and shaded calendar
   period. This merges the earlier redundant boxes 1 and 3, as approved by the
   user. Keep the emission-date and endpoint argument together.
2. **Zero total, same climate history?** +1/−1 t CO₂ in 2030 versus emission
   in 2030 and removal in 2080, both aggregating to zero under fixed GWP100.
   A shaded 50-year gap marks elapsed time, not climate forcing. Use this to
   solicit predictions; the following slide demonstrates the climate response.
3. **Same CO₂-eq, different persistence?** Simultaneous 2030 methane-like and
   CO₂-like pulses with equal illustrative forcing areas over 2030–2130. Their
   masses differ; the methane-like early effect fades and the CO₂-like tail
   persists. Curves are hand-authored schematic shapes, normalized to equal
   100-year areas, not fitted gas impulse-response functions, temperature
   trajectories, FaIR outputs or new physical climate-model calculations.
4. **Same factors in a changing atmosphere?** Schematic indexed CO₂/CH₄/N₂O
   concentration paths against flat CH₄/N₂O GWP100 factors. These are illustrative
   normalized paths, not REMIND outputs, predictions, or gases on a shared physical
   concentration scale. No direction or size of factor changes is claimed.

These now focus on four distinct questions: emission dates/assessment windows,
removal delays, gas persistence and atmospheric backgrounds. After discussing
the overlap, the user approved merging boxes 1/3 and restoring a gas-profile
comparison in the freed box. Arrows are inventory pulses and bars are accounting
windows; only the third card uses schematic forcing curves as described above.
The new fourth card asks about an evolving atmosphere: marginal radiative
efficiencies, the CO₂ reference, gas lifetimes and climate-carbon feedbacks can
depend on background conditions. Speaker notes distinguish fixed-reference
reporting from scenario-specific physical response; do not imply that all GWPs
change in the same direction or that a reporting convention is inherently invalid.
Accessible descriptions preserve that qualification. Scientific distinction:
GWP has a defined integrated-forcing purpose; the critique concerns using fixed
factors as if dated scores supplied a calendar-specific climate trajectory.
This sets up the following pulse-pair demonstration and CO₂-pulse-eq discussion,
without replacing their quantitative examples or calculating new technology
results. References are readable links at the top, with no prose footer:
- IPCC AR6 WGI Chapter 7 §7.6: https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/#7.6
- Levasseur et al. (2010), original dynamic-LCA paper: https://doi.org/10.1021/es9030003
- Reisinger et al. (2011), future GWP changes: https://doi.org/10.1088/1748-9326/6/2/024020

New styles: `assets/zzzzzzzzzz_gwp_discussion.css`. Five speaker bullets are in
`speaker.py`; detailed context is in `deck.py`. This is a **180-second pause**
inside teaching. Preserve 70 minutes teaching plus 20 minutes open discussion:
`inventory` 210→180 s, `delay` 240→180 s, `response` 270→210 s,
`pulse-equivalence` 240→210 s, freeing exactly three minutes. The two earlier
180-second pauses and final 20-minute discussion are retained. All inventories,
climate results, graph files and their hash pins are unchanged.

Validation: all 260 repository tests passed after insertion; the 135 lecture
tests also passed after the 2 × 2 refinement. The previous full 32-slide browser
run passed. Latest targeted checks verify four visible diagrams, removal of the
overview, and both actual PDF export controls, with 29/35 pages, no print overflow
and no browser errors (`build/seoul-review/gwp-discussion-export-check.json`).
The four-card slide fits 1600×900, 1280×800 and 390×844 without horizontal page
overflow. The grid stacks on mobile; the hints are regular diagram cards with
no reveal interaction. `scripts/visual_check_seoul.py` expectations now use four
diagrams and three source links; its full routing checks were not rerun for
this presentation-only layout refinement.
Core/full PDFs and the saved speaker-notes HTML are refreshed under
`build/seoul-review/`. The running local server serves the new slide at
`http://127.0.0.1:8057/seoul-2026/#slide-15`.

Slide 17 (`delay`) now defaults to **2030 · same year**, including the initial
Plotly figure, callback fallback and PDF label/figure. Both **+1 t emitted** and
**−1 t removed** remain visible at 2030, separated vertically, even though the
same-year forcing curve is flat. Delayed cases retain their existing numerical
responses. Implementation: `_pulse()` in `deck.py`, `pulse_timing_figure()` in
`comparison.py`, and `update_pulse()` in `app.py`. The distinct later
CO₂-pulse-equivalence experiment retains its explicit 50-year example.
Targeted verification passed for the default radio/flat curve/both labels,
switching to a delayed response, resetting to same year on return, three screen
sizes and both 29/35-page PDF exports; see `build/seoul-review/pulse-default-check.json`.

## Latest supply-chain structure review: integrated physical roots

User requested that the BECCS captured-and-stored dataset be the functional-unit
activity, with displaced heat upstream, rather than a sibling of a capture
module under a comparison wrapper. They also requested a cement structure review
and readable activity names across all four cases. This is now a **foreground
consolidation before actual TRAILS routing**, not a post-hoc graph relabelling.

`apps/seoul_2026/scripts/routing_structure.py` consolidates only instantaneous
service links, preserves each retained supplier's temporal distribution and
`matrix`/`port` coefficient semantics, and accounts for reference production
amounts (cement cohort production is a reference batch, not one kg). Integrated
roots produce **kg CO2 stored**, demanded at 1,000 kg for the normalized one-tonne
lifetime service. Original foreground workbooks, external library and source
lectures are immutable; changes occur only in the export model's in-memory
matrices. Root date means the project anchor, not that all storage occurs then.

- **BECCS:** capture-and-storage module consolidated into the stored-CO2 root.
  Its exact raw root name is `carbon dioxide, captured and stored, at Nordic
  spruce CHP, post-combustion, LCSS 2026`, product permanently stored CO2.
  The former separate capture-service input disappears. Annual displaced heat
  and electricity remain negative inputs directly upstream, in 2030–2049.
  Biomass CHP operation remains a genuine upstream lifetime service, with its
  forest and equipment clocks intact. Capture assets and consumables now appear
  directly upstream of the integrated root.
- **DACCS:** two redundant wrapper/native service links consolidated into an
  integrated solid-sorbent DAC capture-and-storage root, retaining equipment,
  energy, sorbent, transport and storage schedules and the physical denominator.
- **Cement:** CCS/reference cohort wrappers consolidated into an integrated
  stored-CO2 root relative to matching clinker without capture. Annual clinker,
  capture, fuel, material, heat and storage stages become direct inputs. CCS and
  reference remain separate signed branches. **120 instantaneous elementary-flow
  carrier nodes** are folded into the owning processes with exact biosphere
  checks. **180 historical biomass-carbon carrier nodes** remain because their
  distinct pre-use profiles must not be merged with current emissions. Their
  displayed names identify uptake attributed to refuse-derived fuel, meat and
  bone meal, or cement-bound wood fibre board, with CCS/reference distinguished.
  `scripts/readable_activity_names.py` reads only the fuel-name part of source
  biosphere comments; no private engineering comments/quantities are exported.
- **ERW:** original twenty-year foreground is already directly connected to
  its suppliers, so its graph data/amounts/timing are unchanged. The spreading
  machinery proxy is explicitly identified in the readable activity name.

The viewer uses readable activity names for bands, selections, hover and click,
without internal `ccus | …`, pathway, annual-ID or `dated flow` strings. Original
identities remain in checked graph data. Annual cement variants share layout
bands and selector entries without dropping individual calendar nodes. All
branch selectors now use the **actual first-level inputs**. Root activity names
are visible at the bottom. Displaced BECCS heat/electricity labels receive
readability priority. Node geometry uses reductions rather than spreading large
arrays as JS arguments, so the larger full graphs remain supported.

**Validation:** each new routed foreground is compared against the original
routed zero-lag service tree at the retained supplier boundary, by product/year
and sign. Maximum absolute numerical differences are DACCS 2.27e-13 and
BECCS/cement zero. Direct root biosphere coefficient/profile checks and cement
carrier folding checks pass. Public graph topology, dates and signs match the
actual new in-memory graphs. See `data/routing/topology_checks.json` and each
JSON's `structure_review`. Root attribution and visible depth change; **stored
LCA/FaIR numerical artifacts have not been recomputed**. At a fixed displayed
routing depth the consolidated model exposes additional physical supply tiers;
do not equate its graph depth with the earlier calculation's expansion budget,
or claim complete finite-depth temporal-LCI equivalence from the local checks.

Full graph sizes: **32,216 / 65,562 / 44,175 / 34,097 nodes** for
DACCS / BECCS / ERW / cement. Default levels 0–3 contain
**5,615 / 12,215 / 6,650 / 5,906 nodes**. The lazy level-four loading and width
1.25 edges remain. Current graph JSON and four default PNG previews are pinned
in the updated manifest; ERW's graph JSON hash is unchanged. The exporter accepts
`--output` to stage graphs before publishing; latest staged files are in
`build/seoul-routing-reviewed-public/`, and prior checked exports are preserved
in `build/seoul-routing/pre-structure-review/`. New private routing pickles use
`build/seoul-routing/<case>-integrated-private-graph.pkl`. Compiler revisions
actually executed are recorded per graph; the current implementation additionally
supports non-unit foreground production. Reproduction requires the external
source helpers, reviewed workbooks and licensed package described below.

Completed validation for the structure review: **259 repository tests pass**.
All **31 slides** pass browser checks with zero errors or failed requests; core
and backup PDFs were refreshed with **28 / 34 pages**. Eight additional graph
views at **1280×720 and 390×844** pass readable-name/default-depth/overflow checks;
see `build/seoul-review/routing-structure-viewports.json`. The four-case staged
browser check exercised actual new graph data and level-four loading before
publishing. Final PNG captures also confirm visible displaced heat/electricity
labels in BECCS and meaningful cement process names. Current manifest/code pin:
`d56aff79198e809c5f4b022c9fdf02d8794016ec27ae03b58adf9f7f2f0974b1`.
The locally running server is http://127.0.0.1:8057/seoul-2026/#slide-13.

## Latest graph loading default and edge width

Slide 14 defaults to **levels 0–3**, with level 4 available on demand. The initial
request uses `/routing/<case>.json?depth=3`: a cached exact projection of the
hash-checked full graph. The viewer does not download or render level-four nodes
until the presenter selects 0–4; the full graph is then retained for reuse in
that iframe. Full scientific graph files, routing settings and scores are
unchanged. `routing.shallow_route_json` preserves full provenance and marks the
loaded depth separately. `app.py` serves this lightweight response; the existing
unqualified JSON endpoint still serves the full checked export.

Edges use **width 1.25**, increased from 0.8, in both graph modes. Default-depth
print previews and manifest pins have been refreshed. Initial displayed node
counts are **73 / 6,365 / 6,650 / 1,513** for DACCS / BECCS / ERW / cement,
instead of 423 / 37,519 / 44,175 / 6,028. In the local browser check, initial
views were ready in 0.68 / 1.19 / 0.75 / 0.68 seconds; these are local observations,
not a portable performance guarantee. Four-case network checks confirm no full
JSON request on initial load and exactly one full request when level 4 is
selected, including when switching away and back. See
`build/seoul-review/routing-depth3-report.json`. **134 Seoul tests pass**,
including exact-prefix checks for all four lightweight responses. The core and
backup PDFs are refreshed after this change; their page counts remain 28/34.

## Latest slide 14 viewer refinements

The branch selector now lists **physical root activities**, skipping functional
unit/cohort wrappers. DACCS uses depth-three suppliers (15 choices); BECCS uses
avoided energy at depth one plus direct CHP/capture inputs at depth two (29);
ERW uses depth-one suppliers (10); cement uses depth-two stages (9), grouping
annual variants while preserving CCS versus BAU. These follow the original CDR
helper's physical-branch convention. Selection includes the anchor activities,
all their descendants and their paths back to the functional unit, without
expanding every other branch from those ancestors. Geography/product identities
remain distinct. No exported node, edge, amount, score or routing depth changes.

Graph edges now use width **1.25** (previously 0.8), uniformly in both views.
All four preview snapshots and PDF exports were refreshed for this visual change.
Scientific graph hashes and routing remain unchanged.

**Functional unit is at the bottom in both graph modes**, with supply chains
expanding upward through levels 1–4. Dated mode displays activity-band names at
a readable screen font, with collision handling and additional names on zoom;
full identities remain available on hover/click. Calendar years stay below the
graph. The layout separates activity/product/location identities into bands.
The activity overview remains an explicitly grouped display of the same graph.

Changed files are the viewer template, speaker/detailed notes and browser QA;
all four print snapshots and their manifest hashes were refreshed. Scientific
JSON graph hashes and topology checks are unchanged. The viewer template hash
and branch-choice counts are recorded in `data/routing/manifest.json`.
`build/seoul-review/routing-branch-label-report.json` checks all four branch lists,
visible names, bottom-up orientation in both modes, and connected selected
branches. The 130 Seoul tests pass. Full browser QA passes all 31 slides with zero
browser errors or failed requests. Eight additional laptop/mobile case views
pass visible-name and overflow checks at 1280×720 and 390×844; their report is
`build/seoul-review/routing-upward-viewports.json`. The 28/34-page PDFs and saved
speaker notes have been refreshed. The manifest/code pin after this visual-only
update is `d56aff79198e809c5f4b022c9fdf02d8794016ec27ae03b58adf9f7f2f0974b1`.

## Slide 14 redesign: actual TRAILS routing graphs (latest request)

The user requested a vertical two-pane split. The **left** keeps the complete
IAM scenarios + ecoinvent → premise scenario data → data package with
3D technosphere/biosphere stacks + analyst-encoded temporal distributions →
TRAILS temporal routing and annual solving, with all three project/database
logos. Reuses SETAC's annual-matrix-stack SVG. `branding.py` now also embeds
TRAILS's unchanged existing mark; `data/background_branding.json` records it.

The **right must show the actual output of TRAILS's temporal graph algorithm**.
The first hand-drawn teaching schematic was explicitly rejected by the user.
Start from **level 0: the functional-unit demand**, branching to **level 4**.
Do not replace the actual graphs with flowcharts, timelines or illustrative
branches. Four tabs: DACCS, BECCS, ERW, cement + CCS. The dated view retains every
calendar node and edge up to the selected display depth. View controls can filter depth/branch or transparently
group calendar replicas by activity; this changes only presentation. Pan, zoom,
click/hover metadata and a full-window graph link support dense graphs.

Implementation: `routing.py`, `templates/routing_graph.html`,
`assets/zzzzzzzzzz_routing_split.css`, `assets/zzzzzzzzzz_routing_frames.js`.
Only the active iframe loads. Whitelisted `/routing/<slug>.html`, `.json`, `.png`
endpoints serve the viewer and portable graph data. The viewer uses existing
local vis-network 9.1.2 through `shared/routing-vis.min.js`; no CDN or scientific
Python is needed at runtime. Public JSON retains topology, process/product names,
locations, years and edge signs; **all coefficients/edge amounts are omitted**,
including private cement engineering values. Uniform edge widths; negative
demands are dashed. This is a technosphere activity-demand routing graph;
biosphere event distributions are applied downstream and are not invented as
extra activity nodes. Printed slide uses an actual DACCS graph PNG; core/full
page counts remain 28/34. Five presenter bullets and detailed notes were updated.

`apps/seoul_2026/scripts/export_temporal_routes.py` runs actual
`Trails.temporal_routing(max_depth=4, adaptive_relative_score_cutoff=None)` in
the existing TRAILS Python 3.11 environment. Foreground sources and private graph
pickles stay in ignored build directories; public outputs/provenance live in
`data/routing/`. Existing score tables, LCI and climate responses are unchanged.
Source package is the October REMIND-EU SSP2-PkBudg1000 archive SHA
`bd298b3e30d84adbb9dfe11c87654a318d7b8aed94e0357fa932a6e3dbcf9780`,
already extracted under `build/seoul-daccs-energy-signs/package/`.
`--source-dir` and `--package` accept relocated external sources; defaults are
local reproduction paths. Helpers/workbooks in
`build/setac-regeneration-20261014/` reproduce the checked CDR cohort timing.
Imports share only metadata dictionaries proven exactly equal to avoid repeated
identity scans; the external TRAILS library and all matrices are unchanged.

- DACCS: reviewed foreground + cohort workbooks, 2030, 1/1,944,000 cohort units
  for the 1 t physically stored service; **423 nodes, 1,101 edges**.
- BECCS: reviewed cohort helpers, 1,000 kg storage; retain the 83-year extended
  background coverage for future forest operations. **37,519 nodes, 78,799 edges**,
  activity-demand years 2027–2131; biosphere regrowth years are a separate output.
- ERW: current twenty-year campaign workbook, 1,000 units (1.25 t total olivine,
  1 t eventual gross uptake potential). Use the full 2005–2100 package for
  this four-level routing view: **44,175 nodes, 108,521 edges**, years 2005–2079.
  The reviewed score calculation retains its five anchors and fixed depth one.
- Cement: add an explicit foreground comparison root demanding CCS minus BAU
  for equal clinker, using the reviewed factor 1.2780630126313808 t clinker per
  tonne physically stored. The original reviewed foreground is immutable;
  its augmented copy is `build/seoul-routing/cement-normalized-foreground.xlsx`.
  **The original September archive (SHA a69a4f…) is unavailable locally.** This
  new routing-only view therefore uses October's package with the reviewed
  foreground. It is not the released adaptive result graph and does not replace
  its scores. This difference was disclosed to the user and is in metadata/notes.

Completed and validated: **255 repository tests pass**; full browser QA covers
all 31 slides, four actual routing tabs, depth controls, keyboard tabs, presenter
notes and PDF export, with no browser errors or failed requests. Additional
routing checks cover all four cases, levels and zoom at **1600×900, 1280×720
and 390×844**, without slide overflow. Core/full PDFs were refreshed and have
**28 / 34 pages**. `build/seoul-review/routing-layout-report.json` and the
browser report/screenshots record the checks. The local server remains at
http://127.0.0.1:8057/seoul-2026/#slide-13.

Cement completed with **6,028 nodes / 16,070 edges**, demand years 2005–2100.
The augmented workbook has 1,323 foreground identities, all new relative to the
package, so no existing background caller is overridden. To avoid the importer's
quadratic clearing loop, `import_cement_foreground` partitions untouched timing
records out before importing, restores them afterward and asserts no key
collisions; library and matrices are unchanged. All four public exports were
compared to their private in-memory graph pickles: exact topology, dates and edge
signs match. `data/routing/topology_checks.json` records this independent check.

`data/routing/manifest.json` pins graph JSON and preview PNG hashes, scenario
archive and helper source hashes. Manifest SHA-256:
**d56aff79198e809c5f4b022c9fdf02d8794016ec27ae03b58adf9f7f2f0974b1**.
`routing.verified_route_path` checks this pin and each asset's hash before use.
If regenerating figures or graphs, rebuild the manifest and update its code pin
only after reviewing the changed output. Browser PNG captures use the actual
dated graph at a 720×650 viewport and 2× pixel scale, with interactive help hidden.
The public app and graphs are portable. **Recalculation is not repo-only**:
restore the external source-helper/workbook directory and licensed scenario
archive/descriptor listed above; the source helpers currently live in ignored
build material rather than a separately versioned checkout. Runtime editing or
viewing needs none of those scientific dependencies.

## Latest DACCS diagnosis: separate effects inside electricity, not annual net signs

The presenter observed that DACCS's positive electricity area started high and
collapsed. **The previous visualization split already-netted annual root scores
by sign. It did not separate simultaneous positive and negative effects inside
the electricity supplier.** This hid substantial emissions when biomass-related
uptake offset them. The problem has been corrected using a detailed reproduction
of the original inventory, rather than cosmetically changing the curve.

- Capture/heat-pump electricity demand is **constant in 2030–2049** in the
  reviewed cohort: 58.21478552694843 kWh each year per normalized one-tonne
  lifetime storage service, or 1.16429571054 MWh over that service. This is the
  capture electricity branch; conditioning/transport electricity remains in its
  own responsible supply chain. Do not read the GWP curve as power consumption.
- Within electricity in 2042, **+10.161846** and **−10.304355 kg CO₂-eq** yield
  the original **−0.142509 net**. Positive effects remain **+6.942260** in 2049
  and stop at closure, while modelled negative biomass-carbon effects continue.
  Positive effects also decline through the scenario, but do not disappear in
  2042. Negative characterized flows are dominated by atmospheric CO₂ resource
  uptake and its non-fossil resource correction; positive effects are largely
  non-fossil combustion emissions in electricity supply.
- Correct complete-lifetime electricity components are **+229.5699347** and
  **−189.2842465**, retaining **+40.2856882 kg CO₂-eq/t stored net**. The older
  +86.232445/−45.946757 split below was a sign split of annual net values and
  must not be described as the underlying positive and negative contributions.
- `scripts/extract_daccs_energy_signs.py` reproduces the unchanged original
  fixed-depth-four 2030 DACCS cohort, using the source helpers/workbooks in
  ignored `build/setac-regeneration-20261014/`, original archive SHA
  `bd298b3e30d84adbb9dfe11c87654a318d7b8aed94e0357fa932a6e3dbcf9780`,
  and TRAILS 1.1.1 from the local checkout in the existing Python 3.11 environment.
  It explicitly selects `ecoinvent-3.12-cutoff`; no database, source lecture,
  reviewed result table or shared interpolation cache is modified. Licensed
  matrices/factors stay under ignored `build/seoul-daccs-energy-signs/`.
- The retained factorized LCI is streamed for the ENC medium-voltage electricity
  root. Characterized entries are **first aggregated by root/year/biosphere-flow**,
  cancelling temporal redistribution corrections, and only then separated by
  sign. Do not split individual factor/correction entries before this reduction:
  that would invent large positive and negative effects. Flow identities remain
  diagnostic; the audience plot still shows the electricity activity label,
  not separate upstream CO₂-origin categories.
- The reconstruction matches the original annual electricity net to
  **1.27898e−13 kg CO₂-eq/t stored** maximum. Tiny signed reconciliation preserves
  the original published annual nets exactly. Root sums, whole-plant annual
  totals, red cumulative curves, FaIR results, physical storage denominator
  **1,944,000 t**, and the ERW scenario band are unchanged.
- Portable aggregate artifact: `data/daccs_energy_signed.json`, SHA-256
  **b7d761fee715db86137f54776681f28e35057a1fbe3f6cf06d17b10e5eb69f6b**.
  It contains signed annual electricity scores, constant-demand checks, source
  hashes and characterized flow diagnostic totals, not raw background matrices.
  `daccs_energy.py` checks the pin, original score-table hash, physical denominator
  and every annual signed sum. Runtime presentation needs only these repo files;
  recalculation additionally needs the external original helpers and licensed
  archive at paths recorded in the script/provenance.
- `contributions.temporal_contributions()` replaces only DACCS electricity's
  annual-net root with these two internal signed series. Labels/colours/hatching
  remain. The shared annual scale expands to **−70/+35** to fit the now-visible
  opposing effects; all four panels share it. The cumulative scale stays
  **−1000/+500**, with zero aligned. Other cases retain their source root/stage
  aggregation; gross positive/negative magnitudes are not a harmonized ranking.
  Speaker and scientific notes/README explain the correction and scope.

**251 repository tests passed**, including a near-zero-net 2042 check that still
requires >10 positive and <−10 negative components, original source closure and
constant demand. Desktop/laptop/mobile and speaker fit passed; see
`build/seoul-review/daccs-gross-energy-report.json`. The full browser/PDF review
refreshes the 31-slide screenshots, 28/34-page PDFs and notes HTML. This section
supersedes older claims that the DACCS energy sign split was already complete.

## Latest slide 15: energy signs and an ERW timing-scenario band

The presenter requested explicit positive/negative electricity + heat in DACCS,
asked whether 10-year dissolution/1-year lag is an accepted ERW window, then
requested a shaded uncertainty area. These requests are implemented together.

- Annual electricity/heat traces are named **Electricity + heat (+)** and
  **Electricity + heat (−)**. The latter uses pale yellow hatching; the HTML
  legend matches. The shared key applies across all four panels. Underlying
  signed annual root scores are unchanged, including DACCS's full-lifetime
  +86.232445 / −45.946757 kg CO₂-eq contributions. This is not a new gross-flow
  decomposition inside a supplier and does not expose supply-chain CO₂ origins.
- The ERW **cumulative GWP** curve has a translucent red scenario envelope on
  the secondary axis, computed from **(10,1), (30,5), (100,5)** years of
  dissolution duration and exponential air–sea kernel timescale. Pointwise
  bounds come from `comparison.annual_scores()` and retain all pre-window
  inventory. The twenty annual batches, total 1.25 t rock, 1 t eventual gross
  uptake potential, full reference realization and calculated supplier inventory
  are held fixed. The envelope varies only foreground CO₂ uptake timing.
  **It is not a statistical confidence interval, site-calibrated range, all-source
  uncertainty estimate, or matched grain-size/energy comparison.** The annual
  areas and thick red reference line remain the fast baseline. Stored FaIR
  responses are unchanged; no FaIR rerun is implied by the shaded GWP range.
- Two unstacked `y2` traces, **ERW timing minimum/maximum**, form the envelope;
  the upper trace fills to the lower. The cumulative line is drawn afterwards.
  Trace metadata and figure `timing_envelope` metadata document the scope.
  Shared scales remain annual −60/+30 and cumulative −1000/+500, with calendar
  years only and the previously accepted +100-year visible horizon.
- ERW reference headers now say **illustrative 10 y / 1 y**. The literature
  check confirms no universal combined 10/1-year window: Foteinis et al. (2023,
  doi:10.1021/acs.est.2c08633) selected ten-year dissolution for their 10 µm
  base case. Geerts et al. (2025, doi:10.5194/bg-22-355-2025)
  discuss field full-dissolution times of **10–500 years**, depending on initial
  grain size. He & Tyka (2023, doi:10.5194/bg-20-27-2023) report substantial
  equilibration in **3–4 years** at many sites, **8–10 years** at some, and
  century-scale deep-ocean return tails. These are different quantities from
  this model's exponential time constant; never equate a one-year kernel scale
  with a one-year hard wait, full equilibration, or completion after eleven years.
- Sources were checked on 29 October 2026. Findings/links are in
  `data/erw_review.json` under `timing_evidence`, rendered on `/erw-review`.
  Scientific and five-bullet speaker notes are updated. Implementation is in
  `contributions.py`, `comparison.py`, `deck.py`, `speaker.py`, and the review
  template. No inventories or source scores were changed.

**126 Seoul tests passed**, including sign-preserving energy rendering and an
envelope containing the reference, differing materially during the campaign,
and converging to the same full-horizon net total. Laptop/mobile and speaker
fit checks passed; see `build/seoul-review/erw-envelope-report.json`. All 31
slides passed browser/layout checks; screenshots and the 28/34-page PDFs were
refreshed. Source notes and the review
page retain the broader uncertainty/site-performance limitations.

## Latest slide 15: −1000 limit and separate carbon mechanisms

The presenter requested a **−1000 secondary-axis lower bound**, an explanation
of negative cement materials/equipment, and a split between biogenic uptake
and avoided fossil CO₂. The common annual range remains **−60 / +30**. All
cumulative axes now use **−1000 / +500**, with 500-unit ticks and aligned zeros.
All currently visible cumulative curves fit these limits. The annual range is
still derived from signed stack extrema; the cumulative range is explicit.

The attribution audit found that `cement_type()`'s coarse fallback had put
the entire **capture stage** into Materials + equipment, including an
**avoided-heat-production credit**. This was misleading. The slide-15-only
`TEMPORAL_TYPES` now assigns capture to **Capture operation + heat credit**,
and kiln fuels to **Fuel + biomass supply**. Capture is net **−5.53841 kg
CO₂-eq/t physically stored** over the complete campaign: −17.62633 negative
and +12.08792 positive dated pieces. Independent released static subprocess
tables confirm the heat credit (e.g. −26.05541 kg CO₂-eq/t stored in 2035),
alongside positive electricity, amine, water and other supply contributions.
The temporal export aggregates those together, so do not pretend a separate
annual heat-credit or equipment series was extracted.

Remaining Materials + equipment is the raw-material stage: **+2.37318 net**,
made of **−0.48567 negative** and **+2.85884 positive** year-specific CCS–BAU
pieces. These are modelled counterfactual/time differences, not material carbon
removal. The coarse released export does not resolve individual suppliers for
those dates, and temporal-routing convergence is untested. Do not invent a
physical materials-removal explanation or silently alter the inherited scores.
Audit details are in `build/seoul-review/cement-attribution-audit.json`.

The temporal palette no longer displays **Direct / avoided emissions**. It
separates actual **Biogenic uptake**, **Avoided fossil CO₂** (including mineral
calcination), **Avoided biogenic CO₂**, and **Other foreground effects**.
Avoided biogenic release is explicitly different from newly dated plant growth.
The original static/legacy palettes remain unchanged.

`cement_temporal_foreground.py` loads the unchanged reviewed public
`apps/ccus_webinar/data/public/temporal_carbon_display.json`, pinned to SHA-256
**eed60aa0f8abdf50dd7f845363c2604ddae833d3f33e75ad4471906984c5a313** and
checked against the approved source-bundle hash. Its gross-minus-captured
fossil/non-fossil **characterized scores** replace only the clinker stage's
direct CO₂ portion, CCS minus equal-output BAU. Never infer physical carbon
mass from these scores. A small remaining clinker-root term is retained
separately, including years outside 2035–2064, so annual totals close exactly.
Direct scores reproduce the clinker stage within 1e−4 kg CO₂-eq/t clinker per
year; the largest difference is about 8.28e−5. This is not a whole-system flow
decomposition added to supplier roots. No source release, private workbook,
foreground quantity, GWP total, FaIR response or storage denominator changed.

Changes: `contributions.py`, the new helper, `deck.py`, five authored bullets
in `speaker.py`, tests/browser QA and README. **249 repository tests passed**,
including direct-carbon/annual closure and the attribution-scope checks.
Desktop/laptop/mobile and speaker fit passed; see
`build/seoul-review/cement-attribution-report.json`. The full browser/PDF check
refreshes the 31 slides and 28/34-page exports. This supersedes older secondary
limits, combined-direct labels and capture-to-materials mappings below.

## Latest slide 15: continuous area outlines and common scales on both axes

The presenter requested smoother areas and harmonized primary **and** secondary
y-axes. Annual areas now connect the original annual samples with **linear
segments**, replacing the `hv` stair geometry. Annual sample values, signs,
root closure and discrete cumulative sums are unchanged. This is rendering
interpolation, not smoothing/averaging the inventory or altering uptake kinetics.

`contributions.temporal_axis_ranges()` inspects all four visible signed stacks
and all four running net sums (including pre-window inventory). It pads and
rounds outward to shared bounds: **annual −60 to +30 kg CO₂-eq/year**, and
**cumulative −1,200 to +600 kg CO₂-eq**. Zero is aligned two-thirds up both axes;
the secondary axis remains red and differently labelled/scaled. Bounds are
derived from the data rather than independently autoscaled per panel. Tick
spacing is 20 on the annual axis and 400 on the cumulative axis. X-axis dates,
100-year extent, one-tonne whole-project basis, absent black annual line and
absent selector remain as accepted previously.

Existing numerical/browser checks now verify common ranges, both signed stacks
and cumulative curves fitting those ranges, aligned zeros, and removal of stair
geometry. README and scientific notes are updated; screenshots/PDFs are refreshed
under `build/seoul-review/`. This supersedes older stepped/per-case-axis details.
Validation: **123 Seoul tests passed**; all 31 slides passed browser/layout
checks without JavaScript errors or failed requests, and the 28/34-page PDFs
and speaker HTML were refreshed.

## Latest slide 15 cleanup: red cumulative line only, calendar years only

The presenter removed the black annual net GWP line and its legend entry.
Annual signed areas remain, with the red cumulative line on the right axis.
The x-axis now says **Calendar year** and shows only 2030/2080/2130 (CDR) or
2035/2085/2135 (cement); **Start, +50 and +100 tick sublabels are removed**.
The visible range still ends 100 years after start. Hover labels retain age for
context. Whole-project normalization, data, cumulative sums, aligned zeros and
the ERW modelled-uptake distinction are unchanged. Source, tests, notes and
browser QA reflect this cleanup; PDF exports use the same combined chart.
This supersedes the black-line and two-line-tick descriptions below.

## Latest slide 15: cumulative overlay, calendar years and whole-project unit

The presenter requested removal of the cumulative selector/associated area
graphs, a thick red cumulative line on the annual plots using a secondary axis,
calendar years, and explicit plant-activity normalization to **1 t CO₂ stored**.

- Slide 15 (`inventory`, URL `#slide-14`) now has **one combined chart per case**.
  Annual signed root contributions remain stepped areas on the left axis,
  with the black annual net line. **Cumulative GWP100 is a 4.5 px red line on
  the right axis**, with red ticks/title and a common legend entry. The two
  y-axis zero positions are aligned; their different units/scales are explicit.
  Cumulative sums start from the complete inventory, including years earlier
  than the visible −5-year boundary. Full later tails and source totals remain.
- The relative x-axis remains **−5 to +100**. Tick labels now combine calendar
  year with age: **2030/2080/2130** for DACCS, BECCS and ERW, and
  **2035/2085/2135** for cement. Hover labels include calendar year and age.
- A visible unit band says **“Whole-project activity per 1 t CO₂ stored”**;
  panel services explicitly say **whole project**. ERW instead retains
  **“1 t eventual uptake · modelled”**, because the normalization is reference
  gross uptake potential, not verified permanent storage or net removal.
- The normalization audit confirmed existing source scaling, so **do not divide
  the data a second time or force a cumulative GWP value to −1,000 kg CO₂-eq**.
  DACCS/BECCS CSV rows use the physical `denominator_net_stored_tonnes` fields:
  **1,944,000 t** and **149,394.49520357835 t**, respectively. Every per-tonne row
  was checked against cohort score / physical denominator, and their sums
  against the displayed annual series. Cement already uses the hash-checked
  whole-campaign **1.2780630126313808 t clinker/t CO₂ stored** factor for
  equal-output CCS minus BAU. ERW's entire twenty-year campaign totals
  **1.25 t rock / 1 t eventual gross uptake potential**, not that amount each
  year. Its original campaign results and kinetics are unchanged.
- `contributions.temporal_figure(case)` now has no cumulative-area mode;
  `temporal_panels()` uses that combined figure. `_time_view()` no longer
  mounts `inventory-view` or its radio controls. The obsolete `update_inventory`
  callback is removed. `update_erw()` directly handles the separate ERW
  sensitivity controls and raises `PreventUpdate` when all optional inputs are
  absent, so it cannot replace slide 15 with sensitivity plots. The separate
  sensitivity page intentionally keeps its existing cumulative net plots.
- Other touched files: `comparison.case_heading(..., service=...)` for scoped
  service labels, `speaker.py` (five bullets), detailed notes in `deck.py`,
  `assets/zzzzzzzzz_inventory_overlay.css`, tests, and browser QA. Figure meta
  records the one-tonne whole-lifetime basis and the ERW distinction.

**248 repository tests passed.** Checks include signed-root reconciliation,
pre-window cumulative carry, aligned zeros, calendar-year labels, physical
lifetime denominators and the missing-controls callback guard. Desktop/laptop/
mobile and five-bullet presenter checks passed; see
`build/seoul-review/cumulative-overlay-report.json` and screenshots. The full
browser/PDF run produces `inventory-cumulative-overlay.png` and the usual
28/34-page PDFs. No inventory, FaIR curve, source results or functional-unit
denominators changed during this display revision. This supersedes the previous
two-view slide 15 below.

## Previous slide 15: signed areas and +100-year display limit

Slide 15 (`inventory`, URL `#slide-14`) now uses **stacked areas in both annual
and cumulative views**, replacing the annual vertical bars. Positive and
negative contributions remain in separate Plotly stackgroups, with the same
activity-type colours and black net line. Annual areas and their net line use
step geometry to retain annual bins; cumulative geometry remains linear.
All four x-axis ranges are **−5 to +100 years**. This changes the visible window
only: full source tails and all pre-window inventory remain in the data, totals
and cumulative calculations. No inventory or scientific result was recalculated.

Implementation: `contributions.temporal_figure()`, detailed notes in `deck.py`,
and browser QA checking both modes, signed areas and all four ranges. Screenshots
are `build/seoul-review/inventory-areas-annual.png` and
`inventory-areas-cumulative.png`; the PDF uses the annual default.
The +100 endpoint is explicitly labelled on every chart. **121 Seoul tests
passed**, including complete signed root closure; browser QA exercises both
area views and confirms the same visible range in all four panels.

## Latest slide 13 and ERW: equipment stages and a calculated twenty-year campaign

**This supersedes the previous single-batch decisions below.** The presenter
explicitly requested plant build-up before Start, dismantling after operation,
and a twenty-year ERW supply chain aligned with the other CDR options.

Slide 13 (`clocks`, URL `#slide-12`) retains the uncluttered equipment/carbon
diagram and bottom relative-year axis. Each row now has **Build-up → operating
inputs → Dismantle**. Build-up is visibly before Start; dismantling is after
year 20 (DACCS/BECCS/ERW) or year 30 (cement). Stage widths are schematic: no
unsupported equipment-construction, replacement, retirement dates or end-of-life
quantities have been added to the inventories. The four background supply
chains retain whatever equipment burdens/timing they already contain. The
relative-axis scale break after year 30 remains explicit. The former diamond
marker is removed. ERW has a full 0–20 operating strip, **annual batch** arrows
into a fading dissolution/alkalinity-transport band, then curved arrows into a
separate delayed-atmospheric-uptake band. Open tails are qualitative and are
not a measured completion time or a mass scale. The diagram still has no tabs.

The ERW change is **numerical as well as visual**:

- **2030–2049**, twenty equal annual batches, normalized across the whole
  campaign to **1,250 kg rock / 1,000 kg eventual gross atmospheric uptake
  potential**. Thus the normalized annual batch is 62.5 kg rock; this is a
  service normalization, not a proposed plant capacity. Do not multiply the
  functional unit by twenty or label potential as guaranteed net removal.
- `scripts/calculate_erw_campaign.py` generates the new
  `data/coastal_erw_campaign.xlsx` from the unchanged hash-checked
  `coastal_erw_ei312.xlsx`. Technosphere/deployment inputs are distributed over
  offsets 0–19. Each original uptake and Ni-release distribution is convolved
  with those weights, preserving rock, energy, uptake potential and nickel
  totals. Ni remains an ocean-release upper bound, not a measured mobile fraction.
- Reproduction uses the existing TRAILS Python 3.11 environment, explicitly
  selects Brightway project `ecoinvent-3.12-cutoff`, and reads the original
  REMIND-EU PkBudg1000 archive (SHA
  `bd298b3e30d84adbb9dfe11c87654a318d7b8aed94e0357fa932a6e3dbcf9780`).
  Five source anchors 2030/35/40/45/50 are interpolated to annual suppliers.
  Licensed matrices stay in ignored `build/seoul-erw-campaign/`. No source
  lecture, original workbook, Brightway database, or shared cache is modified.
- Twenty independent forward annual static LCAs check the campaign's dated
  GWP total: **−983.740883517643 kg CO₂-eq**. Difference from their sum is
  **−0.000004594824 kg CO₂-eq**. Responsible-root series close year by year
  to about 1.4e−14 kg. Fixed routing depth one retains complete residual
  background solves; full routing-depth convergence is not established.
  Root contributions can precede/outlast operating demands because upstream
  biosphere timing is retained; do not truncate them to the twenty demand years.
- FaIR was rerun from the new inventory, not shifted from the old curve.
  Background, mapping, configuration and properties hashes match the old run.
  Median response arrays are stored through 2500; displayed project comparisons
  retain their prior horizon through 2200. Kinetics remain illustrative,
  with default 10-year dissolution/1-year air–sea lag, not field calibration.
- `data/erw_campaign.json` is the portable aggregate artifact, SHA-256
  **793c6300f1467f336430a3a60e43a04974b934bdc9d5c41314d91417c81ff007**.
  `erw_campaign.py` checks that pin, source/new workbook hashes, service, period
  and annual-static/root closure. It needs no scientific environment at runtime.
  `erw.campaign_profile()` convolves physical per-batch uptake profiles for the
  live sensitivity; it never interpolates or convolves LCIA scores.
- `comparison.annual_scores()` and `forcing_series()`, temporal attribution in
  `contributions.py`, and the backup uptake chart in `technical.py` now use
  the campaign. Sensitivity controls preserve the calculated supplier inventory
  and perturb all annual batches' uptake; they do not rerun FaIR live.
  Current/prospective static snapshots retain the same total service collapsed
  into a selected year, and their checked root contributions are unchanged.
  DACCS, BECCS and cement numerical results are unchanged.
- `/erw-review` now leads with the active campaign, closure and scope.
  `/erw-campaign-inventory.xlsx` downloads the active workbook; the old
  `/erw-inventory.xlsx` and old batch result/attribution files remain provenance.
  README, case/context notes and five-bullet speaker notes reflect the campaign.

**246 repository tests passed**, including physical campaign mass/tail checks,
mean uptake shift, independent annual static closure, varying suppliers,
preserved FaIR inputs and sensitivity mass balance. Laptop/desktop/mobile and
speaker-fit checks are in `build/seoul-review/clocks-campaign-report.json`.
All 31 slides passed browser/layout checks with no JavaScript errors or failed
requests; the 28/34-page PDFs and speaker HTML were refreshed. The campaign
review page and active workbook download were checked against the result hash.
Teaching time, slide count, REMIND/Northern European geography and functional
units are unchanged.

## Previous slide 13 refinement: fewer labels, bottom timeline, ERW deployment period

The presenter found the integrated phase diagram crowded and requested the
timeline at the bottom. Slide 13 (`clocks`) now uses shorter labels, slim neutral
operating-input strips and the four coloured carbon paths on a shared relative
axis. Bottom ticks are **Start, +10, +20, +30, +50, +100 years**. An explicit
double-slash break after year 30 separates the near-term and long-tail scales;
the legend states this. Before-start equipment is a schematic diamond, not an
evidenced construction date. Geological-storage and uptake arrows remain open
beyond the displayed horizon. The tab is still removed.

**ERW clarification:** grinding/spreading physically occur over a deployment
period, and a sustained project would repeat batches. The present numerical
example remains a **2030 reference batch**, explicitly labelled in the diagram.
The checked `coastal_erw_ei312.xlsx` assigns grinding electricity (and the
deployment inputs) with `temporal_distribution=1`, `temporal_loc=0`, anchored
to 2030; this is annual aggregation, not an instantaneous physical grind.
The equipment strip covers that annual deployment bin and is called
**“Grinding + spreading period”**, replacing “One rock deployment”. A new
multi-year campaign has NOT been calculated or assigned an arbitrary duration.
It would require dated repeated demands, year-matched suppliers and the uptake
profile for each batch, followed by revised temporal/FaIR results. Do not stretch
the old batch curve across a campaign or silently label it a 20-year project.
Primary source context: Foteinis et al. (2023), doi:10.1021/acs.est.2c08633,
and Geerts et al. (2025), doi:10.5194/bg-22-355-2025.

Changes: `visuals.project_clocks_uri()`, `methods.clocks()`, `deck.py`, five
bullets in `speaker.py`, and the updated browser assertion. Inputs and results
are unchanged. **118 Seoul tests passed**. Desktop/laptop/mobile and note-fit
checks are in `build/seoul-review/clocks-bottom-report.json`; the full-deck QA
refreshes screenshots and 28/34-page PDFs. This supersedes the phase-width
description in the earlier revision below.

## Previous slide 13 revision: equipment and carbon in one diagram

Slide 13 (`clocks`, URL `#slide-12`) is now **“Equipment and carbon follow
different clocks”**. The two tabs and separate equipment-card view are removed.
One native SVG aligns equipment/recurring inputs above carbon pathways for all
four cases, across **before start / active project / beyond operation** phases.
Equipment uses neutral grey; carbon retains the four technology colours. Icons,
phase shading and continuing arrows replace the former sparse timeline.

- DACCS pairs plant construction and recurring sorbent with capture/storage.
- BECCS pairs CHP/capture upkeep with harvest/capture, geological storage and
  regrowth beginning after **each** harvest, overlapping the operating period.
- ERW pairs machinery preparation and one grinding/spreading deployment with
  separate, open-ended dissolution and delayed atmospheric uptake paths.
- Cement pairs construction/retrofit and component-specific upkeep with avoided
  kiln release during capture and subsequent geological storage.

The key explicitly says **schematic phases, not to scale**. Equipment ticks
illustrate repeated demand, not evidenced replacement dates. The diagram adds
no quantified equipment burdens, assumed replacement schedule or numerical
results. Original cohort dates, duration labels and full carbon tails remain.
On narrow screens the diagram scrolls horizontally inside its container rather
than shrinking the text or widening the slide.

Implementation: `visuals.project_clocks_uri()` (through `timeline()`),
`methods.clocks()`, `assets/zzzzzzzz_project_clocks.css`, title/detailed notes in
`deck.py`, and five speaker bullets in `speaker.py`. Browser QA now checks the
single integrated view and absence of tabs. **118 Seoul tests passed**; full
31-slide browser/PDF checks refreshed the 28/34-page exports. Target layout and
presenter checks are in `build/seoul-review/integrated-clocks-report.json`.
Teaching time and slide count are unchanged. This supersedes all older tab-based
clock descriptions below.

## Latest slide 12: evolving suppliers during operation

The second discussion pause (`pause-future`, URL `#slide-11`) now asks **“Is one
future snapshot enough for a long-lived system?”** It retains the equal-total,
different-removal-date thought experiment and four case prompts. A prominent
in-content band adds **“The background economy changes, too”**, with early →
later operation and year-specific electricity/heat suppliers. This is a
conceptual hint, with no assumed decarbonization rate or new numerical result.
The speaker first holds production conditions fixed to isolate emission timing,
then relaxes that assumption: unchanged annual plant demand can face changing
supplier mixes and upstream impacts. A single future background should not be
applied to an entire operating life when modelling an evolving economy.

Changes are in `deck.py`, five authored bullets in `speaker.py`, and
`assets/zzzzzzz_operating_background.css`. The band is part of the main content,
not small footer prose, and also appears in PDF export. The three-minute pause,
slide count, inventories, scenarios, contributions and climate curves are
unchanged. Browser layout checks and export artifacts are in
`build/seoul-review/`, including `operating-background-report.json`.
All 31 slides passed the browser/PDF check; slide 12 also fits 1600×900,
1280×720 and mobile width without horizontal overflow, and all five presenter
bullets fit at 1280×720. Core/full 28/34-page PDFs and notes HTML were refreshed.

## Latest slide 11: 2035 bars, both scenario diamonds and explicit default

Slide 11 (`future`, URL `#slide-10`) compares **2025 / 2035 / 2050** for the
same four cases. **PkBudg1000 is the default contribution-bar scenario** and is
labelled explicitly. A selector switches the 2035/2050 signed contribution bars
and the large 2050 score to NPi. Both scenario net scores remain visible:
**hollow grey diamonds = NPi**, **filled teal diamonds = PkBudg1000**. Future
diamonds are offset slightly horizontally for visibility, not to imply different
dates. The 2025 reference keeps its single dark diamond and original,
case-specific source; changing the selector does not change that baseline.
PDF export labels the default explicitly and retains both future scenario nets.

The additional bars/diamonds are calculated static results, not interpolation
between plotted LCIA scores. `scripts/calculate_static_scenarios.py` inside the
Seoul app produces `data/static_scenario_results.json`: DACCS, BECCS and coastal
ERW at 2035 and 2050 under both scenarios. Every root-level contribution sum
was checked against an independent forward static LCA; existing released 2050
scores were also reproduced. Foreground fossil/non-fossil CO₂ remains separate
from complete upstream contributions grouped by responsible root activity type.
The original case-specific methods/source vintages are retained; the new points
do not harmonize those methods, change temporal cohorts, or rerun FaIR.

- `static_scenarios.py` loads and validates the pinned aggregate result file
  (SHA-256 `fe8589702232a54175bb38029152fd04f9efaff29b865adc1427927831d2584e`).
  It is portable with the repository and needs no local Brightway project to
  display the lecture. The JSON records calculation provenance, input hashes,
  provider-level LCIA scores and closure checks, not licensed background matrices.
- Reproduction uses the TRAILS environment and `ecoinvent-3.12-cutoff` project.
  PkBudg1000 uses the original all-years REMIND-EU archive under
  `/Users/romain/GitHub/premise/export/trails/remind-eu-SSP2-PkBudg1000-all-years-20261014/`.
  The original NPi archive is unavailable, so the script reads its existing
  trusted annual interpolation cache at
  `/Users/romain/Library/Application Support/trails/cache/interp_31c40820e920`.
  Cache hashes and original package identity are recorded. Do not substitute the
  unrelated older `trails/dev/publication/trails_SSP2-NPi.zip`. These local
  dependencies are needed only for recalculation, not presentation. Matrices
  reconstructed into ignored `build/seoul-static-scenarios/` remain private.
- Cement reads the existing reviewed 2035/2050 bundles for each pathway, with
  CCS minus equal-output BAU normalized to **1 tonne physically stored**.
  Physical route checks confirmed the same denominator for both pathways at
  each date: 1.320117909129454 t clinker/t stored in 2035 and
  1.2551211005126701 in 2050. The source CCUS app and its functional unit were
  not edited.
- Implementation: `comparison.py`, `contributions.py`, `app.py`, `deck.py`,
  `speaker.py`, `assets/zzzzzz_future_scenarios.css`; the existing browser QA now
  switches both scenarios and checks all four plots and the default restoration.

**243 repository tests passed.** All 31 slides passed browser checks with no
JavaScript errors, failed requests or desktop overflow. The 28/34-page PDFs and
screenshots were refreshed under `build/seoul-review/`. Speaker notes retain
five bullets for this slide. The deck remains 25 core slides plus six backups,
with the same 70-minute teaching and 20-minute discussion plan.

## Latest slides 4 and 10: ecoinvent background and premise branding

The presenter requested the premise logo in slide 10’s “premise transforms”
block, ecoinvent branding with a database icon, and a visual explanation on
slide 4 that background processes come from the ecoinvent LCA database.

- **Slide 10 (`suppliers`), first tab:** its middle transformation block now
  contains the unchanged premise mark, plus an **ecoinvent wordmark + database
  cylinder → scenario-updated suppliers** mini-diagram. The background label
  remains **ecoinvent 3.12 cut-off**. IAM inputs, mapping, updates, supplier
  relinking and foreground demand remain separate concepts. The duplicate
  four-case ribbon is omitted because the four foreground-choice rows already
  identify the cases; this preserves space for the chart. Existing contribution
  values (+96.7 / +26.8) and their interpretation are unchanged.
- **Slide 4 (`supply-chain`), all four carousel/PDF diagrams:** selected purchased
  input boxes (electricity, chemicals, sorbent, fuels, water/freight) have a pale
  blue fill. An **ecoinvent + cylinder background key** in previously unused
  space at the bottom identifies those as links to database unit processes.
  The foreground chain remains white. This is a data-source illustration, not
  an additional physical flow, impact credit, exhaustive supplier classification,
  or a claim that analyst foreground technology assumptions come from ecoinvent.
  The DAC heat-pump conversion/COP, foreground carbon uptake and atmospheric
  emission boxes remain distinct; physical quantities, arrows, sign conventions,
  boundaries and scientific results are unchanged. The key moves right in ERW
  to avoid its atmosphere node. The SVG viewport/diagram scale is unchanged.
- `branding.py` embeds the original marks as data URIs, including a nested SVG
  image in each process map. This keeps images offline and avoids shared-asset
  URL rewriting. The ecoinvent wordmark is copied unmodified from the official
  homepage asset `https://ecoinvent.org/app/uploads/2023/09/Logo-Wordmark.svg`;
  premise reuses `apps/workshop/assets/premise-logo-transparent.png`. Exact
  paths, source URLs and SHA-256 hashes are in `data/background_branding.json`;
  both hashes were checked. Ownership is recorded in `THIRD_PARTY_NOTICES.md`.
- `visuals.py` adds a native database-cylinder icon. `methods.supplier_trace()`
  adds branding in the centre card. `processes._tag(..., supplier=True)` shades
  the selected supplier-input examples and `process_uri()` adds the data key.
  Styles are in `assets/zzzzz_background_branding.css`; the authored speaker
  notes still have five bullets. Detailed notes explain the foreground/background
  boundary and that premise transforms selected linked suppliers rather than
  supplying a complete analyst-defined project model.
- **108 focused tests passed**, including unchanged physical and contribution
  closure. Browser/PDF checks refresh all 31 slides, all four process diagrams,
  28/34-page PDFs and note HTML in `build/seoul-review/`. Native figures, source
  inventories, model/scenario settings and teaching times were not recalculated.

## Latest slide 9: five SSPs, AR6 pathways and the IPCC, 29 October 2026

The presenter requested short descriptions of all five SSPs in the left block,
a similarly detailed right block, and the link to the IPCC. `scenario_layers()`
now uses the existing workshop combination visual plus three detailed columns:

- Left: **SSP1 Sustainability**, **SSP2 Middle of the road**, **SSP3 Regional
  rivalry**, **SSP4 Inequality**, **SSP5 Fossil-fuelled development**, each with
  one short socioeconomic description.
- Centre: a **one-to-many** illustration (SSP1 → SSP1-1.9 / SSP1-2.6) explains
  why a storyline does not fix an emissions outcome. A separate worked example
  retains **SSP2 + REMIND-EU + NPi / PkBudg1000** as the lecture's actual codes.
- Right: the **five illustrative AR6 WGI emissions pathways** from very low to
  very high: SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5, each with a brief
  emissions-trajectory description. The header defines the numeric suffix as
  approximate radiative forcing in 2100 in **W/m²**. These are joint scenario
  labels, not the five socioeconomic narratives, not temperatures, and not
  one-to-one counterparts of the left list. SSP1 is intentionally shown twice;
  SSP4 is absent from the illustrative AR6 WGI set. Older RCP terminology is
  distinguished in detailed notes. Do not relabel NPi/PkBudg1000 as one of
  those five AR6 examples or infer a warming category from the lecture code.
- An IPCC band expands **Intergovernmental Panel on Climate Change** and shows
  **research teams develop scenarios → IPCC assesses the evidence**. Three
  labels introduce WG I climate response, WG II impacts/adaptation, and WG III
  mitigation pathways. Linked primary references are AR6 WGI Chapter 1, WGI SPM,
  and the IPCC working-groups overview. Narrative details also use the SR1.5
  Chapter 2 SSP descriptions. The IPCC is not portrayed as the developer of
  this premise package or of technology-specific LCIA results.

Implementation: `reused.py`, `assets/zzzz_scenario_details.css`, `deck.py`, and
five authored bullets in `speaker.py`. The four-case ribbon is omitted on slide
9 because it adds no information on this conceptual page. Top combination boxes
remain the reused workshop structure. Use the scoped **scenario-assumption-fork**
class: the older source-deck `scenario-fork` class has pseudo-elements which
would draw unwanted lines through the new labels. No source lecture was edited.

**108 focused tests passed**. All 31 slides passed browser checks without
JavaScript errors, failed requests or overflow. Laptop/mobile layout and the
five-bullet presenter notes passed. Core/full PDFs, screenshots and speaker-note
HTML were refreshed under `build/seoul-review/`. The deck remains
25 core slides plus six backups, 70 + 20 minutes, and 28/34 PDF pages. No scenario
inputs, inventories, project LCA results or climate curves changed.

## Latest slide 8: broader IAM map and model/team marks, 29 October 2026

This supersedes the energy/economy-only centre described in the earlier
slides 7–8 revision below. The presenter correctly requested a broader IAM scope
and names/logos of the main IAMs.

- The centre of slide 8 (`iam`) now maps **economy/demand/investment**, **energy
  and industry**, **land/food/forestry**, **transport/buildings**, **water and
  resources**, and **emissions/climate/environment**. Resource competition,
  markets and trade link domains; the diagram and notes explicitly say that
  sector coverage, feedbacks, algorithms and internal/external module linkages
  differ by model. Do not imply a universal energy-only architecture, a universal
  full climate-damage feedback, or that every IAM optimizes one welfare function.
  Primary broad-scope sources are the IMAGE framework and GCAM documentation.
- The title is “IAMs connect economies, land, resources and climate”. The
  three-column assumptions → linked sectors/constraints → outputs structure
  remains. SSP2 population and MAGICC7 temperature graphs are unchanged stored
  scenario context; **the lecture still uses REMIND-EU**, not a new model run.
- A six-card strip links **REMIND–MAgPIE, IMAGE, MESSAGEix–GLOBIOM, GCAM,
  AIM/CGE and WITCH** to model/team homepages. Use the unchanged downloaded marks
  in `assets/iam-logos/`. The explicit captions distinguish **model-component
  marks** (MAgPIE and MESSAGEix), **family/model marks** (AIM, WITCH) and **team
  marks** (IMAGE/PBL government mark; GCAM/UMD partner seal). Do not describe the
  PBL crest or UMD seal as independently designed IMAGE/GCAM model logos.
  Dedicated separate model-logo artwork for those two was not verified; team
  marks are used transparently. The six examples are not an exhaustive IAM list.
- `data/iam_logos.json` records model names, mark types, primary source pages,
  exact asset URLs, access date, descriptions and SHA-256 hashes. The source
  artwork is copied unchanged; no generated or reconstructed logos were used.
  `THIRD_PARTY_NOTICES.md` preserves ownership/mark attribution. All six assets
  are local for offline teaching and PDF export.
- `layout._rewrite` preserves the app-owned `assets/iam-logos/` URLs, instead of
  rewriting them to the source decks’ `/shared/` endpoint. This narrow ownership
  exception works with both the portal prefix and standalone app. The existing
  shared-asset rewrite remains intact. A browser check caught this routing issue
  and the corrected page verifies all six images loaded.
- The `buildings` SVG icon extends the existing native icon style. Styles in
  `zzz_scenarios.css` allocate a compact six-logo row and preserve stacked mobile
  layouts. The visible speaker notes remain exactly five bullets; they now cover
  broad domains, variable scope and model-family recognition. Detailed notes
  carry provenance and the distinction between IAM background and project FaIR.
- Six asset hashes and **108 focused Seoul tests passed**. All **31 slides**
  passed browser checks without errors, failed requests or overflow; the **28/34-
  page PDFs**, screenshots and speaker-note HTML were refreshed under
  `build/seoul-review/`. Laptop/mobile layout checks and five-bullet presenter
  notes passed; all six logos loaded at both viewport sizes.
  No inventories, scientific results, timings, page counts, source lectures,
  commits, deployment or external messages changed.

## Slides 7–8: pathway evidence and a visual IAM tour, 29 October 2026

The presenter requested more information/interest on slide 7 (`pathways`) and
icons/graphs on slide 8 (`iam`). Both are implemented in `reused.py`, with styles
in `assets/zzz_scenarios.css`. The title/notes/timer use the same stable keys;
slide counts and pacing remain unchanged.

- **Slide 7** is now “The same year can mean very different supply systems”.
  The original SETAC REMIND-EU/SSP2 World net-CO₂ figure is reused, with shading
  between pathways, a common-2025 annotation, direct 2050 labels, a 23.0 Gt/year
  gap annotation and two policy cards. The cards read the actual stored CSV rows
  via `_context_value`, rather than hard-coding numbers: approximately 32.2 and
  9.2 Gt/year in 2050, respectively 26% and 79% below the common 2025 value.
  These percentages are global net-emissions comparisons, **not LCA scaling
  factors**. A four-case icon strip makes the qualitative supply mechanisms
  explicit: cleaner DACCS energy, shrinking BECCS displaced-energy credits,
  changing ERW grinding/haulage, and evolving cement fuels/capture utilities.
  The global curve is explicitly distinguished from supplier emission factors.
- **Slide 8** is now “An IAM connects demand, investment and climate”, with
  three panels: assumptions → linked decisions → conditional outputs. Native
  SVG people, investment, policy, power, heat and kiln icons match the existing
  design. A central economy/energy diagram uses energy demand and system costs
  as the two links; it is schematic, not a complete model architecture or a
  quantified sensitivity calculation. Existing capacity/resources/policy constrain
  joint investment choices. Primary methodological reference: Baumstark et al.
  (2021), REMIND2.1, https://doi.org/10.5194/gmd-14-6571-2021 and PIK’s REMIND
  overview, https://www.pik-potsdam.de/en/institute/departments/transformation-pathways/models/remind .
- The two slide-8 mini-charts reuse **stored SETAC scenario-context data**:
  World SSP2 population (one curve; the two policy inputs are checked identical),
  and global mean temperature for NPi/PkBudg1000, explicitly labelled **MAGICC7
  scenario-background medians relative to 1850–1900**. These are neither new
  model runs nor FaIR warming caused by the four projects. Do not substitute a
  newer REMIND version or reinterpret these source-vintage trajectories as
  guaranteed temperature targets. Context provenance is unchanged in
  `apps/setac_2026/data/scenario_context.json` (premise 2.4.9 extraction, retained
  after the unchanged-IAM-input regeneration check).
- The duplicated four-case ribbon is omitted on these two slides: slide 7 has
  its own four-case cards, while slide 8 focuses on the IAM mechanism. Mobile
  layouts stack the panels. Both slides retain exactly five presenter bullets.
  The source lectures, scenario files, project inventories, LCA/FaIR results,
  normalization and PDF page counts are unchanged.
- **108 focused Seoul tests passed**. All 31 slides passed browser checks
  without JavaScript errors, failed requests or slide-boundary overflow. Both
  PDFs (28/34 pages), `slide-06.png`, `slide-07.png` and speaker-note HTML were
  refreshed under ignored `build/seoul-review/`. The two revised slides also
  pass laptop/mobile width checks; their five-bullet notes fit at 1280×720.
  No external publication or commit was made.

## Slide 2: delayed landfill impacts, 29 October 2026

The presenter requested a third motivation block on impacts occurring long after
normal operations. `visuals.temporal_introduction()` now has three equal-width
cards: changing suppliers, climate timing, and **delayed impacts**. The third
uses landfill leachate releasing pollutants centuries after disposal and the
potential resulting human-toxicity impacts. It explains that a short assessment
horizon or a “no LT” method can exclude these effects. It does **not** claim all
conventional LCA excludes long-term emissions: ecoinvent can already include
these flows in static inventories and some LCIA implementations characterize
them. Distinguish the release date from fate/exposure/effect timing, and inventory
horizons from GWP100. This is a general landfill example, not an added quantified
EV-waste scenario or a toxicity calculation using FaIR.

The new card cites Turner, Beaven & Woodman (2017), *Evaluating landfill aftercare
strategies: A life cycle assessment approach*, Waste Management 63, 417–431,
https://doi.org/10.1016/j.wasman.2016.12.005 (10,000-year leachate assessment,
including human toxicity), and ecoinvent’s primary LT/no-LT explanation:
https://support.ecoinvent.org/lcia-results . The local LCA wiki clone was absent;
primary sources were used rather than claiming to have read local wiki pages.

CSS uses three columns on desktop and preserves stacked mobile cards. The first
two headings were shortened to keep the layout readable. Detailed notes explain
the scope distinction; the presenter still has exactly five bullets, with the
last covering delayed landfill effects. Counts, pacing, scientific inventories,
LCA results and climate curves are unchanged. **108 Seoul tests passed** and the
1600×900 preview shows all three cards without overflow. Browser/PDF artifacts
under `build/seoul-review/` are refreshed for this revision.

## Latest changes: cement storage basis, atmosphere arrows and slide removal

These decisions supersede earlier clinker-basis and partial fuel-carbon diagram
instructions **for the Seoul lecture only**. The reviewed CCUS webinar and its
scientific inputs/results have not been modified.

- The presenter explicitly requested **1 tonne CO₂ physically stored** for
  cement + CCS. `cement_basis.py` loads the pinned derived factors in
  `data/cement_storage_basis.json`, validates their public source-result hashes,
  and converts every cement result consistently. Static 2025/2050 use their
  matching physical storage yields; temporal GWP and FaIR use the equal-output
  mean physical storage over the complete 2035–2064 production campaign.
  Construction, end-of-life and earlier dated effects receive that same campaign
  factor. Do not normalize a lifetime result with the 2025 or 2050 snapshot.
- 2025 requires **1.135148576 tonnes clinker per tonne stored**; 2050 uses
  **1.255121101**, and the campaign factor is **1.278063013**. The intervention
  remains CCS minus BAU producing exactly the same associated clinker output.
  Avoided fossil/mineral release is not atmospheric removal. Cement static
  scores are approximately **−820.4 (2025), −966.4 (2050) kg CO₂-eq per stored
  tonne**; the summed dated inventory is **−958.7** on its campaign basis.
  These are linear unit conversions, **not new LCA/FaIR simulations**.
- Slide 4's cement stream now includes **calcination, fuel and capture-boiler
  carbon**, replacing the former fuel-only 235 + 104 kg storage illustration.
  The 2025 aggregate balance per stored tonne is ~1187 kg gross, ~1068 kg
  captured, **1000 kg stored**, and ~187 kg emitted through uncaptured gas and
  conditioning/transport losses. Fossil/mineral and non-fossil streams remain
  distinct. Material/fuel/utility arrows and clinker output share this basis;
  utility amounts are now per stored tonne, not per captured tonne. The combined
  kiln/boiler node supplies the full CO₂ stream. The future source uses heat
  pumps, unlike the 2025 gas-boiler configuration.
- All four diagrams have outgoing CO₂ arrows ending at an **Atmosphere** node.
  DACCS and BECCS losses remain physical inventory quantities. ERW machinery/
  haulage exhaust is explicitly unquantified: do not derive CO₂ mass from MJ
  diesel or a GWP score. ERW still uses **1.25 t olivine-rich rock deployed,
  1 t eventual gross uptake potential**, not guaranteed net storage.
- The presenter removed former **slide 6**, key `mechanisms` (standalone
  reference-system cards), because it repeated existing explanations. References
  remain on process maps and results. Its 120 seconds were split equally between
  `supply-chain` and `current`. There are now **25 core slides + six backups =
  31 audience/backup slides**, with **28 core PDF pages / 34 including backups**
  because slide 4 prints four separate diagrams. Teaching remains 70 minutes,
  followed by 20 minutes discussion and an untimed thank-you slide. All subsequent
  ordinal slide numbers shifted by one; use stable keys when editing.
- The scalar storage factors were checked against exact hash-locked reviewed
  physical evidence locally. `scripts/check_seoul_cement_basis.py` reproduces
  that check when private evidence exists. It checks 2025 captured throughput
  including boiler recapture, the 30 annual physical storage ledgers, sequential
  losses, carbon closure and original approval hashes. Portable runtime needs
  only derived factors and existing public reviewed result bundles. No raw
  private inventories, source-cell coefficients or licensed provider copies were
  added to the presentation assets. Do not revive the retired private exporter.
- Validation: **233 repository tests passed**, including independent checks that
  static, dated-inventory and climate responses receive the correct conversion,
  signed contribution closure and source-app privacy tests. The local server is
  at **http://127.0.0.1:8057/seoul-2026/**; presenter companion is `/presenter`.
  Browser artifacts/PDFs were refreshed under ignored `build/seoul-review/`: all
  **31 slides passed**, with no JavaScript errors, failed requests or overflow;
  PDFs are **28 / 34 pages**. All 31 presenter note lists fit at 1280×720;
  desktop/laptop/mobile presenter views have no horizontal overflow.

## Heat-pump interpretation audit, 29 October 2026

The user asked whether DACCS uses an industrial air-to-air heat pump and whether
COP 3 is reasonable in Northern Europe. Read-only checks found that the native
DAC operation in `lci-carbon-capture.xlsx` (both the main premise checkout and
the isolated trals worktree) implements the heat pump as an electricity proxy:
11.9 MJ thermal/kg captured / 3.6 / COP 3 = 1.10185 kWh/kg, plus 0.7 kWh/kg
direct capture electricity. `build/setac-regeneration-20261014/data/inventories/parameters.json`
records the same COP 3. The operation does not establish an air-to-air design,
source/sink fluid specification or seasonal Northern European performance.

**Do not describe COP 3 as a measured Northern European value or attribute it
directly to Qiu et al.** Qiu et al. (2022), Methods, specify roughly 80–120 °C
regeneration heat and a heat-pump COP of **2.5**:
https://doi.org/10.1038/s41467-022-31146-1 . The repository's COP 3 is an adapted
proxy. IEA's *Renewables for Industry: Electrification of low-temperature heat
and steam*, Chapter 2, Figure 2.3, relates COP to source-to-sink temperature lift;
warm waste heat and cold outdoor air cannot be treated as equivalent sources.
COP 3 is plausible for appropriate industrial source/delivery conditions but is
unvalidated for this unspecified site/design, especially if ambient air supplies
heat near 100 °C in winter. Holding the displayed 12.2428 GJ demand fixed, COP
2.5 would imply about 1.360 MWh heat-pump electricity per net tonne stored,
20% above the COP-3 value. That arithmetic is not a recalculated LCA result.
No inventory parameters, scores or slide quantities were changed during this
question-and-answer audit.

## Slide 4 energy split, flow legend and inventory sources, 29 October 2026

The later rock-type request is implemented: the ERW extraction node explicitly
labels **olivine-rich rock**, matching the coastal olivine inventory. Its accessible
description and concise speaker bullet use the same wording; quantities are unchanged.

The user requested explicit DAC technology/energy demands, inventory citations
on every diagram, and distinct electricity, heat, material and CO₂ flow colours.
Implemented in `processes.py` and its carousel CSS:

- DACCS is labelled **low-temperature solid-sorbent DAC / TVSA** (temperature–
  vacuum swing adsorption), with its heat pump shown separately. Per net tonne
  physically stored, the heat pump uses **1.134 MWh electricity** at **COP 3**
  and supplies **12.24 GJ capture heat**. Direct capture uses another
  **0.720 MWh electricity**, computed as the original capture-plus-heat-pump
  total minus the heat-pump input. The separate conditioning/transport/injection
  total remains **139 kWh**. These split the original quantities, not a new
  inventory or an extra heat demand.
- Electricity arrows are amber dashed; delivered heat is red dash-dot;
  materials, alkalinity and fuels are slate; generic CO₂ is teal. Cement still
  uses brown fossil and green dotted non-fossil CO₂. The common four-category
  legend includes physical units and shows cement's CO₂-origin variants when
  that diagram is selected. Fuel MJ/GJ denote material energy content, not
  delivered heat.
- BECCS has separate electricity-export and useful-heat-export branches, plus
  its existing CHP-to-capture heat. ERW separates deployment electricity from
  machinery diesel. Cement distinguishes kiln fuels, capture electricity,
  capture gas-boiler fuel, boiler heat and recovered kiln heat. Its **2.77 GJ
  gas** and **41.9 kWh electricity** remain intensities per tonne captured CO₂;
  no useful-heat amount is inferred from the gas input. The former connector
  from a loss-rate annotation was removed because a rate is not a material flow.
- Every case has its own linked source strip adjacent to the diagram, retained
  on its expanded PDF page. DACCS cites Deutz & Bardow (2021) / Qiu et al. (2022);
  BECCS cites ecoinvent 3.12 forestry/CHP / Volkart et al. (2013); both identify
  Koornneef et al. (2008) / Terlouw et al. (2021) for transport/storage. ERW cites
  Foteinis et al. (2023), its SI Table S1 and the reviewed local adaptation.
  Cement cites Gallego Dávila et al. (2023), SI.2 and the reviewed webinar
  adaptation. These are adapted inventories, not claims that every displayed
  normalized quantity is verbatim from the publications.

The five speaker bullets and detailed process notes reflect the new colours and
energy split. The source inventories and scientific scores remain unchanged.
Three focused process tests passed, including electricity-split and heat/COP
closure. All 32 slides passed browser checks without errors, failed requests or
overflow; citations and the common four-category legend were checked for each
case, and both PDFs and `process-0.png` through `process-3.png` were refreshed.

## Slide 2 electric-car example, 29 October 2026

The introduction's generic construction/operation/end-of-life timeline is now
an **electric-car life cycle**: vehicle and battery production before driving,
charging and maintenance over years of driving, then dismantling and recycling
after use. Car, battery, charger and recycling glyphs are native SVGs in
`visuals.py`. All stages still feed one aggregated inventory and impact score;
the changing-supply explanation now uses the car's charging electricity.
This is a conceptual illustration with no assumed vehicle lifetime, mandatory
battery replacement, new EV inventory or calculated EV impact values. The three
existing methodological references remain. Detailed context and the five short
speaker bullets have been updated; the four numerical case studies are unchanged.

## Presenter simplification, 29 October 2026

Latest user request: retain the timer and slide-by-slide time distribution, and
convert the notes into a maximum of four or five bullet sentences. The presenter
page now has only timer controls, concise current-slide notes and a scrollable
time plan. The event introduction, instructional paragraph, separate cue,
next-slide preview, audience link and dropdown were removed. Plan rows select
notes passively; audience navigation still synchronizes them automatically.

All **32 slides have four or five authored bullet sentences** in
`apps/seoul_2026/speaker.py`. `presenter_slides()` returns these lists and pacing
start/end seconds, without appending dense footer context. Detailed scientific
notes remain in `deck.py` and this handover for implementation reference, rather
than being displayed. Do not restore the old paragraph/cue presentation. The
time plan shows per-slide durations and target ranges; discussion has its own
0:00–20:00 phase and the closing slide is untimed. The 70/20 minute timer keeps
its existing local-storage state and start/pause/reset behaviour.

Presenter-specific browser checks covered all 32 bullet lists, audience sync,
passive manual row selection, timer persistence across reloads and phase
switching. No JavaScript errors occurred; desktop/laptop have no page overflow,
mobile has no horizontal overflow, and all 32 note lists fit without internal
scrolling at 1280×720. Existing timing/route tests passed (2 selected tests).
See `build/seoul-review/presenter-report.json`, `presenter.png`,
`presenter-1280.png`, `presenter-mobile.png` and refreshed `speaker-notes.html`.
The full browser checker now reads `#slide-notes[data-slide-index]` in place of
the deleted `#selection` dropdown. Audience slides and PDF content did not change.

## Source-lecture teaching revision, 29 October 2026

The user approved incorporating the review suggestions from all four source
lectures. They are implemented inside the existing **26 core + six backup
slides**, with the existing European cases and scientific result bundles.

- **6 / mechanisms:** project-versus-reference cards with native services and
  the physical-service / life-cycle-benefit distinction. BECCS retains standing
  forest plus equivalent energy; cement retains CCS minus BAU clinker.
- **11 / suppliers:** default tab traces IAM evidence → premise mapping/update/
  relinking → foreground electricity input → observed supplier contribution.
  The bars sum exact ENC medium-voltage electricity roots from the checked Seoul
  extracts: about +96.7 (2025 NPi) and +26.8 (2050 PkBudg1000) kg CO₂-eq/net t
  stored. These are complete root scores, not upstream CO₂ partitions or per-kWh
  intensities. The snapshots differ in year, pathway and package vintage and may
  differ in demanded inputs; do not claim an isolated climate-policy effect.
  The original SETAC supply-mix explorer remains in the second tab.
- **14 / clocks:** existing carbon timeline plus an equipment-clock tab. These
  explanations add no equipment quantities, invented replacement dates or new
  burdens. Do not import CCUS-only electrolyzer/methanol schedules into CCS.
  Unquantified cement capture-plant construction remains unquantified.
- **15 / trails:** four selectable worked 1 kWh inputs, not full project
  inventories. DACCS/BECCS use 2037 (within 2030–2049), ERW grinding 2030,
  cement 2042 (within 2035–2064). Show annual backgrounds, exchange dates and
  retention of the complete matrix-solved demand beyond the explicit graph.
- **18 / response:** gases and years → paired FaIR scenarios → forcing and
  temperature. Never feed the aggregate GWP100 score into FaIR.
- **19 / pulse-equivalence:** a live three-handle calendar window and reference
  pulse, adapted from SETAC's interaction pattern. The fixed pedagogical
  inventory is +1000 kg CO₂ in 2030, −1000 kg in 2080. Default dates are
  2020 / 2030 / 2100; the illustrative equivalent is about +632 kg. Extending
  the endpoint to 2300 yields about +130 kg with the same reference. These are
  ratios of stored median marginal CO₂-response areas, prominently labelled
  as an illustration, **not configuration-first ensemble results for the four
  technologies**. Both plots share the signed integration window; the reference
  curve is scaled to match its area. The all-four conceptual mapping is retained
  in the second tab. Real project equivalents require configuration-resolved
  responses and ratios calculated before ensemble summarization. Do not import
  older `lca_time` full-project climate values/ranking reversals.
- **21 / erw-sensitivity:** existing live ERW controls plus a second tab on
  scenario, foreground/reference, timing and climate-parameter uncertainty.
  FaIR ensembles do not sample uncertainty in the other layers. Existing ERW
  controls still do not recalculate FaIR.
- **22 / lenses:** separate selection of the inventory model from the climate
  question. Timing can matter even when the preferred option is unchanged.
- **25 / discussion:** timing/reference questions and possible land, water,
  resource and ecosystem trade-offs, without inventing non-climate scores.

Implementation: `apps/seoul_2026/methods.py`, `pulse.py`, `deck.py`, new pulse
callback in `app.py`, `assets/zz_methods.css`, and accessible lesson tabs in
`assets/presentation.js`. A scoped date-control keyboard handler uses Dash
`set_props`; a capture-phase focus handler prevents this rc-slider version from
starting a drag and shifting a date merely on focus. Pointer dragging is native.
The source applications and result artifacts remain untouched.

Presenter cues and detailed notes follow the revised explanations. Pacing still
totals **4,200 seconds**, including the same two three-minute pauses; 30 seconds
each from the carbon-atlas/coast pages give the pulse demonstration 240 seconds.
Open discussion remains 1,200 seconds. PDF uses curated first tabs, with only
the DACCS worked routing example; secondary views stay available live and in
speaker notes. PDF page counts remain **29 core / 35 including backup**.

Verification: **233 full-suite tests passed (108 focused)**, including independent
signed-area closure, fixed-inventory invariance and the early-window +1 t limit.
The browser script now checks the lesson tabs, routing keyboard navigation,
pulse date/readout updates and retained ERW controls, alongside all-slide layout
and PDF export checks. **All 32 slides passed with no browser errors, failed
requests or slide overflow; both PDF exports were refreshed.** See
`build/seoul-review/browser-report.json` and the PDFs/screenshots there.

## Cover revision, 29 October 2026

Slide 1 no longer displays the "70 min teaching" / "20 min discussion" tags.
Its subtitle is: "How does accounting for time change the life cycle assessment
of long-lived systems in rapidly changing economies?" The opening presenter cue
now follows this question. Presenter timers and the teaching/discussion schedule
retain their existing durations.

## Final geography decision: REMIND and Northern Europe, 29 October 2026

**Latest user clarification: "we stick with REMIND and Northern Europe".**
Retain the existing REMIND-EU background, NPi/PkBudg1000 scenario identities,
and original European case locations, inventories and results. This supersedes
the earlier request to relocate the examples to South Korea. The Korean
regionalization and proposed IMAGE build are cancelled; no Korean variants or
replacement background packages remain pending. The existing deck already uses
the retained case setup, so this clarification requires documentation changes
only. Keep each case's documented location explicit rather than relabelling all
four with a single country.

### Superseded Korean investigation (historical only)

Read-only inspection of the existing all-years SSP2-PkBudg1000 archive confirmed
these exact suppliers at 2025, 2030 and 2050:

- `market for electricity, medium voltage`, `electricity, medium voltage`,
  `kilowatt hour`, `KR`.
- `market group for electricity, medium voltage`, `electricity, medium voltage`,
  `kilowatt hour`, `OAS`.
- `market for lignocellulosic biomass, used as fuel`, `lignocellulosic biomass`,
  `kilogram`, `OAS`.

Package: `/Users/romain/GitHub/premise/export/trails/remind-eu-SSP2-PkBudg1000-all-years-20261014/trails_remind-eu_SSP2-PkBudg1000.zip`.
REMIND-EU's OAS topology includes KR, KP and many other Asian countries. These
supplier findings belong to the cancelled investigation and are not instructions
to modify the retained European cases.

### Earlier IMAGE check (retained for provenance)

The user requested moving all four examples to South Korea, then proposed an
IMAGE TRAILS datapackage using premise's `trals` branch. Before generation they
explicitly asked whether IMAGE `KOR` is South Korea alone. **It is not:** the
branch's `premise/iam_variables_mapping/topologies/image-topology.json` maps
`KOR` to both `KP` (North Korea) and `KR` (South Korea). PBL independently lists
both countries in IMAGE region 19, "Korea region":
https://models.pbl.nl/image/Region_classification_map . Do not describe KOR
biomass or electricity mixes as South-Korea-only. Native ecoinvent `KR` datasets
and prospective IMAGE `KOR` trajectories have different geographical scopes;
retaining a KR location does not disaggregate a KOR scenario. The same branch's
GCAM topology has a separate `South Korea: [KR]` region, if country-specific IAM
resolution is required; exporter/scenario availability still needs checking.

No IMAGE build has started and the displayed European results have not been
rebased or relabelled. The dirty main premise checkout remains untouched on
`metals-fix`. An isolated detached worktree was created at
`/Users/romain/GitHub/.codex-worktrees/premise-image-trals-20261029`, local trals
commit `a9d7af846ba0e7502a230050d348d64e99d6bd52`. Fetched `origin/trals` is one
formatting commit ahead (`0716a0f1`). This worktree is unused after the decision
to retain REMIND and Northern Europe. Preserve it and the unrelated dirty main
checkout.

## Current rule: foreground CO₂ + root supply-chain contributions

**This supersedes the earlier CO₂-origin views described below.** Only direct
foreground CO₂ is shown as fossil/non-fossil CO₂. All upstream effects, including
biomass uptake in electricity supply, remain inside complete supplier LCIA
contributions grouped by root activity type. Current and prospective charts use
this boundary consistently; temporal charts retain root attribution. Full-chain
CO₂ flow toggles have been removed from the displayed result slides. No net
scores, native services, time assumptions or climate responses changed.

DACCS/BECCS now use `data/cdr_static_roots_2025.json` and
`data/cdr_static_roots_2050.json`, extracted and independently validated against
the saved static scores. Read the final section of this file for reproduction.
**233 full-suite tests passed (108 focused); browser QA passed all 32 slides.**
Core/full PDFs remain 29/35 pages. Keep the local server running.

## Introduction added earlier on 28 October 2026

A new scene-setting slide is **audience slide 2**, key `why-time`, directly after
the cover. It explains conventional LCA's aggregation of life-cycle exchanges
without event dates and distinguishes two motivations for retaining time:
changing supply systems over long activity lifetimes, and the timing of climate
effects. The diagram is schematic, not a new inventory. Qualify the claim:
static LCA can include all life-cycle stages, and GWP100 already has a time
horizon; event dates and changing systems are the missing distinctions.

The user explicitly requested references on this slide. It contains visible,
clickable DOI links for Beloin-Saint-Pierre, Heijungs & Blanc (2014),
10.1007/s11367-014-0710-9; Müller et al. (2025), 10.1007/s11367-025-02539-3;
and Levasseur et al. (2010), 10.1021/es9030003. Full citations and methodological
qualifications are in its speaker notes.

There are now **26 core pages and six backups (32 total)**. The introduction has
150 seconds, offset by shorter allocations to the carbon atlas, supply-network,
IAM, scenario, climate-response and ERW-sensitivity pages. Teaching remains
**4,200 seconds**, with the same separate **1,200-second discussion** and untimed
thank-you. Existing pages after the cover shift by one. Chapter indices now
derive from stable keys rather than hard-coded positions. Use the current
health manifest or `SLIDE_INDEX`; older one-based slide numbers in the previous
review section describe the layout before this insertion.

## Latest review: 27 October 2026

The user requested changes to audience slides **7, 9, 11, 15, 16 and 22**,
questioned the apparent twenty-year ERW uptake period, and asked for a closing
thank-you. All are implemented; slide numbers refer to one-based audience pages.

- Slide 7 uses actual stored NPi/PkBudg1000 global trajectories and connects them
  to the four projects' supplier needs. Slide 9 has concrete bullets in each box.
- Slide 11 now has signed activity-type stacks at 2025/2050 and net diamonds.
  Slide 15 has responsible-root signed series with annual/cumulative toggle.
  New `contributions.py` keeps opposite signs separate and checks source closure.
  Cement retains the approved subprocess/stage attribution and CCS-minus-BAU.
- `data/erw_contributions.json` and `scripts/extract_erw_contributions.py` were
  added. The same reviewed workbook/package are used. Static first-tier results
  close to source totals; temporal roots reproduce annual GWP within 2.84e-14 kg.
  The extraction uses TRAILS 1.1.1 and its checked adjoint intensity helper;
  it does not change inventories or rerun climate simulations.
- ERW has **no universal twenty-year uptake cutoff**. The timeline now shows
  open-ended dissolution and uptake. The stored numerical/FaIR reference is
  still explicitly the **fast illustrative 10-year dissolution / 1-year lag**.
  The separate sensitivity page now opens with **100-year / 5-year** and displays
  170 years. Neither is a field-calibrated estimate; the slow sensitivity does
  not propagate into stored FaIR. The new ERW backup explains this with 10/30/100
  year curves and literature (also He & Tyka 2023, DOI 10.5194/bg-20-27-2023).
- Slide 16 has a dated emit/wait/remove sequence, a separate zero GWP100 balance,
  and an unclipped forcing plot with warming/cooling areas. The toy pulse-eq
  value is now on the slide defining the metric, not on this introductory plot.
- Slide 22 is a five-stage evidence/tool workflow. The new final core slide is
  **Thank you** after discussion. It now reuses the actual SETAC `_closing()`
  composition through `reused.thank_you()`: two-column summary/contact/funding
  layout, adapted four-case table and conclusions, Seoul event/host text, and
  unchanged PSI contact and UPTAKE/EU acknowledgement. The inherited SETAC
  two-case result table/ranking/outlook are replaced. The EU emblem is served
  through the Seoul shared-asset allowlist. Presenter pacing uses keys for discussion and
  closing; do not restore the assumption that discussion is the last core page.
- Six technical backups now cover matrix equations, dated characterization,
  provenance, pulse-equivalence, ERW kinetics and root-attribution closure.
- The browser script now captures all pages and exports both a 25-page core PDF
  and a 31-page `_with_backup.pdf`. Re-run it after changes.

The user also requested an autonomous quality pass to make this a clear,
well-argued, logically structured, visually attractive and pedagogical lecture,
with sufficient technical backup and without vague or cryptic claims. That pass
is complete for the current brief; the revised deck is ready for user review.
Continue from this state if further feedback arrives. Source app/result bundles
remain unchanged.

Latest verification on 27 October: **212 full-suite tests passed**, **87 focused
Seoul tests** (including six backup pages), and browser QA passed all **31 pages**
with zero page errors/failed requests/slide-boundary overflows. Core and full
PDFs contain **25** and **31** landscape pages. All source/workbook hashes remain
consistent; extraction preserves the existing scientific totals. The original
local preview remains running on port 8057.

## Purpose and audience

Prepare Romain Sacchi's guest lecture, **“Why timing matters in life cycle
assessment”**, for Jooyoung Park's graduate LCA course and research group at
**Seoul National University, 30 October 2026**. Context came from the user's
conversation with Jooyoung Park in their PSI inbox, read during this session.
The audience is approximately 20–25 graduate students, mostly new to LCA,
plus researchers. The precise session time/platform is not recorded here;
consult the original correspondence if that becomes necessary.

The intended learning outcome is to understand **why the timing of production,
emissions and removals matters**, and to distinguish:

1. **Current static LCA:** a present-day production system and an aggregate
   life-cycle climate score.
2. **Prospective static LCA:** conditional future production conditions,
   retaining a snapshot treatment of the life cycle.
3. **Time-explicit LCA and climate assessment:** dated exchanges in changing
   production systems, followed by their climate responses and a deliberately
   chosen climate metric.

Explain the respective roles of ecoinvent, IAM models and scenarios, premise,
TRAILS, Brightway and FaIR. Include enough tooling to make a reproducible
workflow understandable, without turning the lecture into a software tutorial.
Explain the difference between a dated inventory characterized with GWP100 and
an actual climate-response trajectory.

## User decisions to preserve

- **70 minutes teaching + 20 minutes open discussion.** Teaching includes two
  three-minute discussion pauses: current static → prospective static, then
  prospective static → time-explicit. Keep the pacing metadata coherent.
- An **interactive web presentation inside the existing portal**, reusing its
  design, layout, figures and relevant teaching components, including IAM
  workshop material. This is not a PowerPoint task or a new website project.
- **The same four interventions, in this order, throughout:** DACCS, BECCS,
  coastal enhanced rock weathering (**ERW**, sometimes typed “EWR” by the user),
  and **cement + CCS**. Earlier discussion mentioned broader CCS/CCUS; the
  later, more specific four-case selection takes precedence.
- Better visuals, an interesting teaching narrative and fewer redundant slides.
  The latest revision deliberately consolidated repeated diagrams, reference
  cards and chart pages. Do not restore the previous 35-slide structure merely
  because old screenshots or an earlier draft contain it.
- **Less emphasis on formulas.** The user initially allowed equations more room,
  then requested fewer. Formal equations are now in backup; the core uses
  diagrams, comparisons and interactions.
- **Speaker notes, persistent teaching/discussion timers and PDF export.**
  **No handout or exercises.** Discussion prompts are intentional.
- The user confirmed premise's **coastal** weathering inventory and explicitly
  requested checking it against literature and refining it if needed.
- The latest content request was to **introduce CO₂-pulse-eq to address the
  pitfalls of GWP in time-explicit assessment**. This is now implemented;
  preserve the qualifications below.
- The user asked to run it locally. Local preview was left running. There has
  been no commit, push or deployment of this lecture in this session.

The last user feedback before requesting this handover was “not too bad,”
followed by requests for better visuals, fewer redundant slides and the
CO₂-pulse-eq concept. There is no unanswered scoping question or blocked action.
Future work should continue from the implemented deck, guided by further user
feedback, rather than restart its design.

## Transfer the working tree, not just the current commit

At handover, branch `main` is based on commit
`39d451633d0a5e40915c454dd928f1d0b5938b91`. **The lecture work is uncommitted.**
A clean clone at that commit will not contain the new app. A patch made only
with `git diff` will also miss the untracked files. Transfer the complete
working tree, or include these changes in a commit through the user's chosen
handoff process; this document does not itself imply a commit was created.

Existing modified files at handover:

```text
README.md
THIRD_PARTY_NOTICES.md
portal/landing.py
portal/presentations.yaml
portal/wsgi.py
tests/conftest.py
tests/test_portal.py
```

New files/directories that must be transferred, including binary workbooks:

```text
apps/seoul_2026/                 # Entire directory, particularly data/ and assets/
scripts/visual_check_seoul.py
tests/test_seoul_2026.py
CODEX_HANDOVER_SEOUL_2026.md
```

The app README also now links to this handover. Inspect the actual git status
before subsequent work; it may have changed since this snapshot. Preserve
unrelated changes. The earlier source lectures and their result bundles were
reused without editing them.

`build/`, `venv/`, `.venv/` and environment files are ignored. A checkout does
not transfer the virtual environment, generated PDFs/screenshots or scientific
calculation workspace. The presentation can regenerate its PDF from the app.

## Run on another computer

From the repository root, create a fresh environment. The root README recommends
Python 3.13; the original development `venv` used Python 3.11. Install the
repository requirements rather than copying that machine's environment.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
.venv/bin/gunicorn portal.wsgi:application --workers 1 --threads 4 --bind 127.0.0.1:8057
```

Use the **combined WSGI application**, which sets the mounted Dash prefixes
before importing the apps. Set any custom prefix before import, not afterward.
No PSI inbox access, ecoinvent installation, TRAILS installation or background
LCA database is needed to **serve and edit the existing presentation**. Its
scientific figures read stored result artifacts in this repository.

Routes, using port 8057:

| Purpose | URL |
| --- | --- |
| Audience deck | `http://127.0.0.1:8057/seoul-2026/` |
| New pulse-equivalence concept | `http://127.0.0.1:8057/seoul-2026/#slide-18` |
| Speaker notes and timer | `http://127.0.0.1:8057/seoul-2026/presenter` |
| Health and ordered slide keys | `http://127.0.0.1:8057/seoul-2026/health` |
| ERW literature/inventory/calculation review | `http://127.0.0.1:8057/seoul-2026/erw-review` |
| Reviewed calculation foreground | `http://127.0.0.1:8057/seoul-2026/erw-inventory.xlsx` |

`#slide-N` is **zero-based**. The port is a local convention, not a requirement.
The original machine's server was responding at handover; its process and PID
do not transfer. Restart/reload the local worker after Python edits, and wait
for `/seoul-2026/health` to respond before browser QA. An immediate request
during a Gunicorn reload can receive a transient connection reset.

## Current implementation and narrative

There are **26 core pages: 24 teaching pages totaling exactly 4,200 seconds,
then one 1,200-second discussion page and an untimed thank-you. Six backup pages
make 32 total.**

| Zero-based index | Stable key | Role |
| --- | --- | --- |
| 0 | `cover` | Opening question and lecture identity |
| 1 | `why-time` | Opening motivation: aggregate inventory, long-lived systems and climate timing, with three linked references |
| 2 | `carbon-atlas` | Carbon origins/destinations, services and references |
| 3 | `supply-chain` | One connected background; introduce ecoinvent |
| 4 | `current` | Four present-day scores |
| 5 | `mechanisms` | Visual ledger: removal, burdens and avoided release |
| 6 | `pause-current` | Three-minute discussion: why today's suppliers are insufficient |
| 7 | `pathways` | Same target year, different pathways |
| 8 | `iam` | Connected human/natural systems |
| 9 | `scenario` | Society, model and policy layers |
| 10 | `suppliers` | Interactive IAM/premise supplier transformations |
| 11 | `future` | Same four cases in a 2050 snapshot |
| 12 | `pause-future` | Three-minute discussion: why a future snapshot misses timing |
| 13 | `clocks` | Four dated life-cycle structures |
| 14 | `trails` | Temporal routing and annual matrices |
| 15 | `inventory` | One annual/cumulative inventory toggle |
| 16 | `delay` | Equal aggregate GWP100 totals, different forcing histories |
| 17 | `response` | Four forcing responses; adjustable displayed horizon |
| 18 | `pulse-equivalence` | Fixed-calendar-window CO₂-pulse-eq concept |
| 19 | `coast` | Coastal cross-section: deployment, dissolution, transport, uptake |
| 20 | `erw-sensitivity` | Change only ERW uptake duration, delay and realization |
| 21 | `lenses` | Which question each LCA treatment answers |
| 22 | `workflow` | One ecoinvent/IAM/premise/TRAILS/FaIR workflow |
| 23 | `sources` | Literature, source lectures and inventory review |
| 24 | `discussion` | Twenty-minute open discussion, beginning with the lab's ERW study |
| 25 | `thanks` | Untimed closing and contact |
| 26–31 | `matrix-equations`, `temporal-equations`, `provenance`, `pulse-equation`, `erw-timing-evidence`, `root-attribution` | Backup |

Use stable keys / `SLIDE_INDEX` / health metadata for code and checks where
possible. Some pacing tests intentionally assert the discussion locations and
core count, so update them if the narrative genuinely changes.

### Where to edit

| File | Responsibility |
| --- | --- |
| [deck.py](apps/seoul_2026/deck.py) | Slide metadata, durations, notes, content dispatch and rendering |
| [visuals.py](apps/seoul_2026/visuals.py) | Case order/colours, code-native SVG diagrams, ledger and case prompts |
| [reused.py](apps/seoul_2026/reused.py) | Extract/rewrite existing workshop components |
| [comparison.py](apps/seoul_2026/comparison.py) | Stored result readers and four-case Plotly figures; toy pulse illustration |
| [contributions.py](apps/seoul_2026/contributions.py) | Signed static/temporal activity-type attribution, provenance checks and closing stacks |
| [technical.py](apps/seoul_2026/technical.py) | ERW timing and attribution backup figures |
| [app.py](apps/seoul_2026/app.py) | Routes, callbacks, navigation, asset allowlist and print-deck construction |
| [layout.py](apps/seoul_2026/layout.py) | Shared component helpers, cover, sources and backup equations |
| [erw.py](apps/seoul_2026/erw.py) | Assumed uptake/metal-release profiles and mass-preserving tails |
| [styles.css](apps/seoul_2026/assets/styles.css) | Base lecture styles |
| [z_story.css](apps/seoul_2026/assets/z_story.css) | Latest visual layouts; loaded after the base styles |
| [presentation.js](apps/seoul_2026/assets/presentation.js) | Keyboard, fullscreen, note synchronization and print readiness |
| [presenter.html](apps/seoul_2026/templates/presenter.html) | Notes UI and persistent 70/20-minute timers |

The app directly imports helpers/results/assets from `apps/workshop/`,
`apps/setac_2026/`, `apps/lca_time/` and `apps/ccus_webinar/`; transfer the full
repository, not just the Seoul folder. The app's shared-asset allowlist and URL
rewriting must remain consistent with its mounted prefix.

The recent visual revision replaced repeated four-card layouts with the carbon
atlas, qualitative balance ledger, coastal scene and method-choice diagram.
Four-panel charts deliberately remain consistent for result comparisons.
Do not introduce a second identical supply-network map, functional-unit page,
workflow or separate annual/cumulative page. Keep native SVG/code visuals
editable. Account for CSS selector specificity inherited from SETAC; generic
paragraph rules can otherwise override new panel font sizes. Avoid index-based
CSS when a `data-slide-key` selector expresses the intended target.

## Scientific interpretation that must survive the handoff

These are **cross-study teaching examples, not a harmonized technology ranking**.
Keep the native service, reference, cohort and package differences explicit.

| Case / colour | Service and reference |
| --- | --- |
| DACCS / blue `#3292b5` | One net physical tonne CO₂ stored after transport loss; no-DAC reference |
| BECCS / green `#3e7654` | One net physical tonne stored; standing forest plus equivalent Northern European market energy |
| Coastal ERW / amber `#c18a1b` | Fixed **1.25 t rock deployment**, one tonne reference eventual atmospheric uptake potential; no extra deployment |
| Cement + CCS / purple `#7656a8` | **One tonne grey clinker**, CCS minus equivalent unabated clinker production |

- A physical tonne stored is not a tonne of net life-cycle climate benefit.
  Capturing kiln carbon mainly avoids release; it must not be labelled as
  atmospheric removal. Retain the cement inventory's non-fossil fuel fraction.
- Native temporal cohorts are 2030 for DACCS/BECCS/ERW and 2035 for cement.
  Project-relative axes do not relocate the original inventories in calendar time.
- Current/future snapshots are 2025/2050. Different temporal cohorts/lifetimes
  mean snapshot-to-temporal score differences do not isolate timing alone.
- Read DACCS/BECCS numerical results through **`apps.setac_2026.results`**, which
  isolates the updated result reader and caches. The older `lca_time` release
  has different results/contracts. The toy delayed-pulse illustration
  intentionally uses `apps.lca_time.workshop.results`, which has the required
  reference pulses at several dates.
- Cement uses approved webinar release bundles: `main` for 2025 and
  `2050-SSP2-PkBudg1000` for the future snapshot. Its forcing comparison is
  the difference of released CCS and BAU response summaries, not a newly paired
  ensemble uncertainty calculation.
- Never reset a cumulative balance to zero at the left display boundary.
  Preserve all earlier contributions and late tails. A shorter display horizon
  hides part of a trajectory; it does not change the underlying model.
- Keep land/forest counterfactuals, displaced energy and supply-chain burdens.
  Cleaner markets can reduce both burdens and substitution credits.

### CO₂-pulse-eq: what has and has not been implemented

The concept uses **integrated radiative forcing over a fixed calendar window**:

```text
M_equivalent = M_reference ×
  integral(window_start → window_end, ΔRF_inventory) /
  integral(window_start → window_end, ΔRF_reference_CO2_pulse)
```

Both responses use the same climate background and calendar window; the
reference pulse has a declared date. In a full TRAILS calculation, compute
ratios **within each FaIR configuration before summarizing quantiles**.
Ordinary aggregate GWP100 assigns each emission/removal a fresh 100-year
horizon, so equal CO₂ masses at different dates can cancel in the aggregate
despite interim warming. This fixed-window metric preserves those dates.

The worked toy example emits +1 t CO₂ in 2030 and removes −1 t after 0, 20 or
50 years. Aggregate CO₂-only GWP100 is zero in each case. The displayed
2020–2100 equivalents against a 2030 pulse are approximately 0, +232 and
+632 kg CO₂-pulse-eq respectively. **These are illustrative ratios of stored
median marginal-response areas, not medians of ensemble-level ratios.**
The worked example caption on the metric-definition slide and the notes disclose this. Do not relabel these as full TRAILS
ensemble results. The four-case metric diagram is explicitly schematic;
four new harmonized technology pulse-equivalent scores have **not** been calculated.

Equal integrated forcing does not imply identical forcing/temperature paths,
physical removal, permanent storage or climate neutrality at every date.
State the background, window and reference year with every equivalent. This
definition is not GWP* and is not presented as a universal replacement for GWP.

Sources already consulted and linked in the deck:

- [TRAILS fixed-window definition](https://trails.readthedocs.io/en/latest/theory.html#fixed-window-co2-pulse-equivalence)
- [Levasseur et al. (2010), dynamic LCA](https://doi.org/10.1021/es9030003)
- Existing SETAC lecture's pulse-equivalence teaching material and documentation.

## ERW review, calculation state and external inputs

The source is **coastal** ERW, not a terrestrial spreading inventory. The
original premise workbook was preserved. Literature review checked the
Foteinis et al. paper and SI, marine-weathering synthesis, and air–sea exchange:

- [Foteinis et al. 2023](https://doi.org/10.1021/acs.est.2c08633)
- [Supporting inventory, Table S1](https://doi.org/10.1021/acs.est.2c08633.s001)
- [Geerts et al. 2025](https://doi.org/10.5194/bg-22-355-2025)
- [Zhou et al., online 2024 / issue 2025](https://doi.org/10.1038/s41558-024-02179-9)

Repo artifacts under `apps/seoul_2026/data/`:

- `coastal_erw_temporalized.xlsx`: source-normalized foreground variants.
- `coastal_erw_ei312.xlsx`: exact linked calculation variant for ecoinvent 3.12.
- `erw_review.json`: evidence, refinements, limits and calculation summary.
- `erw_comparison.json`: calculated snapshots, dated inventory and FaIR response.
- `erw_contributions.json`: new closing first-tier static and responsible-root temporal attribution.

Implemented refinements: use source-SI medium-voltage grinding rather than
inherited low-voltage electricity; correct exact EURO 3/5/6 diesel truck names
for ecoinvent 3.12; aggregate duplicate supplier coordinates after the voltage
correction while retaining quantities; keep nickel in ocean water and date its
conservative upper-bound release separately. Default uptake uses shrinking-core
dissolution plus a discrete exponential air–sea delay, with complete tails.
Its durations/lags are scenario assumptions, not site-calibrated measurements.

The 2023 reference potential already contains conservative composition/buffering
assumptions. The extra realization sensitivity is not a universal second
carbonate correction. The retained spreading proxy, quarry transport proxy,
missing restoration rows, local geochemistry, metals and ecological effects
remain explicitly qualified; do not invent site evidence or restoration credits.

Actual calculations used ecoinvent **3.12 cut-off**, premise **2.5.4** and
TRAILS **1.1.1**, with REMIND-EU SSP2-PkBudg1000. ERW FaIR scenario:
`REMIND|SSP2-EU21-PkBudg1000`. The climate run used the 841-configuration
ensemble, storing median responses. Method:
`IPCC 2021 (incl. biogenic CO2) - climate change: total (incl. biogenic CO2) - global warming potential (GWP100)`.

Import has zero unlinked exchanges. Dated LCI uses **fixed routing depth one
with complete residual background solves**, not full upstream temporal
convergence. Static/temporal GWP closure error is about `9.42e-6 kg CO2-eq`
per 1.25 t deployment, below the `0.001 kg` check. Snapshot scores are about
−956.26 (2025), −975.81 (2030) and −990.90 (2050) kg CO₂-eq per deployment.
The earlier fixed published 51 kg screening footprint is no longer used.

Live ERW controls change only its foreground uptake profile, holding upstream
inventory fixed and leaving the other three cases unchanged. They do not rerun
LCA or FaIR; they do not model a matched particle-size/energy optimization.

### Only needed if recalculating scientific results

Original-machine inputs, **not portable dependencies of the web app**:

```text
/Users/romain/GitHub/premise/premise/data/additional_inventories/lci-coastal-enhanced-weathering.xlsx
/Users/romain/GitHub/premise/export/trails/remind-eu-SSP2-PkBudg1000-all-years-20261014/trails_remind-eu_SSP2-PkBudg1000.zip
/Users/romain/GitHub/trails
/opt/homebrew/Caskroom/miniforge/base/envs/premise/bin/python
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python
```

The package hash is
`bd298b3e30d84adbb9dfe11c87654a318d7b8aed94e0357fa932a6e3dbcf9780`.
Other workbook and FaIR input hashes are recorded in the result/review JSON.
Raw licensed backgrounds were not added to the repository. Obtain appropriately
licensed inputs separately if recalculation is necessary; do not redistribute
them with the presentation.

Reproduction entry points:

1. [refine_erw_inventory.py](apps/seoul_2026/scripts/refine_erw_inventory.py),
   run in a premise/Brightway environment with `openpyxl`, `numpy` and `bw2io`.
   It accepts `--source /new/path/to/source.xlsx` and `--output ...`.
2. [calculate_erw_comparison.py](apps/seoul_2026/scripts/calculate_erw_comparison.py),
   run in the compatible TRAILS environment with `--climate`. Its `ARCHIVE`
   constant is still an original-machine absolute path; adapt it before use
   on another computer. Only `--climate` is currently a CLI option.
3. [extract_erw_contributions.py](apps/seoul_2026/scripts/extract_erw_contributions.py)
   exports the root attribution without changing the workbooks or climate
   results. Use the TRAILS environment; its `--package`, `--foreground` and
   `--output` flags let you adapt local paths. Keep the selected package aligned
   with the comparison record. The import and static/annual closure checks must pass.

The calculation extracts selected 2025/2030/2050 matrices under ignored
`build/seoul-erw-calculation/`. If changing the archive, use a fresh extraction
workspace rather than trusting files skipped because they already exist.
Running without `--climate` produces a smaller screening record, insufficient
for the current app's stored response views.

Do **not** rerun these generators for visual/copy changes. Regenerating a
workbook can change its binary hash even when quantities appear identical.
`comparison.erw_results()` deliberately rejects result/workbook hash mismatches.
If changing scientific inputs, regenerate the linked workbook, full results
and review together, rerun checks, and restart cached readers. Follow applicable
TRAILS/premise/Brightway skills and repository instructions if present on the
new machine. No Brightway database was written by the completed calculation.

## Validation, exports and what remains

Previous implementation verification, 25 October 2026 (superseded by the new review below):

- Full test suite: **197 passed**. Focused Seoul suite: **72 passed** after the
  final content/layout changes.
- Browser QA visited **all 28 pages** at 1600×900, with no reported page errors,
  failed requests or slide-boundary overflow. It exercised case order, notes
  synchronization, timer persistence, navigation, toggles, ERW sensitivity,
  delayed removal, horizon controls and actual export preparation; it also
  captured laptop/mobile views.
- Exported core PDF: **24 landscape 16:9 pages**, approximately 2.3 MB.
- Unused-import checks and `git diff --check` passed.

Run after relevant implementation changes, from the repo root:

```sh
.venv/bin/python -m pytest -q tests/test_seoul_2026.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/visual_check_seoul.py --url http://127.0.0.1:8057/seoul-2026/
```

Use a trailing slash in that browser command. The browser script reads the
health manifest, prepares the real print deck and writes ignored artifacts to
`build/seoul-review/`, including:

```text
SNU_2026_Romain_Sacchi_Time_explicit_LCA.pdf
SNU_2026_Romain_Sacchi_Time_explicit_LCA_with_backup.pdf
browser-report.json
slide-NN.png
laptop-1280.png
mobile.png
presenter.png
```

The original workspace also has `speaker-notes.html` and
`erw-inventory-review.html` snapshots there. Those two standalone HTML files
were saved manually from the live routes; the browser script does not update
them. For refreshed standalone notes, save `/presenter`, change its audience
link to the PDF filename and explain that slide selection is manual offline.
The live notes page remains the canonical synchronized presenter UI.

PDF export uses default slide states, not the current live selections, and
waits for fonts, images and charts. **Include backup** exports 35 pages (the process carousel expands to four pages).
Notes use local-storage keys `snu-2026-slide` and `snu-2026-timer`; keep audience
and presenter on the same origin/browser for synchronization. The presenter
page is public, without access control. Manual note selection does not navigate
the audience deck.

There is no known blocking defect or outstanding authorized implementation
step at this handover. The current result is ready for the user's next review.
If asked to refine it, inspect it running first, preserve the scientific
qualifications and teaching requirements above, make the requested changes,
then refresh the affected checks/PDF. Do not claim full temporal convergence,
site-validated weathering performance or newly calculated four-case ensemble
pulse-equivalents. Those are possible future scientific tasks, not completed
work. Publishing/deployment is separate from the local-preview request.

28 October verification: **213 full-suite tests passed** (88 focused Seoul tests).
Browser QA passed all **32 pages**; core/full PDFs have **26/32 pages**.

28 October opening transition edit: the user requested removal of the visible
sentence “Diagram is schematic; a static LCA can include every life-cycle
stage.” It has been removed from slide 2; the three on-slide references remain.
Slide 3 (`carbon-atlas`) is now “Changing supply systems and carbon timing:
four cases”. Every route pairs its relevant supply system with its carbon
timeline, explicitly carrying forward the two timing questions. Its speaker cue
and notes explain the transition. Metadata keys/counts/pacing are unchanged.

## Standing style preference: no small explanatory footers

The user requested removing small-font sentences at the bottom of **all**
slides, including technical backups. `editorial.py` now applies
`clean_audience_footer()` in `render_slide()` for both screen and print. It
removes explanatory source/caption prose, panel footnotes, evidence notes,
ledger/lens footers, the small metric example/reporting strip and timing-control
caption. Bibliographic links remain as `.slide-references`; intro references
and the bibliography page remain visible. Compact chart metadata, units and
legends are retained. Do not restore explanatory footer prose.

The `/presenter` route now uses `presenter_slides()` to include removed figure
context in the speaker notes without mutating metadata. The reused
`context-note` callback output stays mounted but hidden; removing its ID would
break the scenario callback. ERW timing assumptions and cement CCS-minus-BAU
context appear in compact chart headers. Net GWP100 and warming/cooling keys
are in legends. Print selections are readable header labels rather than
“PDF default” prose. The technical table's units are a table caption. The
closing retains the funding credit as a compact EU/grant label.

No scientific results, native services, event dates, routing or climate
calculations changed. Current counts and 70+20-minute pacing are unchanged.

## 28 October: slide 4 process maps

The user requested main CO₂, material and energy flows from capture to storage
for each option, using a carousel if helpful. Slide key `supply-chain` remains
at audience index 3; its title is now “Follow carbon, materials and energy to
storage”. `processes.py` generates five-stage, code-native SVG maps and a
shared teal CO₂ / slate material+alkalinity / dashed amber energy key. Side
streams show capture materials, energy, transport losses, BECCS heat/power
exports and residual stack emissions, clinker, and coastal ERW mineral residue.
ERW explicitly follows reactive rock → dissolution → alkalinity → ocean carbon,
with atmospheric CO₂ entering through air–sea exchange. It does not send rock
carbon into a geological-storage route. These are selected qualitative flows,
not new inventory quantities or proportional Sankeys; source data are unchanged.

`presentation.js` delegates tab/case-flip clicks and keyboard navigation; the
carousel retains one visible panel, supports wraparound, and tab arrow/Home/End
keys stay within this slide. There is no new Dash callback. No small explanatory
footer was added. The main figure key and native service remain visible.

PDF expands this one audience slide to **four full-size pages** via
`pdf_deck()` and `render_slide(process_case=...)`, independent of live selection.
There remain **26 audience slides + 6 backups**, and pacing remains 70+20 min.
Current core/full PDF lengths are **29 / 35 pages**. Health exposes `pdf_pages`
and `pdf_all_pages`; browser QA uses these separately from audience counts.
Screenshot artifacts `process-0.png` through `process-3.png` capture each case.
The browser script also verifies tab switching, wraparound, keyboard behavior
and all four print selections. The focused suite now contains **89 tests**.

Process-carousel verification: **89 focused tests passed**; browser QA passed all
32 audience/backup slides with no page errors, failed requests or slide-boundary
overflow. Core/full exports were regenerated and confirmed at **29 / 35 pages**.

## Slide 4 numerical flow labels and cement interpretation

The user subsequently requested amounts on arrows and an explanation of the
cement + CCS boundary/results. `processes.process_quantities()` now supplies
physical quantities for the 1400×520 diagrams. Arrow widths remain schematic.
DACCS/BECCS reuse SETAC `case_inventory()`; numbers are per net physical tonne
stored, not per tonne captured. DAC's 1.854 MWh includes heat-pump electricity;
12.24 GJ is its delivered heat, not an additional heat purchase. Compression,
transport and injection use a single 139 kWh total. BECCS distinguishes forest
uptake, dry wood, internal heat, exported energy and stack/transport losses.

ERW reads `data/erw_process_quantities.json`, a hash-checked selected extraction
from the unchanged linked workbook. Reproduce using
`scripts/extract_process_quantities.py` in the premise environment (openpyxl).
Per 1.25 t rock: 93.120605 kWh foreground electricity, 24.597464 MJ direct
machinery diesel, 76.03 t-km freight, 0.49612 m³ water, 1 t eventual gross uptake
potential and 3.2875 kg conservative Ni mobilization bound. Direct diesel
excludes fuel embedded in transport/spreader providers. Alkalinity is not
independently quantified or credited again. No new dissolution or climate run.

Cement's quantitative diagram is explicitly a **2025 published-SI fuel-carbon
illustration per tonne clinker**. It reads only public BAU/capture data plus
published normalized gas-boiler utility coefficients. Do not copy exact private
engineering quantities into it. Displayed fuel CO₂: ~402 kg generated, 362 kg
captured, 339 kg stored; ~40.2 kg uncaptured and 23.0 kg storage-chain loss.
Calcination/capture-boiler CO₂ are additional streams left unquantified in this
illustration, although included in approved LCA results. The rounded ~1.3 t
chalk slurry was explicitly approved earlier; it is not pure dry limestone or
a stoichiometric basis for calcination. Capture utilities 41.9 kWh electricity
and 2.77 GJ gas input have a DIFFERENT denominator: per tonne CAPTURED CO₂,
clearly stated on their arrow card. They cannot be added to the stored LCA.
Speaker notes explain these source/basis distinctions; no footers were added.

The explanation given to the user: clinker at Aalborg (1 t), raw materials,
fuels, kiln, capture, conditioning, transport, North Sea storage, residuals,
upstream suppliers, modelled construction/replacement/end-of-life and useful
surplus-heat substitution. Concrete use/carbonation are outside the clinker
service. Current 2025 GWP100: BAU +888.62, CCS +165.92, difference −722.69 kg
CO₂-eq/t clinker. Future 2050 PkBudg1000: +689.50, −80.46, difference −769.96.
Temporal 2035–2064 campaign differential sum −750.16. Negative difference means
improvement versus unabated production; mineral/fossil capture avoids release,
while non-fossil fuel storage can contribute removal. This is not a harmonized
ranking against other native services. The future snapshot/campaign difference
also includes foreground/scenario/lifetime effects, not timing alone.

The focused suite now has 90 tests, including physical carbon closure, heat
balance, ERW service scaling and the partial cement fuel-carbon balance.
Audience counts and pacing are unchanged; PDF counts remain 29/35 pages.

Numerical-label verification: 90 focused tests passed; browser checks passed all
32 audience/backup slides, with no errors, failed requests or slide-boundary
overflow. PDF exports refreshed at 29/35 pages. Signed temporal absolute cement
totals are BAU +723.05 and CCS −27.11 kg CO₂-eq/t clinker (difference −750.16).
Equipment coverage remains incomplete: separate capture-plant construction is
not quantified; do not imply the drawings or infrastructure model are exhaustive.

## Cement fossil / non-fossil visual distinction

The user requested this distinction on slide 4 and other cement result slides.
`carbon.py` defines a separate carbon-origin palette: fossil/mineral CO₂ brown
`#ad603d`, non-fossil CO₂ green `#3e7654`, atmospheric uptake teal `#008a82`,
other/unassigned effects grey `#91a4ad`. Purple remains the cement technology
identity. Process connectors use solid brown versus dotted green, including
separate numbers through capture, storage, uncaptured emissions and chain
losses. Numbers still cover ONLY the public 2025 fuel-derived carbon fraction;
unquantified calcination/boiler CO₂ remain explicit. The legend changes with the
carousel selection, including each expanded PDF page. Public-origin pools close
to every prior aggregate physical quantity; no private input is newly exposed.
The opening carbon atlas and mechanisms ledger also distinguish the origins.

`cement_origins.py` adds an independently closing alternative plot partition.
Current/prospective/dated/ERW-sensitivity cement charts default to **CO₂ origins**;
Plotly buttons restore **Activities** (signed root types) or **Net only**, as
appropriate. The alternative traces are mutually exclusive; NEVER add the
flow view to the existing stage view. Both views and all net values remain in
the figure. Other three technology charts retain their original decomposition.
The origin key is in the cement panel header; plot margins preserve comparable
chart domains. The temporal-page title is now “What drives the GWP score, and
when?” to accommodate both root and origin views.

Scope matters: static origin colours classify only explicitly named CO₂
foreground subprocesses (including calcination and its storage correction).
Other supplier effects remain grey without inferred carbon origin. Dated
origin colours classify the released FULL-system elementary-flow table, with
signed CCS-minus-BAU values per species/year. Non-fossil CO₂ and soil/biomass
stock exchanges are green; `Carbon dioxide, in air` is a separate atmospheric
uptake category, not silently netted against releases. Methane and other gases
remain “Other effects”. Both scope labels are visible in chart headers;
presenter notes explain that static and temporal origin scopes differ. Each
view closes independently to the unchanged net at every year/snapshot.

The FaIR result lacks an origin decomposition. Its purple curve stays combined;
a brown/green key explicitly says “Combined response”. No fossil/non-fossil
forcing fractions or response curves were invented. Technical net tables carry
the combined-origin key as well. No LCAs or climate simulations were rerun.

Focused tests now number 95 and cover named-flow classification, independent
annual/snapshot closure, mutually exclusive view visibility and physical
origin-pool conservation. Browser QA additionally clicks both Plotly view
buttons on current, future, temporal and ERW-sensitivity pages and checks the
active traces. Core/full PDF counts remain 29/35 (26 audience slides + backups).

Carbon-origin verification: 95 focused tests passed; all 32 audience/backup
slides passed browser checks, including view switches, with no page errors,
failed requests or slide-boundary overflow. Refreshed PDFs contain 29/35 pages.

## Slide 5: harmonized signed current-static contributions

The latest user instruction supersedes the current-slide-only origin default:
slide 5 (`current`, audience index 4) now uses **signed 2025 activity-type stacks
for all four cases**, one common `contributions.TYPES` palette/legend, one shared
−1600…750 kg CO₂-eq axis, and dark net diamonds. Every case shows non-zero
positive and negative contributions; their signed sum reproduces its original
current-static score. Technology colours remain on headers and net-number text.
Cement opens in **Activities** here, with its CO₂-origins view still selectable.
Other cement result slides keep the previous origin-view default.

`contributions.static_figure/static_panels` now accept a `years` tuple and
`default_view`; the current slide passes `(2025,)` / `activities`, while the
prospective slide retains its existing `(2025, 2050)` / `origins` defaults.
`cement_origins.with_origins` accepts the explicit initial view and initializes
both trace visibility and the active Plotly button accordingly. Speaker notes
explain the current-page exception. No scientific quantities or scores changed.
Browser QA checks both signs on all current panels, switches the cement view
and restores **Activities** before capturing the slide. PDF uses the same
Activities default. The focused suite now has **96 tests**, including screen
and print assertions for category colours, common scale, signed closure and net
diamonds on the actual current-slide component tree. PDF lengths remain 29/35.

Slide-5 verification: 96 focused tests passed; browser QA passed all 32 slides
with no errors, failed requests or slide overflow. The current page was captured
with all four activity stacks visible. Both PDFs and offline notes are refreshed.

## Slide 5: two CO₂ flow names only

The user then requested only **“fossil CO₂”** and **“non-fossil CO₂”** for CO₂
flow labels on this slide. `co2_terms=True` is scoped to the current page;
other pages retain their previous terms. `CURRENT_TYPES/current_contributions`
provide selected named CO₂ effects plus supplier/activity effects, using a
shared brown fossil / green non-fossil palette. The current cement header and
its alternative view also use these two names; atmospheric uptake is combined
with the requested non-fossil terminology without netting opposite signs.

Known DACCS/BECCS transport CO₂ and BECCS residual stack CO₂ are separated using
the existing public physical inventory, then subtracted once from the original
activity groups. Remaining direct effects stay separate. DACCS upstream forest
supplier effects remain in Biomass supply, rather than mislabelling a whole
supplier GWP as a CO₂ flow. Cement uses explicitly named foreground CO₂
subprocesses, including calcination as fossil CO₂; remaining supplier effects
keep their activity labels. This is not a complete species split of upstream
suppliers. All four signed sums and net scores remain unchanged. Positive and
negative CO₂ are separate traces under the same origin name. Shared palette,
scale, diamonds and the current-page Activities default are retained.

The focused suite contains 97 tests, including allowed CO₂ names in both visible
and alternative traces, physical residual-stack/transport amounts, signed
closure and screen/print colour consistency. Browser view-switch checks compare
trace visibility with each button's explicit partition, since both current
views now contain the same CO₂ labels. Export page counts remain 29/35.

Two-name CO₂ verification: 97 focused tests passed; all 32 slides passed browser
checks, including cement view switching, with no errors or overflow. PDFs and
offline notes refreshed; the default slide screenshot is `slide-04.png`.

## DACCS biomass correction; case geography and dates

The user identified ambiguity in the brown DACCS biomass-supplier segment and
asked where/when the four cases operate. DACCS slide-5 attribution now uses the
**stored 2025 SSP2-NPi biosphere-flow table** matched by exact provenance ID,
rather than using a forestry activity's net GWP as a CO₂ uptake proxy. The flow
partition closes independently: non-fossil negative −1533.4406756, non-fossil
positive +593.7039135, fossil positive +92.9564979, other GHG effects
+15.6037614 kg CO₂-eq per native service, net −831.1765028. Atmospheric uptake,
biomass releases, soil/biomass-stock CO₂ and non-fossil resource corrections are
green. Named fossil CO₂ alone is brown; there is no negative fossil DACCS
segment. The source's residual “Other” stays in Other GHG effects without
inventing its species. No supplier root scores are added to this flow view,
so electricity/biomass emissions are counted once. The other three cases retain
their previous selected-CO₂ plus supplier partitions; do not describe all four
as exhaustive species decompositions. No LCA or climate simulation was rerun.

The regional/date answer given to the user, based on local model contracts:
DACCS and BECCS use Northern European ENC markets (no specific plant site),
commissioned 2030 and operating through 2049. BECCS regrowth extends beyond
operation. Coastal ERW is a generic European RER foreground (no calibrated
coastal site), deployed in 2030 with later dissolution/uptake. Cement is at
Aalborg, Denmark, with North Sea storage, operating 2035–2064. Slide 5 uses
2025 production conditions; prospective-static uses 2050 conditions. These
snapshots are distinct from project commissioning and campaign dates. The
current-slide headings now show the modelled region/site and 2025 explicitly.
The cases are modelled examples, not four identified real operating projects.

DACCS correction verification: 98 focused tests passed; browser QA passed all
32 slides with zero errors/overflow. Both PDFs and offline notes were refreshed.

## Foreground/root boundary: calculation and verification

The user explicitly rejected disaggregating supply-chain CO₂ on contribution
graphs. Do not reintroduce the earlier DACCS full-biosphere-flow view or the
cement temporal CO₂-origin toggle. Only foreground flows receive fossil/non-fossil
labels; suppliers include their entire upstream life cycles, with signed root
scores grouped into electricity/heat, biomass, materials/equipment, transport/
storage, or mining/spreading. Direct non-CO₂ GHGs have their own category.
The fossil/non-fossil process-diagram arrows remain valid: they show foreground
physical routes. Whole-system climate-response curves remain combined.

`extract_cdr_static_roots.py` loads the unchanged generated CDR foreground,
identifies imported foreground activities plus the native DAC operation by
metadata, solves its foreground block, then scores each signed frontier supplier
with the complete static adjoint intensity. Foreground B exchanges are counted
separately. No upstream elementary flows are classified for display. It validates
against both the original saved scores and TRAILS `static_lca()`; errors for
DACCS/BECCS in 2025/2050 were at most ~1.95e-11 kg CO₂-eq.

The original NPi archive path no longer exists on this computer. For 2025, the
script reads the existing trusted TRAILS interpolation cache
`~/Library/Application Support/trails/cache/interp_31c40820e920` without mutation.
It memory-maps ZIP_STORED NumPy members, extracts only 2025, and reconstructs a
static-only package under ignored `build/seoul-cdr-root-extraction/npi-2025`.
Already-flipped matrix signs are retained with CSV flip=0. This reconstruction
is for static attribution only; it does not reconstruct uncertainty or temporal
exchange fields. For 2050, it uses the existing selected PkBudg1000 package.
Both model/case scores match their correct original scenario, not a substituted
2025 PkBudg1000 score. The published JSON records selected matrix/index hashes,
foreground hash, exact method, script hash, TRAILS 1.1.1/source path and timestamp.

Run in the TRAILS environment (the web app needs only the stored aggregates):

```sh
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  apps/seoul_2026/scripts/extract_cdr_static_roots.py --year 2025
/opt/homebrew/Caskroom/miniforge/base/envs/trails/bin/python \
  apps/seoul_2026/scripts/extract_cdr_static_roots.py --year 2050
```

On another computer use `--cache`, `--foreground` and `--package` to supply the
corresponding local licensed inputs. The foreground is the hash-locked
`build/setac-regeneration-20261014/data/inventories/generated/lcss2026-foreground.xlsx`;
its hash is checked against SETAC's public physical-inventory basis. The 2050
package argument is a descriptor, by default
`build/seoul-erw-calculation/selected-package/datapackage.json`.
Do not distribute the private reconstructed background CSVs with the app.

Runtime `foreground_contributions(case,year)` validates source hashes and score
closure. It uses those new CDR roots, existing ERW first-tier intensities and
cement's released foreground/provider subprocesses. Supplier CO₂ remains inside
the supplier's score. For DACCS 2025 the foreground CO₂ balance is approximately
−1000, complete supplier contributions +168.8235, net −831.1765. The electricity
root includes biomass uptake/combustion without separate green/brown upstream
segments. Static charts now share a tighter −1250…350 axis, including both signs
and net diamonds. Temporal root charts no longer expose an origin-flow view;
ERW sensitivity keeps complete net curves. No FaIR runs were repeated.

Final verification: 228 tests passed, including 103 focused Seoul checks;
all 32 audience/backup pages passed browser QA without errors, failed requests
or slide overflow. Core/full PDFs and notes were refreshed (29/35 pages).
