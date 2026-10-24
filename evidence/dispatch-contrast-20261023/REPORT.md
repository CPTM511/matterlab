# Bounded ATen CPU-dispatch contrast

The fresh control reproduced R1 exactly. Changing only the supported per-process `ATEN_CPU_CAPABILITY` setting from unset to `default` changed the saved forces and stress while preserving input, consumed neighbors, graph arrays and parameter hashes. Energy stayed identical. The altered process remained finite and captured all required data.

The frozen comparison gate nevertheless **failed**: its literal comparison of `torch_build` included a second copy of the intended CPU-capability change. The protocol therefore stopped after **two** new single points, without the optional repeat. The failed machine gate is preserved unchanged. This is a single observed sensitivity to the selected dispatch setting, not a completed repeated contrast, a correction of the old result or an explanation of historical host differences.

| Outcome | Result |
|---|---|
| C0 fresh control versus R1 | Exact equality of all input/graph/parameter captures, all six model-output tensors and ASE observables |
| C1 raw capture | Complete, finite, one graph/model call; input/graph/parameter invariants passed |
| Intended intervention | Observed capability changed from AVX512 to NO AVX |
| Frozen C1 comparison gate | Failed on duplicate capability text in `torch_build` |
| C2 altered-condition repeat | Not run; gate prohibits it |
| Original baseline numerical acceptance | Failed for C0 and C1, with original thresholds unchanged |
| Full migration / publication | Incomplete / not performed |

## Authority, public source and preflight

This continuation used the same isolated native cloud task. It created neither another environment nor another physical campaign. A read-only independent reviewer worked concurrently but performed no model inference. Public main remained at `2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1`, whose parent is `f1fdd7fbe07b05c60cb2c15f808ddaa6c13a06bb`. The original checkout remained clean, all 446 publication entries were reverified, and public STATE listed no active physical job. Local process checks found no overlapping physical calculation. Current cloud ownership came from the parent's assignment, not a separate campaign.

The original R1 protocol, private scientific observations, 106-file sanitized export and archive remain byte-identical. Its archive SHA256 is `fd3470e977e37f62977e08e341c4977dfdb5c3f925049b48746369d98d37e32c`; public manifest SHA256 is `3bf1a29f665c140ef9d3c96d07c2516c424f8921d083c7b25e7c4d5a69c08743`. R1's original failure and reports were not edited. The pre-R1 restored failure and D1's missing numerical output likewise remain unchanged.

Before inference, 506 preflight checks again verified public source/manifest, dependency versions, the Python executable, raw input/configuration, CHGNet Python sources and cached model hashes. An additional 15,077 installed RECORD hashes verified. The active model remained CHGNet package 0.4.2/model 0.3.0 with checkpoint SHA256 `d14ab7c0f093efe64b60a7bcd540bca10e74fb7f46c86108a079af60524659d1`. Physics source remained `3319dc595397f68c0e7a3326e64c2b27ae799027`; imports and all eight source hashes were bound to the verified public checkout. No package or global setting was changed.

The parent supplied a fresh startup included-usage check. Account evidence stays private. Neither this task nor the reviewer independently meter account billing or attest the actual model variant/effort/tier. Requested primary and reviewer configuration is GPT-6 Astra, High reasoning, Standard speed for the primary. Observable developer identity is GPT-6-based Codex. The reviewer was explicitly launched with the available `gpt-6-astra` and `high` settings; that tool configuration is not an independent backend attestation. No paid API, extra-credit use, rental, credentials, billing/security change, publication or schedule operation was invoked.

## Supported setting and frozen protocol

The installed PyTorch 2.6.0+cpu build identifies commit `2236df1770800ffea5697b11b0bb0d910b2e59e1`. Public `aten/src/ATen/native/DispatchStub.cpp` at that exact commit was fetched and saved with URL and SHA256 in `dispatch-source.json`. Lines 27–63 show the environment-variable selection, including `default`; lines 117–119 cache the choice per process. Metadata-only probes, with no model load or inference, independently observed AVX512 when unset and NO AVX when set to `default`. The installed implementation thus accepted the chosen intervention.

The interpretation is limited to ATen DispatchStub capability selection in this build. It does not globally disable AVX, select every MKL/oneDNN kernel, or reveal which individual kernels changed. No per-kernel trace or reconstruction of historical CPU/backend settings is claimed.

`protocol.json` was frozen before any new inference with SHA256 `790f9eebe9c41285001efccddfa7f234507d88918ed5882ac20a21b072f06e6f`. It declared: C0 must exactly reproduce saved R1, including all six model tensors; only then may C1 change the per-process capability variable; C2 may run only after C1's complete comparison gate passes and a finite ASE observable actually changes. C2 would test altered-condition repeatability, rather than fill an evaluation quota.

The limits were three new evaluations, 600 seconds total calculation-process wall time and 1,800 seconds investigation. All evaluation processes used CPU affinity `[0]`, seed 20261024 for Python/NumPy/PyTorch and Python hash randomization, numerical-library environment controls of one and PyTorch intra-op/inter-op threads of one. No relaxation was performed. Other captured runtime settings, input/configuration, graph order and parameter digests were fixed. MKLDNN remained enabled; no alternate package, precision mode or additional backend setting was explored.

Before freeze, the independent review strengthened the launch-time deadline calculation, exact model-tensor dtype/keyset checks, preflight status, R1 manifest verification and helper hash checks. The reviewer and primary did not anticipate that `torch.__config__.show()` embeds a live CPU-capability line. That review limitation is explicitly retained.

