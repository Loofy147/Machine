#!/usr/bin/env python3
"""Run the demo contract distribution and show the anchor-update delta."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from context_contract_distribution import compare_plans, load_spec, plan_distribution


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?", type=Path, default=Path(__file__).with_name("contracts.demo.json"))
    args = parser.parse_args()

    with args.spec.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    contexts, anchor = load_spec(data)
    initial = plan_distribution(contexts, anchor)
    result = {"initial_plan": initial.to_dict()}

    anchor_update = data.get("anchor_update")
    if anchor_update:
        updated_anchor = dict(anchor)
        updated_anchor.update(anchor_update)
        updated = plan_distribution(contexts, updated_anchor)
        result["anchor_update"] = {
            "new_anchor": updated_anchor,
            "plan": updated.to_dict(),
            "delta": compare_plans(initial, updated).to_dict(),
        }

    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
