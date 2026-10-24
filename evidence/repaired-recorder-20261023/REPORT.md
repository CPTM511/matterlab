# Independent checkpoint resume and repaired-recorder validation

The isolated invocation successfully resumed from the public GitHub checkpoint and completed exactly one real 20-atom CaTiO3 CHGNet single-point evaluation. The repaired recorder captured all required observations. Numerical replay against both original onboarding baselines **failed** the unchanged force and stress tolerances. The new energy, forces and stress exactly equal the earlier restored observation. No second evaluation, backend experiment, relaxation, research campaign, publication or schedule change was performed.

| Outcome | Result |
|---|---|
| Independent GitHub-backed checkpoint resume | Verified for this invocation |
| Repaired recorder capture and integrity | Passed |
| Numerical acceptance against original baselines | Failed |
| Exact match to the previous restored observation | Passed for energy, every force component and every stress component |
| Full migration | Incomplete; non-overlapping local fallback retained |

## Public source and environment independence

A fresh unauthenticated clone of `https://github.com/CPTM511/matterlab` was checked out at `2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1`. Its immediate parent is the required coordination commit `f1fdd7fbe07b05c60cb2c15f808ddaa6c13a06bb`. The public main branch still pointed to the requested checkpoint at preflight, immediately before launch and final preservation checks. Git status was clean. All 446 publication-manifest entries passed; the sole tracked file outside its entries is the manifest itself. Manifest SHA256 is `dc15e4f699346755bb2c12cfb8bb4d36c648827fee23c8f509528636263e808c`; audit SHA256 is `2736cf96d41380a71ac08ef40ff2eb13a4a2aaa6df391895c3e0f499df114bcd`. The published audit's broader historical checks are reported claims; this invocation independently recomputed the complete publication hashes.

AGENTS.md, OPERATIONS.md, STATE.json, diagnosis checkpoint and CLOUD_START.md were read from that clone. CLOUD_START.md explicitly identifies itself as a **new explicit startup instruction**, not the recovered historical `start_skill`. Current STATE reports no active physical job. Local process inspection found no other physical calculation; the parent's assignment supplies current cloud ownership. Older handoff prose contains stale scheduled-wake statements; current STATE and the parent evidence take precedence. This invocation did not independently inspect the scheduler or attest another scheduled wake.

All scientific references, inputs, configuration and instructions came from the public clone. No owner computer, private local history, old task evidence directory or credentials supplied scientific evidence. The preexisting project checkout was inspected only for Git status; its existing virtual environment supplied permitted packages and cached models. Those were hash checked before use. No package was installed or upgraded. The selected environment was provided as a separate isolated native cloud invocation; this report does not independently attest the environment-publication backend.

Preflight passed 506 checks, including eight loaded project source digests against `replay/code.json` and the physics commit `3319dc595397f68c0e7a3326e64c2b27ae799027`, the Python executable, 20 CHGNet Python source files, all saved dependency versions, all three cached checkpoint hashes, raw input/configuration hashes and semantic configuration equality. The active CHGNet 0.3.0 checkpoint hash is `d14ab7c0f093efe64b60a7bcd540bca10e74fb7f46c86108a079af60524659d1`. Every imported matterlab module used by the evaluation resolves under the verified source checkout; `__main__` was hash checked but not imported because importing it executes the CLI.

An additional 15,077 installed file digests matched local RECORD metadata across CHGNet, PyTorch, NumPy, SciPy, ASE and pymatgen. Native-library hashes were saved. This is installed-file consistency, not independent supply-chain attestation or a match to unavailable historical native-library hashes. `pip check` reported no broken requirements.

## Frozen condition and actual execution

`protocol.json` was frozen before inference with SHA256 `c7dc58e056588a9fb3a0edb6ff4f0d6dbb50961e33332a08b7120b36070dcb37`. It specifies one evaluation, a 600-second calculation-process timeout, no retries, original thresholds, capture/integrity criteria and stop conditions. The published proposed recorder and capture helper were executed unchanged. A single-use exclusive launch token prevents accidental second launch. Python and NumPy seeds were explicitly set to 20261024; the verified calculator sets PyTorch's seed to 20261024. Python hash seed was also fixed.

The new condition wraps the actual bound model `forward` and the structure's consumed `get_neighbor_list` return. The installed converter source directly consumes this query. Unlike D1, the model capture is not a module forward hook. Explicit inter-op count one and the fixed auxiliary seeds make this a new declared condition; it does not retroactively repair D1.

Actual runtime: Linux x86_64, Python 3.12.14, CHGNet package 0.4.2/model 0.3.0, PyTorch 2.6.0+cpu, NumPy 2.2.6, ASE 3.26.0 and pymatgen 2025.6.14. The in-process record reports CPU device, float32 parameters, AVX512 capability, fast graph construction, CPU affinity `[0]`, PyTorch intra-op/inter-op threads both one, deterministic algorithms enabled, MKLDNN enabled and highest float32 matmul precision. OMP/MKL/OpenBLAS/NumExpr/VECLIB controls were one; BLIS was also set to one by the launcher. Native-library pool counts beyond PyTorch were not separately interrogated inside inference. ATEN_CPU_CAPABILITY and MKL_CBWR were unset, and no backend contrast was run.

