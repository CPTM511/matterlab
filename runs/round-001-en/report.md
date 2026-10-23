# MatterLab materials exploration: round-001-en

Started: 2026-10-24T01:27:02.182678+08:00.

These are actual local CHGNet 0.3.0 interatomic-potential calculations. They are not DFT, experimental synthesis, or proof of global novelty.

Enumerated 432 raw decorations, retaining 27 parent-symmetry representatives. Attempted 6 candidates and 9 endmember references.

## Computed results

| Candidate | Cell composition | Energy-screen status | Density g/cm3 | Restricted decomposition meV/atom | Fixed-shape compression response GPa | Gamma minimum curvature eV/A2 | Gamma assessment |
|---|---|---|---:|---:|---:|---:|---|
| [C01-007](C01-007/result.json) | Ca2SrBaTi2ZrSnO12 | above_restricted_reference | 5.0865 | 30.4262 | Not calculated | Not calculated | Not calculated |
| [C01-009](C01-009/result.json) | Ca2SrBaTi2ZrSnO12 | above_restricted_reference | 5.0597 | 19.1332 | Not calculated | Not calculated | Not calculated |
| [C02-002](C02-002/result.json) | CaSr2BaTiZr2SnO12 | above_restricted_reference | 5.4050 | 15.3608 | Not calculated | Not calculated | Not calculated |
| [C02-009](C02-009/result.json) | CaSr2BaTiZr2SnO12 | above_restricted_reference | 5.3883 | 10.4643 | 132.2693 | 0.1514 | inconclusive_near_zero_or_numerically_sensitive |
| [C03-005](C03-005/result.json) | CaSrBa2TiZrSn2O12 | ml_screened | 5.8142 | 9.0260 | 128.3723 | 0.2728 | inconclusive_near_zero_or_numerically_sensitive |
| [C03-008](C03-008/result.json) | CaSrBa2TiZrSn2O12 | above_restricted_reference | 5.7835 | 15.3561 | Not calculated | Not calculated | Not calculated |

A positive decomposition energy means a lower-energy mixture exists among the selected endmembers in this model. A negative value only improves on this limited reference set; it does not establish full phase-diagram stability. The configured energy-screen threshold is a research triage rule, not a model-accuracy or stability guarantee.

Positive Gamma eigenvalues alone are insufficient: the assessment also considers displacement-step sensitivity, Hessian asymmetry, and translation residuals. An inconclusive result is not a pass. This local diagnostic does not replace full phonon dispersion.

## Potential applications

1. **Dielectric-ceramic research for capacitors and electronic packaging.** Related Ca/Sr/Ba-Ti/Zr/Sn oxides have published precedents. This round supplies structures and limited compression response; permittivity, dielectric loss, insulation, breakdown, temperature response, and manufacturability remain unverified.
2. **Ceramic-composite filler research.** Structures and densities can inform subsequent composite models. Interface bonding, thermal conductivity, thermal expansion, toughness, fatigue, processing, and lifetime require separate evaluation.
3. **Open computational benchmarks.** The structures, raw observations, negative results, and uncertainty records can already be used to evaluate generation algorithms, compare interatomic potentials, or study decomposition hypotheses.

Related-family precedent: https://doi.org/10.1016/j.ceramint.2023.11.388 . This precedent also limits novelty claims.

## Reproducibility

- config.json records generation and calculation parameters.
- generated/generation.json records enumeration, symmetry, seeds, and selection; corresponding CIF files preserve every representative input.
- Candidate directories contain structures, FIRE logs and trajectories, raw energy/force/stress observations, and EOS/Gamma data where actually calculated.
- provenance.json, requirements-lock.txt, and source_snapshot/ record the environment, checkpoint hashes, and exact run source.
- manifest.json records SHA256 hashes; verification.json checks integrity and recomputes aggregate metrics from observations.

Use the README commands to rerun in a new output directory. Same-platform numerical replay is tested separately where reported. Timestamps and cross-platform floating-point behavior are not guaranteed to match byte-for-byte.

## Limitations

- CHGNet ML interatomic-potential screening; these results are neither DFT nor experimental synthesis.
- The material family has experimental precedents; novelty of the exact compositions and orderings is unverified.
- Limited initial structures and reference phases cannot establish the global minimum or full phase-diagram stability.
- Volume scans measure fixed-shape compression response, not strength, hardness, toughness, or full elastic stability.
- Gamma curvatures probe local displacements in the chosen periodic cell, not the full phonon dispersion.
- Applications are research hypotheses; dielectric, thermal, breakdown, processing, and lifetime performance remain unverified.
