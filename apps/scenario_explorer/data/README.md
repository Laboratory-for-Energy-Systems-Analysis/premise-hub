# IAM scenario explorer data

These structured CSV files are processed IAM scenario exports distributed with
the corresponding Premise releases. Large current releases may use transparent
gzip compression (`.csv.gz`). The version manifest in `datasets.yaml` controls
which files are available in the public explorer.
Premise 2.4.9 is the current default. Its manifest entry records the upstream
premise commit used to generate it. Earlier releases remain selectable for
comparison and reproducibility.

The 2.4.9 heat data are presented as three separate sectors: `Heat - Buildings`,
`Heat - Industry`, and `Heat - District heating`. Keeping these layers separate
avoids stacking end-use heat demand with its upstream supply.

Every 2.4.9 row carries a `region_source` value. `reported` identifies values
provided by the IAM; `derived` identifies missing IMAGE World series calculated
as the sum of its non-overlapping native regions. Reported World values are
never overwritten. The generator retains every finite non-zero value; the
dashboard's Top 8 + Other display is a reversible presentation step only.
The generator also compares absolute sector totals across pathways for shared
historical years and rejects any two-order-of-magnitude scale mismatch. This
guards against mixing IAM files that express the same mapped sector in
incompatible units.

Every sector exposed by the 2.4.9 explorer has an explicit entry in
`units.yaml`; chart axes and result badges therefore show physical units rather
than the generic `Value` fallback.

The files are not relicensed by the BSD license covering the portal code.
Users must consult the originating IAM model teams and Premise documentation for
the applicable source, citation, and reuse requirements.

`variable_catalog.json` is generated from the listed CSV files and provides a
small startup-time index used for stable Plotly colour assignment.

## Regeneration

First regenerate `dev/mapping_overview.xlsx` with the `extract_mapping.py`
shipped by the target premise source. Then build the dataset from the encrypted
IAM archive and refresh the shared variable catalog:

```bash
export PREMISE_KEY='<local key>'
export BRIGHTWAY2_DIR='/path/to/a/writable/brightway-directory'
conda run -n premise python apps/scenario_explorer/dev/generate_data.py \
  --iam-dir '/path/to/encrypted/iam-files' \
  --expected-version 2.4.9
python scripts/build_explorer_catalog.py
```
