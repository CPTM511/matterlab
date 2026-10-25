# N1 native reference-curvature result

Outcome: one permitted reference forward and both added native derivative queries completed. The exact G1 baseline gate passed. Native reciprocity passed the selected 0.005 eV/Angstrom^2 criterion; all 12 selected native-versus-saved-finite-difference comparisons FAILED that unchanged criterion. This is a discriminating numerical observation, not a correction of G1 or a physical-accuracy result. No retry or additional calculation occurred.

## Execution and identity

The immutable investigation began 2026-10-24T12:56:10.647491+00:00; its hard deadline is 2026-10-24T13:26:10.647491+00:00. The single calculation process ran from 12:58:05.862476 to 12:58:23.218483 UTC, returned0 and used17.356001833002665 seconds of the600-second cap. The controller recorded132.57105300000012 seconds elapsed since the original investigation start at process finalization. Reporting and independent review belong to that same clock; their terminal receipt records the later completion, not a reset.

One N1 scientific anchor, one launch token and one forward token are consumed. Recorded native grad calls: one original force call, one original stress call and two added row queries. Graph conversion, actual consumed-neighbor query and bound model forward each occurred once. Preflight passed3424 checks. No controller remains active at terminal process inspection. G1's previous anchor remains intact and consumed. The raw execution record and signed-comparison record still say pending independent review; the later independent review is additive and does not rewrite those original records.

The checkout is public commit c3c089ff893dda65d12713aea49d9a17a08991be. Physics source remains3319dc595397f68c0e7a3326e64c2b27ae799027, CHGNet0.4.2/model0.3.0 with checkpoint d14ab7c0f093efe64b60a7bcd540bca10e74fb7f46c86108a079af60524659d1. Actual recorded fingerprint is CPU affinity[0], NO AVX/default dispatch, float32, seed20261024, numerical-library and PyTorch intra/inter-op threads1, Python3.12.14 and PyTorch2.6.0+cpu. All six output tensors, inputs, graph, neighbors, ASE observations, parameter/configuration records and full runtime matched the saved G1 reference; only the predeclared condition label differs.

Requested agent configuration was Astra High and Standard speed. The observable interface identifies GPT-6-based Codex; serving variant, reasoning effort and speed were not independently attested. Model construction and two added native AD queries occurred only in the permitted child process; review and report arithmetic use saved evidence.

## Native observations and signed comparisons

The captured finite scalar before intensive normalization/composition addition is -18.561548233032227 eV (float32). It is the actual scalar passed to native force differentiation, not the returned total ASE energy. ASE energy is -169.5611572265625 eV, exactly the saved G1 baseline; these quantities have different normalization/reference semantics and their difference is not a diagnosed conversion error. Native atom-position tensors and both complete60-component rows are retained as float32 NPZ arrays; a readable JSON rendering is also retained without changing originals.

The selected native block, with row and column order[50,59], is [[14.91781997680664,-2.1931087970733643],[-2.1931121349334717,5.674581050872803]] eV/Angstrom^2. Signed reciprocity A[50,59]-A[59,50] is +3.337860107421875e-06 eV/Angstrom^2: PASS at0.005,rtol0. Rows are -dF_j/dR from the original retained position graph. Saved FD columns use -(Fplus-Fminus)/(2h); conversion to float64 for subtraction does not restore lost float32 information.

| h (Angstrom) | row j | column k | Native (eV/Angstrom^2) | Saved FD | Native minus FD | Within 0.005 |
|---|---:|---:|---:|---:|---:|---|
| 0.015 | 50 | 50 | 14.91781997680664 | 16.688712437947594 | -1.770892461140953 | FAIL |
| 0.015 | 59 | 50 | -2.1931121349334717 | -2.3287793000539145 | 0.13566716512044286 | FAIL |
| 0.015 | 50 | 59 | -2.1931087970733643 | -2.405349413553874 | 0.21224061648050974 | FAIL |
| 0.015 | 59 | 59 | 5.674581050872803 | 5.886479963858923 | -0.21189891298612018 | FAIL |
| 0.0075 | 50 | 50 | 14.91781997680664 | 16.350491841634117 | -1.4326718648274763 | FAIL |
| 0.0075 | 59 | 50 | -2.1931121349334717 | -2.3793806632359824 | 0.18626852830251073 | FAIL |
| 0.0075 | 50 | 59 | -2.1931087970733643 | -2.3048559824625654 | 0.11174718538920114 | FAIL |
| 0.0075 | 59 | 59 | 5.674581050872803 | 5.865579346815745 | -0.1909982959429426 | FAIL |
| 0.00375 | 50 | 50 | 14.91781997680664 | 15.48449198404948 | -0.5666720072428397 | FAIL |
| 0.00375 | 59 | 50 | -2.1931121349334717 | -2.2912781685590744 | 0.09816603362560272 | FAIL |
| 0.00375 | 50 | 59 | -2.1931087970733643 | -2.2569974263509116 | 0.06388862927754735 | FAIL |
| 0.00375 | 59 | 59 | 5.674581050872803 | 5.770436426003775 | -0.09585537513097186 | FAIL |

The smallest absolute AD-minus-FD discrepancy is0.06388862927754735 and the largest is1.770892461140953 eV/Angstrom^2. Every selected entry at every sampled step exceeds0.005. The smallest-step discrepancies are smaller for these four entries than at the larger steps, but this does not establish convergence, a limiting value or a cause. No additional step sizes were tested.

## Meaning, failures and limits

This result supplies an internally reciprocal native local block while the previously saved finite differences disagree. It narrows the discrepancy toward finite-step/numerical behavior relative to the native derivative at this reference point. It does not distinguish all mechanisms, prove smoothness between sampled points, establish global integrability or show that native AD is physically correct. Reference graph stability excludes the candidate's observed connectivity change as a sufficient explanation of this reference discrepancy; it does not exclude changes in continuous graph features.

Original replay tolerances remain energy1e-5 eV, forces1e-6 eV/Angstrom and stress1e-7 eV/Angstrom^3 at rtol0. Historical original force/stress failures, D1 missing capture, failed C1 gate, unrun C2, G1 failed local/translation criteria, original entrypoint/cache failure and presentation-utility failure remain unchanged. N1 has not cleared full Gamma convergence or migration. No DFT, candidate expansion, relaxation, stability, synthesis, novelty or application-performance evidence was produced.

The calculation log retains Matplotlib/Fontconfig cache warnings. No numerical exception was recorded in this invocation. Preparation draft guard defects, metadata fixtures, independent source review and the status-only envelope review are retained. The independent status delta passed40 checks and did not claim the earlier source review attested the later envelope hash. Real derivative support was exercised in this one invocation only; no broader backend claim follows.

## Evidence and next boundary

Raw manifest coverage is26 files plus its manifest. Complete raw input/graph/neighbor arrays, six outputs, ASE observations, runtime/parameter/source hashes, native pre-normalization snapshot, both full rows, all signed comparisons and before-call counters are preserved. Private execution records retain tokens, release, ownership and process metadata. This is not a sanitized public export and no publication occurred. Original source snapshots and license records remain retained.

The investigation authorizes no further numerical work. The next decision belongs to parent review of this exact report, the independent saved-evidence review and raw hashes. Any subsequent question needs a separately frozen bounded protocol; this report does not choose new step sizes or authorize a full Hessian, DFT or another repeat. Scientific order remains diagnosis, candidate DFT/competing phases, then application-specific properties. An eventual candidate dossier must name intended use, actual property with units, baseline/conditions/convergence, uncertainty and a supported recommendation or rejection; these local derivatives do not establish dielectric, thermal or mechanical application performance.
