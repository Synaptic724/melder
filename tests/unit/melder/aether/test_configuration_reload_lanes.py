"""
Unit tests for the configuration RELOAD lanes (owner ruling: EVERY config
rebuilds from recorded JSON truth through a dedicated load-and-freeze verb,
never from present-day defaults): SpellbookConfiguration,
AethericFrameConfiguration, AetherConfiguration, NexusConfiguration, and
CrystallizerConfiguration - plus the crystallizer's own policy twin.

Runs only on 3.14t (melder package root import chain).
"""
from pathlib import Path

import pytest

from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystals.crystallizer_crystal import (
    CrystallizerCrystal,
)
from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode


def test_load_recorded_dictionary_applies_recorded_and_seals_in_one_motion():
    """
    Contract: recorded values win, required keys the record lacks are
    backfilled AND reported per key, and the verb loads-and-FREEZES
    internally - a reloaded configuration comes back sealed, never
    mutable (owner ruling: reload is one motion, load it in, freeze it).
    """
    configuration = SpellbookConfiguration()
    # Registered rich-config properties only: the posture trio
    # (system_state / ai_native / rift) lives on the FRAME configuration,
    # not the spellbook property registry - feeding those here is the
    # rejection lane, covered by the refused-keys test below.
    outcome = configuration.load_recorded_dictionary({
        "phase_scheduler_workers_per_spellbook": 3,
        "disposal": True,
        "disposal_method_names": ["close"],
    })
    assert outcome["rejected"] == []
    assert "disposal" not in outcome["backfilled"]
    assert (
        "phase_scheduler_barrier_timeout_milliseconds"
        in outcome["backfilled"]
    )
    assert configuration.get_property(
        "phase_scheduler_workers_per_spellbook"
    ) == 3
    assert configuration.get_property("disposal") is True
    # Sealed on return: no caller-side finalize exists in the reload lane.
    with pytest.raises(Exception):
        configuration.set_property("disposal", False)
    configuration.cleanup()


def test_load_recorded_dictionary_reports_refused_keys_with_reason():
    """
    Contract: a recorded key the property system refuses comes back under
    "rejected" as "key: reason" - never raised, never silently coerced.
    """
    configuration = SpellbookConfiguration()
    outcome = configuration.load_recorded_dictionary({
        "no_such_property_xyz": 1,
    })
    assert len(outcome["rejected"]) == 1
    assert outcome["rejected"][0].startswith("no_such_property_xyz:")
    configuration.cleanup()


def test_load_recorded_dictionary_never_overwrites_recorded_with_default():
    """
    Contract: a recorded value for a defaults-table key is preserved and
    NOT listed as backfilled (recorded truth beats schema defaults).
    """
    configuration = SpellbookConfiguration()
    outcome = configuration.load_recorded_dictionary({"disposal": True})
    assert "disposal" not in outcome["backfilled"]
    assert configuration.get_property("disposal") is True
    configuration.cleanup()


def test_from_recorded_posture_round_trips_a_full_twin_payload():
    """
    Contract: a complete recorded twin payload rebuilds every posture
    field with zero missing keys - including non-default dev-ops values.
    """
    posture, missing = AethericFrameConfiguration.from_recorded_posture({
        "system_state_name": "dynamic",
        "ai_native_enabled": True,
        "rift_enabled": True,
        "dev_ops_payload": {
            "shared_framewide_spellbook_configuration": True,
            "system_caching_enabled": False,
            "system_cache_root_path": None,
            "disable_all_transactions_after_conjure": True,
            "disable_mutations": False,
            "disable_linking": True,
            "disable_bind": True,
            "disable_conduit_cluster": True,
            "disable_transfer_of_ownership": True,
            "disable_contract_mutation": True,
            "max_transaction_wait_time_in_seconds": 12.5,
        },
    })
    assert missing == []
    assert posture.system_state is SystemState.dynamic
    assert posture.ai_native_enabled is True
    assert posture.disable_mutations is False
    assert posture.disable_bind is True
    assert posture.max_transaction_wait_time_in_seconds == 12.5
    posture.cleanup()


def test_from_recorded_posture_reports_every_defaulted_key_and_seals():
    """
    Contract: a minimal payload rebuilds with constructor defaults and
    reports EVERY key that fell back (13 = 2 root + 11 dev-ops); the
    returned posture is SEALED (reload is one motion: load it in, freeze
    it) - the frame's bind lane copies values, it never mutates this
    object.
    """
    posture, missing = AethericFrameConfiguration.from_recorded_posture({
        "system_state_name": "dynamic",
    })
    assert len(missing) == 13
    assert "ai_native_enabled" in missing
    assert "disable_mutations" in missing
    assert posture.system_state is SystemState.dynamic
    assert posture.disable_mutations is True
    # Sealed on return: the fluent authoring lane is refused post-reload.
    with pytest.raises(RuntimeError):
        posture.with_rift_enabled(True)
    posture.cleanup()


