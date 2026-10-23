"""Evidence-grounded English reports; no language-model calls."""
import json
from pathlib import Path


def report(directory):
    directory = Path(directory)
    s = json.loads((directory / "summary.json").read_text())
    candidates = [r for r in s["candidates"] if r["kind"] == "candidate"]
    references = [r for r in s["candidates"] if r["kind"] == "reference"]
    lines = [f"# MatterLab materials exploration: {s['run_id']}", "", f"Started: {s['created_at']}.", "",
             f"These are actual local CHGNet {s['model']} interatomic-potential calculations. They are not DFT, experimental synthesis, or proof of global novelty.", "",
             f"Enumerated {sum(g['raw_decorations'] for g in s['generation'])} raw decorations, retaining "
             f"{sum(g['symmetry_unique'] for g in s['generation'])} parent-symmetry representatives. "
             f"Attempted {len(candidates)} candidates and {len(references)} endmember references.", "",
             "## Computed results", "",
             "| Candidate | Cell composition | Energy-screen status | Density g/cm3 | Restricted decomposition meV/atom | Fixed-shape compression response GPa | Gamma minimum curvature eV/A2 | Gamma assessment |",
             "|---|---|---|---:|---:|---:|---:|---|"]

    def number(value, scale=1):
        return "Not calculated" if value is None else f"{value * scale:.4f}"

    for r in candidates:
        lines.append(f"| [{r['id']}]({r['id']}/result.json) | {r['formula']} | {r['status']} | "
                     f"{number(r.get('density_g_cm3'))} | {number(r.get('restricted_decomposition_eV_per_atom'),1000)} | "
                     f"{number(r.get('bulk_modulus_GPa'))} | {number(r.get('gamma_min_curvature_eV_A2'))} | "
                     f"{r.get('gamma_assessment', 'Not calculated')} |")
    lines += ["", "A positive decomposition energy means a lower-energy mixture exists among the selected endmembers in this model. A negative value only improves on this limited reference set; it does not establish full phase-diagram stability. The configured energy-screen threshold is a research triage rule, not a model-accuracy or stability guarantee.", "",
              "Positive Gamma eigenvalues alone are insufficient: the assessment also considers displacement-step sensitivity, Hessian asymmetry, and translation residuals. An inconclusive result is not a pass. This local diagnostic does not replace full phonon dispersion.", "",
              "## Potential applications", "",
              "1. **Dielectric-ceramic research for capacitors and electronic packaging.** Related Ca/Sr/Ba-Ti/Zr/Sn oxides have published precedents. This round supplies structures and limited compression response; permittivity, dielectric loss, insulation, breakdown, temperature response, and manufacturability remain unverified.",
              "2. **Ceramic-composite filler research.** Structures and densities can inform subsequent composite models. Interface bonding, thermal conductivity, thermal expansion, toughness, fatigue, processing, and lifetime require separate evaluation.",
              "3. **Open computational benchmarks.** The structures, raw observations, negative results, and uncertainty records can already be used to evaluate generation algorithms, compare interatomic potentials, or study decomposition hypotheses.", "",
              "Related-family precedent: https://doi.org/10.1016/j.ceramint.2023.11.388 . This precedent also limits novelty claims.", "",
              "## Reproducibility", "",
              "- config.json records generation and calculation parameters.",
              "- generated/generation.json records enumeration, symmetry, seeds, and selection; corresponding CIF files preserve every representative input.",
              "- Candidate directories contain structures, FIRE logs and trajectories, raw energy/force/stress observations, and EOS/Gamma data where actually calculated.",
              "- provenance.json, requirements-lock.txt, and source_snapshot/ record the environment, checkpoint hashes, and exact run source.",
              "- manifest.json records SHA256 hashes; verification.json checks integrity and recomputes aggregate metrics from observations.", "",
              "Use the README commands to rerun in a new output directory. Same-platform numerical replay is tested separately where reported. Timestamps and cross-platform floating-point behavior are not guaranteed to match byte-for-byte.", "",
              "## Limitations", ""] + [f"- {x}" for x in s["limitations"]]
    (directory / "report.md").write_text("\n".join(lines) + "\n")
