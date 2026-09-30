# Observation–Dynamics Method Review v0.1

Status: AUDIT RECORD
Date: 2026-09-30
Branch: research/observation-dynamics-factorization-v0.1

## 1. System reconstruction

The research began as a concrete SplitMix64 inverse/prediction verification.

The sequence of reductions is:

1. SplitMix64 mix is a bijection.
2. Additive state stepping is a finite permutation.
3. Output transition is a conjugate permutation.
4. Bijective output implies exact state recovery from one complete output.
5. For lossy output, state recovery and future prediction must be separated.
6. One-observation prediction is exactly a factorization/forward-fiber compatibility question.
7. Finite observation histories induce nested partitions.
8. On a finite system those partitions stabilize.
9. For a single hidden cycle, the stable quotient is the least period of the cyclic observation word.
10. When the observation period is full, the prediction/recovery depth equals the longest repeated cyclic block length.
11. Truncated SplitMix64 has full observation period for every b=1..63 by one half-period witness.
12. Therefore the remaining 64-bit problem is quantitative: determine minimal depth and practical recovery complexity.

## 2. Important corrections / killed paths

### Killed: tautological conjugacy test

The original test compared

    mix64(unmix64(y) + GAMMA)

against the same expression.

It could not independently validate the inverse-derived transition.

It was replaced by an independently sampled hidden state s.

### Killed: collision counting as a prediction kill test

Truncation collisions prove non-injectivity and loss of unique one-observation state recovery.

They do not prove failure of observable deterministic dynamics.

The explicit conflicting-successor witness was added to kill factorization itself.

### Killed: “history depth is only one-step information”

Once the finite-history factorization condition holds, the induced history transition determines all future observations.

No additional persistence condition is required.

### Corrected: finite-history/LRS reduction

The longest-repeated-cyclic-block reduction only equals the prediction/recovery depth when the cyclic observation word has full period.

A non-full-period word can have repeated arbitrarily long finite blocks because different states may have identical infinite futures.

The implementation therefore requires a full-period check before using the LRS-to-depth reduction.

### Corrected: sampled arbitrary-bijection claim

The sampled permutation experiment was not exhaustive over permutations.

An additional E4X experiment exhaustively checked every bijection and nonzero increment for w<=3.

### Corrected: evidence semantics

Mathematical identities are marked ESTABLISHED.

Executable checks are marked EXPERIMENTALLY_SUPPORTED only after an execution record exists.

A search routine is not evidence that a witness exists until a witness is actually recorded.

## 3. Deeper structural reduction

For

    M = 2^n
    q = 2^b

and a bijection f:[M]->[M], the truncated observation

    h_b(s) = f(s) mod q

produces a cyclic q-ary word in which every symbol occurs exactly

    M/q = 2^(n-b)

times.

Conversely, every q-ary word with exactly this multiplicity for every symbol can be lifted to a bijection f by assigning the M/q distinct full outputs in each residue class to the positions carrying that symbol.

Thus arbitrary bijective scramblers plus b-bit truncation are equivalent, at the observation-word level, to balanced words with equal symbol multiplicities.

A uniformly random bijection induces the uniform balanced-word distribution because every balanced word has exactly

    ((M/q)!)^q

bijection lifts.

This makes the balanced-word ensemble the correct finite-width null model for random bijective scramblers.

## 4. Single-cycle reduction

For a single hidden cycle, let a_i=h(tau^i(s_*)) and let p be its least cyclic period.

Then stable observation equivalence is

    i ~= j iff i == j (mod p).

Hence the stable quotient has p states.

If p=M, the observation is eventually state-separating and

    d = r.

Moreover the exact depth is the maximum length of a repeated cyclic block in the observation word.

The problem therefore admits an exact string-theoretic representation.

## 5. Random-null scaling

For a random string of length N over alphabet Sigma, known results place the expected longest repeated-substring length at first order

    2 log_|Sigma| N + O(1).

This is used only as a benchmark heuristic for the random/balanced null model, not as a theorem about SplitMix64.

