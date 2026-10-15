# Composite Repair, Interaction Diagnosis, and Iterative Convergence — Findings v0.1

Date: 2026-09-20

## Provenance

This document records the durable conclusions and findings produced during the composite-repair investigation on 2026-09-19/20.

The experimental state was reported as verified against the local working tree/on-disk artifacts during the investigation, including real subprocess-tested artifacts and replay/gating results. During this repository update, the raw experiment files were not found on the inspected GitHub branches, so this document is the durable findings/provenance record and does not claim that the raw local artifacts were pushed here.

Evidence status:
- ESTABLISHED — supported by the executed controlled result in the declared regime.
- EXPERIMENTALLY_SUPPORTED — supported by the reported executed experiment, with remaining scope limits.
- PARTIAL — observed but not demonstrated at the intended scale/generalization.
- UNKNOWN / OPEN — not yet experimentally established.

---

# 1. Current capability frontier

| Level / mechanism | Status | Boundary |
|---|---|---|
| L0 fixed execution | ESTABLISHED | ordinary fixed execution |
| L1 mutable parameters | ESTABLISHED | parameter mutation only |
| L2 mutable executable implementation | ESTABLISHED | executable state itself changes |
| L2.5 online hot-swap in same process | EXPERIMENTALLY_SUPPORTED | demonstrated in the current same-process stream harness |
| L3 learned reusable structure | UNKNOWN | not yet synthesized by the machine |
| L4 self-modifying modifier | UNKNOWN | proposer/modifier logic is still privileged |
| L5 causal reflection of evaluator | UNKNOWN / NOT YET | acceptance/evaluation mechanism has not been made causally mutable |

The important boundary is that L3/L4/L5 are not implied by L2/L2.5. They require new experimental capabilities.

---

# 2. Previously established adaptive results

## 2.1 History-biased proposal

Claim: outcome history bound to operator identity can causally suppress bad proposals under a fixed candidate palette.

Status: ESTABLISHED.

Evidence: enabled vs erased vs shuffled controls; 60 seeds x 100 generations; reported p < 0.0001.

Interpretation: the result is not explained by merely having historical state or the same distributional shape. Correct binding matters.

Limit: candidate/action space was fixed and supplied externally.

## 2.2 Operator x context relationship learning

Claim: the learned history contains useful operator/context binding rather than only a marginal operator preference.

Status: ESTABLISHED.

Evidence: repeated-context intervention after a detour; context-aware and context-blind conditions diverged, with context-blind belief degrading under off-context evidence while context-aware belief remained useful.

Limit: context was supplied explicitly. Context discovery itself remains unresolved.

## 2.3 Composite-fault diagnosis and minimal repair

Claim: a bundled change can be decomposed, a causal fault isolated, and a minimal repair validated without discarding the whole bundle.

Status: ESTABLISHED in the demonstrated regime.

Evidence: ddmin and an independent Bayesian tracker converged on the same main-effect culprit; repair passed a gated stream that was not used for diagnosis.

Limit: the marginal Bayesian mechanism is structurally blind to certain interactions; ddmin alone finds one minimal failing configuration, not all faults.

## 2.4 Interaction structure

Claim: interaction structure is detectable.

Status: EXPERIMENTALLY_SUPPORTED / PARTIAL.

Evidence: an AND-interaction pair and an OR-independent case were distinguished by interaction-aware analysis after the failure mode was checked numerically.

Critical limitation: the marginal Bayesian tracker is provably blind to the demonstrated interaction structure.

For the tested pair, the marginal tracker produced byte-identical evidence for:
- a joint AND dependency;
- two unrelated bugs.

Reported signature:
P: +0.500, Q: +0.500, R: 0.000

Therefore this is a model-shape failure, not a tuning failure.

---

# 3. Interaction-aware repair architecture

The tested and retained architecture is a two-stage hybrid:

1. Use ddmin/coarse localization to narrow a large edit set.
2. Run exact or fractional-factorial interaction analysis only on the narrowed cluster.
3. Derive the repair from the interaction structure.
4. Run an explicit minimality check.
5. Run correctness, replay, generalization, and preservation gates.

