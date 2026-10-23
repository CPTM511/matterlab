# MatterLab cloud restoration and single-point replay

Prepared 2026-10-23T18:29:13.789180+00:00. Validation ID: matterlab-restoration-20261023T182448Z.

## Outcome

Restored evidence integrity and one real cloud calculation were verified. Numerical replay acceptance **FAILED**: energy is identical to both baselines, while forces and stress exceed the tolerances declared before evaluation. No further calculation was attempted, and no tolerance was relaxed. This is not migration completion.

The one saved `evaluate.py` invocation ran from 2026-10-23T18:26:16.208976+00:00 to 2026-10-23T18:26:19.282688+00:00, returned 0, and took 3.073684402 seconds under a 600-second wall limit. Execution used CPU affinity to one available CPU and one thread for PyTorch and numerical libraries. It evaluated the initial 20-atom CaTiO3 reference without relaxation. All outputs were finite.

| Quantity | Result versus each of the two baselines | Predeclared absolute tolerance | Result |
|---|---|---|---|
| Total energy | -166.1494140625 eV; difference 0 | 1e-5 eV | PASS, exactly equal |
| 60 force components | maximum absolute difference 3.039836883544922e-5 eV/Angstrom | 1e-6 eV/Angstrom | FAIL |
| 9 stress components | maximum absolute difference 5.364418029785156e-7 eV/Angstrom^3 | 1e-7 eV/Angstrom^3 | FAIL |

Relative tolerance is zero. Every signed component difference is in `comparison.json`. These strict criteria concern numerical replay, not the accuracy of the ML potential. The cause of derivative drift is unresolved. Matching package, platform and model hashes does not prove identical hardware or every numerical-library execution detail; the saved baseline lacks a comparable CPU/backend fingerprint. No cause is asserted from this single replay.

## Runtime and identity

Source SHA: `3319dc595397f68c0e7a3326e64c2b27ae799027`. Native cloud Linux x86_64, Python 3.12.14, platform Linux-6.18.55-x86_64-with-glibc2.41; installed PyTorch 2.6.0+cpu; CHGNet package 0.4.2, pretrained model 0.3.0. The helper log records 412,525 model parameters. Model SHA256: `d14ab7c0f093efe64b60a7bcd540bca10e74fb7f46c86108a079af60524659d1`.

Requested assistant configuration: GPT-6 Astra, High reasoning, Standard service tier. Independently exposed assistant identity is GPT-6-based Codex. Actual variant, reasoning setting and service tier are not exposed by authoritative runtime metadata and remain unverified. The setup began under the UI default Sol Light before the selector changed according to the owner; its whole run cannot be described as Astra-only. No model API or delegated agent was used.

## Startup, integrity and tests

The selected saved cloud environment restored the dedicated repository and onboarding directory. Git status was clean on branch `work`; repository `active_work` was empty and the visible process table contained no competing scientific calculation. This check covers this environment and the saved coordination state, not unknown external jobs. No owner computer, private repository history, subscription credentials, network service, installation, package upgrade, schedule, publication or historical campaign was used.

The root workspace itself is not a Git checkout; the first Git status there returned the expected error, then inspection proceeded at the dedicated repository. Required repository instructions, cloud migration guidance and the saved onboarding report were read. `start_skill` was mentioned in the saved report but was not exposed as a file, injected startup instruction, or readable environment-settings tool. Its full content and restoration are unverified. The saved report and explicit delegation independently supplied the replay command and gates used here.

All 285 onboarding manifest entries and both 16-entry baseline manifests passed SHA256 verification. Both complete checkpoints, helper, input, all eight MatterLab source files, exact saved configuration serialization, Python/platform/package provenance and all three installed model checkpoint hashes matched. The corrected preflight has 37 passing checks; `pip check` passed. All 16 new replay manifest entries passed.

An initial preflight check failed before any evaluation: source configuration bytes (800 bytes) differ from the helper's formatted JSON snapshot (1249 bytes). Exact parsed values and the unchanged helper serializer both match. The initial protocol, checker and failed preflight remain intact; `preflight-correction.json` records the correction to the checker. The raw source config hash is `e270d736f658e73a5491ed75a5aaa7269ecb53fd923615e066ea807d3ec70601`; the saved serialized config hash is `34e39cf96b437bb7fbbc18266942cc00d7135a0dd7e9e83d7909f702b8a0f4bc`. Existing source/checks and numerical tolerances were unchanged.

All 34 existing tests passed (22 scientific and 12 publication guard tests), with five warnings and no skipped or failed tests. `test-results.json` lists every test outcome; `pytest.log` retains the warnings. These unit tests do not override the failed force/stress replay comparisons. No dashboard, new campaign, DFT or external physics test was run. The old onboarding test claims were not treated as results of this task.

## Evidence and limitations

