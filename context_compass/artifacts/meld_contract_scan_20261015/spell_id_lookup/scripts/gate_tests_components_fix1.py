"""
Content Preservation Gate for tests_components (find_spell_by_spell_id_2026_10_17).

Usage: python gate_tests_components_fix1.py <repo_root>

Multiset of non-blank, whitespace-normalised lines: baseline (docs_baselines/tests_components.md.before, taken before
the first transform and byte-identical to the document when this pass began) -> the document now. Every baseline line
must still be present, or sit on a line one of docs_tests_components_fix1.py's anchors touches (including the
end_line, loc and verified_at lines of the two remeasured records). No citation remap was needed in this
document. Prints every unaccounted line; exit 1 if any.
"""
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import docs_tests_components_fix1 as fix1

BASE = pathlib.Path(__file__).resolve().parent.parent / "docs_baselines"


def norm_lines(text: str) -> list:
    """Return the document's non-blank lines with every whitespace run collapsed to one space."""
    return [re.sub(r"\s+", " ", ln) for ln in text.split("\n") if ln.strip()]


def main() -> None:
    """Compare the baseline multiset with the document now and report every unaccounted line."""
    root = pathlib.Path(sys.argv[1]).resolve()
    before = (BASE / "tests_components.md.before").read_text(encoding="utf-8")
    now = (root / fix1.DOC).read_text(encoding="utf-8")
    stored = {}
    for line in (BASE / "tests_components.md.before.multiset").read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^\s*(\d+) (.*)$", line)
        if m:
            stored[m.group(2)] = int(m.group(1))
    mb = collections.Counter(norm_lines(before))
    print("stored baseline multiset agrees with the .before copy:", stored == dict(mb))
    allowed = collections.Counter()
    for old, _new in fix1.EDITS:
        # The whole lines an anchor touches: an anchor may start or end inside a line.
        pos = before.index(old)
        start = before.rfind("\n", 0, pos) + 1
        end = before.find("\n", pos + len(old) - 1)
        allowed.update(norm_lines(before[start:end if end != -1 else len(before)]))
    allowed.update(norm_lines(fix1.LAST_RECORD_END))
    for rel in fix1.REMEASURE:
        start, end = fix1.entry_span(before, rel)
        allowed.update(norm_lines("\n".join(before[start:end].split("\n")[2:5])))
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