Design principle:

ddmin result != repair set

A failing subset is evidence about localization, not automatic evidence that every member of the subset should be deleted.

---

# 4. Composite multi-fault experiment

## 4.1 Question

Does a single pass of:

ddmin -> interaction analysis -> minimality -> gates

recover all faults when one composite candidate contains more than one independent fault mechanism?

## 4.2 Composite structure

The tested composite contained:
- one standalone main-effect bug D_bug;
- one AND-interaction pair P_state + Q_state;
- other safe edits in the bundle.

## 4.3 Round 1

ddmin found:
{D_bug}

with 4 probes.

The result was a correct minimal main-effect diagnosis.

After removing the diagnosed fault, the repaired candidate still failed the acceptance gates.

Interpretation:

A single ddmin pass under-repairs composite candidates.

The interaction P_state ∧ Q_state remained undiscovered because ddmin stopped once it found one minimal failing subset.

This falsifies the straight-line architecture as a general multi-fault repair protocol.

---

# 5. Required loop-back

The repair pipeline is therefore a loop/fixpoint process:

    Candidate C
       |
       v
    Diagnose currently failing subset
       |
       v
    Interaction analysis when required
       |
       v
    Minimal repair R
       |
       v
    Apply R -> C'
       |
       v
    Correctness / Replay / Generalize / Preserve
       |
       +---- ALL PASS ----> CONVERGED
       |
       +---- ANY FAIL ----> re-diagnose C'

The acceptance gates are therefore both:
- an acceptance mechanism;
- a trigger for re-localization of residual faults.

---

# 6. Round 2 and convergence result

On the remaining broken residue:

{A_isqrt, B_evenskip, C_neutral, P_state, Q_state}

ddmin correctly localized:
{P_state, Q_state}

using 14 probes.

The interaction analysis re-derived the same +0.500 interaction signature from the standalone interaction experiment.

This is evidence that the two-stage hybrid still works after the problem changes between rounds rather than only on the originally constructed isolated interaction case.

The corrected minimality gate then established:
- removing Q_state alone -> correct=True;
- removing nothing -> correct=False.

Final repaired candidate:
{A_isqrt, B_evenskip, C_neutral, P_state}

Final gates:
- correctness = true
- replay = true
- generalization = true
- preserve = true
- all pass = true

The process converged after two rounds.

Removed edits:
{D_bug, Q_state}

Retained P_state is inert without Q_state in the tested semantics.

---

# 7. Real defect in the safety machinery

A real bug was discovered in the implementation of minimize_removal_set.

The logging claimed that:
removal=[]
passed correctness on a candidate already known to fail.

The cause was set algebra in the test construction.

The implementation used the opposite candidate from the one it logged:
(full - S) | smaller

instead of testing:
full - smaller

For a two-element failing set, this caused the procedure to test the wrong candidate and could produce a false empty-removal success.

The observed consequence was an infinite loop across rounds 2–5 in the first run.

The bug was fixed and the full composite experiment was rerun.

Finding: the verifier, minimality gate, and repair machinery are themselves executable safety-critical mechanisms and require independent tests. They cannot be treated as trusted infrastructure merely because they are part of the test harness.

---

# 8. ddmin interaction over-correction

The earlier standalone interaction experiment established another boundary:

A heuristic that drops the entire minimal failing set is unsafe for AND interactions.

For an interaction:
P ∧ Q

dropping:
{P,Q}

is not necessarily minimal.

The composite experiment reinforced the need for a separate minimality stage.

Therefore:
localization -> repair
must not be collapsed into a single heuristic.

---

# 9. Validation coverage finding

A buggy operator passed correctness under one validation stream and failed under another because the first stream lacked a discriminating structure.

The concrete example involved an isqrt-related bug whose failure required a perfect square of a prime.

Therefore:
non-destructive test
is only as trustworthy as its sampling/discrimination mechanism.

