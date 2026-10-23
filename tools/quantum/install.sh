#!/usr/bin/env bash
# Free project-local macOS Apple Silicon Quantum ESPRESSO installation.
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT="$PWD"
mkdir -p .tools/bin .tools/pseudo runs/quantum
if [[ ! -x .tools/bin/micromamba ]]; then
  curl -fLsS --retry 2 https://micro.mamba.pm/api/micromamba/osx-arm64/latest -o .tools/micromamba.tar.bz2
  tar -xjf .tools/micromamba.tar.bz2 -C .tools bin/micromamba
fi
export MAMBA_ROOT_PREFIX="$ROOT/.tools/mamba-root"
export CONDA_PKGS_DIRS="$ROOT/.tools/mamba-root/pkgs"
if [[ -f tools/quantum/conda-explicit-openmpi-osx-arm64.txt ]]; then
  .tools/bin/micromamba create -y --no-rc -p "$ROOT/.tools/qe-openmpi" --file tools/quantum/conda-explicit-openmpi-osx-arm64.txt
else
  .tools/bin/micromamba create -y --no-rc -p "$ROOT/.tools/qe-openmpi" -c conda-forge 'qe=7.6' 'mpi=1.0=openmpi'
fi
.tools/bin/micromamba env export -p "$ROOT/.tools/qe-openmpi" --explicit > tools/quantum/conda-explicit-openmpi-osx-arm64.txt
for pseudo in Ca.pbe-spn-kjpaw_psl.1.0.0.UPF Ti.pbe-spn-kjpaw_psl.1.0.0.UPF O.pbe-n-kjpaw_psl.1.0.0.UPF; do
  curl -fLsS --retry 2 "https://pseudopotentials.quantum-espresso.org/upf_files/$pseudo" -o ".tools/pseudo/$pseudo"
done
if [[ -f tools/quantum/pseudopotentials.sha256 ]]; then
  shasum -a 256 -c tools/quantum/pseudopotentials.sha256
else
  shasum -a 256 .tools/pseudo/*.UPF > tools/quantum/pseudopotentials.sha256
fi
shasum -a 256 .tools/bin/micromamba .tools/qe-openmpi/bin/pw.x > tools/quantum/executables.sha256
