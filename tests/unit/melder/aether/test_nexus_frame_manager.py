from types import SimpleNamespace
from typing import Optional

import pytest

from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.nexus.nexus_frame_manager import NexusFrameManager
from melder.aether.spellbook.configuration.system_state import SystemState


class _FakeConduitCloud:
    def __init__(self, cloud_names=None, cluster_names=None) -> None:
        self._registry = dict(cloud_names or {})
        self._cluster_names = tuple(sorted(cluster_names or ()))

    def list_conduit_names(self):
        return tuple(sorted(self._registry.keys()))

    def list_cloud_names(self):
        return tuple(sorted(self._registry.keys()))

    def list_cluster_names(self):
        return self._cluster_names


class _FakeFrame:
    def __init__(
            self,
            name: str,
            *,
            frame_id: str = "frame-1",
            conduit_ids=None,
            named_conduits=None,
            cloud_names=None,
            cluster_names=None,
    ) -> None:
        self.name = name
        self._id = frame_id
        self.cleaned = False
        self._conduits = dict(conduit_ids or {})
        self._conduit_cloud = _FakeConduitCloud(cloud_names, cluster_names)
        self._conduit_clusters = dict(cluster_names or {})
        self.bound_frame_configuration = None

    def cleanup(self) -> None:
        self.cleaned = True

    def bind_frame_configuration(self, frame_configuration) -> None:
        self.bound_frame_configuration = frame_configuration

    def __enter__(self) -> "_FakeFrame":
        # The real AethericFrame is used as a context manager (frame lock) by
        # NexusFrameManager._publish_frame_overview; the fake mirrors that
        # protocol as a no-op so the publish path can be exercised.
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeConduit:
    def __init__(
            self,
            *,
            conduit_name: str,
            frame_name: str,
            spellbook_id: str = "spellbook-1",
            conduit_id: str = "conduit-1",
    ) -> None:
        self.name = conduit_name
        self.id = conduit_id
        self._id = conduit_id
        self._name = conduit_name
        self._aetheric_frame = frame_name
        self._spellbook = SimpleNamespace(id=spellbook_id, _id=spellbook_id)
        self.cleaned = False

    def cleanup(self) -> None:
        self.cleaned = True


class _FakeDescriptor:
    def __init__(self, frame_name: str) -> None:
        self.frame_name = frame_name
        self.frame_handle = None
        self.frame_configuration = None
        self.frame_overview = None

    def set_frame_handle(self, frame_handle) -> None:
        self.frame_handle = frame_handle

    def set_frame_configuration(self, frame_configuration) -> None:
        self.frame_configuration = frame_configuration

    def set_frame_overview(self, frame_overview) -> None:
        self.frame_overview = frame_overview

    def clear_runtime_publication_state(self) -> None:
        self.frame_handle = None
        self.frame_configuration = None
        self.frame_overview = None


class _FakeFrameDescriptorManager:
    def __init__(self) -> None:
        self.descriptors = {}

    def _has_frame_descriptor(self, frame_name: str) -> bool:
        return frame_name in self.descriptors

    def _get_required_frame_descriptor(self, frame_name: str):
        return self.descriptors[frame_name]

    def _get_or_create_frame_descriptor(self, frame_name: str):
        descriptor = self.descriptors.get(frame_name)
        if descriptor is None:
            descriptor = _FakeDescriptor(frame_name)
            self.descriptors[frame_name] = descriptor
        return descriptor


class _FakeFrameACLManager:
    def __init__(self) -> None:
        self.removed = []

    def _remove_frame_acl_container(self, frame_name: str) -> bool:
        self.removed.append(frame_name)
        return True


class _FakeNexusConfiguration:
    def __init__(self, **properties) -> None:
        self._properties = properties

    def get_property(self, property_name: str):
        value = self._properties[property_name]
        if property_name == "nexus_frame_mode" and isinstance(value, str):
            return NexusFrameMode(value)
        return value


