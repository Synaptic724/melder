"""Apply the probe tests (red on 0.2.8203): rewrite one unit test, add one unit and one component test.

Run from the repository root. Byte-level, CRLF-preserving; each anchor must match exactly once.
"""
import pathlib

UNIT = pathlib.Path("tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py")
COMPONENT = pathlib.Path("tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py")

OLD_UNIT = '''def test_spellspace_meld_describe_live_creation_status_reports_owner_conduit_many() -> None:
    """
    Verify SpellSpaceMeld reports owner conduit many-scope payloads.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    owner_creations.add_many_creations("spell-1", object())
    owner_creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        requires_spellspace_request=False,
    )
    _seed_spell(spellbook, spell)

    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "many",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "owner_conduit_many",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": None,
        "creation_count": 2,
    }
'''

NEW_UNIT = '''def test_spellspace_meld_describe_live_creation_status_reports_spellspace_many() -> None:
    """
    Verify SpellSpaceMeld reports many-scope payloads from the space's own store.

    A disposal-bearing `many` melded through a SpellSpace is registered in the
    space's store (the innermost scope), the only store the space purges it
    from, so the probe counts that bucket. Before 0.2.8204 it read the owner
    conduit's store and missed what the space held.
    """
    meld, spellspace_creations, _owner_creations, spellbook = _make_spellspace_meld()
    spellspace_creations.add_many_creations("spell-1", object())
    spellspace_creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        requires_spellspace_request=False,
    )
    _seed_spell(spellbook, spell)

    assert meld.has_live_creation(spell="spell-1") is True
    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": True,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "many",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "spellspace_many",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": "space-1",
        "creation_count": 2,
    }


def test_spellspace_meld_describe_live_creation_status_ignores_owner_conduit_many() -> None:
    """
    Verify SpellSpaceMeld does not count many objects the owner conduit holds.

    A `many` melded through the owner conduit lives in the conduit's store and
    is reported by the conduit's own probe; the space door neither registers
    into nor purges from that store, so it reports none.
    """
    meld, _spellspace_creations, owner_creations, spellbook = _make_spellspace_meld()
    owner_creations.add_many_creations("spell-1", object())
    spell = _SpellStub(
        spell_id="spell-1",
        existence=Existence.many,
        requires_spellspace_request=False,
    )
    _seed_spell(spellbook, spell)

    assert meld.has_live_creation(spell="spell-1") is False
    assert meld.describe_live_creation_status(spell="spell-1") == {
        "is_live": False,
        "spell_id": "spell-1",
        "spell_name": "Spell",
        "existence": "many",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "spellspace_many",
        "storage_owner_conduit_id": "conduit-1",
        "active_spellspace_id": "space-1",
        "creation_count": 0,
    }
'''

NEW_COMPONENT = '''

def test_component_spellspace_live_creation_probe_counts_space_held_many() -> None:
    """
    Purpose:
        Validate the SpellSpace door's live-creation probe counts the
        disposal-bearing many objects the space holds.
    Contract:
        - a disposal-bearing many melded through a space is held in the space's
          store and counted by the space door's probe (before 0.2.8204 the probe
          read the owner conduit's store and reported none).
        - a many melded through the owner conduit is counted by the conduit's
          probe and not by the space door's.
        - the space's exit disposes what it held; the conduit's object stays.
    Returns:
        None.
    Raises:
        AssertionError: If the probe misses the space's objects or counts the
            conduit's.
    """
    spellbook = _make_spellbook(disposal=True, disposal_methods=["cleanup"])
    spell_id = spellbook.bind(
        spell=DisposableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        conduit_instance = conduit.meld(spell_id=spell_id)
        with conduit.enter_spellspace() as space:
            first = space.meld(spell_id=spell_id)
            second = space.meld(spell_id=spell_id)
            assert space._meld.has_live_creation(spell=spell_id) is True
            status = space._meld.describe_live_creation_status(spell=spell_id)
            assert status["is_live"] is True
            assert status["creation_count"] == 2
            assert status["storage_scope_kind"] == "spellspace_many"
            assert status["storage_owner_conduit_id"] == conduit._id
            assert status["active_spellspace_id"] == space.id
            conduit_status = conduit.describe_live_creation_status(spell=spell_id)
            assert conduit_status["creation_count"] == 1
        assert first.cleanup_calls == 1
        assert second.cleanup_calls == 1
        assert conduit_instance.cleanup_calls == 0
        assert conduit.has_live_creation(spell=spell_id) is True
    finally:
        conduit.permanent_cleanup()
'''


def _crlf(text: str) -> bytes:
    return text.replace("\n", "\r\n").encode("utf-8")


unit = UNIT.read_bytes()
old = _crlf(OLD_UNIT)
assert unit.count(old) == 1, unit.count(old)
UNIT.write_bytes(unit.replace(old, _crlf(NEW_UNIT)))

component = COMPONENT.read_bytes()
assert component.endswith(b"        conduit.permanent_cleanup()\r\n")
assert b"test_component_spellspace_live_creation_probe_counts_space_held_many" not in component
COMPONENT.write_bytes(component + _crlf(NEW_COMPONENT))
print("tests applied")
