"""
Probe (read-only on src/): what `Conduit.notch_spell` does today with each way a caller can name, or misname, the
version to activate. Cases:

- C1 the public trap: `find_spell_by_id(<parked id>)` returns the index's LIVE spell, so a notch to it is a silent no-op.
- C2 the private path the S8 tests use (`Spellbook._get_owned_spell`): the notch works.
- C3 a version parked in ANOTHER index of the same Book, passed with this index.
- C4 the ACTIVE version of another index, passed with this index.
- C5 a version parked in ANOTHER Book.

Run from the repository root with src on the path:
    PYTHONPATH=src python -X gil=0 <this file>   (and -X gil=1)
"""
import sys
import traceback

import melder as md


def make(name: str) -> type:
    """Return a fresh class whose `who()` answers its own name."""
    return type(name, (), {"who": lambda self, _n=name: _n})


def state(book, root, index, label: str) -> str:
    """One line on an index: its selected id, the Book's active map entry for it, and its members."""
    active = book._spells.get(index)
    return (
        f"{label}: selected={index.selected_spell_id[:8]} active_map={active.spell_id[:8] if active else None} "
        f"members={sorted(m[:8] for m in index.spells_in_index())}"
    )


def meld_who(root, spell_id: str) -> str:
    """Meld a version by id and answer its `who()`, or the error raised."""
    try:
        return root.meld(spell_id=spell_id).who()
    except Exception as error:
        return f"{type(error).__name__}: {str(error)[:90]}"


def stage(tag: str):
    """A conjured Book with index X (x1 active, x2 parked) and index Y (y1 active, y2 parked), staged after conjure."""
    book = md.Spellbook()
    x1 = book.bind(spell=make(f"{tag}X1"), existence="unique", binding_name=f"{tag}x1")
    y1 = book.bind(spell=make(f"{tag}Y1"), existence="unique", binding_name=f"{tag}y1")
    root = book.conjure(name=f"{tag}_root")
    ix = book.find_spell_by_id(x1).spell_index
    iy = book.find_spell_by_id(y1).spell_index
    x2 = root.bind_inactive(spell=make(f"{tag}X2"), spell_index=ix, existence="unique", binding_name=f"{tag}x2")
    y2 = root.bind_inactive(spell=make(f"{tag}Y2"), spell_index=iy, existence="unique", binding_name=f"{tag}y2")
    return book, root, ix, iy, x1, x2, y1, y2


def c1_public_trap() -> str:
    book, root, ix, iy, x1, x2, y1, y2 = stage("c1")
    found = book.find_spell_by_id(x2)
    result = root.notch_spell(spell_index=ix, spell=found)
    return (
        f"C1 find_spell_by_id(x2) is x1's Spell: {found.spell_id == x1}; notch returned "
        f"{result.spell_id[:8]}; {state(book, root, ix, 'X')}; meld(x2) -> {meld_who(root, x2)}"
    )


def c2_private_path() -> str:
    book, root, ix, iy, x1, x2, y1, y2 = stage("c2")
    root.notch_spell(spell_index=ix, spell=book._get_owned_spell(x2))
    after = meld_who(root, x2)
    root.notch_spell(spell_index=ix, spell=book._get_owned_spell(x1))
    back = meld_who(root, x1)
    return f"C2 private: meld(x2) after notch -> {after}; after notch back meld(x1) -> {back}"


def c3_parked_of_other_index() -> str:
    book, root, ix, iy, x1, x2, y1, y2 = stage("c3")
    try:
        root.notch_spell(spell_index=ix, spell=book._get_owned_spell(y2))
        outcome = "returned"
    except Exception as error:
        outcome = f"{type(error).__name__}: {str(error)[:80]}"
    return (
        f"C3 notch X to Y's parked y2: {outcome}; {state(book, root, ix, 'X')}; {state(book, root, iy, 'Y')}; "
        f"y2.spell_index is Y: {book._get_owned_spell(y2).spell_index is iy}; meld(x1) -> {meld_who(root, x1)}; "
        f"meld(y1) -> {meld_who(root, y1)}; meld(y2) -> {meld_who(root, y2)}"
    )


def c4_active_of_other_index() -> str:
    book, root, ix, iy, x1, x2, y1, y2 = stage("c4")
    try:
        root.notch_spell(spell_index=ix, spell=book._get_owned_spell(y1))
        outcome = "returned"
    except Exception as error:
        outcome = f"{type(error).__name__}: {str(error)[:80]}"
    line = f"C4 notch X to Y's active y1: {outcome}; {state(book, root, ix, 'X')}; meld(x1) -> {meld_who(root, x1)}"
    try:
        root.notch_spell(spell_index=ix, spell=book._get_owned_spell(x1))
        line += f"; renotch X to x1 -> meld(x1) {meld_who(root, x1)}"
    except Exception as error:
        line += f"; renotch X to x1 raised {type(error).__name__}: {str(error)[:60]}"
    return line


def c5_parked_of_other_book() -> str:
    book, root, ix, iy, x1, x2, y1, y2 = stage("c5a")
    other, other_root, ox, oy, ox1, ox2, oy1, oy2 = stage("c5b")
    try:
        root.notch_spell(spell_index=ix, spell=other._get_owned_spell(ox2))
        outcome = "returned"
    except Exception as error:
        outcome = f"{type(error).__name__}: {str(error)[:80]}"
    return f"C5 notch X to another Book's parked version: {outcome}; {state(book, root, ix, 'X')}; meld(x1) -> {meld_who(root, x1)}"


def main() -> None:
    """Settle the frame dynamic, run each case, print one line each."""
    print(f"python {sys.version.split()[0]}, gil enabled: {sys._is_gil_enabled()}, melder {md.__version__}")
    md.Spellbook().conjure(dynamic=True, name="settle")
    failed = False
    for case in (c1_public_trap, c2_private_path, c3_parked_of_other_index, c4_active_of_other_index,
                 c5_parked_of_other_book):
        try:
            print(case())
        except Exception:
            failed = True
            print(f"{case.__name__}: RAISED")
            traceback.print_exc()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