class _FakeAether:
    def __init__(self) -> None:
        self.frames = {}
        self.bound_configurations = {}
        self.bound_frame_configurations = {}
        self.raise_on_bind_configuration = False
        self.raise_on_bind_frame_configuration = False

    def _ensure_frame(self, frame_name: str):
        frame = self.frames.get(frame_name)
        if frame is None:
            frame = _FakeFrame(frame_name, frame_id="frame-{0}".format(frame_name))
            self.frames[frame_name] = frame
        return frame

    def _create_frame(self, frame_name: str):
        if frame_name in self.frames:
            raise ValueError(
                "AethericFrame '{0}' already exists.".format(frame_name)
            )
        frame = _FakeFrame(frame_name, frame_id="frame-{0}".format(frame_name))
        self.frames[frame_name] = frame
        return frame

    def _bind_configuration(self, configuration, frame_name: str) -> None:
        if self.raise_on_bind_configuration:
            raise RuntimeError("bind_configuration_failure")
        self.bound_configurations[frame_name] = configuration

    def _bind_aetheric_frame_configuration(
            self,
            configuration,
            frame_name: str,
    ) -> None:
        if self.raise_on_bind_frame_configuration:
            raise RuntimeError("bind_frame_configuration_failure")
        self.bound_frame_configurations[frame_name] = configuration

    def _get_aetheric_frame_configuration(self, frame_name: str):
        return self.bound_frame_configurations.get(frame_name)


class _FakeRift:
    def __init__(self, rift_id: str) -> None:
        self.id = rift_id


class _FakeNexus:
    def __init__(
            self,
            *,
            nexus_frame_mode: str = "indexed",
            default_nexus_frame_name: str = "aetheric_frame_system",
            max_nexus_frame_count: int = 8,
    ) -> None:
        self._aether = _FakeAether()
        self._configuration = _FakeNexusConfiguration(
            nexus_frame_mode=nexus_frame_mode,
            default_nexus_frame_name=default_nexus_frame_name,
            max_nexus_frame_count=max_nexus_frame_count,
        )
        self._frame_descriptor_manager = _FakeFrameDescriptorManager()
        self._frame_acl_manager = _FakeFrameACLManager()
        self._rifts_by_id = {}
        self.enabled_checked = False
        self.ensured_acl_frames = []

    @property
    def configuration(self):
        return self._configuration

    def _require_activated(self) -> None:
        self.enabled_checked = True

    def _get_required_rift(self, rift_id: str):
        try:
            return self._rifts_by_id[rift_id]
        except KeyError as exc:
            raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

    def list_rift_ids(self):
        return tuple(self._rifts_by_id.keys())

    def _ensure_frame_acl_container(self, frame_name: str) -> None:
        self.ensured_acl_frames.append(frame_name)

    def _remove_frame_acl_container(self, frame_name: str) -> bool:
        return self._frame_acl_manager._remove_frame_acl_container(frame_name)

    def _get_required_frame_descriptor(self, frame_name: str):
        return self._frame_descriptor_manager._get_required_frame_descriptor(
            frame_name
        )

    def _get_or_create_frame_descriptor(self, frame_name: str):
        return self._frame_descriptor_manager._get_or_create_frame_descriptor(
            frame_name
        )


class _PatchableNexusFrameManager(NexusFrameManager):
    pass


def _build_manager(
        *,
        nexus_frame_mode: str = "indexed",
        default_nexus_frame_name: str = "aetheric_frame_system",
        max_nexus_frame_count: int = 8,
):
    nexus = _FakeNexus(
        nexus_frame_mode=nexus_frame_mode,
        default_nexus_frame_name=default_nexus_frame_name,
        max_nexus_frame_count=max_nexus_frame_count,
    )
    manager = _PatchableNexusFrameManager(nexus=nexus)
    return manager, nexus


def _build_configuration(
        frame_name: str = "ops",
        *,
        immutable: bool = False,
        metadata=None,
        root_conduit_name="root",
):
    return NexusFrameConfiguration.create_dynamic_defaults(
        frame_name,
        immutable=immutable,
        metadata=metadata,
        root_conduit_name=root_conduit_name,
    )