## Executed conditions and observations

| Condition | Start UTC | Process wall seconds | Recorder interval seconds | Return code |
|---|---|---:|---:|---:|
| C0 control, capability unset | 2026-10-23 19:21:27.282857 | 4.075613838 | 0.180288050 | 0 |
| C1 default, capability `default` | 2026-10-23 19:21:38.793484 | 3.923635362 | 0.253259919 | 0 |

Total calculation-process wall time was **7.999249200 seconds**. Both conditions recorded exactly one graph conversion and one bound model-forward call. ASE's force/stress getters reused the single-point result. All raw inputs, 1,318 consumed directed neighbors, eight graph tensors, six model-output tensors, parameter hashes, ASE observations, seeds/settings, environment provenance, logs and timings are saved in the condition directories. Exact float32 model-to-ASE conversions reproduce each saved observation. The same harmless Matplotlib/fontconfig cache-location warnings seen in R1 are retained; neither calculation reported an evaluator exception or timeout.

All raw input/neighbor/graph arrays, including shape, dtype and ordering, and all model parameter hashes were identical between R1, C0 and C1. C0 also exactly matched every R1 model-output tensor and all ASE observations. C1 changed the magnetic-moment output, crystal feature tensor, forces and model stress, while `atoms_per_graph` and energy remained identical. All signed array differences are saved; no missing D1 output was reconstructed.

| Comparison, maximum absolute difference | Energy (eV) | Forces (eV/Angstrom) | Stress (eV/Angstrom^3) |
|---|---:|---:|---:|
| C0 minus R1 | 0 | 0 | 0 |
| C1 minus C0 (also versus R1 and prior replay) | 0 | `5.1021575927734375e-5` | `5.736947059631348e-7` |
| C0 minus either onboarding baseline | 0 | `3.039836883544922e-5` | `5.364418029785156e-7` |
| C1 minus either onboarding baseline | 0 | `3.4332275390625e-5` | `4.4249463826417923e-7` |

Every total energy was `-166.1494140625 eV`. Original absolute tolerances remain `1e-5 eV`, `1e-6 eV/Angstrom` and `1e-7 eV/Angstrom^3`, with relative tolerance zero. Both new conditions still fail force/stress acceptance against both onboarding baselines. The C1 force difference is larger and the stress difference smaller than C0's; neither is an optimization target or acceptance correction.

## Failed gate and bounded interpretation

The only failed C1 check was `other_effective_runtime_settings`. The intended top-level capability and environment-variable fields were excluded from that comparison, but the build-description string still changed from `CPU capability usage: AVX512` to `CPU capability usage: NO AVX`. Consequently the frozen machine record has both `capture_integrity_passed=false` and `comparison_assumptions_passed=false`, because it bundles that metadata check with raw-capture checks.

`raw-capture-review.json` distinguishes this combined failure from the successful raw-array/manifests/count/conversion checks. `runtime-comparison-diagnosis.json` preserves every actual runtime-field difference and shows, post hoc, that removing the duplicate capability line leaves all other captured runtime settings equal. This explanation does **not** rewrite the frozen gate, alter the protocol or authorize C2. No third attempt was launched.

The saved observations narrow the uncertainty: under invariant captured input, neighbor/graph and weights, a supported ATen capability-selection change is accompanied by finite derivative changes of the recorded magnitude. No captured factor other than the intended capability setting and its duplicate metadata changed. This is useful evidence of dispatch sensitivity in this environment, with one altered process. It is not repeatability evidence for the altered condition, a causal account of the historical host, a numerical error bound or a demonstration that one output is physically more accurate.

The next research decision should be whether independently confirming this altered-condition response would change the reproduction policy or scientific interpretation. If so, a separate future protocol should predeclare a semantic runtime comparison that treats both capability representations consistently, and test only that repeatability question. Do not run a settings search to match old baselines. No further inference is authorized by the completed protocol. Candidate S1/S2/S3 work remains pending.

## Review, export and remaining gates

A separate Decimal/scalar implementation checked all 630 saved observable-difference components and threshold decisions without numerical model inference. The independent reviewer separately recomputed saved-data hashes, signed scalar/array differences, conversion checks and invariants: 330 checks passed. The reviewer confirms the frozen C1 failure and unrun C2, and its final counter-review accompanies this export. It is a bounded saved-evidence and sanitation review, not a physical rerun or independent attestation of historical runtime.

The integrated candidate contains the original public tree, the unchanged R1 additive evidence, this new evidence and a reconciled STATE/checkpoint proposal. Original source/evidence and owner coordination are preserved; only reviewable current-state/publication metadata are proposed for update. The unchanged `tools/export_public.py` performs the complete publication audit on the integrated tree. Current audit results and complete manifest accompany the candidate, with separate additional NPZ/ledger sanitation checks. The original publication audit/manifest are retained as provenance.

Every private original is retained with its private manifest. The public transformation ledger records original and derivative hashes and exact sanitation. Account records, raw process listings, private task/host identifiers and private execution paths are excluded or sanitized. Source snapshots and dependency licenses remain available in unchanged R1 evidence; the newly fetched PyTorch source retains its license. No original archive or export was overwritten. The final candidate patch and archives are for parent review only, not publication authorization.

Remaining blockers are original numerical acceptance, the frozen C1 metadata-comparison failure and untested altered-condition repeatability. Full migration remains incomplete; the non-overlapping local fallback and existing schedules are retained. These CHGNet ML-potential observations are not DFT, synthesis, material stability, novelty or application evidence.
