# Third-party software and evidence sources

Checked 2026-10-24. This project licenses only its original code under MIT. Installed binaries, checkpoints and externally acquired data retain their licenses. They are not committed with the source code.

| Component | Role | Authoritative source |
|---|---|---|
| CHGNet 0.4.2 / checkpoint 0.3.0 | Local energies, forces and stresses | https://github.com/CederGroupHub/chgnet and its LICENSE |
| ASE | Structures, optimization, trajectories and EOS | https://ase-lib.org/ |
| pymatgen / spglib | Material representations / symmetry | https://pymatgen.org/ ; https://spglib.github.io/spglib/ |
| NumPy / SciPy | Arrays, linear programming and numerical analysis | https://numpy.org/ ; https://scipy.org/ |
| Quantum ESPRESSO | Separate first-principles verification where actually run | https://www.quantum-espresso.org/ |
| PSlibrary pseudopotentials | Separate DFT inputs, licensed by their providers | See tools/quantum and raw downloaded UPF headers |
| Related six-cation ceramic study | Prior art and use hypotheses, not candidate validation | https://doi.org/10.1016/j.ceramint.2023.11.388 |
| CHGNet paper | Model provenance | https://doi.org/10.1038/s42256-023-00716-3 |
| Systematic ML-potential softening | Known limitation | https://doi.org/10.1038/s41524-024-01500-6 |

All raw simulation outputs in this project were produced locally. No Materials Project private API key or paid database is required. Public papers and pretrained model data can overlap, so calibration against known compounds is not an independent out-of-distribution benchmark. Newly created CIF coordinates do not establish novel chemistry.
