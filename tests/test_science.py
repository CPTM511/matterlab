"""Analytic unit fixtures only: none are scientific results or written to runs/."""
from collections import Counter

import numpy as np
import pytest
from ase.io import read

from matterlab.generate import (
    canonical_decoration,
    generate,
    parent_cell,
    perturb,
    symmetry_permutations,
    validate_structure,
)
from matterlab.physics import (
    fit_eos,
    force_constant_matrix,
    gamma_diagnostic,
    restricted_decomposition,
)


MATRIX = [[1, 1, 0], [-1, 1, 0], [0, 0, 2]]


@pytest.fixture
def config():
    return {
        "seed": 72,
        "supercell": MATRIX,
        "a_elements": ["Ca", "Sr", "Ba"],
        "b_elements": ["Ti", "Zr", "Sn"],
        "orderings_per_composition": 3,
        "initial_displacement_A": 0.03,
        "compositions": [{"A": {"Ca": 2, "Sr": 1, "Ba": 1},
                          "B": {"Ti": 2, "Zr": 1, "Sn": 1}}],
    }


def test_generator_reproduces_structures_and_sampling(config, tmp_path):
    first = generate(config, tmp_path / "first")
    second = generate(config, tmp_path / "second")
    assert first == second
    assert first["groups"][0]["raw_decorations"] == 144  # (4!/2!) squared
    assert first["groups"][0]["selected"] == 3
    candidate_records = [r for r in first["structures"] if r["kind"] == "candidate"]
    assert len({tuple(r["canonical_symbols"]) for r in candidate_records}) == len(candidate_records)
    for record in first["structures"]:
        name = record["id"] + ".cif"
        left = read(tmp_path / "first" / name)
        right = read(tmp_path / "second" / name)
        np.testing.assert_array_equal(left.numbers, right.numbers)
        np.testing.assert_allclose(left.positions, right.positions, rtol=0, atol=1e-12)
        np.testing.assert_allclose(left.cell, right.cell, rtol=0, atol=1e-12)


def test_generated_candidates_preserve_charge_composition_and_separation(config, tmp_path):
    result = generate(config, tmp_path / "structures")
    expected = Counter({"Ca": 2, "Sr": 1, "Ba": 1, "Ti": 2, "Zr": 1, "Sn": 1, "O": 12})
    oxidation = {"Ca": 2, "Sr": 2, "Ba": 2, "Ti": 4, "Zr": 4, "Sn": 4, "O": -2}
    for record in result["structures"]:
        atoms = read(tmp_path / "structures" / (record["id"] + ".cif"))
        assert len(atoms) == 20
        assert sum(oxidation[s] for s in atoms.get_chemical_symbols()) == 0
        if record["kind"] == "candidate":
            assert Counter(atoms.get_chemical_symbols()) == expected
        assert atoms.get_volume() == pytest.approx(4 * 4.05**3)
        distances = atoms.get_all_distances(mic=True)
        assert distances[np.triu_indices(20, k=1)].min() > 1.0


def test_perturb_seed_changes_coordinates_without_changing_composition():
    parent = parent_cell(MATRIX)
    one = perturb(parent, seed=12, amplitude=0.03, lattice=4.05)
    repeat = perturb(parent, seed=12, amplitude=0.03, lattice=4.05)
    other = perturb(parent, seed=13, amplitude=0.03, lattice=4.05)
    np.testing.assert_array_equal(one.positions, repeat.positions)
    assert not np.allclose(one.positions, other.positions)
    np.testing.assert_array_equal(one.numbers, parent.numbers)
    np.testing.assert_array_equal(one.cell, parent.cell)


def test_decoration_key_is_invariant_under_every_parent_operation():
    parent = parent_cell(MATRIX)
    operations = symmetry_permutations(parent)
    labels = parent.get_chemical_symbols()
    a_sites = np.flatnonzero(parent.numbers == 20)
    b_sites = np.flatnonzero(parent.numbers == 22)
    for i, symbol in zip(a_sites, ["Ca", "Sr", "Ba", "Ca"]):
        labels[i] = symbol
    for i, symbol in zip(b_sites, ["Sn", "Ti", "Zr", "Ti"]):
        labels[i] = symbol
    canonical = canonical_decoration(labels, operations)
    for permutation in operations:
        transformed = [labels[i] for i in permutation]
        assert canonical_decoration(transformed, operations) == canonical
    # A real species substitution must not disappear under symmetry reduction.
    different = labels.copy()
    different[a_sites[0]] = "Sr"
    assert canonical_decoration(different, operations) != canonical


