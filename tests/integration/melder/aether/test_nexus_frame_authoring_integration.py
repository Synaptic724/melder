import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.spellbook import Spellbook


def _reset_runtime_singletons() -> None:
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def _isolated_runtime() -> None:
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _create_enabled_nexus(
        *,
        nexus_frame_mode: str = "indexed",
        max_nexus_frame_count: int = 8,
) -> Nexus:
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode(nexus_frame_mode)
    if nexus_frame_mode == "single":
        max_nexus_frame_count = 1
    configuration.with_max_nexus_frame_count(max_nexus_frame_count)
    nexus.enable(configuration)
    return nexus


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "expected_name"),
    [
        ("single", None, "aetheric_frame_system"),
        ("single", "aetheric_frame_system", "aetheric_frame_system"),
        ("indexed", None, "aetheric_frame_system-1"),
        ("indexed", "ops", "ops"),
        ("indexed", "finance", "finance"),
        ("one_per_workspace", None, None),
        ("one_per_workspace", None, None),
        ("indexed", None, "aetheric_frame_system-1"),
    ],
)
def test_integration_rift_create_nexus_frame_matrix(
        nexus_frame_mode: str,
        frame_name,
        expected_name,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    rift = nexus.create_rift(rift_name="alpha")

    frame = rift.create_nexus_frame(frame_name=frame_name)
    descriptor = nexus._get_required_frame_descriptor(frame.name)

    if nexus_frame_mode == "one_per_workspace":
        assert frame.name == "aetheric_frame_system:{0}".format(rift.id)
    else:
        assert frame.name == expected_name
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_configuration.ai_native_enabled is True
    assert descriptor.frame_configuration.rift_enabled is True


@pytest.mark.parametrize(
    ("nexus_frame_mode", "create_kind"),
    [
        ("single", "shared"),
        ("single", "shared_second"),
        ("indexed", "explicit"),
        ("indexed", "explicit_second"),
        ("indexed", "auto"),
        ("one_per_workspace", "private"),
        ("one_per_workspace", "private_second"),
        ("one_per_workspace", "private_repeat"),
    ],
)
def test_integration_rift_get_nexus_frame_matrix(
        nexus_frame_mode: str,
        create_kind: str,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if create_kind == "shared":
        created = first.create_nexus_frame()
        assert first.get_nexus_frame() is created
        return
    if create_kind == "shared_second":
        created = first.create_nexus_frame()
        assert second.get_nexus_frame() is created
        return
    if create_kind == "explicit":
        created = first.create_nexus_frame(frame_name="ops")
        assert first.get_nexus_frame("ops") is created
        return
    if create_kind == "explicit_second":
        created = first.create_nexus_frame(frame_name="ops")
        assert second.get_nexus_frame("ops") is created
        return
    if create_kind == "auto":
        created = first.create_nexus_frame()
        assert first.get_nexus_frame(created.name) is created
        return
    if create_kind == "private":
        created = first.create_nexus_frame()
        assert first.get_nexus_frame() is created
        return
    if create_kind == "private_second":
        created = second.create_nexus_frame()
        assert second.get_nexus_frame() is created
        return

    created = first.create_nexus_frame()
    assert first.get_nexus_frame() is created


@pytest.mark.parametrize(
    ("nexus_frame_mode", "create_kind", "expected_names"),
    [
        ("single", "none", tuple()),
        ("single", "shared", ("aetheric_frame_system",)),
        ("indexed", "none", tuple()),
        ("indexed", "one_named", ("ops",)),
        ("indexed", "two_named", ("finance", "ops")),
        ("indexed", "auto", ("aetheric_frame_system-1",)),
        ("one_per_workspace", "none", tuple()),
        ("one_per_workspace", "one_private", None),
    ],
)
def test_integration_rift_list_accessible_nexus_frame_names_matrix(
        nexus_frame_mode: str,
        create_kind: str,
        expected_names,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if create_kind == "shared":
        first.create_nexus_frame()
    elif create_kind == "one_named":
        first.create_nexus_frame(frame_name="ops")
    elif create_kind == "two_named":
        first.create_nexus_frame(frame_name="ops")
        second.create_nexus_frame(frame_name="finance")
    elif create_kind == "auto":
        first.create_nexus_frame()
    elif create_kind == "one_private":
        first.create_nexus_frame()

    names = first.list_accessible_nexus_frame_names()

    if nexus_frame_mode == "one_per_workspace" and create_kind == "one_private":
        assert names == ("aetheric_frame_system:{0}".format(first.id),)
        return
    assert names == expected_names


@pytest.mark.parametrize(
    ("immutable", "metadata", "root_conduit_name"),
    [
        (False, None, None),
        (True, None, None),
        (False, {"team": "ops"}, None),
        (False, None, "root"),
        (True, {"team": "ops"}, None),
        (True, {"team": "ops"}, "root"),
    ],
)
def test_integration_nexus_frame_manager_direct_create_matrix(
        immutable,
        metadata,
        root_conduit_name,
) -> None:
    nexus = _create_enabled_nexus()

    frame = nexus.frame_manager.create_dynamic_frame(
        "ops",
        immutable=immutable,
        metadata=metadata,
        root_conduit_name=root_conduit_name,
    )
    descriptor = nexus._get_required_frame_descriptor("ops")

    assert frame.name == "ops"
    assert nexus.frame_manager.exists("ops") is True
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_configuration.ai_native_enabled is True
    assert descriptor.frame_configuration.rift_enabled is True
    if root_conduit_name is None:
        assert descriptor.frame_overview.payload.root_conduit_count == 0
    else:
        assert descriptor.frame_overview.payload.root_conduit_count == 1


@pytest.mark.parametrize(
    ("cleanup_kind", "nexus_frame_mode"),
    [
        ("external", "single"),
        ("external", "indexed"),
        ("external", "one_per_workspace"),
        ("remove_rift", "single"),
        ("remove_rift", "indexed"),
        ("remove_rift", "one_per_workspace"),
    ],
)
def test_integration_nexus_frame_cleanup_matrix(
        cleanup_kind: str,
        nexus_frame_mode: str,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    rift = nexus.create_rift(rift_name="alpha")
    if nexus_frame_mode == "indexed":
        frame = rift.create_nexus_frame(frame_name="ops")
    else:
        frame = rift.create_nexus_frame()

    assert nexus.frame_manager.exists(frame.name) is True

    if cleanup_kind == "external":
        frame.cleanup()
        assert nexus.frame_manager.exists(frame.name) is False
        return

    nexus.remove_rift(rift.id)
    if nexus_frame_mode == "indexed":
        assert nexus.frame_manager.exists(frame.name) is True
    else:
        assert nexus.frame_manager.exists(frame.name) is False


@pytest.mark.parametrize(
    ("nexus_frame_mode", "action", "message"),
    [
        ("single", "wrong_name", "Shared Nexus mode only exposes the shared frame"),
        ("one_per_workspace", "foreign_access", "private Nexus frame"),
        ("one_per_workspace", "immutable_private", "cannot be immutable"),
        ("indexed", "missing_lookup_name", "explicit frame_name"),
        ("indexed", "duplicate_create", "already exists"),
        ("indexed", "invalid_configuration", "system_state=SystemState.dynamic"),
    ],
)
def test_integration_nexus_frame_rejection_matrix(
        nexus_frame_mode: str,
        action: str,
        message: str,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if action == "wrong_name":
        with pytest.raises(ValueError, match=message):
            first.create_nexus_frame(frame_name="other")
        return
    if action == "foreign_access":
        frame = second.create_nexus_frame()
        with pytest.raises(ValueError, match=message):
            nexus.get_nexus_frame_for_rift(first.id, frame_name=frame.name)
        return
    if action == "immutable_private":
        with pytest.raises(ValueError, match=message):
            first.create_nexus_frame(immutable=True)
        return
    if action == "missing_lookup_name":
        with pytest.raises(ValueError, match=message):
            first.get_nexus_frame()
        return
    if action == "duplicate_create":
        nexus.frame_manager.create_dynamic_frame("ops")
        with pytest.raises(ValueError, match=message):
            nexus.frame_manager.create_dynamic_frame("ops")
        return

    with pytest.raises(ValueError, match=message):
        nexus.frame_manager.create(
            NexusFrameConfiguration(
                frame_name="ops",
                system_state=SystemState.automatic,
                ai_native_enabled=False,
                rift_enabled=True,
            )
        )
