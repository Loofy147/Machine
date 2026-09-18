# Machine

Machine-native computation / adaptation research.

## Current phase

This repository is defining an **implementation-independent machine model** before committing to a language, runtime, model architecture, or anthropomorphic cognitive vocabulary.

The project does not assume that a machine should think, feel, attend, remember, or reason in human terms. Human concepts may describe observations later, but they are not accepted as architectural primitives without machine-level evidence.

## Research origin

The current experiments grew out of earlier questions about machine identity, goals, feelings, operational significance, adaptation, and the difference between human descriptions and machine mechanisms.

- `docs/RESEARCH-ORIGIN.md` — conceptual lineage, including the airplane thought experiment and the early questions about feelings, goals, executable behavior, experience, and reflection
- `docs/OPERATIONAL-PHENOMENA.md` — human-described phenomena translated into candidate machine-operational relations and discriminating experiments
- `docs/OPERATIONAL-RELATIONS.md` — candidate machine-native relations, dependencies, and experimental ordering
- `docs/INTELLIGENCE-QUESTIONS.md` — deeper questions about representation, significance, learning, reachable capability space, continuity, and the limits imposed by the machine's own architecture

These documents are provenance and research framing, not evidence. Origin questions motivate experiments but do not establish their answers.

## Current research question

> What is the smallest fixed substrate that permits executable state to change its own future operating regime, while consequences and retained history can affect subsequent changes?

The broader question of machine intelligence remains deliberately downstream of this operational question.

## Current claim frontier

### Experimentally supported in tested regimes

- Executable representations can be changed and subsequently produce different behavior.
- Mutable executable representation is a capability for adaptation, but does not itself provide a search advantage.
- Continuous same-process evaluator hot-swap works in the current prime-stream harness.
- Outcome history bound to operator identity can causally change proposal policy over a fixed candidate palette.
- Context-indexed history can preserve useful credit when a previously encountered context returns, provided the context is supplied explicitly.
- The error-source-localization v0 harness reproducibly separates lower-level injected faults from a representation ceiling under the declared deterministic fixture; this is a harness result, not evidence of causal reflection.

### Not established

- context discovery;
- reusable learned executable structure;
- self-discovery of the adaptation mechanism;
- causal reflection of the evaluator/transition semantics;
- machine-discovered localization of representation/partition failure rather than success by supplied intervention structure;
- general-purpose machine intelligence;
- general machine-native implementations of phenomena described as emotion, curiosity, urgency, identity, or self-preservation.

## Core separation

```text
implementation language
    != operational representation
    != operational semantics
    != physical substrate
```

Python, Rust, C, a VM, an interpreter, native code, or another substrate may be used as research instruments. None is assumed to be the machine's native definition.

Likewise:

```text
human phenomenon
    != human mechanism
    != machine primitive
```

A useful research path is:

```text
human-described phenomenon
    -> operational effect
    -> machine-native candidate relation
    -> controlled experiment
```

And:

```text
reconfigurability
    != adaptation
    != learning
    != reusable learning
    != causal reflection
```

## Research gates

1. Stabilize the abstract transition semantics.
2. Preserve reproducible evidence artifacts for completed experiments.
3. Test the same semantics on independent execution substrates.
4. Validate adaptive mechanisms with controlled ablations and matched budgets.
5. Test contextual credit without supplying context labels.
6. Test operational significance, persistence/decay, prediction error, suppression, ambiguity retention, and model-revision mechanisms as machine-native relations rather than named human faculties.
7. Implement deterministic error-source localization under matched interventions; then remove fixed intervention priors, introduce hidden fault switching, and charge explicit representation cost.
8. Test reusable executable structure on genuinely held-out task families.
9. Test continuity/lineage effects separately from simple retained statistics.
10. Implement the smallest causal-reflection substrate only after the preceding semantics are sufficiently constrained.

## Current documents

- `docs/RESEARCH-ORIGIN.md` — conceptual lineage and original questions
- `docs/OPERATIONAL-PHENOMENA.md` — candidate machine-native relations for human-described operational phenomena
- `docs/OPERATIONAL-RELATIONS.md` — candidate relations, dependencies, and experimental ordering
- `docs/INTELLIGENCE-QUESTIONS.md` — deeper machine-intelligence questions and discriminating directions
- `docs/ABSTRACT-MACHINE.md` — implementation-independent model
- `docs/FOUNDATION.md` — current principles and claim frontier
- `docs/EXPERIMENT-V0.md` — falsifiable experimental program
- `docs/EXPERIMENT-REVIEW-9-MECHANISMS.md` — nine-mechanism ablation review
- `docs/EXPERIMENT-B-CLEAN.md` — clean mutable-executable-representation experiment
- `docs/EXPERIMENT-ONLINE-REFLECTIVE-LEARNING.md` — online reflective-learning design and boundary
- `docs/EXPERIMENT-CONTEXTUAL-CREDIT.md` — context-indexed credit experiment
- `docs/EXPERIMENT-ERROR-SOURCE-LOCALIZATION.md` — deterministic fault-localization and representation-partition experiment
- `experiments/error-source-localization/PROTOCOL.md` — executable v0 protocol and controls
- `experiments/error-source-localization/harness.py` — deterministic harness
- `experiments/error-source-localization/RESULTS-V0.md` — first reproducible run and interpretation boundary
- `docs/REFLECTION-FRONTIER.md` — causal-reflection boundary
- `docs/REFLECTION-SUBSTRATE-LITERATURE-ALIGNMENT_v0.1.md` — literature alignment and first substrate gap audit
- `docs/REFLECTION-SUBSTRATE-REAUDIT_v0.2.md` — current re-audit and narrow dispatch-reflection decision boundary
- `docs/INTERACTION-OPERATING-MODE.md` — project interaction/evidence discipline
- `docs/OPEN-QUESTIONS.md` — unresolved questions

The repository remains research-first. Implementation code should be introduced only as an explicitly named experimental substrate with reproducible evidence attached to its claims.


## Immediate reflection target

The current implementation target is intentionally narrower than whole-evaluator reflection:

```
rho_dispatch = compound-procedure dispatch semantics
```

The immediate proof obligation is causal replacement of this dispatch rule during one uninterrupted computation, with matched controls. Broader evaluator reflection remains OPEN.
