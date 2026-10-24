# P1 default-dispatch repeat: result for parent review

The single authorized P1 evaluation completed. The frozen controller reports **H1_exact_pairwise_repeat**: all six model-output tensors and ASE energy/forces/stress reproduce saved C1 exactly, with complete matching primary runtime metadata except the predeclared condition label. All 120 capture/integrity checks and the execution/resource gate passed. **Original baseline numerical acceptance remains FAILED.** The earlier frozen C1 gate remains FAILED, historical C2 remains unrun, and full migration remains incomplete.

## Frozen authorization and execution

This was the new protocol `P1-default-repeat-20261024`, not C2. The parent explicitly released the exact reviewed protocol and implementation. Before use, the complete freeze, all 12 implementation-manifest entries, independent review identity and Python executable hash were verified. No frozen code or thresholds were edited.

- English protocol SHA256: `8818e943d53d64884c9ed0ad7e7b35836627fb9cb611ec92e7a9c9dbcfc442c7`.
- Machine protocol SHA256: `65edd51f107018e757b920fcc339789373b1dbba498bd2f71aef7423d41d6d7f`.
- Implementation manifest SHA256: `7e4b3630e23d721486a59d6342fd303b25eeaab1dea4d1faf525f89696c42c7f`.
- Independent pre-execution review SHA256: `01a4e1ee61098ab79977b8a660fbc0e4dca2213fd2cb828e4ea164c44c3951d6`.
- Freeze envelope SHA256: `fd475de8179f83f4cb71ffe7a8449ec43f72e7db20d501fe50354b87515ce1b9`.

The scientific checkout and references are public commit `91147ff73336ce205717117b2ab7de3e62c5fdb1`. A fresh authorized connector read returned that remote main. The frozen controller also required the same remote head, clean checkout and pinned public STATE before preflight and before launch. Its successful execution path means those checks returned without raising. The full metadata/hash preflight passed 1,498 checks. The current environment process scan found no known overlapping calculation; parent coordination supplied fallback/scheduler non-overlap. That attestation is not an independent scan of the owner's computer. Account/ownership evidence remains private.

The single-use protocol token and inference token were each claimed once and retained. No retry, alternate backend, second evaluation, relaxation, Gamma/DFT work, installation, publication or schedule change occurred. No denied or uncertain write action remains.

## Observed conditions and timing

One 20-atom CaTiO3 CPU single point used affinity `[0]`, seed 20261024, ATEN_CPU_CAPABILITY=default, observed NO AVX, float32 model parameters, graph algorithm fast, PyTorch intra-op/inter-op one, deterministic algorithms enabled, MKLDNN enabled and highest matmul precision. Numerical-library environment controls were set to one, and MKL_CBWR remained unset. These controls do not independently measure every library thread pool or globally disable AVX.

Runtime: Python 3.12.14; PyTorch 2.6.0+cpu; NumPy 2.2.6; ASE 3.26.0; CHGNet package 0.4.2/model 0.3.0. All saved dependency versions, expected source/model/native-library hashes and available CPU identity fields matched. Physics source remains `3319dc595397f68c0e7a3326e64c2b27ae799027`; model checkpoint SHA256 remains `d14ab7c0f093efe64b60a7bcd540bca10e74fb7f46c86108a079af60524659d1`.

Investigation start was 2026-10-24T03:00:12Z and was not reset. The calculation process ran 2026-10-24T03:01:12.491792Z through 2026-10-24T03:01:16.919139Z. Its measured wall time was 4.427294630000688 seconds; the frozen timeout was 594 seconds, leaving cleanup margin within the 600second maximum. The recorder's nested numerical section reported 0.2636702060008247 seconds. These are different timing scopes. Preflight took 3.1703699760000745 seconds, and saved-data analysis took 0.21436207999795442 seconds. At the controller's final decision, investigation elapsed time was 65.134202 seconds, within 1,800 seconds. Subsequent bounded reporting/saved-data verification did not run another inference.

Exactly one graph conversion and one model forward were captured. The process and analyzer returned 0 with no timeout or recorder/controller exception. Stderr retains handled Matplotlib cache-directory permission messages and a Fontconfig no-writable-cache message, of the same kind present in published C1. They did not become recorder exceptions or numerical-gate failures. The log is preserved; its review copy redacts only runtime-home and ephemeral cache paths. No cache/configuration repair was attempted.

Requested model configuration was GPT-6 Astra, High reasoning, Standard speed where selectable. The observable developer identity is GPT-6-based Codex; exact serving model/reasoning/speed are not independently attested.

