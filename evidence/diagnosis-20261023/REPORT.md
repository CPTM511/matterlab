# MatterLab bounded numerical-reproducibility diagnosis

## Decision

The original restored replay remains **FAILED** against its declared force and stress tolerances. This investigation does not resolve the physical-output mismatch. One additional instrumented single-point attempt stopped on a recorder assertion; no further evaluation was launched, as required by the frozen protocol. D2, D3 and D4 were not run.

The failure is localized to instrumentation: CHGNet `predict_graph` calls `self.forward` directly, bypassing a registered PyTorch module forward hook. The graph hook fired once; the model-output hook did not fire. Numerical finiteness checks were reached, but the assertion preceded writing energy/forces/stress to disk. Those numerical values and model-output tensors are therefore **unavailable** and cannot be reconstructed. The empty comparison map means unavailable comparisons, never zero differences or a numerical pass.

## Scope, runtime and observations

The dedicated saved cloud environment was reused. No owner computer, private repository history, package installation, upgrade, paid API, credentials, publication or schedule creation was used. The parent supplied a fresh private included-usage gate; no account usage values belong in this public report. Native allowance observations are startup evidence, not billing enforcement. Hard-coded `external_api_calls` and `paid_compute` fields in historical provenance are source declarations, not independent metering.

Requested reasoning identity was GPT-6 Astra, High, Standard for the task. The independent review was requested as GPT-6 Astra High. Both workers can observe GPT-6-based Codex developer identity, but cannot independently attest actual variant, reasoning setting or service tier. The earlier setup is not claimed to have been Astra-only.

Source remained `3319dc595397f68c0e7a3326e64c2b27ae799027`. Runtime was Linux x86_64, Python 3.12.14, PyTorch 2.6.0+cpu, CHGNet package 0.4.2/model 0.3.0. Current CPU is AMD EPYC 9V74 with AVX512 capability. Model SHA256 is `d14ab7c0f093efe64b60a7bcd540bca10e74fb7f46c86108a079af60524659d1`.

In-process D1 capture shows one PyTorch intra-op thread, a single CPU affinity, five configured inter-op threads, deterministic algorithms enabled, float32 default/model parameters, fast graph converter, MKLDNN enabled and highest float32 matmul precision. Configured inter-op capacity is not evidence that five threads executed concurrently; the process was restricted to one CPU. These are current D1 settings, not reconstructed historical baseline settings. The proposed future recorder will explicitly set one inter-op thread under a newly declared condition to remove that uncontrolled capacity; it has not been physically run.

Baseline provenance records package/Python/platform/model/device/seed/thread declarations and source/input/config hashes. It does **not** record CPU identity/ISA/microcode, effective backend flags, affinity, inter-op threads, runtime dtype, raw neighbor lists or graph arrays. Current probes cannot fill those unknown fields.

The CIF and serialized configuration match the saved baseline; all source/model hashes checked previously remain intact. Current fast and legacy graph constructors produce byte-identical atomic-number, fractional-coordinate, lattice, atom-edge, neighbor-image, directed/undirected mapping and bond-graph arrays. That rules out a difference between those two constructors for this current inspection only. It cannot establish historical graph equality. D1 captured actual converter output tensors. Its `neighbors.npz` came from a separate pre-hook neighbor query, not interception of the exact query consumed by the converter; this limitation is explicit.

## Declared experiment and stopping rule

Protocol SHA256: `43da0b0d217fe5c267a4d2b7aedd5f8e66fb9d8af2b4688b01a7b2e250ee4584`.

The proposed sequence was D1 instrumented restored control, D2 independent identical-process control, D3 generic ATen CPU-dispatch condition only if controls were exactly repeatable and reproduced the prior restored observations, and D4 generic repeat only if the dispatch condition changed output at identical captured graph/input/weights. This could demonstrate dispatch sensitivity; it could not identify baseline hardware.

The original criteria remain energy absolute tolerance 1e-5 eV, forces 1e-6 eV/Angstrom, stress 1e-7 eV/Angstrom^3, all with zero relative tolerance. Original failed force/stress maxima remain 3.039836883544922e-5 eV/Angstrom and 5.364418029785156e-7 eV/Angstrom^3. Original signed arrays, reports, manifests and directories are unchanged.

The ceilings were four additional evaluations, 600 seconds cumulative calculation-process wall time and 1800 seconds investigation time from 2026-10-23 18:35:41 UTC. The actual attempt count was one, using 3.173585715 seconds. The instrumentation exception activated the stop/no-retry condition. No CPU-dispatch contrast was executed. Consequently no claim of derivative sensitivity, nondeterminism or a corrected numerical result is supported.

## Failures, repairs and tests

