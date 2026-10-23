# First-round results and potential research uses

2026-10-24. The platform has executed real local calculations and produced reproducible computational candidates. It has not established a globally novel, synthesizable material that meets product requirements.

The numerical results below belong to the completed English campaign `round-001-en`. Its [verification record](../runs/round-001-en/verification.json) passes 301 integrity and recomputation checks. A [fresh independent reproduction of C03-005](../runs/reproduction-round-001-en-C03-005/reproduction.json) also passes. Neither result establishes physical accuracy, stability or novelty. The original Chinese historical results remain unchanged in the private research workspace and are not included in this English public release.

## Completed calculations

The generator enumerated 432 site decorations and reduced them to 27 initial structures using parent-lattice symmetry. A fixed seed selected six candidates, which were calculated alongside nine endmember controls with the same CHGNet 0.3.0 potential. All 15 structures met the recorded atomic-force and stress convergence conditions. Two candidates near the top of the energy screen received further refinement, 14 energy-volume points in total, and Gamma-curvature diagnostics at two displacement sizes, requiring 480 displaced-force calculations.

The English campaign ran from 01:27:02 to 01:30:26, Asia/Shanghai, on 2026-10-24. Its recorded verification completed at 01:32:06. The campaign interval excludes installation, development, testing, the independent reproduction and quantum calculations. It used a local CPU, with no rented compute or paid API calls.

| Candidate | Composition of the 20-atom cell | Density, g/cm³ | Energy relative to restricted endmember mixture, meV/atom | Fixed-shape volume response, GPa | Assessment |
| --- | --- | ---: | ---: | ---: | --- |
| C03-005 | CaSrBa₂TiZrSn₂O₁₂ | 5.814 | +9.03 | 128.4 | Prioritized for further investigation; stability unconfirmed |
| C02-009 | CaSr₂BaTiZr₂SnO₁₂ | 5.388 | +10.46 | 132.3 | Slightly above the exploratory energy threshold; retained as a comparison |
| C01-009 | Ca₂SrBaTi₂ZrSnO₁₂ | 5.060 | +19.13 | Not calculated | Lower priority; no detailed property evidence |

The other selected ordering of each composition is also retained in the [run data](../runs/round-001-en/summary.json) and [full English report](../runs/round-001-en/report.md). Different arrangements at the same composition have different calculated energies. A [comparison with the historical campaign](../runs/round-001-en/english-replay-comparison.json) found no numerical differences across 136 checks using the same settings, model and platform.

The +9.03 meV/atom value is positive: the selected endmember set contains a lower-energy mixture under the same model. The 10 meV/atom cutoff was an exploratory screening threshold, **not a stability criterion or a guarantee of model accuracy**. It excludes other competing phases, finite-temperature entropy and synthesis kinetics, and must not be interpreted as a complete energy-above-hull result.

## What the calculations do not yet establish

Both equation-of-state fits have R² values of approximately 0.999996. Reducing the seven-point window to its middle five points changes the fitted volume response by approximately 0.18% for C03-005 and 0.25% for C02-009. This supports the numerical fit under the chosen potential and fixed-shape constraint. It does not imply that the error relative to a real material is that small, or establish strength, hardness or toughness.

Both candidates have positive minimum Gamma curvatures. However, the maximum Hessian asymmetry residuals are approximately 0.57 and 0.71 eV/Å², respectively, exceeding their minimum curvatures. Under the recorded assessment rules, **both stability diagnostics are inconclusive**; neither counts as a stability pass. Raw force arrays for both displacement sizes, Hessians, translational residuals and diagnostic scales are preserved. Symmetrization was not used to suppress the residuals or turn an inconclusive calculation into a pass.

The independent Quantum ESPRESSO calculations concern the known CaTiO₃ control and establish that a real local DFT workflow can execute. They do not validate the new candidates with DFT. Parameter sensitivity and failed attempts are retained in the [quantum validation report](quantum-validation.en.md).

## Potential research uses

