"""Part A red tests: reload lanes, the Aether regime property, the recorded twin and restore stage 1."""
import sys

from apply_support import ApplySession

session = ApplySession(sys.argv[1])

RELOAD = "tests/unit/melder/aether/test_configuration_reload_lanes.py"
session.replace(RELOAD, '''def test_aether_from_recorded_payload_reloads_knob_and_reports_callables():
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
''', '''def test_aether_from_recorded_payload_reloads_knob_and_reports_callables():
    """
    Contract: the boolean knob and the spell-id regime reload and seal (a
    full payload reports nothing missing); presence-flagged callables
    report under code_participation (a record cannot carry a live
    resolver); the returned configuration is frozen but NOT yet activated
    (activation is the booting Aether's act).
    """
    configuration, report = AetherConfiguration.from_recorded_payload({
        "channel_logger_activation_enabled": True,
        "channel_logger_resolver_present": True,
        "default_logger_present": False,
        "process_wide_unique_spell_ids": True,
    })
    assert configuration.channel_logger_activation_enabled is True
    assert configuration.process_wide_unique_spell_ids is True
    assert report["missing"] == []
''')
session.replace(RELOAD, '''def test_aether_from_recorded_payload_defaults_missing_knob_with_report():
    """
    Contract: an absent knob falls to the documented default (False) and
    is reported under "missing" - never silently.
    """
    configuration, report = AetherConfiguration.from_recorded_payload({})
    assert configuration.channel_logger_activation_enabled is False
    assert report["missing"] == ["channel_logger_activation_enabled"]
    assert report["code_participation"] == []
    configuration.cleanup()
''', '''def test_aether_from_recorded_payload_defaults_missing_knob_with_report():
    """
    Contract: absent keys fall to their documented defaults (logger
    activation False, process-wide spell ids True) and each is reported
    under "missing" - never silently. A record sealed before the regime was
    recorded (record major 3 and older) reloads this way.
    """
    configuration, report = AetherConfiguration.from_recorded_payload({})
    assert configuration.channel_logger_activation_enabled is False
    assert configuration.process_wide_unique_spell_ids is True
    assert report["missing"] == [
        "channel_logger_activation_enabled",
        "process_wide_unique_spell_ids",
    ]
    assert report["code_participation"] == []
    configuration.cleanup()


def test_aether_from_recorded_payload_reloads_a_per_frame_regime_and_seals() -> None:
    """
    Purpose:
        A world recorded under per-frame spell ids must rebuild a root
        configuration that says so, or its restore runs process-wide ids.
    Contract:
        A recorded `process_wide_unique_spell_ids` False reloads False, the
        configuration comes back frozen (the regime cannot be changed after
        the reload), and nothing is reported missing.
    """
    configuration, report = AetherConfiguration.from_recorded_payload({
        "channel_logger_activation_enabled": False,
        "channel_logger_resolver_present": False,
        "default_logger_present": False,
        "process_wide_unique_spell_ids": False,
    })
    assert configuration.process_wide_unique_spell_ids is False
    assert configuration.frozen is True
    assert report["missing"] == []
    with pytest.raises(RuntimeError):
        configuration.set_process_wide_unique_spell_ids(True)
    configuration.cleanup()
''')