Preparation first failed because a newly written script named `inspect.py` shadowed Python's standard-library module. Renaming that new script to `inspect_runtime.py` fixed the import; no model evaluation had occurred. The failure is retained in `preparation-failure.json`.

D1's graph/input/neighbor arrays, model-parameter tensor hashes, configuration, runtime, source recorder, logs, traceback and manifest are preserved. D1 observations/model-output files are absent. `execution.json`, `decision.json` and `comparison.json` retain this failed status.

A separate proposed recorder binds `matterlab` imports to explicit `MATTERLAB_ROOT`, wraps the actual bound `forward` method, captures the converter's actual neighbor-query return, and writes observations before capture-count assertions. It also explicitly sets one inter-op thread for a future diagnostic condition. The failing recorder remains unchanged. The proposal is **not physically validated** and is not a resumed or replacement D1.

Two synthetic recorder unit tests passed: direct `forward` bypasses the module hook while the wrapper captures the same return object; the neighbor wrapper captures the actual query once without reordering its return. These fixtures are not material measurements. Syntax compilation of the proposed recorder passed. The earlier 34 repository tests are frozen restoration evidence and were not rerun as part of this diagnosis.

## Independent review and export

An independent requested Astra High reviewer supports the hook-bypass diagnosis, unavailable numerical comparison and stop decision. The reviewer identified the repeated-neighbor-query limitation, ambiguous prior ledger wording, and the fact that `MATTERLAB_ROOT` alone did not bind Python imports. Review identity remains subject to the attestation limits above.

The frozen restoration bundle is preserved. A new public derivative corrects contradictory transformation labels, normalizes public provenance timestamps to UTC, and binds portable helper imports to the named checkout and saved source hashes. The named timezone in old source is a project convention, not evidence of the owner's location; original source snapshots remain byte-identical. Original physical observations, inputs and signed differences are unchanged. Every transformation records original and derivative SHA256 values. No account usage records, process/task/host identifiers, private paths or credentials are included in the new payload.

The new payload includes the failure and proposed repair rather than a successful diagnostic claim. It is staged for parent review only. The integrated publication audit, transformation audit and independent review artifacts specify the checks actually performed and their limits. No branch has been pushed.

## Public coordination and next action

GitHub connector reads independently verified `main` at public commit `f1fdd7fbe07b05c60cb2c15f808ddaa6c13a06bb`. A public content snapshot was downloaded without Git history, and all 323 entries of its publication manifest passed. This commit contains newer restoration/failure and cloud-ownership state; the proposed patch preserves it and adds the bounded diagnostic checkpoint. Before eventual publication, fetch/reconcile latest public state again and do not overwrite concurrent changes.

The parent reports the existing scheduled continuation actually woke at 2026-10-23 18:38:51 UTC for nominal 18:40:00 UTC, 69 seconds early under its flexible four-hour schedule. At that wake, current cloud work was detected and no duplicate calculation or task was started. This is parent-observed scheduler evidence, not a direct scheduler observation by this worker. Private scheduler identifiers and account metrics are excluded. First wake is verified by the parent; full migration and independent GitHub-backed evidence resume remain incomplete. Local fallback remains available and defers to active cloud work.

The narrow next action is parent review and publication of the audited additive checkpoint, followed by a fresh-gated, separately declared one-evaluation recorder-validation test using the proposed repair. Require saved observations, actual consumed neighbor arrays, graph and model-output captures, and verified imported source before considering any dispatch contrast. Preserve the original failed tolerances and baseline unknowns. The repaired inter-op setting and recorder are new conditions, not retroactive corrections. No S1/S2/S3 work, DFT, synthesis, stability, novelty or application claim follows from this investigation.


## Final read-only checks

All eight actual D1 graph tensor arrays exactly match the earlier current-environment inspection graph; see captured-array-comparison.json. This supports current graph-construction consistency across those two contexts only. Historical baseline graph arrays and D1 numeric observations remain unavailable.

The proposed recorder now requires MATTERLAB_EXPECTED_CODE as well as MATTERLAB_ROOT and checks all saved source hashes before inference. Capture callbacks can themselves raise before ASE outputs become available; the repair does not promise output retention under every exception. The synthetic tests cover direct-call interception and return/order preservation, not full CHGNet integration.

The initial full staging audit rejected a generated tools/__pycache__ directory from importing the auditor. Only that generated staging cache was removed, and the audit was rerun with bytecode writes disabled; no source, saved check or old evidence was changed. This operational failure is retained privately. The repository's unmodified audit is used directly on the integrated public tree; the quantum exporter intentionally rejects re-exporting an already public derivative, so no historical quantum export or calculation was restarted.