The process ran from 2026-10-23T19:07:46.898886Z to 19:07:51.073128Z, returned zero, and used **4.174238583 seconds** wall time. The recorder's interval around ASE energy/force/stress retrieval was **0.146995120 seconds**. The graph and model counters are each exactly one; cached ASE getters did not cause additional inference. Matplotlib/fontconfig emitted cache-location warnings, including a read-only default directory and a temporary-cache fallback. They are retained in the log; no evaluator exception or timeout was reported. No retry was made for these warnings.

Requested agent settings were GPT-6 Astra, High reasoning and Standard speed. Observable developer identity describes GPT-6-based Codex; the actual variant, reasoning setting and service tier are not independently attested. The parent supplied the startup included-usage gate. This instance has no independently refreshed account read or billing enforcement; account evidence is retained only privately. No paid API, rental, credential operation or billing/security change was invoked. Hard-coded historical provenance fields about API calls and paid compute are declarations, not metering.

## Raw capture and numerical decision

`R1/` contains the exact CIF and raw configuration, ASE/Pymatgen input arrays, the actual consumed neighbor list, eight graph arrays, all six returned model tensor arrays, model parameter hashes, ASE observations, code expectations, provenance, runtime settings, recorder/helper source, array hashes and the recorder manifest. All arrays are nonempty and finite. Each shape, dtype and data digest was independently recomputed after execution. The model returned `atoms_per_graph`, `m_0`, `crystal_fea`, `f_0`, `s_0` and `e` tensors.

The consumed neighbor list has 1,318 directed entries. Its center/neighbor pairs and images exactly match the corresponding graph arrays. The graph has 659 undirected links and a 1,924-by-5 bond graph. Direct arithmetic on saved positions, images and cell reproduces neighbor distances with maximum residual `1.7763568394002505e-15 Angstrom`; this sanity calculation makes no new neighbor query. CHGNet's float32 energy scaling, force values and GPa-to-ASE stress conversion (including ASE symmetrization) exactly reproduce the saved ASE observations.

All new input, neighbor and graph arrays match the available D1 captures exactly, and all recorded model parameter hashes match. D1's neighbors came from a separate query, while this run intercepted the consumed query. This comparison supplies neither historical onboarding graphs nor D1's missing energy, force and stress values.

| Quantity | New observation / maximum difference from either original baseline | Original absolute tolerance | Acceptance |
|---|---|---|---|
| Total energy | `-166.1494140625 eV`; difference `0 eV` | `1e-5 eV` | Pass |
| Forces | maximum absolute difference `3.039836883544922e-5 eV/Angstrom` | `1e-6 eV/Angstrom` | Fail |
| Stress | maximum absolute difference `5.364418029785156e-7 eV/Angstrom^3` | `1e-7 eV/Angstrom^3` | Fail |

Relative tolerance is zero for every comparison. `comparisons.json` preserves every signed component as **new minus reference**, for baseline-001, baseline-002 and the prior restored replay. All three quantities exactly match the prior replay. `D1-capture-comparison.json` retains signed raw-array differences; D1 numerical comparison is explicitly unavailable, not an empty comparison reported as zero. `model-ASE-consistency.json` preserves all conversion differences.

The numerical mismatch triggers the protocol stop. There is no subsequent inference, backend experiment or campaign. Original restored force/stress acceptance remains failed, and D1 remains an instrumentation failure with missing numerical values. Matching the restored result under the new recorder does not identify the cause of the historical drift or establish general repeatability across platforms.

## Review, preservation and handoff

A separate standard-library Decimal/scalar implementation independently recomputed all 210 signed observable components, maxima and threshold decisions, agreeing with the NumPy analysis. It imports no numerical model. `sanity-review.json` records this computational cross-check. This is not an independent human reviewer or separately attested reviewer agent; external parent review remains pending. Saved-array graph/neighbor checks and model-to-ASE checks add independent arithmetic integrity evidence without another physical evaluation.

Final verification reconfirmed all 446 original publication entries and a clean checkpoint checkout. No original scientific evidence or coordination record was changed. `proposed-STATE.json` is a separate review proposal preserving all existing coordination fields, leaving full migration false and adding the new bounded outcome. `resume-checkpoint.json` gives the next exact action. Local fallback remains retained without overlap; schedules were not inspected or changed in this task.

The additive export is intended for `evidence/repaired-recorder-20261023/` after parent review. It retains every raw scientific observation and signed difference, source snapshots, applicable dependency licenses, reference observations and portable analysis helpers. `transformation-ledger.json` links each exported file to its private original hash and records path sanitation and manifest regeneration. Public derivative hashes are in the new manifest; historical/private source hashes remain provenance and must not be used as the current derivative manifest. Private account and process records and scripts embedding account evidence are excluded. Original private bytes and hashes are retained. No export was published or pushed.

The remaining blocker is numerical acceptance against the original baselines. A later diagnostic requires a separately declared discriminating condition, fresh included-usage and ownership gates, and explicit separation from this completed protocol. The result is an ML-potential runtime/recorder validation, not DFT, synthesis, material stability, novelty or application evidence. Independent GitHub-backed resume has been demonstrated here; full migration is not complete.
