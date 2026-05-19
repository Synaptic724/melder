import json
import logging
from types import SimpleNamespace

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.spellbook.configuration.system_state import SystemState


@pytest.fixture(autouse=True)
def fresh_nexus_runtime() -> None:
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _create_enabled_nexus() -> Nexus:
    nexus = Nexus(aether=Aether())
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    nexus.enable(configuration)
    return nexus


def _bind_target_frame_configuration(
        frame_name: str,
        *,
        rift_enabled: bool,
        ai_native_enabled: bool = False,
        system_state: SystemState = SystemState.automatic,
) -> None:
    aether = Aether()
    aether._ensure_frame(frame_name)
    posture = AethericFrameConfiguration(
        origin_spellbook_id="{0}-spellbook".format(frame_name),
        system_state=system_state,
        ai_native_enabled=ai_native_enabled,
        rift_enabled=rift_enabled,
    )
    aether._ensure_frame(frame_name).bind_frame_configuration(posture)


def _bind_target_runtime_posture(
        frame_name: str,
        *,
        rift_enabled: bool,
        ai_native_enabled: bool = False,
        system_state: SystemState = SystemState.automatic,
) -> AethericFrameConfiguration:
    aether = Aether()
    aether._ensure_frame(frame_name)
    posture = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=system_state,
        ai_native_enabled=ai_native_enabled,
        rift_enabled=rift_enabled,
    )
    aether._ensure_frame(frame_name).bind_frame_configuration(posture)
    return posture


def _seed_descriptor(frame_name: str) -> FrameRecord:
    descriptor = Nexus()._get_or_create_frame_descriptor(frame_name)
    descriptor.set_frame_handle(SimpleNamespace(name=frame_name))
    record = FrameRecord(
        frame_name=frame_name,
        frame_id="{0}-frame".format(frame_name),
        config_origin_spellbook_id="{0}-spellbook".format(frame_name),
        payload=FrameDescriptorPayload(
            system_state=SystemState.automatic,
            ai_native_enabled=False,
            rift_enabled=True,
            root_conduit_count=0,
            root_conduit_ids=tuple(),
            named_root_conduits=tuple(),
            conduit_cloud_entry_count=0,
            conduit_cloud_names=tuple(),
            cluster_count=0,
            cluster_names=tuple(),
        ),
    )
    descriptor.set_frame_overview(record)
    return record


def _build_typed_json_payload(
        frame_name: str,
        *,
        view_profile_name: str,
        codegen_profile_name: str,
        marker: str,
) -> str:
    return json.dumps(
        {
            "frame_name": frame_name,
            "view_configuration": {
                "profile_name": view_profile_name,
                "profile_version": "0.0.1",
                "precision_profile_name": "precision",
                "precision_profile_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
                "frame_override_ruleset": {
                    "name": "frame_override_{0}".format(marker),
                    "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "member_override_ruleset": {
                    "name": "member_override",
                    "rules": [],
                },
            },
            "codegen_configuration": {
                "profile_name": codegen_profile_name,
                "profile_version": "0.0.1",
                "frame_override_ruleset": {
                    "name": "frame_override",
                    "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "capability_override_ruleset": {
                    "name": "capability_override",
                    "rules": [],
                },
            },
        },
        sort_keys=True,
    )


class _FakeGate:
    def __init__(self, gate_id: str) -> None:
        self.id = gate_id
        self.cleaned = False

    def cleanup(self) -> None:
        self.cleaned = True


class _FakeGateController:
    def __init__(self, gate: _FakeGate) -> None:
        self.gate = gate
        self.created = []
        self.unregistered = []

    def create_rift_gate(self, rift_id: str):
        self.created.append(rift_id)
        return self.gate

    def unregister_rift_gate(self, rift_id: str) -> None:
        self.unregistered.append(rift_id)

    def cleanup(self) -> None:
        return None