Finite balanced-word experiments at widths 10..18 showed depths close to this birthday-scale quantity, with the information bound remaining substantially lower.

Representative three-trial means:

    w=10: b=1 -> 18.33, b=2 -> 10.00, b=4 -> 4.33, b=8 -> 2.00
    w=12: b=1 -> 21.33, b=2 -> 11.67, b=4 -> 5.00, b=8 -> 2.33
    w=14: b=1 -> 25.67, b=2 -> 13.67, b=4 -> 6.67, b=8 -> 3.00
    w=16: b=1 -> 30.33, b=2 -> 16.33, b=4 -> 7.33, b=8 -> 3.33
    w=18: b=1 -> 34.67, b=2 -> 17.33, b=4 -> 8.00, b=8 -> 4.00

The birthday-scale reference is

    ceil(2w/b) - 1.

These observations are consistent with the scale but do not establish an asymptotic law for balanced words or SplitMix64.

## 6. 64-bit prefix probe

A separate local exploratory measurement used a 2^19-length SplitMix64 prefix.

Observed local depth values across three seeds were:

    b=1: 35, 36, 36
    b=2: 20, 18, 19
    b=4: 9, 9, 8
    b=8: 4, 4, 4
    b=16: 2, 2, 2
    b=32: 1, 1, 1

A same-length iid q-ary comparison gave:

    b=1: 40, 36, 36
    b=2: 19, 18, 17
    b=4: 9, 9, 9
    b=8: 4, 5, 4
    b=16: 2, 2, 2
    b=32: 1, 1, 1

These are prefix statistics only. They are not global values of d_b for the 2^64 cycle.

A repeated block inside the prefix is a valid lower-bound witness for the global LRS/d_b. Absence of a repetition in the prefix is not a global certificate.

## 7. Current open frontier

The universal full-period certificate removes the existence question:

    p_b = 2^64 for every 1 <= b <= 63.

Hence

    d_b = r_b < infinity

for every 1 <= b <= 63.

The remaining problem is to determine or tightly bound:

    d_b = r_b,

and to construct a sound practical recovery algorithm from truncated output streams.

The information bound is:

    d_b >= ceil(64/b) - 1.

The random-like birthday benchmark suggests a much larger scale near:

    2*64/b - 1

up to lower-order effects and constants.

Whether actual SplitMix64 follows this benchmark closely, systematically deviates from it, or admits a structural shortcut is OPEN.

## 8. Required next discriminating tests

A useful next experiment must do more than generate more examples.

Priority order:

1. Validate exact small-word LRS/depth equality for all full-period words at very small widths.
2. Characterize the balanced-word null distribution and its finite-size correction to iid birthday estimates.
3. Measure SplitMix64 prefix repeated-block statistics over larger prefixes and multiple seeds.
4. Build a sound 64-bit constraint solver for truncated observations.
5. Search for structural proofs or counterexamples to the empirical depth scaling.

Do not turn prefix uniqueness into a global proof.

Do not turn agreement with the random null into evidence of cryptographic randomness.

Do not infer the exact 64-bit depth from small-width interpolation.

## 9. Evidence and provenance rule

Every future result must record:

    repository
    branch
    commit
    command
    parameters
    seed
    state/observation width
    execution duration
    raw result
    interpretation
    remaining limitation

A conceptual claim without these fields remains UNKNOWN/OPEN when the fields are needed to distinguish competing explanations.

## 10. Solver boundary

A sound recovery result for a fixed finite observation history requires two checks:

1. satisfiable: at least one 64-bit state matches every observed b-bit output;
2. uniqueness: after blocking that model, the solver returns UNSAT.

SAT for a second model proves ambiguity.

UNKNOWN, timeout, parser failure, or infrastructure failure does not prove either side.

The repository therefore records solver status as:

    unique
    ambiguous
    unsat
    unknown

Only the first two are substantive state-count outcomes, and both require the corresponding solver certificates.

The Z3 experiment encodes the complete 64-bit SplitMix64 mix as bit-vector arithmetic, including modular multiplication through fixed-width bit-vectors. No floating-point arithmetic or probabilistic hash is used.
