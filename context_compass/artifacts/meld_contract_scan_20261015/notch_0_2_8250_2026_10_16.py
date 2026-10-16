"""Notch the package version for rule 2 (melder_1, 2026-10-16): read `__version__` now and take the next number.

usage (from the repository root): python <this script> [--check]
agent_contribution_guide: one notch per landed source change, read at that moment, never reserved in advance; the
notch is 0.0001 in the owner's decimal reading, so 0.2.8249 -> 0.2.8250. Refuses unless the file holds exactly one
`__version__` line and it reads 0.2.8249 (another lane notching first means re-reading, not overwriting).
"""
import pathlib
import re
import sys

CHECK = "--check" in sys.argv[1:]
PATH = pathlib.Path("src/melder/__version__.py")
CURRENT = "0.2.8249"
NEXT = "0.2.8250"

raw = PATH.read_bytes()
assert b"\r" not in raw, "__version__.py is not LF"
text = raw.decode("utf-8")
found = re.findall(r'^__version__ = "([^"]+)"$', text, flags=re.M)
assert found == [CURRENT], found
text = text.replace(f'__version__ = "{CURRENT}"', f'__version__ = "{NEXT}"', 1)
if not CHECK:
    PATH.write_bytes(text.encode("utf-8"))
    assert re.findall(r'^__version__ = "([^"]+)"$', PATH.read_text(encoding="utf-8"), flags=re.M) == [NEXT]
print(("checked " if CHECK else "notched ") + f"{CURRENT} -> {NEXT}")
