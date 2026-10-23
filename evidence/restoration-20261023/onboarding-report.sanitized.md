# MatterLab cloud onboarding evidence

Prepared during onboarding; original timestamp retained in private evidence. Current instance is ready for publication review; not yet published or verified in a subsequent task.

## Runtime and scope

- Actual execution: native cloud Linux x86_64, Python 3.12.14, virtual environment CHECKOUT/.venv, PyTorch 2.6.0+cpu, CHGNet package 0.4.2, pretrained CHGNet model 0.3.0, one CPU thread.
- Source HEAD: 3319dc595397f68c0e7a3326e64c2b27ae799027. Tracked and untracked Git status remained clean.
- Assistant system identity: GPT-6-based Codex. The tools did not expose authoritative Astra variant or High reasoning metadata, nor a model-switch operation. No delegation or model API was used. Selected Astra/High cannot be independently attested.

## Verified results

- All 34 existing tests passed (22 scientific tests and 12 publication guards), with five existing warnings, no failed/skipped tests.
- pip check passed; repository dependencies installed at declared versions. Resolved transitive dependencies saved in requirements-linux-cpu.txt.
- Historical round-001-en was copied before verification to avoid changing prior evidence. All 301 integrity and metric-recomputation checks passed.
- CLI generation produced 27 symmetry-distinct decorations and selected six candidates; output is generated-smoke.
- Dashboard returned HTML and the 15-record evidence summary, and denied source-file access with HTTP 404. Validation server was stopped after checks. No live process is assumed to survive publication.
- Two independent real single-point evaluations on the saved initial 20-atom CaTiO3 reference completed: energy -166.1494140625 eV; all forces and stresses finite and exactly equal across same-instance repeats. No relaxation, research campaign, DFT or scientific acceptance claim.
- Each evaluation directory contains raw CIF, raw observations, configuration, source snapshot, package versions, model checkpoint SHA256, code SHA256, manifest and checkpoint. All 16 manifest entries per run verified. See replay-comparison.json.
- The complete saved install script was executed successfully a second time.

No required check failed. The first evaluation emitted writable-cache warnings; preserved in evaluation-001.log. Explicit writable Matplotlib/XDG cache directories removed those warnings on the second evaluation. A pip cache warning during initial installation did not affect dependency integrity. TLS/checksum verification was never disabled.

## Persistence and continuation

Saved configuration draft fields: install_script and start_skill. No secret, network, repository-membership or billing changes. Saving does not publish. Review and save the draft in environment settings, then publish the environment to snapshot this runtime and the ONBOARDING evidence/helper directory.

The helper directory is outside the Git checkout and relies on the environment snapshot for persistence. It has not been pushed to GitHub. A new hosted task must verify that it was restored. Its manifest.json covers the helper files, logs and evaluation evidence.

From CHECKOUT, set XDG_CACHE_HOME=CHECKOUT/.cache and MPLCONFIGDIR=CHECKOUT/.cache/matplotlib, create the directories, then use .venv/bin/python ONBOARDING/evaluate.py NEW_ABSOLUTE_OUTPUT_DIRECTORY to replay one bounded evaluation. The output directory must be new. Check baseline manifests and checkpoint first; compare new energy, forces and stress with baseline observations. Refresh dependencies with bash ONBOARDING/install.sh if needed. For dashboard use .venv/bin/matterlab serve --port 8877 and validate local responses. The saved start_skill includes the detailed checks.

This does not establish durable cross-task resume, publication, the cloud assistant activation, recurring scheduling, or cloud migration completion. Do not resume a historical macOS campaign under this Linux environment: source/environment drift checks must remain intact. Quantum ESPRESSO and candidate DFT were not installed or tested. Keep the local fallback until migration acceptance is independently met, and coordinate responsibility before research starts. No message was sent to the cloud assistant; this report and saved startup instructions provide the handoff after publication.