Random or ordinary samples cannot be treated as evidence of broad correctness without an explicit coverage/discrimination argument.

The natural extension is challenge-directed validation:
choose the next test for expected discrimination between competing hypotheses
rather than merely sampling more inputs.

This remains UNBUILT.

---

# 10. Off-policy credit freezing

A champion mechanism can stop accumulating useful evidence when nothing is allowed to challenge it.

This creates a feedback loop:

current policy -> controls evidence collection -> receives no counter-evidence -> remains champion

A proposed architecture is an independent challenger channel:
- deployed champion;
- protected/periodic challenger;
- independent evidence collection;
- comparison outside champion control.

This remains UNBUILT.

Key design principle:
evidence collection must not be completely controlled by the current deployed policy.

---

# 11. Diagnosis-path non-determinism

ddmin search order currently depends on Python set iteration order.

Python hash randomization can therefore cause different valid minimal failing subsets or different search paths on different processes.

PYTHONHASHSEED=0 was pinned for the reported run, but the pipeline itself does not enforce deterministic diagnosis ordering.

Two guarantees must be separated:

### Behavioral reproducibility

The repaired candidate reproduces the expected behavior.

### Diagnostic reproducibility

The same failing candidate produces the same diagnosis/search path.

The current replay gate establishes the first, not the second.

The second is currently OPEN.

A stricter requirement may not be necessary. There can be multiple valid minimal diagnoses. A potentially better contract is:

same candidate -> same equivalence class of valid diagnoses

rather than:
same candidate -> identical search path

This must be experimentally tested.

---

# 12. Convergence requirements exposed by the loop

The iterative architecture needs an explicit progress invariant.

At minimum, each failed-gate round must either:
- reduce the candidate under the declared repair objective; or
- produce a stronger diagnostic state without repeating an identical candidate.

A useful first measure is:
|C_(i+1)| < |C_i|

when repair removes edits.

More generally:
M(C_(i+1)) < M(C_i)

for a declared monotonic progress measure.

The implementation should record per round:
- round number;
- candidate fingerprint;
- failure signature;
- localized subset;
- interaction signature;
- proposed repair;
- resulting candidate;
- gate results;
- progress measure.

If a round produces no progress, the procedure should stop as OPEN rather than silently loop.

This termination/progress contract remains to be implemented and experimentally validated.

---

# 13. Minimal repair vs minimal candidate

The current repair objective must remain distinct from a later simplification objective.

minimal fault repair != minimal remaining edit set

A repaired candidate can contain an edit that is currently inert because another edit was removed.

In the composite result, P_state remained in the candidate after Q_state was removed.

That is acceptable under the demonstrated fault-repair objective.

Whether P_state should subsequently be removed is a different question:
Does the retained edit contribute to accepted behavior?

That should be a separate simplification experiment rather than silently redefining the minimality gate.

---

# 14. Current research architecture

The evidence now supports the following architecture for composite repair:

    candidate executable bundle
              |
              v
       coarse localization
            (ddmin)
              |
              v
    interaction-aware analysis
       on suspicious cluster
              |
              v
         minimal repair
              |
              v
    correctness / replay / generalize
          / preserve
              |
       +------+------+
       |             |
    ALL PASS        FAIL
       |             |
       v             v
   CONVERGED    re-diagnose residue
                      |
                      +---- loop

This is an iterative fixpoint protocol, not a linear pipeline.

---

# 15. L3 boundary

Current adaptive experiments select from human-supplied operators/edits.

That is not L3.

L3 requires the system to synthesize its own candidate edit decomposition:

observed executable delta/failure
-> construct candidate edit decomposition
-> test candidates
-> select/compose repair

A proposed edit algebra is:
AST / IR / bytecode delta
-> primitive change atoms
-> candidate decompositions
-> candidate repairs
-> test

The important change is from:
which supplied operator should be used?
to:
what edit should exist at all?

L3 remains UNKNOWN.

---

# 16. L4 boundary

propose() or the modifier-selection mechanism has not itself been reified, tested, and committed in the manner demonstrated for transition().

