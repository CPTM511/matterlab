# Independent pre-execution review of P1

The reviewed protocol and implementation are suitable for the parent's exact-hash review and possible later release. No material issue remains in the inspected source and tested metadata behavior. This conclusion is not execution permission. No P1 evaluation, execution release, actual attempt token, publication or schedule action occurred in this review.

## Exact review boundary

This review applies to the following SHA256 identities:

| Artifact | SHA256 |
|---|---|
| `PROTOCOL.md` | `8818e943d53d64884c9ed0ad7e7b35836627fb9cb611ec92e7a9c9dbcfc442c7` |
| `protocol.json` | `65edd51f107018e757b920fcc339789373b1dbba498bd2f71aef7423d41d6d7f` |
| `implementation-manifest.json` | `7e4b3630e23d721486a59d6342fd303b25eeaab1dea4d1faf525f89696c42c7f` |
| `control.py` | `96c528df9dea67d6185e2f04eb60ff47cddd05083f4dd2a3929a16e196d83380` |
| `guarded_recorder.py` | `530bedca0d338401a8f3821fb21f98bb3569f26f6f1efe2f612d07ba0e052419` |
| `runtime_compare.py` | `65c4ab2017a8485b6c38ff2c3395a21d7e450fdfcce36c19160b0722535700d6` |
| `analyze_saved.py` | `538e50281b2ec25589e226a8f12e5493ad44a9d1b62b136e9923efc24df5b59c` |
| `preflight.py` | `c203ef0f9952179b1f00924867265086be67c6c829707d481bde1c60deb01615` |
| `child_entry.py` | `80f2ff4956dc9a6333bc47758e9d43c44adb7a38a4978510ac2d550b1bdc816e` |

All 12 implementation-manifest entries and the protocol's Markdown, implementation and reference bindings verified. `final-hash-verification.json` records every reviewed implementation digest and preservation check. The final freeze envelope will be added afterward to pin this review and these identities; it is intentionally outside this review's hash boundary and must not substitute for a separate parent release.

The scientific reference is public commit `91147ff73336ce205717117b2ab7de3e62c5fdb1`, parent `2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1`. I independently checked the local published checkout, its manifest/audit digests, pinned reference records, clean Git state and parent commit. The original draft remains unchanged, including Markdown SHA256 `699161bffb5cc5b9fdc10d0d0d3c5f9aac93f891e5fba7173b04016cd60699b7`. Superseded findings and test failures remain available rather than being relabeled as passes.

## Scientific assessment

One fresh process under saved C1's default-dispatch condition is a useful, minimal test of pairwise exact repeatability. The saved C0 already supplies a fresh control matching R1. Another backend setting or control calculation would broaden this question without being necessary for the stated test.

The primary P1/C1 comparison correctly retains every runtime field and the entire build-description string except the condition label. It validates both representations of the capability and rejects malformed, duplicated or contradictory capability text. Only the secondary descriptive C0 comparison excludes the three explicitly declared intervention representations. That diagnostic comparison cannot rescue a failed primary gate or change the old frozen C1 result.

Exact output equality covers all six model tensors and all ASE observations. Array comparisons require matching shapes, dtypes and contiguous data bytes, including signed zero. JSON metadata comparisons are type-sensitive. The original float32 energy scaling and stress conversion/symmetrization are preserved; independent saved-C1 arithmetic demonstrated that an early float64 upcast changes the result and therefore must fail exact conversion.

The assertion-only recorder derivative is justified because it can stop before forward when recorded inputs, graph, parameter hashes or runtime differ. The published recorder/helper bytes are preserved. Removing only the added guard import and named calls from the derivative yields the same syntax tree as the published recorder. This is source-level evidence; the derivative has not been physically validated. A later mismatch would not isolate its instrumentation effects from other unrecorded effects.

H1, H2 and inconclusive outcomes are separated correctly. A success establishes equality only for this pair under the recorded fingerprint and guard derivative. It does not measure a variability distribution, identify historical hardware, rank physical accuracy, complete migration or establish readiness to interpret Gamma results. Gamma displacement-size, graph-continuity and finite-difference-noise questions require their own reviewed protocol.

The original force/stress failures, unchanged `1e-5`/`1e-6`/`1e-7` absolute tolerances with zero relative tolerance, failed frozen C1 gate, unrun C2 and retained fallback remain explicit. No post-hoc exclusion repairs the earlier gate.

## Verification actually performed

