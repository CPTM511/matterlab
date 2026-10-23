"""Explicit, seeded crystal generation. No database entries masquerade as discoveries."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import spglib
from ase import Atoms
from ase.build import make_supercell
from ase.geometry import find_mic
from ase.io import write


def parent_cell(matrix, lattice=4.05):
    if np.asarray(matrix).shape != (3, 3) or not np.equal(matrix, np.rint(matrix)).all():
        raise ValueError("Supercell must be a 3x3 integer matrix")
    if round(np.linalg.det(matrix)) != 4:
        raise ValueError("This generator requires a positive determinant-four supercell")
    primitive = Atoms("CaTiO3", scaled_positions=[(0, 0, 0), (.5, .5, .5),
                      (.5, .5, 0), (.5, 0, .5), (0, .5, .5)],
                      cell=np.eye(3) * lattice, pbc=True)
    return make_supercell(primitive, np.asarray(matrix, dtype=int))


def symmetry_permutations(atoms, tolerance=1e-5):
    positions = atoms.get_scaled_positions(wrap=True)
    sym = spglib.get_symmetry((atoms.cell.array, positions, atoms.numbers), symprec=tolerance)
    permutations = []
    for rotation, translation in zip(sym["rotations"], sym["translations"]):
        moved = positions @ rotation.T + translation
        delta = moved[:, None, :] - positions[None, :, :]
        delta -= np.rint(delta)
        distance = np.linalg.norm(delta @ atoms.cell.array, axis=-1)
        distance[atoms.numbers[:, None] != atoms.numbers[None, :]] = np.inf
        permutation = np.argmin(distance, axis=1)
        if np.max(distance[np.arange(len(atoms)), permutation]) > tolerance:
            raise ValueError("Invalid symmetry mapping")
        if len(set(permutation)) != len(atoms):
            raise ValueError("Symmetry mapping must be a bijection")
        permutations.append(permutation)
    return permutations


def canonical_decoration(symbols, permutations):
    return min(tuple(symbols[i] for i in p) for p in permutations)


def occupations(counts):
    items = [element for element, count in sorted(counts.items()) for _ in range(count)]
    return sorted(set(itertools.permutations(items)))


def cell_formula(composition, config):
    result = ""
    for site, elements in [("A", config["a_elements"]), ("B", config["b_elements"])]:
        for element in elements:
            n = composition[site].get(element, 0)
            if n:
                result += element + (str(n) if n != 1 else "")
    return result + "O12"


def perturb(atoms, seed, amplitude, lattice):
    """Seed both an anti-phase tilt and general displacements, without imposing symmetry."""
    result = atoms.copy()
    b_ids = [i for i, s in enumerate(atoms.symbols) if s in {"Ti", "Zr", "Sn"}]
    for i, symbol in enumerate(atoms.symbols):
        if symbol != "O":
            continue
        displacement, distances = find_mic(atoms.positions[i] - atoms.positions[b_ids], atoms.cell, pbc=True)
        nearest = np.flatnonzero(distances < .6 * lattice)
        increments = []
        for k in nearest:
            site = np.floor(atoms.positions[b_ids[k]] / lattice + 1e-5).astype(int)
            rotation = np.array([.07, .07, .05]) * (-1.0) ** int(site.sum())
            increments.append(np.cross(rotation, displacement[k]))
        if increments:
            result.positions[i] += np.mean(increments, axis=0)
    rng = np.random.default_rng(seed)
    offsets = rng.normal(0, amplitude, size=(len(result), 3))
    offsets -= offsets.mean(axis=0)
    result.positions += offsets
    result.wrap()
    return result


def validate_structure(atoms):
    if not np.isfinite(atoms.positions).all() or not np.isfinite(atoms.cell.array).all():
        raise ValueError("Nonfinite structure")
    if atoms.get_volume() <= 0:
        raise ValueError("Nonpositive volume")
    symbols = atoms.get_chemical_symbols()
    a = sum(s in {"Ca", "Sr", "Ba"} for s in symbols)
    b = sum(s in {"Ti", "Zr", "Sn"} for s in symbols)
    o = symbols.count("O")
    if not (a == b and o == 3 * a and len(symbols) == a + b + o):
        raise ValueError("Candidate violates charge-balanced ABO3 stoichiometry")
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    if d.min() < 1.0:
        raise ValueError("Atomic overlap below 1 angstrom")


def generate(config, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    lattice = 4.05  # initialization only, never a measured result
    parent = parent_cell(config["supercell"], lattice)
    permutations = symmetry_permutations(parent)
    a_ids = np.flatnonzero(parent.numbers == 20)
    b_ids = np.flatnonzero(parent.numbers == 22)
    if len(a_ids) != 4:
        raise ValueError("This generator currently requires four ABO3 formula units")
    records = []
    totals = []
    for group_index, composition in enumerate(config["compositions"]):
        if any(type(n) is not int or n < 0 for site in ("A", "B") for n in composition[site].values()):
            raise ValueError("Sublattice counts must be nonnegative integers")
        if sum(composition["A"].values()) != 4 or sum(composition["B"].values()) != 4:
            raise ValueError("Both sublattice occupations must sum to four")
        if not set(composition["A"]) <= set(config["a_elements"]) or not set(composition["B"]) <= set(config["b_elements"]):
            raise ValueError("Unsupported elements")
        unique = {}
        raw_count = 0
        for a_occ, b_occ in itertools.product(occupations(composition["A"]), occupations(composition["B"])):
            raw_count += 1
            symbols = parent.get_chemical_symbols()
            for indices, occ in [(a_ids, a_occ), (b_ids, b_occ)]:
                for index, element in zip(indices, occ):
                    symbols[index] = element
            key = canonical_decoration(symbols, permutations)
            unique.setdefault(key, symbols)
        keys = sorted(unique)
        rng = np.random.default_rng(config["seed"] + group_index)
        selected = set(rng.choice(len(keys), min(len(keys), config["orderings_per_composition"]), replace=False).tolist())
        for index, key in enumerate(keys):
            candidate_id = f"C{group_index + 1:02d}-{index + 1:03d}"
            atoms = parent.copy()
            atoms.set_chemical_symbols(unique[key])
            seed = config["seed"] + group_index * 1000 + index
            atoms = perturb(atoms, seed, config["initial_displacement_A"], lattice)
            validate_structure(atoms)
            write(directory / f"{candidate_id}.cif", atoms)
            records.append({"id": candidate_id, "kind": "candidate", "formula": cell_formula(composition, config),
                            "composition": composition, "seed": seed, "selected": index in selected,
                            "input_cif": f"generated/{candidate_id}.cif", "canonical_symbols": list(key)})
        totals.append({"composition": composition, "raw_decorations": raw_count, "symmetry_unique": len(keys), "selected": len(selected)})
    for a, b in itertools.product(config["a_elements"], config["b_elements"]):
        atoms = parent.copy()
        symbols = atoms.get_chemical_symbols()
        for i in a_ids:
            symbols[i] = a
        for i in b_ids:
            symbols[i] = b
        atoms.set_chemical_symbols(symbols)
        seed = config["seed"] + 10000 + len(records)
        atoms = perturb(atoms, seed, config["initial_displacement_A"], lattice)
        validate_structure(atoms)
        rid = f"R-{a}{b}O3"
        write(directory / f"{rid}.cif", atoms)
        records.append({"id": rid, "kind": "reference", "formula": f"{a}{b}O3",
                        "composition": {"A": {a: 4}, "B": {b: 4}}, "seed": seed, "selected": True,
                        "input_cif": f"generated/{rid}.cif"})
    result = {"seed": config["seed"], "symmetry_operations": len(permutations), "symprec_A": 1e-5,
              "selection": "seeded sampling without replacement from exact parent-symmetry representatives",
              "groups": totals, "structures": records}
    (directory / "generation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