A controlled L4 architecture would use:
- active proposer;
- shadow proposer;
- candidate modifier;
- isolated/shadow evaluation;
- atomic installation only after acceptance.

The proposer may modify the proposer mechanism but should not silently modify the acceptance kernel.

L4 remains UNKNOWN.

---

# 17. L5 boundary

The acceptance/evaluation criterion has not been brought into the mutation scope.

A causal-reflection experiment requires a stable meta-kernel defining what counts as an admissible evaluator transition while allowing the evaluator itself to become a mutable object.

The minimum causal test would be:
1. reify evaluator;
2. intervene on evaluator;
3. execute the modified evaluator;
4. observe changed acceptance behavior;
5. demonstrate causal persistence across subsequent modification.

This is not established by L2/L2.5 and remains OPEN.

---

# 18. Immediate experimental frontier

The next discriminating experiment should be adversarial rather than another easy composite.

Recommended composition:
- 3 independent standalone faults;
- 2 independent AND interactions;
- an edit participating in both a main effect and an interaction;
- multiple valid minimal diagnoses;
- repeated runs across varied PYTHONHASHSEED values.

Acceptance criteria:
1. every run reaches an accepted candidate or explicitly returns OPEN;
2. no candidate repeats;
3. no repair oscillation occurs;
4. progress measure is monotonic;
5. different diagnosis paths converge to behaviorally equivalent accepted repairs;
6. declared repair minimality is preserved;
7. diagnosis reproducibility/equivalence is measured separately from behavioral replay.

The result should bound or falsify the current convergence hypothesis before L3 work begins.

---

# 19. Net claim frontier after this investigation

### ESTABLISHED / EXPERIMENTALLY_SUPPORTED

- history-bound proposal adaptation in the tested fixed action space;
- operator x context credit in the supplied-context regime;
- main-effect composite fault localization and gated repair;
- interaction structure is real and detectable;
- marginal Bayesian credit is structurally insufficient for the demonstrated interaction;
- two-stage localization + interaction analysis works in the tested composite sequence;
- a single ddmin pass is insufficient for a composite containing multiple independent fault mechanisms;
- iterative re-localization after failed gates can separate the demonstrated standalone fault and interaction pair;
- the corrected minimality gate can reject the empty repair and accept the smaller valid interaction repair;
- the demonstrated composite converged in two rounds after fixing the gate bug.

### PARTIAL / OPEN

- deterministic diagnosis path;
- convergence/termination guarantees for larger composites;
- bounded behavior under repeated alternative diagnoses;
- adaptive challenge generation;
- independent challenger evidence channel;
- learned reusable executable structure (L3);
- self-modifying modifier (L4);
- causal reflection of evaluator/acceptance semantics (L5).

---

# 20. Engineering rule extracted from the whole experiment

Do not treat the repair pipeline as:
localize -> fix -> trust

Treat it as:
localize -> model -> minimally repair -> falsify the repair -> re-localize residual failure -> converge under an explicit progress contract

The test machinery itself is part of the system under test.
---

# 21. 2026-09-21 addendum — AND/OR interaction distinction and repair-objective correction

This addendum records the correction and extension produced by the follow-up interaction experiment discussion.

## 21.1 Correction to the earlier failure-mode claim

The earlier informal claim was:

> a marginal presence/absence tracker would fail to light up on a pure AND interaction.

That claim was wrong.

For a pure two-edit AND failure:

| P | Q | fail |
|---|---|---:|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

each edit is individually necessary, so the marginal presence/absence gap is non-zero for both P and Q.

The same marginal gaps can arise for an OR-independent structure:

| P | Q | fail |
|---|---|---:|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

Therefore the important limitation is not:

> marginal tracking cannot detect interaction.

It is:

> marginal tracking cannot identify whether the observed association is produced by a joint dependency or by independent sufficient faults.

For the demonstrated coding, the marginal evidence is identical:

- P = +0.500
- Q = +0.500
- R = 0.000