session.create("tests/component/melder/aether/test_aether_spell_id_regime_property_component.py", '''"""
Component tests for `Aether.process_wide_unique_spell_ids` (0.2.8213).

WHY THIS EXISTS. The spell-id regime is sealed when the first frame is born, and until now it was readable only
through private state: `Aether.configuration` may be a policy the next first frame will seal, or one a first frame
already sealed, and nothing said which. The crystallizer records the regime in the Aether twin and keys spell custody
by it, and a restore must know whether the live regime can still change, so the root answers the question itself.

Contract under test:
    1. a fresh Aether (no configuration, no frame) answers True;
    2. before any frame, the answer follows the installed configuration;
    3. the first frame seals the answer;
    4. a frame born without a configuration seals process-wide ids;
    5. a cleaned Aether refuses the read.
"""

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_regime_property() -> None:
    """Give each test an Aether with no frames and no configuration."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _policy(process_wide: bool) -> AetherConfiguration:
    """Return a mutable default Aether configuration with the given regime."""
    configuration = AetherConfiguration().with_defaults()
    configuration.set_process_wide_unique_spell_ids(process_wide)
    return configuration


def test_fresh_aether_reports_process_wide_ids() -> None:
    """Nothing installed and no frame: the default regime (process-wide) is in force."""
    aether = Aether()
    assert aether.configuration is None
    assert aether.list_frame_names() == ()
    assert aether.process_wide_unique_spell_ids is True


def test_before_any_frame_the_answer_follows_the_installed_configuration() -> None:
    """The next first frame seals the installed policy, so that policy's regime is the answer, and may still change."""
    aether = Aether()
    aether.configure(_policy(False))
    assert aether.process_wide_unique_spell_ids is False
    aether.configure(_policy(True))
    assert aether.process_wide_unique_spell_ids is True


def test_the_first_frame_seals_the_answer() -> None:
    """A per-frame policy installed before the first frame stays the answer once a frame exists."""
    aether = Aether()
    aether.configure(_policy(False))
    Spellbook(aetheric_frame="tenant_a")
    assert "tenant_a" in aether.list_frame_names()
    assert aether.process_wide_unique_spell_ids is False
    with pytest.raises(RuntimeError, match="spell-id regime is sealed while frames exist"):
        aether.configure(_policy(True))
    assert aether.process_wide_unique_spell_ids is False


def test_a_frame_born_without_configuration_seals_process_wide_ids() -> None:
    """The first frame installs frozen defaults without configuring the root; the answer is True."""
    aether = Aether()
    Spellbook(aetheric_frame="host")
    assert aether.configured is False
    assert aether.process_wide_unique_spell_ids is True


def test_a_cleaned_aether_refuses_the_read() -> None:
    """A torn-down root has no regime in force; reading it raises like every other guarded root read."""
    aether = Aether()
    aether.cleanup()
    with pytest.raises(RuntimeError):
        _ = aether.process_wide_unique_spell_ids
''')

TWIN = "tests/integration/melder/crystallizer/test_crystallizer_aether_twin_integration.py"
session.insert_after(TWIN, '''    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    assert crystallizer.describe_profile()["has_aether_crystal"] is False
''', '''

def _activated_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _recorded_aether_payload(crystallizer: Crystallizer) -> dict:
    """Seal one checkpoint and return the Aether twin configuration payload it captured."""
    checkpoint_id = crystallizer.create_checkpoint()
    replay = crystallizer.checkpoint_replay_data(checkpoint_id)
    return dict(replay["payloads"]["aether"]["root"]["configuration_payload"])


def test_aether_root_twin_records_the_spell_id_regime() -> None:
    """
    Purpose:
        A world run under per-frame spell ids must say so in its record, or a restore rebuilds it process-wide.
    Contract:
        Activating a per-frame root configuration while recording puts process_wide_unique_spell_ids False in the
        Aether twin; activating it on Aether (which re-applies the logger policy through the utility system, and the
        utility system re-emits the twin from live truth) keeps it False.
    Returns:
        None.
    """
    crystallizer = _activated_crystallizer()
    aether_configuration = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    aether_configuration.activate()
    assert _recorded_aether_payload(crystallizer)["process_wide_unique_spell_ids"] is False
    Aether().activate(aether_configuration)
    assert _recorded_aether_payload(crystallizer)["process_wide_unique_spell_ids"] is False


def test_utility_system_reemission_records_the_regime_in_force() -> None:
    """
    Purpose:
        The utility system's logger verbs re-emit the Aether twin from live truth, and that twin replaces the
        configuration's own, so it must carry the regime too or it would erase it.
    Contract:
        On an Aether that was never configured, a logger verb re-emits a twin carrying the default regime in force
        (True).
    Returns:
        None.
    """
    crystallizer = _activated_crystallizer()
    AetherUtilitySystem().set_channel_logger_activation_enabled(False)
    assert _recorded_aether_payload(crystallizer)["process_wide_unique_spell_ids"] is True
''')

session.create("tests/unit/melder/crystallizer/crystal_loader_system/test_restore_spell_id_regime.py", '''"""
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
    5. a record without the regime reports it missing and rebuilds the default.
"""

from typing import Dict, List, Optional

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
''')

for path in session.write():
    print(path)
