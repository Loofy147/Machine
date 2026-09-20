
# Substrate–Frontier Contract v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/evidence-disposition-v0
Status: RESEARCH CONTRACT / SPECIFICATION DEBT
Purpose: make capability, representation, access, timing, and resource claims precise enough to test without relying on mechanism names.

## 1. Core statement

The current evidence supports the following bounded statement:

Direct predecessor access is a resource-favorable access mechanism that can shift the resource-bounded online frontier under a particular substrate/resource contract.

This does not by itself establish a new absolute computational capability.

Whether direct predecessor access is:
1. a new substrate capability,
2. an efficient implementation of information already representable in state, or
3. merely a different allocation of computation,

depends on the exact fixed substrate contract.

## 2. Separate the four questions

Every frontier comparison must separately specify:

    A. Information
       What relation/information is available?

    B. Timing
       When may that information be constructed or revealed?

    C. Representation
       How may the information be stored?

    D. Access
       How may the fixed substrate read, interpret, and transform it?

A fifth dimension is required for conclusions about efficiency:

    E. Cost
       What resource is charged for each access/operation?

A change in any one of these can move the measured frontier without implying a change in ultimate computability.

## 3. Fixed substrate contract

Represent the fixed substrate as:

    Sigma = (
      transition primitives,
      state primitives,
      relation/data primitives,
      control primitives,
      observation/result semantics,
      cost model
    )

For the present question, the minimum state-access contract must explicitly answer whether Sigma contains:

    read_state(address_or_key)
    write_state(address_or_key, value)
    compare(a, b)
    branch(condition)
    iterate(container)
    construct(container_or_relation_entry)
    retrieve_relation_entry(relation, key)
    enumerate_relation(relation)
    interpret_relation_entry(entry)

The exact names are irrelevant. The semantic capabilities are not.

## 4. Three substrate regimes

### S0 — opaque state

State can persist information, but the fixed substrate cannot generically inspect arbitrary stored relations.

Under S0:

    adding generic relation access
    =
    substrate extension

A reverse index stored in state is inert unless a new access/interpretation mechanism is added.

### S1 — generic readable state

The fixed substrate already permits:

    read + compare + branch + iterate

and can construct/read ordinary data structures.

Under S1, finite relation lookup is derivable as ordinary computation over state.

Therefore:

    direct relation lookup
    =
    potential resource optimization
    not automatically a new semantic capability

### S2 — indexed relation access

The substrate additionally provides direct indexed relation access.

Under S2, lookup may occupy a better resource point than the S1 scan while preserving the same semantic relation.

This is a resource distinction unless the added index access changes the admissible task set under the declared resource contract.

## 5. Target-oblivious representation

A preprocessing function is target-oblivious when:

    P(instance, configuration)

is computed before the target/query is revealed and does not depend on that target.

Online computation then has the form:

    A(P(instance), target)

This distinction is required because moving target-dependent computation into "offline" work would contaminate the frontier comparison.

## 6. Resource vector

The current minimum resource vector is:

    (B_off, R, B_on)

where:
- B_off = preprocessing/representation-construction work;
- R = persistent representation size;
- B_on = post-instance-reveal online work.

For direct relation mechanisms, this vector is incomplete unless access cost is defined.

Therefore the next specification revision should support:

    C_access

or an equivalent cost function that charges:
- relation lookup itself;
- relation enumeration;
- number of returned neighbors;
- comparisons/scans required by an index;
- any hidden preprocessing or cache construction.

No mechanism receives "free" information merely because the benchmark implementation exposes it as a primitive.

## 7. Frontier definitions

For fixed task family T, admissible inputs I, and query set Q, define:

    F_Sigma(T, Q)
    =
    resource vectors under which the fixed substrate Sigma
    can satisfy the correctness contract.

A mechanism/representation is frontier-equivalent on a tested domain when its observed success pattern and required resource budgets match another method under the same declared contract.

The following levels must not be conflated:

Exact finite closure:
Same success pattern and same minimum measured online budgets on the tested finite workload.

Family closure:
The same equivalence holds across independently generated instances of the declared family.

General closure:
The representation/interpreter construction is shown to reproduce the mechanism across the relevant class of substrates/tasks, not merely one finite fixture.

Asymptotic closure:
The resource transformation is characterized as problem size grows.

Current reverse-index evidence reaches only:

    EXACT FINITE CLOSURE

for the tested arithmetic graph family.

## 8. Representation closure criterion

A mechanism m is representation-closed under substrate Sigma for a declared workload if there exists a target-oblivious representation constructor P and fixed executor A such that:

    A(P(instance), target)

