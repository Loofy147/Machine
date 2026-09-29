# Decision Use-Case Gap Audit v0.1

**Status:** BLOCKER CONFIRMED — operational contract absent  
**Branch:** `research/confirmatory-freeze-order-v0.1`

## 1. Finding

The repository has frozen the scientific shape of the primary comparison:

```text
persistence/decay fault -> context-discrimination fault
```

with S2 sequential/adaptive probing and a transfer artifact restricted to diagnosis/probe selection. The repository does **not** currently contain an external operational use case that specifies what a correct diagnosis is worth, what an incorrect diagnosis costs, what incremental resources are acceptable, or what safety/irreversibility bounds apply.

Therefore numeric practical margins cannot yet be derived defensibly.

## 2. Why this is a real blocker

`delta_D` is defined as an operationally important diagnostic-success change. Operational importance requires a decision context.

`delta_R+/-` is defined relative to a practically negligible change in repair-search cost. “Practically negligible” likewise requires an operational resource contract.

Without those contracts, any numeric value would have to come from one of the following invalid shortcuts:

- the exploratory pilot effect;
- a convenient sample size;
- a desired power calculation;
- a conventional arbitrary percentage;
- a post-hoc reading of generated cases.

Those routes would make the practical margin outcome-dependent or otherwise unsupported.

## 3. What the repository does have

The repository already provides the scientific components needed once a use case exists:

- mechanism definitions for `Za` and `Zb`;
- target/transfer arm separation;
- S2 as the primary diagnostic policy;
- repair-controller invariance;
- case-population and twin-audit discipline;
- estimands `theta_D`, `theta_P`, `theta_R`, `theta_V`;
- utility and repair-margin semantics;
- a freeze-order contract.

These are necessary but not sufficient for numerical practical margins.

## 4. Consequence for the current experiment

The current branch should remain a **design candidate** rather than proceeding to confirmatory generation.

The correct next operation is not another statistical calculation. It is to choose or explicitly construct one operational decision context for which the machine capability would matter.

## 5. Acceptable resolution paths

### Path A — Real deployment contract

Identify a real machine/system where the failure loop is operationally meaningful:

```text
failure observation
 -> diagnosis
 -> probe/search choice
 -> repair
 -> independent validation
 -> accept / reject / escalate
```

Then derive the required values from actual resource, safety, delay, and recovery requirements.

### Path B — Explicit research-system contract

If the work is intentionally laboratory-only, declare a bounded synthetic operational contract before confirmatory generation. It must specify:

- what counts as a recovered system state;
- what resource units are consumed by diagnosis/probing/repair;
- what delay matters;
- what failures are safety-invalid rather than merely costly;
- what minimum decision improvement justifies the additional mechanism.

This is a design specification, not empirical evidence, and must be labeled as such.

### Path C — Remove practical-utility claims

The study may remain a purely methodological experiment and stop short of claiming operationally meaningful superiority. In that case, `delta_D`/`delta_R` as practical deployment margins are no longer needed for the stated claim, but the primary estimand and claim must be rewritten accordingly.

This path changes the scientific question and therefore requires a new preregistered design version rather than a silent relaxation.

## 6. Current decision

Do **not** populate the numeric margin fields from existing experimental results.

Do **not** generate confirmatory cases solely to discover what operational values could have been.

First resolve whether the experiment is:

1. deployment-linked,
2. laboratory-contract-linked, or
3. methodological-only.

Only (1) or (2) permits the current practical-margin framework to proceed without changing the scientific claim.

## 7. Relation to the decision-first document

`DECISION_USE_CASE_AND_MARGIN_DERIVATION_V0.1.md` defines how to derive the values once the operational contract exists. This audit establishes why that contract cannot currently be filled from the repository's existing evidence.

## 8. Status labels

- **ESTABLISHED:** numerical margins are not currently justified by the repository evidence.
- **ESTABLISHED:** confirmatory generation is blocked under the current practical-margin claim.
- **OPEN:** which operational contract should govern the experiment.
- **UNKNOWN:** the eventual numerical values after that contract is fixed.
