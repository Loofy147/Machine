# Memory Under Uncertain Future Demand — Research Record v0.1

**Status:** RESEARCH SYNTHESIS / OPEN  
**Recorded:** 2026-10-30  
**Repository:** `Loofy147/Machine`  
**Branch:** `research/memory-under-uncertainty-v0.1`  
**Parent research line:** `research/machine-native-primitives-v0`  
**Purpose:** Preserve corrected synthetic results, distinguish memory failure modes, and define a reproducible research programme for memory allocation under uncertain future demand.

> Central design constraint: preserve recoverability; adapt as demands emerge.

This document is a research record, not a claim that the proposed memory architecture has been implemented or experimentally validated as a whole.

## 1. Executive finding

Memory should not be framed as a single mechanism that predicts which information will matter later. Different tasks require different memory functions, and future queries and goals are not generally known at write time.

A bounded active representation therefore faces an allocation problem:

- retain exact evidence where future distinctions may matter;
- maintain compact state where reusable structure can be represented;
- expose a query-dependent access path to retained evidence;
- account for storage, retrieval, latency, compute, staleness and distribution shift;
- preserve enough provenance to recover or revise earlier interpretations.

A compact formulation is:

\[
\max_{\pi}\; \mathbb{E}_{Q,G\sim D}\left[U(M_{\pi},Q,G)\right]
\quad\text{subject to}\quad
\operatorname{Memory}(M_{\pi})\leq B
\]

where:

- \(\pi\) is the retention, compression, retrieval and update policy;
- \(Q\) is a future query;
- \(G\) is a future goal or task condition;
- \(D\) is the assumed future workload distribution;
- \(U\) is task-dependent utility;
- \(B\) is the available memory budget.

This is an optimization model for reasoning about design trade-offs. It is not a universal objective function, and its usefulness depends on how well the workload distribution and utility are specified.

Perfect write-time prediction is not a general solution: future usefulness depends on future queries and goals that may not be available when an item is stored. Predictors can exploit regularities in a known workload, but they cannot guarantee optimal retention for arbitrary future demand.

## 2. Keep the memory questions separate

The following quantities must not be used interchangeably.

| Question | What it measures | What it does not establish |
|---|---|---|
| Access skew | Whether use is concentrated on a small subset of items | Whether the memory can represent all required information |
| Attention rank | Relative ordering of keys for a query/head | How much probability mass the leading key receives |
| Attention mass | Softmax share assigned to a key or set | Semantic importance or causal usefulness |
| Retrieval accuracy | Whether the required evidence is recovered | Whether the recovered evidence changes the final decision |
| Causal utility | Whether removing or changing evidence harms task performance | General usefulness on unseen workloads |
| Write-time predictability | Whether future utility correlates with insertion-time features | Perfect knowledge of future queries |
| Compressed-state capacity | What distinctions a bounded state can preserve | The capacity of a separate exact archive or KV store |
| Recoverability | Whether original evidence can still be accessed and reinterpreted | That retrieval is free, fast or always available |

In particular:

1. **Attention concentration is an access-distribution measurement, not a capacity diagnosis.**
2. **A key can remain rank 1 while its softmax mass becomes very small.**
3. **High attention is not proof of causal contribution to an answer.**
4. **A fixed-state capacity limit and attention dilution are different failure modes.**
5. **A retrieval archive changes the recoverability boundary; it does not eliminate access cost.**

## 3. Corrected synthetic result record

### 3.1 Hebbian versus delta-rule update strength

The supplied sweep reports the following accuracies:

| Number of stored items (n) | Hebbian | Delta, b = 0.1 | Delta, b = 1.0 |
|---:|---:|---:|---:|
| 64 | 0.95 | 0.96 | 0.75 |
| 256 | 0.43 | 0.42 | 0.17 |
| 1024 | 0.03 | 0.04 | 0.05 |

Interpretation within this synthetic setup:

- Delta with write strength \(b=0.1\) behaves approximately like plain Hebbian learning across the tested loads.
- Delta with \(b=1.0\) degrades earlier, consistent with overwriting previously stored associations.
- At \(n=1024\), all tested methods are near the failure floor. The sweep does not support the claim that tuning the update rule removes the high-load limit.

**Capacity boundary.** The tested associative store uses a \(d\times d\) state while each arbitrary stored key/value binding carries an amount of information proportional to \(d\). When \(n\gg d\), the state has fewer scalar degrees of freedom than the collection of arbitrary bindings. This is a parameter-counting limitation for this exact synthetic storage problem; it is not a universal theorem about learned representations, semantic compression, external memory, or every state-space model.

