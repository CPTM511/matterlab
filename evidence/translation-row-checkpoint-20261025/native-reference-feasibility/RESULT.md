# Source-only feasibility: a saved-row translation constraint

Outcome: a narrow independent analytic constraint is feasible for future saved-data analysis, with zero new model evaluations. No analysis or execution is released here. There is still no independently certified value for the selected curvature entries and no established cause of the G1/N1 discrepancy. The first STOP draft is preserved; independent challenge identified the additional constraint before this stage ended.

## Question and admission rule

Before inspection, the question was fixed: can preserved source establish a scalar-coordinate-unit convention mismatch between the N1 native derivative and G1 finite differences, or an independent derivative/backend reference? Admission required a source-backed discrepancy with an isolated correction, or a reference with justified comparable semantics. The narrower admitted reference is a necessary translation identity, not a full derivative oracle. The rejected endpoint screen and stopped float64 contrast remain closed.

## Source findings

CHGNet computes force as -grad(energy.sum(), g.atom_positions) before intensive energy normalization. The composition shift depends on species counts, not positions at fixed composition. ASE multiplies model forces by one; the atom-count and GPa factors apply to energy and stress. N1 returns -dF_j/dx_k. G1 forms column k as -(F_plus-F_minus)/(2h), and N1 compares row j, element k with column k, element j. No sign, force-unit, atom-count or index mismatch was found. This is source inspection, not a new compiled-runtime certification.

G1's raw Cartesian displacement passes through fractional conversion, float32 casts and native Cartesian reconstruction. N1 differentiates the Cartesian intermediate at fixed lattice/image branches. This distinction remains an unbounded confounder; it is not an identified cause. Actual displaced G1 Cartesian intermediates were not captured. Rational products cannot replace those native observations.

In the inspected model path, positions enter the energy through center-minus-neighbor periodic bond vectors; downstream bond/angle features and message passing use those relative quantities. At fixed lattice and graph, a real-arithmetic scalar with these dependencies is invariant under a common Cartesian translation. Wherever its force derivatives exist, each Hessian row therefore obeys sum over atoms of H[j,3*a+alpha] = 0 for alpha=x,y,z. This zero reference is analytic and independent of a finite-displacement step. The proof does not certify native rounding, differentiability at every branch, or backend behavior.

## One prospective saved-data check

Use only the two complete saved N1 rows j=50 and j=59, each containing 60 float32 values. For each row and each Cartesian axis, form one exact rational sum over its 20 corresponding atom components: six checks total. Do not execute a forward, AD query, finite-difference sweep or graph reconstruction.

For every saved finite float32 value, construct a conservative closed rounding cell from the exact midpoints to its immediately adjacent representable values. Decode IEEE-754 bits and use exact integers/rationals throughout. Handle negative values, signed zero, subnormals, asymmetric spacing at powers of two and ties explicitly. Stop on unsupported formats, infinities, NaNs, shape/hash mismatch or ambiguous extreme-value treatment. Do not replace the cells by a common symmetric ULP approximation.

Sum each group's lower and upper cell endpoints exactly. If zero is outside any sum interval, reject the joint hypothesis that these components are all correctly rounded values of a smooth translation-invariant scalar's exact Hessian row in the stated coordinate convention. A finite-step truncation error cannot itself produce this signature because the test uses no finite differences. The conclusion is error beyond one final correct rounding OR a failed smoothness, translation or coordinate premise. Ordinary accumulated native arithmetic is possible; an AD implementation bug is not established.

If every interval contains zero, the result is inconclusive: six necessary conditions do not certify the individual derivatives, interior smoothness or force convergence. Both outcomes leave the original FD discrepancy unresolved unless additional evidence supports attribution. No row sums or intervals were calculated in this stage.

Retain the six signed sums, exact rational interval endpoints and distance from each interval to zero. If that distance is d>0, at least one of the 20 components must lie at distance at least d/20 from its reported rounding cell under the stated exact-row premise. Report this bound and its relation to 0.005 eV/Angstrom^2 only as an effect-size diagnostic; it does not identify which component or alter any acceptance gate. All quantities have units eV/Angstrom^2.

## Inputs, preparation gate and bounds

Pinned original N1 files: native-row-50.npz SHA256 9f266858e0d1c5c1164241a8425099ebec0c9c8305f7ea5803cb0f9c4369e328; native-row-59.npz SHA256 fe30ec0c926385cd412cdd39bb5e316e5445398046c68e342de842b1c910854f. No new model or material input is proposed.

Concrete restart trigger: parent acceptance followed by an independently reviewed exact-rational implementation with negative fixtures for rounding-cell boundaries, signed zero, subnormals, powers of two, invalid formats, incomplete rows and intentional identity violations. The review must confirm all six checks, conservative premise handling and no float leakage. No implementation currently exists for this check and no old launcher or anchor may be used.

A future combined preparation/review/saved-analysis stage should be capped prospectively at 600 seconds all roles, with one analysis invocation, at most 120 parsed components and six interval sums, and at most 60 seconds for the analysis process. Zero model constructions, forwards, AD queries and scientific-token claims. Stop on any failed fixture, integrity/premise ambiguity, exception, stale gate or deadline; no automatic retry or scope expansion. These are proposed bounds, not an execution release.

## Evidence and unchanged limits

All 18 N1 implementation-manifest entries matched. source-receipt.json records nine inspected source identities; the independent review retains its additional inspection identities. The verified publication checkout was clean. Two initial path lookups failed and were retained; the correct files were then read. No source was imported or executed, no scientific arithmetic was performed, and no installation or public write occurred. Only source reading, hashing and private reports were performed.

Original replay thresholds remain energy 1e-5 eV, forces 1e-6 eV/Angstrom and stress 1e-7 eV/Angstrom^3, rtol=0; local curvature acceptance remains 0.005 eV/Angstrom^2. Original failures, failed C1 gate, unrun C2, consumed G1/N1 attempts, precision STOP, earlier timing failures and retained fallback remain unchanged. This is not physical accuracy, migration, stability or application evidence.

Requested configuration is Astra High, Standard speed. Observable identity is GPT-6-based Codex; actual serving variant, effort and speed are not independently attested. This source-only stage has a fixed 600-second all-role deadline; exact start and terminal timing are recorded separately without extending any prior stage.
