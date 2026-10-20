"""
Run the running release note's two notch examples as written, each in a fresh interpreter, and check every refusal
message the 0.2.8249 section quotes against what the calls raise (TASK-2026-10-16-public_notch_target_for_staged_
versions, after the owner's extension: `add_to_spell_index` / `remove_from_spell_index` take `spell_id=` too).

The examples are taken from release_docs/next_version_release.md itself - the python block of the S8 section and of
the 0.2.8249 section - and run verbatim after `import melder as md`. The quoted messages are taken from the 0.2.8249
section's prose (any double-quoted text starting with a verb name and ": spell_id") and compared, whitespace
collapsed, with the raised message once its spell_id is replaced by '<id>'.

Run from the repository root:  PYTHONPATH=src python -X gil=0 <this file>  (and -X gil=1)
"""
import json
import os
import pathlib
import re
import subprocess
import sys

S8 = "## A version staged before `conjure` melds after a notch"
NOTCH = ("## `notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take a `spell_id`; a notch checks its "
         "target")


def section_of(heading: str) -> str:
    """
    Return a release-note section's text, from below its heading to the next `## ` heading.

    Args:
        heading: The section's heading line.

    Returns:
        str: The section's text.
    """
    note = pathlib.Path("release_docs/next_version_release.md").read_text(encoding="utf-8")
    assert note.count(heading + "\n") == 1, heading
    return note.split(heading + "\n", 1)[1].split("\n## ", 1)[0]


def block_of(heading: str) -> str:
    """
    Return the first python block under a release-note heading.

    Args:
        heading: The section's heading line.

    Returns:
        str: The block's source.
    """
    return re.search(r"```python\n(.*?)```", section_of(heading), re.S).group(1)


def run_code(code: str) -> subprocess.CompletedProcess:
    """
    Run code in a fresh interpreter with this interpreter's GIL mode.

    Args:
        code: The source to run.

    Returns:
        subprocess.CompletedProcess: The finished process.
    """
    gil = "0" if not sys._is_gil_enabled() else "1"
    return subprocess.run([sys.executable, "-X", f"gil={gil}", "-c", code], capture_output=True, text=True,
                          env=dict(os.environ), timeout=120)


def run_block(name: str, source: str, tail: str) -> str:
    """
    Run one example verbatim after `import melder as md`, then `tail`.

    Args:
        name: A label for the result line.
        source: The example's source.
        tail: Statements that print what the example produced.

    Returns:
        str: One result line.
    """
    done = run_code("import melder as md\n" + source + tail)
    if done.returncode != 0:
        return f"{name}: FAILED rc={done.returncode}: {done.stderr.strip().splitlines()[-1]}"
    return f"{name}: OK {done.stdout.strip()}"


REFUSALS = r'''
import json
import melder as md

class A:
    pass

class B:
    pass

class C:
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
out = []

def attempt(label, call, ids):
    try:
        call()
        out.append([label, "NOT REFUSED", ""])
    except (ValueError, TypeError, RuntimeError) as error:
        text = str(error)
        for spell_id in ids:
            text = text.replace(spell_id, "<id>")
        out.append([label, type(error).__name__, text])

attempt("notch other index", lambda: root.notch_spell(spell_index=x_index, spell_id=y2), [y2])
attempt("notch not owned", lambda: root.notch_spell(spell_index=x_index, spell_id="no-such-spell-id"),
        ["no-such-spell-id"])
attempt("notch both", lambda: root.notch_spell(spell_index=x_index, spell_id=b, spell=root.get_spell_by_id(a)), [])
attempt("notch neither", lambda: root.notch_spell(spell_index=x_index), [])
attempt("notch non-str", lambda: root.notch_spell(spell_index=x_index, spell_id=7), [])
attempt("add not owned", lambda: root.add_to_spell_index(spell_id="no-such-spell-id", target_index=y_index),
        ["no-such-spell-id"])
attempt("remove not owned", lambda: root.remove_from_spell_index(spell_id="no-such-spell-id", source_index=x_index),
        ["no-such-spell-id"])
attempt("remove active", lambda: root.remove_from_spell_index(spell_id=a, source_index=x_index), [a])
attempt("add active", lambda: root.add_to_spell_index(spell_id=a, target_index=y_index), [a])
attempt("add both", lambda: root.add_to_spell_index(spell_id=b, spell=root.get_spell_by_id(a), target_index=y_index),
        [])
attempt("remove str spell", lambda: root.remove_from_spell_index(spell=b, source_index=x_index), [b])
intact = (x_index.selected_spell_id == a and x_index.spells_in_index() == {a, b}
          and y_index.selected_spell_id == y1 and y_index.spells_in_index() == {y1, y2})
melds = [type(root.meld(spell_id=a)).__name__, type(root.meld(spell_id=y1)).__name__]
# The moves by spell_id do what the note says: b out to an index of its own, then onto y.
root.remove_from_spell_index(spell_id=b, source_index=x_index)
moved_out = b not in x_index.spells_in_index() and root.get_spell_by_id(a).spell_index is x_index
root.add_to_spell_index(spell_id=b, target_index=y_index)
moved_in = y_index.spells_in_index() == {y1, y2, b}
root.notch_spell(spell_index=y_index, spell_id=b)
promoted = type(root.meld(spell_id=b)).__name__
print(json.dumps({"refusals": out, "intact": intact, "melds": melds, "moved_out": moved_out, "moved_in": moved_in,
                  "promoted": promoted}))
'''


def quoted_messages(section: str) -> list:
    """
    Return the refusal messages the section quotes for the three verbs, whitespace collapsed.

    Args:
        section: The 0.2.8249 section's text.

    Returns:
        list: The quoted messages.
    """
    flat = " ".join(section.split())
    return re.findall(r'"((?:notch_spell|add_to_spell_index|remove_from_spell_index): spell_id [^"]*)"', flat)


def main() -> None:
    """Print one line per check."""
    print(f"Python {sys.version.split()[0]}, GIL enabled: {sys._is_gil_enabled()}")
    print(run_block("S8 example", block_of(S8), "print(type(service).__name__, service.render())\n"))
    print(run_block("0.2.8249 example", block_of(NOTCH),
                    "print(index.selected_spell_id == v1, sorted(index.spells_in_index()) == sorted({v1, v2}), "
                    "type(reports.meld(spell_id=v1)).__name__)\n"))
    done = run_code(REFUSALS)
    if done.returncode != 0:
        print("refusals: FAILED", done.returncode, (done.stdout + done.stderr).strip()[-400:])
        return
    result = json.loads(done.stdout.strip().splitlines()[-1])
    raised = {text for _label, _type, text in result["refusals"]}
    for label, kind, text in result["refusals"]:
        print(f"refusal {label}: {kind}: {text[:100]}")
    quoted = quoted_messages(section_of(NOTCH))
    for message in quoted:
        print("quoted message", "MATCHES" if message in raised else "DOES NOT MATCH", "-", message[:70])
    print("quoted messages found:", len(quoted))
    print("indexes intact after the refusals:", result["intact"], "| melds:", result["melds"])
    print("moves by spell_id: out", result["moved_out"], "| in", result["moved_in"], "| notch and meld ->",
          result["promoted"])


if __name__ == "__main__":
    main()
