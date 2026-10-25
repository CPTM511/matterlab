# Association candidate-v2 whole-path reconciliation

Outcome: NOT READY. This is a separately bounded source-review stage. It does not extend either prior preparation stage, repair the implementation, or release scientific execution.

The exact candidate remains unchanged: implementation-manifest SHA256 97aa54fee56a7cc0d5b45a313035b90957f7d22902db8fcf673a4c06d7940649; preparation-only freeze SHA256 9518d5548c001cfed1463bbf68a5025ad1596ec67d60b52fc6e7afb07c76b0c8. All 21 declared members match; with the two envelopes, coverage is exactly 23 files. The previous missing REVIEW.md and review.json remain absent. This new review is not attributed retrospectively to the completed preparation.

Saved final receipts bind to final source bytes: guards 35/35, state/comparator/native-budget 54/54, capture/runtime/path/cleanup 25/25, symbolic adapter/mutations 14/14, and eight bundle metadata checks. These receipts were read, not rerun. The earlier guard receipt remains 34/35 with external_symlink_blocks failed. The earlier state/comparator receipt binds an older controller hash; the final receipt binds the current controller. Passing unit and symbolic receipts do not establish the complete launch path.

Two unresolved source-level findings block preparation acceptance:

1. Strict wall-time enforcement is incomplete. controller.py masks SIGALRM and SIGTERM across Popen. A stalled spawn can therefore delay deadline handling; the later wait allowance and elapsed check detect an overrun only after spawn returns. After the one-shot investigation alarm, cleanup can wait another second and terminal/manifest I/O has no remaining watchdog. The existing fixtures test state arithmetic and a mocked bounded reap, not those lifecycle paths. The intended 60/120/600-second bounds cannot be claimed fully enforced by this frozen source.

2. Freshness is checked before potentially blocking metadata work rather than immediately at each sensitive boundary. In the launch loop, coordination and reference hashing follow the release check. Native context validation likewise performs coordination/reference work after its freshness check; forward input comparison and added-query setup follow. A previously fresh observation can expire before launch, forward or the added derivative. Stale-at-entry fixtures do not cover this elapsed-check gap.

The prior report's statements about enforcement describe implementation intent and are not whole-path certification. Its bytes remain preserved. No fix or additional fixture is authorized by this review. The next decision is whether to admit a separately bounded repair and independent negative-fixture review addressing these exact findings while keeping the same scientific design and thresholds. The candidate must not execute meanwhile.

The stage started 2026-10-25T18:54:31.347117+00:00 with immutable deadline 2026-10-25T19:04:31.347117+00:00. Current public main was b2895ba36bbab3e93e409a0c3975d0250c8134f6, checkout clean, public active_work empty, and the initial process scan found no competing scientific process. The association anchor was absent. The same restored dedicated workspace was used; no owner-computer access or independent durable-host attestation occurred.

No candidate edits, new fixtures, scientific-array calculations, torch/model imports, forwards, AD queries, scientific entrypoint invocations, attempt claims, installations or publication occurred. Requested configuration remains Astra High/Standard; actual serving identity is not independently attested. All historical failures, consumed attempts, original Sol Light provenance, stopped precision contrast, incomplete migration/S1 and fallback remain unchanged.
