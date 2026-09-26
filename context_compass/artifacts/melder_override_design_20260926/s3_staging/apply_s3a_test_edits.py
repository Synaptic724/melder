"""Move the two eager-construction characterization tests to design v2 B1.

Usage: python apply_s3a_test_edits.py <tree_root> [--check]

Supplied branches are no longer constructed (B1), so a supplied child's own
missing input is never needed. Each block must match exactly once, in the
file's own line endings, or nothing is written.
"""

import pathlib
import sys

TARGET = "tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py"

EDITS = [
    (
        '''def test_whole_branch_override_preserves_existing_eager_construction(
    runtime_book: Spellbook, family: str, cached: bool,
) -> None:
    """Existing eager child construction still requires its input before the parent replaces it."""
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    child = SuppliedConsumer(ExternalValue())
    with pytest.raises((TypeError, MeldExecutionError), match="external"):
        conduit.meld(spell_id=root_id, override={"child": child})
    result = conduit.meld(
        spell_id=root_id, override={"child": child, "child>external": child.external},
    )
    assert result.child is child
''',
        '''def test_whole_branch_override_skips_the_supplied_branch(
    runtime_book: Spellbook, family: str, cached: bool,
) -> None:
    """A supplied branch is used as given: its own input is never needed (design v2 B1).

    Before the key-set plans the child was built first and failed on its missing
    input; now it is not built, and a rule below it is validated but inactive.
    """
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    child = SuppliedConsumer(ExternalValue())
    assert conduit.meld(spell_id=root_id, override={"child": child}).child is child
    result = conduit.meld(
        spell_id=root_id, override={"child": child, "child>external": ExternalValue()},
    )
    assert result.child is child
    assert result.child.external is child.external
''',
    ),
    (
        '''def test_ordinary_branch_override_also_constructs_its_registered_child(runtime_book: Spellbook) -> None:
    """Characterize eager construction independently of the new registration capability."""
    runtime_book.bind(spell=OrdinaryRequiredConsumer, existence="many")
    root_id = runtime_book.bind(spell=OrdinaryOuter, existence="many")
    conduit = runtime_book.conjure()
    child = OrdinaryRequiredConsumer(3)
    with pytest.raises((TypeError, MeldExecutionError), match="count"):
        conduit.meld(spell_id=root_id, override={"child": child})
''',
        '''def test_ordinary_branch_override_skips_its_registered_child(runtime_book: Spellbook) -> None:
    """A supplied child is not built, so its unsatisfiable plain input is never needed (design v2 B1)."""
    runtime_book.bind(spell=OrdinaryRequiredConsumer, existence="many")
    root_id = runtime_book.bind(spell=OrdinaryOuter, existence="many")
    conduit = runtime_book.conjure()
    child = OrdinaryRequiredConsumer(3)
    assert conduit.meld(spell_id=root_id, override={"child": child}).child is child
    with pytest.raises((TypeError, MeldExecutionError), match="count"):
        conduit.meld(spell_id=root_id)
''',
    ),
]


def main() -> None:
    """Apply (or check) every edit against the tree given on the command line."""
    path = pathlib.Path(sys.argv[1]) / TARGET
    check = "--check" in sys.argv[2:]
    data = path.read_bytes().decode("utf-8")
    for old, new in EDITS:
        for nl in ("\r\n", "\n"):
            old_nl = old.replace("\n", nl)
            count = data.count(old_nl)
            if count > 1:
                raise SystemExit(f"anchor matched {count} times: {old[:70]!r}")
            if count == 1:
                data = data.replace(old_nl, new.replace("\n", nl))
                break
        else:
            raise SystemExit(f"anchor not found: {old[:70]!r}")
    if not check:
        path.write_bytes(data.encode("utf-8"))
    print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