### 3.2 Exact-cache plus fixed-state probe

The reported probe uses an exact cache of 64 slots alongside a fixed-state representation at \(n=1024\).

| Query distribution | No cache | Random 64 | Frequency-learned 64 | Oracle 64 |
|---|---:|---:|---:|---:|
| Uniform | 0.03 | 0.08 | 0.09 | 0.10 |
| Zipf-skewed | 0.02 | 0.08 | 0.63 | 0.65 |

Interpretation:

- Under uniform access, there is little predictable concentration for a frequency policy to exploit. Random and frequency-based admission are close.
- Under Zipf-skewed access, past-query frequency captures about 97% of the reported oracle-cache score (0.63 / 0.65).
- The result supports the narrower conclusion that **observed access skew can make a small exact cache valuable when the future workload resembles the observed one**.
- The oracle is a hindsight upper bound, not an implementable policy.
- This does not establish that a generally learned hybrid architecture outperforms pure attention, an exact store, or a fixed-state model. The contribution of the fixed state is small in this particular high-load synthetic setup.

The earlier hybrid trade-off discussion must not be cited as proof of a hybrid-system performance advantage. A comparative claim requires an actual integrated hybrid, matched resource budgets, and direct baselines.

### 3.3 Attention-mass and dilution probe

The reported synthetic attention-metric test uses a gold key with a fixed logit margin of 5 over distractors.

| Number of keys (n) | Reported gold mass | Median gold rank |
|---:|---:|---:|
| 64 | 0.57 | 1 |
| 4096 | 0.035 | 1 |
| 32768 | 0.005 | 1 |

Additional reported observations:

- Zipf top-64 attention mass: approximately 0.632.
- Uniform top-64 attention mass: 0.0625.
- At \(n=32768\), a hand-set dilution flag was 0.86; approximately 14% of trials had the gold item outranked by more than two distractors.

The key result is that the gold item can remain median rank 1 while its attention mass collapses as the number of distractors grows. Rank and mass therefore answer different questions.

**Interpretation boundary.** The 0.86 flag is a thresholded synthetic diagnostic, not an observed model failure probability. The aggregation statistic for the gold-mass values and the sensitivity of the hand-set thresholds must be confirmed from the source script before these values can become a reproducible result package.

### 3.4 Synthetic experiment limitations

The supplied record describes the following limitations:

- random keys in 64 dimensions are only approximately, not perfectly, orthogonal;
- the hybrid and cache results use a simplified synthetic workload;
- the reported sweep used one seed;
- the attention router threshold was hand-set to 0.5;
- 3,000 queries were used, so sampling noise is material;
- the attention dilution thresholds were hand-set;
- synthetic random-key bindings are not learned semantic representations;
- no real model's hidden states, attention maps, recurrent state or end-task causal behavior were established by these probes.

**Evidence status:** the numerical tables above are **USER_REPORTED SYNTHETIC RESULTS**. The source script `attn_mass_metrics.py`, complete raw outputs, environment metadata and seed ledger were not present in the inspected repository state when this record was prepared. They have not been independently re-executed here. Do not promote these values to independently reproduced evidence until those artifacts are committed and checked.

## 4. Memory functions: a working decomposition

The following decomposition is a design framework, not a claim that every system needs four physically separate memory products.

### 4.1 Active state

A compact, currently available representation that supports ongoing computation. It may contain summaries, learned state, selected context, current task state or operational statistics.

Risk: compression may erase distinctions that future queries require.

### 4.2 Addressable evidence

Exact or provenance-preserving records that can be retrieved later: source documents, observations, events, key/value records, experiment artifacts, decisions and their lineage.

Risk: an archive that cannot be found, accessed or interpreted in time is not operationally recoverable.

### 4.3 Working context

The bounded information currently exposed to a process or module. It is an execution window, not necessarily the durable location of the information it contains.

Risk: context-window length is not equivalent to effective information use.

### 4.4 Access and retrieval

The mechanism and budget by which an active process selects, fetches, ranks, validates and incorporates stored evidence.

Risk: retrieval can be incomplete, biased, expensive, stale or incorrectly grounded.

A useful cross-check is the 2026 **State–Evidence–Access (SEA)** framework: active state, addressable evidence and the per-step access budget are jointly necessary to reason about memory function. SEA is a recent survey framework, not proof that one physical architecture is optimal.

