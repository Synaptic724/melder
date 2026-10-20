"""
Content Preservation Gate for the running release note (find_spell_by_spell_id_2026_10_17).

melder_1 (synaptic_python_developer), 2026-10-17. Usage: python gate_release_note_fix1.py <repo_root>

Multiset of non-blank, whitespace-normalised lines: baseline (docs_baselines/next_version_release.md.before,
byte-identical to the note when this pass began) -> the note now. Every baseline line must still be present, or sit
on a line one of docs_release_note_fix1.py's anchors touches. Prints every unaccounted line; exit 1 if any.
"""
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import docs_release_note_fix1 as fix1

BASE = pathlib.Path(__file__).resolve().parent.parent / "docs_baselines"


def norm_lines(text: str) -> list:
    """Return the note's non-blank lines with every whitespace run collapsed to one space."""
    return [re.sub(r"\s+", " ", ln) for ln in text.split("\n") if ln.strip()]


def main() -> None:
    """Compare the baseline multiset with the note now and report every unaccounted line."""
    root = pathlib.Path(sys.argv[1]).resolve()
    before = (BASE / "next_version_release.md.before").read_text(encoding="utf-8")
    now = (root / fix1.DOC).read_text(encoding="utf-8")
    mb = collections.Counter(norm_lines(before))
    allowed = collections.Counter()
    for old, _new in fix1.EDITS:
        # The whole lines an anchor touches: an anchor may start or end inside a line.
        pos = before.index(old)
        start = before.rfind("\n", 0, pos) + 1
        end = before.find("\n", pos + len(old) - 1)
        allowed.update(norm_lines(before[start:end if end != -1 else len(before)]))
    mn = collections.Counter(norm_lines(now))
    gone = mb - mn
    bad = list((gone - allowed).elements())
    print(f"edit step: {sum(gone.values())} lines removed or rewritten, unaccounted {len(bad)}")
    print(f"lines added: {sum((mn - mb).values())}")
    for s in bad:
        print("UNACCOUNTED:", s[:160])
    print("GATE:", "PASS" if not bad else "FAIL")
    raise SystemExit(0 if not bad else 1)


if __name__ == "__main__":
    main()
