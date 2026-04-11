import types
import threading

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor_manager import FrameDescriptorManager
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.configuration.system_state import SystemState


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each manager unit test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _bind_frame_posture(
        frame_name: str,
        *,
        rift_enabled: bool,
) -> Aether:
    """
    Bind one frame posture into Aether for manager tests.

    Args:
        frame_name:
            Target frame name.
        rift_enabled:
            Whether the frame should be publishable.

    Returns:
        Aether: Active Aether singleton.
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
    return aether


def test_manager_publish_frame_record_creates_descriptor_and_overview() -> None:
    """
    Verify frame publication lazily creates the descriptor and stores overview.

    Returns:
        None.
    """
    aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(aether)
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert manager._publish_frame_record(spellbook) is True

    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.frame_configuration is not None
    assert descriptor.frame_overview is not None
    assert descriptor.frame_overview.frame_name == "ops"
    assert descriptor.frame_overview.payload.rift_enabled is True


def test_manager_constructor_rejects_missing_aether() -> None:
    """
    Verify the manager fails fast when no substrate is provided.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="aether cannot be None"):
        FrameDescriptorManager(None)


def test_manager_create_and_detach_nexus_frame_record_updates_descriptor_indexes() -> None:
    """
    Verify Nexus-managed frame records are stored and detached through manager.

    Returns:
        None.
    """
    aether = Aether()
    manager = FrameDescriptorManager(aether)

    record = manager._create_nexus_frame_record(
        "ops",
        creator_rift_id="rift-1",
        immutable=False,
        nexus_frame_mode=NexusFrameMode.single,
    )

    assert manager._get_nexus_frame_record("ops") is record
    assert manager._count_nexus_frame_records() == 1
    assert manager._list_nexus_frame_names() == ["ops"]

    detached = manager._detach_nexus_frame_record("ops")

    assert detached is record
    assert manager._get_nexus_frame_record("ops") is None
    assert manager._count_nexus_frame_records() == 0
    assert manager._list_nexus_frame_names() == []


def test_manager_publishable_frame_posture_short_circuits_when_rift_disabled() -> None:
    """
    Verify manager keeps the descriptor but denies passive publication posture.

    Returns:
        None.
    """
    aether = _bind_frame_posture("ops", rift_enabled=False)
    manager = FrameDescriptorManager(aether)

    posture = manager._get_publishable_frame_posture("ops")

    assert posture is None
    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.frame_configuration is not None
    assert descriptor.frame_configuration.rift_enabled is False


def test_manager_refresh_frame_posture_cache_returns_none_for_missing_frame() -> None:
    """
    Verify posture refresh clears descriptor state when the frame is missing.

    Returns:
        None.
    """
    aether = Aether()
    manager = FrameDescriptorManager(aether)

    posture = manager._refresh_frame_posture_cache("missing")

    assert posture is None
    descriptor = manager._get_required_frame_descriptor("missing")
    assert descriptor.frame_configuration is None
    assert descriptor.frame_handle is None


