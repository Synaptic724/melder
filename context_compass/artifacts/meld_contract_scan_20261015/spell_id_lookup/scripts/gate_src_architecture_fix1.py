"""
Content Preservation Gate for src_architecture (find_spell_by_spell_id_2026_10_17).

Usage: python gate_src_architecture_fix1.py <repo_root>

Multiset of non-blank, whitespace-normalised lines: baseline (docs_baselines/src_architecture.md.before, taken
before the first transform) -> after the citation remap (docs_baselines/src_architecture.md.remapped) -> the
document now. Every baseline line must still be present, or be accounted for: a remapped citation line (the same
line with only its digits changed), or an old text of docs_src_architecture_fix1.py's anchors (including the
eleven code-map entries' end_line, loc, verified_at and note lines). Prints every unaccounted line; exit 1 if any.
"""
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import docs_src_architecture_fix1 as fix1

BASE = pathlib.Path(__file__).resolve().parent.parent / "docs_baselines"


def norm_lines(text: str) -> list:
    return [re.sub(r"\s+", " ", ln) for ln in text.split("\n") if ln.strip()]


def multiset(text: str) -> collections.Counter:
    return collections.Counter(norm_lines(text))


def main() -> None:
    root = pathlib.Path(sys.argv[1]).resolve()
    before = (BASE / "src_architecture.md.before").read_text(encoding="utf-8")
    remapped = (BASE / "src_architecture.md.remapped").read_text(encoding="utf-8")
    now = (root / fix1.DOC).read_text(encoding="utf-8")
    stored = {}
    for line in (BASE / "src_architecture.md.before.multiset").read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^\s*(\d+) (.*)$", line)
        if m:
            stored[m.group(2)] = int(m.group(1))
    mb = multiset(before)
    print("stored baseline multiset agrees with the .before copy:", stored == dict(mb))
    # Step 1: before -> remapped may only change digits.
    mr = multiset(remapped)
    gone1 = mb - mr
    new1 = mr - mb
    digits = lambda s: re.sub(r"\d+", "#", s)
    new_shapes = collections.Counter(digits(s) for s in new1.elements())
    bad1 = []
    for s in gone1.elements():
        k = digits(s)
        if new_shapes[k] > 0:
            new_shapes[k] -= 1
        else:
            bad1.append(s)
    print(f"remap step: {sum(gone1.values())} lines changed, unaccounted {len(bad1)}")
    # Step 2: remapped -> now may remove only anchor old texts.
    allowed = collections.Counter()
    edits = [fix1.BOUNDARY_SENTENCE, fix1.BOUNDARY_BULLET, fix1.INVARIANT, fix1.FAILURES, fix1.HANDOFF] + fix1.SMALL
    for old, _new in edits:
        allowed.update(norm_lines(old))
    for rel, (old_note, _new_note) in fix1.CODE_MAP.items():
        start, end = fix1.entry_span(remapped, rel)
        entry_lines = remapped[start:end].split("\n")
        allowed.update(norm_lines("\n".join(entry_lines[2:5])))
        allowed.update(norm_lines(old_note))
    mn = multiset(now)
    gone2 = mr - mn
    bad2 = list((gone2 - allowed).elements())
    print(f"edit step: {sum(gone2.values())} lines removed or rewritten, unaccounted {len(bad2)}")
    for s in bad1 + bad2:
        print("UNACCOUNTED:", s[:160])
    total = len(bad1) + len(bad2)
    print("GATE:", "PASS" if total == 0 else "FAIL")
    raise SystemExit(0 if total == 0 else 1)


if __name__ == "__main__":
    main()
