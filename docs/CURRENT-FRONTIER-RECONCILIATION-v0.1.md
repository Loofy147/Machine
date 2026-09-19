# Current Frontier Reconciliation v0.1

**Recorded:** 2026-09-19  
**Repository:** `Loofy147/Machine`  
**Purpose:** durable research-state record for the current capability/allocation frontier and the results that must not be reconstructed from conversation context.

## 1. Branch audit

Audited branch refs:

| Role | Branch | Audited ref / head known from repository records | Relation / disposition |
|---|---|---|---|
| Integration baseline | `main` | `1626bac2f5c478294afa4b9463f694608c322117` | integration authority |
| Machine-native research | `research/machine-native-primitives-v0` | `081f649f5c4cc31c52cbeb7af0fbda4ee90c5478` | 48 ahead / 3 behind main at audit; broad research line |
| Target-oblivious frontier | `research/target-oblivious-frontier-v0` | `5decefaafb5b6abad2364629dafa1d96a5ffdba0` | 52 ahead / 3 behind main at audit; resource/placement line |
| Confirmatory freeze | `research/confirmatory-freeze-order-v0.1` | `6f724f9c6b4f3c979587a4117f8bdcde8a5ccc48` | 25 ahead / 1 behind main at audit; protocol/freeze line |
| Evidence integration | `research/evidence-disposition-v0` | audit base after current consolidation commits: `78fa2f77e12acfec295d696790594ae71332e0a0` | 63 ahead before this consolidation; 65 ahead after two evidence commits; evidence/provenance line |
| Stale candidates | `research/definition`, `research/machine-native-primitives`, `research/machine-native-primitives-v0-docs`, `research/machine-native-primitives-v0-issue`, `research/test-write` | old state rooted at `641517a26790c40295606f12fd6e4a87fcab7186` | ARCHIVE CANDIDATES; no unique changes vs main at audit |

The existing canonicalization document recorded the evidence branch as 53 commits ahead. Direct comparison at this audit returned 63 commits ahead. Therefore the old count is stale and must not be reused as current repository state.

The evidence branch itself is not scientific authority; it is the current reproducibility/provenance integration line.

## 2. Repository-backed results already established

### 2.1 Nine-mechanism review

Source: `research/machine-native-primitives-v0/docs/EXPERIMENT-REVIEW-9-MECHANISMS.md`, ref `081f649...`.

Current interpretation:

- the nine mechanisms should not become nine flat architectural primitives;
- variation and invocation gating produced strong testbed effects, but causal interpretation is bounded;
- composition and reformation are empirically relevant in the tested system;
- representation, transformation, and control are structural scaffolds rather than proven irreducible primitives;
- contextualized experience remains a hypothesis requiring further ablation.

Evidence status in the evidence branch remains OPEN / UNVERIFIED_PACKAGE for the broader nine-mechanism claim.

### 2.2 B-clean executable mutation

Source: `research/machine-native-primitives-v0/docs/EXPERIMENT-B-CLEAN.md`.

Established within scope:

- mutable executable representation can be changed and executed;
- adaptation came from the search procedure, not from mutation alone;
- search algorithm dominated the reported result in the bounded candidate family;
- this does not establish a substrate-level adaptive advantage for mutable executable representation.

Evidence status remains OPEN / UNVERIFIED_PACKAGE in the evidence branch.

### 2.3 Contextual credit

Source: `research/machine-native-primitives-v0/docs/EXPERIMENT-CONTEXTUAL-CREDIT.md`.

Established within scope:

- context-indexed history can outperform global history when operator value crosses between supplied contexts;
- the current experiment supplies the context label;
- context discovery remains OPEN.

Evidence status remains OPEN / UNVERIFIED_PACKAGE.

### 2.4 Online reflective learning

Source: `research/machine-native-primitives-v0/docs/EXPERIMENT-ONLINE-REFLECTIVE-LEARNING.md`.

Established within scope:

- continuous executable hot-swap is demonstrated;
- history-dependent proposal behavior is demonstrated for a fixed candidate palette;
- contextual credit is demonstrated with supplied context.

Not established:

- causal reification of the live evaluator/transition machinery;
- self-discovery of executable structure;
- context discovery from machine state;
- modification of the modifier/proposer.

The reflection target remains OPEN.

### 2.5 Target-oblivious frontier

Source: `research/target-oblivious-frontier-v0/experiments/target-oblivious-frontier/RESULTS-V0.md`, ref `5decefa...`.

Established for the declared finite graph fixture:

- strict-heldout invariant passes exactly;
- target-specific offline state that cannot contain the realized target does not alter held-out success or online work;
- increasing offline target coverage raises hit rate and lowers expected online work;
- full target-oblivious precomputation moves target-selection work to offline state in this finite graph;
- fixed-depth online lookahead has bounded per-decision expansion at fixed depth, but its success changes with M.

Interpretation boundary recorded by the branch:

> resource/placement tradeoff, not evidence that transition-mechanism modification is necessary.

## 3. New adversarial detector result now packaged

Code:

`experiments/frontier-insufficiency-adversarial-v0/detector.py`

Result:

`experiments/frontier-insufficiency-adversarial-v0/RESULTS-V0.md`

Code commit: `72dce24466a86d395174a6e4995d20f9fecdd523`  
Result commit: `78fa2f77e12acfec295d696790594ae71332e0a0`

Local execution reproduced:

- sufficient funnel -> `SUFFICIENT_FOUND`;
- sufficient needle with no gradient -> `INCONCLUSIVE_AT_RESOLUTION(5)`;
- insufficient easy positive floor -> `INCONCLUSIVE_AT_RESOLUTION(5)`;
- insufficient dense near-misses -> `INCONCLUSIVE_AT_RESOLUTION(5)`;
- pathological multiscale positive basins -> `INCONCLUSIVE_AT_RESOLUTION(5)`.

