# Native-derivative redesign: no causal contrast admitted

This design-only stage recommends no new model calculation. The reviewed publication is complete at `fd650fa09d255de78ae412f9421096854bb80a2d`. This proposal does not change its evidence or release another experiment.

## Question and saved reference

Can one minimal additional native derivative observation distinguish finite-step truncation or continuous-feature curvature variation from input rounding or internal derivative arithmetic in the reference coordinate-50 discrepancy?

The saved N1 native entry A[50,50] is 14.91781997680664 eV/Angstrom^2. The saved G1 central difference at h=0.00375 Angstrom exceeds it by 0.5666720072428397 eV/Angstrom^2. N1 exact baseline replay passed; all twelve selected native-versus-finite-difference comparisons failed the unchanged 0.005 eV/Angstrom^2 criterion. Native reciprocity passed only for the selected block. Those facts concern the recorded computation, not physical accuracy.

The exact-rational geometric audit found no cutoff crossing or tangency over the ideal reference coordinate-50 interval [-3/800,+3/800] Angstrom in its complete periodic-pair enclosure. It did not certify the native compiled neighbor backend, rounded Cartesian formation, branch behavior or force smoothness. It therefore removes an ideal geometric cutoff-crossing explanation within that interval, not all graph or numerical explanations.

## Competing explanations and identifiability

Finite-step truncation or continuous-feature variation could make a secant derivative differ from a local derivative even with stable ideal topology. Internal float32 arithmetic, input quantization or numerical AD behavior could also produce the discrepancy. Native graph construction and ordering remain incompletely certified. These mechanisms can coexist.

Saved output-storage rounding bounds are much smaller than the observed discrepancy, rejecting final force storage rounding alone under their stated rounding assumption. They do not bound internal arithmetic. Smallest-step improvement and the local linear position projection do not identify a cause. The stopped precision contrast remains stopped: uniform derivative/remainder, baseline-transport and arithmetic-error certificates are missing.

## Smallest prospective screen considered, and why it is not recommended now

A positive-endpoint native row-50 query could compare A[50,50] with saved N1. Only after exact matching against that saved G1 endpoint's input, graph, neighbor, six output tensors, ASE observables, parameters and runtime would an added derivative query be permitted. A difference of at least 0.05 eV/Angstrom^2 would answer the narrow existential question that at least one endpoint's native output differs materially from baseline. Otherwise the negative endpoint would be needed. This would require at most two forwards and two added row queries, positive first, with no new baseline repeat.

The 0.05 value would be a declared effect-size screen, not an error certificate or a replacement for 0.005 acceptance. A YES would prohibit treating baseline as a constant surrogate for every sampled endpoint output. A NO after both endpoints would close only this endpoint screen; it could not establish interior constancy. Neither result distinguishes exact-curvature variation from input or AD arithmetic. No current downstream decision requires the constant endpoint-output surrogate. Consequently this screen is not admitted as the next causal experiment, and its proposed counters are not a release.

## Exact launch-path limitation

There is no executable launch path for this redesign. The consumed N1 launcher must not be invoked. Its saved NativeCapture.query_rows implementation is bound to rows 50 and 59 and its own counters/context; it is not an endpoint single-row launcher. A future implementation would require a new reviewed one-attempt controller, one row-50 query per endpoint, endpoint-specific exact gates and a deterministic stop decision. Merely changing an input or assigning a new identifier would not satisfy those requirements.

Source inspection confirms that installed CHGNet BatchedGraph.from_graphs forms atom_cart_coords as graph.atom_frac_coord @ lattice; the stress path also forms lattice through graph.lattice @ (identity + strain). Saved G1 graphs are not captures of those actual displaced Cartesian tensors. Recomputing ideal rational products does not recover their floating-point execution. Calling all of BatchedGraph.from_graphs is not a bare matrix-product audit: it also invokes bond-basis expansion. No such call was made here.

## Next gate and bounds

Before a model experiment can be recommended, a separately authorized, source-only preparation must specify either an independently defensible backend/derivative reference or an isolated intervention with a bounded confounder and an outcome that changes a causal conclusion. Actual native Cartesian-position capture could close a missing-input observation, but alone cannot certify nonlinear force contamination and is not proposed here as a cure. No executable adapter or certificate currently meets this gate.

The next admissible action is parent review of this no-computation conclusion. Any subsequent feasibility work should have a new prospective cap of at most 600 seconds all roles, zero model forwards, zero AD queries and zero scientific-token claims, and stop when the required reference or confounder bound cannot be established. That work is not released by this proposal. A numerical compute allowance is presently zero; no future inference budget is reserved.

Stop on stale usage or ownership uncertainty, missing source/input identity, an unsupported certificate, a request to reuse a consumed anchor, or a deadline. No fallback backend, tolerance widening, hidden retry, installation or publication is allowed. Original replay thresholds remain energy 1e-5 eV, forces 1e-6 eV/Angstrom and stress 1e-7 eV/Angstrom^3, all rtol=0. Original replay failure, failed C1 gate, unrun C2, G1/N1 consumed attempts, precision STOP and prior timing failures remain unchanged. Migration and physical/application acceptance remain incomplete; the non-overlapping fallback remains.

## Evidence and stage boundary

The evidence base is the published G1 package and published n1-precision-geometric-checkpoint-20261025 package at the commit above, supplemented only by reading preserved source. No model was constructed, no forward/AD query or scientific token was issued, and no scientific data were recomputed. This is an eight-minute design stage including review and checkpoint. Requested configuration is Astra High, Standard; the observable assistant is GPT-6-based Codex, with variant, effort and speed not independently attested.
