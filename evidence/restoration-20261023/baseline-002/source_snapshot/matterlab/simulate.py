from __future__ import annotations

import csv
import json
import time
import traceback
from pathlib import Path

import numpy as np
from ase.filters import FrechetCellFilter
from ase.io import read, write
from ase.optimize import FIRE

from .evidence import manifest, now, snapshot, write_json, check_resume
from .generate import generate, validate_structure
from .physics import (AMU_A3_TO_G_CM3, EV_A3_TO_GPA, fit_eos, force_constant_matrix,
                      gamma_diagnostic, restricted_decomposition, assess_gamma)


LIMITATIONS = [
    "CHGNet ML interatomic-potential screening; these results are neither DFT nor experimental synthesis.",
    "The material family has experimental precedents; novelty of the exact compositions and orderings is unverified.",
    "Limited initial structures and reference phases cannot establish the global minimum or full phase-diagram stability.",
    "Volume scans measure fixed-shape compression response, not strength, hardness, toughness, or full elastic stability.",
    "Gamma curvatures probe local displacements in the chosen periodic cell, not the full phonon dispersion.",
    "Applications are research hypotheses; dielectric, thermal, breakdown, processing, and lifetime performance remain unverified.",
]


def applications(result):
    base = "Related oxides have dielectric-ceramic literature; this candidate has only the interatomic-potential calculations listed in its record."
    if result.get("restricted_decomposition_eV_per_atom", 0) > .01:
        base += " Its energy exceeds the restricted endmember screening threshold; decomposition and synthesizability need priority investigation."
    return [
        {"name": "Dielectric-ceramic research candidate for capacitors and electronic packaging", "evidence": base,
         "missing": ["Permittivity and dielectric loss", "Insulation resistance and breakdown field", "Temperature response", "Full phase stability and experimental synthesis"]},
        {"name": "Ceramic-composite filler research candidate", "evidence": "Composition, density, and calculated compression response can inform subsequent models; no product-performance claim is established.",
         "missing": ["Interface bonding and dispersion", "Thermal conductivity and expansion", "Toughness, fatigue, and processing validation"]},
    ]


def make_calculator(config):
    import torch
    from chgnet.model.model import CHGNet
    from chgnet.model.dynamics import CHGNetCalculator
    torch.set_num_threads(config["threads"])
    torch.manual_seed(config["seed"])
    torch.use_deterministic_algorithms(True)
    model = CHGNet.load(model_name=config["model"], use_device=config["device"])
    return CHGNetCalculator(model=model, use_device=config["device"])


def relax(atoms, calculator, output, config, cell=True, steps=None, fmax=None):
    atoms.calc = calculator
    target = FrechetCellFilter(atoms) if cell else atoms
    optimizer = FIRE(target, logfile=str(output) + ".log", trajectory=str(output) + ".traj")
    tolerance = fmax if fmax is not None else min(config["relax_fmax_eV_A"], .01)
    stopped = optimizer.run(fmax=tolerance, steps=steps or config["relax_steps"])
    forces = atoms.get_forces()
    stress = atoms.get_stress(voigt=False)
    result = {"energy_eV": float(atoms.get_potential_energy()), "forces_eV_A": forces.tolist(),
              "stress_eV_A3": stress.tolist(), "max_force_eV_A": float(np.linalg.norm(forces, axis=1).max()),
              "max_stress_GPa": float(np.max(np.abs(stress)) * EV_A3_TO_GPA),
              "optimizer_converged": bool(stopped), "optimizer_steps": optimizer.nsteps}
    result["relaxation_converged"] = bool(stopped and result["max_force_eV_A"] <= (fmax or config["relax_fmax_eV_A"]) and
                                          (not cell or result["max_stress_GPa"] <= .15))
    return result


