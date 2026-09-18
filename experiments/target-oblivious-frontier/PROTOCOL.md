# Target-Oblivious Precomputation / Online Computation Frontier v0

Status: EXPERIMENT / EXECUTED

## Question

When future targets are unknown when persistent state is frozen, how much computation must remain after a target is revealed?

This is a resource/capability experiment. It is not yet a proof of reflection or evaluator self-modification.

## Target-oblivious rule

Offline state must be fixed before the realized query target is known:

```
offline computation
    -> freeze state
    -> reveal target
    -> online computation
```

A universal all-target table is legal because it was built before knowing which target will later be queried. A table built after seeing the realized target is not legal offline state.

## Experimental controls

- Target permutation seed: `0x5EED`
- IID query seed: `0xC001`
- Strict-heldout query seed: `0xBEEF`
- Query budget: exact shortest-path length + 2
- Lookahead: fixed depth, budget-capped
- Ground-truth BFS: evaluator-only; not charged to the controller

For prefix size `h`, the first `h` targets of the frozen target permutation are precomputed before query generation.

Strict-heldout targets come from the second half of the permutation, so every `h <= M/2` configuration must have zero cache hits.

## Compared configurations

- `h=0`: no target-specific persistent computation.
- intermediate `h`: exact shortest-path policies for `h` targets.
- `h=M`: exact policy for every target.

Offline work in this graph is exactly `h*M` state expansions and `h*M` action bytes.

## Online accounting

A cached policy performs one constant-time policy lookup per transition.

Fixed-depth lookahead counts expanded recursive nodes. Its depth is clamped by remaining execution budget:

```
further = min(depth, budget - 1)
```

This prevents future-budget leakage.

A full table is therefore O(1) **per transition decision**, not O(1) total time for a whole path.

## Workloads

### IID

Start and target are sampled uniformly with an independent query seed. This measures hit rate and expected online work.

### Strict-heldout

Targets are sampled only from the second half of the frozen target permutation.

For `h <= M/2`:

```
hits = 0
```

Therefore adding offline work that cannot cover the realized target must not change online work or success.

## Validity conditions

The experiment is invalid if:

1. offline state can observe the realized query target;
2. strict-heldout queries produce cache hits for `h <= M/2`;
3. lookahead inspects beyond the remaining budget;
4. the target policy is not shortest-path correct;
5. a partial cache changes strict-heldout behavior despite zero hits.

## Interpretation boundary

The experiment measures where computation is paid:

```
offline state/storage
        <-> 
online computation
```

It does not by itself establish that transition-mechanism modification is necessary.

The remaining question is whether a compact, target-oblivious state plus a fixed executor can close every observed gap under explicit bounds, or whether some capability gap remains that genuinely requires a different transition topology.
