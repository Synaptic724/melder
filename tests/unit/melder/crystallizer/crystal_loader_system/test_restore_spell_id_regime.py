"""
Unit tests for restore stage 1 and the recorded spell-id regime (0.2.8213, refusal 0.2.8214).

WHY THIS EXISTS. Measured on 0.2.8212: a world recorded under per-frame spell ids restored under process-wide ids,
because the Aether record did not carry the regime and stage 1 rebuilt the default. Stage 1 now installs the recorded
regime while the live one can still change, and otherwise says so with a named shortfall - or, when the record binds
one spell id in two frames and cannot be rebuilt under the live regime, refuses before anything is built.

The chains are hand-made replay windows in the PersistenceCrystal shape; a real Aether is reset around each test.

Contract under test:
    1. nothing fixed (no configuration, no frame): the recorded per-frame regime is installed;
    2. a configured Aether with another regime: shortfall, the host configuration is kept;
    3. an unconfigured Aether whose first frame sealed another regime: shortfall, the recorded logger policy is
       installed under the live regime, and the restore completes;
    4. the opposite direction names its own shortfall;
    5. a record without the regime reports it missing and rebuilds the default;
    6. a host running process-wide ids refuses, before building anything, a per-frame record that binds one spell id
       in two frames (a payload without its own frame is placed in its Book's frame);
    7. recorded-to-live spell translation is kept per Book.
"""

from typing import Dict, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystal_loader_system.restore_engine import RestoreEngine
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


