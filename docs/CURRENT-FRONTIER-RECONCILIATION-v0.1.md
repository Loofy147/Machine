# Current Frontier Reconciliation v0.1

**Recorded:** 2026-09-19
**Repository:** `Loofy147/Machine`
**Purpose:** durable research-state record for the current capability/allocation frontier and the results that must not be reconstructed from conversation context.

## 1. Branch audit

Audited branch refs:

| Role | Branch | Audited ref / head known from repository records | Relation / disposition |
|---|---|---|---|
| Integration baseline | `main` | `1626bac2f5c478294afa4b9463f694608c322117` | integration authority |
| Machine-native research | `research/machine-native-primitives-v0` | `081f649f5c4cc31c52cbeb7af0fbda4ee90c5478` | broad machine-model research |
| Target-oblivious frontier | `research/target-oblivious-frontier-v0` | `5decefaafb5b6abad2364629dafa1d96a5ffdba0` | resource/placement line |
| Confirmatory freeze | `research/confirmatory-freeze-order-v0.1` | `6f724f9c6b4f3c979587a4117f8bdcde8a5ccc48` | protocol/freeze line |
| Evidence integration | `research/evidence-disposition-v0` | current consolidation line | evidence/provenance line |
| Stale candidates | `research/definition`, `research/machine-native-primitives`, `research/machine-native-primitives-v0-docs`, `research/machine-native-primitives-v0-issue`, `research/test-write` | old state rooted at `641517a26790c40295606f12fd6e4a87fcab7186` | ARCHIVE CANDIDATES |

The older canonicalization document's evidence-branch commit count is stale; direct audit supersedes the old count.

## 2. Repository-backed results already established

### 2.1 Nine-mechanism review

The nine mechanisms should not be promoted to nine flat primitives. Variation, invocation gating, composition, and reformation produced measured effects in the bounded testbed, while representation, transformation, and control remain structural scaffolds rather than proven irreducible primitives.

Evidence packaging status remains bounded/open as recorded by the evidence branch.

### 2.2 B-clean executable mutation

Mutable executable representation can be modified and executed, but the measured adaptive behavior was driven by the external search procedure. Mutable executable representation itself was not shown to provide an adaptive advantage.

Evidence packaging status remains OPEN / UNVERIFIED_PACKAGE.

### 2.3 Contextual credit

Context-indexed history can outperform global history when operator value crosses between supplied contexts. Context discovery from machine-observable state remains OPEN.

Evidence packaging status remains OPEN / UNVERIFIED_PACKAGE.

### 2.4 Online reflective learning

Continuous executable hot-swap and history-dependent proposal behavior are demonstrated within their declared boundaries.

Not established:

- causal reification of the live evaluator/transition machinery;
- context discovery;
- arbitrary executable structure discovery;
- modification of the modifier/proposer.

Causal reflection remains OPEN.

### 2.5 Target-oblivious frontier

For the declared finite graph fixture:

- strict-heldout invariant passes;
- partial target-specific offline state that cannot contain the realized target does not change held-out behavior;
- increasing offline target coverage increases hits and lowers expected online work;
- full target-oblivious precomputation can move target-selection work to offline state;
- fixed-depth online lookahead remains resource-sensitive as M grows.

Interpretation boundary remains resource/placement tradeoff, not evidence that reflection is necessary.

## 3. Adversarial insufficiency detector

Code and results:

`experiments/frontier-insufficiency-adversarial-v0/`

The detector has three verdicts:

- `SUFFICIENT_FOUND`
- `INCONCLUSIVE_AT_RESOLUTION(delta)`
- `INSUFFICIENT_CERTIFIED_AT_RESOLUTION`

Observed blind results support the methodological rule that persistent positive residual is not, by itself, proof of expressive insufficiency.

Independent Lipschitz certificates can support a bounded negative result for selected fixtures.

The package remains locally replayed but is not yet CI-integrated.

## 4. Current mechanism-frontier experiment

### 4.1 Fair baseline

The old naive forward recursion was removed from the primary comparison.

Baseline:

```text
successor-only substrate
+
BFS
+
visited set
```

Changed mechanism:

```text
successor access
+
direct online predecessor access
+
bidirectional BFS
```

Contract:

```text
B_off = 0
R = 0
no persistent target-dependent state
same instances
same correctness criterion
1 candidate-edge examination = 1 online tick
```