matches the mechanism's required semantics and the declared frontier point within the allowed resource accounting.

This definition deliberately asks for a representation and an interpreter.

Stored information alone is not executable capability.

## 9. Current evidence mapped to the contract

Target-oblivious precomputation:
    target-oblivious state
    can relocate computation from B_on
    to B_off + R.

Direct predecessor access:
    resource-favorable access mechanism
    that shifts the sampled online frontier
    under B_off=0, R=0.

Reverse-index state:
    exact finite representation closure
    of the native predecessor frontier
    when generic stored-relation traversal is permitted.

All-pairs policy:
    a much richer target-oblivious representation
    that can reduce online search further
    at approximately Theta(M^2) preprocessing/storage
    in the tested finite graph.

## 10. What is not established

The present evidence does not establish:

    "predecessor access is fundamentally more powerful than state mutation"

It also does not establish:

    "every predecessor mechanism is representable compactly"

or:

    "a finite reverse-index closure is a general closure theorem."

The missing proof obligations are:
1. exact concrete state-access semantics of the Machine substrate;
2. explicit cost of direct predecessor access;
3. stronger successor-only representations;
4. independently generated graph families;
5. compact encodings between raw reverse index and all-pairs policy;
6. family/asymptotic closure rather than one finite arithmetic family.

## 11. Decisive Machine-substrate audit

The next experiment must operate on the actual interpreter substrate, not an abstract toy substrate.

For the fixed Machine implementation, record:

    State representation
    State read/write operations
    Equality/comparison
    Branching/control
    Iteration
    Collection construction
    Relation entry representation
    Relation traversal
    Relation interpretation
    Closure/application semantics
    Per-operation cost

Then run a minimal pair.

Control:
    Use only the fixed substrate and no direct relation primitive.

Treatment:
    Add only direct indexed relation access.

Keep identical:
    instance
    target
    correctness
    timing of target revelation
    persistent storage budget
    online budget
    executor semantics

Measure:

    (B_off, R, B_on, C_access)

and the full success frontier.

## 12. Decision rule

Case A:
If relation traversal is derivable from fixed substrate primitives and direct lookup only changes cost:

    classification = resource primitive / optimization

Case B:
If relation traversal itself requires a capability not in the fixed substrate:

    classification = substrate extension

Case C:
If both are derivable but no tested admissible representation can match the direct mechanism under a specified resource contract:

    classification = resource-bounded frontier advantage
    status = representation closure OPEN

This is not an absolute computability separation.

## 13. Important failure modes

The following must be treated as explicit threats to validity:

1. Free-oracle confound: direct predecessor access may hide an uncharged information-access cost.
2. Interpreter confound: a representation may appear executable only because the benchmark silently grants a generic relation interpreter.
3. Timing confound: target-dependent preprocessing may accidentally enter the offline budget.
4. Finite-closure overclaim: equality on one finite graph family is promoted to a general theorem.
5. Baseline weakness: failure of one successor-only algorithm is treated as failure of the whole successor-only substrate.
6. Storage blindness: B_on alone is optimized while B_off and R are ignored.
7. Output-cardinality blindness: returning many predecessors may have hidden cost unless output-sensitive access is charged.
8. Mechanism-name reasoning: "bidirectional", "lookup", "memory", or "reflection" is treated as a capability class before the contract is specified.

## 14. Refined governing principle

Measure the Pareto frontier under an explicit substrate contract. Then determine whether the frontier shift is caused by new information, new information access, different timing, different representation, or different computational cost.

Mechanism names are labels for implementation choices.

They are not capability classes.

## 15. Current status

    target-oblivious computation relocation       EXPERIMENTALLY_SUPPORTED
    direct-predecessor frontier shift              EXPERIMENTALLY_SUPPORTED
    reverse-index finite closure                   EXPERIMENTALLY_SUPPORTED
    all-pairs online-cost reduction                EXPERIMENTALLY_SUPPORTED
    mechanism-category absolutism                  REFINED / NOT SUPPORTED
    fixed Machine state-access contract            OPEN / SPECIFICATION DEBT
    direct-predecessor capability classification   OPEN

## 16. Immediate next action

Do not expand the reflective substrate yet.

First:

    audit actual Machine substrate
    -> freeze concrete access contract
    -> charge direct-access cost
    -> run derived-vs-direct minimal pair
    -> measure full Pareto frontier
    -> update claim disposition

Only then classify direct predecessor access as optimization, representation closure, or substrate extension.
