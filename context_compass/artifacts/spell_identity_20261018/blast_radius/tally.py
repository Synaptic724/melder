"""Tally the blast-radius run: new failures (patched mirror minus baseline), by first error kind, per GIL mode."""
import re
import sys
from pathlib import Path

RUNS = Path("/tmp/m0_mq/br/runs")
OUTCOME = re.compile(r"^(tests/\S.*?) (PASSED|FAILED|ERROR)\b")
HEADER = re.compile(r"^_+ (test\S.*?) _+$")


def outcomes(prefix: str) -> dict:
    result = {}
    for log in sorted(RUNS.glob(prefix + "_*_part*.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            match = OUTCOME.match(line)
            if match:
                result[match.group(1)] = match.group(2)
    return result


def first_errors(prefix: str) -> dict:
    errors = {}
    for log in sorted(RUNS.glob(prefix + "_*_part*.txt")):
        current = None
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            match = HEADER.match(line)
            if match:
                current = match.group(1)
                continue
            if current and line.startswith("E ") and current not in errors:
                errors[current] = line[1:].strip()
    return errors


def kind(text: str) -> str:
    if "Spell ID collision detected" in text:
        return "one object registered twice (bind/bind_inactive collision)"
    if "Conjure refused" in text:
        return "one object registered twice (conjure integrity, another Book/frame)"
    return "other: " + text[:150]


base = outcomes("base")
for gil in ("gil0", "gil1"):
    patched = {}
    for log in sorted(RUNS.glob("br2_*_" + gil + "_part*.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            match = OUTCOME.match(line)
            if match:
                patched[match.group(1)] = match.group(2)
    failed = {t for t, o in patched.items() if o in ("FAILED", "ERROR")}
    base_failed = {t for t, o in base.items() if o in ("FAILED", "ERROR")}
    new = sorted(failed - base_failed)
    fixed = sorted(base_failed - failed)
    print(f"== {gil}: ran {len(patched)}; failed {len(failed)}; baseline failed {len(base_failed)}; "
          f"new {len(new)}; baseline failures now passing {len(fixed)}")
    if gil == "gil0":
        errors = {}
        for log in sorted(RUNS.glob("br2_*_gil0_part*.txt")):
            current = None
            for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
                match = HEADER.match(line)
                if match:
                    current = match.group(1)
                    continue
                if current and line.startswith("E ") and current not in errors:
                    errors[current] = line[1:].strip()
        counts = {}
        others = []
        for test_id in new:
            name = test_id.split("::")[-1]
            k = kind(errors.get(name, "?"))
            counts[k] = counts.get(k, 0) + 1
            if k.startswith("other"):
                others.append(test_id + "  ->  " + k)
        for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"   {v:3d}  {k}" if not k.startswith("other") else "", end="\n" if not k.startswith("other") else "")
        print("   others:")
        for line in others:
            print("     " + line[:260])
        Path("/tmp/m0_mq/br/new_failures_gil0.txt").write_text("\n".join(new) + "\n", encoding="utf-8")
    else:
        Path("/tmp/m0_mq/br/new_failures_gil1.txt").write_text("\n".join(new) + "\n", encoding="utf-8")
a = Path("/tmp/m0_mq/br/new_failures_gil0.txt").read_text().split()
b = Path("/tmp/m0_mq/br/new_failures_gil1.txt").read_text().split()
print("GIL 0 and GIL 1 new-failure sets identical:", a == b)