- **685 initial integrity checks passed:** public and original-draft manifests, pinned reference records and publication-readback receipt digest.
- **1,498 metadata/hash preflight checks passed:** actual installed Python, dependency versions, CHGNet sources, cached model/native-library digests, imported project source paths, raw input/configuration, CPU identity fields and preserved historical state. This loaded project modules but constructed no model and executed no forward call.
- **Independent comparator and conversion fixtures:** type substitutions, unknown fields, altered build flags, signed zero, dtype changes and saved float32 conversions were tested. The initial comparator's type-equality and malformed-duplicate defects were demonstrated, retained and fixed.
- **12 final analyzer/comparator fixtures passed:** copied-public-C1 positive data; truncated archives; missing hash, tensor and observation fields; malformed runtime; synthetic changed outputs; dtype changes; nonfinite tensors; changed raw config; completely missing capture; and malformed duplicate capability text. Available comparisons and an explicit decision remained available. These were clearly labeled unit-test fixtures, not new scientific observations.
- **39 release-validation fixtures passed:** exact protocol/implementation hashes, each required ownership/authority flag, stale/future/non-UTC timestamps, unavailable or blocked windows, boolean fractions, spending restrictions and investigation limits. They used fictitious in-memory release data; no actual release file was created.
- **Five dummy-process/token checks passed:** timeout and SIGTERM cleaned up direct child and grandchild processes, failure timings were retained, and a second exclusive marker claim failed without altering the first. A separate parent-death fixture also passed after its dummy controller received SIGKILL.
- **31 final-decision fixtures passed against the final controller:** incomplete/failed execution or analysis, invalid attempt counts, missing/nonfinite/negative/over-limit timings and resource breaches cannot become protocol acceptance. A valid process record cannot upgrade a failed numerical result.

The dummy-process tests used controller hash `ceef44f0fa018507a8c337f113e4b4b793efa900f3adb29a573f461a5e018bbd`; the parent-death fixture used child-entry hash `b716ca189c5824298437fa8036c37c5326b328ce9289c00f69a738095ced5db2`; release fixtures used controller hash `8e29a2ec251b6e80725df421f1421133e94f1011d8b493fcbbf0caaf1519b4b0`. Their relevant routines were retained in the final source. Later changes added bounded analysis, final resource classification, provenance copying and repeated coordination/bundle checks, which were source-reviewed. The final resource fixtures directly tested the final controller digest listed above. I did not execute the complete controller or inference branch.

## Operational and audit limits

The controller now checks pinned remote coordination, local HEAD/clean status/STATE, known calculation processes and exact bundle hashes at the prescribed points. The future launch requires fresh private usage/ownership attestations bound to the exact protocol and implementation. The fixed exclusive token is claimed before preflight. It blocks another attempt within the retained package location; the protocol additionally forbids deleting it or copying the package to bypass that boundary. Timeout handling, process-group cleanup and parent-death protection reduce ordinary cancellation risk; they cannot guarantee survival or complete records during catastrophic host/kernel failure. Uncertain outcomes require inspection and no retry.

My independent checks establish the local published and installed-runtime evidence described above. I did not independently query the account, scheduler, other hosts or live remote head. The parent supplies current cloud ownership and reports a fresh public-head/process check; future fallback/scheduler non-overlap and usage gates remain required. Known-process scanning is not a distributed lease or universal proof of idleness.

The public receipt's 643-file publication audit is pinned evidence, not a new full publication/sanitation audit performed in this review. No new public derivative is being released. Any future evidence export still needs its own complete manifest, transformation ledger and sanitation review. This report contains no account readings, private task identifiers or private execution paths.

Requested reviewer configuration was GPT-6 Astra, High reasoning, with Standard speed where selectable. The parent reports the model/reasoning delegation settings; the exposed developer identity is GPT-6-based Codex. No speed selector or independent backend variant/effort/tier attestation is available. I performed source review, metadata/hash checks, saved-data arithmetic and dummy-process fixtures only, writing solely to the new reviewer area. No inference, installation, credential/account access, publication, schedule action or further delegation occurred.

## Remaining gates

No material source-review blocker remains for the exact identities above. The additive freeze envelope, the parent's reading/release of the exact protocol, and fresh future entry attestations remain pending. P1's numerical outcome is unknown because it has not run. Historical numerical acceptance, old C1 failure, untested altered-condition repeatability and all Gamma/DFT/application questions remain unresolved. This review does not release the evaluation.
