# Observation–Dynamics Factorization — Execution Record v0.1

Repository: Loofy147/Machine
Branch: research/observation-dynamics-factorization-v0.1
Base commit: 1626bac2f5c478294afa4b9463f694608c322117
Execution date: 2026-09-30
Execution environment: local Python 3 execution container. Direct git cloning was unavailable in this environment; the experiment source was reconstructed and executed locally, then committed to the research branch.

Command:

    python3 experiments/observation_dynamics_factorization.py --history-width 6 8 10

## E1 — inverse implementation

    A_inv_match=True
    B_inv_match=True
    A_inverse_identity=True
    B_inverse_identity=True
    gamma_odd=True
    roundtrip_failures_forward=0
    roundtrip_failures_backward=0
    edge_ok=True
    samples=200000

Interpretation: implementation agrees with the exact inverse construction for the sampled inputs and edge cases. The inverse theorem itself is algebraic, not statistical.

## E2 — independent conjugacy

    failures=0
    samples=200000

The test uses an independently sampled hidden state and therefore is not the tautological original comparison.

## E3 — complete-output prediction

    length=200
    matches=True

The complete future trajectory was reconstructed from the first complete output under the increment-then-output convention.

## E4 — abstract sampled-bijection conjugacy

    cases=30
    all_pass=True

Widths tested: 4, 6, 8, 10, 12, 14.

For every sampled arbitrary bijection and tested increment, the entire state space was checked for cycle partition equality, predicted cycle structure, and tracked trajectory consistency.

This is exhaustive over each sampled instance, not exhaustive over all bijections.

## E4X — exhaustive all-bijection check for w<=3

A true exhaustive enumeration was executed independently in a Python analysis environment.

    total_bijection_increment_instances=282314
    all_pass=True

Breakdown:

    w=1:  2! permutations × 1 increment = 2 instances
    w=2:  4! permutations × 3 increments = 72 instances
    w=3:  8! permutations × 7 increments = 282240 instances

Every instance checked:

- complete cycle partition equality;
- the analytic cycle-count formula;
- all-state trajectory consistency.

This upgrades the abstract computational check from sampled arbitrary permutations to exhaustive verification for every permutation and nonzero increment at widths w<=3.

## E5 — truncation sanity

    b=32: trials=300000, distinct=299991, repeated_arrivals=9
    b=16: trials=300000, distinct=64835, repeated_arrivals=235165
    b=8:  trials=300000, distinct=256, repeated_arrivals=299744

These are sanity counts only. Exact fiber size follows mathematically:

    |h_b^{-1}(y)| = 2^(64-b).

## E6 — one-observation nonfactorization witnesses

### b=32

    attempt=1
    state1=10321627982211562813
    state2=10489230354334490811
    same_observation=973694259
    next1=1568280146
    next2=320490501

### b=16

    attempt=1
    state1=11479291213973013416
    state2=10944506842384050698
    same_observation=63399
    next1=6132
    next2=3067

### b=8

    attempt=1
    state1=7143951859107569535
    state2=489083623732659671
    same_observation=209
    next1=30
    next2=12

For each row:

    h_b(state1) = h_b(state2)

but

    h_b(tau(state1)) != h_b(tau(state2)).

Therefore one-observation factorization fails for each tested width.

## E7 — universal full-period certificate

A single deterministic witness state is sufficient for every truncation width 1..63:

    witness_state = 0x443CDEF36840FF07
    half_period_state = 0xC43CDEF36840FF07

    mix64(witness_state)          = 0x3A2791A602721CD9
    mix64(half_period_state)      = 0x8A3DB804F344A45E
    xor                           = 0xB01A29A2F136B887

The least significant bit changes:

    1 -> 0

Therefore the truncated observations differ for every b>=1:

    low_b(mix64(witness_state))
    !=
    low_b(mix64(half_period_state))

for all b=1,...,63.

Because every proper divisor of 2^64 divides 2^63, the half-period inequality certifies:

    p_b = 2^64

for every truncation width b=1,...,63.

Consequences:

- eventual state recovery is finite for every nonzero truncation width;
- in the single-cycle setting, d_b = r_b for every b=1,...,63;
- the unresolved problem is the minimal depth/complexity, not whether finite recovery exists.



## E8 — exact history refinement

### w=6, M=64, observation=3 bits

    depth 0: classes=8,  largest_fiber=8, discrete=False
    depth 1: classes=43, largest_fiber=3, discrete=False
    depth 2: classes=62, largest_fiber=2, discrete=False
    depth 3: classes=64, largest_fiber=1, discrete=True
    depth 4: classes=64, largest_fiber=1, discrete=True, stable=True

    d=3
    r=3

### w=8, M=256, observation=4 bits

    depth 0: classes=16,  largest_fiber=16, discrete=False
    depth 1: classes=169, largest_fiber=4, discrete=False
    depth 2: classes=245, largest_fiber=2, discrete=False
    depth 3: classes=255, largest_fiber=2, discrete=False
    depth 4: classes=256, largest_fiber=1, discrete=True
    depth 5: classes=256, largest_fiber=1, discrete=True, stable=True

    d=4
    r=4

### w=10, M=1024, observation=5 bits

    depth 0: classes=32,   largest_fiber=32, discrete=False
    depth 1: classes=654,  largest_fiber=5,  discrete=False
    depth 2: classes=1011, largest_fiber=2, discrete=False
    depth 3: classes=1024, largest_fiber=1, discrete=True
    depth 4: classes=1024, largest_fiber=1, discrete=True, stable=True

    d=3
    r=3

The partitions are nested and the reported stabilization depth is the first depth d for which P_(d+1)=P_d.

## E9 — single-cycle period/quotient consistency

    w=4:  M=16,   least_period=16,   stable_quotient=16,   d=2, r=2
    w=6:  M=64,   least_period=64,   stable_quotient=64,   d=3, r=3
    w=8:  M=256,  least_period=256,  stable_quotient=256, d=3, r=3
    w=10: M=1024, least_period=1024, stable_quotient=1024, d=3, r=3

In every tested instance the least observation-word period equals the stable quotient size, as predicted.

## Evidence boundary

ESTABLISHED:
- exact inverse algebra;
- exact truncation fiber sizes;
- factorization and conjugacy theorems;
- finite history stabilization on finite deterministic systems;
- single-cycle period/quotient theorem;
- half-period full-period certificate.

EXPERIMENTALLY_SUPPORTED:
- the implementation checks and executions recorded in E1–E9;
- explicit nonfactorization witnesses for b=8,16,32;
- full-period certificates for b=8,16,32;
- exact small-state history/period measurements reported above.

OPEN:
- exact 64-bit values d_b and r_b;
- minimal observation history depth for b=1..63;
- scalable algorithms for computing p_b/d_b/r_b without enumerating the 2^64 orbit;
- practical state recovery and prediction complexity from truncated streams;
- whether minimal recovery depth follows a tractable asymptotic law in b.

## Next discriminating implementation work

1. Add exhaustive all-permutation checks for w<=3.
2. Add a direct partition-refinement engine that reports the first stabilization transition explicitly.
3. Add scalable cyclic-period algorithms without materializing the full 2^64 observation word.
4. Add sound bit-vector/SAT/SMT state-recovery experiments for truncated 64-bit streams.
5. Freeze every future execution with branch, commit, command, seed, parameters, runtime, and raw output.