| Direction | Industry context and research objective | Current evidence | Evidence still needed before a product claim |
| --- | --- | --- | --- |
| Dielectric ceramics | Dielectric layers or ceramic components for electronic devices, capacitors and packaging | Related multicomponent oxide families have published precedents; this run supplies explicit structures, density and a constrained volume response | Candidate-specific permittivity, loss, insulation resistance, breakdown field, temperature response, fuller phase stability and manufacturability |
| Ceramic composite fillers | Filler exploration for electronic-packaging resins and functional composites | Structures, density and limited mechanical response can inform later models | Interface compatibility, dispersion, thermal conductivity, expansion, fatigue, processing and lifetime; improved heat transport or toughening was not demonstrated |
| Open computational samples | Materials informatics, potential assessment and structure-generation research | Downloadable input structures, calculated forces/stresses/energies, failures and uncertainty records | This use is available now; it does not require a claim that the materials can be manufactured |

C03-005 is the first candidate for further investigation, with normalized composition (Ca₀.₂₅Sr₀.₂₅Ba₀.₅)(Ti₀.₂₅Zr₀.₂₅Sn₀.₅)O₃. Its priority follows only from the restricted energy ranking in this round. It has not been shown to outperform existing products in dielectric or thermal properties.

The material family has a [published experimental precedent](https://doi.org/10.1016/j.ceramint.2023.11.388). Novelty of the exact compositions and ordered structures still requires database, literature and patent comparisons; see the [novelty ledger](NOVELTY.md). No experimental synthesis or synthesis-reaction-path calculation was performed in this round.

## Verification and reproducibility evidence

- The recorded test suite passed 22 scientific checks covering generation and deduplication, composition conservation, restricted decomposition optimization, EOS units and fitting, finite-displacement signs and Gamma assessment.
- Twelve additional release-guard tests cover changed measurements, missing required evidence, unexpected files, unsafe paths, nested-archive text, language and credential-pattern checks.
- [English campaign verification](../runs/round-001-en/verification.json) passed 301 integrity and raw-data recomputation checks without discrepancies. This is not an external certification of physical accuracy.
- [Full-campaign numerical comparison](../runs/round-001-en/english-replay-comparison.json) passed 136 checks against the historical calculation with no numerical differences detected. Repeated agreement under the same model does not establish accuracy against independent physics or experiment.
- [Fresh independent reproduction](../runs/reproduction-round-001-en-C03-005/reproduction.json) restarted coarse and fine relaxation from the original C03-005 CIF using the saved English source code and model. It compared the active refined state with the recorded refined state. Maximum differences in energy, forces, stress, cell and corresponding atomic displacement were all zero, and both fine relaxations took seven optimizer steps. This result is limited to that replay on the same local machine; this single-candidate reproduction did not repeat EOS scans, Gamma displacements, other candidates or phase-reference calculations.
- [English delivery checks](delivery-checks-en.json) verify the fresh campaign downloads and English search/comparison interface.
- The historical [delivery checks](delivery-checks.json) recorded byte-for-byte SHA256 agreement for 102 dashboard evidence downloads and their local originals. The reproducer rejected a deliberately modified input before starting a calculation.
- Browser checks exercised run loading, type filtering, identifier search, comparison of up to three entries, candidate details and structure rotation. The screenshots showed actual calculation results rather than placeholder data.

Original inputs, model checksums, dependency versions, run-specific source snapshots, optimization trajectories and raw observations are retained under `runs/`. Reproduction commands are documented in the [project README](../README.md).

## Next scientific milestone

For C03-005 and the CaTiO₃ control, first diagnose the large Gamma residual using saved force arrays and fresh force evaluations at multiple displacement sizes. Record Hessian asymmetry, translational residual, the minimum curvature and its displacement-step variation. Acceptance requires a consistent sign decision under the recorded numerical diagnostic rule, which is a screening heuristic rather than a calibrated statistical uncertainty estimate; an inconclusive result remains inconclusive. Check whether tighter relaxation, independent starting distortions or a larger cell change the structural conclusion.

Once a defensible candidate structure is identified, perform a parameter-converged candidate DFT check and extend the competing-phase references. Only then evaluate application-specific quantities, beginning with dielectric response if dielectric ceramics remain the target. Preserve each previous round and its failed checks. These are next-stage requirements, not completed results or a promise of invention.
