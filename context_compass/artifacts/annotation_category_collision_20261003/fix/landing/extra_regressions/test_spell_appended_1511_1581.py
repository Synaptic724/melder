def test_spell_frame_kind_defaults_to_none_with_no_contracts() -> None:
    """A Spell built without the kind arguments is a bare binding: kind none, no implemented Protocols."""
    from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind

    spell = _make_spell()
    try:
        assert spell.spellframe_kind is SpellframeKind.none
        assert spell.implemented_protocols == ()
    finally:
        spell.cleanup()


def test_spell_frame_kind_and_contracts_pass_through_and_survive_cleanup() -> None:
    """The kind and the implemented Protocols are stored as given and stay readable after cleanup, like `spellframe`."""
    from typing import Protocol

    from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind

    class IRepo(Protocol):
        pass

    states = _RecordingStates()
    spell = Spell(
        spell=object,
        spell_index=SpellIndex("fingerprint-contract"),
        spellframe=IRepo,
        binding_name=None,
        spell_name="RepoImpl",
        existence=Existence.unique,
        spell_type=SpellType.SPELL_WITH_SPELLFRAME,
        spell_id="fingerprint-contract",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(states),
        spellframe_kind=SpellframeKind.contract,
        implemented_protocols=(IRepo,),
    )
    assert spell.spellframe_kind is SpellframeKind.contract
    assert spell.implemented_protocols == (IRepo,)
    assert spell.spellframe is IRepo
    spell.cleanup()
    assert spell.spellframe_kind is SpellframeKind.contract
    assert spell.implemented_protocols == (IRepo,)
    assert spell.spellframe is IRepo


def test_spell_category_kind_records_the_label_and_no_contract() -> None:
    """A string category records kind category and an empty contract tuple."""
    from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind

    states = _RecordingStates()
    spell = Spell(
        spell=object,
        spell_index=SpellIndex("fingerprint-category"),
        spellframe="storage",
        binding_name="users",
        spell_name="UsersRepo",
        existence=Existence.unique,
        spell_type=SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        spell_id="fingerprint-category",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(states),
        spellframe_kind=SpellframeKind.category,
    )
    try:
        assert spell.spellframe_kind is SpellframeKind.category
        assert spell.implemented_protocols == ()
        assert spell.key == ("storage", "users")
    finally:
        spell.cleanup()