## 5. Literature synthesis and architectural implications

The following papers provide external support for particular observations. They do not validate the supplied synthetic measurements or the complete MIRA proposal.

| Work | Research finding relevant here | Boundary for MIRA |
|---|---|---|
| [H₂O (NeurIPS 2023)](https://proceedings.neurips.cc/paper_files/paper/2023/file/6ceefa7b15572587b78ecfcebb2827f8-Paper-Conference.pdf) | KV-cache eviction can retain a combination of recent tokens and heavy hitters that contribute strongly to attention scores. | Heavy hitters are workload/model-dependent KV-cache retention signals, not a universal semantic memory policy. |
| [StreamingLLM (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/hash/5e5fd18f863cbe6d8ae392a93fd271c9-Abstract-Conference.html) | Keeping initial attention-sink tokens plus a recent window can stabilize streaming language modeling. The paper explicitly notes that sinks need not be semantically important. | An attention sink may stabilize an attention process without constituting useful evidence or long-term memory. |
| [Lost in the Middle (TACL 2024)](https://aclanthology.org/2024.tacl-1.9/) | Performance on retrieval and multi-document QA can vary with the position of relevant evidence in long contexts. | Context capacity must be evaluated by effective use and position sensitivity, not nominal token count alone. |
| [RULER (2024)](https://arxiv.org/abs/2404.06654) | Long-context capability should be tested beyond a single needle-in-a-haystack task; it adds multi-needle, multi-hop tracing and aggregation. | MIRA memory evaluations need diverse task demands, not a single retrieval score. |
| [Mamba (2023; revised 2024)](https://arxiv.org/abs/2312.00752) | Input-dependent selective state-space dynamics can selectively propagate or forget sequence information with linear sequence scaling. | A selective recurrent state is a useful compressed-state mechanism, not an exact addressable record store. |
| [Overcoming Long-Context Limitations of SSMs (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/3e4ea825a66bf1e1e33eca3e81fe7886-Abstract-Conference.html) | The paper argues that single-key associative recall is insufficient for more complex context-dependent multi-query recall, and studies complementary context-dependent sparse attention. | The result is about the studied task and architectures; it must not be generalized to every SSM or treated as proof that one hybrid is universally superior. |
| [Memory in the Age of AI Agents (2025)](https://arxiv.org/abs/2512.13564) | A survey distinguishes token-level, parametric and latent memory forms, and factual, experiential and working-memory functions, with formation/evolution/retrieval dynamics. | Agent memory should not be reduced to short-term versus long-term labels. |
| [Preserving Memory Function in Hybrid Language Models (Findings EMNLP 2026)](https://aclanthology.org/2026.findings-emnlp.1194/) | Proposes State–Evidence–Access and identifies function-granularity mismatch: saving memory can still lose retrieval, update or access functions. | Evaluate preserved functions, not only parameter count, cache size or average perplexity. |
| [What Attention Recalls and Recurrence Controls (Findings EMNLP 2026)](https://aclanthology.org/2026.findings-emnlp.2061/) | Cache interventions on Qwen3.5 and Falcon-H1 report task-dependent division between exact recall via attention and language/persona behavior via recurrent state. | This is evidence for complementary channels in the tested models/tasks, not a universal division of labor. |

### 5.1 Combined conclusion

The research supports treating memory mechanisms as functionally different:

- exact, addressable retrieval;
- compressed or recurrent state;
- context-sensitive access;
- online cache retention;
- persistent external records.

No one mechanism can be assumed to satisfy all five.

An attention cache is not the same as durable evidence. A compressed state is not the same as an exact store. A retrieval index is not the same as a successful retrieval. The architecture must preserve these distinctions.

## 6. Write-time admission versus online eviction

These are separate policy problems.

**Write-time admission** decides what to retain using only information available when an item arrives. Candidate signals may include source reliability, novelty relative to current state, task provenance, explicit user importance, estimated future reuse, causal role in a completed result, reversibility of loss and storage cost.

**Online eviction** decides what to remove or compress after observing subsequent access, state changes or workload feedback. Recent use, observed frequency, query-conditioned utility and current resource pressure may be available.

An attention score received after insertion is an online signal, not a strict write-time feature.

No predictor can perfectly infer arbitrary future usefulness from information unavailable at insertion. Evaluation should therefore compare:
- strict insertion-time predictors;
- online adaptive policies;
- recency and frequency baselines;
- random admission;
- hindsight oracle upper bounds;
- broad-coverage/diversity policies.

The oracle must be labelled as a non-deployable upper bound.

## 7. Distribution shift and recoverability

A retention policy optimized on yesterday's access distribution can become harmful when the workload changes.

A complete evaluation should measure at least:

1. expected task utility under the training workload;
2. worst-case or lower-tail degradation across plausible workload shifts;
3. regret against an oracle upper bound;
4. retrieval accuracy for exact evidence;
5. state-update quality for compressed memory;
6. staleness and contradiction handling;
7. storage, retrieval and compute cost;
8. latency and throughput;
9. recovery success when an active summary is insufficient;
10. provenance completeness and ability to reconstruct prior state.

A policy should not silently turn a low-probability future demand into irreversible data loss. When the original evidence remains available in an archive, compression can be revised later, at the cost of retrieval and verification.

## 8. Corrected experiment programme

### E1 — Attention dilution on a pure-attention model

**Question:** Does a gold evidence span retain rank while its mass falls as distractors increase?

Design:
- keep the complete KV context available;
- sweep context length and evidence position;
- include beginning, middle and end placements;
- log gold rank, mass, entropy and end-task accuracy per relevant head/layer;
- vary distractor similarity and count independently;
- compare mass/rank changes to causal removal or replacement of the evidence.

Interpretation:
- falling mass with stable rank is consistent with softmax dilution;
- wrong high-mass attention suggests a different competition or relevance failure;
- neither pattern alone proves task-level causal importance.

### E2 — Access-skew characterization

**Question:** How concentrated is actual access across representative workloads?

Design:
- measure top-m mass and hit concentration across queries, heads, layers and task types;
- compare uniform, Zipf-like, bursty and changing workloads;
- report per-task and per-head distributions rather than only pooled means.

Purpose: estimate when cache policies may help and how sensitive they are to workload assumptions.

### E3 — Strict write-time predictability

**Question:** Do future high-utility items have observable insertion-time features?

Controls:
- freeze features to those available at insertion;
- hold out documents, tasks and temporal segments;
- prevent future-query access in the predictor;
- separately report predictors that use early post-insertion access;
- test after workload shift.

Purpose: estimate predictability, not to seek a perfect oracle.

### E4 — Online cache/admission policy comparison

Compare random, LRU/recency, frequency, H₂O-style online heavy hitters, and workload-informed policies using identical capacity and access traces. Report exact task utility and retrieval failures alongside hit rate.

### E5 — Size-matched compressed-state and hybrid comparison

Compare:
- attention with full retained context;
- bounded exact KV cache;
- compressed/recurrent state;
- external exact evidence store;
- hybrid combinations.

Match memory budgets and disclose compute/access costs. The capacity question belongs here, not in an attention-mass-only experiment.

### E6 — Causal evidence utility

Intervene by masking, replacing or removing evidence spans with matched controls. Measure changes in task accuracy and output quality. Distinguish raw attention weight from the causal contribution of an item or span.

### E7 — Recoverability under distribution shift

After building a compact state, introduce a new query/goal distribution requiring previously low-frequency evidence. Compare:
- no archive;
- archive with exact retrieval;
- compressed memory only;
- hybrid archive + state;
- stale summaries with and without provenance-aware revision.

Measure recovery success, access cost, latency and irrecoverable-loss rate.

## 9. Evidence and claim ledger

| Claim | Status | Boundary / next requirement |
|---|---|---|
| Future utility depends on future queries and goals | ESTABLISHED as a logical dependency | Does not specify a usable probability distribution. |
| Perfect strict write-time prediction is impossible in general | INFERENCE from unknown future demand | Predictability can still exist under workload assumptions. |
| Delta b=0.1 is close to Hebbian in the supplied sweep | USER_REPORTED SYNTHETIC RESULT | Preserve script, seeds and raw outputs; reproduce. |
| Delta b=1.0 degrades earlier in the supplied sweep | USER_REPORTED SYNTHETIC RESULT | Reproduce and isolate overwriting mechanism. |
| Fixed \(d\times d\) storage cannot encode arbitrary \(n\times d\) bindings losslessly for \(n\gg d\) without extra assumptions/storage | MATHEMATICAL COUNTING ARGUMENT for the stated representation | Does not bound semantic compression or augmented external-memory systems. |
| Frequency admission tracks Zipf-skewed accesses in the reported cache probe | USER_REPORTED SYNTHETIC RESULT | Reproduce; test distribution shift and more seeds. |
| Gold attention mass can collapse while median rank remains 1 | USER_REPORTED SYNTHETIC RESULT | Confirm aggregation and thresholds from source script. |
| Attention-mass concentration proves memory capacity failure | CONTRADICTED | Access skew and compressed-state capacity are distinct. |
| A hybrid architecture generally beats pure attention or pure recurrent state | OPEN | Requires integrated, size-matched comparative experiments. |
| Attention sinks are semantically important evidence | CONTRADICTED as a general rule | StreamingLLM explicitly distinguishes sink scores from semantic importance. |
| State, Evidence and Access are useful axes for hybrid-memory analysis | LITERATURE-BACKED FRAMEWORK | Survey framework; not a universal optimal architecture. |
| Recoverability reduces irreversible loss but incurs access cost | DESIGN INFERENCE | Quantify with E7. |

## 10. Artifact and reproduction obligations

Before the synthetic record is treated as independently reproduced, add:

- `attn_mass_metrics.py` and all other source scripts used in the sweeps;
- deterministic input-generation rules and exact key/vector construction;
- all seeds and random-state handling;
- exact commands and dependency versions;
- raw per-trial outputs, not just aggregate tables;
- a machine-readable result file;
- the analysis script that generates each table;
- thresholds and their sensitivity analysis;
- commit SHA and workflow/run identity;
- an independent verifier that checks regenerated metrics and provenance.

Do not invent missing run IDs, hashes, environment versions or exact aggregation procedures. Mark unknowns as OPEN.

## 11. Relationship to Machine and MIRA

Machine's abstract model separates State, Operation, Transition and Control, and the machine-native research line distinguishes reconfigurability, adaptation, learning, reusable learning and causal reflection. This memory record must not silently add a universal `Memory` primitive or equate memory with a human cognitive faculty.

The memory findings are candidate mechanisms and constraints that may inform a broader reference architecture:

- active state is one form of operational state;
- stored evidence is an addressable resource;
- retrieval is a relation/operation that incurs cost;
- retention and forgetting alter future reachable information;
- persistence and lineage affect reproducibility and continuity;
- memory-policy changes are not automatically learning or causal reflection.

MIRA may consume these as research-backed distinctions, but Machine remains the owner of its own substrate claims and experimental evidence. Architecture adoption requires a separate contract and provenance reference.

## 12. Immediate next actions

1. Recover and commit the exact synthetic experiment scripts and raw outputs.
2. Reproduce the supplied tables from a clean environment with multiple seeds.
3. Separate access-skew, dilution, compressed-state capacity and causal utility metrics in the analysis.
4. Design the strict write-time predictor protocol before selecting features.
5. Run the size-matched hybrid and recoverability comparisons.
6. Preserve negative results and distribution-shift failures with the same provenance discipline as positive results.

## References

- Zhang et al., H₂O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models, NeurIPS 2023 — https://proceedings.neurips.cc/paper_files/paper/2023/file/6ceefa7b15572587b78ecfcebb2827f8-Paper-Conference.pdf
- Xiao et al., Efficient Streaming Language Models with Attention Sinks, ICLR 2024 — https://proceedings.iclr.cc/paper_files/paper/2024/hash/5e5fd18f863cbe6d8ae392a93fd271c9-Abstract-Conference.html
- Liu et al., Lost in the Middle: How Language Models Use Long Contexts, TACL 2024 — https://aclanthology.org/2024.tacl-1.9/
- Hsieh et al., RULER: What's the Real Context Size of Your Long-Context Language Models?, 2024 — https://arxiv.org/abs/2404.06654
- Gu and Dao, Mamba: Linear-Time Sequence Modeling with Selective State Spaces, 2023/2024 — https://arxiv.org/abs/2312.00752
- Zhan et al., Overcoming Long-Context Limitations of State Space Models via Context-Dependent Sparse Attention, NeurIPS 2025 — https://proceedings.neurips.cc/paper_files/paper/2025/hash/3e4ea825a66bf1e1e33eca3e81fe7886-Abstract-Conference.html
- Hu et al., Memory in the Age of AI Agents, 2025 — https://arxiv.org/abs/2512.13564
- Hu et al., Preserving Memory Function in Hybrid Language Models: A Survey of State, Evidence, Access, and Granularity, Findings EMNLP 2026 — https://aclanthology.org/2026.findings-emnlp.1194/
- Afendulev et al., What Attention Recalls and Recurrence Controls in Hybrid Language Models, Findings EMNLP 2026 — https://aclanthology.org/2026.findings-emnlp.2061/
