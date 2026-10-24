# G1 post-repair execution result

All 32 frozen single points completed with captured inputs, consumed neighbors, graph arrays, six model-output tensors per point and ASE observations. The sole authorized post-repair controller exited 0. This is successful bounded execution and capture, not numerical quality acceptance: both materials fail the frozen local quality criteria. Original replay acceptance and migration remain failed/incomplete.

## Execution and scope

The original investigation start remains 2026-10-24 09:17:46 UTC and hard deadline 09:47:46 UTC. The post-repair controller ran from 09:38:55.376777 to 09:43:17.520105 UTC, measured wall time 262.143162186 seconds. Aggregate calculation-process time was 222.064280851 seconds against the 600-second cap. Controller finalization recorded investigation elapsed time 1,531.445918 seconds against the unchanged 1,800-second cap. Reporting and review continued within the same deadline; their completion timestamp is retained separately.

There were two scientifically released controller invocations in total: the original entrypoint failure with zero evaluations, and this separately authorized post-repair invocation. Eight prior metadata-only launcher probes are recorded separately. The same G1 protocol ID and fixed anchor were retained. One scientific protocol anchor, 32 point-launch tokens and 32 forward tokens now exist. They are consumed evidence, not reusable permission. No numerical retry or replacement point occurred.

The final execution envelope SHA256 is 4585e7755f8a138358d709b2119cb8c0486ab776753e271c0f2b416739d9ea1a. It changes only the permitted status/review envelope; the preparation envelope remains preserved. The repair reviewer did not attest this later hash before execution. Post-launch independent envelope inspection passed 8/8 checks. Protocol SHA256 remains 7998bd0674d03c7ed8ebc45062578c78982fac73b6898b7b831a8a803f2e1382 and implementation-manifest SHA256 remains 0feee37484be73feb72e20d5844cfe9542a0c0f4da499e9bd723f679754da3b4. Scientific source, inputs, model, runtime constraints, points and tolerances were unchanged.

## Observed diagnostic results

All Hessian-column quantities below have units eV/Angstrom^2. The frozen selected-column resolution criterion is 0.005; it does not replace the original replay tolerances.

| Metric | R-CaTiO3 | C03-005 |
|---|---:|---:|
| Pair asymmetry, h=0.015 Angstrom | -0.076570113500 | -0.571491693457 |
| Pair asymmetry, h=0.0075 Angstrom | +0.074524680773 | -0.565100957950 |
| Pair asymmetry, h=0.00375 Angstrom | +0.034280742208 | -0.284852832556 |
| Maximum fine-step column difference | 0.865999857585 | 1.351086298625 |
| Maximum coarse-step column difference | 0.613278150558 | 0.902899106344 |
| All sampled ordered graph topology unchanged | Yes | No |
| Same-endpoint six-tensor exact repeat | Pass | Pass |
| Native rigid-translation criteria | Fail | Fail |
| Selected local quality criteria | Fail | Fail |

Full-precision signed columns, step differences, translations, exact-repeat differences, historical C03-005 comparisons, graph comparisons and float32 output-ULP proxies are retained in raw/signed-comparisons.json. The ULP proxy is a representation scale, not a bound on algorithmic error or internal cancellation. No absent or empty comparison was assigned zero.

The reference's failed criteria despite unchanged sampled graph topology show that observed graph/order changes alone do not account for all uncertainty in this experiment. C03-005 additionally has graph/order changes, which preclude a smooth sampled-derivative claim for this selection. Exact repeats demonstrate reproducibility of these particular outputs; they do not establish physical accuracy. Neither sequence meets the declared fine-step criterion. These observations do not identify the historical host's cause, establish full Gamma convergence or phonon stability, or validate an application.

## Independent review and preserved failures

Independent saved-data verification passed 26,073/26,073 checks, covering 898 root-manifest members, 768 arrays with 839,250 elements, and 2,750 recomputed signed components. The independent terminal review is retained separately. The frozen raw final-decision remains unchanged with execution_eligible=false and a pending-independent-review status; the later review is additive evidence, not a retrospective edit or automatic scientific pass.

An optional presentation-summary utility failed after terminal completion because it assumed a flat stress list while saved stress differences are matrices. Its TypeError, original script and failure record are preserved; it was not repaired or rerun. No frozen calculation, analysis, raw output or independent arithmetic result was changed. The incomplete supplemental presentation summary is not treated as a scientific measurement.

All original force/stress replay failures remain at energy 1e-5 eV, force 1e-6 eV/Angstrom and stress 1e-7 eV/Angstrom^3, rtol 0. Historical D1 missing captures, failed C1 gate, unrun C2, P1's limited pairwise repeatability and reviewer clarifications remain preserved. The original failed G1 entrypoint/cache, launcher-test placeholder and its correction also remain preserved.

This private evidence bundle contains account/release/process metadata and is not a sanitized publication package. No GitHub write, new scientific design, DFT, relaxation, package installation, schedule change or fallback retirement occurred. The parent owns the next design; this run does not self-renew. Requested Astra High and Standard speed are not independently attested serving configuration.
