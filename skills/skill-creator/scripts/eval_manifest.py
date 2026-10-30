#!/usr/bin/env python3
"""Static check for a skill evaluation manifest; does not execute model evals."""
import json
import sys
from pathlib import Path

VALID_TYPES = {"positive", "negative", "ambiguous", "failure", "adversarial", "regression"}
VALID_STATUS = {"NOT_RUN", "PASS", "FAIL", "INCONCLUSIVE"}

def validate(folder, manifest):
    root = Path(folder)
    if not (root / "SKILL.md").is_file():
        raise ValueError("Missing SKILL.md")
    data = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if not isinstance(data.get("skill"), str) or not data["skill"]:
        raise ValueError("Missing skill ID")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("At least one case is required")
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or not all(k in case for k in ("id", "type", "prompt", "expected_skill", "status")):
            raise ValueError("Invalid evaluation case")
        if not isinstance(case["id"], str) or not case["id"] or case["id"] in seen:
            raise ValueError("Missing/duplicate case ID")
        seen.add(case["id"])
        if case["type"] not in VALID_TYPES or case["status"] not in VALID_STATUS:
            raise ValueError("Invalid type/status")
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError("Empty prompt")
        if case["expected_skill"] is not None and not isinstance(case["expected_skill"], str):
            raise ValueError("Expected skill must be string or null")
    return len(cases)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: eval_manifest.py <skill-folder> <manifest.json>")
        raise SystemExit(2)
    try:
        print(f"Manifest valid: {validate(sys.argv[1], sys.argv[2])} cases (behavior NOT tested)")
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"Manifest invalid: {e}")
        raise SystemExit(1)
