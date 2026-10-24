# Independent saved-evidence review of completed P1

The saved evidence supports the frozen result **H1_exact_pairwise_repeat**. P1 reproduces all six C1 model-output tensors byte-for-byte and all ASE observations exactly, with matching input, neighbor, graph, parameter-hash and complete primary runtime records except the declared condition label. The execution/resource gate also passes. **Original baseline force/stress acceptance remains failed.** The earlier C1 gate remains failed, C2 remains unrun, and full migration remains incomplete.

No new model evaluation was performed in this review. No raw, frozen, report, export or archive file was changed. The executing role's earlier verification was treated as evidence to inspect, not as this independent review.

## Exact identities and verification boundary

| Artifact | SHA256 |
|---|---|
| English protocol | `8818e943d53d64884c9ed0ad7e7b35836627fb9cb611ec92e7a9c9dbcfc442c7` |
| Machine protocol | `65edd51f107018e757b920fcc339789373b1dbba498bd2f71aef7423d41d6d7f` |
| Implementation manifest | `7e4b3630e23d721486a59d6342fd303b25eeaab1dea4d1faf525f89696c42c7f` |
| Frozen controller | `96c528df9dea67d6185e2f04eb60ff47cddd05083f4dd2a3929a16e196d83380` |
| Guarded recorder | `530bedca0d338401a8f3821fb21f98bb3569f26f6f1efe2f612d07ba0e052419` |
| Freeze envelope | `fd475de8179f83f4cb71ffe7a8449ec43f72e7db20d501fe50354b87515ce1b9` |
| Frozen final decision | `a3ddfe9689245d9d718146ad9db5478bcad48e9873d11839c75b36cdd6ee6ce9` |
| Unchanged result REPORT.md | `df58b4ed9bbdb1ae9bf70a75ad6d15b0d8a2fb1b4a74390805e68977a2e9dfb0` |

The result report is exactly **9,792 bytes and 9,792 characters**. Its complete text has been delivered separately; this review does not replace or edit it.

Scientific references are the local public checkout pinned to `91147ff73336ce205717117b2ab7de3e62c5fdb1`. I independently recomputed its 642 manifest entries, all 12 frozen implementation entries, the freeze bindings, recorded project-source hashes, and equality of the raw/export implementation snapshots to the frozen files. The recorded physics source remains `3319dc595397f68c0e7a3326e64c2b27ae799027`. The raw recorder and helper match their frozen identities.

I used separately written verification code with NumPy and ASE units for saved-data arithmetic. I did not execute the frozen analyzer/controller, construct a model, load model weights for inference, run a forward call, install software, access an account or remote service, publish, change schedules or delegate work. The executing role's 1,498 preflight checks and 120 capture/integrity checks are retained records; their counts and all-pass state were verified, but installed-environment preflight was not rerun in this review.

## Independent numerical and capture verification

The independent pass performed **1,427 checks: 1,426 passed, and one overly strict reviewer assertion failed**. That failed first-pass artifact is preserved unchanged. Its narrow correction is explained below; it is not a failed frozen P1 check. No evidence defect was found after resolving that distinction.

The checks independently established:

- Complete raw controller-manifest coverage of **53 entries**, recorder coverage of **19 entries**, export coverage of **54 entries**, and matching exported recorder coverage of 19 entries. Every listed digest verified, with no omitted or additional file in those scopes apart from each manifest itself.
- Recomputed data hashes, shapes, dtypes and finiteness for **96 saved arrays containing 106,000 elements** across P1, C1, C0 and R1. All P1 input, consumed-neighbor and graph arrays separately match their corresponding C1 arrays in dtype, shape and bytes.
- Exact bytes for all six C1 output tensors: `atoms_per_graph`, `m_0`, `crystal_fea`, `e`, `f_0` and `s_0`. Raw CIF/configuration and the complete **136-entry parameter-hash record** match C1. Parameter tensors themselves are not included; I verified the stored hash records, not a new rehash of loaded model weights.
- The complete P1/C1 runtime record differs only in `condition`. The full build string matches, including one canonical NO AVX capability line. CPU affinity, seeds, thread settings, device and capability agree with the recorded condition. No build-description line was excluded from the primary comparison.
- Exact float32 model-to-ASE conversion: energy is multiplied by 20 before conversion to Python float; stress is multiplied by ASE `units.GPa` before float32 symmetrization. The resulting energy, 60 force components and nine stress components match saved ASE values exactly. This calculation did not upcast the model tensors prematurely.
- Recomputed **all 420 signed ASE-reference components** across six references and **all 79,500 signed array-reference components** across 72 array comparisons, not merely their maxima. Shapes, dtypes, exact equality, numerical equality and unchanged tolerance decisions were also checked. The 70 model-to-ASE comparison components were checked separately. D1 remains explicitly unavailable.

Energy is `-166.1494140625 eV`. Maximum absolute ASE differences are:

| Reference | Energy (eV) | Force (eV/Angstrom) | Stress (eV/Angstrom^3) |
|---|---:|---:|---:|
| C1 | 0 | 0 | 0 |
| C0, R1, restored replay | 0 | `5.1021575927734375e-5` | `5.736947059631348e-7` |
| Either original baseline | 0 | `3.4332275390625e-5` | `4.4249463826417923e-7` |

Both original baselines still fail force and stress acceptance under unchanged absolute tolerances `1e-5 eV`, `1e-6 eV/Angstrom` and `1e-7 eV/Angstrom^3`, with `rtol=0`. Exact C1 repeatability does not replace that classification.

## Preserved reviewer assertion failure

My first verifier incorrectly required raw byte/dtype equality between consumed neighbor-index pairs and the graph's index representation. The neighbors are int64; `atom_graph` is int32. Their values already matched exactly.

