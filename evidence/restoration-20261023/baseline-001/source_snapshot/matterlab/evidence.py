from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def now():
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    temporary.replace(path)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def environment(config):
    import chgnet
    packages = {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()}
    model_files = sorted(Path(chgnet.__file__).parent.rglob("*.pth.tar"))
    if not model_files:
        model_files = sorted(Path(chgnet.__file__).parent.rglob("*.pth"))
    provenance = {"created_at": now(), "python": sys.version, "platform": platform.platform(),
                  "machine": platform.machine(), "packages": dict(sorted(packages.items())),
                  "model_checkpoints": {str(p.relative_to(Path(chgnet.__file__).parent)): sha256(p) for p in model_files},
                  "model": "CHGNet " + config["model"], "device": config["device"],
                  "threads": config["threads"], "seed": config["seed"],
                  "external_api_calls": 0, "paid_compute": False,
                  "claim": "real local ML-potential calculations, not DFT or experiment"}
    return provenance


def snapshot(directory, config):
    directory = Path(directory)
    provenance = environment(config)
    packages = provenance["packages"]
    write_json(directory / "provenance.json", provenance)
    source = directory / "source_snapshot" / "matterlab"
    source.mkdir(parents=True, exist_ok=True)
    for p in Path(__file__).parent.glob("*.py"):
        shutil.copyfile(p, source / p.name)
    (directory / "requirements-lock.txt").write_text("\n".join(f"{k}=={v}" for k, v in sorted(packages.items()) if k != "matterlab-discovery") + "\n")


def check_resume(directory, config):
    directory = Path(directory)
    old = json.loads((directory / "provenance.json").read_text())
    current = environment(config)
    for key in ("python", "platform", "packages", "model_checkpoints", "model", "device", "threads"):
        if old[key] != current[key]:
            raise ValueError(f"Resume would mix environments ({key}); use a new run directory")
    current_source = {p.name: sha256(p) for p in Path(__file__).parent.glob("*.py")}
    saved_source = {p.name: sha256(p) for p in (directory / "source_snapshot" / "matterlab").glob("*.py")}
    if current_source != saved_source:
        raise ValueError("Resume source code differs from run snapshot; use the saved source or a new run directory")


def manifest(directory):
    directory = Path(directory)
    hashes = {str(p.relative_to(directory)): sha256(p) for p in sorted(directory.rglob("*"))
              if p.is_file() and p.name not in {"manifest.json", "verification.json"} and p.suffix != ".tmp"}
    write_json(directory / "manifest.json", {"algorithm": "SHA256", "files": hashes})


def verify(directory):
    """Check file integrity and recompute reported observables from raw evidence."""
    import numpy as np
    from ase.io import read
    from .physics import (AMU_A3_TO_G_CM3, EV_A3_TO_GPA, fit_eos, restricted_decomposition,
                          force_constant_matrix, gamma_diagnostic, assess_gamma)
    directory = Path(directory)
    errors = []
    checks = 0
    recorded = json.loads((directory / "manifest.json").read_text())
    for relative, expected in recorded["files"].items():
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory.resolve()) or not path.is_file() or sha256(path) != expected:
            errors.append(f"Integrity mismatch: {relative}")
        checks += 1
    summary = json.loads((directory / "summary.json").read_text())
    config = json.loads((directory / "config.json").read_text())
    references = {}
    for result in summary["candidates"]:
        if "energy_eV_per_atom" not in result:
            continue
        path = directory / result["id"]
        raw = json.loads((directory / result["artifacts"]["observations_json"]).read_text())
        atoms = read(directory / result["artifacts"]["relaxed_cif"])
        observables = {"energy_eV_per_atom": raw["energy_eV"] / len(atoms),
                       "density_g_cm3": atoms.get_masses().sum() / atoms.get_volume() * AMU_A3_TO_G_CM3,
                       "volume_A3_per_atom": atoms.get_volume() / len(atoms),
                       "max_force_eV_A": np.linalg.norm(raw["forces_eV_A"], axis=1).max(),
                       "max_stress_GPa": np.max(np.abs(raw["stress_eV_A3"])) * EV_A3_TO_GPA}
        for name, recomputed in observables.items():
            if not np.isclose(result[name], recomputed, rtol=1e-6, atol=1e-7):
                errors.append(f"{result['id']}: {name} does not match raw evidence")
            checks += 1
        if result["relaxation_converged"] and (not raw["optimizer_converged"] or
                observables["max_force_eV_A"] > config["relax_fmax_eV_A"] or observables["max_stress_GPa"] > .15):
            errors.append(f"{result['id']}: invalid relaxation pass claim")
        checks += 1
        if result["kind"] == "reference" and result["relaxation_converged"]:
            a = next(iter(result["composition"]["A"]))
            b = next(iter(result["composition"]["B"]))
            references[a, b] = result["energy_eV_per_atom"]
        if result.get("bulk_modulus_GPa") is not None:
            points = np.genfromtxt(path / "eos.csv", delimiter=",", names=True)
            fit = fit_eos(points["volume_A3"], points["energy_eV"])
            if not np.isclose(fit["bulk_modulus_GPa"], result["bulk_modulus_GPa"], rtol=1e-6):
                errors.append(f"{result['id']}: EOS mismatch")
            checks += 1
        if result.get("gamma_min_curvature_eV_A2") is not None:
            gamma_checks = []
            for suffix in ("", "_half_step"):
                raw_gamma = np.load(path / f"gamma_forces{suffix}.npz")
                hessian, asymmetry = force_constant_matrix(raw_gamma["minus"], raw_gamma["plus"], float(raw_gamma["displacement_A"]))
                diagnostic = gamma_diagnostic(hessian, len(atoms))
                diagnostic["hessian_asymmetry_eV_A2"] = asymmetry
                gamma_checks.append(diagnostic)
            if not np.isclose(diagnostic["gamma_min_curvature_eV_A2"], result["gamma_min_curvature_eV_A2"], atol=1e-9):
                errors.append(f"{result['id']}: Gamma curvature mismatch")
            if assess_gamma(gamma_checks, config["gamma_negative_tolerance_eV_A2"])["gamma_test_passed"] != result["gamma_test_passed"]:
                errors.append(f"{result['id']}: Gamma assessment mismatch")
            checks += 1
    for result in summary["candidates"]:
        if result.get("restricted_decomposition_eV_per_atom") is None:
            continue
        composition = result["composition"]
        fractions = [{k: v / sum(composition[site].values()) for k, v in composition[site].items()} for site in ("A", "B")]
        energy, weights = restricted_decomposition(references, *fractions)
        expected = result["energy_eV_per_atom"] - energy
        if not np.isclose(expected, result["restricted_decomposition_eV_per_atom"], atol=1e-8):
            errors.append(f"{result['id']}: restricted LP mismatch")
        checks += 1
    report = {"checked_at": now(), "passed": not errors, "checks": checks, "errors": errors,
              "scope": "artifact integrity and independent recomputation of aggregate metrics; not external physical validation"}
    write_json(directory / "verification.json", report)
    return report
