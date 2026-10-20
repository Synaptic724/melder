"""Content-preservation check of the four system documents this landing edited (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <baseline dir>
The baseline dir holds <doc>.md.orig, each document as it stood before the landing's doc scripts ran. A line is
compared by its normalized text (stripped, inner whitespace collapsed); the check prints, per document, how many
lines left and how many arrived, then every line that left, so each can be accounted for (an edit replaces it, or
it moved). Read-only.
"""
import collections
import pathlib
import re
import sys

BASE = pathlib.Path(sys.argv[1])
DOCS = pathlib.Path("context_compass/system_docs")


def normalized(path):
    text = path.read_bytes().decode("utf-8")
    return collections.Counter(re.sub(r"\s+", " ", line.strip()) for line in text.split("\n") if line.strip())


for name in ("src_architecture", "src_components", "tests_architecture", "tests_components"):
    before = normalized(BASE / f"{name}.md.orig")
    after = normalized(DOCS / f"{name}.md")
    left = before - after
    arrived = after - before
    print(f"=== {name}: {sum(left.values())} lines left, {sum(arrived.values())} arrived")
    for line, count in sorted(left.items()):
        print(f"  LEFT x{count}: {line[:150]}")
