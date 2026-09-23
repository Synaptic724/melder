"""Real Book/Crystallizer contracts for bind-hook presence, replay and live graft."""

import json
from collections.abc import Iterator
from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.crystal_analysis.preflight.configuration_loss_strategy import (
    ConfigurationLossStrategy,
)
from melder.crystallizer.crystal_loader_system.restore_engine import RestoreEngine
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
from melder.crystallizer.persistence.record_version import RecordVersion
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    RestoreAlpha,
    RestoreBeta,
    _activate_crystallizer,
    _dynamic_book,
    _fresh_boot,
)


@pytest.fixture(autouse=True)
def recording_world() -> Iterator[None]:
    """
    Purpose: Isolate the hosted recorder and Book/Conduit class references.
    Contract: Use the existing full-world bootstrap; tests perform no cache-file I/O.
    Yields: None while the test owns the recording world.
    """
    _fresh_boot()
    yield
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


def _checkpoint(crystallizer: Crystallizer) -> tuple[str, dict[str, Any]]:
    """
    Purpose: Capture a detached replay window through the public recorder facade.
    Args: crystallizer: Active hosted recorder.
    Returns: Checkpoint identity and its complete replay data.
    """
    checkpoint_id = crystallizer.create_checkpoint()
    return checkpoint_id, crystallizer.checkpoint_replay_data(checkpoint_id)


@pytest.mark.parametrize("pre_frozen", [False, True])
def test_origin_freeze_records_bind_markers_alongside_existing_hooks(pre_frozen: bool) -> None:
    """
    Purpose: Cover fresh freeze and origin-bearing re-freeze without callback serialization.
    Contract: The recorded Book retains configuration and existing hook categories.
    Args: pre_frozen: Finalize before conjure, as required when recorded binds exist.
    Returns: None.
    """
    crystallizer = Crystallizer()
    book = _make_spellbook(dynamic=True)
    calls: list[object] = []
    configuration = book.get_configuration()
    configuration.add_hook(book.id, "on_meld_pre_resolve", calls.append)
    configuration.add_hook(book.id, "on_conduit_activated", calls.append)
    book.add_bind_hooks(pre=[calls.append], activation=[calls.append], post=[calls.append])
    if pre_frozen:
        configuration.finalize()
    root = book.conjure(dynamic=True, name="marker-root")
    try:
        _checkpoint_id, window = _checkpoint(crystallizer)
        payload = window["payloads"]["spellbook"][book.id]
        assert payload["hook_names"] == [
            "conduit:on_conduit_activated", "meld:on_meld_pre_resolve",
            "bind:pre", "bind:activation", "bind:post",
        ]
        assert payload["configuration_payload"]["phase_scheduler_workers_per_spellbook"] == 1
        assert json.loads(json.dumps(payload)) == payload
        findings = ConfigurationLossStrategy().analyze(window["payloads"])
        assert all(row["severity"] == "info" for row in findings)
        for marker in ("bind:pre", "bind:activation", "bind:post"):
            assert any(marker in row["detail"] for row in findings)
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("through_conduit", [False, True])
def test_late_clear_and_reregister_replace_complete_book_twin(through_conduit: bool) -> None:
    """
    Purpose: Keep marker recording current after a Book has already conjured.
    Contract: Clearing removes bind markers without dropping configuration or Meld hooks.
    Args: through_conduit: Configure through the matching Conduit facade instead of the Book.
    Returns: None.
    """
    crystallizer = Crystallizer()
    book = _make_spellbook(dynamic=True)
    callbacks: list[object] = []
    configuration = book.get_configuration()
    configuration.add_hook(book.id, "on_meld_pre_resolve", callbacks.append)
    configuration.finalize()
    root = book.conjure(dynamic=True)
    registrar = root if through_conduit else book
    try:
        registrar.add_bind_hooks(pre=[callbacks.append], activation=[callbacks.append])
        _first_id, first = _checkpoint(crystallizer)
        before = first["payloads"]["spellbook"][book.id]
        assert before["hook_names"] == ["meld:on_meld_pre_resolve", "bind:pre", "bind:activation"]
        registrar.clear_bind_hooks()
        _second_id, second = _checkpoint(crystallizer)
        after = second["payloads"]["spellbook"][book.id]
        assert after["hook_names"] == ["meld:on_meld_pre_resolve"]
        assert after["configuration_payload"] == before["configuration_payload"]
        registrar.add_bind_hooks(post=[callbacks.append])
        _third_id, third = _checkpoint(crystallizer)
        assert third["payloads"]["spellbook"][book.id]["hook_names"] == [
            "meld:on_meld_pre_resolve", "bind:post",
        ]
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("scope", ["conduit", "frame"])
def test_markers_survive_formation_capture_and_checkpoint_json(scope: str) -> None:
    """
    Purpose: Exercise existing generic serializers with the additive stage marker values.
    Contract: Both formation scopes and the checkpoint codec preserve the Book's full payload.
    Args: scope: Formation anchor to capture.
    Returns: None; no physical cache files are required to qualify this data path.
    """
    crystallizer = Crystallizer()
    book = _dynamic_book()
    callbacks: list[object] = []
    book.add_bind_hooks(pre=[callbacks.append], activation=[callbacks.append], post=[callbacks.append])
    root = book.conjure(dynamic=True)
    try:
        checkpoint_id, window = _checkpoint(crystallizer)
        cached_item, = crystallizer._persistence_system.cached_item_forms(checkpoint_id)
        restored = PersistenceCrystal.from_cached_item(json.loads(json.dumps(cached_item)))
        try:
            assert restored.replay_data() == window
            assert restored.to_cached_item()["record_version"] == RecordVersion.CURRENT
        finally:
            restored.cleanup()
        formation = crystallizer._persistence_system.capture_formation_record(
            "bind-hooks",
            conduit_id=root.id if scope == "conduit" else None,
            frame_name="default" if scope == "frame" else None,
        )
        payload = json.loads(json.dumps(formation))["payloads"]["spellbook"][book.id]
        assert payload == window["payloads"]["spellbook"][book.id]
    finally:
        root.permanent_cleanup()


