"""Remeasure the C1 records the tests-doc verification recipe reports as STALE RANGE (melder_0, 2026-09-30).
For each `- path:` record whose end_line no longer matches the file, set end_line and loc to the file's
splitlines() count and stamp verified_at. Usage: python remeasure_test_doc_ranges.py <repo_root> <stamp> <doc>..."""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])
STAMP = sys.argv[2]
for doc_arg in sys.argv[3:]:
    doc = pathlib.Path(doc_arg)
    lines = doc.read_bytes().decode("utf-8").split("\n")
    changed = 0
    i = 0
    while i < len(lines):
        match = re.match(r"^- path: `([^`]+)`$", lines[i])
        if match and (ROOT / match.group(1)).exists():
            measured = len((ROOT / match.group(1)).read_bytes().decode("utf-8", "replace").splitlines())
            j = i + 1
            block = []
            while j < len(lines) and lines[j].startswith("  ") and not lines[j].startswith("- "):
                block.append(j)
                j += 1
            end_rows = [k for k in block if re.match(r"^\s+end_line:\s*\d+$", lines[k])]
            if end_rows and int(lines[end_rows[0]].split(":")[1]) != measured:
                for k in block:
                    if re.match(r"^\s+end_line:\s*\d+$", lines[k]):
                        lines[k] = "  end_line: {0}".format(measured)
                    elif re.match(r"^\s+loc:\s*\d+$", lines[k]):
                        lines[k] = "  loc: {0}".format(measured)
                    elif re.match(r"^\s+verified_at:\s*\S+$", lines[k]):
                        lines[k] = "  verified_at: {0}".format(STAMP)
                changed += 1
                print(doc.name, match.group(1), "->", measured)
            i = j
            continue
        i += 1
    doc.write_bytes("\n".join(lines).encode("utf-8"))
    print(doc.name, "records remeasured:", changed)