The saved public converter explicitly constructs `atom_graph` with `torch.int32`. The frozen analyzer checks the index value relation with `np.array_equal`; it does not require cross-representation byte equality. A separate, narrowly scoped check confirmed that all indices are in 0..19, the int64-to-int32 conversion is lossless, graph bytes match after this declared conversion, and neighbor images match after the declared float32 conversion.

This corrects a reviewer assumption, not an experimental result or acceptance rule. Every mandatory P1/C1 comparison between corresponding captures remains exact in its own dtype, shape and bytes. The first failed check remains in `verification.json`; `cross-representation-clarification.json` records the explanation, source hashes and four passing relation checks. Neither the frozen gate nor any original evidence was rewritten.

## Attempts, execution and frozen decision

The retained protocol-level exclusive marker matches the frozen protocol and the actual raw output location. The separate inference marker permits one evaluation. The saved execution record reports one attempt, and the capture counters report exactly one graph conversion and one forward. These records, matching frozen source and successful guard path support one recorded authorized invocation; they are not a universal forensic proof against unlogged machine activity.

The calculation process returned 0 with no timeout or recorded exception. Its wall time was **4.427294630000688 seconds**, below the frozen 594-second timeout and 600-second process limit. The nested recorder interval was **0.2636702060008247 seconds**, a different timing scope. Metadata preflight took **3.1703699760000745 seconds** and saved-data analysis **0.21436207999795442 seconds**, both returning 0. Recorded phases are chronologically ordered.

At the final controller decision, investigation elapsed time was **65.134202 seconds**, below 1,800 seconds. The completion record reports **340.674275 seconds through subsequent reporting**, also below that limit; its timestamps reproduce that elapsed value exactly.

I independently reconstructed the final process/resource eligibility from the saved records and compared the resulting decision with the frozen final decision. They agree: H1 passes, original baseline acceptance is false, old C1 stays failed, C2 stays unrun and migration stays incomplete. The separately retained analysis decision is consistent. No recorder, controller or analyzer failure record is present.

Private release/account records were verified by digest as part of the complete raw manifest, without inspecting their account fields or querying an account. Parent authority and fallback/scheduler non-overlap remain parent attestations. I did not independently inspect another host, live remote coordination or historical process activity. The freeze envelope's pre-execution status fields describe its earlier creation time; they are not a new release or a claim that this completed evaluation remains unexecuted.

## Logged cache messages

The raw calculation log contains a failed write to the default Matplotlib configuration directory on a read-only filesystem, creation of a temporary Matplotlib cache, and `Fontconfig error: No writable cache directories`. These messages are real and remain preserved. They should not be summarized as an absence of all runtime errors or failed cache writes.

There is no logged Python traceback or recorder/controller exception, and the process, captures and numerical gates completed successfully. The messages therefore did not terminate this invocation. This review does not independently isolate their general effect on performance or every possible runtime behavior. The export redacts only the runtime-home and temporary-cache paths; it retains the messages themselves. No cache repair or rerun occurred.

## Export and sanitation boundary

The unchanged archive contains **55 regular-file members**, exactly matching the 55-file review package. Every member's bytes match the package; no traversal path, link or extra member was found. Member ownership names, IDs and timestamps are normalized. The four NPZ archives contain **24 safe numeric members**, inspected without pickle loading.

The transformation ledger accounts for **49 byte-identical copies, one exact calculation-log path redaction and five excluded private records**. Original and derivative digests verified. The five generated package files are the result report, entry-gate summary, completion record, transformation ledger and package manifest; they are covered by the package's complete manifest rather than presented as original raw copies. Raw scientific arrays, observations and source snapshots were not transformed.

Bounded scans found no private execution/home paths, temporary-cache paths, private environment identifiers, credential-like strings, recorded account-window values or Han text in the review payload and inspected NPZ contents. Excluded account/ownership/process records are absent. Frozen source contains generic release-schema field names; those are not actual account records.

| Artifact | SHA256 |
|---|---|
| Raw private manifest | `a68858791c532cb6cca524a7f45451bd940735b1d65d28af0fef0648512481f2` |
| Review-package manifest | `c31149eec57ecfd487b66e04ca8b835bdfb5a4f3f78315a4ee1991358ef99923` |
| 55-member archive | `01d92464eacc8e80298683ed232b239e77be7509d2a1f06703c0fb9945cec0a7` |

The review-start and post-check hashes agree for all raw, frozen and exported files, the archive and the retained attempt token. This is a review-only derivative inspection, not publication authorization, a new integrated public-release audit or an exhaustive privacy guarantee. Nothing was published.

## Interpretation, identity and remaining gates

One fresh guarded-recorder invocation has reproduced the saved altered-dispatch C1 result exactly under the recorded fingerprint. That supports the stated pairwise-repeatability outcome and demonstrates successful capture by this derivative for this invocation. It does not establish a statistical reproducibility distribution, universal instrumentation equivalence, historical backend causation, a numerical error bound or which derivatives are physically more accurate.

A separate Gamma protocol may now be designed for review, but this evidence does not resolve displacement-size dependence, graph continuity under displacement, finite-difference noise or phonon stability. Gamma, DFT, synthesis, material stability, novelty, application properties and complete migration remain unestablished. No further inference is authorized under P1.

This existing reviewer role was requested as GPT-6 Astra with High reasoning; Standard speed was requested where selectable. The parent reports the delegation settings. The exposed developer identity is GPT-6-based Codex; actual serving variant, reasoning effort and service tier are not independently attested. No new agent or environment was created.

The independent review found no unresolved evidence-integrity or numerical-decision defect. Its one failed reviewer assertion is preserved and explained. The parent still needs to read and accept the complete result and independent review. Publication and any further research calculation require their separate authorized steps; neither occurred here.
