"""
Run the running release note's two notch examples as written, each in a fresh interpreter, and check the quoted
refusal messages of the 0.2.8249 section (TASK-2026-10-16-public_notch_target_for_staged_versions).

The examples are taken from release_docs/next_version_release.md itself - the python block of the S8 section ("A
version staged before `conjure` melds after a notch", whose notch is a real call by id since 0.2.8249) and of the
0.2.8249 section - and run verbatim after `import melder as md`. Each runs in its own process because both build
named roots in a fresh world.

Run from the repository root:  python -X gil=0 <this file>  (and -X gil=1); PYTHONPATH=src
"""
import os
import pathlib
import re
import subprocess
import sys

S8 = "## A version staged before `conjure` melds after a notch"
NOTCH = "## `notch_spell` takes the version's id, and refuses a version that is not the index's"


def block_of(heading: str) -> str:
    """
    Return the first python block under a release-note heading.

    Args:
        heading: The section's heading line.

    Returns:
        str: The block's source.
    """
    note = pathlib.Path("release_docs/next_version_release.md").read_text(encoding="utf-8")
    assert note.count(heading + "\n") == 1, heading
    section = note.split(heading + "\n", 1)[1].split("\n## ", 1)[0]
    return re.search(r"```python\n(.*?)```", section, re.S).group(1)


def run_block(name: str, source: str, tail: str) -> str:
    """
    Run one example in a fresh interpreter with the same GIL mode as this one.

    Args:
        name: A label for the result line.
        source: The example's source.
        tail: Extra statements that print what the example produced.

    Returns:
        str: One result line.
    """
    gil = "0" if not sys._is_gil_enabled() else "1"
    code = "import melder as md\n" + source + tail
    done = subprocess.run([sys.executable, "-X", f"gil={gil}", "-c", code], capture_output=True, text=True,
                          env=dict(os.environ), timeout=120)
    if done.returncode != 0:
        return f"{name}: FAILED rc={done.returncode}: {done.stderr.strip().splitlines()[-1]}"
    return f"{name}: OK {done.stdout.strip()}"


REFUSALS = """
import melder as md

class A:
    pass

class B:
    pass

class Y1:
    pass

class Y2:
    pass

book = md.Spellbook()
a = book.bind(spell=A, existence="unique")
y1 = book.bind(spell=Y1, existence="unique")
root = book.conjure(dynamic=True, name="refusals")
x_index = root.get_spell_by_id(a).spell_index
y_index = root.get_spell_by_id(y1).spell_index
b = root.bind_inactive(spell=B, spell_index=x_index, existence="unique")
y2 = root.bind_inactive(spell=Y2, spell_index=y_index, existence="unique")
for label, kwargs in (("other index", {"spell_id": y2}), ("unknown id", {"spell_id": "no-such-id"}),
                      ("both", {"spell_id": b, "spell": root.get_spell_by_id(a)}), ("neither", {}),
                      ("non-str id", {"spell_id": 7})):
    try:
        root.notch_spell(spell_index=x_index, **kwargs)
        print(label, "-> NOT REFUSED")
    except (ValueError, TypeError) as error:
        print(label, "->", type(error).__name__, str(error).replace(y2, "<id>")[:110])
print("x still selects a:", x_index.selected_spell_id == a, "| y still selects y1:", y_index.selected_spell_id == y1)
print("melds:", type(root.meld(spell_id=a)).__name__, type(root.meld(spell_id=y1)).__name__)
"""


def main() -> None:
    """Print one line per check."""
    print(f"Python {sys.version.split()[0]}, GIL enabled: {sys._is_gil_enabled()}")
    print(run_block("S8 example", block_of(S8), "print(type(service).__name__, service.render())\n"))
    print(run_block("0.2.8249 example", block_of(NOTCH),
                    "print(index.selected_spell_id == v1, type(reports.meld(spell_id=v1)).__name__)\n"))
    gil = "0" if not sys._is_gil_enabled() else "1"
    done = subprocess.run([sys.executable, "-X", f"gil={gil}", "-c", REFUSALS], capture_output=True, text=True,
                          env=dict(os.environ), timeout=120)
    print("refusals:", "OK" if done.returncode == 0 else f"FAILED rc={done.returncode}")
    print((done.stdout + done.stderr).strip())


if __name__ == "__main__":
    main()
