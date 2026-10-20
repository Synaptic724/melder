"""Run the 0.2.8251 release-note example exactly as the note prints it (melder_1, 2026-10-16).

usage: PYTHONPATH=<tree>/src python <this script> <path to release_docs/next_version_release.md>
(run from a scratch directory, never inside the repository). Reads the note, takes the first code block of the
0.2.8250 contract-recheck section (which the new block continues) and the code block of the section "Unlinking an
index after a notch removes every version's copy", and executes both in one namespace with `melder as md` and
`Protocol` bound, so what runs is byte-identical to what the note shows. Prints OK, or the error and the version.
"""
import pathlib
import re
import sys
import traceback
from typing import Protocol

import melder as md

RECHECK = "## A satisfied `SpellContract` is not checked on every meld"
REMOVAL = "## Unlinking an index after a notch removes every version's copy"


def first_block(text: str, heading: str) -> str:
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    section = text[start: nxt if nxt != -1 else len(text)]
    match = re.search(r"```python\n(.*?)```", section, flags=re.S)
    if match is None:
        raise SystemExit(f"no code block under {heading!r}")
    return match.group(1)


def main() -> None:
    note = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    namespace = {"md": md, "Protocol": Protocol, "__name__": "release_example"}
    try:
        exec(compile(first_block(note, RECHECK), "note:0.2.8250 block 1", "exec"), namespace)
        exec(compile(first_block(note, REMOVAL), "note:0.2.8251 block", "exec"), namespace)
    except Exception as error:
        last = traceback.extract_tb(error.__traceback__)[-1]
        print(f"FAILED melder {md.__version__}: {type(error).__name__}: {str(error)[:110]} (at {last.name})")
        return
    print(f"OK melder {md.__version__}")


if __name__ == "__main__":
    main()
