# Interactive research explorer

The static MatterLab presentation is built for GitHub Pages at
https://cptm511.github.io/matterlab/. It needs no application server, database,
model API, analytics service or third-party JavaScript runtime.

## Evidence snapshot

The site preserves the original `round-001-en` summary byte for byte and links
raw artifacts and reports to public commit
`2baa6913e66688f5cc0ac9a4251ec2f628727c7f`. Later published G1/N1/F1 diagnostics
qualify the historical screening results. The snapshot does not imply live
research status, candidate stability or verified application performance.

`docs/site/provenance.json` identifies the source and its hash. The CSV is a
selection of source fields; empty cells mean unavailable or unreported data.
Display text explicitly identifies candidates without compression-response
calculations while preserving the original records.

## Build and preview

```sh
python3 tools/build_pages.py
node --check docs/site/app.js
python3 -m http.server 8767 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:8767/`. The builder checks the pinned source blobs and
stops if either source changed. Updating the evidence snapshot requires a
review of the new data, claims, links and hashes; it is not an automatic refresh.
It never runs simulations or publishes changes.

## GitHub Pages configuration

In the repository's Pages settings, choose **Deploy from a branch**, **main**,
and **/docs**. The `.nojekyll` marker serves the generated files directly.
Publication requires the existing complete-tree integrity audit and refreshed
`publication/manifest.json`. Publish only the reconciled public tree.

## Verification scope

The presentation was checked for search and type filters, empty results,
three-record comparison limits, structure selection, keyboard rotation and
zoom, evidence tabs and keyboard navigation, downloadable data, pinned evidence
paths, and responsive layout. The bundled JSON matches the original source.

These checks concern the presentation and integrity of existing records. They
do not rerun scientific calculations or satisfy unresolved scientific criteria.