def test_emission_tap_receives_current_bind_stage_presence() -> None:
    """
    Purpose: Qualify the external value-payload transport without external services.
    Contract: The real emission tap carries initial, added and cleared stage markers.
    Returns: None; the supplied store callback only retains detached dictionaries.
    """
    crystallizer = Crystallizer()
    emissions: list[dict[str, Any]] = []

    def store(kind: str, _profile: str, _unit_id: str, payload: dict[str, Any]) -> None:
        """Retain only Book emission payloads from the real generic store seam."""
        if kind == "emission" and payload["crystal_kind"] == "SpellbookCrystal":
            emissions.append(json.loads(json.dumps(payload["payload"])))

    manager = ExternalPersistenceManagerConfiguration().with_store_handler(store).with_stream_emissions(True)
    crystallizer.configure_external_persistence_manager(manager)
    book = _dynamic_book()
    root = book.conjure(dynamic=True)
    try:
        callbacks: list[object] = []
        book.add_bind_hooks(pre=[callbacks.append])
        book.clear_bind_hooks()
        assert [payload["hook_names"] for payload in emissions] == [[], ["bind:pre"], []]
        assert all(payload["spellbook_id"] == book.id for payload in emissions)
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("recording,dynamic", [(False, True), (True, False)])
def test_hook_updates_do_not_record_outside_dynamic_recording_lane(recording: bool, dynamic: bool) -> None:
    """
    Purpose: Preserve recorder-off and automatic-mode behavior.
    Contract: Hook updates create no Book twin outside the established recording gates.
    Args: recording: Recorder active during updates; dynamic: Frame posture.
    Returns: None.
    """
    crystallizer = Crystallizer()
    if not recording:
        crystallizer.deactivate()
    book = _make_spellbook(dynamic=dynamic)
    book.get_configuration().finalize()
    callbacks: list[object] = []
    book.add_bind_hooks(pre=[callbacks.append])
    root = book.conjure(dynamic=dynamic)
    try:
        book.clear_bind_hooks()
        book.add_bind_hooks(post=[callbacks.append])
        if not recording:
            crystallizer = _activate_crystallizer()
        _checkpoint_id, window = _checkpoint(crystallizer)
        assert book.id not in window["payloads"].get("spellbook", {})
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("legacy", [False, True])
def test_full_restore_reports_missing_callback_code_and_replays_native_bindings(legacy: bool) -> None:
    """
    Purpose: Verify marker-only restore and legacy marker absence using the real engine.
    Contract: Bindings rebuild; recorded callbacks are reported, never silently reconstructed.
    Args: legacy: Remove hook_names to exercise the existing absent-field tolerance.
    Returns: None.
    """
    crystallizer = Crystallizer()
    book = _dynamic_book()
    callbacks: list[object] = []
    book.add_bind_hooks(pre=[callbacks.append], activation=[callbacks.append], post=[callbacks.append])
    spell_id = book.bind(spell=RestoreAlpha, existence="unique")
    root = book.conjure(dynamic=True, name="restored-hooks")
    checkpoint_id, window = _checkpoint(crystallizer)
    if legacy:
        del window["payloads"]["spellbook"][book.id]["hook_names"]
    root.permanent_cleanup()
    rebooted = _fresh_boot()
    engine = RestoreEngine(profile_name="default", checkpoint_ids=[checkpoint_id], chain=[window])
    try:
        report = engine.restore().describe()
        assert report["status"] == "complete"
        assert report["built_counts"]["spell_active"] == 1
        assert rebooted.get_spell_crystal(spell_id).id == spell_id
        assert len(callbacks) == 3
        hook_reasons = [row["reason"] for row in report["shortfalls"] if "hook_requires" in row["reason"]]
        assert hook_reasons == ([] if legacy else [
            "hook_requires_code_participation: bind:pre",
            "hook_requires_code_participation: bind:activation",
            "hook_requires_code_participation: bind:post",
        ])
    finally:
        engine.cleanup()


