# Observation–Dynamics Factorization and Conjugacy v0.2

Status: RESEARCH SPECIFICATION / IMPLEMENTED EXPERIMENTS
Date: 2026-09-30
Repository: Loofy147/Machine
Branch: research/observation-dynamics-factorization-v0.1

## 1. Scope

Let (S, τ) be a deterministic finite-state system and h:S→O its observation map.

The question is:

> When does a current observation determine the complete future observation sequence?

The framework separates hidden-state recovery, one-observation observable determinism, infinite-horizon prediction, finite-history recovery/prediction, and the concrete SplitMix64 case.

The factorization/conjugacy framework is standard mathematics. The targeted research contribution is quantitative analysis of lossy observations of a single-cycle SplitMix64 system.

## 2. One-step factorization theorem

Define

s ~h s'  iff  h(s)=h(s').

The observation factors the dynamics when there exists

T:h(S)→h(S)

such that

h∘τ = T∘h.

This is equivalent to the forward-compatibility condition

h(s)=h(s')  ⇒  h(τ(s))=h(τ(s')).

Proof: if T exists, equal observations have equal images under T. Conversely define T(h(s))=h(τ(s)); forward compatibility makes this well-defined.

If one insists on T:O→O, its values outside h(S) may be assigned arbitrarily.

This is the standard factor-map / semiconjugacy construction.

## 3. Infinite-horizon consequence

Once

h∘τ=T∘h

holds,

h(τ^k(s))=T^k(h(s))

for every k≥0.

No additional condition is required. One sufficient observation therefore determines the entire future observation trajectory.

## 4. Bijective case: conjugacy

If f:S→S is bijective, define

T=f∘τ∘f⁻¹.

Then

T^k=f∘τ^k∘f⁻¹.

Thus f is a conjugacy and preserves cycle structure exactly.

For τ(s)=s+c mod M, the permutation has gcd(c,M) cycles, each of length M/gcd(c,M).

For M=2^64 and odd c, it is one cycle of length 2^64.

## 5. Efficient inversion is separate

Bijectivity proves existence and uniqueness of f⁻¹; it does not imply efficient computation.

For practical single-output prediction the concrete requirement is:

f⁻¹ exists and is efficiently computable.

## 6. SplitMix64 instance

Use

γ = 0x9E3779B97F4A7C15

A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB

The exact modular inverses are

A⁻¹ = 0x96DE1B173F119089
B⁻¹ = 0x319642B2D24D8EC3.

The XOR-shift inverses are:

r=31: y⊕(y≫31)⊕(y≫62)
r=27: y⊕(y≫27)⊕(y≫54)
r=30: y⊕(y≫30)⊕(y≫60)

Therefore the mixing function is an exact bijection on all 64-bit words.

With

sᵢ₊₁=sᵢ+γ mod 2^64

and yᵢ=f(sᵢ₊₁), one complete output gives

s₀=f⁻¹(y₀)

and hence

yₖ=f(s₀+kγ mod 2^64).

## 7. Corrected independent conjugacy test

The original proposed test was tautological because both “true” and “formula” expressions reduced to the same expression.

The valid implementation check starts from an independently selected hidden state:

    s = rng.getrandbits(64)
    y = mix64(s)

    true_next = mix64((s + GAMMA) & MASK)
    formula_next = mix64((unmix64(y) + GAMMA) & MASK)

Equality checks consistency between independent state evolution and inverse-derived evolution.

## 8. Lossy observation

For

h_b(s)=low_b(f(s)),  b<64,

every observed value has exactly 2^(64-b) preimages because f is bijective.

Hence one truncated output never uniquely recovers the full state.

But non-injectivity alone does not prove prediction failure.

## 9. One-observation kill condition

A direct counterexample to factorization is

