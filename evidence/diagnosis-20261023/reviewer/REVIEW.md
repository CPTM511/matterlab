# Independent read-only review

Status: ready for parent review. Protocol, retained failure, proposed recorder, and staged public export reviewed; identified documentation and source-verification findings addressed. Parent must incorporate this final review and regenerate affected publication artifacts and audits before publication.

The requested reviewer configuration was GPT-6 Astra with High reasoning. Observable identity is GPT-6-based Codex from the supplied developer identity. Actual model variant, reasoning setting, and service tier are not independently attested.

## Scientific decision

The frozen protocol appropriately separates exact current-process repeatability, graph/input consistency, and a selected ATen CPU-dispatch contrast. Such a contrast could establish sensitivity under the measured conditions, but cannot reconstruct historical CPU, graph order, or effective backend settings. Matching current fast and legacy graph arrays cannot establish historical graph equality.

The diagnostic stopped after one attempted D1 single point. The recorded process returned 1 after 3.1735857149999447 seconds. The failure is an instrumentation assertion: one graph capture and zero model captures. The evaluator registers a model Module forward hook, while the inspected installed CHGNet predict_graph implementation calls self.forward directly. That call bypasses the registered Module hook. This explanation is supported by the retained source and traceback.

The traceback points to the capture-count assertion after the finite-output assertion and before observations are saved. Thus the execution trace supports reaching the finite-output check successfully; it does not preserve numerical energy, force, or stress values. Neither observations nor raw model output can be reconstructed from the retained input, graph, and runtime files. Empty comparisons correctly mean unavailable comparisons. They must not be replaced by zeros, guessed values, or an inference of exact repeatability.

Stopping without D2, D3, D4, or a retry follows the frozen stop-on-exception rule. No result establishes repeatability or CPU-dispatch sensitivity. The original restoration remains FAILED under energy atol 1e-5 eV, force atol 1e-6 eV/Angstrom, stress atol 1e-7 eV/Angstrom^3, and rtol 0. The instrumentation failure does not change the earlier recorded force/stress failure.

## Proposed repair and evidence limits

A separate, labeled repair wrapping the bound model.forward and returning its result unchanged can intercept direct-forward calls. Save available observations before capture assertions so an instrumentation failure cannot discard computed observables. A synthetic small-tensor test can validate wrapper behavior and output preservation without another physical evaluation. Such a test does not validate CHGNet numerics, the full repaired evaluator, or migration acceptance. Any later physical run needs its own declared protocol; this frozen run must remain unchanged.

The pre-graph hook obtains neighbors through an additional get_neighbor_list call. Its saved neighbor arrays represent that separate query, not interception of the exact query consumed inside the graph converter. The captured output graph tensors remain useful direct graph evidence. Label the neighbor-query limitation rather than claiming captured internal neighbor consumption.

The runtime file explicitly captures settings before inference. Preserve that stage description. Graph arrays and parameter hashes are useful surviving artifacts even though output comparisons are unavailable.

## Prior export review

Targeted reading and text scans found no obvious raw workspace/home path, hostname, credential, subscription value, or private execution/task identifier in the prior candidate. This bounded review is not a universal absence guarantee or an independent rerun of its hash verifier.

Two transformation-ledger entries, test-results.json and pip-check.log, describe a byte-identical copy and also subsequent sanitization, while original and public hashes differ. A new derivative should describe the final transformation accurately. Preserve the frozen prior export and its original ledger.

The portable evaluate.py uses MATTERLAB_ROOT for files and source hashing but imports matterlab before using that variable. Consequently the imported package is not independently bound to the named checkout. A future portable reproduction should verify the loaded module path and relevant hashes, and verify the exact input/config bytes before evaluation. The prior report correctly discloses that its portable helper was not executed.

