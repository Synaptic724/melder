"""Tests for the contracted-copy removal fix (contracted_copy_removal_by_version_2026_10_16).

melder_1 (synaptic_python_developer), 2026-10-16. Edits three test files under TREE: three unit tests (one
parametrized) in test_spellbook.py, two integration tests (one parametrized) in
test_spell_index_meld_and_contract_lifecycle.py, and the one component test that asserted the old member-set match.
usage: python apply_removal_tests_2026_10_16.py <tree root> --check | --apply. Anchors must match exactly once.
"""
import pathlib
import sys

UNIT = "tests/unit/melder/spellbook/test_spellbook.py"
INTEG = "tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py"
COMP = "tests/component/melder/spellbook/test_spellbook_component_contracts.py"

UNIT_ANCHOR = "\n\nclass _RecordingContractRegistry:\n"
UNIT_TESTS = '''

def _two_versions_of_one_index() -> tuple[DummySpellIndex, DummySpell, DummySpell]:
    """
    Purpose:
        Build the two borrowed copies a borrower holds after its lender notched one index from "sid-1" to "sid-2":
        the "sid-1" copy (to be parked) and the "sid-2" copy (active), of one index and under the key
        ("frame", "binding").
    Returns:
        tuple[DummySpellIndex, DummySpell, DummySpell]: The shared index, the sid-1 copy and the sid-2 copy.
    """
    index = DummySpellIndex(versions={"sid-1", "sid-2"}, sid="lineage", current="sid-2")
    copies: list[DummySpell] = []
    for spell_id in ("sid-1", "sid-2"):
        spell = DummySpell(
            spell_id=spell_id,
            versions={"sid-1", "sid-2"},
            spell_name="SpellName",
            binding_name="binding",
            spellframe="Frame",
        )
        spell.spell_index = index
        spell.key = _COPY_KEY
        spell._key = _COPY_KEY
        copies.append(spell)
    return index, copies[0], copies[1]


def test_removing_a_parked_version_keeps_the_active_copy_of_its_index() -> None:
    """
    Purpose:
        Regression for the unlink after a notch (contracted_copy_removal_by_version_2026_10_16): removing a parked
        version removes that version's parked copy, leaves the active copy of the same index - another version - in
        place and marks nothing; removing the active version then removes its copy and marks the consumers.
    Contract:
        - A removal takes the copy of exactly the version it names: the active copy only when it is that version.
    """
    sb = _contracted_book()
    state = _consumer_of_copy_key(sb)
    index, parked, active = _two_versions_of_one_index()
    sb._add_contracted_spell(active, "peer")
    sb._add_inactive_contracted_spell(parked, "peer")
    _assert_marked_then_reset(state)

    sb._remove_contracted_spell("sid-1", "peer")

    assert sb._contracted_spells["peer"] == {index: active}
    assert sb._contracted_spells_by_id["peer"] == {"sid-2": active}
    assert sb._inactive_contracted_spells["peer"] == {}
    assert state.validity is SpellValidity.valid
    assert not state.has_flag(SpellState.contract_unvalidated)

    sb._remove_contracted_spell("sid-2", "peer")

    assert sb._contracted_spells["peer"] == {}
    _assert_marked_then_reset(state)


def test_removing_a_version_the_book_holds_no_copy_of_raises_and_keeps_the_active_copy() -> None:
    """
    Purpose:
        A member id of a borrowed index that the Book holds no copy of is refused with the not-found RuntimeError,
        and the index's active copy - another version - stays (before 0.2.8251 it was removed under that id).
    """
    sb = _contracted_book()
    index, _, active = _two_versions_of_one_index()
    sb._add_contracted_spell(active, "peer")

    with pytest.raises(RuntimeError, match="Spell version sid-1 not found for conduit ID peer."):
        sb._remove_contracted_spell("sid-1", "peer")

    assert sb._contracted_spells["peer"] == {index: active}
    assert sb._contracted_spells_by_id["peer"] == {"sid-2": active}


@pytest.mark.parametrize("order", [("sid-1", "sid-2"), ("sid-2", "sid-1")], ids=["parked_first", "active_first"])
def test_removing_both_versions_of_an_index_in_either_order_leaves_no_copy(order: tuple[str, str]) -> None:
    """
    Purpose:
        An index unlink removes each member's copy in its member set's order, which follows the hash seed: either
        order leaves no copy, active or parked, and an empty set of borrowed version ids.
    """
    sb = _contracted_book()
    _, parked, active = _two_versions_of_one_index()
    sb._add_contracted_spell(active, "peer")
    sb._add_inactive_contracted_spell(parked, "peer")

    for spell_id in order:
        sb._remove_contracted_spell(spell_id, "peer")

    assert sb._contracted_spells["peer"] == {}
    assert sb._contracted_spells_by_id["peer"] == {}
    assert sb._inactive_contracted_spells["peer"] == {}
    assert sb._contracted_spell_ids["peer"] == set()
'''