def _reset_world() -> None:
    """Reset every world singleton and rebind the static Aether references."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_world_singletons() -> None:
    """Isolate each test behind fresh Aether/Nexus/Crystallizer singletons."""
    _reset_world()
    yield
    _reset_world()


def _aether_payload(regime: Optional[bool], channel_logger_activation_enabled: bool = False) -> Dict[str, object]:
    """Build one AetherCrystal configuration payload; regime None leaves the key out (a pre-4.0 record)."""
    payload: Dict[str, object] = {
        "channel_logger_activation_enabled": channel_logger_activation_enabled,
        "channel_logger_resolver_present": False,
        "default_logger_present": False,
    }
    if regime is not None:
        payload["process_wide_unique_spell_ids"] = regime
    return payload


def _engine(configuration_payload: Dict[str, object],
            extra_journal: Optional[List[List[object]]] = None,
            extra_payloads: Optional[Dict[str, Dict[str, object]]] = None) -> RestoreEngine:
    """Build one single-window engine whose chain carries the Aether twin plus optional world rows."""
    journal: List[List[object]] = [[1, "aether", "root"]]
    journal.extend(extra_journal or [])
    payloads: Dict[str, Dict[str, object]] = {
        "aether": {"root": {"configuration_payload": configuration_payload}},
    }
    payloads.update(extra_payloads or {})
    return RestoreEngine(
        profile_name="default",
        checkpoint_ids=["01TESTREGIME0000000000000"],
        chain=[{"journal": journal, "payloads": payloads}],
    )


def _restore(engine: RestoreEngine) -> Dict[str, object]:
    """Run the engine and return its detached report."""
    report = engine.restore()
    try:
        return report.describe()
    finally:
        report.cleanup()
        engine.cleanup()


def _regime_shortfalls(report: Dict[str, object]) -> List[str]:
    """Return the reasons of every shortfall filed against the recorded regime."""
    return [
        str(entry["reason"])
        for entry in list(report["shortfalls"])
        if entry["kind"] == "aether" and entry["key"] == "process_wide_unique_spell_ids"
    ]


def _install(process_wide: bool) -> AetherConfiguration:
    """Configure and activate the live Aether with one regime, the way a host does before restoring."""
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(process_wide)
    policy.activate()
    Aether().activate(policy)
    return policy


def test_nothing_fixed_installs_the_recorded_per_frame_regime() -> None:
    """A fresh process restores a per-frame record under per-frame ids, with no regime shortfall."""
    report = _restore(_engine(_aether_payload(False)))
    assert report["status"] == "complete"
    assert _regime_shortfalls(report) == []
    assert Aether().configured is True
    assert Aether().process_wide_unique_spell_ids is False


def test_configured_host_with_another_regime_reports_and_keeps_its_configuration() -> None:
    """A host that configured process-wide ids keeps them, and the restore says what it could not rebuild."""
    host_policy = _install(True)
    report = _restore(_engine(_aether_payload(False)))
    assert report["status"] == "complete"
    assert _regime_shortfalls(report) == ["recorded_per_frame_ids_restored_under_process_wide_ids"]
    assert {
        "kind": "aether", "key": "root", "reason": "live_aether_already_configured_recorded_payload_skipped",
    } in list(report["shortfalls"])
    assert Aether().configuration is host_policy
    assert Aether().process_wide_unique_spell_ids is True


def test_sealed_frame_without_configuration_installs_the_logger_policy_under_the_live_regime() -> None:
    """
    A host frame sealed process-wide ids before the restore: the recorded logger policy still installs, under the
    live regime. Installing the rebuilt per-frame configuration itself would trip the sealed-regime guard and fail
    the whole restore; on 0.2.8212 the reload dropped the regime, so the mismatch passed silently.
    """
    Spellbook(aetheric_frame="host")
    assert Aether().configured is False
    report = _restore(_engine(_aether_payload(False, channel_logger_activation_enabled=True)))
    assert report["status"] == "complete"
    assert _regime_shortfalls(report) == ["recorded_per_frame_ids_restored_under_process_wide_ids"]
    assert Aether().configured is True
    assert Aether().configuration.channel_logger_activation_enabled is True
    assert Aether().process_wide_unique_spell_ids is True


def test_process_wide_record_into_a_per_frame_host_names_the_opposite_shortfall() -> None:
    """A process-wide record restored into a per-frame host is reported with its own reason."""
    _install(False)
    report = _restore(_engine(_aether_payload(True)))
    assert report["status"] == "complete"
    assert _regime_shortfalls(report) == ["recorded_process_wide_ids_restored_under_per_frame_ids"]
    assert Aether().process_wide_unique_spell_ids is False


def test_record_without_the_regime_reports_it_missing_and_rebuilds_the_default() -> None:
    """A pre-4.0 Aether twin reloads the default regime and says the key was missing."""
    report = _restore(_engine(_aether_payload(None)))
    assert report["status"] == "complete"
    assert _regime_shortfalls(report) == ["root_config_key_missing_defaulted_with_report"]
    assert Aether().configured is True
    assert Aether().process_wide_unique_spell_ids is True


def _one_spell_id_in_two_frames() -> Tuple[List[List[object]], Dict[str, Dict[str, object]]]:
    """Journal rows and payloads of a per-frame world that bound one spell id in two frames (two Books)."""
    journal: List[List[object]] = [
        [2, "spellbook", "book-a"],
        [3, "spellbook", "book-b"],
        [4, "spell_crystal", "sha@tenant_a"],
        [5, "spell_crystal", "sha@tenant_b"],
    ]
    payloads: Dict[str, Dict[str, object]] = {
        "spellbook": {
            "book-a": {"spellbook_id": "book-a", "frame_name": "tenant_a"},
            "book-b": {"spellbook_id": "book-b", "frame_name": "tenant_b"},
        },
        "spell_crystal": {
            "sha@tenant_a": {"id": "sha", "spellbook_id": "book-a", "frame_name": "tenant_a"},
            "sha@tenant_b": {"id": "sha", "spellbook_id": "book-b"},
        },
    }
    return journal, payloads


def _messages(error: BaseException) -> List[str]:
    """Return the messages of one exception and its chained causes."""
    messages: List[str] = []
    current: Optional[BaseException] = error
    while current is not None:
        messages.append(str(current))
        current = current.__cause__ or current.__context__
    return messages


def test_process_wide_host_refuses_a_record_binding_one_spell_id_in_two_frames() -> None:
    """
    A per-frame record that binds one spell id in two frames cannot be rebuilt under the process-wide ids a host
    configured - the second frame's bind would collide. Stage 1 refuses before anything is built (0.2.8214) instead
    of rolling back half a world at stage 6. tenant_b's payload carries no frame, so its Book's frame is used.
    """
    _install(True)
    journal, payloads = _one_spell_id_in_two_frames()
    engine = _engine(_aether_payload(False), extra_journal=journal, extra_payloads=payloads)
    try:
        with pytest.raises(RuntimeError, match="aether_configuration") as raised:
            engine.restore()
        assert any("two frames" in message for message in _messages(raised.value))
        assert "tenant_a" not in Aether().list_frame_names()
        assert "tenant_b" not in Aether().list_frame_names()
    finally:
        engine.cleanup()


def test_spell_translation_is_kept_per_book() -> None:
    """
    Stage 6 keys recorded-to-live spell translation by Book: one spell id rebuilt in two Books may bind to two new
    ids (each Book applies its own receiving policy), and each Book's selections, parked members and contract
    grants must follow its own. No public surface exposes this map, so the engine's helpers are exercised directly.
    """
    engine = _engine(_aether_payload(None))
    try:
        engine._map_spell_identity("book-a", "sha", "sha-live-a")
        engine._map_spell_identity("book-b", "sha", "sha-live-b")
        engine._map_spell_identity("book-c", "sha", "sha")
        assert engine._translate_spell("book-a", "sha") == "sha-live-a"
        assert engine._translate_spell("book-b", "sha") == "sha-live-b"
        assert engine._translate_spell("book-c", "sha") == "sha"
        assert engine._translate_spell("book-d", "sha") == "sha"
    finally:
        engine.cleanup()
