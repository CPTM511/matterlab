# Local Quantum ESPRESSO validation

This project installs Quantum ESPRESSO 7.6 in `.tools/qe-openmpi/` on Apple Silicon macOS and uses `pw.x` for actual plane-wave PBE density-functional theory calculations. The software and pseudopotentials are free, and computation runs on the local CPU without paid APIs or cloud compute. CHGNet results are machine-learning interatomic-potential predictions and are separate from these DFT results.

## Installation and reproduction

For an unmodified original evidence bundle, check its recorded file hashes with `shasum -a 256 -c runs/quantum/manifest.sha256`. A public export must use the publication manifest supplied with that export, because translated documentation and sanitized metadata have different hashes from the original bundle. Preserve the original evidence and its manifest separately.

The standalone SHA256 manifest check needs no solver installation. The Python evidence verifier requires the pseudopotentials in `.tools/pseudo/`, so run `bash tools/quantum/install.sh` before `python3 tools/quantum/verify_evidence.py` in a fresh working copy. The verifier checks recorded input, output, and pseudopotential hashes, accepted energies, and available XML convergence records. It writes `evidence-verification.json`; it does not start a simulation. The installer writes environment locks and executable hashes, so check the archived publication manifest before setup, then perform the scientific evidence checks after setup. Setup changes are not alterations to the published snapshot.

```bash
# Check the downloaded public snapshot before installing anything.
shasum -a 256 -c runs/quantum/manifest.sha256
# Install the local environment and pseudopotentials, then verify the evidence.
bash tools/quantum/install.sh
python3 tools/quantum/verify_evidence.py
```

Before recalculating, preserve the existing `runs/quantum/` directory under a different name or location. The following commands require output directories without existing results; the runner creates the directories and refuses to overwrite existing output. These commands reproduce the attempted settings, including the k-point setting that did not converge in the recorded run.

```bash
bash tools/quantum/install.sh
python3 tools/quantum/run_reference.py --ecut 60 --rho 600 --k 4
python3 tools/quantum/run_reference.py --ecut 80 --rho 800 --k 4 --warm-start runs/quantum/catio3-cubic-e60-r600-k4-m0.1-n12-david-openmpi
python3 tools/quantum/run_reference.py --ecut 80 --rho 800 --k 6 --warm-start runs/quantum/catio3-cubic-e80-r800-k4-m0.1-n12-david-openmpi
python3 tools/quantum/compare_convergence.py
python3 tools/quantum/verify_evidence.py
```

Installation uses conda-forge's native `osx-arm64` QE 7.6 OpenMPI packages. All binaries and dependencies reside inside the project's `.tools/` directory; system packages are not modified. Exact package URLs and checksums are recorded in `tools/quantum/conda-explicit-openmpi-osx-arm64.txt`, which the installer uses when available. Initial setup requires several hundred MB of downloads and approximately 1 GB of environment storage, plus package caches. The supplied installer and lock target Apple Silicon macOS; they are not a cross-platform installation recipe.

The restricted sandbox initially blocked MPICH network-interface initialization even for one local MPI process. A later MPICH calculation completed electronic self-consistency but returned code 143 during shutdown and therefore failed the execution-success requirement. Failed and interrupted logs remain in `runs/quantum/`, and the historical MPICH environment lock remains in `tools/quantum/conda-explicit-osx-arm64.txt`. The OpenMPI build completed the same reference calculation with return code 0 and became the default. The runner uses two OpenMP threads and one local MPI process by default. Recorded verification was performed in a terminal environment permitting MPI initialization.

## Reference system and calculation settings

The reference is ideal cubic CaTiO₃ with five atoms and a fixed lattice parameter of 3.89 Å. This specified reference cell tests the calculation workflow and numerical sensitivity. It is not a new-material discovery or an assertion of the equilibrium ground-state structure of CaTiO₃.

The calculations use PSlibrary 1.0.0 scalar-relativistic PBE PAW pseudopotentials distributed through the official QE pseudopotential site. Ca contributes 10 valence electrons, Ti contributes 12, and each O contributes 6, for 40 valence electrons per cell. SHA256 checksums are recorded in `tools/quantum/pseudopotentials.sha256` and in each run summary.

The electronic self-consistency threshold is `conv_thr=1e-9 Ry`, with fixed occupations and no Hubbard U, hybrid functional, or spin–orbit coupling. Initial attempts with `mixing_beta=0.3` continued oscillating and were interrupted. Reducing the mixing parameter to 0.1 and increasing the mixing-history length to 12 enabled convergence. The checks compare wavefunction/charge-density cutoffs of 60/600 Ry and 80/800 Ry, and unshifted 4×4×4 and 6×6×6 k-point meshes. The lowest settings exceed the suggested minima in all three pseudopotential headers; the strongest requirement is Ti at approximately 52/575 Ry. Header recommendations do not replace convergence checks for a specific target property.

`--warm-start` reuses the charge density of the same reference cell and pseudopotentials only as an initial guess. Wavefunctions are reinitialized, and the self-consistency threshold remains unchanged. The first successful OpenMPI run used the previously converged MPICH density and reproduced the same total energy after 10 iterations. The initial MPICH calculation from an atomic starting guess needed 86 iterations to converge electronically. A fresh run can therefore take longer than the recorded OpenMPI warm-start run.

