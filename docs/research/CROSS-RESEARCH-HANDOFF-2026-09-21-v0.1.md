# Cross-Research Handoff — 2026-09-21

Repository: Loofy147/Machine
Recorded: 2026-09-21

## Final research refs

Bidirectional verification:
- branch: research/bidirectional-grounded-verification-v0
- head: cc61765d6939788ab9c075f04ec3572203c89347

Bidirectional ledger reconciliation:
- branch: research/bidirectional-ledger-reconciliation-v0
- head: f9091636bd96aeb874a931ba0cdff349f853149f

Substrate Rev 2.1 implementation:
- branch: research/substrate-rev2.1-v0
- head: 6694f00b0d6619acf9ec92b97989e2b66508d2e8

Historical M* source archive:
- docs/archive/MSTAR-VERIFICATION-DOCKET-v3.4.md

Rev 2.1 reconciliation:
- docs/SUBSTRATE-REV2.1-RECONCILIATION-v0.1.md

## Current durable state

1. Rev 2.1 target signature:
   M = (S, Sigma, delta, R, C)

2. Historical Phi / R+_opt / Pi constructs are archived and explicitly excluded from Rev 2.1.

3. Player ownership and CPre semantics are explicit.

4. Attractor multiplicity convention is owned by Fiber.deduped; no external (fiber,counter) pair is accepted.

5. Bidirectional weighted/exhaustive verification is durable on its dedicated branch, including the post-edge naive-guard regression and matched simple/multigraph experiment.

6. The original 15-claim ledger is not fabricated. The exact claims_revised.yaml source was not recoverable from the inspected repository/file surfaces. A migration gate records the known demo anchors and leaves the remainder pending.

7. The named original harnesses were not found in the inspected Machine repository trees. The v0.4 replacement runner is distinct and must not be presented as a silent reproduction of those original scripts.

## Resume order

Start with:
1. this handoff;
2. exact branch and head;
3. linked artifact;
4. reproduce before changing claim status.

Do not rely on conversation memory as the canonical research record.