def test_nexus_create_rift_unregisters_gate_and_does_not_consume_configuration_when_add_rift_fails(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    nexus = _create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    gate = _FakeGate("rift-1")
    nexus._rift_gate_controller = _FakeGateController(gate)
    created_rifts = []

    class _FakeRift:
        def __init__(self, *_args, **kwargs) -> None:
            self.id = kwargs["rift_id"]
            self.rift_name = kwargs["rift_name"]
            self.cleaned = False
            created_rifts.append(self)

        def mark_active(self) -> None:
            return None

        def cleanup(self) -> None:
            self.cleaned = True

    monkeypatch.setattr(
        "melder.nexus.rift.rift.Rift",
        _FakeRift,
    )
    monkeypatch.setattr(
        Nexus,
        "add_rift",
        lambda self, rift: (_ for _ in ()).throw(RuntimeError("add_rift_failure")),
    )

    with pytest.raises(RuntimeError, match="add_rift_failure"):
        nexus.create_rift(
            configuration=configuration,
            rift_name="alpha",
            rift_id="rift-1",
        )

    assert configuration.consumed is False
    assert nexus._rift_gate_controller.created == ["rift-1"]
    assert nexus._rift_gate_controller.unregistered == ["rift-1"]
    assert created_rifts[0].cleaned is True
    assert nexus._rifts_by_id == {}


def test_nexus_create_rift_cleans_gate_when_constructor_raises(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    nexus = _create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    gate = _FakeGate("rift-1")
    nexus._rift_gate_controller = _FakeGateController(gate)

    class _FailingRift:
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("rift_init_failure")

    monkeypatch.setattr(
        "melder.nexus.rift.rift.Rift",
        _FailingRift,
    )

    with pytest.raises(RuntimeError, match="rift_init_failure"):
        nexus.create_rift(
            configuration=configuration,
            rift_name="alpha",
            rift_id="rift-1",
        )

    assert configuration.consumed is False
    assert nexus._rift_gate_controller.unregistered == ["rift-1"]
    assert gate.cleaned is True
    assert nexus._rifts_by_id == {}


def test_nexus_add_rift_rejects_gate_mismatch_without_registry_mutation() -> None:
    nexus = _create_enabled_nexus()
    registered_gate = object()
    other_gate = object()

    class _MismatchGateController:
        def get_rift_gate(self, _rift_id):
            return registered_gate

        def register_rift_gate(self, _rift_id, _gate) -> None:
            return None

        def cleanup(self) -> None:
            return None

    nexus._rift_gate_controller = _MismatchGateController()
    rift = SimpleNamespace(
        id="rift-1",
        rift_name="alpha",
        rift_gate=other_gate,
        list_assigned_frame_names=lambda: ("ops",),
        mark_registered=lambda: (_ for _ in ()).throw(AssertionError("should_not_register")),
    )

    with pytest.raises(ValueError, match="does not match the registered gate"):
        nexus.add_rift(rift)

    assert nexus._rifts_by_id == {}
    assert nexus._rift_ids_by_name == {}
    assert nexus._target_frame_ref_counts == {}


def test_nexus_remove_rift_decrements_ref_counts_before_frame_cleanup(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    nexus = _create_enabled_nexus()
    cleanup_calls = []

    class _FakeRift:
        def __init__(self) -> None:
            self.id = "rift-1"
            self.rift_name = "alpha"
            self.cleaned = False

        def list_assigned_frame_names(self):
            return ("ops", "finance")

        def cleanup(self) -> None:
            self.cleaned = True
            cleanup_calls.append("rift_cleanup")

    rift = _FakeRift()
    nexus._rifts_by_id = {rift.id: rift}
    nexus._rift_ids_by_name = {rift.rift_name: rift.id}
    nexus._target_frame_ref_counts = {"ops": 1, "finance": 1}
    class _RemoveGateController:
        def unregister_rift_gate(self, _rift_id) -> None:
            cleanup_calls.append("unregister")

        def cleanup(self) -> None:
            return None

    nexus._rift_gate_controller = _RemoveGateController()

    monkeypatch.setattr(
        type(nexus._frame_manager),
        "get_frame_names_to_cleanup_for_removed_rift",
        lambda self, rift_id: ["nexus-frame"],
    )

    def _record_remove(self, frame_name: str) -> None:
        assert nexus._target_frame_ref_counts == {}
        assert rift.cleaned is False
        cleanup_calls.append(("frame_remove", frame_name))

    monkeypatch.setattr(type(nexus._frame_manager), "remove", _record_remove)

    nexus.remove_rift(rift.id)

    assert cleanup_calls == [
        "unregister",
        ("frame_remove", "nexus-frame"),
        "rift_cleanup",
    ]
    assert nexus._rifts_by_id == {}
    assert nexus._rift_ids_by_name == {}


def test_nexus_refresh_rift_projection_sets_reenables_gates_after_refresh_failure(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    nexus = Nexus(aether=Aether())
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_projection_refresh_gate(True)
    configuration.with_projection_refresh_gate_timeout_seconds(7.0)
    configuration.with_projection_refresh_gate_poll_interval_seconds(0.5)
    nexus.enable(configuration)

    calls = []

    def _raise_refresh(*, frame_names=None):
        calls.append(("refresh", "rift-1", frame_names))
        raise RuntimeError("refresh_failure")

    first_impacted_rift = SimpleNamespace(
        id="rift-1",
        list_assigned_frame_names=lambda: ("ops", "finance"),
        cleanup=lambda: None,
        refresh_runtime_projections=_raise_refresh,
    )
    second_impacted_rift = SimpleNamespace(
        id="rift-2",
        list_assigned_frame_names=lambda: ("finance",),
        cleanup=lambda: None,
        refresh_runtime_projections=lambda *, frame_names=None: calls.append(
            ("refresh", "rift-2", frame_names)
        ),
    )
    nexus._rifts_by_id = {
        "rift-1": first_impacted_rift,
        "rift-2": second_impacted_rift,
    }
    monkeypatch.setattr(
        Nexus,
        "disable_rift_gate",
        lambda self, rift_id: calls.append(("disable", rift_id)),
    )
    monkeypatch.setattr(
        Nexus,
        "enable_rift_gate",
        lambda self, rift_id: calls.append(("enable", rift_id)),
    )
    monkeypatch.setattr(
        Nexus,
        "_wait_until_rift_gate_is_idle",
        lambda self, rift_id, *, timeout, interval: calls.append(
            ("wait", rift_id, timeout, interval)
        ),
    )

    with pytest.raises(RuntimeError, match="refresh_failure"):
        nexus._refresh_rift_projection_sets_for_frames(("ops", "finance"))

    assert calls == [
        ("disable", "rift-1"),
        ("disable", "rift-2"),
        ("wait", "rift-1", 7.0, 0.5),
        ("wait", "rift-2", 7.0, 0.5),
        ("refresh", "rift-1", ("ops", "finance")),
        ("enable", "rift-1"),
        ("enable", "rift-2"),
    ]


def test_nexus_refresh_rift_projection_sets_returns_early_when_disabled() -> None:
    nexus = Nexus(aether=Aether())
    nexus.disable()
    calls = []
    nexus._rifts_by_id = {
        "rift-1": SimpleNamespace(
            id="rift-1",
            list_assigned_frame_names=lambda: ("ops",),
            cleanup=lambda: None,
            refresh_runtime_projections=lambda *, frame_names=None: calls.append(frame_names),
        )
    }

    nexus._refresh_rift_projection_sets_for_frames(("ops",))

    assert calls == []


@pytest.mark.parametrize(
    ("bind_runtime_posture", "rift_enabled", "ai_native_enabled", "system_state", "requested_space_type", "message"),
    [
        (True, False, False, SystemState.automatic, RiftSpaceType.static, "rift_enabled"),
        (True, True, True, SystemState.automatic, RiftSpaceType.static, "ai_native_enabled but is not in dynamic"),
        (True, True, False, SystemState.dynamic, RiftSpaceType.codegen, "ai_native_enabled"),
        (True, True, True, SystemState.automatic, RiftSpaceType.codegen, "ai_native_enabled but is not in dynamic"),
        (False, False, False, SystemState.automatic, RiftSpaceType.static, "rift_enabled"),
    ],
)
def test_nexus_validate_target_frame_runtime_requirements_rejects_invalid_posture(
        bind_runtime_posture: bool,
        rift_enabled: bool,
        ai_native_enabled: bool,
        system_state: SystemState,
        requested_space_type: RiftSpaceType,
        message: str,
) -> None:
    nexus = _create_enabled_nexus()
    if bind_runtime_posture and ai_native_enabled and system_state == SystemState.automatic:
        with pytest.raises(
            ValueError,
            match="ai_native_enabled requires system_state to be dynamic",
        ):
            _bind_target_runtime_posture(
                "ops",
                rift_enabled=rift_enabled,
                ai_native_enabled=ai_native_enabled,
                system_state=system_state,
            )
        return
    if bind_runtime_posture:
        _bind_target_runtime_posture(
            "ops",
            rift_enabled=rift_enabled,
            ai_native_enabled=ai_native_enabled,
            system_state=system_state,
        )
    else:
        _bind_target_frame_configuration(
            "ops",
            rift_enabled=rift_enabled,
            ai_native_enabled=ai_native_enabled,
            system_state=system_state,
        )

    with pytest.raises(ValueError, match=message):
        nexus._validate_target_frame_runtime_requirements("ops", requested_space_type)


def test_nexus_validate_target_frame_runtime_requirements_accepts_valid_static_frame() -> None:
    nexus = _create_enabled_nexus()
    _bind_target_runtime_posture(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )

    nexus._validate_target_frame_runtime_requirements("ops", RiftSpaceType.static)


def test_nexus_get_required_target_frame_runtime_configuration_prefers_bound_runtime_posture() -> None:
    nexus = _create_enabled_nexus()
    posture = _bind_target_runtime_posture(
        "ops",
        rift_enabled=True,
        ai_native_enabled=True,
        system_state=SystemState.dynamic,
    )
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=False,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )

    bound = nexus._get_required_target_frame_runtime_configuration("ops")
    assert bound is not posture
    assert bound.origin_spellbook_id == "spellbook-alpha"
    assert bound.system_state is SystemState.dynamic
    assert bound.ai_native_enabled is True
    assert bound.rift_enabled is True


def test_nexus_get_required_target_frame_runtime_configuration_falls_back_to_bound_configuration() -> None:
    nexus = _create_enabled_nexus()
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=True,
        system_state=SystemState.dynamic,
    )

    posture = nexus._get_required_target_frame_runtime_configuration("ops")

    assert posture.system_state == SystemState.dynamic
    assert posture.ai_native_enabled is True
    assert posture.rift_enabled is True


def test_nexus_register_frame_acl_profile_replaces_existing_profile_and_cleans_old() -> None:
    nexus = Nexus(aether=Aether())
    first = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_default(),
        codegen_profile=FrameACLCodegenProfile.create_default(),
    )
    second = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_default(),
        codegen_profile=FrameACLCodegenProfile.create_default(),
    )

    nexus.register_frame_acl_profile(first)
    nexus.register_frame_acl_profile(second)

    assert first.cleaned is True
    assert nexus.get_frame_acl_profile("support") is second