def _patch_conjure_root_conduit(
        monkeypatch: pytest.MonkeyPatch,
        manager: NexusFrameManager,
        nexus,
        *,
        conduit_name: Optional[str] = None,
        spellbook_id: str = "spellbook-1",
        failure_message: Optional[str] = None,
) -> None:
    def _conjure(configuration: NexusFrameConfiguration):
        if failure_message is not None:
            raise RuntimeError(failure_message)
        nexus._aether.bound_configurations[configuration.frame_name] = (
            configuration.to_spellbook_configuration()
        )
        nexus._aether.bound_frame_configurations[configuration.frame_name] = (
            configuration.to_aetheric_frame_configuration()
        )
        frame = nexus._aether._ensure_frame(configuration.frame_name)
        conduit = _FakeConduit(
            conduit_name=conduit_name or configuration.root_conduit_name,
            frame_name=configuration.frame_name,
            spellbook_id=spellbook_id,
        )
        frame._conduits[conduit.id] = conduit
        return conduit

    monkeypatch.setattr(
        manager,
        "_conjure_root_conduit_for_configuration",
        _conjure,
    )


def test_nexus_frame_manager_rejects_missing_nexus() -> None:
    with pytest.raises(TypeError, match="nexus cannot be None"):
        NexusFrameManager(nexus=None)


def test_nexus_frame_manager_exists_is_false_for_missing_frame() -> None:
    manager, _ = _build_manager()

    assert manager.exists("ops") is False


def test_nexus_frame_manager_exists_is_true_for_present_frame() -> None:
    manager, _ = _build_manager()
    manager._frames_by_name["ops"] = _FakeFrame("ops")

    assert manager.exists("ops") is True


@pytest.mark.parametrize(
    ("frame_names", "expected"),
    [
        ({}, tuple()),
        ({"b": _FakeFrame("b")}, ("b",)),
        ({"b": _FakeFrame("b"), "a": _FakeFrame("a")}, ("a", "b")),
    ],
)
def test_nexus_frame_manager_list_frame_names_returns_sorted_snapshot(
        frame_names,
        expected,
) -> None:
    manager, _ = _build_manager()
    manager._frames_by_name.update(frame_names)

    assert manager.list_frame_names() == expected


@pytest.mark.parametrize(
    ("immutable", "metadata", "root_conduit_name"),
    [
        (False, None, "root"),
        (True, None, "root"),
        (False, {"team": "ops"}, "root"),
        (False, None, "root"),
        (True, {"team": "ops"}, "root"),
    ],
)
def test_nexus_frame_manager_create_dynamic_frame_forwards_configuration(
        immutable,
        metadata,
        root_conduit_name,
) -> None:
    manager, _ = _build_manager()

    recorded = {}

    def _record(configuration):
        recorded["configuration"] = configuration
        return _FakeFrame("ops")

    manager.create = _record

    result = manager.create_dynamic_frame(
        "ops",
        immutable=immutable,
        metadata=metadata,
        root_conduit_name=root_conduit_name,
    )

    assert result.name == "ops"
    configuration = recorded["configuration"]
    assert configuration.frame_name == "ops"
    assert configuration.immutable is immutable
    assert configuration.metadata == (metadata or {})
    assert configuration.root_conduit_name == root_conduit_name


def test_nexus_frame_manager_create_rejects_non_configuration_inputs() -> None:
    manager, _ = _build_manager()

    with pytest.raises(TypeError, match="NexusFrameConfiguration"):
        manager.create(object())


def test_nexus_frame_manager_create_rejects_duplicate_frame_name() -> None:
    manager, _ = _build_manager()
    manager._frames_by_name["ops"] = _FakeFrame("ops")

    with pytest.raises(ValueError, match="already exists"):
        manager.create(_build_configuration("ops"))


@pytest.mark.parametrize(
    ("system_state", "ai_native_enabled", "rift_enabled", "message"),
    [
        (SystemState.automatic, True, True, "system_state=SystemState.dynamic"),
        (SystemState.dynamic, False, True, "ai_native_enabled=True"),
        (SystemState.dynamic, True, False, "rift_enabled=True"),
    ],
)
def test_nexus_frame_manager_validate_configuration_contract_rejects_invalid_posture(
        system_state,
        ai_native_enabled,
        rift_enabled,
        message,
) -> None:
    class _Configuration:
        def __init__(self) -> None:
            self.system_state = system_state
            self.ai_native_enabled = ai_native_enabled
            self.rift_enabled = rift_enabled

    with pytest.raises(ValueError, match=message):
        NexusFrameManager._validate_configuration_contract(_Configuration())