def test_manager_refresh_frame_posture_cache_returns_none_when_posture_not_bound() -> None:
    """
    Verify posture refresh leaves a descriptor without posture when the frame
    exists but has no bound frame configuration.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame("ops")
    manager = FrameDescriptorManager(aether)

    posture = manager._refresh_frame_posture_cache("ops")

    assert posture is None
    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.frame_configuration is None
    assert descriptor.frame_handle is None


def test_manager_descriptor_helpers_cover_create_has_and_missing_record_cases() -> None:
    """
    Verify descriptor-registry helpers expose expected missing and present behavior.

    Returns:
        None.
    """
    manager = FrameDescriptorManager(Aether())

    assert manager._has_frame_descriptor("ops") is False
    assert manager._detach_nexus_frame_record("ops") is None

    descriptor = manager._get_or_create_frame_descriptor("ops")

    assert manager._has_frame_descriptor("ops") is True
    assert manager._get_required_frame_descriptor("ops") is descriptor

    with pytest.raises(ValueError, match="Nexus frame 'ops' was not found."):
        manager._get_required_nexus_frame_record("ops")


def test_manager_required_getters_raise_for_missing_records() -> None:
    """
    Verify required descriptor/frame-record getters fail loudly when absent.

    Returns:
        None.
    """
    manager = FrameDescriptorManager(Aether())

    with pytest.raises(KeyError, match="ops"):
        manager._get_required_frame_descriptor("ops")

    with pytest.raises(ValueError, match="Nexus frame 'ops' was not found."):
        manager._get_required_nexus_frame_record("ops")


def test_manager_get_or_create_nexus_frame_record_reuses_existing_record() -> None:
    """
    Verify get-or-create returns the same Nexus frame record on repeat calls.

    Returns:
        None.
    """
    manager = FrameDescriptorManager(Aether())

    first_record = manager._get_or_create_nexus_frame_record(
        "ops",
        creator_rift_id="rift-1",
        immutable=False,
        nexus_frame_mode=NexusFrameMode.single,
    )
    second_record = manager._get_or_create_nexus_frame_record(
        "ops",
        creator_rift_id="rift-2",
        immutable=True,
        nexus_frame_mode=NexusFrameMode.indexed,
    )

    assert second_record is first_record
    assert second_record.creator_rift_id == "rift-1"
    assert second_record.immutable is False


def test_manager_publish_conduit_record_short_circuits_for_none_or_unpublishable_frame() -> None:
    """
    Verify conduit publication refuses missing conduits and unpublished frames.

    Returns:
        None.
    """
    unpublished_aether = _bind_frame_posture("ops", rift_enabled=False)
    manager = FrameDescriptorManager(unpublished_aether)
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
    assert manager._publish_conduit_record(None) is False
    assert manager._publish_conduit_record(conduit) is False
    assert manager._remove_conduit_record("conduit-1", "ops") is False


def test_manager_publish_conduit_record_accepts_lesser_conduits() -> None:
    """
    Verify conduit publication accepts lesser conduits in the first expanded slice.

    Returns:
        None.
    """
    published_aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(published_aether)
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    root_conduit = types.SimpleNamespace(_id="root-1", _conduit_ward=None)
    lesser_conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="root-1",
        _name=None,
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.lesser,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _parent_conduit=root_conduit,
            _get_links=lambda: [],
        ),
    )

    assert manager._publish_conduit_record(lesser_conduit) is True

    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.conduit_records_by_id["conduit-1"].payload.conduit_state is ConduitState.lesser
    assert descriptor.conduit_records_by_id["conduit-1"].payload.parent_conduit_id == "root-1"
    assert descriptor.conduit_records_by_id["conduit-1"].payload.lineage_depth == 1


def test_manager_publish_spell_record_requires_descriptor_payload_and_publishable_frame() -> None:
    """
    Verify spell publication rejects missing descriptor payloads and disabled frames.

    Returns:
        None.
    """
    published_aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(published_aether)
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    invalid_spell = types.SimpleNamespace(
        profile=object(),
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=None,
        existence=None,
    )

    with pytest.raises(RuntimeError, match="requires a non-empty descriptor payload"):
        manager._publish_spell_record(spellbook, invalid_spell, "conduit-1")

    unpublished_aether = _bind_frame_posture("shadow", rift_enabled=False)
    unpublished_manager = FrameDescriptorManager(unpublished_aether)
    valid_spell = types.SimpleNamespace(
        profile=types.SimpleNamespace(
            to_descriptor_payload=lambda: SpellDescriptorPayload(
                payload_type="general",
                binding_payload={},
                resolution_payload={},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            )
        ),
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=None,
        existence=None,
    )
    shadow_spellbook = types.SimpleNamespace(_aetheric_frame="shadow", _id="spellbook-shadow")

    assert unpublished_manager._publish_spell_record(
        shadow_spellbook,
        valid_spell,
        "conduit-1",
    ) is False
    assert unpublished_manager._remove_spell_record(
        "spellbook-shadow",
        "spell-1",
        "shadow",
    ) is False


def test_manager_cleanup_cleans_owned_descriptors_and_nuls_state() -> None:
    """
    Verify manager cleanup cascades into owned descriptors and releases state.

    Returns:
        None.
    """
    aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(aether)
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert manager._publish_frame_record(spellbook) is True
    descriptor = manager._get_required_frame_descriptor("ops")

    manager.cleanup()

    assert descriptor.cleaned is True
    assert manager._lock is None


def test_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the manager.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(aether)
    manager._get_or_create_frame_descriptor("ops")
    coordinated_lock = _CoordinatedLock()
    manager._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        manager.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert manager.cleaned is True
    assert manager._lock is None


def test_manager_rejects_invalid_published_payload_and_record_contracts() -> None:
    """
    Verify payload and record validators fail loudly for unsupported contracts.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="Unsupported frame descriptor payload version"):
        FrameDescriptorManager._validate_published_frame_payload(
            FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
                rift_enabled=True,
                root_conduit_count=0,
                root_conduit_ids=tuple(),
                named_root_conduits=tuple(),
                conduit_cloud_entry_count=0,
                conduit_cloud_names=tuple(),
                cluster_count=0,
                cluster_names=tuple(),
                payload_version="9.9.9",
            )
        )

    with pytest.raises(ValueError, match="Unsupported conduit descriptor payload version"):
        FrameDescriptorManager._validate_published_conduit_payload(
            ConduitDescriptorPayload(
                conduit_name="root",
                conduit_state=ConduitState.normal,
                policy=Policies.default,
                peer_conduit_ids=tuple(),
                payload_version="9.9.9",
            )
        )

    with pytest.raises(ValueError, match="Unsupported spell descriptor payload type"):
        FrameDescriptorManager._validate_published_spell_payload(
            SpellDescriptorPayload(
                payload_type="invalid",
                binding_payload={},
                resolution_payload={},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            )
        )

    with pytest.raises(ValueError, match="Unsupported frame record Nexus contract"):
        FrameDescriptorManager._validate_published_record_contract(
            nexus_label="unsupported",
            nexus_version="9.9.9",
            label="frame record",
        )
