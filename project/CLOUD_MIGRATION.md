# Cloud continuation: readiness and acceptance

Updated 2026-10-24, Asia/Shanghai.

## Requested outcome

Continue MatterLab while the owner's computer is off, using GPT-6 Astra and only the included allowance of the existing ChatGPT Pro subscription, with no additional spending. All deliverables remain English. This request authorizes free native cloud execution and supersedes the former local-only runtime preference. Scientific acceptance and evidence preservation do not change.

## Verified facts

- Official OpenAI documentation says Codex Cloud runs commands in isolated cloud workspaces and continues while the owner's computer sleeps. Environments must be prepared, tested and published for reuse. [Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
- Official documentation describes dots as Astra-powered cloud agents for ongoing work. Availability is subject to rollout. Work/Codex tasks managed by a dot use the relevant product allowance. A dot's local-computer connection is optional. [Dots](https://learn.chatgpt.com/docs/dots)
- Local and cloud Codex work share plan usage. API use is separately charged. This project must not add an API-key route or consume extra credits. [Pricing](https://learn.chatgpt.com/docs/pricing)
- The signed-in web scheduler exposed GPT-6 Astra, High reasoning, and a four-hour interval in China Standard Time. However, task-list and schedule-option loading failed. Selecting Create returned no verified success state or task identifier. Activation is therefore unconfirmed; inspect the hosted task list before any further creation attempt to prevent duplicates.

The English instructions are saved in [CLOUD_HANDOFF.md](CLOUD_HANDOFF.md). On 2026-10-24 the owner explicitly authorized handing them to the existing cloud assistant under the strict zero-additional-fee boundary. Delivery and acknowledgement were verified in the signed-in interface. The assistant accepted the quota, runtime and durable-resume checks before migration acceptance. Requested settings are GPT-6 Astra, High reasoning and an approximately four-hour cadence in Asia/Shanghai; actual runtime and recurrence still require evidence.

The existing local heartbeat remains active as a fallback. Do not overlap cloud and local calculations; check current responsibility and repository state first. A subsequent signed-in hosted-task inventory and a MatterLab search both returned no matching task; the cloud assistant must still inspect current state before adding recurrence.

## Cloud onboarding validation

A dedicated native cloud setup task checked out the public repository at `3319dc595397f68c0e7a3326e64c2b27ae799027`. Its returned task metadata identifies a durable cloud host, and command output identifies a Linux workspace. The setup installed Python 3.12.14, CPU PyTorch 2.6.0 and CHGNet 0.4.2/model 0.3.0. All 34 existing tests and 301 historical evidence checks passed; historical evidence was copied before verification to avoid modification.

Two real single-point evaluations of the initial 20-atom CaTiO3 reference returned `-166.1494140625 eV`, with identical energies, forces and stresses on the same cloud instance. All 16 manifest entries in each evaluation verified. This is runtime validation, not candidate DFT, material stability, novelty, synthesis or application validation. Raw evidence, resolved dependencies, helper code and the report are retained in the private cloud environment; they are not yet part of the public release.

The interface initially started setup with its default GPT-6.1 Sol Light. The model selector was subsequently changed to GPT-6 Astra High. The setup agent could not independently attest variant/effort metadata, so the original setup must not be described as verified Astra-only execution.

The dedicated private environment is published. A subsequent hosted task restored the helper and both baseline evidence directories, verified their manifests and ran a new real evaluation. Energy matched exactly, but maximum force and stress differences of `3.03984e-5 eV/A` and `5.36442e-7 eV/A^3` failed the predeclared `1e-6 eV/A` and `1e-7 eV/A^3` tolerances. All observations were finite. The original failed comparison and signed differences are retained; no tolerance was widened. The cloud coordinator will compare hardware/backend settings and graph/input ordering before a predeclared discriminating test. Filesystem restoration and actual execution are demonstrated; numerical replay acceptance and complete migration are not.

Exactly one active hosted task named **MatterLab cloud research** was verified in the signed-in Scheduled interface: every four hours, China Standard Time, no end date, with its first displayed wake at 2026-10-24 02:40. Its stored instructions require fresh included-usage checks, zero extra credits/overage, English delivery, an explicit Astra High request for delegated work, preserved failures and overlap prevention. The actual first scheduled wake remains unverified. The schedule editor did not expose an independently verifiable controller model; the task's text is not proof of a runtime parameter. The existing cloud restoration task was launched with an explicit Astra High request. Local fallback stays available while acceptance is incomplete and must not duplicate active cloud work.

The signed-in web route `https://chatgpt.com/settings/usage?tab=overview` exposed an included-plan usage indicator. The cloud assistant has been given that read-only route for later checks. A local snapshot is not continuing billing enforcement; if the route cannot be verified from the cloud, substantial work must defer. Account-specific usage records stay out of public artifacts.

## Migration acceptance

1. Confirm an active native hosted task or cloud agent responsibility, its actual model, recurrence, repository access and included-usage availability. A visible model picker alone is insufficient.
2. Prepare a cloud-only runtime from the public English repository. Do not mount or call the owner's local computer, transfer subscription credentials, or depend on the local virtual environment.
3. Execute a real bounded physical calculation in a new run directory. Record actual environment, code/model hashes, inputs, raw outputs, convergence state and failures. Do not treat same-platform replay requirements as cross-platform physical validation or weaken checks to accommodate differences.
4. Persist a verifiable checkpoint and evidence in an authorized durable cloud location, then resume from that checkpoint in a subsequent hosted run without local files. Test the publication audit on the exported results.
5. Only after successful cloud continuation is verified, pause the local heartbeat to prevent duplicate work. Preserve the repository as the durable coordination source.

## Cost and resource gates

Use native subscription-included cloud capabilities only after verifying availability. Before substantial model work, check included allowance; defer if unavailable or at the recorded reserve threshold. Prompts are operating constraints, not billing controls. Do not change billing settings, purchase credits, use existing extra credits/overage, upgrade a plan, rent servers, or create paid API clients. If required computation cannot fit the available free/included runtime, checkpoint and report the concrete limitation.

Public GitHub Actions standard runners offer free runtime, but artifact storage and larger runners have distinct billing rules. They are not a substitute for Astra reasoning. No Actions research schedule has been enabled as part of this migration. [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