INTEG_IMPORTS = [
    ("from typing import Iterator\n", "from typing import Callable, Iterator\n"),
    (
        "from melder.aether.spellbook.existence.existence import Existence\n",
        "from melder.aether.spellbook.bind.spell_index import SpellIndex\n"
        "from melder.aether.spellbook.existence.existence import Existence\n",
    ),
    (
        "from tests.mocks.spellbook.contract_classes import ContractServicePrimary\n",
        "from tests.mocks.spellbook.contract_classes import ContractServicePrimary\n"
        "from tests.mocks.spellbook.contract_classes import ContractServiceSecondary\n",
    ),
]
INTEG_TAIL_ANCHOR = "        assert service_id not in active_by_id\n"
INTEG_TESTS = '''

# --- one version, one copy (contracted_copy_removal_by_version_2026_10_16) -------------------------------------

def _stage_secondary(owner: Conduit, index: SpellIndex) -> str:
    """
    Purpose:
        Stage ContractServiceSecondary as a parked version of the service index, under the same frame and binding
        name, and return its spell_id.
    """
    return owner.bind_inactive(
        spell=ContractServiceSecondary,
        spell_index=index,
        spellframe=IService,
        binding_name="primary",
        existence=Existence.unique,
        permissions="create",
    )


def _members_in_order(order: list[str]) -> Callable[[SpellIndex], list[str]]:
    """
    Purpose:
        Build a stand-in for `SpellIndex.spells_in_index` that returns the members in `order` (members not named
        come last), so a test fixes the order an index unlink visits them in. The real method runs first, so a
        cleaned index raises as it does.
    """
    real = SpellIndex.spells_in_index

    def ordered(index: SpellIndex) -> list[str]:
        members = real(index)
        return sorted(members, key=lambda member_id: order.index(member_id) if member_id in order else len(order))

    return ordered


@pytest.mark.parametrize("first", ["parked", "active"])
def test_remove_index_contract_after_a_notch_removes_each_members_copy_in_either_order(
        monkeypatch: pytest.MonkeyPatch, first: str,
) -> None:
    """
    Purpose:
        After the owner notches a linked index to a version staged on it, unlinking the index removes every member's
        own copy - the old version's parked copy and the new version's active one - whichever member the unlink
        visits first. The member set's order follows the hash seed, so the test fixes each order. Until 0.2.8251
        the parked-first order removed the active copy under the parked member's id, then raised RuntimeError
        "Spell version <id> not found for conduit ID <owner>." and left the parked copy behind.
    """
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        staged_id = _stage_secondary(owner, index)
        owner.notch_spell(spell_index=index, spell_id=staged_id)
        assert set(borrower_book._contracted_spells_by_id.get(owner._id, {})) == {staged_id}
        assert set(borrower_book._inactive_contracted_spells.get(owner._id, {})) == {service_id}

        order = [service_id, staged_id] if first == "parked" else [staged_id, service_id]
        with monkeypatch.context() as patch:
            patch.setattr(SpellIndex, "spells_in_index", _members_in_order(order), raising=True)
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.remove_index_from_contract(index_id=index.id, conduit=owner)

        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is False
        assert contract._check_if_exists(owner._conduit_ward, service_id) is False
        assert contract._check_if_exists(owner._conduit_ward, staged_id) is False
        assert index.id not in borrower_book._contracted_indexes
        assert borrower_book._contracted_spells_by_id.get(owner._id, {}) == {}
        assert borrower_book._inactive_contracted_spells.get(owner._id, {}) == {}


def test_removing_a_parked_version_grant_keeps_the_active_versions_copy() -> None:
    """
    Purpose:
        A borrower granted a version that its owner then notched away from, and granted the new version too, removes
        only the old version's parked copy when that grant goes, and still melds the new version. Until 0.2.8251 the
        removal took the new version's active copy instead and left the old one parked.
    """
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        primary_spell = owner.get_spell_by_id(service_id)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
        staged_id = _stage_secondary(owner, index)
        owner.notch_spell(spell_index=index, spell_id=staged_id)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=staged_id, conduit=owner, permissions="create")
        assert set(borrower_book._contracted_spells_by_id.get(owner._id, {})) == {staged_id}
        assert set(borrower_book._inactive_contracted_spells.get(owner._id, {})) == {service_id}

        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_spell_from_contract(spell=primary_spell, conduit=owner)

        assert set(borrower_book._contracted_spells_by_id.get(owner._id, {})) == {staged_id}
        assert service_id not in borrower_book._inactive_contracted_spells.get(owner._id, {})
        assert borrower.validate_contracts_and_define()
        assert isinstance(borrower.meld(spell_id=staged_id), ContractServiceSecondary)
'''

