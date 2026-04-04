import types

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each passive-ingest test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _bind_frame_posture(
        frame_name: str,
        *,
        rift_enabled: bool,
) -> None:
    """
    Bind one narrow frame posture into Aether for passive-ingest tests.

    Args:
        frame_name:
            Target frame name.
        rift_enabled:
            Whether the frame should be publishable into Nexus.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame(frame_name)
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=rift_enabled,
    )
    aether._bind_aetheric_frame_configuration(frame_configuration, frame_name)


def test_publish_frame_record_does_not_require_nexus_enable() -> None:
    """
    Verify frame publication succeeds before interactive Nexus enablement.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert nexus.is_enabled is False
    assert nexus._publish_frame_record(spellbook) is True

    record = nexus._canonical_store.frame_records_by_name["ops"]

    assert record.frame_name == "ops"
    assert record.origin_spellbook_id == "spellbook-alpha"
    assert record.rift_enabled is True


def test_publish_methods_short_circuit_when_frame_is_not_publishable() -> None:
    """
    Verify passive publication returns early when frame posture denies Rift.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=False)
    nexus = Nexus()

    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    spell = types.SimpleNamespace(
        profile=None,
        resolution_profile=None,
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
    )
    conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="conduit-1",
        _name="root",
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.normal,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _get_links=lambda: [],
        ),
    )

    assert nexus._publish_frame_record(spellbook) is False
    assert nexus._publish_conduit_record(conduit) is False
    assert nexus._publish_spell_record(spellbook, spell, "conduit-1") is False
    assert nexus._canonical_store.frame_records_by_name == {}
    assert nexus._canonical_store.conduit_records_by_id == {}
    assert nexus._canonical_store.spell_records_by_key == {}


def test_publish_spell_record_updates_primary_store_and_indexes() -> None:
    """
    Verify spell publication writes the primary record and secondary indexes.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    spell = types.SimpleNamespace(
        profile=None,
        resolution_profile=None,
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
    )

    assert nexus._publish_spell_record(spellbook, spell, "conduit-1") is True

    record_key = ("spellbook-alpha", "spell-1")
    assert record_key in nexus._canonical_store.spell_records_by_key
    assert record_key in nexus._canonical_store.spell_keys_by_frame_name["ops"]
    assert record_key in nexus._canonical_store.spell_keys_by_conduit_id["conduit-1"]
    assert record_key in nexus._canonical_store.spell_keys_by_spellbook_id["spellbook-alpha"]


def test_publish_conduit_record_ignores_lesser_conduits() -> None:
    """
    Verify the first passive-ingest slice ignores ordinary lesser conduits.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="root-1",
        _name="lesser",
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.lesser,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _get_links=lambda: [],
        ),
    )

    assert nexus._publish_conduit_record(conduit) is False
    assert nexus._canonical_store.conduit_records_by_id == {}


def test_remove_spell_and_conduit_records_clear_indexes() -> None:
    """
    Verify record removals clean their associated secondary indexes.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="conduit-1",
        _name="root",
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.normal,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _get_links=lambda: [],
        ),
    )
    spell = types.SimpleNamespace(
        profile=None,
        resolution_profile=None,
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
    )

    assert nexus._publish_conduit_record(conduit) is True
    assert nexus._publish_spell_record(spellbook, spell, "conduit-1") is True

    nexus._remove_spell_record("spellbook-alpha", "spell-1", "ops")
    nexus._remove_conduit_record("conduit-1", "ops")

    assert nexus._canonical_store.spell_records_by_key == {}
    assert nexus._canonical_store.conduit_records_by_id == {}
    assert nexus._canonical_store.spell_keys_by_frame_name == {}
    assert nexus._canonical_store.spell_keys_by_conduit_id == {}
    assert nexus._canonical_store.spell_keys_by_spellbook_id == {}
    assert nexus._canonical_store.conduit_ids_by_frame_name == {}
