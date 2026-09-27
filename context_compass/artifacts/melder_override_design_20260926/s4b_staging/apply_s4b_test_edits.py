"""S4b tests: the solo lane decides unresolved inputs before calling - anchored edits.

Usage: python apply_s4b_test_edits.py <tree_root> [--check]

test_conduit_component_unresolved_inputs.py: every family raises with no TypeError cause; a solo root whose input is
missing is never called, and its keyword and positional supply still reach the constructor. Each anchor must match
exactly once or nothing is written. Engine: ../s3_staging/apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

COMPONENT = "tests/component/melder/aether/conduit/test_conduit_component_unresolved_inputs.py"

CAUSE_OLD = """    # Plans decide it before calling (B6, 2026-09-26); the solo lane still converts the TypeError.
    if family == "solo":
        assert isinstance(error.__cause__, TypeError)
    else:
        assert error.__cause__ is None
"""
CAUSE_NEW = """    # Every family decides it before calling (B6, 2026-09-26), so no TypeError precedes it.
    assert error.__cause__ is None
"""

CLASS_ANCHOR = '''class Outer:
    """Build Needy as a dependency."""
'''
CLASS_NEW = '''class CountedTask:
    """A solo root with an unresolved input that counts its constructor calls."""

    count = 0

    def __init__(self, work: Package) -> None:
        """Count one call and keep the supplied value."""
        CountedTask.count += 1
        self.work = work


''' + CLASS_ANCHOR

TAIL_ANCHOR = """    assert conduit.meld(spell_id=root_id, override={"needy>work": value}).needy.work is value
    assert Counted.count == 1
"""
TAIL_NEW = TAIL_ANCHOR + '''

def test_solo_root_is_not_called_without_its_unresolved_input(runtime_book: Spellbook) -> None:
    """B6 for the solo lane: a missing input fails before the constructor runs; a keyword or positional value calls it."""
    root_id = runtime_book.bind(spell=CountedTask, existence="many")
    conduit = runtime_book.conjure()
    CountedTask.count = 0
    for override in (None, {}, ()):
        with pytest.raises(UnresolvedInputError) as caught:
            conduit.meld(spell_id=root_id, override=override)
        assert caught.value.spell_name == "CountedTask" and caught.value.__cause__ is None
    assert CountedTask.count == 0
    value = Package()
    assert conduit.meld(spell_id=root_id, override={"work": value}).work is value
    assert conduit.meld(spell_id=root_id, override=[value]).work is value
    assert CountedTask.count == 2
'''

EDITS = {
    COMPONENT: [
        ("replace", CAUSE_OLD, CAUSE_NEW),
        ("replace", CLASS_ANCHOR, CLASS_NEW),
        ("replace", TAIL_ANCHOR, TAIL_NEW),
    ],
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
