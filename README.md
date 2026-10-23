# MatterLab

An English-only, local-first platform for generating material composition and ordering hypotheses, running real atomistic calculations, and inspecting reproducible evidence.

**Current result:** 27 symmetry-distinct initial decorations; six candidates and nine reference structures calculated; two candidates investigated with energy-volume scans and Gamma finite-displacement diagnostics. Both Gamma diagnostics are inconclusive. No stable, synthesizable, globally novel material or product performance has been established.

Read the [results and potential applications](docs/RESULTS.md), [model and candidate card](docs/MODEL_CARD.md), and [scientific protocol](docs/scientific-design.md) before interpreting the numbers.

## What it does

- Enumerates 20-atom oxide perovskite decorations with configurable Ca/Sr/Ba and Ti/Zr/Sn occupations, exact parent-symmetry deduplication, and seeded sampling.
- Relaxes atoms and cells with a pinned CHGNet model and explicit force/stress criteria.
- Uses composition-constrained linear programming to compare candidates against a restricted set of nine endmember references.
- Runs fixed-shape energy-volume scans and two-step Gamma curvature diagnostics for selected candidates.
- Preserves CIF files, optimization trajectories, raw energies/forces/stresses, model and dependency hashes, code snapshots, and failed or inconclusive checks.
- Provides an offline English dashboard with searchable candidates, comparison, rotatable structures, application hypotheses, and evidence downloads.
- Includes separate, actual Quantum ESPRESSO calculations on a known CaTiO3 reference. These are not candidate DFT validation.

## Quick start

Python 3.11 or 3.12 is required. Installation downloads free dependencies; the included CHGNet workflow and dashboard can then run locally without a model API key.

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/pytest -q
.venv/bin/matterlab verify runs/round-001-en
.venv/bin/matterlab serve --port 8877
```

Open http://127.0.0.1:8877/ . The server is read-only and binds to the local computer only. Pick another port if necessary. The repository includes actual first-round results, so you can inspect them before starting another calculation.

## Generate and calculate

```sh
# Generate structures only. The output directory must be new.
.venv/bin/matterlab generate --config configs/round-001.json --output runs/new-design

# Run a complete independent campaign with the saved settings.
.venv/bin/matterlab run --config configs/round-001.json --output runs/my-first-run
.venv/bin/matterlab verify runs/my-first-run

# Replay one candidate from original input and compare raw final observations.
.venv/bin/python tools/reproduce_candidate.py \
  runs/round-001-en C03-005 runs/my-replay-C03-005
```

Use a new directory for each independent run. `--resume` reuses saved results and rejects configuration, environment, checkpoint, or source drift; it is not independent reproduction. Every campaign records `requirements-lock.txt` and `source_snapshot/matterlab`. To invoke an older saved source, use `PYTHONPATH=runs/RUN/source_snapshot .venv/bin/python -m matterlab ...` with its compatible locked environment. Exact same-platform replay is separate from cross-platform reproducibility and physical accuracy.

The tested macOS environment uses SciPy 1.17.1. Its official wheel resolved a native-extension loading failure encountered with SciPy 1.15.3; no system security controls were changed.

## Evidence and applications

- [English campaign report](runs/round-001-en/report.md) and [machine-readable results](runs/round-001-en/summary.json).
- [Integrity and metric-recomputation checks](runs/round-001-en/verification.json).
- [Independent C03-005 replay](runs/reproduction-round-001-en-C03-005/reproduction.json).
- [Known-reference DFT execution and convergence limitations](docs/quantum-validation.md).
- [Novelty ledger](docs/NOVELTY.md) and [third-party sources](docs/THIRD_PARTY.md).

The potential research directions are dielectric ceramics for capacitors/electronic packaging and ceramic-composite fillers. Permittivity, dielectric loss, breakdown, thermal transport, strength, processing, and lifetime remain unverified. The datasets can already serve as open samples for materials-informatics and interatomic-potential research.

A [published six-cation family precedent](https://doi.org/10.1016/j.ceramint.2023.11.388) limits novelty claims. Generated coordinates are not an invention certificate. Restricted decomposition energies are not a complete convex hull, Gamma tests are not full phonon dispersion, and fixed-shape compression response is not strength, hardness, toughness, or dielectric performance.

## Continuing development

The project is maintained through an owner-authorized, scheduled research workflow. See [operating agreement](project/OPERATIONS.md) and [research state](project/STATE.json). Each iteration must answer a specific unresolved question, keep separate evidence, and retain negative results. Engineering release and materials discovery are separate milestones; research success is not guaranteed.

GPT Astra roles assist planning, development, and review within the owner's existing Codex subscription. This repository does not offer a free model API, contain subscription credentials, or require GPT calls to replay saved simulations. Local scheduled work requires the host and desktop app to remain available. No paid API, rented compute, paid database, credits, or automatic overage is part of this workflow.

![English dashboard](docs/images/matterlab-english.png)

## Publication and license

Original code is MIT-licensed. External software, pretrained weights, pseudopotentials, and cited data retain their own licenses; they are not relicensed or bundled as model weights. Local computer time, power, and storage remain real resource costs.

The public release is a clean English export. Historical private workspace records are preserved locally; they are not pushed as Git history. Public quantum artifacts with sanitized machine paths/archive ownership are explicitly marked as derivatives, with source and exported checksums. See `publication/manifest.json` and `runs/quantum/public-transformation.json` in the public release. Do not describe those sanitized metadata files as byte-identical originals.
