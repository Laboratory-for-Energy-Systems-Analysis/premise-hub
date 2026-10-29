# Third-party material

The BSD 3-Clause License in this repository applies to the application code.
It does not relicense scenario data, logos, screenshots, or figures supplied by
third parties.

## Scenario data

The IAM scenario explorer contains processed scenario exports distributed with
the corresponding Premise releases. Users must follow the terms and attribution
requirements of the originating IAM teams and datasets. See
`apps/scenario_explorer/data/README.md`.

The workshop contains reduced, teaching-oriented extracts and calculated LCA
results. Their provenance is documented in `apps/workshop/data/README.md` and
in the source notes displayed on the relevant slides.

The LCA-through-time presentation contains reviewed, processed LCA and climate
response results. Their provenance is documented in
`apps/lca_time/data/README.md` and in the source notes displayed on the slides.

The Seoul lecture reuses these presentation figures and the reviewed public
cement-webinar results. Its coastal-weathering foreground is adapted from
Foteinis, Campbell and Renforth (2023), DOI 10.1021/acs.est.2c08633, and the
open supporting inventory (Table S1). The original article and supporting
information are CC BY 4.0. Corrections and analyst timing assumptions are
identified in `apps/seoul_2026/data/erw_review.json`; these do not validate
field performance. No ecoinvent background inventories are redistributed.

## Project and institutional marks

Premise, Brightway, Pathways, Trails, Activity Browser, and PSI names and logos
remain the property of their respective projects and institutions. Their
inclusion identifies linked resources and does not place those marks under the
repository's BSD license.

The Seoul lecture identifies six widely used IAM families with unchanged marks
from their model or institution websites: MAgPIE (PIK), IMAGE's PBL team mark,
MESSAGEix/IIASA, GCAM's University of Maryland partner mark, AIM, and WITCH/RFF-CMCC.
Model-family/component marks and institutional marks are explicitly labelled on
the slide. Their original ownership and trademark rights remain unchanged.
Asset URLs, source pages, access dates and hashes are recorded in
`apps/seoul_2026/data/iam_logos.json`; the artwork is stored locally for offline
teaching and PDF export. Inclusion identifies the model families and their teams.

The ecoinvent wordmark on Seoul slides 4, 10, 14 and 20 is copied unchanged from
`https://ecoinvent.org/app/uploads/2023/09/Logo-Wordmark.svg`, as linked by the
official ecoinvent homepage. It identifies the background inventory database;
it remains ecoinvent's mark and is not relicensed under BSD. The premise mark
reuses the unchanged workshop project asset. Source paths, URLs and hashes are
recorded in `apps/seoul_2026/data/background_branding.json`.

The TRAILS routing, climate response and workflow slides also reuse the unchanged TRAILS mark from the LCA-through-time
lecture and the SETAC annual technosphere/biosphere matrix-stack SVG. Its
interactive graph viewer uses the existing local vis-network 9.1.2 bundle
under its original license. Actual four-level TRAILS graph exports retain
topology and dated activity identities, without background coefficients or
private engineering amounts. Logo paths and hashes are in the branding manifest
above.

## Seoul presenter introduction assets

- EDGES logo: unchanged `edges_logo_tight_frame.png` from the
  [EDGES project](https://github.com/Laboratory-for-Energy-Systems-Analysis/edges/tree/main/assets/permanent),
  copied to `apps/seoul_2026/assets/edges-logo.png` for the introduction slide.
- Switzerland outline: [Natural Earth 1:10m admin-0 map units](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-details/),
  simplified and drawn as native SVG with an approximate PSI campus marker.
  Natural Earth data are [public domain](https://www.naturalearthdata.com/about/terms-of-use/).
- Romain Sacchi portrait: supplied by the presenter; copied unchanged from
  `portrait_romain_sacchi_resized.png`. Provenance and hashes for these assets
  are recorded in `apps/seoul_2026/data/bio_sources.json`.
