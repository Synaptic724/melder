from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_transfer_footprint() -> None:
    """
    Purpose:
        Ensure each transfer-footprint component test starts on a clean Aether.
    Contract:
        - Resets the Aether singleton + rebinds Spellbook/Conduit._aether before and
          after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """Build a dynamic Spellbook with one scheduler worker for component tests."""
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def _local_spell(spellbook: Spellbook, spell_id: str) -> Optional[object]:
    """Resolve a locally owned spell by its current version id."""
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell
    return None


def test_build_transfer_metadata_stamps_the_source_and_target_footprint() -> None:
    """
    Purpose:
        Verify the conduit's metadata builder discovers and stamps the affected
        footprint (the migrated, domain-side responsibility) for a simple transfer.
    Contract:
        - source/target conduit ids + both as participants.
        - the spell id/index + a binding key are recorded.
        - the source spellbook id is resolved.
    Returns:
        None.
    Raises:
        AssertionError: If the stamped footprint is incomplete.
    """
    owner_book = _make_spellbook()
    target_book = _make_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        metadata = owner._build_transfer_transaction_metadata(
            spell=spell_id,
            target_conduit=target,
            move_creations=False,
            include_dependencies=False,
            force_unshare=True,
            invalidate_after_transfer=True,
            mark_dependencies_dirty=False,
        )

        assert metadata["source_conduit_id"] == owner.id
        assert metadata["target_conduit_id"] == target.id
        assert owner.id in metadata["participant_conduit_ids"]
        assert target.id in metadata["participant_conduit_ids"]
        assert metadata["spell_id"] == spell_id
        assert metadata["binding_keys"]
        assert metadata["source_spellbook_id"] is not None
    finally:
        owner.cleanup()
        target.cleanup()


def test_discover_transfer_footprint_returns_participants_and_identity_keys() -> None:
    """
    Purpose:
        Verify the footprint helper returns the participant + affected-identity sets the
        envelope strategy plans scopes from, with no mutation.
    Contract:
        - participant_conduit_ids includes source + target.
        - affected_identity_keys includes the source conduit identity.
        - preflight_dependencies is present (empty for a standalone spell).
    Returns:
        None.
    Raises:
        AssertionError: If the discovered footprint is incomplete.
    """
    owner_book = _make_spellbook()
    target_book = _make_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    spell = _local_spell(owner_book, spell_id)
    assert spell is not None
    try:
        footprint = owner._discover_transfer_footprint(
            spell_obj=spell,
            target_conduit=target,
            move_creations=False,
            include_dependencies=False,
            force_unshare=True,
            invalidate_after_transfer=True,
            mark_dependencies_dirty=False,
        )

        assert owner.id in footprint["participant_conduit_ids"]
        assert target.id in footprint["participant_conduit_ids"]
        assert ("conduit", owner.id) in footprint["affected_identity_keys"]
        assert "preflight_dependencies" in footprint
    finally:
        owner.cleanup()
        target.cleanup()


def test_transfer_spell_ownership_still_moves_the_spell_after_migration() -> None:
    """
    Purpose:
        Verify the full transfer surface still moves the lineage end-to-end after the
        footprint-discovery migration (metadata build -> envelope strategy -> ward effect).
    Contract:
        - The spell leaves the source spellbook and lands on the target, owned by target.
        - The summary reports source/target/spell.
    Returns:
        None.
    Raises:
        AssertionError: If the transfer no longer moves the spell.
    """
    owner_book = _make_spellbook()
    target_book = _make_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    spell = _local_spell(owner_book, spell_id)
    assert spell is not None
    spell_index_id = spell.spell_index.id
    try:
        summary = owner.transfer_spell_ownership(
            spell=spell_id,
            target_conduit=target,
        )

        assert summary["spell_id"] == spell_id
        assert summary["source"] == owner.id
        assert summary["target"] == target.id
        assert owner_book.get_spell_by_index_id(spell_index_id) is None
        transferred = target_book.get_spell_by_index_id(spell_index_id)
        assert transferred is not None
        assert transferred._owner_conduit_id == target.id
    finally:
        owner.cleanup()
        target.cleanup()
