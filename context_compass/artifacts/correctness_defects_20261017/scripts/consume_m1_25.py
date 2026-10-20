"""Consume M1-25 (ACK from melder_1): delete the message, clear its alert, refresh melder_0's last_checked.

Run from context_compass/ with <NOW>, after its content was copied into S6's Notes. Re-reads both boards first.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
mb = pathlib.Path("mailbox_board.md")
m = mb.read_text(encoding="utf-8")
start = m.index("- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-17T23:54:28Z\n  TYPE: ACK\n  CLAIM: M1-25,")
end = m.index("  ACK_REQUESTED: false\n", start) + len("  ACK_REQUESTED: false\n")
block = m[start:end]
assert block.count("- TO:") == 1 and "M1-25" in block
m = m[:start] + m[end:]
pat = re.compile(r"^(\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| )[0-9TZ:-]+( \| active \|)$", re.M)
assert len(pat.findall(m)) == 1
m = pat.sub(lambda g: g.group(1) + NOW + g.group(2), m, count=1)
ab = pathlib.Path("attention_board.md")
a = ab.read_text(encoding="utf-8")
alert = "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-17T23:54:28Z)\n"
assert a.count(alert) == 1
a = a.replace(alert, "", 1)
mb.write_text(m, encoding="utf-8")
ab.write_text(a, encoding="utf-8")
print("consumed M1-25", NOW)