def test_graft_uses_receiving_book_hooks_for_active_and_staged_members() -> None:
    """
    Purpose: Verify live graft enters the receiving Book's actual callback lifecycle.
    Contract: Source callbacks do not transfer; active and staged new members each invoke host hooks.
    Returns: None; source claims are explicitly released before grafting identical versions.
    """
    crystallizer = Crystallizer()
    source = _dynamic_book()
    source_calls: list[object] = []
    source.add_bind_hooks(pre=[source_calls.append])
    active_id = source.bind(spell=RestoreAlpha, existence="unique")
    source_root = source.conjure(dynamic=True)
    index = source.find_spell_by_id(active_id).spell_index
    staged_id = source_root.bind_inactive(spell=RestoreBeta, spell_index=index, existence="unique")
    record = crystallizer.capture_index_graft(index.id)
    source_root.permanent_cleanup()
    host = _dynamic_book()
    host_root = host.conjure(dynamic=True)
    pre: list[object] = []
    activated: list[Spell] = []
    posts: list[Spell] = []
    try:
        host.add_bind_hooks(pre=[pre.append], activation=[activated.append], post=[posts.append])
        report = crystallizer.graft_index(record, host)
        assert report["status"] == "complete"
        assert pre == [RestoreAlpha, RestoreBeta]
        assert activated == posts and len(posts) == 2
        assert [spell.spell_id for spell in posts] == [active_id, staged_id]
        assert posts[0].spell_index is posts[1].spell_index
        assert posts[1]._active is False
        assert source_calls == [RestoreAlpha, RestoreBeta]
    finally:
        host_root.permanent_cleanup()


def test_activation_native_values_are_captured_before_post_observes_record() -> None:
    """
    Purpose: Verify publication consumes the actual activation-configured Spell.
    Contract: Native permissions changed during activation are recorded before post executes.
    Returns: None; this does not imply arbitrary Spell metadata serialization.
    """
    crystallizer = Crystallizer()
    book = _dynamic_book()
    observed: list[str] = []

    def activation(spell: Spell) -> None:
        """Select a native permission value before existing profile/capture work."""
        spell.permissions = Permissions.read

    def post(spell: Spell) -> None:
        """Observe the native value already captured through normal bind publication."""
        observed.append(crystallizer.get_spell_crystal(spell.spell_id).describe()["permissions_name"])

    try:
        book.add_bind_hooks(activation=[activation], post=[post])
        book.bind(spell=RestoreAlpha, existence="unique")
        assert observed == ["read"]
    finally:
        book.cleanup()
