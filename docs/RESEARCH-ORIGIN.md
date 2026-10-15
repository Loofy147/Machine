# Research Origin — Machine

Status: PROVENANCE / OPEN

This document records the questions, observations, thought experiments, and conceptual distinctions that generated the `Machine` research program.

It is **provenance, not evidence**.

A question can motivate an experiment without supporting its answer. A metaphor can expose a missing variable without becoming an architectural primitive. A human description can point toward a machine-operational function without prescribing the implementation.

## 1. Why this project started

The starting problem was not "how do we make a more human-like AI?"

It was closer to:

> What is a machine actually doing when it changes its behavior, uses prior consequences, selects among executable possibilities, and changes the way it operates?

The project therefore began by distrusting human cognitive vocabulary as architecture.

Human concepts are useful observations. They are not automatically machine primitives.

```text
human description
    !=
required machine mechanism
```

The working rule became:

```text
observed requirement
    -> machine-operational function
    -> minimal candidate mechanism
    -> experiment
```

## 2. Machines should be machines

A recurring early principle was:

> Machines should be machines, not human clones.

This does **not** mean that machine behavior cannot have functional analogues of things humans describe as memory, emotion, curiosity, attention, motivation, or reasoning.

It means that the human implementation is not the default implementation target.

The research question becomes:

```text
human phenomenon
    -> what function does it perform?
    -> under what conditions does it alter future behavior?
    -> can a machine implement that function by machine-native means?
```

The same distinction applies to terms such as `intelligence`, `goal`, `memory`, and `feeling`.

## 3. Goals and operation

An early question was whether a machine must always possess or receive a semantic goal in order to operate.

The motivating distinction was:

```text
semantic objective
    !=
condition required for a transition
```

A machine can have a transition because of an explicit condition such as:

- a state change;
- environmental change;
- failure;
- unexpected consequence;
- resource pressure;
- an available experiment;
- inconsistency;
- a scheduled event.

This does **not** establish that useful autonomous operation is possible without objectives. It only establishes the question that the experiments must separate from hidden objective injection.

## 4. The airplane thought experiment

The recurring "jumping from the airplane" thought experiment served as a compact test of the goal/condition distinction.

The human description might use words such as:

```text
fear
urgency
self-preservation
attention
motivation
```

The project does not assume that a machine therefore needs human-like fear or motivation.

The machine-native question is:

> What changes in the operational state when the machine enters a condition where some future consequences become extremely costly, immediate, or irreversible?

A candidate machine description might instead use:

```text
state deviation
+ predicted consequence
+ consequence cost
+ time/resource pressure
+ transition-policy shift
```

This is a **research framing**, not an established architecture.

The thought experiment matters because it suggests that what humans call a feeling may sometimes be a compact description of a large change in the relative significance of possible transitions.

## 5. Early discussion of feelings

The project explicitly considered whether "feelings" could have an operational role.

The useful question was not:

> Should a machine have feelings?

It was:

> What machine-native mechanism could perform whatever operational function makes feelings behaviorally consequential in biological systems?

Potential functions considered include:

- rapidly changing operational significance;
- prioritization under uncertainty;
- persistent bias toward or away from classes of transitions;
- reinforcement of consequences;
- state-dependent exploration or avoidance;
- coordination of many otherwise independent processes.

None of these is currently established as a required primitive.

The current evidence instead suggests that some of these functions may be expressible through ordinary machine state, context-conditioned history, consequence estimates, scheduling, and regime adaptation.

That remains an open research direction.

## 6. Knowledge is not operation

Another original distinction was:

```text
having a representation
    !=
being able to use it during operation
```

This motivated separation between:

- stored representation;
- executable representation;
- transition semantics;
- operational conditions;
- future policy changes.

The later executable-representation experiments emerged from this distinction.

## 7. Changing what is stored vs changing how the machine operates

An early boundary that remained important throughout the project was:

```text
change state contents
    !=
change executable structure
    !=
change the mechanism that determines future execution
```

The x86 mutation experiment established the first important mechanical fact: changing executable representation can change subsequent behavior.

The later adaptive experiments then tested whether search/history could guide such changes.

This sequence was deliberate:

```text
reconfigurability
    -> adaptation
    -> history-dependent proposal
    -> context-conditioned credit
    -> context discovery
    -> causal reflection
```

These are separate claims.

## 8. Why experience became a central question

The early nine-mechanism experiment showed that naive operation-level accumulation could become actively harmful when given enough weight.

That created the question:

```text
What exactly should experience be about?
```

The candidate answer became:

```text
(operation, context/state conditions, transition, consequence)
```

rather than:

```text
score(operation)
```

The contextual-credit experiments subsequently provided testbed-specific evidence that operator credit can remain useful when conditioned on an explicitly supplied context.

The next question is whether the machine can discover such contexts from its own observable state or event history.

## 9. Why reflection entered the project

Once executable representation and online replacement were demonstrated, a sharper boundary appeared.

There is a difference between:

```text
external program replacement
```

and:

```text
an ongoing execution causally changing the machinery
that determines its own subsequent transitions
```

This motivated the reflective frontier.

The target construction is approximately:

```text
Q = <R, S, K, rho, H>
```

where `rho` is not merely described externally but is represented in the causal state consulted by future execution.

The project does not claim that this is the universal minimum. It is an explicit experimental construction for testing causal reflection.

## 10. Research path generated so far

The conceptual lineage can be compressed to:

```text
human cognitive descriptions
        ↓
separate function from implementation
        ↓
machine-native operational questions
        ↓
state / transition / executable representation
        ↓
change executable behavior
        ↓
adaptation and search
        ↓
experience and credit assignment
        ↓
context-conditioned operation
        ↓
context discovery
        ↓
reusable executable structure
        ↓
causal reflection
```

Each arrow is a research gate, not a claim that one stage automatically produces the next.

## 11. What this history does not prove

This origin record does not prove:

- that emotions are required by machines;
- that goals are unnecessary;
- that a machine can become generally intelligent;
- that contextual credit is universally necessary;
- that reflective execution is necessary for learning;
- that the airplane thought experiment maps directly to a specific architecture;
- that human cognitive concepts correspond one-to-one with machine mechanisms.

These remain questions or hypotheses.

## 12. Why preserve the origin

The origin is retained because removing it would erase why the current research questions exist.

It also provides a guard against two opposite errors:

```text
forgetting the original question
        or
mistaking the original metaphor for a proved mechanism
```

The correct relation is:

```text
origin
  -> hypothesis
  -> experiment
  -> result
  -> revision
```

This document records the first part of that chain. The experiment documents record the later parts.
