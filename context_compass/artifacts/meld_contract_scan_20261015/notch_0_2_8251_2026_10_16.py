"""Notch the package version for the contracted-copy removal fix (melder_1, 2026-10-16).

usage (from the repository root): python <this script> [--check]
agent_contribution_guide: one notch per landed source change, read at that moment, never reserved in advance; the
notch is 0.0001 in the owner's decimal reading, so 0.2.8250 -> 0.2.8251. Refuses unless the file holds exactly one
`__version__` line and it reads 0.2.8250 (another lane notching first means re-reading, not overwriting). Whoever
notches updates the running release note's header and its rebuild line.
"""
import pathlib
import re
import sys

CHECK = "--check" in sys.argv[1:]
PATH = pathlib.Path("src/melder/__version__.py")
NOTE = pathlib.Path("release_docs/next_version_release.md")
CURRENT = "0.2.8250"
NEXT = "0.2.8251"

raw = PATH.read_bytes()
assert b"\r" not in raw, "__version__.py is not LF"
text = raw.decode("utf-8")
found = re.findall(r'^__version__ = "([^"]+)"$', text, flags=re.M)
assert found == [CURRENT], found
text = text.replace(f'__version__ = "{CURRENT}"', f'__version__ = "{NEXT}"', 1)

note_raw = NOTE.read_bytes()
assert b"\r" not in note_raw, "release note is not LF"
note = note_raw.decode("utf-8")
assert note.startswith(f"# Melder {CURRENT}\n"), note[:40]
rebuild = f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {CURRENT}.\n"
assert note.count(rebuild) == 1, note.count(rebuild)
note = f"# Melder {NEXT}\n" + note[len(f"# Melder {CURRENT}\n"):]
note = note.replace(rebuild, rebuild.replace(CURRENT, NEXT))

if not CHECK:
    PATH.write_bytes(text.encode("utf-8"))
    NOTE.write_bytes(note.encode("utf-8"))
    assert re.findall(r'^__version__ = "([^"]+)"$', PATH.read_text(encoding="utf-8"), flags=re.M) == [NEXT]
    assert NOTE.read_text(encoding="utf-8").startswith(f"# Melder {NEXT}\n")
print(("checked " if CHECK else "notched ") + f"{CURRENT} -> {NEXT}")
