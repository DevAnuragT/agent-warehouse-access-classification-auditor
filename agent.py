#!/usr/bin/env python3
"""Deterministic evidence reviewer."""
import json, sys
from datetime import date
from pathlib import Path
DOMAIN = 'Warehouse Access Classification Auditor'
FIELDS = {'datasets': {'label': 'datasets', 'kind': 'list', 'minimum': 1}, 'classifications': {'label': 'classifications', 'kind': 'object', 'minimum': 1}, 'role_grants': {'label': 'role grants', 'kind': 'list', 'minimum': 1}, 'approval_evidence': {'label': 'approval evidence', 'kind': 'required', 'minimum': 0}}

def valid(value, kind, minimum):
    missing = value is None or value == "" or value == [] or value == {}
    if kind == "required": return not missing
    if kind == "text": return isinstance(value, str) and len(value.strip()) >= minimum
    if kind == "list": return isinstance(value, list) and len(value) >= minimum
    if kind == "object": return isinstance(value, dict) and len(value) >= minimum
    if missing: return False
    if kind == "number": return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= minimum
    if kind == "date":
        try: date.fromisoformat(value); return True
        except (TypeError, ValueError): return False
    raise ValueError("Unknown rule kind: " + kind)

def audit(payload):
    if not isinstance(payload, dict): raise TypeError("Input must be a JSON object")
    findings, passed = [], 0
    for field, rule in FIELDS.items():
        value = payload.get(field)
        if valid(value, rule["kind"], rule["minimum"]):
            passed += 1
        else:
            findings.append({"rule": field, "severity": "review", "message": "Insufficient " + rule["label"] + " evidence", "evidence": value, "action": "Provide evidence satisfying " + rule["kind"] + " rule."})
    total = len(FIELDS)
    return {"agent": DOMAIN, "status": "pass" if passed == total else "needs-review", "score": {"passed": passed, "total": total}, "findings": findings, "checked_rules": list(FIELDS)}

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    payload = json.loads(path.read_text(encoding="utf-8") if path else sys.stdin.read())
    print(json.dumps(audit(payload), indent=2, sort_keys=True))
