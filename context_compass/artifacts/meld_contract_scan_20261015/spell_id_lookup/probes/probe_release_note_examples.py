"""
Run the release note's examples that fix #1 adds or renames, each in a fresh interpreter, as a user would.

melder_1 (synaptic_python_developer), 2026-10-17. Usage: python probe_release_note_examples.py <note.md> <src_dir>

Each example is a ```python block of the note, picked by a marker line it must contain; the 0.2.8251 block continues
the 0.2.8250 contract block, so the two run together. A run prepends `import melder as md` and `from typing import
Protocol`, puts <src_dir> first on sys.path and must exit 0. Prints one PASS/FAIL line per example.
"""
import os
import pathlib
import re
import subprocess
import sys

PICKS = [
    ("spell_id lookup (0.2.8253)", ["get_spell_by_index_id(index.id)"]),
    ("staged before conjure (0.2.8248)", ["book.find_spell_by_spell_id(v1).spell_index"]),
    ("notch by spell_id (0.2.8249)", ["reports.remove_from_spell_index(spell_id=v2, source_index=index)"]),
    ("contract recheck + unlink (0.2.8250-0.2.8251)", ["lender_book = md.Spellbook()",
                                                        "Continuing the first example above"]),
    ("annotation dependents (0.2.8250)", ["clock_index = reports.get_spell_by_spell_id(utc)"]),
]


def main() -> None:
    """Pick the blocks, run each in a subprocess with the given src on the path, report and exit non-zero on a FAIL."""
    note, src = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).resolve()
    blocks = re.findall(r"```python\n(.*?)```", note.read_text(encoding="utf-8"), re.S)
    failed = 0
    for name, markers in PICKS:
        parts = []
        for marker in markers:
            found = [b for b in blocks if marker in b]
            if len(found) != 1:
                raise SystemExit(f"{name}: marker {marker!r} matched {len(found)} blocks")
            parts.append(found[0])
        code = "import melder as md\nfrom typing import Protocol\n\n" + "\n".join(parts)
        env = dict(os.environ, PYTHONPATH=str(src))
        run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=120)
        ok = run.returncode == 0
        failed += not ok
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            print(run.stderr[-1500:])
    print("examples failed:", failed)
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