The prior source explicitly hard-codes a named timezone and therefore explains matching local offsets in provenance. These fields are a project timestamp convention, not evidence of the owner's location. UTC-normalized public metadata may minimize unnecessary context, provided the conversion is recorded and original source/evidence remain intact.

Historical provenance fields external_api_calls=0 and paid_compute=false are hard-coded source declarations, not independent usage metering. Do not describe them as measured service or billing attestation.

## Scope and remaining gate

This reviewer read files and source only; no model evaluation, scientific calculation, network access, installation, publication, schedule change, or credential access was performed. Only reviewer documents were written. Publication remains pending parent review. Scheduled-wake information was communicated by the parent and is not independently verified by this review.

## Final staged-export review

The new diagnosis report honestly distinguishes the one failed attempt, unavailable outputs, unchanged original force/stress failure, and unexecuted D2/D3/D4 conditions. Its identity statements avoid model/reasoning/tier attestation. The proposed STATE changes preserve the supplied public-base coordination and identify scheduled-wake evidence as parent-observed. This reviewer inspected the supplied STATE diff; remote freshness and scheduler evidence were not independently checked.

The proposed recorder inserts MATTERLAB_ROOT/src before importing matterlab and verifies the resolved package path. The restored portable helpers also check source hashes against saved code.json. After review feedback, the proposed diagnostic recorder additionally requires MATTERLAB_EXPECTED_CODE, checks all recorded source hashes before inference, and saves that reference. CLOUD_START identifies the saved restoration code.json to use. Exact input/configuration/model checks remain a mandatory preflight gate before any future inference.

The bound-method wrapper calls the original once, supplies its return to the callback, and returns the same object. The proposed graph pre-hook wraps the actual structure.get_neighbor_list method, which the installed graph converter directly calls. Capture callbacks serialize values without an explicit in-place numerical modification. Observations are written before the final capture-count assertion. A callback exception can still interrupt inference before the ASE observations become available; the repair does not guarantee output retention after every possible exception. The separate failure path must remain available.

The two supplied synthetic tests exercise direct-forward capture and actual neighbor-query return preservation. Their log reports two passes. This reviewer inspected source and the existing log, but did not execute these tests, compile code, or run CHGNet. These tests establish neither the complete repaired workflow nor physical replay success. Explicit inter-op thread count one is correctly labeled a new future condition.

The corrected prior ledger removes the contradictory byte-identical labels for the two sanitized files. The new ledger identifies its inputs as frozen public derivatives, so byte-identical labels there refer to that second-stage boundary. Public metadata normalization leaves the historical source timezone convention unchanged. Targeted scans of the new evidence payload and ledger found no obvious private paths, task/process/host identifiers, account values, or credentials. No blanket privacy or billing guarantee follows.

The supplied sanitation-review.json reports passing checks for 444 files, nine archive members, and 284 evidence hashes plus a private-marker scan. These are inspected audit results, not checks independently rerun by this reviewer. Binary archives were not independently decoded in this review.

The restoration README correction was inspected and closes the packaging finding. It now identifies current local and repository publication manifests, the current parent-directory transformation ledger, and the provenance-only roles of prior manifests/ledger. It explicitly distinguishes the unchanged historical REPORT from current instructions. New root evidence manifests were added by the parent. Incorporate this final reviewer version and regenerate affected hashes/ledgers and the integrated publication audit. No further physical calculation is required for those packaging steps.

The supplied captured-array-comparison.json reports all eight current D1 graph tensors exactly equal to the initial current inspection, with matching shape/dtype/hash records. Its scope expressly excludes historical graph comparison. This reviewer inspected that report rather than recomputing the arrays. It does not supply the missing D1 numerical outputs or demonstrate process-output repeatability.

No unresolved scientific-honesty, static portability, or obvious private-metadata blocker remains within this review's bounded scope. Readiness is for parent review of a failed diagnostic and unvalidated proposed repair, not a successful numerical replay, migration-completion claim, or permission to bypass final publication checks.