This is an identifiability limitation of the model shape.

## 21.2 Interaction contrast

Using the same full-factorial probe table, the second-order PQ contrast distinguishes the structures under the fixed Yates coding convention:

- AND interaction: PQ = +0.500
- OR-independent: PQ = -0.500

The important result is the opposite interaction direction under the same coding, not the absolute numerical scale by itself.

The interaction pass is therefore a structural detector, whereas the marginal pass is only an association detector.

## 21.3 ddmin is a localization operation, not a repair operation

A second correction is now experimentally motivated.

ddmin returns a 1-minimal failing set (MFS): a subset whose failure disappears when any single member is removed.

That object is not necessarily the minimum repair set (MCR).

For the AND case:

- MFS = {P,Q}
- valid minimum repair sets = {P} or {Q}

Dropping the entire MFS is therefore a valid repair but can be an over-repair.

The protocol must keep these operations separate:

    failure localization
        -> MFS
        -> repair-set search
        -> MCR
        -> validation

A minimum repair set R must satisfy:

    fail(candidate - R) == false

while minimizing |R|.

The corrected harness explicitly tests proper subsets of the MFS before accepting removal of the whole set.

## 21.4 Consequence for the architecture

The retained architecture is:

    candidate
       |
       v
    coarse localization (ddmin)
       |
       v
    interaction analysis on suspicious cluster
       |
       v
    minimum repair-set search
       |
       v
    replay / generalize / preserve
       |
       +---- PASS ----> converged
       |
       +---- FAIL ----> re-localize residual failure

The distinction is now contractual:

    MFS != MCR

and:

    interaction diagnosis != repair selection

## 21.5 Scaling boundary

The exact Yates interaction pass requires the relevant factorial probes. For k edits, exhaustive factorial evaluation is O(2^k).

Therefore the current evidence justifies:

1. use adaptive/coarse localization on a large candidate set;
2. run exact factorial interaction analysis only inside a small suspicious cluster;
3. search minimum repair sets inside that cluster;
4. validate and re-localize residual faults.

It does not yet establish that fractional designs or screening methods provide an equivalent guarantee at larger k.

A particular caution is required for Plackett-Burman designs: they are primarily main-effect screening designs, and interactions can be aliased with main effects. They should not be treated as a generic interaction detector without an explicit resolution/aliasing analysis.

## 21.6 Verification status of the current follow-up harness

The AND/OR contrast and MFS/MCR conclusions above are recorded from the executed experimental results discussed in the conversation.

The fixed source harness was not independently re-executed by this ChatGPT session after the final code revision because the available user-visible execution tool was temporarily rate-limited. Accordingly, this addendum does not upgrade those follow-up results beyond the evidence already reported in the conversation.

Repository provenance for this addendum:

- repository: Loofy147/Machine
- branch: research/machine-native-primitives-v0
- prior document blob: 4fd7ff629c3d23dd33528fc6d802b908af060b99
- date: 2026-09-21
- raw fixed harness: not committed by this update

## 21.7 Updated claim frontier

### EXPERIMENTALLY_SUPPORTED / USER-REPORTED

- marginal presence/absence gaps can be identical for AND and OR fault structures;
- an interaction contrast can distinguish the demonstrated AND/OR pair under the fixed factorial design;
- ddmin can expose an MFS larger than a minimum repair set;
- whole-MFS deletion is therefore not a generally valid minimal-repair rule.

### OPEN

- adaptive interaction localization at larger candidate-set sizes;
- fractional/sparse interaction designs with explicit aliasing guarantees;
- convergence bounds for repeated multi-fault repair;
- equivalence classes of valid diagnoses across different ddmin search paths;
- challenge-directed validation and independent challenger evidence.

## 21.8 Engineering rule

The durable rule extracted from this correction is:

> Never infer repair directly from a failure-inducing subset.

Instead:

> localize the failure structure -> model interactions -> search the repair space -> validate the repair -> re-localize any residual failure.

This is the correction that should govern subsequent composite-repair experiments.