def compute_one(record, directory, calculator, config):
    start = time.perf_counter()
    output = directory / record["id"]
    output.mkdir(exist_ok=True)
    atoms = read(directory / record["input_cif"])
    observations = relax(atoms, calculator, output / "relax", config)
    validate_structure(atoms)
    write(output / "relaxed.cif", atoms)
    write(output / "relaxed.extxyz", atoms)
    write_json(output / "observations.json", observations)
    result = dict(record)
    result.update({k: v for k, v in observations.items() if k not in {"forces_eV_A", "stress_eV_A3", "energy_eV"}})
    result.update({"status": "relaxed" if observations["relaxation_converged"] else "unconverged",
                   "energy_eV_per_atom": observations["energy_eV"] / len(atoms),
                   "density_g_cm3": float(atoms.get_masses().sum() / atoms.get_volume() * AMU_A3_TO_G_CM3),
                   "volume_A3_per_atom": atoms.get_volume() / len(atoms),
                   "novelty_status": "known_reference" if record["kind"] == "reference" else "unverified_generated_composition_and_ordering",
                   "structure": {"symbols": atoms.get_chemical_symbols(), "positions": atoms.positions.tolist(), "cell": atoms.cell.array.tolist()},
                   "artifacts": {"initial_cif": record["input_cif"], "relaxed_cif": f"{record['id']}/relaxed.cif",
                                 "result_json": f"{record['id']}/result.json", "observations_json": f"{record['id']}/observations.json",
                                 "relaxation_log": f"{record['id']}/relax.log", "trajectory": f"{record['id']}/relax.traj"},
                   "elapsed_seconds": time.perf_counter() - start})
    if record["kind"] == "candidate":
        result["applications"] = applications(result)
    write_json(output / "result.json", result)
    return result