With independent Lipschitz certificates, the two certified insufficient fixtures returned:

- `INSUFFICIENT_CERTIFIED_AT_RESOLUTION` for the easy floor;
- `INSUFFICIENT_CERTIFIED_AT_RESOLUTION` for dense near-misses.

Interpretation:

> finite black-box persistence is not enough to prove expressive insufficiency; a third honest outcome, INCONCLUSIVE_AT_RESOLUTION(delta), is required unless an independent regularity/certificate assumption supports a negative conclusion.

This package has not yet been added to the branch's CI evidence verifier, so it is reproducible repository state but not yet CI-verified evidence.

## 4. Recent capability/allocation results that are NOT yet repository evidence

The following results were obtained and discussed in the current conversation but are absent from repository search at the audit:

- exact policy-table / BFS replay;
- h-based allocation frontier;
- memoized lookahead comparison;
- crossover around N=40 versus N=62;
- the reported ~19.3% reduction from memoization with the same success/failure pattern;
- the reported miss cost remaining roughly flat around 40--44 as offline coverage h increased.

Current disposition:

`USER_REPORTED / CONVERSATION-ONLY`

They must not be treated as repository evidence until their code, run command, raw results, and interpretation boundary are committed and replayable.

## 5. Corrected conceptual claims

### Claim C1 — fixed transition semantics do not imply fixed computational behavior

A fixed `step()` can produce substantially different behavior when its state contains richer policy/program/table data.

The policy-table experiment demonstrates this principle, but the BFS that built the table is the source of the necessary search computation.

Status: USER_REPORTED / CONVERSATION-ONLY pending repository packaging.

### Claim C2 — precomputation can relocate computation without expanding uncovered capability

The target-oblivious experiment establishes this in the declared finite graph under strict-heldout controls.

Status: EXPERIMENTALLY_SUPPORTED within fixture scope.

### Claim C3 — optimization can reduce cost without changing the feasible set

The memoized-lookahead result currently exists only as USER_REPORTED / CONVERSATION-ONLY. It must not yet be promoted.

### Claim C4 — capability is relative to the complete execution contract

Statements such as "S is sufficient" or "S is insufficient" are incomplete unless the following are fixed:

```text
transition mechanism
+ frozen representation/state budget
+ offline/preprocessing budget
+ online/post-instance budget
+ information timing
+ correctness criterion
+ allowed operations
```

Status: INFERENCE derived from the combined experimental corrections; next tests are required.

### Claim C5 — mechanism change is not a privileged category by definition

A changed transition mechanism is evidence of a different implementation. It is not by itself evidence of a new computational capability, because some mechanism changes may be representable as data interpreted by an unchanged substrate, or may only reduce cost.

Status: INFERENCE / OPEN.

## 6. Current formal comparison target

For a fixed mechanism T, frozen artifact A, and online budget Q, define the feasible instance set:

```text
F(T, A, Q) = { I : T(A, I) satisfies the task within Q }
```

The next comparison should distinguish:

1. same F, lower cost -> optimization;
2. different F because A contains more target-oblivious precomputation -> allocation/representation;
3. different F under matched A, offline budget, online budget, information timing, and correctness -> evidence that the transition mechanism changes the feasible set relative to the baseline.

Even case (3) requires auditing whether the new mechanism hides additional representation/search computation in its own definition.

## 7. Current frontier

The current research frontier is no longer:

```text
mechanism change vs state mutation
```

The active question is:

> After a target-oblivious artifact is frozen, with explicit limits on representation, preprocessing, and post-instance computation, what minimum computation must still occur after the instance is revealed?

Then:

> Can a different transition mechanism lower that minimum or expand the feasible instance set under the same explicit resource contract, or can the same effect be achieved by re-representing or relocating computation inside the fixed substrate?

## 8. Immediate discriminating experiments

### E1 — package the policy-table/allocation experiment

Commit:

- generator;
- freeze order;
- raw outputs;
- h/N sweep;
- exact cost accounting;
- success/failure pattern;
- crossover derivation.

The experiment must keep the future instance hidden during artifact construction.

### E2 — genuine mechanism capability comparison

Hold fixed:

- instance family;
- target-oblivious artifact A;
- representation budget;
- offline budget;
- online budget;
- information timing;
- correctness criterion.

Compare a baseline transition mechanism with a genuinely different mechanism.

Measure both:

```text
feasible-set membership
and
computation cost
```

Do not label a result "new capability" unless the feasible set changes under the matched contract.

### E3 — representation-equivalence controls

For every apparent mechanism advantage, test whether an equivalent program/data representation inside the baseline substrate can reproduce it without violating the same resource constraints.

### E4 — extend the insufficiency detector

Generate independent sufficient and insufficient families varying separately:

- search difficulty;
- solution sparsity;
- near-miss density;
- multiscale structure.

Report false-insufficiency and false-sufficiency rates, not only individual fixture outcomes.

### E5 — compact target-oblivious structures

Move beyond exact target tables:

- landmarks;
- partial policies;
- hierarchical summaries;
- reusable subplans;
- compact executable representations.

Measure the complete offline/representation/online Pareto frontier.

## 9. Governing interpretation rule

Do not treat computation location as computation absence.

Do not treat mechanism-name changes as capability changes.

Do not treat persistent plateau as proof of expressive insufficiency without the assumptions needed to exclude unseen solutions.

Do not upgrade conversation results to repository evidence without code/result/provenance packaging.

