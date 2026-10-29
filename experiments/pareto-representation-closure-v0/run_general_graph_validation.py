"""Run adversarial general-graph validation and persist the evidence report."""
import json
from pathlib import Path

from general_graph_validation import validate_suite


def main() -> None:
    result = validate_suite()
    output = Path(__file__).with_name("GENERAL-GRAPH-PREDECESSOR-VALIDATION-V0.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