### 4.2 Observed frontier shift

Under fixed tight online budgets, direct predecessor access produced many additional solved instances.

Examples:

- M=30, B_on=20: forward 105/192; native bidi 192/192.
- M=300, B_on=80: forward 37/200; native bidi 197/200.
- M=3000, B_on=640: forward 18/200; native bidi 200/200.

This is a measured feasible-set/Pareto-frontier shift under the declared resource contract.

### 4.3 Decisive emulation control

The successor-only substrate was then forced to emulate predecessor access by exhaustive online scanning:

```text
candidate state
→ apply original successor operations
→ test whether successor(candidate) = requested node
```

Every candidate-edge examination is charged to `B_on`.

This emulation did not reproduce the native bidirectional frontier at the tight budgets tested.

Examples:

- M=30, B_on=40: native bidi 192; successor-only emulated bidi 19.
- M=300, B_on=160: native bidi 200; successor-only emulated bidi 3.
- M=3000, B_on=640: native bidi 200; successor-only emulated bidi 0.

At sufficiently high budgets, the finite sampled cases can eventually be solved, demonstrating that the present result is not a proof of different ultimate computational power.

### 4.4 Current interpretation

The current experiment supports:

> a resource-bounded mechanism-induced frontier shift for the specific addition of direct predecessor access.

It does not support:

> mechanism change in general creates absolute new computational capability.

The critical remaining question is whether cheaper successor-only inverse representations exist that reproduce the frontier without adding predecessor access, with every representation-construction and access cost charged to the same online budget.

## 5. Recent results that remain Conversation-only

The following are explicitly not repository evidence yet:

- exact policy-table/BFS replay;
- h-based allocation sweep;
- memoized-lookahead comparison;
- reported ~19.3% memoized operation reduction;
- reported crossover near N=40 versus N=62;
- reported miss floor around 40–44.

Their current disposition is USER_REPORTED / CONVERSATION-ONLY until code, raw output, provenance, and replay are packaged.

## 6. Corrected conceptual claims

### C1 — fixed mechanism does not imply fixed computational behavior

A fixed transition mechanism can execute substantially different behavior when its state contains different policy/program/table data.

The policy-table result currently remains conversation-only because its generator and raw run are not yet packaged.

### C2 — computation can be relocated

The target-oblivious experiment establishes that precomputation can relocate work from online execution into frozen state under the declared finite graph contract.

### C3 — optimization is distinct from capability

Memoization is currently conversation-only, but the intended distinction is:

```text
same feasible set + lower cost = optimization
```

### C4 — capability is contract-relative

A capability statement is incomplete unless transition mechanism, representation/state budget, preprocessing budget, post-instance budget, information timing, correctness criterion, and allowed operations are fixed.

### C5 — mechanism should be evaluated by frontier movement

A mechanism change should be considered consequential only to the extent that a measured feasible-set or Pareto-frontier shift remains after matched resource accounting and representation-equivalence controls.

## 7. Current frontier

The research question is now:

> After a target-oblivious artifact is frozen, with explicit limits on representation, preprocessing, and post-instance computation, what minimum computation must still occur after the instance is revealed?

Then:

> Can a changed transition mechanism lower that minimum or expand the feasible instance set under the same explicit execution contract, or can the same effect be reproduced by re-representing or relocating computation inside the fixed substrate?

The present mechanism experiment supplies the first repository-backed example where a specific transition-access change shifts the resource-bounded frontier.

## 8. Immediate discriminating experiments

1. Repeat the predecessor-access comparison on independent graph families and seeds.
2. Build stronger successor-only inverse representations and charge all construction/use cost online.
3. Normalize inverse-access cost so the comparison distinguishes information access from hidden implementation efficiency.
4. Add compact target-oblivious representations under controlled `B_off,R`.
5. Package and replay the policy-table/allocation/memoization experiments before using their reported numerical values as evidence.

## 9. Governing interpretation rules

Do not treat computation relocation as computation elimination.

Do not treat algorithm-name changes as capability changes.

Do not treat a plateau as proof of expressive insufficiency without the assumptions needed to exclude unseen solutions.

Do not treat a mechanism-induced frontier shift under a tight resource contract as proof of absolute computational-power separation.

Do not promote conversation results to repository evidence without executable provenance and replay.