`replay/` contains raw CIF, energy/force/stress observations, configuration, source snapshot, model/package provenance, original saved helper, checkpoint and manifest. `evaluation.log`, `execution.json`, `protocol.json`, `preflight.json`, `runtime-hashes.json`, `torch-runtime.txt`, `comparison.json` and the retained initial failure provide supplementary evidence. Original onboarding evidence was rehashed after the replay and is unchanged. Only live repository coordination state is updated separately with this task's outcome.

Onboarding manifest SHA256: `52ad334c0dfac1a3a3fe86090ed04ddeb2695a75d446ab158e9cf70451298381`.
Baseline 001 manifest SHA256: `ab1f71f40775f51bc22757620b61e92f3416688bdabc202f698fb825f40f0e5d`.
Baseline 002 manifest SHA256: `f6d98f5dc1e94ec3f2bbe6991481f00e508632c811f3188ae94bccfee6cc6e00`.
New replay manifest SHA256: `5b90b8ca06653ab8356bcee7df836a9af9d575e1284d93db7fc59dd738dce54e`.
Input SHA256: `1fe444e55772222e8f09e8b333901a94efdc701ef96909a4c22462087185cdd0`.
Original helper SHA256: `16b46c145d371a85266e9c8502c693712396b047361e60eb46533d55bc376b8b`.

The `public-candidate/` directory is a review-only additive evidence bundle, not a complete repository export or a published commit. Its transformation ledger maps original logical file labels and SHA256 values to public derivatives and records omissions. Original manifests are retained as provenance documents; transformed derivatives have new manifests. Public helpers replace the private absolute root with the explicit `MATTERLAB_ROOT` environment variable. This portability edit has not been executed in this task. Raw physical observations, input, source snapshots and model hashes retain their original bytes. Account records, private execution identifiers, host metadata and paths are excluded or transformed. The bounded content scan complements manual review; it is not a universal guarantee against unknown private metadata.

These are ML-potential observations, not DFT, experimental synthesis, evidence of candidate stability, novelty, or application performance. They do not resolve S1/S2/S3 or establish recurrence, GitHub durability, or retirement of the local fallback.

## Exact next steps for GitHub-backed resume

1. Parent reviews this failed numerical comparison, the saved-startup gap, requested-versus-observable model identity, `public-transformation.json`, and `sanitation-audit.json`. Inspect the existing native task inventory before separately handling recurrence; this task creates none.
2. After review, use a clean checkout of the authorized public repository. Copy only this additive public candidate beneath a new evidence directory; preserve existing evidence. Do not push this private workspace or its Git history. Integrate the additive path into the repository's publication export allowlist and run its unmodified full export/audit workflow before publishing. Record the resulting public commit SHA and content manifest hash. No push has occurred here.
3. Save an explicit portable startup instruction file and a coordination checkpoint in that public commit. Record the failed comparisons, no active job, source/model/dependency pins, and exact pending bounded diagnostic. Do not mark replay acceptance passed. Retain the local fallback.
4. A later authorized task in the same published environment must verify the public commit and candidate SHA256 manifest, confirm no overlap and current included allowance, and read the saved startup instruction. Install nothing unless separately required and authorized. `MATTERLAB_ROOT` must point to the verified checkout. A possible new replay command is `MATTERLAB_ROOT=CHECKOUT CHECKOUT/.venv/bin/python EVIDENCE/replay/evaluate.py NEW_OUTPUT_DIRECTORY`, under the same one-thread/600-second controls. It is a future action, not a second invocation in this validation.
5. Before any new calculation, separately predeclare a bounded investigation of the force/stress drift, preserve this failed criterion, and decide what numerical evidence is needed. Verify actual task/model/recurrence and an independent GitHub-backed checkpoint resume before transferring responsibility or retiring fallback. No S1/S2/S3 launch is authorized by this report.

## Final coordination and diagnostic preparation

After this calculation, the parent reported that one MatterLab recurrence is already saved. This worker did not create, change, or independently verify that schedule or its actual wake. Do not create another recurrence. Parent will refresh the usage gate and coordinate a later bounded diagnosis after reviewing this report. No further calculation is performed in this turn.

`hardware-backend.json` records available CPU identity/ISA and the installed PyTorch build/backend capabilities, collected in a separate process after evaluation. It distinguishes source-enforced settings from directly observed post-run settings. The baseline lacks CPU/ISA/microcode, affinity, backend build/runtime details, inter-op thread count, effective dtype/backend flags, graph neighbor/edge ordering and intermediate tensor hashes. Exact CIF bytes establish saved input order, but not runtime graph ordering. These missing fields limit causal attribution. Preparation did not construct a graph or run another model evaluation.

The first sanitation scan failed on a private pip-cache home path and synthetic private-path/credential strings in parametrized test names. The initial scan result remains in private evidence. Public derivatives replace those strings with explicit logical markers, preserve test outcomes and warnings, and record updated hashes in the transformation ledger. The later passing scan does not erase the initial failure.