def test_nexus_frame_manager_create_publishes_descriptor_and_acl_state(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, nexus = _build_manager()
    _patch_conjure_root_conduit(monkeypatch, manager, nexus)

    conduit = manager.create(_build_configuration("ops"))
    descriptor = nexus._frame_descriptor_manager._get_required_frame_descriptor("ops")

    assert conduit.name == "root"
    assert nexus._aether.bound_configurations["ops"]._aether_frame == "ops"
    assert nexus._aether.bound_frame_configurations["ops"].system_state == SystemState.dynamic
    assert descriptor.frame_handle.name == "ops"
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_overview.frame_name == "ops"
    assert descriptor.frame_overview.payload.root_conduit_count == 1
    assert nexus.ensured_acl_frames == ["ops"]


def test_nexus_frame_manager_create_allows_raw_single_shared_frame_name(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode="single")
    _patch_conjure_root_conduit(monkeypatch, manager, nexus)

    conduit = manager.create(_build_configuration("aetheric_frame_system"))

    assert conduit.name == "root"
    assert nexus._frame_descriptor_manager._get_required_frame_descriptor(
        "aetheric_frame_system"
    ).frame_overview is not None


def test_nexus_frame_manager_create_rejects_raw_single_non_shared_frame_name(
) -> None:
    manager, _ = _build_manager(nexus_frame_mode="single")

    with pytest.raises(ValueError, match="only allows raw creation of the shared frame"):
        manager.create(_build_configuration("ops"))


def test_nexus_frame_manager_create_rejects_raw_one_per_workspace_creation(
) -> None:
    manager, _ = _build_manager(nexus_frame_mode="one_per_workspace")

    with pytest.raises(ValueError, match="Raw NexusFrameManager creation is not allowed"):
        manager.create(_build_configuration("ops"))


def test_nexus_frame_manager_create_uses_rooted_spellbook_conjure(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, _ = _build_manager()
    calls = []

    monkeypatch.setattr(
        manager,
        "_conjure_root_conduit_for_configuration",
        lambda configuration: calls.append(
            (configuration.frame_name, configuration.root_conduit_name)
        ) or _FakeConduit(
            conduit_name=configuration.root_conduit_name,
            frame_name=configuration.frame_name,
        ),
    )
    monkeypatch.setattr(
        manager,
        "_ensure_descriptor_and_acl",
        lambda frame_name: None,
    )
    monkeypatch.setattr(
        manager,
        "_publish_frame_overview",
        lambda frame_name, config_origin_spellbook_id=None: None,
    )

    manager.create(_build_configuration("ops", root_conduit_name="root"))

    assert calls == [("ops", "root")]


@pytest.mark.parametrize(
    "failure_step",
    [
        "conjure_root_conduit",
        "ensure_descriptor_and_acl",
        "publish_frame_overview",
    ],
)
def test_nexus_frame_manager_create_rolls_back_registry_on_failure(
        monkeypatch: pytest.MonkeyPatch,
        failure_step: str,
) -> None:
    manager, nexus = _build_manager()
    configuration = _build_configuration("ops", root_conduit_name="root")

    if failure_step == "conjure_root_conduit":
        _patch_conjure_root_conduit(
            monkeypatch,
            manager,
            nexus,
            failure_message="conjure_failure",
        )
    elif failure_step == "ensure_descriptor_and_acl":
        _patch_conjure_root_conduit(monkeypatch, manager, nexus)
        monkeypatch.setattr(
            manager,
            "_ensure_descriptor_and_acl",
            lambda frame_name: (_ for _ in ()).throw(RuntimeError("descriptor_failure")),
        )
    elif failure_step == "publish_frame_overview":
        _patch_conjure_root_conduit(monkeypatch, manager, nexus)
        monkeypatch.setattr(
            manager,
            "_publish_frame_overview",
            lambda frame_name, config_origin_spellbook_id=None: (_ for _ in ()).throw(
                RuntimeError("overview_failure")
            ),
        )
    else:
        _patch_conjure_root_conduit(monkeypatch, manager, nexus)

    with pytest.raises(RuntimeError):
        manager.create(configuration)

    assert manager.exists("ops") is False
    assert "ops" not in manager._configurations_by_frame_name
    if "ops" in nexus._aether.frames:
        assert nexus._aether.frames["ops"].cleaned is True


def test_nexus_frame_manager_remove_rejects_missing_frame() -> None:
    manager, _ = _build_manager()

    with pytest.raises(ValueError, match="was not found"):
        manager.remove("ops")


def test_nexus_frame_manager_remove_rejects_immutable_frame() -> None:
    manager, _ = _build_manager()
    manager._frames_by_name["ops"] = _FakeFrame("ops")
    manager._configurations_by_frame_name["ops"] = _build_configuration(
        "ops",
        immutable=True,
    )

    with pytest.raises(ValueError, match="is immutable"):
        manager.remove("ops")


def test_nexus_frame_manager_remove_rejects_active_frame(monkeypatch) -> None:
    manager, _ = _build_manager()
    manager._frames_by_name["ops"] = _FakeFrame("ops")
    manager._configurations_by_frame_name["ops"] = _build_configuration("ops")
    monkeypatch.setattr(manager, "_frame_is_in_active_rift_use", lambda frame_name: True)

    with pytest.raises(ValueError, match="still in active Rift use"):
        manager.remove("ops")


def test_nexus_frame_manager_remove_cleans_frame_when_allowed(monkeypatch) -> None:
    manager, _ = _build_manager()
    frame = _FakeFrame("ops")
    manager._frames_by_name["ops"] = frame
    manager._configurations_by_frame_name["ops"] = _build_configuration("ops")
    monkeypatch.setattr(manager, "_frame_is_in_active_rift_use", lambda frame_name: False)

    manager.remove("ops")

    assert frame.cleaned is True


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "existing_frame_name"),
    [
        ("single", None, "aetheric_frame_system"),
        ("single", "aetheric_frame_system", "aetheric_frame_system"),
        ("one_per_workspace", None, "aetheric_frame_system:rift-1"),
        ("one_per_workspace", "aetheric_frame_system:rift-1", "aetheric_frame_system:rift-1"),
        ("indexed", "ops", "ops"),
    ],
)
def test_nexus_frame_manager_get_frame_for_rift_returns_expected_frame(
        nexus_frame_mode: str,
        frame_name: str,
        existing_frame_name: str,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")
    frame = _FakeFrame(existing_frame_name)
    manager._frames_by_name[existing_frame_name] = frame

    assert manager.get_frame_for_rift("rift-1", frame_name=frame_name) is frame


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "message"),
    [
        ("single", "other", "Shared Nexus mode only exposes the shared frame"),
        ("one_per_workspace", "other", "own private Nexus frame"),
        ("indexed", None, "explicit frame_name"),
    ],
)
def test_nexus_frame_manager_get_frame_for_rift_rejects_invalid_lookup(
        nexus_frame_mode: str,
        frame_name: str,
        message: str,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")

    with pytest.raises(ValueError, match=message):
        manager.get_frame_for_rift("rift-1", frame_name=frame_name)


def test_nexus_frame_manager_get_frame_for_rift_rejects_missing_frame() -> None:
    manager, nexus = _build_manager(nexus_frame_mode="single")
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")

    with pytest.raises(ValueError, match="was not found"):
        manager.get_frame_for_rift("rift-1")


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "existing", "expected"),
    [
        ("single", None, False, "aetheric_frame_system"),
        ("single", None, True, "aetheric_frame_system"),
        ("indexed", "ops", False, "ops"),
        ("indexed", "ops", True, "ops"),
        ("one_per_workspace", None, False, "aetheric_frame_system:rift-1"),
        ("one_per_workspace", None, True, "aetheric_frame_system:rift-1"),
    ],
)
def test_nexus_frame_manager_create_frame_for_rift_matrix(
        nexus_frame_mode: str,
        frame_name: str,
        existing: bool,
        expected: str,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")
    if existing:
        existing_frame = _FakeFrame(expected)
        nexus._aether.frames[expected] = existing_frame
        manager._frames_by_name[expected] = existing_frame
        existing_conduit = _FakeConduit(conduit_name="root", frame_name=expected)
        existing_frame._conduits[existing_conduit.id] = existing_conduit
        with pytest.raises(ValueError, match="already exists"):
            manager.create_frame_for_rift("rift-1", frame_name=frame_name)
        return

    created = _FakeConduit(conduit_name="root", frame_name=expected)
    monkeypatch.setattr(
        manager,
        "_create_configuration",
        lambda configuration, validate_raw_mode: created,
    )

    result = manager.create_frame_for_rift("rift-1", frame_name=frame_name)

    assert result is created


def test_nexus_frame_manager_create_frame_for_rift_rejects_immutable_private_frame() -> None:
    manager, nexus = _build_manager(nexus_frame_mode="one_per_workspace")
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")

    with pytest.raises(ValueError, match="cannot be immutable"):
        manager.create_frame_for_rift("rift-1", immutable=True)


def test_nexus_frame_manager_create_frame_for_rift_allocates_indexed_frame_name() -> None:
    manager, nexus = _build_manager(nexus_frame_mode="indexed")
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")
    created = _FakeConduit(
        conduit_name="root",
        frame_name="aetheric_frame_system-1",
    )
    recorded = {}

    def _create_configuration(configuration, validate_raw_mode):
        recorded["frame_name"] = configuration.frame_name
        return created

    manager._create_configuration = _create_configuration

    result = manager.create_frame_for_rift("rift-1")

    assert result is created
    assert recorded["frame_name"] == "aetheric_frame_system-1"


def test_nexus_frame_manager_get_required_root_conduit_for_frame_rejects_missing_manager_frame(
) -> None:
    manager, _ = _build_manager()

    with pytest.raises(ValueError, match="was not found"):
        manager._get_required_root_conduit_for_frame("ops")


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frames", "expected"),
    [
        ("single", {}, tuple()),
        ("single", {"aetheric_frame_system": _FakeFrame("aetheric_frame_system")}, ("aetheric_frame_system",)),
        ("one_per_workspace", {}, tuple()),
        ("one_per_workspace", {"aetheric_frame_system:rift-1": _FakeFrame("aetheric_frame_system:rift-1")}, ("aetheric_frame_system:rift-1",)),
        ("indexed", {}, tuple()),
        ("indexed", {"b": _FakeFrame("b"), "a": _FakeFrame("a")}, ("a", "b")),
    ],
)
def test_nexus_frame_manager_list_accessible_frame_names_for_rift_matrix(
        nexus_frame_mode: str,
        frames,
        expected,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")
    manager._frames_by_name.update(frames)

    assert manager.list_accessible_frame_names_for_rift("rift-1") == expected


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frames", "immutable", "rift_count", "expected"),
    [
        ("single", {}, False, 0, tuple()),
        ("single", {"aetheric_frame_system": _FakeFrame("aetheric_frame_system")}, False, 0, ("aetheric_frame_system",)),
        ("single", {"aetheric_frame_system": _FakeFrame("aetheric_frame_system")}, True, 0, tuple()),
        ("single", {"aetheric_frame_system": _FakeFrame("aetheric_frame_system")}, False, 1, tuple()),
        ("one_per_workspace", {}, False, 0, tuple()),
        ("one_per_workspace", {"aetheric_frame_system:rift-1": _FakeFrame("aetheric_frame_system:rift-1")}, False, 0, ("aetheric_frame_system:rift-1",)),
        ("one_per_workspace", {"aetheric_frame_system:rift-1": _FakeFrame("aetheric_frame_system:rift-1")}, True, 0, tuple()),
        ("indexed", {"ops": _FakeFrame("ops")}, False, 0, tuple()),
    ],
)
def test_nexus_frame_manager_get_frame_names_to_cleanup_for_removed_rift_matrix(
        nexus_frame_mode: str,
        frames,
        immutable: bool,
        rift_count: int,
        expected,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    manager._frames_by_name.update(frames)
    for frame_name in frames:
        manager._configurations_by_frame_name[frame_name] = _build_configuration(
            frame_name,
            immutable=immutable,
        )
    nexus._rifts_by_id = {
        "rift-{0}".format(index): _FakeRift("rift-{0}".format(index))
        for index in range(rift_count)
    }

    assert manager.get_frame_names_to_cleanup_for_removed_rift("rift-1") == expected


def test_nexus_frame_manager_handle_aether_frame_disposal_returns_false_when_untracked() -> None:
    manager, _ = _build_manager()

    assert manager.handle_aether_frame_disposal("ops") is False


@pytest.mark.parametrize(
    ("frame_present", "configuration_present"),
    [
        (True, True),
        (True, False),
        (False, True),
    ],
)
def test_nexus_frame_manager_handle_aether_frame_disposal_cleans_state(
        frame_present: bool,
        configuration_present: bool,
) -> None:
    manager, nexus = _build_manager()
    if frame_present:
        manager._frames_by_name["ops"] = _FakeFrame("ops")
    if configuration_present:
        manager._configurations_by_frame_name["ops"] = _build_configuration("ops")
    descriptor = nexus._frame_descriptor_manager._get_or_create_frame_descriptor("ops")
    descriptor.frame_handle = object()
    descriptor.frame_configuration = object()
    descriptor.frame_overview = object()

    handled = manager.handle_aether_frame_disposal("ops")

    assert handled is True
    assert descriptor.frame_handle is None
    assert descriptor.frame_configuration is None
    assert descriptor.frame_overview is None
    assert nexus._frame_acl_manager.removed == ["ops"]


def test_nexus_frame_manager_determine_frame_name_for_rift_uses_default_name() -> None:
    manager, _ = _build_manager(default_nexus_frame_name="frame")

    assert manager._determine_frame_name_for_rift("rift-1") == "frame:rift-1"


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "allow_creation", "expected"),
    [
        ("single", None, False, "aetheric_frame_system"),
        ("single", "aetheric_frame_system", False, "aetheric_frame_system"),
        ("one_per_workspace", None, False, "aetheric_frame_system:rift-1"),
        ("one_per_workspace", "aetheric_frame_system:rift-1", False, "aetheric_frame_system:rift-1"),
        ("indexed", "ops", False, "ops"),
        ("indexed", None, True, "aetheric_frame_system-1"),
    ],
)
def test_nexus_frame_manager_resolve_frame_name_for_rift_matrix(
        nexus_frame_mode: str,
        frame_name: str,
        allow_creation: bool,
        expected: str,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")

    assert manager._resolve_frame_name_for_rift(
        "rift-1",
        frame_name=frame_name,
        allow_creation=allow_creation,
    ) == expected


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "allow_creation", "message"),
    [
        ("single", "other", False, "Shared Nexus mode only exposes the shared frame"),
        ("one_per_workspace", "other", False, "own private Nexus frame"),
        ("indexed", None, False, "explicit frame_name"),
    ],
)
def test_nexus_frame_manager_resolve_frame_name_for_rift_rejects_invalid_inputs(
        nexus_frame_mode: str,
        frame_name: str,
        allow_creation: bool,
        message: str,
) -> None:
    manager, nexus = _build_manager(nexus_frame_mode=nexus_frame_mode)
    nexus._rifts_by_id["rift-1"] = _FakeRift("rift-1")

    with pytest.raises(ValueError, match=message):
        manager._resolve_frame_name_for_rift(
            "rift-1",
            frame_name=frame_name,
            allow_creation=allow_creation,
        )


