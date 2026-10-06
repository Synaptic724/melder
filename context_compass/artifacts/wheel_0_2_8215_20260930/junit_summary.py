"""Summarise one or more junit XML files: totals and every non-passing case.

Usage: python junit_summary.py <xml> [<xml> ...]
"""
import sys
import xml.etree.ElementTree as ET

totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
bad = []
for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    for suite in root.iter("testsuite"):
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    for case in root.iter("testcase"):
        for kind in ("failure", "error"):
            node = case.find(kind)
            if node is not None:
                message = (node.get("message") or "").splitlines()[0][:160] if node.get("message") else ""
                bad.append(f"{kind.upper()} {case.get('classname')}::{case.get('name')} - {message}")
passed = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
print(f"tests {totals['tests']}: passed {passed}, failed {totals['failures']}, errors {totals['errors']}, "
      f"skipped {totals['skipped']}")
for line in bad:
    print(line)
