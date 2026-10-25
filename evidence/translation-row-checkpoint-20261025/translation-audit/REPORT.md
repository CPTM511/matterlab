# Exact saved-row translation audit

One saved-data analysis completed successfully. Exactly one of six conservative rounding-cell sum intervals excludes zero: native row 59, x translation. The other five are inconclusive. This rejects the joint final-correct-rounding and exact smooth translation-invariant row premises for that group. It does not identify an AD bug or explain the original finite-difference discrepancy.

## Scope and execution

Only the two pinned N1 float32 rows were parsed: rows 50 and 59, 60 components each. Each row was partitioned into three Cartesian translation groups of 20 atoms. One analysis invocation processed 120 components and six exact rational sums. There was no model construction, torch import, forward, AD query, graph reconstruction, scientific-token claim, installation or public write. G1/N1 scientific anchors remain consumed and untouched.

The stage began 2026-10-25 at 10:30:44.961213 UTC, with an immutable deadline of 10:40:44.961213 UTC. Independent pre-execution PASS was recorded at 10:35:16.922189 UTC. The sole launched analysis ran from 10:35:36.695377 to 10:35:36.759896 UTC, exit code 0; measured elapsed time was 0.06450216099983663 seconds against the 60-second cap. No analysis retry occurred. Terminal review and final checkpoint are recorded separately within the same stage.

## Complete six-group results

All entries below are exact rational numbers in eV/Angstrom^2. Interval endpoints are closed and conservative. Inclusion is not a correctness pass.

| Row | Axis | Signed sum | Sum interval [lower, upper] | Zero included | Conditional component-distance lower bound |
|---|---|---|---|---|---|
| 50 | x | -59/1073741824 | [-631/2147483648, 395/2147483648] | yes | 0 |
| 50 | y | 47/134217728 | [-5/1073741824, 757/1073741824] | yes | 0 |
| 50 | z | -37/33554432 | [-53/16777216, 1/1048576] | yes | 0 |
| 59 | x | 23/67108864 | [115/2147483648, 1357/2147483648] | no | 23/8589934592 |
| 59 | y | -3/134217728 | [-4673/17179869184, 3905/17179869184] | yes | 0 |
| 59 | z | 11/67108864 | [-213/268435456, 301/268435456] | yes | 0 |

For row 59/x, distance from the sum interval to zero is exactly 115/2147483648. Dividing by 20 yields the reported conditional lower bound 23/8589934592 for at least one component's distance from its reported rounding cell. This bound is below 0.005. It is a lower bound, not an upper bound on actual error; it does not show the actual error is small, locate the component or measure its contribution to the original FD gap.

The analytic reference is translation invariance of the fixed-lattice, fixed-graph real scalar wherever the required derivatives exist. Interval exclusion means error beyond one final correct rounding OR a failed smoothness, translation or coordinate premise. Ordinary accumulated arithmetic remains possible. Finite-step truncation is absent from this check, but it can still contribute to the separate G1/N1 discrepancy. No full derivative oracle or backend certificate has been established.

## Integrity, review and retained failures

Input SHA256 values matched the accepted originals: row 50, 9f266858e0d1c5c1164241a8425099ebec0c9c8305f7ea5803cb0f9c4369e328; row 59, fe30ec0c926385cd412cdd39bb5e316e5445398046c68e342de842b1c910854f. The parser required exact little-endian binary32, shape (60,), C-order and bounded NPZ/NPY contents. Exact binary decoding and rational arithmetic supplied all scientific decisions; signed zero, subnormals, unequal spacing and closed midpoint ties were handled explicitly.

Independent pre-execution review passed 74 synthetic checks: 32 supplied, 29 independent arithmetic/parser/pipeline checks and 13 mocked launcher checks. Three earlier findings were repaired before approval: missing immutable-stage digest binding, terminal resource limits not conditioning success, and acceptance of a non-integer shape dimension. Original code versions and findings are retained. The reviewed launcher enforces source/stage hashes, one exclusive saved-analysis invocation, resource limits and no retry. The exclusive invocation record is consumed.

raw/classifications.jsonl retains all 120 bit patterns and rounding cells, all six sums, interval endpoints, distances, bounds and classifications. raw/input-identities.json and raw/manifest.json bind the inputs and outputs; process-receipt.json and reviewer records retain execution and review evidence. No terminal analysis exception was recorded. This stage did not repeat or replace earlier publication audits.

## Unchanged acceptance and next boundary

Original replay tolerances remain 1e-5 eV, 1e-6 eV/Angstrom and 1e-7 eV/Angstrom^3 with rtol=0. Local curvature acceptance remains 0.005 eV/Angstrom^2. All original failures, failed C1 gate, unrun C2, consumed G1/N1 attempts, precision STOP and previous timing failures remain unchanged. Migration, physical accuracy, stability and application performance are not established; the fallback remains retained.

The result modestly narrows the final-rounding-only joint hypothesis for one native row sum. It supplies no released next computation. Any further design must explain how it would distinguish the remaining causes rather than repeat this consumed audit. No publication is authorized in this stage.

Requested configuration was Astra High, Standard speed. Observable assistant identity is GPT-6-based Codex; actual serving variant, effort and speed are not independently attested.