def test_nexus_register_named_frame_acl_configuration_rejects_duplicate_named_contract() -> None:
    nexus = Nexus(aether=Aether())
    _seed_descriptor("ops")
    first = FrameACLConfiguration.create_default("ops")
    second = FrameACLConfiguration.create_default("ops")

    nexus.register_named_frame_acl_configuration(
        "ops",
        first,
        contract_name="alt",
    )

    with pytest.raises(ValueError, match="already exists"):
        nexus.register_named_frame_acl_configuration(
            "ops",
            second,
            contract_name="alt",
        )

    assert first.cleaned is False
    assert second.cleaned is False
    registered = nexus.get_named_frame_acl_configuration("ops", "alt")
    assert registered.frame_name == "ops"
    assert registered is not second


def test_nexus_create_frame_projection_sets_respects_named_contract_selection() -> None:
    nexus = Nexus(aether=Aether())
    _seed_descriptor("ops")
    alternate = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string=_build_typed_json_payload(
            "ops",
            view_profile_name="hybrid",
            codegen_profile_name="permissive",
            marker="projection_alt",
        ),
        source_configuration_id=None,
        previous_configuration_id=None,
        reason="projection-alt",
        locked=True,
    )
    nexus.register_named_frame_acl_configuration("ops", alternate, contract_name="alt")

    projection_sets = nexus.create_frame_projection_sets(
        ("ops",),
        contract_names_by_frame_name={"ops": "alt"},
    )

    projection_set = projection_sets["ops"]
    assert projection_set.metadata["selected_contract_names"] == {
        "view": "alt",
        "command": "alt",
        "codegen": "alt",
    }
    assert projection_set.view_projection.frame_acl_configuration.view_configuration.profile_name == "hybrid"
    assert projection_set.codegen_projection.frame_acl_configuration.codegen_configuration.profile_name == "permissive"


