import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.nexus.nexus import Nexus
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spellbook import Spellbook


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


def _expected_frame_name(
        nexus_frame_mode: str,
        rift,
        frame_name: str = None,
) -> str:
    if nexus_frame_mode == "single":
        return "aetheric_frame_system"
    if nexus_frame_mode == "one_per_workspace":
        return "aetheric_frame_system:{0}".format(rift.id)
    if frame_name is not None:
        return frame_name
    return "aetheric_frame_system-1"


@pytest.mark.parametrize(
    ("immutable", "metadata", "root_conduit_name"),
    [
        (False, None, "root"),
        (True, None, "root"),
        (False, {"team": "ops"}, "root"),
        (True, {"team": "ops"}, "root"),
    ],
)
def test_component_nexus_frame_manager_create_dynamic_frame_matrix(
        immutable,
        metadata,
        root_conduit_name,
) -> None:
    nexus = _create_enabled_nexus()

    conduit = nexus.frame_manager.create_dynamic_frame(
        "ops",
        immutable=immutable,
        metadata=metadata,
        root_conduit_name=root_conduit_name,
    )
    descriptor = nexus._get_required_frame_descriptor("ops")

    assert conduit.name == root_conduit_name
    assert conduit._aetheric_frame == "ops"
    assert nexus.frame_manager.exists("ops") is True
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_configuration.ai_native_enabled is True
    assert descriptor.frame_configuration.rift_enabled is True
    assert descriptor.frame_overview.payload.root_conduit_count == 1


def test_component_nexus_frame_manager_create_dynamic_frame_allows_single_shared_name(
) -> None:
    nexus = _create_enabled_nexus(nexus_frame_mode="single")

    conduit = nexus.frame_manager.create_dynamic_frame("aetheric_frame_system")

    assert conduit.name == "root"
    assert conduit._aetheric_frame == "aetheric_frame_system"
    assert nexus.frame_manager.exists("aetheric_frame_system") is True


def test_component_nexus_frame_manager_create_dynamic_frame_rejects_single_non_shared_name(
) -> None:
    nexus = _create_enabled_nexus(nexus_frame_mode="single")

    with pytest.raises(ValueError, match="only allows raw creation of the shared frame"):
        nexus.frame_manager.create_dynamic_frame("ops")


def test_component_nexus_frame_manager_create_dynamic_frame_rejects_one_per_workspace(
) -> None:
    nexus = _create_enabled_nexus(nexus_frame_mode="one_per_workspace")

    with pytest.raises(ValueError, match="Raw NexusFrameManager creation is not allowed"):
        nexus.frame_manager.create_dynamic_frame("ops")


