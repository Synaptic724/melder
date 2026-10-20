"""S7 D5: give the four managed-spell root exports (0.2.8244) their place in the docs site's API selection.

The docs build reads `__all__` from `src/melder/__init__.py` and refuses a selection in `docs/api.toml` that misses
an export ("Public API selection drift"); S4 added ManagedSpellMode, ReleaseManagedSpell, ManagedSpellLease and
ManagedSpellExhaustedError to the root without adding them here. The three managed surfaces join the "resolution"
group, whose guide is the README lifetimes chapter that now teaches them; the error joins "errors" beside
UnresolvedInputError. One exact line per group is replaced; the file's CRLF endings are kept.
Run from the repository root: python <this file> [--apply]
"""
import pathlib
import sys

PATH = "docs/api.toml"
EDITS = (
    ('exports = ["Conduit", "SpellSpace", "SpellMap", "SpellContract", "Existence"]',
     'exports = ["Conduit", "SpellSpace", "SpellMap", "SpellContract", "Existence", "ManagedSpellMode", '
     '"ReleaseManagedSpell", "ManagedSpellLease"]'),
    ('"UnresolvedInputError", "SpellSpaceScopeError",',
     '"UnresolvedInputError", "ManagedSpellExhaustedError", "SpellSpaceScopeError",'),
)


def main() -> None:
    """Replace each line once, or write nothing."""
    text = pathlib.Path(PATH).read_bytes().decode("utf-8")
    for old, new in EDITS:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{PATH}: {old!r} occurs {count} times (expected 1); nothing written")
        text = text.replace(old, new)
        print("matched:", old[:60])
    if "--apply" in sys.argv[1:]:
        pathlib.Path(PATH).write_bytes(text.encode("utf-8"))
        print("wrote", PATH)
    else:
        print("dry run: nothing written (pass --apply)")


main()
