# Production Substrate Profile Discriminator v0.1

Status: **LOCAL REPLAY PASS / CI STATUS NOT YET OBSERVED / DECISION GATED**

Recorded: 2026-09-27

## Question

The frozen resource contract permits three state-addressing profiles:

- **A0_OPAQUE** — no direct internal state addressing.
- **A1_RANDOM_ACCESS** — generic indexed reads over ordinary machine state.
- **A2_SPECIALIZED_INDEX** — dedicated inverse-fiber access such as `fiber_lookup(u)`.

The existing Rev 2.1 substrate is already documented as **A2** because P-05 exposes fiber lookup explicitly. That is a concrete-interface fact.

The unresolved architectural question is different:

> What is the minimum access capability that should be frozen as the production Machine substrate contract?

## Discriminating hypothesis

The experiment tests whether the inverse-dependent workload family closes under A1 without adding a semantic fiber primitive.

Required workload family:

1. predecessor enumeration;
2. backward-basin reachability;
3. retrograde value computation;
4. mixed bidirectional reachability.

All profiles use the same transition system, target queries, target-oblivious inverse representation, and semantic references.

## Interpretation rules

### A0

A0 can still compute inverse results by repeated forward probing. Therefore A0 is not semantically incapable of the workloads in an unrestricted computation model.

Its distinction is an **access/resource boundary**: it cannot consume persistent inverse representation through the machine interface.

### A1

A1 permits the inverse CSR representation to remain ordinary state. The inverse fiber is reconstructed using generic reads, arithmetic, and finite iteration.

If all required workloads close semantically, A1 is the **minimal generic access profile** for this workload family.

### A2

A2 exposes inverse-fiber access directly.

If A1 already closes the workload family, A2 is not required for semantic closure. It remains a valid concrete optimization/interface contract whose extra semantic specialization must be justified separately.

## Production decision gate

The experiment does **not** select a production profile merely from measured speed.

After execution, profile selection must use two separate questions:

1. **Capability minimum:** what is the least specialized profile that closes the frozen production workload set?
2. **Resource envelope:** under the actual production limits for online work, persistent representation, preprocessing, and mutation, which profile(s) are admissible?

Local execution closed the tested inverse workload family for A0/A1/A2 with zero semantic failures. This does not by itself freeze the production profile. Until the production resource envelope is frozen, the repository-wide canonical production profile remains **OPEN**.

## Observed local result\n\nThe committed discriminator was replayed independently with the following outcome:\n\n- 60 systems across 6 generated families.\n- 4 inverse-dependent workload classes.\n- semantic failures: A0=0, A1=0, A2=0.\n- aggregate access work: A0=169090253, A1=976186, A2=488093.\n- A0/A1 = 173.2152x.\n- A1/A2 = 2.0x under the declared access-count model.\n\nIndependent checks added outside the primary run covered 100 additional systems × 20 targets with 0 semantic failures, and 1000 degree values with 0 violations of the declared A1/A2 cost relation.\n\nTherefore the present evidence supports this narrower statement:\n\n> **A1 is sufficient and is the least semantically specialized profile tested for the inverse workload family; A2 is not necessary for semantic closure, but remains the explicit Rev 2.1 interface.**\n\nThis is still not a repository-wide production decision because the actual production resource envelope and mutation requirements have not been frozen.\n\n## Expected result categories

- **A1 closes + A2 not required:** inverse access is representation/resource closure at the minimal generic level; Rev 2.1 may remain A2 as a concrete specialized interface.
- **A1 fails while A2 closes:** specialized inverse access is necessary under the frozen abstract workload contract.
- **A0 acceptable under production online budget:** the inverse index is an optional optimization rather than a substrate requirement.
- **Contracts or workload semantics mismatch:** **INCONCLUSIVE**.

## Provenance

Parent branch:

`research/machine-substrate-primitive-closure-v0`

Parent contract repair:\n\n`c0fd531cfd0d447e321ed552770ac4b77c4cb95a0`\n
Concrete Rev 2.1 contract instance:

`experiments/machine-substrate-resource-contract-v0/CONTRACT-INSTANCES-v0.1.json`

The corresponding concrete instance declares:

`A2_SPECIALIZED_INDEX`

and `P05_FIBER_LOOKUP`.