def detailed(result, directory, calculator, config):
    output = directory / result["id"]
    atoms = read(output / "relaxed.cif")
    # Tighten before energy-volume and finite-difference calculations.
    fine = atoms.copy()
    fine_obs = relax(fine, calculator, output / "refine", config, fmax=.005, steps=400)
    write(output / "refined.cif", fine)
    write_json(output / "refined_observations.json", fine_obs)
    result["refinement"] = {k: v for k, v in fine_obs.items() if k not in {"forces_eV_A", "stress_eV_A3"}}
    if not fine_obs["relaxation_converged"]:
        result["detail_error"] = "Tight relaxation did not converge; detailed claims withheld"
        return
    result["initial_relaxation"] = {k: result[k] for k in ("energy_eV_per_atom", "density_g_cm3", "volume_A3_per_atom", "max_force_eV_A", "max_stress_GPa")}
    result["active_structure_stage"] = "refined"
    result["refinement_energy_change_eV_per_atom"] = fine_obs["energy_eV"] / len(fine) - result["energy_eV_per_atom"]
    result["refinement_volume_relative_change"] = fine.get_volume() / atoms.get_volume() - 1
    result.update({"energy_eV_per_atom": fine_obs["energy_eV"] / len(fine),
                   "density_g_cm3": float(fine.get_masses().sum() / fine.get_volume() * AMU_A3_TO_G_CM3),
                   "volume_A3_per_atom": fine.get_volume() / len(fine),
                   "max_force_eV_A": fine_obs["max_force_eV_A"], "max_stress_GPa": fine_obs["max_stress_GPa"],
                   "structure": {"symbols": fine.get_chemical_symbols(), "positions": fine.positions.tolist(), "cell": fine.cell.array.tolist()}})
    result["artifacts"].update({"coarse_relaxed_cif": f"{result['id']}/relaxed.cif",
                                "relaxed_cif": f"{result['id']}/refined.cif",
                                "observations_json": f"{result['id']}/refined_observations.json",
                                "refinement_log": f"{result['id']}/refine.log"})
    rows = []
    for index, strain in enumerate(config["eos_strains"]):
        point = fine.copy()
        point.set_cell(fine.cell.array * (1 + strain) ** (1 / 3), scale_atoms=True)
        obs = relax(point, calculator, output / f"eos-{index:02d}", config, cell=False,
                    steps=config["eos_steps"], fmax=.005)
        write(output / f"eos-{index:02d}.extxyz", point)
        rows.append({"volume_strain": strain, "volume_A3": point.get_volume(), "energy_eV": obs["energy_eV"],
                     "max_force_eV_A": obs["max_force_eV_A"], "converged": int(obs["relaxation_converged"])})
    with (output / "eos.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result["artifacts"]["eos_csv"] = f"{result['id']}/eos.csv"
    if all(r["converged"] for r in rows):
        try:
            fit = fit_eos([r["volume_A3"] for r in rows], [r["energy_eV"] for r in rows])
            if fit["bulk_modulus_r2"] < .99:
                result["eos_error"] = "Fit R2 below 0.99; modulus withheld"
            else:
                result.update(fit)
                inner = fit_eos([r["volume_A3"] for r in rows[1:-1]], [r["energy_eV"] for r in rows[1:-1]])
                result["bulk_modulus_inner_window_GPa"] = inner["bulk_modulus_GPa"]
                result["bulk_modulus_window_relative_difference"] = abs(inner["bulk_modulus_GPa"] / fit["bulk_modulus_GPa"] - 1)
        except (ValueError, RuntimeError) as error:
            result["eos_error"] = str(error)
    else:
        result["eos_error"] = "One or more EOS ionic relaxations failed; modulus withheld"
    diagnostics = []
    for step_index, displacement in enumerate([config["gamma_displacement_A"], config["gamma_displacement_A"] / 2]):
        plus, minus = [], []
        for coordinate in range(len(fine) * 3):
            for sign, target in [(1, plus), (-1, minus)]:
                point = fine.copy()
                point.positions[coordinate // 3, coordinate % 3] += sign * displacement
                point.calc = calculator
                target.append(point.get_forces())
        suffix = "" if step_index == 0 else "_half_step"
        np.savez_compressed(output / f"gamma_forces{suffix}.npz", plus=np.array(plus), minus=np.array(minus), displacement_A=displacement)
        hessian, asymmetry = force_constant_matrix(minus, plus, displacement)
        np.savetxt(output / f"gamma_hessian{suffix}.csv", hessian, delimiter=",")
        diagnostic = gamma_diagnostic(hessian, len(fine))
        diagnostic.update({"displacement_A": displacement, "hessian_asymmetry_eV_A2": asymmetry})
        diagnostics.append(diagnostic)
    result.update(diagnostics[1])
    result["gamma_step_checks"] = diagnostics
    result["gamma_step_min_curvature_difference_eV_A2"] = abs(diagnostics[0]["gamma_min_curvature_eV_A2"] - diagnostics[1]["gamma_min_curvature_eV_A2"])
    result.update(assess_gamma(diagnostics, config["gamma_negative_tolerance_eV_A2"]))
    result["artifacts"]["gamma_forces_npz"] = f"{result['id']}/gamma_forces.npz"
    result["artifacts"]["gamma_hessian_csv"] = f"{result['id']}/gamma_hessian.csv"
    result["artifacts"]["gamma_half_step_forces_npz"] = f"{result['id']}/gamma_forces_half_step.npz"


def run(config_path, output, resume=False):
    config = json.loads(Path(config_path).read_text())
    directory = Path(output)
    if directory.exists() and not resume:
        raise FileExistsError("Output already exists; choose another directory or use --resume")
    directory.mkdir(parents=True, exist_ok=True)
    saved_config = directory / "config.json"
    if saved_config.exists() and json.loads(saved_config.read_text()) != config:
        raise ValueError("Resume configuration differs from recorded configuration")
    write_json(saved_config, config)
    if not (directory / "provenance.json").exists():
        snapshot(directory, config)
    elif resume:
        check_resume(directory, config)
    generation_path = directory / "generated" / "generation.json"
    generation = json.loads(generation_path.read_text()) if generation_path.exists() else generate(config, directory / "generated")
    calculator = make_calculator(config)
    summary = {"run_id": directory.name, "campaign": config["run_id"], "created_at": now(), "method": "ML interatomic potential: CHGNet",
               "model": config["model"], "seed": config["seed"], "limitations": LIMITATIONS,
               "generation": generation["groups"], "candidates": [], "completed": False}
    selected = [r for r in generation["structures"] if r["selected"]]
    selected.sort(key=lambda r: (r["kind"] != "reference", r["id"]))
    for record in selected:
        cached = directory / record["id"] / "result.json"
        print(f"Computing {record['id']} {record['formula']}", flush=True)
        try:
            result = json.loads(cached.read_text()) if resume and cached.exists() else compute_one(record, directory, calculator, config)
        except Exception as error:
            result = dict(record, status="failed", error=str(error), traceback=traceback.format_exc())
            write_json(cached, result)
        summary["candidates"].append(result)
        write_json(directory / "summary.json", summary)
        print(f"  {result['status']} E={result.get('energy_eV_per_atom')} fmax={result.get('max_force_eV_A')}", flush=True)
    references = {}
    for result in summary["candidates"]:
        if result["kind"] == "reference" and result.get("relaxation_converged"):
            references[next(iter(result["composition"]["A"])), next(iter(result["composition"]["B"]))] = result["energy_eV_per_atom"]
    for result in summary["candidates"]:
        if result["kind"] != "candidate" or not result.get("relaxation_converged"):
            continue
        if len(references) == len(config["a_elements"]) * len(config["b_elements"]):
            composition = result["composition"]
            fractions = [{k: v / sum(composition[s].values()) for k, v in composition[s].items()} for s in ("A", "B")]
            energy, weights = restricted_decomposition(references, *fractions)
            result["restricted_decomposition_eV_per_atom"] = result["energy_eV_per_atom"] - energy
            result["restricted_reference_weights"] = weights
            result["status"] = "above_restricted_reference" if result["restricted_decomposition_eV_per_atom"] > config["restricted_energy_tolerance_eV_atom"] else "ml_screened"
        else:
            result["restricted_reference_error"] = "Not all nine endmembers converged; decomposition withheld"
        result["applications"] = applications(result)
    finalists = [r for r in summary["candidates"] if r["kind"] == "candidate" and r.get("relaxation_converged")]
    finalists.sort(key=lambda r: (r.get("restricted_decomposition_eV_per_atom", float("inf")), r["id"]))
    for result in finalists[:config["detailed_candidates"]]:
        print(f"Detailed EOS/Gamma diagnostic: {result['id']}", flush=True)
        if not (resume and "gamma_min_curvature_eV_A2" in result):
            try:
                detailed(result, directory, calculator, config)
            except Exception as error:
                result["detail_error"] = str(error)
                result["detail_traceback"] = traceback.format_exc()
        if result.get("gamma_test_passed") is False:
            result["status"] = "gamma_instability_detected"
        write_json(directory / result["id"] / "result.json", result)
        write_json(directory / "summary.json", summary)
    # Reconcile every individual result with the aggregate, including failed candidates.
    for result in summary["candidates"]:
        if result["kind"] == "candidate" and result.get("restricted_reference_weights"):
            composition = result["composition"]
            fractions = [{k: v / sum(composition[s].values()) for k, v in composition[s].items()} for s in ("A", "B")]
            energy, weights = restricted_decomposition(references, *fractions)
            result["restricted_decomposition_eV_per_atom"] = result["energy_eV_per_atom"] - energy
            if result.get("gamma_test_passed") is not False:
                result["status"] = "above_restricted_reference" if result["restricted_decomposition_eV_per_atom"] > config["restricted_energy_tolerance_eV_atom"] else "ml_screened"
            result["applications"] = applications(result)
        write_json(directory / result["id"] / "result.json", result)
    summary["completed"] = True
    summary["completed_at"] = now()
    summary["discovery_claim"] = "No verified new material discovery or synthesis claim"
    write_json(directory / "summary.json", summary)
    manifest(directory)
    index_path = directory.parent / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else []
    index = [r for r in index if r["run_id"] != directory.name]
    index.append({"run_id": directory.name, "path": f"/runs/{directory.name}/summary.json", "created_at": summary["created_at"]})
    write_json(index_path, index)
    return summary
