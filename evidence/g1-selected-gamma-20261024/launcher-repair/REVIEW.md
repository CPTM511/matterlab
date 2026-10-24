# Independent G1 launcher-repair preparation review

Outcome: no unresolved finding within the launcher-only preparation scope. The tested launcher prevents the observed initial bytecode-write failure without weakening exact bundle coverage. Scientific execution remains blocked: the candidate status is launcher_repair_preparation_only, and the original G1 release remains stopped on exception. This review does not promote status or authorize another numerical attempt.

Exact SHA256 identities:

- launch.sh: a55e5474b646675c60690c16988a40673c7ce47cacb89a47e0575e4e305bc08f
- REPAIR.md: 1a68b879f04bec71dcea0e684e7f1e11e3fe721359c1d83cfc7ab13148e9d6df
- implementation-manifest.json: 0feee37484be73feb72e20d5844cfe9542a0c0f4da499e9bd723f679754da3b4
- freeze.json: e739e06eeab416da82023068444030804c8874ed4a5d1a2b2abd765c934ba45a
- minimal.diff: 40258df72f4d879bc6ebb3c6101d31008332e69d9abbf83b6aa5b7666a8144cb
- Unchanged protocol.json: 7998bd0674d03c7ed8ebc45062578c78982fac73b6898b7b831a8a803f2e1382

The candidate has 19 files: 15 original files are byte-identical, two bindings are derived, and launch.sh plus REPAIR.md are added. Its implementation manifest covers 16 entries. I verified all hashes and regenerated the exact supplied diff. Scientific protocol text, points, arithmetic, recorder, runtime comparison, preflight, controller and process guards are unchanged. The original frozen bundle and its unexpected cache remain unchanged; the cache was not deleted to obtain a pass.

The shell launcher supplies -B to the separately verified interpreter before run_gamma.py imports control_common. This addresses the observed ordering defect. The launcher requires MATTERLAB_PYTHON; it does not independently authenticate that interpreter. I verified the tested interpreter's file hash against the retained runtime reference. The flag suppresses writes, not reads of existing bytecode, so the unchanged rejection of unexpected files remains necessary.

Independent verification passed 58/58 checks, including three actual metadata-only launcher/controller probes. Before each probe I checked the exact launcher and controller identities, preparation-only status, absent protocol anchor and nonexistent release. Inherited bytecode-suppression and cache-prefix environment settings were removed so they could not explain success. Each process had a 10-second timeout.

The clean candidate exited 1 with Not reviewed/released, after passing bundle integrity and before release reading, anchor claim, output creation or child preflight. Separate fixture copies with an inert unexpected Python source file or inert unexpected bytecode file exited 1 at exact coverage with Unexpected or missing frozen bundle file. All before/after file comparisons passed, no new cache or output appeared, and no protocol token was claimed. The three measured subprocess wall times totalled 0.113503188 seconds; these are metadata-test timings, not physical calculation performance. The original bundle and all 19 candidate hashes were unchanged afterward.

The executing role separately reported 38/38 checks, including optimization rejection, missing-interpreter rejection and a dummy interpreter-flag check. Its first aggregate candidate_before_after_identical value was a literal true placeholder. The original script and receipt are preserved, and a separate saved-file comparison clarifies all 19 identities without rerunning that launcher suite. I inspected this defect and clarification. My independent before/after conclusions come from actual hash comparisons, not that placeholder. I did not independently repeat the executing role's additional cases.

These probes were expressly authorized preparation tests, using no real release. They are not a retry under the stopped scientific release. An absent anchor is not permission to proceed; the repair assigns no new scientific protocol ID, resets no resource clock and changes no no-retry rule. Any future scientific continuation requires a separate parent decision resolving that boundary and exact renewed authorization. Nothing in this review supplies it.

Prior failed invocations, cache evidence, reviewer failures, original numerical acceptance failures, failed historical C1 and unrun C2 remain preserved. The displaced-input recorder is still physically unvalidated, and this repair provides no new material evidence. Any later review-copy or freeze-envelope update must retain these identities and explicitly state its new boundary; previous reviews do not attest the new manifest automatically.

Requested role: Astra High; observable identity: GPT-6-based Codex without independently exposed serving variant, reasoning level or speed attestation. Controller code ran only through the authorized metadata rejection paths described above. No model import/construction/forward, scientific calculation, token claim, source repair, installation, remote/account/schedule action, publication or delegation was performed by this reviewer.
