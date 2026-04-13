from typing import Dict, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


class BasicService:
    """
    Basic service used to seed one real spell into the Nexus viewer path.
    """

    def run(self) -> str:
        """
        Return a stable string for integration assertions.

        Returns:
            str: Stable integration string.
        """
        return "ok"


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each integration matrix case.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether


def _make_rift_publishable_configuration(aetheric_frame: str) -> Configuration:
    """
    Build one Spellbook configuration that allows Nexus/Rift publication.

    Args:
        aetheric_frame:
            Target frame name for the spellbook.

    Returns:
        Configuration: Publishable dynamic configuration.
    """
    configuration = Configuration(aether_frame=aetheric_frame)
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    return configuration


def _build_real_nexus_viewer() -> object:
    """
    Build one real Nexus-backed viewer for integration checks.

    Returns:
        object: Descriptor-driven viewer built from a real Spellbook/Nexus path.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    nexus = Nexus()
    viewer = nexus.create_frame_viewer(["ops"])
    return spellbook, conduit, nexus, viewer


def _build_real_rift_viewer() -> object:
    """
    Build one real Rift-backed frame-specific viewer for integration checks.

    Returns:
        object: Tuple of live runtime objects plus the Rift-created viewer.
    """
    spellbook, conduit, nexus, _ = _build_real_nexus_viewer()
    system_configuration = nexus.create_system_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    system_configuration.with_target_frame_override(True)
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(2)
    system_configuration.with_default_space_type(RiftSpaceType.dynamic)
    system_configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(system_configuration)

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_space_type(RiftSpaceType.static)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops", set_as_default=True)
    viewer = rift.create_new_frame_viewer("ops", viewer_profile_name="general")
    return spellbook, conduit, nexus, rift, viewer


def _build_tool_kwargs(viewer: object, tool_name: str) -> dict[str, object]:
    """
    Build the required kwargs for one real viewer tool call.

    Args:
        viewer:
            Bound real viewer instance.
        tool_name:
            Tool name being executed.

    Returns:
        dict[str, object]: Tool kwargs.
    """
    conduit_id = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="conduit",
    )[0].source_id
    spell_source_id = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="spell",
    )[0].source_id
    if tool_name in {"describe_frame_inventory", "describe_frame_access_contract", "describe_frame_payload"}:
        return {"frame_name": "ops"}
    if tool_name in {"describe_conduits"}:
        return {"frame_name": "ops"}
    if tool_name in {"describe_conduit", "describe_conduit_topology", "explain_conduit_access"}:
        return {"frame_name": "ops", "conduit_id": conduit_id}
    if tool_name in {"describe_spells"}:
        return {"frame_name": "ops"}
    if tool_name in {"describe_spell", "describe_spell_payload", "describe_spell_detail", "explain_spell_access"}:
        return {"frame_name": "ops", "spell_source_id": spell_source_id}
    raise ValueError(tool_name)


NEXUS_VIEWER_CASES = [
    ("describe_frame_inventory", "frame_name"),
    ("describe_frame_access_contract", "view_profile_name"),
    ("describe_frame_payload", "payload"),
    ("describe_conduits", None),
    ("describe_conduit", "source_kind"),
    ("describe_conduit_topology", "spell_count"),
    ("explain_conduit_access", "reason"),
    ("describe_spells", None),
    ("describe_spell_payload", "payload_type"),
    ("explain_spell_access", "detail_reason"),
]


@pytest.mark.parametrize(
    ("tool_name", "expected_key"),
    NEXUS_VIEWER_CASES,
)
def test_real_nexus_viewer_general_tool_matrix(
        tool_name: str,
        expected_key: Optional[str],
) -> None:
    spellbook, conduit, _, viewer = _build_real_nexus_viewer()
    try:
        result = viewer.execute_method(
            tool_name,
            **_build_tool_kwargs(viewer, tool_name),
        )
        if expected_key is None:
            assert len(result) >= 1
        else:
            assert expected_key in result
    finally:
        conduit.cleanup()
        spellbook.cleanup()


RIFT_VIEWER_CASES = [
    ("describe_frame_inventory", "frame_name"),
    ("describe_frame_access_contract", "view_profile_name"),
    ("describe_frame_payload", "payload"),
    ("describe_conduits", None),
    ("describe_conduit", "source_kind"),
    ("describe_conduit_topology", "spell_count"),
    ("explain_conduit_access", "reason"),
    ("describe_spells", None),
    ("describe_spell_payload", "payload_type"),
    ("explain_spell_access", "detail_reason"),
]


@pytest.mark.parametrize(
    ("tool_name", "expected_key"),
    RIFT_VIEWER_CASES,
)
def test_real_rift_viewer_general_tool_matrix(
        tool_name: str,
        expected_key: Optional[str],
) -> None:
    spellbook, conduit, _, rift, viewer = _build_real_rift_viewer()
    try:
        result = viewer.execute_method(
            tool_name,
            **_build_tool_kwargs(viewer, tool_name),
        )
        if expected_key is None:
            assert len(result) >= 1
        else:
            assert expected_key in result
    finally:
        rift.cleanup()
        conduit.cleanup()
        spellbook.cleanup()