def test_structure_validation_detects_periodic_boundary_overlap():
    atoms = parent_cell(MATRIX)
    atoms.positions[1] = atoms.positions[0] + atoms.cell[0] + [0.1, 0, 0]
    with pytest.raises(ValueError, match="overlap"):
        validate_structure(atoms)


def test_structure_validation_rejects_wrong_stoichiometry_and_nonfinite_input():
    atoms = parent_cell(MATRIX)
    del atoms[-1]
    with pytest.raises(ValueError, match="stoichiometry"):
        validate_structure(atoms)
    atoms = parent_cell(MATRIX)
    atoms.positions[0, 0] = np.nan
    with pytest.raises(ValueError, match="Nonfinite"):
        validate_structure(atoms)


def test_restricted_decomposition_finds_lower_cross_pairing_than_naive_average():
    # Synthetic endpoint energies in eV/atom. Optimum uses only the cross pairs.
    refs = {("Ca", "Ti"): -10.0, ("Ca", "Zr"): -12.0,
            ("Sr", "Ti"): -13.0, ("Sr", "Zr"): -10.0}
    energy, weights = restricted_decomposition(refs, {"Ca": 0.5, "Sr": 0.5}, {"Ti": 0.5, "Zr": 0.5})
    assert energy == pytest.approx(-12.5)
    assert weights == pytest.approx({"CaZrO3": 0.5, "SrTiO3": 0.5})
    assert energy < np.mean(list(refs.values()))


def test_restricted_decomposition_obeys_six_cation_marginals():
    # The diagonal is uniquely favored and exactly accommodates the 2:1:1 recipe.
    a = {"Ca": 0.5, "Sr": 0.25, "Ba": 0.25}
    b = {"Ti": 0.5, "Zr": 0.25, "Sn": 0.25}
    refs = {(x, y): -1.0 for x in a for y in b}
    refs.update({("Ca", "Ti"): -4.0, ("Sr", "Zr"): -6.0, ("Ba", "Sn"): -8.0})
    energy, weights = restricted_decomposition(refs, a, b)
    assert energy == pytest.approx(-5.5)
    assert weights == pytest.approx({"CaTiO3": 0.5, "SrZrO3": 0.25, "BaSnO3": 0.25})
    assert sum(weights.values()) == pytest.approx(1.0)


@pytest.mark.parametrize("extraneous", [
    {("Ba", "Sn"): -100.0},  # Neither element occurs in the candidate.
    {("Ca", "Sn"): -100.0, ("Ba", "Ti"): -100.0},  # Illegal partial marginals.
])
def test_restricted_decomposition_excludes_absent_elements(extraneous):
    refs = {("Ca", "Ti"): -10.0, **extraneous}
    energy, weights = restricted_decomposition(refs, {"Ca": 1.0}, {"Ti": 1.0})
    assert energy == pytest.approx(-10.0)
    assert weights == pytest.approx({"CaTiO3": 1.0})


def test_restricted_decomposition_reports_infeasible_reference_coverage():
    with pytest.raises(ValueError, match="[Ii]nfeasible"):
        restricted_decomposition({("Ca", "Ti"): -10.0},
                                 {"Ca": 0.5, "Sr": 0.5}, {"Ti": 1.0})


def synthetic_birch_murnaghan(volumes, *, v0, e0, bulk_eva3, derivative=4.2):
    """Analytic test curve, intentionally independent of ASE's implementation."""
    eta = (v0 / np.asarray(volumes)) ** (2 / 3)
    return e0 + 9 * v0 * bulk_eva3 / 16 * ((eta - 1)**3 * derivative + (eta - 1)**2 * (6 - 4 * eta))


def test_eos_recovers_known_bulk_modulus_and_is_extensive():
    v0, e0 = 260.0, -1000.0
    # Conversion derived from the SI eV definition, not imported from production.
    bulk_eva3 = 180.0 / (1.602176634e-19 / 1e-30 / 1e9)
    volumes = v0 * np.linspace(0.94, 1.06, 11)
    energies = synthetic_birch_murnaghan(volumes, v0=v0, e0=e0, bulk_eva3=bulk_eva3)
    fitted = fit_eos(volumes, energies)
    assert fitted["bulk_modulus_GPa"] == pytest.approx(180.0, rel=1e-6)
    assert fitted["eos_equilibrium_volume_A3"] == pytest.approx(v0, abs=1e-5)
    assert fitted["eos_equilibrium_energy_eV"] == pytest.approx(e0, abs=1e-7)
    assert fitted["eos_rmse_eV"] < 1e-8
    doubled = fit_eos(2 * volumes, 2 * energies)
    assert doubled["bulk_modulus_GPa"] == pytest.approx(fitted["bulk_modulus_GPa"], rel=1e-6)
    assert doubled["eos_equilibrium_volume_A3"] == pytest.approx(2 * v0, abs=1e-4)