## Numerical comparisons

Energy is **-166.1494140625 eV**. Full forces and stress are in `P1/observations.json`; no components are omitted. `comparisons.json` retains every available signed difference, defined as P1 minus the named public reference, including model/input/neighbor/graph arrays. D1 has no numerical observations and remains explicitly unavailable, not zero.

The primary C1 criterion is exact dtype/shape/raw-byte equality for all six model tensors and exact ASE observations, plus the complete runtime/build comparison and all invariants. It passed. The table uses the separately retained original tolerances: energy 1e-5 eV, force 1e-6 eV/Angstrom, stress 1e-7 eV/Angstrom^3, all rtol 0.

| Public reference | Max absolute energy difference (eV) | Max absolute force difference (eV/Angstrom) | Max absolute stress difference (eV/Angstrom^3) | Original-threshold comparison |
|---|---:|---:|---:|---|
| C1 | 0.0 | 0.0 | 0.0 | PASS |
| C0 | 0.0 | 5.1021575927734375e-05 | 5.736947059631348e-07 | FAIL |
| R1 | 0.0 | 5.1021575927734375e-05 | 5.736947059631348e-07 | FAIL |
| baseline-001 | 0.0 | 3.4332275390625e-05 | 4.4249463826417923e-07 | FAIL |
| baseline-002 | 0.0 | 3.4332275390625e-05 | 4.4249463826417923e-07 | FAIL |
| replay | 0.0 | 5.1021575927734375e-05 | 5.736947059631348e-07 | FAIL |

Input/config bytes, all input/consumed-neighbor/graph array bytes, model parameters and the entire same-condition runtime/build description matched C1. Only the declared condition label differs. All six model-output tensor data hashes matched. Exact float32 energy scaling and stress conversion/symmetrization matched ASE output. The secondary descriptive C0 runtime comparison passed its narrower intervention-only metadata rule; it does not change the old frozen C1 gate.

## Integrity and evidence boundaries

The frozen analyzer reports 120/120 capture/integrity checks, no missing capture and no recorded analysis errors. A separate saved-data-only check by the executing role passed 170 checks, verifying raw manifest coverage/hashes, all primary arrays and runtime, complete ASE observations, every signed ASE difference against six references, unchanged thresholds, retained historical failure and one graph/forward. This was not an independent new reviewer and involved no model construction or forward call.

`P1/` contains raw CIF/config, input arrays, consumed neighbors, graph arrays, model tensor outputs/parameter hashes, source/hash records, runtime/provenance, observations, capture counters and the recorder manifest. The implementation snapshot, preflight/integrity records, complete comparisons, analysis/final decisions and timings accompany them. Private originals retain full stdout, process and entry-gate evidence; those private account/host records are excluded from the review derivative. The transformation ledger identifies byte-identical copies and the log path redactions. Scientific arrays and observations are not transformed. The original private controller manifest is preserved separately, and the review package has its own manifest.

The assertion-only derivative had no physical validation before this invocation. This result now demonstrates successful capture and exact C1 equality for this one invocation. It does not establish universal equivalence of the instrumentation or erase its pre-execution uncertainty. The published original recorder, its exact derivative diff and every superseded source/draft/failure remain preserved.

The earlier publication readback remains identified by SHA256 `63efc41bfa9f142b3d6415039f0168fa347bf4a1dfa3bc1b9c940599d01f3b9b`. Its 643-file/9-archive-member/284-historical-hash audit scope concerns that prior publication. This new local review package is not published and has not received a new independent full publication audit.

## What this changes, and what remains unresolved

The altered-dispatch C1 output has now recurred exactly in one fresh process under the matching recorded fingerprint and reviewed assertion derivative. This resolves the specific pairwise-repeat question for these two observations and supports selecting that explicit fingerprint for designing a separate Gamma numerical-diagnosis protocol. It does not estimate a reproducibility distribution, establish the historical backend, prove which derivatives are more physically accurate or explain the original host drift.

Original baseline force/stress failures persist without threshold changes. The old C1 gate stays failed and C2 stays unrun. Missing D1 measurements remain missing. Full migration is not accepted and the fallback remains retained. ML-potential results are not DFT, synthesis, stability, novelty or application evidence.

The exact next unexecuted action is parent review of this result and its raw evidence. A later separately frozen Gamma protocol would need to address displacement-size dependence, graph continuity and finite-difference noise under the explicit backend fingerprint; this release authorizes none of those calculations. No further inference remains authorized under P1.