@pytest.mark.parametrize(
    ("enabled", "managed_frame", "descriptor_seeded", "acl_only", "expect_removed"),
    [
        (True, True, True, False, True),
        (True, False, True, False, True),
        (True, False, False, True, True),
        (False, False, True, False, True),
    ],
)
def test_nexus_check_for_aetheric_frame_matrix(
        enabled: bool,
        managed_frame: bool,
        descriptor_seeded: bool,
        acl_only: bool,
        expect_removed: bool,
) -> None:
    nexus = Nexus(aether=Aether())
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    if enabled:
        nexus.enable(configuration)
    else:
        nexus._configuration = configuration
        nexus._configured = True
        nexus._enabled = False

    frame_name = "ops"
    if managed_frame:
        frame_name = configuration.get_property("default_nexus_frame_name")
    if descriptor_seeded:
        record = _seed_descriptor(frame_name)
        descriptor = nexus._get_required_frame_descriptor(frame_name)
        assert descriptor.frame_overview is record
    if acl_only or descriptor_seeded:
        nexus._ensure_frame_acl_container(frame_name)
    if managed_frame:
        nexus.frame_manager.create_dynamic_frame(frame_name)

    nexus.check_for_aetheric_frame(frame_name)

    if not expect_removed:
        if descriptor_seeded:
            assert nexus._get_required_frame_descriptor(frame_name).frame_overview is not None
        return

    if descriptor_seeded:
        descriptor = nexus._get_required_frame_descriptor(frame_name)
        assert descriptor.frame_handle is None
        assert descriptor.frame_configuration is None
        assert descriptor.frame_overview is None
    if managed_frame:
        assert nexus.frame_manager.exists(frame_name) is False
    assert frame_name not in nexus._frame_acl_manager.frame_acl_containers_by_name


