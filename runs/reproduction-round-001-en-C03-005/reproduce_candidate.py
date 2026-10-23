#!/usr/bin/env python3
"""Replay one real relaxation from saved source and compare like-for-like raw states.

This checks numerical reproducibility, not accuracy against DFT or experiment.
The output directory must be new and separate from the original run.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import traceback


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def load(path):
    return json.loads(Path(path).read_text())


def contained(root, relative):
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"Evidence path must be relative and contained: {relative}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Missing or out-of-run evidence path: {relative}")
    return path


def refinement_settings(source):
    """Read the literal first refinement call; fail instead of guessing new code."""
    tree = ast.parse(Path(source).read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "detailed")
    for statement in function.body:
        if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "fine_obs" for t in statement.targets):
            call = statement.value
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "relax":
                break
            settings = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
            if set(settings) != {"fmax", "steps"}:
                break
            return settings
    raise ValueError("Saved refinement implementation is not recognized; replay settings cannot be inferred safely")


def worker(args):
    # Both sys.path and the subprocess PYTHONPATH select this immutable copy.
    sys.path.insert(0, str(args.output / "source_snapshot"))
    import numpy as np
    from ase import Atoms
    from ase.io import read, write
    import matterlab.simulate as simulate
    from matterlab.evidence import check_resume, environment

    imported = Path(simulate.__file__).resolve()
    if not imported.is_relative_to(args.output / "source_snapshot"):
        raise RuntimeError("Replay imported live project code instead of the saved source")
    config = load(args.output / "config.json")
    # Reject changed Python/packages/checkpoints/device, even when results look close.
    check_resume(args.run_directory, config)
    write_json(args.output / "provenance.json", environment(config))
    random.seed(config["seed"])
    np.random.seed(config["seed"])
    calculator = simulate.make_calculator(config)  # Also resets torch seed/determinism.
    record = load(args.output / "candidate_record.json")
    recorded = load(args.output / "expected" / "result.json")
    replay = simulate.compute_one(record, args.output, calculator, config)
    stage = recorded.get("active_structure_stage", "relaxed")
    candidate_dir = args.output / args.candidate_id
    if stage == "refined":
        # Follow detailed(): serialize/read the coarse CIF, then refine without EOS/Gamma.
        atoms = read(candidate_dir / "relaxed.cif")
        settings = refinement_settings(imported)
        raw = simulate.relax(atoms, calculator, candidate_dir / "refine", config, **settings)
        write(candidate_dir / "refined.cif", atoms)
        write(candidate_dir / "refined.extxyz", atoms)
        write_json(candidate_dir / "refined_observations.json", raw)
    elif stage == "relaxed":
        structure = replay["structure"]
        atoms = Atoms(structure["symbols"], positions=structure["positions"], cell=structure["cell"], pbc=True)
        raw = load(candidate_dir / "observations.json")
        settings = None
    else:
        raise ValueError(f"Unsupported active structure stage: {stage}")
    expected = load(args.output / "expected" / "observations.json")
    # CIF round trips canonicalize cell orientation. Compare the recorded raw basis
    # from result.json to the replay raw basis, never raw vectors to a rotated CIF.
    structure = recorded["structure"]
    expected_atoms = Atoms(structure["symbols"], positions=structure["positions"], cell=structure["cell"], pbc=True)
    symbols_match = atoms.get_chemical_symbols() == expected_atoms.get_chemical_symbols()
    if not symbols_match:
        raise ValueError("Atom count/order/species differ; raw force comparison is invalid")

    comparisons = {}

    def compare(name, actual, reference, tolerance):
        actual, reference = np.asarray(actual), np.asarray(reference)
        finite = bool(np.isfinite(actual).all() and np.isfinite(reference).all())
        shape_match = actual.shape == reference.shape
        difference = float(np.max(np.abs(actual - reference))) if finite and shape_match else None
        comparisons[name] = {"max_absolute_difference": difference, "absolute_tolerance": tolerance,
                             "passed": finite and shape_match and difference <= tolerance}

    compare("energy_eV_per_atom", raw["energy_eV"] / len(atoms), expected["energy_eV"] / len(expected_atoms), args.energy_atol)
    compare("forces_eV_A", raw["forces_eV_A"], expected["forces_eV_A"], args.force_atol)
    compare("stress_eV_A3", raw["stress_eV_A3"], expected["stress_eV_A3"], args.stress_atol)
    compare("cell_A", atoms.cell.array, expected_atoms.cell.array, args.cell_atol)
    # Fractional MIC handles CIF wrapping without silently permuting atom identities.
    fractional_delta = atoms.get_scaled_positions() - expected_atoms.get_scaled_positions()
    fractional_delta -= np.rint(fractional_delta)
    compare("same_site_displacement_A", fractional_delta @ expected_atoms.cell.array,
            np.zeros((len(atoms), 3)), args.position_atol)
    convergence_matches = raw["relaxation_converged"] == expected["relaxation_converged"]
    comparisons["convergence_state"] = {"actual": raw["relaxation_converged"],
                                         "recorded": expected["relaxation_converged"], "passed": convergence_matches}
    passed = all(check["passed"] for check in comparisons.values())
    report = {"passed": passed, "candidate_id": args.candidate_id, "active_structure_stage": stage,
              "original_run": os.path.relpath(args.run_directory, args.output),
              "source_module": str(imported.relative_to(args.output)),
              "source_module_sha256": digest(imported), "refinement_parameters": settings,
              "geometry_reference": "authenticated result.json structure in its raw Cartesian basis; CIF retained separately",
              "comparisons": comparisons, "optimizer_steps": raw["optimizer_steps"],
              "recorded_optimizer_steps": expected["optimizer_steps"],
              "scope": "Independent fresh local ML-potential relaxation from original generated CIF; same saved model/code. Not DFT or experimental validation.",
              "not_replayed": ["EOS scans", "Gamma finite displacements", "other candidates", "phase-reference calculations"]}
    write_json(args.output / "reproduction.json", report)
    print(json.dumps({"passed": passed, "stage": stage, "comparisons": comparisons}, indent=2), flush=True)
    return 0 if passed else 1


def launch(args):
    run, output = args.run_directory, args.output
    if output == run or output.is_relative_to(run) or run.is_relative_to(output):
        raise ValueError("Output must be separate from, and not an ancestor of, the original run")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.candidate_id):
        raise ValueError("Invalid candidate identifier")
    if any(not math.isfinite(value) or value <= 0 for value in (args.energy_atol, args.force_atol, args.stress_atol, args.cell_atol, args.position_atol)):
        raise ValueError("Comparison tolerances must be positive")
    source_manifest = load(run / "manifest.json")
    records = load(run / "generated" / "generation.json")["structures"]
    record = next(r for r in records if r["id"] == args.candidate_id)
    result_path = f"{args.candidate_id}/result.json"
    result = load(contained(run, result_path))
    raw_path = result["artifacts"]["observations_json"]
    cif_path = result["artifacts"]["relaxed_cif"]
    stage = result.get("active_structure_stage", "relaxed")
    expected_raw = "refined_observations.json" if stage == "refined" else "observations.json"
    if stage not in {"relaxed", "refined"} or raw_path != f"{args.candidate_id}/{expected_raw}":
        raise ValueError("Recorded active stage and raw-observation artifact disagree")
    files = ["config.json", "provenance.json", "generated/generation.json", "requirements-lock.txt",
             record["input_cif"], result_path, raw_path, cif_path]
    files += [str(p.relative_to(run)) for p in (run / "source_snapshot" / "matterlab").glob("*.py")]
    for relative in files:
        path = contained(run, relative)
        if source_manifest["files"].get(relative) != digest(path):
            raise ValueError(f"Original manifest does not authenticate required evidence: {relative}")
    output.mkdir(parents=True, exist_ok=False)
    (output / "expected").mkdir()
    source = output / "source_snapshot" / "matterlab"
    source.mkdir(parents=True)
    for path in (run / "source_snapshot" / "matterlab").glob("*.py"):
        shutil.copyfile(path, source / path.name)
    for name in ("config.json", "requirements-lock.txt"):
        shutil.copyfile(run / name, output / name)
    generated = output / record["input_cif"]
    generated.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(run / record["input_cif"], generated)
    for relative, name in ((result_path, "result.json"), (raw_path, "observations.json"),
                           (cif_path, "active.cif"), ("provenance.json", "provenance.json")):
        shutil.copyfile(run / relative, output / "expected" / name)
    write_json(output / "candidate_record.json", record)
    write_json(output / "original_manifest.json", source_manifest)
    shutil.copyfile(__file__, output / "reproduce_candidate.py")
    command = [sys.executable, str(output / "reproduce_candidate.py"), str(run), args.candidate_id, str(output),
               "--worker", "--energy-atol", str(args.energy_atol), "--force-atol", str(args.force_atol),
               "--stress-atol", str(args.stress_atol), "--cell-atol", str(args.cell_atol),
               "--position-atol", str(args.position_atol)]
    portable_command = ["python", "reproduce_candidate.py", os.path.relpath(run, output),
                        args.candidate_id, "."] + command[5:]
    write_json(output / "invocation.json", {
        "argv": portable_command,
        "path_policy": "Recorded invocation uses paths relative to this output directory; execution resolved local absolute paths.",
        "original_inputs_sha256": {p: digest(run / p) for p in files}})
    env = dict(os.environ, PYTHONPATH=str(output / "source_snapshot"), PYTHONDONTWRITEBYTECODE="1")
    if env.get("MPLCONFIGDIR"):
        env["MPLCONFIGDIR"] = str(Path(env["MPLCONFIGDIR"]).resolve())
    with (output / "replay.log").open("w") as stream:
        completed = subprocess.run(command, env=env, cwd=output, stdout=stream, stderr=subprocess.STDOUT)
    if not (output / "reproduction.json").exists():
        write_json(output / "reproduction.json", {"passed": False, "error": "Worker failed before comparison", "worker_exit_code": completed.returncode})
    write_json(output / "manifest.json", {"algorithm": "SHA256", "files": {
        str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts and ".cache" not in p.parts}})
    print(f"Reproduction {'PASSED' if completed.returncode == 0 else 'FAILED'}: {output / 'reproduction.json'}")
    return completed.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=lambda p: Path(p).resolve())
    parser.add_argument("candidate_id")
    parser.add_argument("output", type=lambda p: Path(p).resolve())
    parser.add_argument("--energy-atol", type=float, default=1e-5, help="absolute eV/atom tolerance (default: %(default)s)")
    parser.add_argument("--force-atol", type=float, default=2e-4, help="absolute force-component eV/Angstrom tolerance")
    parser.add_argument("--stress-atol", type=float, default=1e-5, help="absolute stress-component eV/Angstrom^3 tolerance")
    parser.add_argument("--cell-atol", type=float, default=1e-4, help="absolute cell-component Angstrom tolerance")
    parser.add_argument("--position-atol", type=float, default=1e-3, help="absolute MIC same-site displacement-component Angstrom tolerance")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        return worker(args) if args.worker else launch(args)
    except Exception as error:
        if args.worker:
            write_json(args.output / "reproduction.json", {"passed": False, "error": str(error), "traceback": traceback.format_exc()})
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
