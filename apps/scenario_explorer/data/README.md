# IAM scenario explorer data

These structured CSV files are processed IAM scenario exports distributed with
the corresponding Premise releases. The version manifest in `datasets.yaml`
controls which files are available in the public explorer.
Premise 2.4.9 is the current default. Because the release has not yet been
published, its manifest entry is explicitly labelled as a pre-release and
records the upstream premise commit used to generate it. Earlier releases
remain selectable for comparison and reproducibility.

The 2.4.9 heat data are presented as three separate sectors: building heat,
industrial heat, and the secondary/district-heating supply mix. Keeping these
layers separate avoids stacking end-use heat demand with its upstream supply.

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
