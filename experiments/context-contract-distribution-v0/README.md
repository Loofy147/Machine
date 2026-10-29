# Context Contract Distribution Center v0.1

Offline planning core for matching fact-consistent, dependency-linked contract contexts under a fixed anchor. It emits JSON plans with paired context IDs, directional need witnesses, conflict explanations, a canonical input digest, and deltas after anchor updates.

This is a **research prototype**, not a production contract authority or remote dispatcher. The planner uses existential pair admission (at least one need must be satisfied in one direction) and reports other needs that remain unmet by that partner.

## Run

    python -m pip install -r requirements.txt
    python -m unittest -v
    python run_demo.py

contracts.demo.json mirrors the supplied context fact/need structure, including a second anchor state to demonstrate recomputation. See docs/research/CONTEXT-CONTRACT-DISTRIBUTION-CENTER-v0.1.md for the contract and evidence boundary.
