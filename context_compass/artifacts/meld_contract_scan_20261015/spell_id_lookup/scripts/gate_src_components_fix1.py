"""
Content Preservation Gate for src_components (find_spell_by_spell_id_2026_10_17).

Usage: python gate_src_components_fix1.py <repo_root>

Multiset of non-blank, whitespace-normalised lines: baseline (docs_baselines/src_components.md.before, taken before
the first transform) -> after the citation remap (docs_baselines/src_components.md.remapped) -> the document now.
Every baseline line must still be present, or be accounted for: a remapped citation line (the same line with only
its digits changed), or an old text of docs_src_components_fix1.py's anchors (including the ten code-map entries'
end_line, loc and verified_at lines). Prints every unaccounted line; exit 1 if any.
"""
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import docs_src_components_fix1 as fix1

BASE = pathlib.Path(__file__).resolve().parent.parent / "docs_baselines"


def norm_lines(text: str) -> list:
    return [re.sub(r"\s+", " ", ln) for ln in text.split("\n") if ln.strip()]


def main() -> None:
    root = pathlib.Path(sys.argv[1]).resolve()
    before = (BASE / "src_components.md.before").read_text(encoding="utf-8")
    remapped = (BASE / "src_components.md.remapped").read_text(encoding="utf-8")
    now = (root / fix1.DOC).read_text(encoding="utf-8")
    stored = {}
    for line in (BASE / "src_components.md.before.multiset").read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^\s*(\d+) (.*)$", line)
        if m:
            stored[m.group(2)] = int(m.group(1))
    mb = collections.Counter(norm_lines(before))
    print("stored baseline multiset agrees with the .before copy:", stored == dict(mb))
    mr = collections.Counter(norm_lines(remapped))
    gone1, new1 = mb - mr, mr - mb
    digits = lambda s: re.sub(r"\d+", "#", s)
    shapes = collections.Counter(digits(s) for s in new1.elements())
    bad1 = []
    for s in gone1.elements():
        k = digits(s)
        if shapes[k] > 0:
            shapes[k] -= 1
        else:
            bad1.append(s)
    print(f"remap step: {sum(gone1.values())} lines changed, unaccounted {len(bad1)}")
    allowed = collections.Counter()
    for old, _new in fix1.EDITS:
        allowed.update(norm_lines(old))
    for rel in fix1.CODE_MAP:
        start, end = fix1.entry_span(remapped, rel)
        allowed.update(norm_lines("\n".join(remapped[start:end].split("\n")[2:5])))
    mn = collections.Counter(norm_lines(now))
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