def test_from_recorded_posture_refuses_a_stateless_payload():
    """
    Contract: system_state_name is hard-required - the reload lane never
    guesses a frame state.
    """
    with pytest.raises(ValueError):
        AethericFrameConfiguration.from_recorded_posture({
            "ai_native_enabled": True,
        })


def test_aether_from_recorded_payload_reloads_knob_and_reports_callables():
    """
    Contract: the boolean knob reloads and seals; presence-flagged
    callables report under code_participation (a record cannot carry a
    live resolver); the returned configuration is frozen but NOT yet
    activated (activation is the booting Aether's act).
    """
    configuration, report = AetherConfiguration.from_recorded_payload({
        "channel_logger_activation_enabled": True,
        "channel_logger_resolver_present": True,
        "default_logger_present": False,
    })
    assert configuration.channel_logger_activation_enabled is True
    assert report["missing"] == []
    assert report["code_participation"] == ["channel_logger_resolver"]
    assert configuration.frozen is True
    assert configuration.activated is False
    configuration.cleanup()


def test_aether_from_recorded_payload_defaults_missing_knob_with_report():
    """
    Contract: an absent knob falls to the documented default (False) and
    is reported under "missing" - never silently.
    """
    configuration, report = AetherConfiguration.from_recorded_payload({})
    assert configuration.channel_logger_activation_enabled is False
    assert report["missing"] == ["channel_logger_activation_enabled"]
    assert report["code_participation"] == []
    configuration.cleanup()


def test_nexus_load_recorded_dictionary_round_trips_emission_forms():
    """
    Contract: recorded enum member NAMES and collection LISTS (the
    emission scalar filter's forms) convert back to their registered
    types; recorded values win; the configuration seals WITHOUT the
    enable-confirmation emission (enable owns that moment).
    """
    configuration = NexusConfiguration()
    outcome = configuration.load_recorded_dictionary({
        "nexus_frame_mode": "single",
        "allowed_target_frame_names": ["default", "aux"],
        "max_active_rift_count": 7,
    })
    assert outcome["rejected"] == []
    assert configuration.get_property(
        "nexus_frame_mode"
    ) is NexusFrameMode.single
    assert configuration.get_property(
        "allowed_target_frame_names"
    ) == ("default", "aux")
    assert configuration.get_property("max_active_rift_count") == 7
    assert "allow_rift_creation" in outcome["backfilled"]
    assert configuration.frozen is True
    configuration.cleanup()


def test_nexus_reload_refuses_a_frozen_configuration():
    """
    Contract: the reload lane requires a fresh configuration object -
    reloading over sealed truth is refused loudly.
    """
    configuration = NexusConfiguration()
    configuration.load_recorded_dictionary({})
    with pytest.raises(RuntimeError):
        configuration.load_recorded_dictionary({})
    configuration.cleanup()


def test_crystallizer_load_recorded_dictionary_reloads_policy_and_seals():
    """
    Contract: the recorder's own policy reloads from its twin payload
    (list -> tuple for source roots), recorded values win over defaults,
    absences report per key, and the state seals in one motion.
    """
    configuration = CrystallizerConfiguration()
    outcome = configuration.load_recorded_dictionary({
        "user_source_root_paths": ["/recorded/root"],
        "checkpoint_interval_minutes": 15,
        "max_persistence_crystals": 25,
    })
    assert outcome["rejected"] == []
    # The property system normalizes source roots to resolved Paths, so
    # the recorded string round-trips as its platform-resolved form.
    assert configuration.get_property(
        "user_source_root_paths"
    ) == (Path("/recorded/root").resolve(),)
    assert configuration.get_property("checkpoint_interval_minutes") == 15
    assert configuration.get_property("max_persistence_crystals") == 25
    assert sorted(outcome["backfilled"]) == [
        "auto_flush_checkpoints", "remove_inactive_synthmodules",
        # S2 physical custody: retain_user_sources joined the schema and
        # backfills False for pre-S2 recorded payloads.
        "retain_user_sources",
    ]
    assert configuration.frozen is True
    configuration.cleanup()


def test_crystallizer_crystal_round_trips_its_payload():
    """
    Contract: the crystallizer policy twin is pure data - detached payload
    copies in, detached describe out, twin_kind "crystallizer".
    """
    crystal = CrystallizerCrystal(configuration_payload={
        "checkpoint_interval_minutes": 60,
        "user_source_root_paths": ["/somewhere"],
    })
    snapshot = crystal.describe()
    assert snapshot["twin_kind"] == "crystallizer"
    assert snapshot["configuration_payload"][
        "checkpoint_interval_minutes"
    ] == 60
    crystal.cleanup()
    crystal.cleanup()
    with pytest.raises(RuntimeError):
        crystal.describe()
