# Source-only derivative-reference feasibility

Outcome: STOP before implementation or numerical execution. The inspected source supplies no concrete sign, force-unit, atom-count or row/column convention mismatch that explains the saved discrepancy. It also supplies no already validated independent derivative reference or bounded-confounder intervention. This is a bounded information gap, not a claim that an independent reference is impossible in principle.

## Frozen question and admission rule

Before inspection, the question was fixed: can preserved source establish a scalar-coordinate-unit convention mismatch between the N1 native derivative and G1 force finite differences, or an independent derivative/backend reference? Admission required a concrete source-backed discrepancy with an isolated correction, or a reference with justified comparable semantics. Otherwise the stage must stop and identify missing evidence. The endpoint-output screen and stopped float64 contrast were not reopened.

## What the source establishes

CHGNet model.py computes force as minus the gradient of energy.sum() with respect to g.atom_positions, before dividing intensive energy by atoms_per_graph. Its composition-energy addition occurs after _compute; AtomRef depends on species counts, not coordinates at fixed composition. Thus the difference between the captured pre-normalization scalar and ASE total energy is not by itself evidence of an erroneous force factor.

The ASE adapter maps model forces with factor 1. It applies the atom-count factor to energy and the GPa conversion to stress, not forces. N1 preserves the original native gradient call and captures its scalar and Cartesian inputs. Its additional query returns minus dF_j/dx_k. G1 forms column k as minus (F_plus-F_minus)/(2h); N1 compare_saved.py compares native row j, element k with that column's element j. The sign, row/column pairing and eV/Angstrom^2 units therefore agree at source level. The worker also contains exact model-force/ASE-force equality checks. No new runtime validation was performed here, so this is not a proof of all compiled behavior.

The remaining coordinate distinction is real but not a demonstrated cause. G1 displaces ASE Cartesian inputs, passes through structure fractional coordinates, float32 graph arrays and Cartesian reconstruction. N1 differentiates the native Cartesian intermediate with the selected image/lattice branches held in that graph. Installed source forms that intermediate as atom_frac_coord @ lattice; the stress path also constructs lattice through lattice @ (identity + strain). The saved displaced G1 graphs do not contain captures of those actual native Cartesian intermediates. An ideal rational matrix product cannot substitute for a captured floating-point result.

Bond encoding uses native norms, normalized vectors, periodic-image lattice products, regularized acos and polynomial cutoffs selected by torch.where. No specific wrong derivative rule was established. The exact geometric enclosure remains about the ideal Cartesian path; it does not certify those numerical operations or compiled neighbor semantics. A second differentiation wrapper around the same PyTorch graph would share the backend and be a consistency test, not an independently certified reference.

## What remains missing, and the restart trigger

There is no preserved end-to-end independent derivative implementation with matched parameter values, operator conventions, coordinate inputs and an adequate error budget. There is also no captured displaced native-coordinate/activation trace establishing the effective path, nor a uniform derivative/remainder and arithmetic-error certificate bounding transport from that path to the intended one below the unchanged 0.005 eV/Angstrom^2 criterion. Local projection and stable ideal topology do not supply those bounds.

Restart this route only when a concrete new item is available for review: either (1) a specified operator or conversion with a demonstrable source-level inconsistency and a matched independent identity/reference, plus a way to bound confounders at the selected curvature entry; or (2) a versioned independent derivative implementation and comparison/error budget covering the same scalar and effective coordinates. Native intermediate captures would help establish input equivalence but alone would not satisfy either trigger. None of these items was produced or found in this stage.

If obtaining a missing trace requires a new forward, that needs its own identifiable question, frozen capture protocol, independent review and parent release. It is not authorized by this STOP, and no consumed G1 or N1 launch path may be reused. There is no executable next experiment or reserved inference allowance. Source availability is not evidence of an implemented or validated reference.

## Evidence, limits and preservation

All 18 N1 implementation-manifest entries matched their recorded hashes. source-receipt.json records byte counts and SHA256 for the nine inspected source files. model.py remains 767b120ba8b3ee7f75c247416902d1b72e871ba8ffc2916ed76d24809c98fc96; native_capture.py remains 941e18f30469629c161b105818fc7b86175d1db481aa52a46f9e38aed60668db; compare_saved.py remains b03cb466823ba972edb1e4e86faff961bde2293bb0e949ee867943d65d4340c3. The verified publication checkout was clean. Two initial path lookups failed; the correct saved paths were subsequently read, and those lookup errors are retained in the receipt.

No model or torch import, forward, AD query, scientific-token claim, new scientific arithmetic, installation or public write occurred. Only text inspection, file hashing and private reports were performed. Original replay tolerances remain 1e-5 eV, 1e-6 eV/Angstrom and 1e-7 eV/Angstrom^3 with rtol=0. The 0.005 local curvature criterion, original failures, failed C1 gate, unrun C2, G1/N1 consumed attempts, precision STOP and prior timing failures remain unchanged. This does not establish physical accuracy, force convergence, migration or application properties; fallback remains retained.

Requested configuration: Astra High, Standard speed. Observable assistant identity: GPT-6-based Codex; serving variant, reasoning setting and speed are not independently attested. This separately admitted source-only stage has a fixed 600-second all-role cap. Exact start, deadline and terminal checkpoint are retained separately; no earlier clock is extended.