Each executed OpenMPI warm-start run also retains `initial-density.tar.gz`, containing the actual initial charge density, PAW data, and source XML. These archives total approximately 1 MB. For replay of an archived input, use a new working directory, extract its density archive there, and copy the corresponding `input.in`. Change `pseudo_dir` in that copy to the absolute path of the current project's `.tools/pseudo/` directory, then invoke the current project's `.tools/qe-openmpi/bin/pw.x` by absolute path with `-in input.in`. The archive supplies the initial density; the new execution still solves the electronic self-consistency equations. Recorded paths are historical machine-specific metadata and should be adapted only in replay copies.

Every run retains `input.in`, `output.out`, `summary.json`, and an XML schema file when available. The wrapper succeeds only when `pw.x` returns 0, the raw output contains `JOB DONE.`, and electronic self-consistency is explicitly reported as converged. `runs/quantum/convergence.json` summarizes accepted calculations, energy differences, and unaccepted records. Large `scratch/` directories remain local and are excluded from Git; they can be regenerated by replay.

Successful OpenMPI output includes Fortran floating-point status flags at shutdown: invalid, divide by zero, and underflow. The reported energies are finite and the process returned 0; the warning text is preserved. This reference exercise does not establish production accuracy through independent solver validation.

## First recorded calculation results

Two OpenMPI reference calculations passed both execution and electronic self-consistency checks on 24 October 2026, Asia/Shanghai time. Wall times below are measured by the Python wrapper and include process startup and shutdown.

| Wavefunction / charge cutoff, Ry | k-point mesh | SCF iterations | Total energy, Ry | Wall time, seconds | Result |
| --- | --- | --- | --- | --- | --- |
| 60 / 600 | 4×4×4 | 10 | −442.91302725 | 84.04 | Electronic convergence; process return code 0 |
| 80 / 800 | 4×4×4 | 53 | −442.91712792 | 362.57 | Electronic convergence; process return code 0 |
| 80 / 800 | 6×6×6 | Stopped after 52 iterations | No accepted energy | 742.73 | Not converged; wrapper rejected the result |

The 60/600 → 80/800 Ry energy change is **11.1585 meV/atom**, exceeding the predefined exploratory threshold of 1 meV/atom. The 60/600 Ry cutoff check therefore failed. No comparison with a higher cutoff establishes that 80/800 Ry is sufficiently converged either. During the later part of the 6×6×6 run, the electronic residual continued oscillating around 1e-7–1e-6 Ry and did not satisfy the 1e-9 Ry requirement. Further unchanged iterations were stopped through QE EXIT files, with the raw output retained. That run cannot establish k-point convergence.

There are **seven recorded attempts in total: two accepted and five unaccepted**. The five unaccepted records comprise the sandbox MPI initialization failure, two interrupted initial mixing trials, one electronically converged MPICH run with return code 143, and the interrupted, unconverged OpenMPI k6 run. These are distinct failure or interruption conditions. In particular, k6 returned process code 0 after a clean stop, but `scf_converged` is false and its wrapper exited unsuccessfully. Neither `JOB DONE.` nor process code 0 alone is treated as scientific convergence.

These records establish that free local DFT installation, input preparation, computation, evidence preservation, and failure detection have actually been exercised. They apply to the fixed cubic CaTiO₃ reference and do not validate the platform's generated 20-atom candidates. The two successful SCF calculations support no claim about candidate stability, band gap, mechanical performance, or novelty.

## Scope of the results

Electronic self-consistency means that the electronic iteration completed for the specified discretization. An energy change below 1 meV/atom between adjacent settings is this project's exploratory check; it does not by itself prove complete basis-set, k-point, force, or stress convergence. Raw total energies of different compositions cannot be used directly to rank stability.

These fixed-cell SCF calculations do not establish ionic or cell relaxation, phonon dynamical stability, a competing-phase convex hull, synthesizability, experimental performance, or novelty. Generated candidates require calculations using their own structures, compositions, and pseudopotentials. The five-atom reference does not substitute for candidate-specific quantum verification.

## Public evidence export

From the original local project, after copying project source files to a separate staging directory, run:

```bash
python3 tools/export_quantum_public.py --output /absolute/path/to/public-staging
```

The exporter copies quantum evidence without `scratch/`, retains the original files locally, and publishes English documentation. Absolute workspace paths become the literal `${PROJECT_ROOT}` placeholder and home paths become `${HOME}` in text metadata, logs, and XML. These placeholders document removed machine-specific paths; QE input strings do not expand them automatically. Replace `pseudo_dir` with the actual current pseudopotential directory when preparing a replay copy.

Density archives are repacked with zero numeric ownership, empty owner names, normalized permissions and timestamps, and portable paths in embedded text. Binary HDF5 density payloads remain byte-for-byte unchanged. Numerical results, statuses, self-consistency thresholds, and failed attempts are preserved. Summary input/output hashes are updated to match the exported derivative files.

`runs/quantum/public-transformation.json` records original and exported SHA256 hashes and the operation applied to each file, including archive member hashes and original summary input/output hashes. `historical-manifest.sha256` retains the original listing for provenance; it is not the checksum list for the public derivative. The exporter creates a new public `manifest.sha256` and `public-export-verification.json`, and checks that source and exported records agree on all seven attempts and the two accepted calculations. This verifies the published evidence transformation, not additional physical accuracy. No solver or network operation is started by export.

## Official sources

- [Quantum ESPRESSO input parameter documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [Quantum ESPRESSO pseudopotential documentation](https://www.quantum-espresso.org/pseudopotentials/)
- [conda-forge QE packages and supported platforms](https://anaconda.org/conda-forge/qe/files)
- [Micromamba installation documentation](https://mamba.readthedocs.io/en/stable/installation/micromamba-installation.html)
- [Quantum ESPRESSO methods paper](https://arxiv.org/abs/0906.2569)
