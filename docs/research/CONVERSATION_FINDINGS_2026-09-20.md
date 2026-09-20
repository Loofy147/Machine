# Conversation Findings Sync — 2026-09-20

Status: DURABLE RESEARCH RECORD
Repository: Loofy147/Machine
Branch: research/evidence-disposition-v0
Base branch head observed before this write: ad68742c880a67f3042ed55557a2e0c31691d9de

Purpose
-------
Persist the durable conclusions and open questions from the September 19–20, 2026 engineering discussion that are relevant to the Machine interpreter/research line. This file records conclusions, evidence boundaries, and next discriminating actions; it is not a transcript.

## 1. Composite-repair finding

Claim: A single ddmin -> analysis -> minimality -> gates pass is insufficient for bundled failures.

Status: EXPERIMENTALLY_SUPPORTED

Finding:
- A bundled candidate can contain an independent standalone bug plus an AND-interaction pair.
- ddmin can return one minimal failing subset and stop while another independent failure remains.
- Therefore “minimal failing subset” is local to one failure witness, not proof that the whole candidate is repaired.

Required repair architecture:
1. Diagnose one failing subset.
2. Produce the smallest repair for that diagnosis.
3. Run correctness, replay, generalization, and preservation gates.
4. If any gate fails, reject/repair accordingly.
5. Re-run diagnosis against the remaining failure set.
6. Repeat until the full acceptance suite has no unresolved failure.

Interpretation boundary:
- This establishes an iterative diagnosis/repair loop for bundled failures.
- It does NOT establish that any particular diagnosis algorithm is globally complete.

Next discriminating action:
- Re-run the bundled independent+interaction fixture and demonstrate that the iterative loop reaches a globally passing candidate while a one-shot ddmin loop under-repairs.

## 2. S2 substrate/interpreter verification

Claim: The repaired substrate-interpreter implementation has post-repair conformance evidence.

Status: EXPERIMENTALLY_SUPPORTED — case/suite scoped

Recorded evidence:
- Repository: Loofy147/Machine
- Branch family: research/substrate-interpreter-v0
- Repair commit: d768ffdea4472ea4c88351f5bd680b8f30bc9152
- GitHub Actions run: #10 / 35466392638
- The unchanged conformance suite was executed after the repair through the S2 workflow.

Interpretation boundary:
- The evidence supports the tested conformance/property surface at that commit.
- It does not establish unrestricted semantic correctness beyond the executed suite.
- External/vendor claims or conversation reasoning do not upgrade this status.

## 3. Property-freeze discipline

Finding:
- Property freezes and post-repair verification must remain tied to exact repository refs and executable workflows.
- A property description in prose is specification debt until the corresponding executable check and provenance are recorded.

Relevant Machine refs discussed:
- ea31e36d85ac8af689282f3840b1d4dff055ed75
- 4de38729c44f03d99c44c9ec7f714e587a7a5a4b
- 61f4286cf695eb7a827a321fccec9...
  (full historical ref retained in repository history where available)

Status: ESTABLISHED as an engineering process rule; individual property claims remain suite-scoped.

## 4. Target-oblivious frontier remains an open research question

Research line:
- research/target-oblivious-frontier-v0

Question:
- What can be represented/verified offline without conditioning on the eventual target, versus what necessarily requires target-conditioned online work?
- Candidate dimensions discussed: bandwidth/representation size, work allocation, and accuracy.

Status: OPEN

Constraint:
- Do not convert a frontier hypothesis into an architecture claim without a discriminating benchmark and an explicit target/measurement definition.

## 5. Evidence/branch reconciliation

Finding:
- Machine research branches are evidence-bearing artifacts, not interchangeable implementation branches.
- The repository/branch/ref/commit tuple is the minimum identity for reusing a result.
- Branch comparisons must be interpreted with exact refs; a conversation summary is not a substitute for repository state.

Relevant branch audit refs discussed:
- main: 1626bac2f5c478294afa4b9463f694608c322117
- research/target-oblivious-frontier-v0: 5decefa... (full ref in repository history)
- research/confirmatory-freeze-order-v0.1: 6f724f... (full ref in repository history)
- current evidence-disposition branch head before this write: ad68742c880a67f3042ed55557a2e0c31691d9de

Status: ESTABLISHED

## 6. Durable engineering-record rule

Every important engineering action must be recoverable from repository history with:
- repository
- branch
- base/head or exact commit
- files/changes
- command or experiment executed
- actual result
- claim/status
- interpretation boundary
- next discriminating action

A conversation-only action is CONVERSATION-ONLY and must not be treated as repository evidence.

Status: ACCEPTED OPERATING INVARIANT

## 7. Current next actions

1. Reproduce and document the composite-repair bundled fixture with both one-shot and iterative repair loops.
2. Keep S2 claims suite-scoped and tied to executable workflow evidence.
3. Define the target-oblivious frontier experiment with measurable B/W/accuracy quantities before implementation claims.
4. Continue branch/ref reconciliation before reusing results across research lines.

## Provenance note

This document was created from the engineering findings preserved in the conversation state and prior repository verification records. It intentionally distinguishes experimentally supported findings from open questions and does not promote unexecuted hypotheses to facts.