@pytest.mark.parametrize("frame_name", ["ops", "finance"])
def test_component_nexus_frame_manager_rejects_duplicate_dynamic_frame(
        frame_name: str,
) -> None:
    nexus = _create_enabled_nexus()
    nexus.frame_manager.create_dynamic_frame(frame_name)

    with pytest.raises(ValueError, match="already exists"):
        nexus.frame_manager.create_dynamic_frame(frame_name)


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "expected_name"),
    [
        ("single", None, "aetheric_frame_system"),
        ("single", "aetheric_frame_system", "aetheric_frame_system"),
        ("indexed", "ops", "ops"),
        ("indexed", "finance", "finance"),
        ("one_per_workspace", None, None),
        ("one_per_workspace", None, None),
    ],
)
def test_component_rift_create_nexus_frame_matrix(
        nexus_frame_mode: str,
        frame_name,
        expected_name,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    rift = nexus.create_rift(rift_name="alpha")

    conduit = rift.create_nexus_frame(frame_name=frame_name)
    expected_frame_name = _expected_frame_name(
        nexus_frame_mode,
        rift,
        frame_name=frame_name,
    )

    assert conduit.name == "root"
    assert conduit._aetheric_frame == expected_frame_name
    descriptor = nexus._get_required_frame_descriptor(expected_frame_name)
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_configuration.ai_native_enabled is True
    assert descriptor.frame_configuration.rift_enabled is True


@pytest.mark.parametrize(
    ("nexus_frame_mode", "setup_kind"),
    [
        ("single", "shared"),
        ("indexed", "explicit"),
        ("indexed", "explicit_second"),
        ("one_per_workspace", "private"),
        ("one_per_workspace", "private_second"),
        ("single", "shared_second"),
    ],
)
def test_component_rift_get_nexus_frame_lookup_matrix(
        nexus_frame_mode: str,
        setup_kind: str,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if setup_kind == "shared":
        created = first.create_nexus_frame()
        looked_up = first.get_nexus_frame()
        assert looked_up is created
        return
    if setup_kind == "shared_second":
        created = first.create_nexus_frame()
        looked_up = second.get_nexus_frame()
        assert looked_up is created
        return
    if setup_kind == "explicit":
        created = first.create_nexus_frame(frame_name="ops")
        looked_up = first.get_nexus_frame("ops")
        assert looked_up is created
        return
    if setup_kind == "explicit_second":
        created = first.create_nexus_frame(frame_name="ops")
        looked_up = second.get_nexus_frame("ops")
        assert looked_up is created
        return
    if setup_kind == "private":
        created = first.create_nexus_frame()
        looked_up = first.get_nexus_frame()
        assert looked_up is created
        return

    created = second.create_nexus_frame()
    looked_up = second.get_nexus_frame()
    assert looked_up is created


@pytest.mark.parametrize(
    ("nexus_frame_mode", "create_kind", "expected_count"),
    [
        ("single", "none", 0),
        ("single", "shared", 1),
        ("indexed", "none", 0),
        ("indexed", "one", 1),
        ("indexed", "two", 2),
        ("one_per_workspace", "none", 0),
        ("one_per_workspace", "one", 1),
        ("one_per_workspace", "two", 1),
    ],
)
def test_component_rift_list_accessible_nexus_frame_names_matrix(
        nexus_frame_mode: str,
        create_kind: str,
        expected_count: int,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if create_kind == "shared":
        first.create_nexus_frame()
    elif create_kind == "one":
        if nexus_frame_mode == "indexed":
            first.create_nexus_frame(frame_name="ops")
        else:
            first.create_nexus_frame()
    elif create_kind == "two":
        if nexus_frame_mode == "indexed":
            first.create_nexus_frame(frame_name="ops")
            second.create_nexus_frame(frame_name="finance")
        else:
            first.create_nexus_frame()
            second.create_nexus_frame()

    names = first.list_accessible_nexus_frame_names()

    assert len(names) == expected_count


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name"),
    [
        ("single", "aetheric_frame_system"),
        ("indexed", "ops"),
        ("indexed", "finance"),
        ("indexed", "ops_beta"),
        ("one_per_workspace", None),
        ("one_per_workspace", None),
    ],
)
def test_component_external_frame_cleanup_clears_manager_state_matrix(
        nexus_frame_mode: str,
        frame_name,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    rift = nexus.create_rift(rift_name="alpha")
    if nexus_frame_mode == "single":
        conduit = rift.create_nexus_frame()
        managed_frame_name = conduit._aetheric_frame
    elif nexus_frame_mode == "indexed":
        conduit = rift.create_nexus_frame(frame_name=frame_name)
        managed_frame_name = conduit._aetheric_frame
    else:
        conduit = rift.create_nexus_frame()
        managed_frame_name = conduit._aetheric_frame

    assert nexus.frame_manager.exists(managed_frame_name) is True

    conduit.cleanup()

    assert nexus.frame_manager.exists(managed_frame_name) is True

    nexus._aether._ensure_frame(managed_frame_name).cleanup()

    assert nexus.frame_manager.exists(managed_frame_name) is False


@pytest.mark.parametrize(
    ("nexus_frame_mode", "frame_name", "repeat_on_same_rift"),
    [
        ("single", None, False),
        ("indexed", "ops", False),
        ("one_per_workspace", None, True),
    ],
)
def test_component_rift_create_nexus_frame_rejects_existing_manager_frame(
        nexus_frame_mode: str,
        frame_name,
        repeat_on_same_rift: bool,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if frame_name is None:
        first.create_nexus_frame()
    else:
        first.create_nexus_frame(frame_name=frame_name)

    target_rift = first if repeat_on_same_rift else second
    kwargs = {} if frame_name is None else {"frame_name": frame_name}

    with pytest.raises(ValueError, match="already exists"):
        target_rift.create_nexus_frame(**kwargs)


@pytest.mark.parametrize(
    ("nexus_frame_mode", "remove_kind"),
    [
        ("single", "first"),
        ("single", "last"),
        ("indexed", "named"),
        ("indexed", "named_second"),
        ("one_per_workspace", "private"),
        ("one_per_workspace", "other_private"),
    ],
)
def test_component_nexus_remove_rift_cleans_frames_by_topology_matrix(
        nexus_frame_mode: str,
        remove_kind: str,
) -> None:
    nexus = _create_enabled_nexus(
        nexus_frame_mode=nexus_frame_mode,
        max_nexus_frame_count=8,
    )
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    if nexus_frame_mode == "single":
        shared = first.create_nexus_frame()
        shared_frame_name = shared._aetheric_frame
        assert second.get_nexus_frame() is shared
        nexus.remove_rift(first.id if remove_kind == "first" else second.id)
        assert nexus.frame_manager.exists(shared_frame_name) is True
        nexus.remove_rift(second.id if remove_kind == "first" else first.id)
        assert nexus.frame_manager.exists(shared_frame_name) is False
        return

    if nexus_frame_mode == "indexed":
        frame_name = "ops" if remove_kind == "named" else "finance"
        created = first.create_nexus_frame(frame_name=frame_name)
        created_frame_name = created._aetheric_frame
        nexus.remove_rift(first.id)
        assert nexus.frame_manager.exists(created_frame_name) is True
        return

    first_frame = first.create_nexus_frame()
    second_frame = second.create_nexus_frame()
    first_frame_name = first_frame._aetheric_frame
    second_frame_name = second_frame._aetheric_frame
    if remove_kind == "private":
        nexus.remove_rift(first.id)
        assert nexus.frame_manager.exists(first_frame_name) is False
        assert nexus.frame_manager.exists(second_frame_name) is True
        return

    nexus.remove_rift(second.id)
    assert nexus.frame_manager.exists(second_frame_name) is False
    assert nexus.frame_manager.exists(first_frame_name) is True