def test_eos_rejects_unbracketed_minimum():
    volumes = np.linspace(210, 230, 11)
    energies = synthetic_birch_murnaghan(volumes, v0=260, e0=-1000, bulk_eva3=1.0)
    with pytest.raises(ValueError, match="outside"):
        fit_eos(volumes, energies)


def coupled_spring_hessian(stiffnesses):
    spring = np.diag(stiffnesses)
    return np.block([[spring, -spring], [-spring, spring]])


def forces_for_displacements(matrix, delta):
    # E = 1/2 sum_axis k_axis (r1_axis-r2_axis)^2 for the physical spring case.
    # A nonzero constant force checks that central differencing cancels the offset.
    baseline = np.array([0.12, -0.21, 0.02, -0.12, 0.21, -0.02])
    minus, plus = [], []
    for coordinate in range(6):
        displacement = np.zeros(6)
        displacement[coordinate] = delta
        minus.append((baseline + matrix @ displacement).reshape(2, 3))
        plus.append((baseline - matrix @ displacement).reshape(2, 3))
    return np.array(minus), np.array(plus)


def test_force_difference_recovers_harmonic_sign_and_coordinate_couplings():
    expected = coupled_spring_hessian([2.0, 3.0, 5.0])
    minus, plus = forces_for_displacements(expected, 0.015)
    hessian, asymmetry = force_constant_matrix(minus, plus, 0.015)
    np.testing.assert_allclose(hessian, expected, atol=1e-12)
    assert hessian[0, 3] == pytest.approx(-2.0)
    assert hessian[2, 5] == pytest.approx(-5.0)
    assert asymmetry < 1e-12


def test_nonconservative_force_derivative_is_reported_before_symmetrization():
    matrix = coupled_spring_hessian([2.0, 3.0, 5.0])
    matrix[0, 4] = 0.4
    minus, plus = forces_for_displacements(matrix, 0.01)
    hessian, asymmetry = force_constant_matrix(minus, plus, 0.01)
    assert asymmetry == pytest.approx(0.4)
    assert hessian[0, 4] == pytest.approx(0.2)
    assert hessian[4, 0] == pytest.approx(0.2)


@pytest.mark.parametrize("stiffnesses, expected", [
    ([2.0, 3.0, 5.0], [4.0, 6.0, 10.0]),
    ([-0.5, 2.0, 3.0], [-1.0, 4.0, 6.0]),
])
def test_gamma_projection_removes_only_three_translations(stiffnesses, expected):
    diagnostic = gamma_diagnostic(coupled_spring_hessian(stiffnesses), 2)
    np.testing.assert_allclose(diagnostic["gamma_curvatures_eV_A2"], expected, atol=1e-12)
    assert diagnostic["gamma_min_curvature_eV_A2"] == pytest.approx(expected[0])
    assert diagnostic["gamma_translation_residual_eV_A2"] < 1e-12


def test_gamma_reports_translation_violation_instead_of_hiding_it():
    hessian = coupled_spring_hessian([2.0, 3.0, 5.0]) + 0.7 * np.eye(6)
    diagnostic = gamma_diagnostic(hessian, 2)
    assert diagnostic["gamma_translation_residual_eV_A2"] == pytest.approx(0.7 / np.sqrt(2))
    np.testing.assert_allclose(diagnostic["gamma_curvatures_eV_A2"], [4.7, 6.7, 10.7], atol=1e-12)


@pytest.mark.parametrize("minima,expected", [([0.2, 0.201], True), ([-0.2, -0.201], False),
                                             ([-0.04, -0.041], None), ([0.2, -0.1], None)])
def test_gamma_assessment_does_not_pass_small_negative_or_step_sensitive_modes(minima, expected):
    from matterlab.physics import assess_gamma
    diagnostics = [{"gamma_min_curvature_eV_A2": minimum, "hessian_asymmetry_eV_A2": 1e-4,
                    "gamma_translation_residual_eV_A2": 1e-4} for minimum in minima]
    assert assess_gamma(diagnostics, -0.05)["gamma_test_passed"] is expected
