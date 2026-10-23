"""Numerical analyses with explicit units and intentionally bounded claims."""
from __future__ import annotations

import numpy as np
from ase.eos import EquationOfState, birchmurnaghan
from scipy.optimize import linprog

EV_A3_TO_GPA = 160.21766208
AMU_A3_TO_G_CM3 = 1.66053906660


def restricted_decomposition(reference_energies, a_fractions, b_fractions):
    """Minimize eV/atom at fixed A/B composition over provided ABO3 endpoints only."""
    pairs = sorted(reference_energies)
    for fractions in (a_fractions, b_fractions):
        if any(not np.isfinite(x) or x < 0 for x in fractions.values()) or not np.isclose(sum(fractions.values()), 1):
            raise ValueError("Sublattice fractions must be nonnegative and sum to one")
    a_symbols = sorted(set(a_fractions) | {a for a, b in pairs})
    b_symbols = sorted(set(b_fractions) | {b for a, b in pairs})
    constraints = [[float(a == x) for a, b in pairs] for x in a_symbols]
    constraints += [[float(b == x) for a, b in pairs] for x in b_symbols]
    target = [a_fractions.get(x, 0) for x in a_symbols] + [b_fractions.get(x, 0) for x in b_symbols]
    result = linprog([reference_energies[p] for p in pairs], A_eq=constraints, b_eq=target,
                     bounds=(0, None), method="highs")
    if not result.success:
        raise ValueError(f"Infeasible restricted decomposition: {result.message}")
    return float(result.fun), {f"{a}{b}O3": float(w) for (a, b), w in zip(pairs, result.x) if w > 1e-10}


def fit_eos(volumes, energies):
    """Fixed-shape isotropic EOS, internally relaxed ions. Not full elastic stability."""
    volumes = np.asarray(volumes, dtype=float)
    energies = np.asarray(energies, dtype=float)
    if len(volumes) < 5 or not np.isfinite(volumes).all() or not np.isfinite(energies).all():
        raise ValueError("EOS needs at least five finite observations")
    eos = EquationOfState(volumes, energies, eos="birchmurnaghan")
    v0, e0, bulk = eos.fit()
    prediction = birchmurnaghan(volumes, *eos.eos_parameters)
    residual = energies - prediction
    denominator = np.sum((energies - energies.mean()) ** 2)
    r2 = 1 - np.sum(residual ** 2) / denominator if denominator > 0 else 0.0
    if bulk <= 0 or not min(volumes) < v0 < max(volumes):
        raise ValueError("EOS minimum is nonphysical or outside sampled volumes")
    return {"bulk_modulus_GPa": float(bulk * EV_A3_TO_GPA), "bulk_modulus_r2": float(r2),
            "eos_equilibrium_volume_A3": float(v0), "eos_equilibrium_energy_eV": float(e0),
            "eos_rmse_eV": float(np.sqrt(np.mean(residual ** 2))),
            "eos_parameters": [float(x) for x in eos.eos_parameters],
            "eos_constraint": "fixed shape, isotropic cell scaling; internal ionic relaxation"}


def force_constant_matrix(force_minus, force_plus, displacement):
    """Column j is -dF_i/dx_j; forces have shape (3N, N, 3)."""
    fm = np.asarray(force_minus, dtype=float)
    fp = np.asarray(force_plus, dtype=float)
    if fm.shape != fp.shape or fm.ndim != 3 or fm.shape[0] != fm.shape[1] * 3 or fm.shape[2] != 3:
        raise ValueError("Inconsistent finite-displacement force array")
    hessian = -((fp - fm) / (2 * displacement)).reshape(fm.shape[0], -1).T
    asymmetry = float(np.max(np.abs(hessian - hessian.T)))
    return (hessian + hessian.T) / 2, asymmetry


def gamma_diagnostic(hessian, atom_count):
    """Project out translations, report unweighted curvature eigenvalues, NOT phonon frequencies."""
    translations = np.zeros((3 * atom_count, 3))
    for axis in range(3):
        translations[axis::3, axis] = 1 / np.sqrt(atom_count)
    q, _ = np.linalg.qr(translations, mode="complete")
    internal = q[:, 3:]
    eigenvalues = np.linalg.eigvalsh(internal.T @ hessian @ internal)
    return {"gamma_min_curvature_eV_A2": float(eigenvalues.min()),
            "gamma_curvatures_eV_A2": eigenvalues.tolist(),
            "gamma_scope": "Gamma of this 20-atom periodic cell, fixed lattice, translations projected out; not full phonon dispersion",
            "gamma_translation_residual_eV_A2": float(np.max(np.abs(hessian @ translations)))}


def assess_gamma(diagnostics, negative_tolerance):
    minima = [d["gamma_min_curvature_eV_A2"] for d in diagnostics]
    scale = max(abs(minima[0] - minima[1]), 1e-4,
                *(d["hessian_asymmetry_eV_A2"] for d in diagnostics),
                *(d["gamma_translation_residual_eV_A2"] for d in diagnostics))
    if max(minima) < -max(abs(negative_tolerance), 3 * scale):
        passed, label = False, "negative_curvature_detected_at_both_steps"
    elif min(minima) > 3 * scale:
        passed, label = True, "positive_internal_curvature_at_tested_steps"
    else:
        passed, label = None, "inconclusive_near_zero_or_numerically_sensitive"
    return {"gamma_test_passed": passed, "gamma_assessment": label,
            "gamma_numerical_diagnostic_scale_eV_A2": scale,
            "gamma_assessment_scope": "numerical screening heuristic, not statistical uncertainty or full phonon stability"}