def test_nexus_frame_manager_allocate_indexed_frame_name_increments_counter() -> None:
    manager, _ = _build_manager(default_nexus_frame_name="frame")

    assert manager._allocate_indexed_frame_name() == "frame-1"
    assert manager._allocate_indexed_frame_name() == "frame-2"


@pytest.mark.parametrize(
    ("existing_frames", "candidate_frame_names", "max_nexus_frame_count", "raises"),
    [
        ({}, ("ops",), 1, False),
        ({"ops": _FakeFrame("ops")}, ("ops",), 1, False),
        ({}, ("ops", "ops"), 1, False),
        ({}, ("ops", "finance"), 2, False),
        ({}, ("ops", "finance"), 1, True),
        ({"ops": _FakeFrame("ops")}, ("finance",), 1, True),
    ],
)
def test_nexus_frame_manager_validate_frame_budget_matrix(
        existing_frames,
        candidate_frame_names,
        max_nexus_frame_count: int,
        raises: bool,
) -> None:
    manager, _ = _build_manager(max_nexus_frame_count=max_nexus_frame_count)
    manager._frames_by_name.update(existing_frames)

    if raises:
        with pytest.raises(ValueError, match="frame cap has been reached"):
            manager._validate_frame_budget(candidate_frame_names)
        return

    manager._validate_frame_budget(candidate_frame_names)