def test_nexus_check_for_aetheric_frame_is_noop_when_no_state_exists() -> None:
    nexus = _create_enabled_nexus()

    nexus.check_for_aetheric_frame("ops")

    assert "ops" not in nexus._frame_acl_manager.frame_acl_containers_by_name


def test_nexus_repeated_init_with_logger_override_reuses_singleton_and_replaces_logger(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    nexus = Nexus(aether=Aether())
    cleanup_calls = []
    original_logger = nexus._logger
    monkeypatch.setattr(original_logger, "cleanup", lambda: cleanup_calls.append("cleanup"))

    same_nexus = Nexus(logger=logging.getLogger("override"))

    assert same_nexus is nexus
    assert cleanup_calls == ["cleanup"]


def test_nexus_cleanup_cleans_frame_manager_after_live_manager_population() -> None:
    nexus = _create_enabled_nexus()
    manager = nexus._frame_manager
    shared_frame_name = nexus._configuration.get_property("default_nexus_frame_name")
    nexus.frame_manager.create_dynamic_frame(shared_frame_name)

    nexus.cleanup()

    assert manager.cleaned is True
    assert Nexus._instance is None
    assert Nexus._initialized is False


def test_nexus_reset_singleton_for_tests_cleans_live_manager_state() -> None:
    nexus = _create_enabled_nexus()
    manager = nexus._frame_manager
    shared_frame_name = nexus._configuration.get_property("default_nexus_frame_name")
    nexus.frame_manager.create_dynamic_frame(shared_frame_name)

    Nexus._reset_singleton_for_tests()

    assert manager.cleaned is True
    assert Nexus._instance is None
    assert Nexus._initialized is False
