# SETAC Europe LCA Case Study Symposium 2026

**How time integration changes LCA: the case of CDR**

Romain Sacchi (presenter), Tom Terlouw, Karin Treyer, Alvaro Hahn Menacho,
Arthur Jakobs and Christian Bauer. Romain's name is underlined on the cover.

19 October 2026, 14:05, Foyer 3, Bruges. Presentation **1.01.T01** in session
*Advancing Life Cycle Assessment for Carbon Dioxide Removal (CDR)*.

Twelve main slides, timed to **10:00**, leaving two minutes within the 12-minute
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
Use the arrow keys, Page Up/Down, space bar, or navigation buttons. Navigation
stops at main slide twelve; **Backup slides** opens the appendix separately.
Keyboard navigation yields to focused inputs, sliders, buttons and links.

**Presenter** opens notes, the speaking plan and a 12-minute timer in another
tab. Notes follow slide changes in the same browser. The timer starts manually.
Direct slide links use zero-based fragments, e.g. `#slide-9` for pulse equivalence.

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
regrowth tail through 2132. Each has a red cumulative net GWP100 line on a
secondary right-hand axis, including upstream contributions before 2000. Both
cases use the same annual and cumulative scales, with their zeros aligned.

Slide ten uses a three-handle slider spanning **2000–2300**. The handles select
the window start, reference-pulse year and window end, initially **2020, 2030
and 2100**. They move in five-year steps and stay at least five years apart.
The curve, scores, settings and 2100/2300 comparison update together. A comparison
endpoint at or before the selected reference pulse is marked unavailable.

Slide eleven concludes with five takeaway sentences on the left and a thank-you
message, Romain Sacchi’s name, PSI affiliation and email address on the right.
A frame below the takeaways reports net tonnes of CO₂ stored needed for a
−1 t CO₂-eq GWP100 score and a −1 t CO₂-pulse-equivalent score, for both systems.
It divides −1000 by the existing kg-equivalent-per-net-tonne cohort scores.
Both scores include life-cycle GHG emissions and the modeled credits; the
reported tonnes measure physical CO₂ storage needed to meet those climate targets.
GWP100 uses the full dated inventory; pulse equivalence uses the default
2020–2100 window and 2030 reference pulse. These are linearly scaled net-storage
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
| 2 | Does timing change the BECCS–DACCS comparison? | 0:25 |
| 3 | BECCS and DACCS: material, energy and CO₂ flows | 0:45 |
| 4 | BECCS has the lower GWP100 score in 2025 | 1:05 |
| 5 | Future electricity, heat and material supply | 0:55 |
| 6 | CDR scores with 2025, 2030 and 2050 backgrounds | 0:55 |
| 7 | TRAILS: matrices and supply chains through time | 0:50 |
| 8 | When do emissions and CO₂ removals occur? | 1:00 |
| 9 | GWP100 does not distinguish emission dates, but radiative forcing does | 1:00 |
| 10 | Comparing CDR with CO₂-pulse equivalents | 2:15 |
| 11 | Conclusions and contact details | 0:30 |
| 12 | Data sources and model versions | — |

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

## Reused results

`figures.py` reads the existing `apps.lca_time.workshop.results` API. The
[source data contract](../lca_time/data/README.md) documents the reviewed
processed artifacts, assumptions, units and reproduction workflow. No source
table, inventory, model or existing presentation is modified. This app depends
on `apps/lca_time/` being present. The additional sector-mix snapshots are
small aggregate extracts stored in the SETAC app; inventory packages remain local.

- System-flow slide: original `case-pathways.svg` artwork annotated with selected
  operating flows from `system_inventory_2025.json`, the same reviewed inventory
  used by the long deck's detailed BECCS and DACCS diagrams. Values are loaded from
  that source; physical storage is distinct from the subsequent life-cycle GHG score.
- Static snapshots: 2025, 2030 and 2050; SSP2-NPi and SSP2-PkBudg1000.
- IAM context: `data/scenario_context.csv`, a 129-row extract of REMIND-EU
  indicators from the existing scenario explorer's premise 2.4.9 export.
  The adjacent JSON records its source path, hash and premise commit. Source
  values retain °C above 1850–1900, tonnes CO₂/year and million people; chart
  units convert emissions to Gt (World) or Mt (ENC), and World population to
  billions. GMST is the global MAGICC7 median, distinct from the project-level
  FaIR responses later in the talk. The ENC NPi CO₂ series has no 2100 source
  row: it ends at 2090 and is not extrapolated or filled with zero.
  Regenerate with `python apps/setac_2026/scripts/extract_scenario_context.py`.
- Mixes: `data/sector_mixes.csv`, from premise-generated ENC markets at
  2025, 2030, 2035, 2040, 2045 and 2050. The original source-project extractor
  reads each year directly from the reviewed packages; it preserves the original
  market selection and technology classification. All 180 existing rows for
  2025, 2030 and 2050 match `lca_time/data/processed/scenario_sector_mixes.csv`.
  `data/sector_mixes.json` records package and extractor hashes, version metadata
  and baseline verification. Regenerate with
  `python apps/setac_2026/scripts/extract_sector_mixes.py --source-project /path/to/FSLCI_workshop_2026`.
  Display categories below 1% in every sector snapshot across both pathways are
  combined into Other, retaining all shares. Electricity uses high-voltage supply;
  heat uses the single `market for heat, district or industrial` with reference
  product `heat, district or industrial`, in MJ. The export does not distinguish
  the two uses. This is not the DAC heat-pump inventory.
- The current-static bars stack process contributions on either side of zero,
  with diamonds marking the net GWP100 scores. BECCS uses the reviewed
  foreground-step attribution; DACCS uses the existing activity contributions
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
  checked against `/Users/romain/GitHub/trails` (current source 1.1.1); the
  reused case-study calculations remain TRAILS 1.0.1 and were not rerun.
- Temporal and FaIR: complete 2030 cohorts; SSP2-PkBudg1000.
  Temporal categories retain positive and negative annual root scores separately.
  Uptake contains only explicit forest regrowth and DAC; energy includes biomass,
  electricity, compression and avoided energy. CO₂ and stack emissions includes the whole
  residual stack branch and CO₂ transport losses; individual stack gases are not
  separated in this branch-level GWP table. Materials includes chemicals, sorbent, construction and
  related end-of-life branches. Bundled pipeline/storage and remaining branches
  stay in Other supply chain. Upstream biogenic uptake stays in its source category.
- Normalization: one physical net tonne stored after transport loss, with
  supply-chain GHG emissions retained in the numerator.
- Pulse equivalents: selectable window start, reference-pulse year and window
  end in five-year steps within 2000–2300, defaulting to 2020 / 2030 / 2100.
  The reference pulse stays strictly inside the window. The underlying FaIR
  trajectories still span 1940–2300 and temporal inventories extend back to
  1882; choosing a later window excludes earlier response from the metric,
  without modifying the inventory or trajectory. Pre-operation contributions
  are inherited upstream timing, not early plant operation.
- Pulse values come from the existing configuration-first 841-member ensemble
  grid, not ratios of the median display trajectories.
- The forest sensitivity is the existing illustrative GWP-only screen. It is
  available in backup and is not propagated to FaIR or pulse equivalence.