h_b(s)=h_b(s')

but

h_b(τ(s)) ≠ h_b(τ(s')).

Such a witness proves that no deterministic T_b:h_b(S)→h_b(S) can satisfy

h_b∘τ=T_b∘h_b.

Therefore the current truncated observation cannot determine the next truncated observation.

## 10. Finite histories

Define

H_k(s)=(h(s),h(τ(s)),…,h(τ^k(s))).

Let P_k be the partition induced by equality of H_k.

Then P_{k+1} refines P_k.

If

H_k(s)=H_k(s')  ⇒  h(τ^(k+1)(s))=h(τ^(k+1)(s')),

define

F_k(H_k(s))=H_k(τ(s)).

The shifted histories agree in their first k entries automatically, and the final entry agrees by the hypothesis. Therefore F_k is well-defined and

H_k∘τ=F_k∘H_k.

Consequently H_k(τ^n(s))=F_k^n(H_k(s)) for every n≥0.

Thus a stabilized finite history is sufficient for exact infinite-horizon prediction.

## 11. Stabilization theorem

Because S is finite, the nested partition sequence eventually stabilizes.

Define

d=min{k:P_{k+1}=P_k}.

Each strict refinement adds at least one class, starting from |h(S)| classes and ending at most at |S|. Hence

d ≤ |S|−|h(S)|.

For truncated SplitMix64:

d_b ≤ 2^64−2^b.

This is an existence bound, not a practical computational bound.

## 12. State-recovery depth

Define

r=min{k:P_k is discrete}.

If no such k exists, set r=∞.

Therefore finite-state systems always have finite prediction depth, while state recovery may remain impossible.

## 13. Single-cycle observation-period theorem

Suppose τ is one cycle of size M. Label states by

s_n=τ^n(s_*).

The cyclic observation word is

a_n=h(s_n).

Let p be its least cyclic period. Then

s_i ~h s_j  iff  i≡j mod p.

Therefore:

1. the stable observational quotient has exactly p states;
2. each stable class has M/p hidden states;
3. state recovery is possible exactly when p=M.

If p=M, the stable partition is discrete, so

d=r.

If p<M, exact future prediction can still become possible while state recovery remains impossible.

## 14. Universal full-period certificate for 2^64

Every proper divisor of 2^64 divides 2^63.

Therefore, for a single-cycle observation word, one state satisfying

h_b(s) ≠ h_b(s+2^63 mod 2^64)

certifies

p_b=2^64.

For odd γ,

τ^2^63(s)=s+2^63 mod 2^64.

A deterministic machine-checkable witness is:

    s = 0x443CDEF36840FF07
    s + 2^63 = 0xC43CDEF36840FF07

    mix64(s)       = 0x3A2791A602721CD9
    mix64(s+2^63)  = 0x8A3DB804F344A45E

Their XOR has least significant bit 1. Hence their low-b observations differ for every b=1,...,63.

Therefore this single witness certifies

    p_b = 2^64

for every b=1,...,63.

Consequently eventual state recovery is finite for every nonempty truncation width. In the single-cycle setting this also gives

    d_b = r_b

for every b=1,...,63.

The certificate does not determine the minimal depth.

## 15. Implemented experiments

The repository implementation is experiments/observation_dynamics_factorization.py.

It implements:

- E1 inverse constants and round-trip implementation checks;
- E2 independent conjugacy consistency;
- E3 complete-output prediction;
- E4 cycle/trajectory verification for sampled arbitrary bijections;
- E4X exhaustive all-bijection verification for w<=3;
- E5 truncation collision sanity;
- E6 explicit one-observation nonfactorization witnesses;
- E7 full-period certificate;
- E8 exact finite-history partition refinement;
- E9 exact small-state period/quotient consistency.

## 16. Evidence boundary

### ESTABLISHED

- the supplied SplitMix64 inverse constants are correct;
- the explicit XOR-shift inverse identities are exact;
- SplitMix64's mixing function is bijective;
- odd-γ translation modulo 2^64 is one cycle;
- conjugacy preserves cycle structure;
- the one-step factorization criterion is equivalent to forward-compatible observation fibers;
- once finite-history factorization stabilizes, it determines the complete future;
- finite history always stabilizes on a finite deterministic system;
- the stabilization bound is d≤|S|−|h(S)|;
- the single-cycle stable quotient is characterized by observation-word least period;
- one half-period witness certifies full period for a 2^64 single cycle.

### EXPERIMENTALLY_SUPPORTED

The current execution reports:

- E1: 0 round-trip failures in each direction over 200000 random samples; edge cases pass;
- E2: 0 failures over 200000 independent conjugacy checks;
- E3: exact reconstruction of 200 outputs from the first complete output;
- E4: 30/30 sampled arbitrary-bijection cases pass cycle and trajectory checks;
- E5: truncation sanity counts for b=32,16,8;
- E6: explicit conflicting-successor witnesses for b=32,16,8;
- E7: full-period certificates for b=32,16,8;
- E8/E9: exact small-state history and period checks pass in the tested instances.

### OPEN

For the actual 64-bit truncated system, the key unresolved quantitative quantities are

p_b = observation-word least period,
d_b = minimal infinite-horizon prediction depth,
r_b = minimal hidden-state recovery depth,

and the practical complexity of computing or recovering them from truncated observations.

## 17. Research scope

The factor-map, semiconjugacy, conjugacy, and finite partition-refinement constructions are standard.

The intended research contribution is narrower:

> Quantitatively characterize truncated SplitMix64 as a deterministic finite-state observation process.

The target quantities are p_b, d_b, and r_b, together with practical algorithms and complexity bounds for obtaining them.

The central transition is:

“SplitMix64 is invertible”
→
“how much temporal information does a lossy observer need?”