def test_nexus_frame_manager_validate_frame_budget_counts_inflight_reservations() -> None:
    """
    In-flight reservations consume the Nexus frame budget (BUG-051 regression).

    A concurrent create records its frame name in ``_creating_frame_names`` under
    ``_lock`` before it publishes into ``_frames_by_name``. ``_validate_frame_budget``
    must count those reservations, otherwise a second create validated during that
    window observes only published frames and slips past ``max_nexus_frame_count``.
    With a cap of one and one name already reserved, a new candidate must be refused.
    """
    manager, _ = _build_manager(max_nexus_frame_count=1)
    manager._creating_frame_names.add("frame_a")

    with pytest.raises(ValueError, match="frame cap has been reached"):
        manager._validate_frame_budget(("frame_b",))

    # A revalidation of the already-reserved name is not double-counted: it is
    # excluded from the candidate set, so the single reservation stays within cap.
    manager._validate_frame_budget(("frame_a",))


def test_nexus_frame_manager_bootstrap_root_conduit_binds_and_refreshes_overview(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, nexus = _build_manager()
    calls = []

    class _FakeSpellbook:
        def __init__(self, aetheric_frame: str, configuration) -> None:
            calls.append(("init", aetheric_frame, configuration))
            self.id = "spellbook-1"
            self.aetheric_frame = aetheric_frame
            self.configuration = configuration

        def conjure(self, name: str, dynamic: bool):
            calls.append(("conjure", name, dynamic))
            nexus._aether.bound_configurations["ops"] = self.configuration
            nexus._aether.bound_frame_configurations["ops"] = (
                _build_configuration("ops").to_aetheric_frame_configuration()
            )
            nexus._aether._ensure_frame("ops")
            return _FakeConduit(
                conduit_name=name,
                frame_name="ops",
                spellbook_id=self.id,
            )

    monkeypatch.setattr(
        "melder.aether.spellbook.spellbook.Spellbook",
        _FakeSpellbook,
    )

    conduit = manager._conjure_root_conduit_for_configuration(
        _build_configuration("ops", root_conduit_name="root")
    )

    assert conduit.name == "root"
    assert calls[0][0] == "init"
    assert calls[1] == ("conjure", "root", True)


@pytest.mark.parametrize(
    ("accessible_names", "expected"),
    [
        (("ops",), True),
        (("finance",), False),
        (tuple(), False),
    ],
)
def test_nexus_frame_manager_frame_is_in_active_rift_use_matrix(
        accessible_names,
        expected: bool,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, nexus = _build_manager()
    nexus._rifts_by_id = {
        "rift-1": _FakeRift("rift-1"),
    }
    monkeypatch.setattr(
        manager,
        "list_accessible_frame_names_for_rift",
        lambda rift_id: accessible_names,
    )

    assert manager._frame_is_in_active_rift_use("ops") is expected


def test_nexus_frame_manager_frame_is_in_active_rift_use_ignores_access_errors(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager, nexus = _build_manager()
    nexus._rifts_by_id = {
        "rift-1": _FakeRift("rift-1"),
    }

    def _raise(_rift_id):
        # A rift that vanished between the registry snapshot and the
        # accessibility check surfaces as ValueError, which
        # _frame_is_in_active_rift_use deliberately skips (a vanished rift
        # cannot hold the frame in active use). Non-ValueError errors must
        # propagate, so they are intentionally not exercised here.
        raise ValueError("access failure")

    monkeypatch.setattr(manager, "list_accessible_frame_names_for_rift", _raise)

    assert manager._frame_is_in_active_rift_use("ops") is False