COMP_EDITS = [
    (
        "    Purpose:\n"
        "        Validate removing a contracted index member clears every tracked member id.\n"
        "    Contract:\n"
        "        - The contracted copy is the ACTIVE member, so the by-id registration key\n"
        "          (selected_spell_id at add time) and the copy's own spell_id agree.\n"
        "        - _remove_contracted_spell drops the index subscription and every member\n"
        "          id tracked for the peer conduit.\n",
        "    Purpose:\n"
        "        Validate removing the active contracted copy of a live index clears every\n"
        "        tracked member id of that index.\n"
        "    Contract:\n"
        "        - The contracted copy is the ACTIVE member, so the by-id registration key\n"
        "          (selected_spell_id at add time) and the copy's own spell_id agree.\n"
        "        - _remove_contracted_spell is asked for that copy's own version id: a removal\n"
        "          takes exactly the copy of the version it names (0.2.8251; before, a member id\n"
        "          with no copy took the index's active copy). It drops the index subscription\n"
        "          and every member id tracked for the peer conduit, the staged member's included.\n",
    ),
    (
        "        spellbook._add_contracted_spell(spell, conduit_id)\n"
        "        spellbook._remove_contracted_spell(next_id, conduit_id)\n",
        "        spellbook._add_contracted_spell(spell, conduit_id)\n"
        "        spellbook._remove_contracted_spell(initial_id, conduit_id)\n",
    ),
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: anchor found {n} times - refusing")
    return text.replace(old, new)


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: <tree root> --check | --apply")
    root = pathlib.Path(sys.argv[1])
    out = {}
    text = (root / UNIT).read_text(encoding="utf-8")
    out[UNIT] = replace_once(text, UNIT_ANCHOR, UNIT_TESTS + UNIT_ANCHOR, "unit anchor")
    text = (root / INTEG).read_text(encoding="utf-8")
    for old, new in INTEG_IMPORTS:
        text = replace_once(text, old, new, f"integration import {old.strip()}")
    if not text.endswith(INTEG_TAIL_ANCHOR):
        raise SystemExit("integration file does not end with the expected last line - refusing")
    out[INTEG] = text + INTEG_TESTS
    text = (root / COMP).read_text(encoding="utf-8")
    for old, new in COMP_EDITS:
        text = replace_once(text, old, new, "component test")
    out[COMP] = text
    for rel, new_text in out.items():
        long = [i + 1 for i, ln in enumerate(new_text.split("\n")) if len(ln) > 120]
        old_long = [i + 1 for i, ln in enumerate((root / rel).read_text(encoding="utf-8").split("\n")) if len(ln) > 120]
        print(rel, "lines", new_text.count("\n"), "over-120 before/after", len(old_long), len(long))
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    for rel, new_text in out.items():
        (root / rel).write_text(new_text, encoding="utf-8")
        assert (root / rel).read_text(encoding="utf-8") == new_text
    print("applied and read back")


if __name__ == "__main__":
    main()
