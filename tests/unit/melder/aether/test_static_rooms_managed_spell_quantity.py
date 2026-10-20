"""
Unit tests: the static rooms treat a managed spell like `many` (STORY-2026-10-15-managed_quantity_pool, S3).

A static room hands out an already-live stored object. A managed spell stores none - its objects are leased from a
pool - so, like `many` and `unique_per_spell_space`, it is an unsupported static existence: no static access, and
never listed as a live static spell.
"""
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.nexus.rift.frame_viewer.static_frame_viewer import StaticFrameViewer
from tests.unit.melder.aether.test_frame_viewer_projection import _build_viewer
from tests.unit.melder.aether.test_static_command_system_direct import (
    _make_spell_record,
    _make_static_command_system,
)


@pytest.fixture
def fresh_singletons() -> Iterator[None]:
    """Reset the singleton runtime surfaces around a static-viewer test."""
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether


def test_static_access_to_a_managed_spell_is_an_unsupported_static_existence() -> None:
    """Asking a static room for a managed spell's object names the existence instead of probing a store."""
    command_system, viewer = _make_static_command_system()
    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-managed",)
    viewer.descriptor.spell_records_by_key["ops-spellbook:managed-sha"] = _make_spell_record(
        spell_id="managed-sha",
        spell_index_id="lineage-managed",
        existence=Existence.managed_spell_quantity,
    )
    with pytest.raises(ValueError, match="unsupported static existence 'managed_spell_quantity'"):
        command_system.get_spell_by_index_id("lineage-managed")


def test_static_status_of_a_managed_spell_reports_it_unsupported() -> None:
    """The status payload says why a managed spell is never available statically."""
    command_system, viewer = _make_static_command_system()
    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-managed",)
    viewer.descriptor.spell_records_by_key["ops-spellbook:managed-sha"] = _make_spell_record(
        spell_id="managed-sha",
        spell_index_id="lineage-managed",
        existence=Existence.managed_spell_quantity,
    )
    command_system._aether = type(
        "_AetherStub",
        (),
        {"get_root_conduit_by_id": lambda self, conduit_id, frame_name: type(
            "_Owner", (), {"has_live_creation": lambda self, *, spell: True},
        )()},
    )()
    status = command_system.describe_spell_status_by_index_id("lineage-managed")
    assert (status["is_static_supported"], status["is_available"], status["reason"]) == (
        False, False, "unsupported_static_existence",
    )


def test_a_managed_spell_is_never_a_live_static_spell(
        fresh_singletons: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """The static viewer lists only spells with one stored object; a live managed pool does not make one."""
    viewer = StaticFrameViewer.from_frame_viewer(_build_viewer(("ops",)))
    descriptor = viewer._get_required_frame_descriptor("ops")
    spell_record = descriptor.spell_records_by_key[("ops-spellbook", "ops-spell")]
    spell_record.owner_conduit_id = "ops-conduit"

    class _LiveOwner:
        """An owner root whose probe says the spell is live."""

        def has_live_creation(self, spell: str) -> bool:
            """Answer live."""
            return True

    monkeypatch.setattr(StaticFrameViewer, "_get_owner_conduit", lambda self, frame_name, conduit_id: _LiveOwner())
    spell_record.existence = Existence.unique
    assert viewer._is_spell_record_live("ops", spell_record) is True
    spell_record.existence = Existence.managed_spell_quantity
    assert viewer._is_spell_record_live("ops", spell_record) is False
