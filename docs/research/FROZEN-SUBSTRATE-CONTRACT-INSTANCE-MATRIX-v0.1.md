# Frozen Substrate Contract Instance Matrix v0.1

This note binds the frozen resource-contract schema to the relevant Machine surfaces.

| Surface | Access profile | Classification consequence |
|---|---|---|
| Abstract Machine | A0/A1/A2 remain admissible; no one is selected | **UNDERDETERMINED** |
| Rev 2.1 | A2 specialized-index | fiber access is a **declared substrate capability** |
| A1 reference implementation | A1 random-access | inverse fiber is **representation-level closure** |
| A0 reference implementation | A0 opaque | inverse fiber requires an **access extension** |

## Interpretation

The contract deliberately freezes the disclosure dimensions without selecting one physical access profile as universally canonical.

Thus:

[
A0 \neq A1 \neq A2
]

as resource/access contracts, even though they can realize the same abstract transition semantics.

The primitive question must therefore be phrased relative to the declared contract:

> Under which admitted access operations is (F(u)) non-derivable?

The repository-level statement "Machine requires predecessor fibers as a primitive" is therefore
not admissible yet.

The branch-level statement "Rev 2.1 exposes predecessor fibers through P-05" is admissible.

The statement "inverse fibers are representation-level closure under generic random-access state"
is admissible for A1.

These statements are compatible.

## Promotion gate

A capability may be promoted to the abstract Machine primitive set only after the project chooses
a production substrate profile and the capability remains non-derivable under that frozen profile.
