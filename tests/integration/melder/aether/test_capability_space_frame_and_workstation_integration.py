from typing import Dict, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.rift import Rift
from melder.nexus.rift.rift_space.capability_rift_space import (
    CapabilityRiftSpace,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


class CapabilityWorkspaceService:
    """
    Stable runtime service used by the capability integration matrix.

    Purpose:
        Give the capability-room integration tests one deterministic runtime
        object with a simple callable method so frame-link, command, and
        workstation flows can be asserted without incidental behavior noise.
    """

    def __init__(self, kind_name: str) -> None:
        """
        Initialize the stable service marker.

        Args:
            kind_name:
                Stable marker used in assertions to distinguish frame-local
                runtime objects.

        Returns:
            None.
        """
        self.kind = kind_name
        self.calls = []

    def run(self, prefix: str = "ok") -> str:
        """
        Record one call and return a stable value.

        Args:
            prefix:
                Prefix used in the returned payload.

        Returns:
            str: Stable return value for the current service instance.
        """
        self.calls.append(prefix)
        return "{0}:{1}".format(self.kind, prefix)

    def make_payload(self, label: str) -> Dict[str, str]:
        """
        Return one stable payload dictionary for attribute-store assertions.

        Args:
            label:
                Stable label included in the payload.

        Returns:
            Dict[str, str]: Deterministic payload dictionary.
        """
        return {
            "kind": self.kind,
            "label": label,
        }

    def make_runner(self, prefix: str):
        """
        Return one deterministic callable for method-store assertions.

        Args:
            prefix:
                Stable prefix captured by the returned callable.

        Returns:
            object: Callable that appends a suffix to the captured prefix.
        """

        def _runner(suffix: str = "tail") -> str:
            return "{0}:{1}:{2}".format(self.kind, prefix, suffix)

        return _runner


def _reset_runtime_singletons() -> None:
    """
    Reset the singleton runtime surfaces used by the capability integration lane.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    CommandSystem._aether = aether


@pytest.fixture(autouse=True)
def _isolated_runtime() -> None:
    """
    Reset the singleton runtime surfaces before and after each integration test.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _build_publishable_configuration(
        frame_name: str,
        *,
        dynamic_frame: bool = True,
) -> SpellbookConfiguration:
    """
    Build one publishable Spellbook configuration for an integration frame.

    Args:
        frame_name:
            Target frame name.
        dynamic_frame:
            Whether the frame should use dynamic posture.

    Returns:
        SpellbookConfiguration: Publishable frame configuration.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=dynamic_frame,
        rift_enabled=True,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bind_service_in_spellbook(
        frame_name: str,
        *,
        conduit_name: str,
        kind_name: str,
        binding_name: str,
        spellframe_name: str = "CapabilityBench",
) -> Tuple[Spellbook, Conduit, str]:
    """
    Create one Spellbook, bind the stable capability service, and conjure a root conduit.

    Args:
        frame_name:
            Target frame name.
        conduit_name:
            Root conduit name.
        kind_name:
            Stable runtime-service marker.
        binding_name:
            Binding name used for the capability spell.
        spellframe_name:
            Spellframe/grouping name for the capability spell.

    Returns:
        Tuple[Spellbook, Conduit, str]:
            Spellbook, rooted conduit, and bound spell id.
    """
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_build_publishable_configuration(frame_name),
    )
    spell_id = spellbook.bind(
        spell=CapabilityWorkspaceService(kind_name),
        spellframe=spellframe_name,
        binding_name=binding_name,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name=conduit_name, automatic=False)
    return spellbook, conduit, spell_id


def _bind_service_in_conduit(
        conduit: Conduit,
        *,
        kind_name: str,
        binding_name: str,
        spellframe_name: str = "CapabilityBench",
) -> str:
    """
    Bind the stable capability service through an already-created rooted conduit.

    Args:
        conduit:
            Rooted conduit that should own the new spell.
        kind_name:
            Stable runtime-service marker.
        binding_name:
            Binding name used for the capability spell.
        spellframe_name:
            Spellframe/grouping name for the capability spell.

    Returns:
        str: Newly bound spell id.
    """
    with conduit.binding_transaction():
        return conduit.bind(
            spell=CapabilityWorkspaceService(kind_name),
            spellframe=spellframe_name,
            binding_name=binding_name,
            existence=Existence.unique,
            permissions="create",
        )


def _create_enabled_capability_nexus(
        *,
        nexus_frame_mode: str = "indexed",
        allowed_target_frame_names: Tuple[str, ...] = ("default",),
) -> Nexus:
    """
    Build one enabled Nexus configured for capability-room integration work.

    Args:
        nexus_frame_mode:
            Nexus internal frame topology mode.
        allowed_target_frame_names:
            Explicitly allowed non-Nexus frame targets.

    Returns:
        Nexus: Enabled Nexus instance.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(8)
    configuration.with_allowed_target_frame_names(allowed_target_frame_names)
    configuration.with_nexus_frame_mode(nexus_frame_mode)
    if nexus_frame_mode == "single":
        configuration.with_max_nexus_frame_count(1)
    else:
        configuration.with_max_nexus_frame_count(8)
    nexus.enable(configuration)
    return nexus


def _create_capability_rift(nexus: Nexus, *, rift_name: str) -> Rift:
    """
    Create one capability Rift from an enabled Nexus.

    Args:
        nexus:
            Enabled Nexus instance.
        rift_name:
            Stable Rift name.

    Returns:
        Rift: Live capability Rift.
    """
    configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.capability
    )
    return nexus.create_rift(configuration=configuration, rift_name=rift_name)


def _build_default_frame_harness() -> Dict[str, object]:
    """
    Build one capability-room harness linked to the default frame.

    Returns:
        Dict[str, object]: Live harness objects and stable test metadata.
    """
    spellbook, conduit, spell_id = _bind_service_in_spellbook(
        "default",
        conduit_name="default_root",
        kind_name="default_live",
        binding_name="default_live",
    )
    spell = conduit.get_spell_by_id(spell_id, "default")
    nexus = _create_enabled_capability_nexus(allowed_target_frame_names=("default",))
    rift = _create_capability_rift(nexus, rift_name="default_capability_rift")
    rift.create_frame_link("default")
    space = rift.space
    if not isinstance(space, CapabilityRiftSpace):
        raise RuntimeError("Capability harness did not create a capability room.")
    return {
        "frame_name": "default",
        "spellbook": spellbook,
        "conduit": conduit,
        "spell_id": spell_id,
        "spell_index_id": spell.spell_index.id,
        "source_id": "{0}:{1}".format(spellbook.id, spell_id),
        "nexus": nexus,
        "rift": rift,
        "space": space,
        "command": space.command_system,
        "workstation": space.workstation,
    }


def _build_nexus_frame_harness(frame_name: str = "ops") -> Dict[str, object]:
    """
    Build one capability-room harness linked to a newly created Nexus-managed frame.

    Args:
        frame_name:
            Nexus-managed frame name to create and link.

    Returns:
        Dict[str, object]: Live harness objects and stable test metadata.
    """
    nexus = _create_enabled_capability_nexus()
    rift = _create_capability_rift(nexus, rift_name="nexus_capability_rift")
    conduit = rift.create_nexus_frame(frame_name=frame_name)
    spell_id = _bind_service_in_conduit(
        conduit,
        kind_name="nexus_live",
        binding_name="nexus_live",
    )
    rift.create_frame_link(frame_name)
    spell = conduit.get_spell_by_id(spell_id, frame_name)
    space = rift.space
    if not isinstance(space, CapabilityRiftSpace):
        raise RuntimeError("Capability harness did not create a capability room.")
    return {
        "frame_name": frame_name,
        "conduit": conduit,
        "spell_id": spell_id,
        "spell_index_id": spell.spell_index.id,
        "source_id": "{0}:{1}".format(conduit._spellbook.id, spell_id),
        "nexus": nexus,
        "rift": rift,
        "space": space,
        "command": space.command_system,
        "workstation": space.workstation,
    }


def _build_dual_frame_harness() -> Dict[str, object]:
    """
    Build one capability-room harness linked to both a default frame and one
    Nexus-created frame.

    Returns:
        Dict[str, object]: Live harness objects and stable dual-frame metadata.
    """
    default_spellbook, default_conduit, default_spell_id = _bind_service_in_spellbook(
        "default",
        conduit_name="default_root",
        kind_name="default_live",
        binding_name="default_live",
    )
    nexus = _create_enabled_capability_nexus(allowed_target_frame_names=("default",))
    rift = _create_capability_rift(nexus, rift_name="dual_capability_rift")
    rift.create_frame_link("default")
    nexus_conduit = rift.create_nexus_frame(frame_name="ops")
    nexus_spell_id = _bind_service_in_conduit(
        nexus_conduit,
        kind_name="ops_live",
        binding_name="ops_live",
    )
    rift.create_frame_link("ops")
    space = rift.space
    if not isinstance(space, CapabilityRiftSpace):
        raise RuntimeError("Capability harness did not create a capability room.")
    default_spell = default_conduit.get_spell_by_id(default_spell_id, "default")
    ops_spell = nexus_conduit.get_spell_by_id(nexus_spell_id, "ops")
    return {
        "default_spellbook": default_spellbook,
        "default_conduit": default_conduit,
        "default_spell_id": default_spell_id,
        "default_spell_index_id": default_spell.spell_index.id,
        "default_source_id": "{0}:{1}".format(default_spellbook.id, default_spell_id),
        "ops_conduit": nexus_conduit,
        "ops_spell_id": nexus_spell_id,
        "ops_spell_index_id": ops_spell.spell_index.id,
        "ops_source_id": "{0}:{1}".format(nexus_conduit._spellbook.id, nexus_spell_id),
        "nexus": nexus,
        "rift": rift,
        "space": space,
        "command": space.command_system,
        "workstation": space.workstation,
    }


def _assert_default_frame_scenario(scenario_name: str) -> None:
    """
    Execute and assert one default-frame capability-room scenario.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    harness = _build_default_frame_harness()
    command = harness["command"]
    workstation = harness["workstation"]
    conduit = harness["conduit"]
    frame_name = harness["frame_name"]
    rift = harness["rift"]
    spell_id = harness["spell_id"]
    spell_index_id = harness["spell_index_id"]
    source_id = harness["source_id"]

    if scenario_name == "link_contract":
        assert rift.list_assigned_frame_names() == ("default",)
        assert rift.get_selected_contract_names("default") == {
            "view": "default",
            "command": "default",
            "codegen": "default",
        }
        return
    if scenario_name == "get_conduit_by_id":
        assert command.get_conduit_by_id(conduit.id, frame_name=frame_name) is conduit
        return
    if scenario_name == "get_conduit_by_name":
        assert command.get_conduit_by_name(conduit.name, frame_name=frame_name) is conduit
        return
    if scenario_name == "get_spell_by_index_id":
        spell = command.get_spell_by_index_id(spell_index_id, frame_name=frame_name)
        assert spell.spell_id == spell_id
        assert spell.spell_name == "CapabilityWorkspaceService"
        return
    if scenario_name == "get_spell_by_source_id":
        spell = command.get_spell_by_source_id(source_id, frame_name=frame_name)
        assert spell.spell_id == spell_id
        assert spell.spell_name == "CapabilityWorkspaceService"
        return
    if scenario_name == "meld":
        runtime_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        assert runtime_object.kind == "default_live"
        return
    if scenario_name == "meld_existing_spell":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        existing_object = command.meld_existing_spell(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        assert existing_object is live_object
        return
    if scenario_name == "bind_object_and_execute_target_method":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.set_target("live", store="objects")
        result = command.execute_target_method(
            "run",
            "default_object",
            bind_as_name="run_result",
        )
        assert result == "default_live:default_object"
        assert workstation.get("run_result", store="objects") == result
        return
    if scenario_name == "bind_attribute_and_get_target_attribute":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.bind_attribute("kind_value", live_object.kind, weak_ref=False)
        workstation.set_target("live", store="objects")
        assert command.get_target_attribute("kind") == "default_live"
        assert workstation.get("kind_value", store="attributes") == "default_live"
        return
    if scenario_name == "bind_method_and_call_target":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        workstation.bind_method("runner", live_object.run, weak_ref=False)
        workstation.set_target("runner", store="methods")
        assert workstation.call_target("default_method") == "default_live:default_method"
        return
    raise AssertionError(scenario_name)


def _assert_nexus_frame_scenario(scenario_name: str) -> None:
    """
    Execute and assert one Nexus-created capability-room scenario.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    harness = _build_nexus_frame_harness()
    command = harness["command"]
    workstation = harness["workstation"]
    conduit = harness["conduit"]
    frame_name = harness["frame_name"]
    rift = harness["rift"]
    spell_id = harness["spell_id"]

    if scenario_name == "create_returns_root_conduit":
        assert conduit.name == "root"
        assert conduit._aetheric_frame_name == frame_name
        return
    if scenario_name == "get_returns_created_root_conduit":
        assert rift.get_nexus_frame(frame_name) is conduit
        return
    if scenario_name == "duplicate_create_raises":
        with pytest.raises(ValueError, match="already exists"):
            rift.create_nexus_frame(frame_name=frame_name)
        return
    if scenario_name == "frame_link_contract_after_link":
        assert frame_name in rift.list_assigned_frame_names()
        assert rift.get_selected_contract_names(frame_name) == {
            "view": frame_name,
            "command": frame_name,
            "codegen": frame_name,
        }
        return
    if scenario_name == "get_conduit_by_id":
        assert command.get_conduit_by_id(conduit.id, frame_name=frame_name) is conduit
        return
    if scenario_name == "get_conduit_by_name":
        assert command.get_conduit_by_name(conduit.name, frame_name=frame_name) is conduit
        return
    if scenario_name == "meld":
        runtime_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        assert runtime_object.kind == "nexus_live"
        return
    if scenario_name == "meld_existing_spell":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        existing_object = command.meld_existing_spell(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        assert existing_object is live_object
        return
    if scenario_name == "bind_object_and_execute_target_method":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.set_target("live", store="objects")
        result = command.execute_target_method(
            "run",
            "nexus_object",
            bind_as_name="run_result",
        )
        assert result == "nexus_live:nexus_object"
        assert workstation.get("run_result", store="objects") == result
        return
    if scenario_name == "bind_attribute_and_get_target_attribute":
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name=frame_name,
        )
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.bind_attribute("kind_value", live_object.kind, weak_ref=False)
        workstation.set_target("live", store="objects")
        assert command.get_target_attribute("kind") == "nexus_live"
        assert workstation.get("kind_value", store="attributes") == "nexus_live"
        return
    raise AssertionError(scenario_name)


def _assert_dual_frame_scenario(scenario_name: str) -> None:
    """
    Execute and assert one dual-frame capability-room scenario.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    harness = _build_dual_frame_harness()
    command = harness["command"]
    workstation = harness["workstation"]
    rift = harness["rift"]
    default_conduit = harness["default_conduit"]
    default_spell_id = harness["default_spell_id"]
    ops_conduit = harness["ops_conduit"]
    ops_spell_id = harness["ops_spell_id"]

    if scenario_name == "assigned_frame_names":
        assert rift.list_assigned_frame_names() == ("default", "ops")
        return
    if scenario_name == "contract_names_per_frame":
        assert rift.get_selected_contract_names("default") == {
            "view": "default",
            "command": "default",
            "codegen": "default",
        }
        assert rift.get_selected_contract_names("ops") == {
            "view": "ops",
            "command": "ops",
            "codegen": "ops",
        }
        return
    if scenario_name == "get_default_and_ops_conduits":
        assert command.get_conduit_by_id(default_conduit.id, frame_name="default") is default_conduit
        assert command.get_conduit_by_id(ops_conduit.id, frame_name="ops") is ops_conduit
        return
    if scenario_name == "meld_from_default_frame":
        runtime_object = command.meld(
            default_conduit.id,
            spell=default_spell_id,
            frame_name="default",
        )
        assert runtime_object.kind == "default_live"
        return
    if scenario_name == "meld_from_ops_frame":
        runtime_object = command.meld(
            ops_conduit.id,
            spell=ops_spell_id,
            frame_name="ops",
        )
        assert runtime_object.kind == "ops_live"
        return
    if scenario_name == "workstation_holds_both_frame_objects":
        default_object = command.meld(
            default_conduit.id,
            spell=default_spell_id,
            frame_name="default",
        )
        ops_object = command.meld(
            ops_conduit.id,
            spell=ops_spell_id,
            frame_name="ops",
        )
        workstation.bind_object("default_live", default_object, weak_ref=False)
        workstation.bind_object("ops_live", ops_object, weak_ref=False)
        bindings = workstation.describe_bindings()
        assert bindings["objects"] == ["default_live", "ops_live"]
        return
    if scenario_name == "switch_target_between_frame_objects":
        default_object = command.meld(
            default_conduit.id,
            spell=default_spell_id,
            frame_name="default",
        )
        ops_object = command.meld(
            ops_conduit.id,
            spell=ops_spell_id,
            frame_name="ops",
        )
        workstation.bind_object("default_live", default_object, weak_ref=False)
        workstation.bind_object("ops_live", ops_object, weak_ref=False)
        workstation.set_target("default_live", store="objects")
        default_result = command.execute_target_method("run", "first")
        workstation.set_target("ops_live", store="objects")
        ops_result = command.execute_target_method("run", "second")
        assert default_result == "default_live:first"
        assert ops_result == "ops_live:second"
        return
    if scenario_name == "bind_methods_from_both_frames":
        default_object = command.meld(
            default_conduit.id,
            spell=default_spell_id,
            frame_name="default",
        )
        ops_object = command.meld(
            ops_conduit.id,
            spell=ops_spell_id,
            frame_name="ops",
        )
        workstation.bind_method("default_runner", default_object.run, weak_ref=False)
        workstation.bind_method("ops_runner", ops_object.run, weak_ref=False)
        workstation.set_target("default_runner", store="methods")
        default_result = workstation.call_target("first")
        workstation.set_target("ops_runner", store="methods")
        ops_result = workstation.call_target("second")
        assert default_result == "default_live:first"
        assert ops_result == "ops_live:second"
        return
    if scenario_name == "bind_results_from_both_frames":
        default_object = command.meld(
            default_conduit.id,
            spell=default_spell_id,
            frame_name="default",
        )
        ops_object = command.meld(
            ops_conduit.id,
            spell=ops_spell_id,
            frame_name="ops",
        )
        workstation.bind_object("default_live", default_object, weak_ref=False)
        workstation.bind_object("ops_live", ops_object, weak_ref=False)
        workstation.set_target("default_live", store="objects")
        command.execute_target_method(
            "run",
            "default_result",
            bind_as_name="default_result",
        )
        workstation.set_target("ops_live", store="objects")
        command.execute_target_method(
            "run",
            "ops_result",
            bind_as_name="ops_result",
        )
        assert workstation.get("default_result", store="objects") == "default_live:default_result"
        assert workstation.get("ops_result", store="objects") == "ops_live:ops_result"
        return
    if scenario_name == "get_nexus_frame_while_default_frame_stays_linked":
        assert rift.get_nexus_frame("ops") is ops_conduit
        assert "default" in rift.list_assigned_frame_names()
        return
    if scenario_name == "describe_bindings_after_cross_frame_work":
        default_object = command.meld(
            default_conduit.id,
            spell=default_spell_id,
            frame_name="default",
        )
        ops_object = command.meld(
            ops_conduit.id,
            spell=ops_spell_id,
            frame_name="ops",
        )
        workstation.bind_object("default_live", default_object, weak_ref=False)
        workstation.bind_object("ops_live", ops_object, weak_ref=False)
        workstation.bind_attribute("default_kind", default_object.kind, weak_ref=False)
        workstation.bind_attribute("ops_kind", ops_object.kind, weak_ref=False)
        bindings = workstation.describe_bindings()
        assert bindings["objects"] == ["default_live", "ops_live"]
        assert bindings["attributes"] == ["default_kind", "ops_kind"]
        return
    raise AssertionError(scenario_name)


@pytest.mark.parametrize(
    "scenario_name",
    (
        "link_contract",
        "get_conduit_by_id",
        "get_conduit_by_name",
        "get_spell_by_index_id",
        "get_spell_by_source_id",
        "meld",
        "meld_existing_spell",
        "bind_object_and_execute_target_method",
        "bind_attribute_and_get_target_attribute",
        "bind_method_and_call_target",
    ),
)
def test_capability_default_frame_workflow_matrix(
        scenario_name: str,
) -> None:
    """
    Verify capability-room default-frame link and workstation workflows.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    _assert_default_frame_scenario(scenario_name)


@pytest.mark.parametrize(
    "scenario_name",
    (
        "create_returns_root_conduit",
        "get_returns_created_root_conduit",
        "duplicate_create_raises",
        "frame_link_contract_after_link",
        "get_conduit_by_id",
        "get_conduit_by_name",
        "meld",
        "meld_existing_spell",
        "bind_object_and_execute_target_method",
        "bind_attribute_and_get_target_attribute",
    ),
)
def test_capability_nexus_created_frame_workflow_matrix(
        scenario_name: str,
) -> None:
    """
    Verify capability-room workflows over a newly created Nexus-managed frame.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    _assert_nexus_frame_scenario(scenario_name)


@pytest.mark.parametrize(
    "scenario_name",
    (
        "assigned_frame_names",
        "contract_names_per_frame",
        "get_default_and_ops_conduits",
        "meld_from_default_frame",
        "meld_from_ops_frame",
        "workstation_holds_both_frame_objects",
        "switch_target_between_frame_objects",
        "bind_methods_from_both_frames",
        "bind_results_from_both_frames",
        "get_nexus_frame_while_default_frame_stays_linked",
    ),
)
def test_capability_dual_frame_workstation_handoff_matrix(
        scenario_name: str,
) -> None:
    """
    Verify capability-room cross-frame and workstation handoff workflows.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    _assert_dual_frame_scenario(scenario_name)


def _assert_result_binding_scenario(scenario_name: str) -> None:
    """
    Execute and assert one result-binding integration scenario.

    Args:
        scenario_name:
            Stable scenario name.

        Returns:
            None.
    """
    if scenario_name.startswith("default_"):
        harness = _build_default_frame_harness()
        command = harness["command"]
        workstation = harness["workstation"]
        conduit = harness["conduit"]
        spell_id = harness["spell_id"]
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name="default",
        )
        if scenario_name in (
                "default_execute_bind_attribute_store",
                "default_execute_bind_method_store",
        ):
            workstation.bind_object("live", live_object, weak_ref=False)
            workstation.set_target("live", store="objects")
        if scenario_name == "default_execute_bind_attribute_store":
            result = command.execute_target_method(
                "make_payload",
                "default_attr",
                bind_as_name="payload",
                bind_as_store="attributes",
            )
            assert result == {"kind": "default_live", "label": "default_attr"}
            assert workstation.get("payload", store="attributes") == result
            return
        if scenario_name == "default_execute_bind_method_store":
            command.execute_target_method(
                "make_runner",
                "default_method",
                bind_as_name="runner",
                bind_as_store="methods",
            )
            workstation.set_target("runner", store="methods")
            assert workstation.call_target("tail") == "default_live:default_method:tail"
            return
        if scenario_name == "default_call_target_bind_attribute_store":
            workstation.bind_method("payload_builder", live_object.make_payload, weak_ref=False)
            workstation.set_target("payload_builder", store="methods")
            result = workstation.call_target(
                "default_call_attr",
                bind_as_name="payload",
                bind_as_store="attributes",
            )
            assert result == {"kind": "default_live", "label": "default_call_attr"}
            assert workstation.get("payload", store="attributes") == result
            return
        if scenario_name == "default_call_target_bind_method_store":
            workstation.bind_method("runner_builder", live_object.make_runner, weak_ref=False)
            workstation.set_target("runner_builder", store="methods")
            workstation.call_target(
                "default_call_method",
                bind_as_name="runner",
                bind_as_store="methods",
            )
            workstation.set_target("runner", store="methods")
            assert workstation.call_target("tail") == "default_live:default_call_method:tail"
            return
        if scenario_name == "default_execute_bind_object_store":
            workstation.bind_object("live", live_object, weak_ref=False)
            workstation.set_target("live", store="objects")
            result = command.execute_target_method(
                "make_payload",
                "default_object",
                bind_as_name="payload",
                bind_as_store="objects",
            )
            assert result == {"kind": "default_live", "label": "default_object"}
            assert workstation.get("payload", store="objects") == result
            return
    if scenario_name.startswith("nexus_"):
        harness = _build_nexus_frame_harness()
        command = harness["command"]
        workstation = harness["workstation"]
        conduit = harness["conduit"]
        spell_id = harness["spell_id"]
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name="ops",
        )
        if scenario_name in (
                "nexus_execute_bind_attribute_store",
                "nexus_execute_bind_method_store",
                "nexus_execute_bind_object_store",
        ):
            workstation.bind_object("live", live_object, weak_ref=False)
            workstation.set_target("live", store="objects")
        if scenario_name == "nexus_execute_bind_attribute_store":
            result = command.execute_target_method(
                "make_payload",
                "nexus_attr",
                bind_as_name="payload",
                bind_as_store="attributes",
            )
            assert result == {"kind": "nexus_live", "label": "nexus_attr"}
            assert workstation.get("payload", store="attributes") == result
            return
        if scenario_name == "nexus_execute_bind_method_store":
            command.execute_target_method(
                "make_runner",
                "nexus_method",
                bind_as_name="runner",
                bind_as_store="methods",
            )
            workstation.set_target("runner", store="methods")
            assert workstation.call_target("tail") == "nexus_live:nexus_method:tail"
            return
        if scenario_name == "nexus_call_target_bind_attribute_store":
            workstation.bind_method("payload_builder", live_object.make_payload, weak_ref=False)
            workstation.set_target("payload_builder", store="methods")
            result = workstation.call_target(
                "nexus_call_attr",
                bind_as_name="payload",
                bind_as_store="attributes",
            )
            assert result == {"kind": "nexus_live", "label": "nexus_call_attr"}
            assert workstation.get("payload", store="attributes") == result
            return
        if scenario_name == "nexus_call_target_bind_method_store":
            workstation.bind_method("runner_builder", live_object.make_runner, weak_ref=False)
            workstation.set_target("runner_builder", store="methods")
            workstation.call_target(
                "nexus_call_method",
                bind_as_name="runner",
                bind_as_store="methods",
            )
            workstation.set_target("runner", store="methods")
            assert workstation.call_target("tail") == "nexus_live:nexus_call_method:tail"
            return
        if scenario_name == "nexus_execute_bind_object_store":
            workstation.bind_object("live", live_object, weak_ref=False)
            workstation.set_target("live", store="objects")
            result = command.execute_target_method(
                "make_payload",
                "nexus_object",
                bind_as_name="payload",
                bind_as_store="objects",
            )
            assert result == {"kind": "nexus_live", "label": "nexus_object"}
            assert workstation.get("payload", store="objects") == result
            return
    harness = _build_dual_frame_harness()
    command = harness["command"]
    workstation = harness["workstation"]
    default_object = command.meld(
        harness["default_conduit"].id,
        spell=harness["default_spell_id"],
        frame_name="default",
    )
    ops_object = command.meld(
        harness["ops_conduit"].id,
        spell=harness["ops_spell_id"],
        frame_name="ops",
    )
    if scenario_name == "dual_default_execute_bind_attribute_store":
        workstation.bind_object("default_live", default_object, weak_ref=False)
        workstation.set_target("default_live", store="objects")
        result = command.execute_target_method(
            "make_payload",
            "dual_default",
            bind_as_name="payload",
            bind_as_store="attributes",
        )
        assert result == {"kind": "default_live", "label": "dual_default"}
        assert workstation.get("payload", store="attributes") == result
        return
    if scenario_name == "dual_ops_execute_bind_method_store":
        workstation.bind_object("ops_live", ops_object, weak_ref=False)
        workstation.set_target("ops_live", store="objects")
        command.execute_target_method(
            "make_runner",
            "dual_ops",
            bind_as_name="runner",
            bind_as_store="methods",
        )
        workstation.set_target("runner", store="methods")
        assert workstation.call_target("tail") == "ops_live:dual_ops:tail"
        return
    raise AssertionError(scenario_name)


def _assert_failure_scenario(scenario_name: str) -> None:
    """
    Execute and assert one workstation or mixed-frame failure scenario.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    if scenario_name.startswith("dual_"):
        harness = _build_dual_frame_harness()
        command = harness["command"]
        if scenario_name == "dual_get_conduit_by_id_wrong_frame":
            with pytest.raises(ValueError, match="disabled in frame 'ops'"):
                command.get_conduit_by_id(
                    harness["default_conduit"].id,
                    frame_name="ops",
                )
            return
        if scenario_name == "dual_get_spell_by_index_id_wrong_frame":
            with pytest.raises(ValueError, match="disabled in frame 'ops'"):
                command.get_spell_by_index_id(
                    harness["default_spell_index_id"],
                    frame_name="ops",
                )
            return
        raise AssertionError(scenario_name)

    harness = _build_default_frame_harness()
    command = harness["command"]
    workstation = harness["workstation"]
    conduit = harness["conduit"]
    spell_id = harness["spell_id"]
    live_object = command.meld(
        conduit.id,
        spell=spell_id,
        frame_name="default",
    )

    if scenario_name == "workstation_get_target_without_target":
        with pytest.raises(ValueError, match="no active target"):
            workstation.get_target()
        return
    if scenario_name == "command_execute_target_method_without_target":
        with pytest.raises(ValueError, match="no active target"):
            command.execute_target_method("run", "x")
        return
    if scenario_name == "workstation_set_target_missing_binding":
        with pytest.raises(ValueError, match="was not found"):
            workstation.set_target("missing", store="objects")
        return
    if scenario_name == "workstation_get_wrong_store":
        workstation.bind_object("live", live_object, weak_ref=False)
        with pytest.raises(ValueError, match="was not found in 'attributes'"):
            workstation.get("live", store="attributes")
        return
    if scenario_name == "workstation_release_missing_binding":
        with pytest.raises(ValueError, match="was not found"):
            workstation.release("missing", store="objects")
        return
    if scenario_name == "workstation_ambiguous_binding_across_stores":
        workstation.bind_object("shared", live_object, weak_ref=False)
        workstation.bind_method("shared", live_object.run, weak_ref=False)
        with pytest.raises(ValueError, match="ambiguous across workstation stores"):
            workstation.get("shared")
        return
    if scenario_name == "workstation_call_target_non_callable_object":
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.set_target("live", store="objects")
        with pytest.raises(RuntimeError, match="not callable"):
            workstation.call_target("x")
        return
    if scenario_name == "command_execute_target_method_invalid_bind_store":
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.set_target("live", store="objects")
        with pytest.raises(ValueError, match="Unsupported workstation store"):
            command.execute_target_method(
                "run",
                "x",
                bind_as_name="bad",
                bind_as_store="bad_store",
            )
        return
    if scenario_name == "command_get_target_method_empty_name":
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.set_target("live", store="objects")
        with pytest.raises(ValueError, match="method_name cannot be empty"):
            command.get_target_method("")
        return
    if scenario_name == "command_get_target_attribute_empty_name":
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.set_target("live", store="objects")
        with pytest.raises(ValueError, match="attribute_name cannot be empty"):
            command.get_target_attribute("")
        return
    raise AssertionError(scenario_name)


def _assert_cleanup_scenario(scenario_name: str) -> None:
    """
    Execute and assert one cleanup-after-binding integration scenario.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    if scenario_name.startswith("nexus_"):
        harness = _build_nexus_frame_harness()
        command = harness["command"]
        workstation = harness["workstation"]
        conduit = harness["conduit"]
        spell_id = harness["spell_id"]
        live_object = command.meld(
            conduit.id,
            spell=spell_id,
            frame_name="ops",
        )
        workstation.bind_object("live", live_object, weak_ref=False)
        workstation.bind_attribute("kind_value", live_object.kind, weak_ref=False)
        workstation.bind_method("runner", live_object.run, weak_ref=False)
        workstation.bind_object("conduit", conduit, weak_ref=False)
        conduit.cleanup()
        if scenario_name == "nexus_object_binding_survives_cleanup_retrieval":
            assert workstation.get("live", store="objects") is live_object
            return
        if scenario_name == "nexus_object_target_call_survives_cleanup":
            workstation.set_target("live", store="objects")
            assert command.execute_target_method("run", "after_cleanup") == "nexus_live:after_cleanup"
            return
        if scenario_name == "nexus_attribute_binding_survives_cleanup":
            assert workstation.get("kind_value", store="attributes") == "nexus_live"
            return
        if scenario_name == "nexus_method_binding_survives_cleanup":
            workstation.set_target("runner", store="methods")
            assert workstation.call_target("after_cleanup") == "nexus_live:after_cleanup"
            return
        if scenario_name == "nexus_cleaned_conduit_target_raises":
            workstation.set_target("conduit", store="objects")
            with pytest.raises(RuntimeError, match="Conduit has already been cleaned"):
                command.execute_target_method("get_spell_by_index_id", harness["spell_index_id"])
            return
        raise AssertionError(scenario_name)

    harness = _build_default_frame_harness()
    command = harness["command"]
    workstation = harness["workstation"]
    conduit = harness["conduit"]
    spell_id = harness["spell_id"]
    live_object = command.meld(
        conduit.id,
        spell=spell_id,
        frame_name="default",
    )
    workstation.bind_object("live", live_object, weak_ref=False)
    workstation.bind_attribute("kind_value", live_object.kind, weak_ref=False)
    workstation.bind_method("runner", live_object.run, weak_ref=False)
    workstation.bind_object("conduit", conduit, weak_ref=False)
    conduit.cleanup()
    if scenario_name == "default_object_binding_survives_cleanup_retrieval":
        assert workstation.get("live", store="objects") is live_object
        return
    if scenario_name == "default_object_target_call_survives_cleanup":
        workstation.set_target("live", store="objects")
        assert command.execute_target_method("run", "after_cleanup") == "default_live:after_cleanup"
        return
    if scenario_name == "default_attribute_binding_survives_cleanup":
        assert workstation.get("kind_value", store="attributes") == "default_live"
        return
    if scenario_name == "default_method_binding_survives_cleanup":
        workstation.set_target("runner", store="methods")
        assert workstation.call_target("after_cleanup") == "default_live:after_cleanup"
        return
    if scenario_name == "default_cleaned_conduit_target_raises":
        workstation.set_target("conduit", store="objects")
        with pytest.raises(RuntimeError, match="Conduit has already been cleaned"):
            command.execute_target_method("get_spell_by_index_id", harness["spell_index_id"])
        return
    raise AssertionError(scenario_name)


@pytest.mark.parametrize(
    "scenario_name",
    (
        "default_execute_bind_attribute_store",
        "default_execute_bind_method_store",
        "default_call_target_bind_attribute_store",
        "default_call_target_bind_method_store",
        "default_execute_bind_object_store",
        "nexus_execute_bind_attribute_store",
        "nexus_execute_bind_method_store",
        "nexus_call_target_bind_attribute_store",
        "nexus_call_target_bind_method_store",
        "nexus_execute_bind_object_store",
    ),
)
def test_capability_result_binding_store_matrix(
        scenario_name: str,
) -> None:
    """
    Verify richer capability-room result-binding behavior across workstation stores.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    _assert_result_binding_scenario(scenario_name)


@pytest.mark.parametrize(
    "scenario_name",
    (
        "workstation_get_target_without_target",
        "command_execute_target_method_without_target",
        "workstation_set_target_missing_binding",
        "workstation_get_wrong_store",
        "workstation_release_missing_binding",
        "workstation_ambiguous_binding_across_stores",
        "workstation_call_target_non_callable_object",
        "command_execute_target_method_invalid_bind_store",
        "dual_get_conduit_by_id_wrong_frame",
        "dual_get_spell_by_index_id_wrong_frame",
    ),
)
def test_capability_workstation_failure_matrix(
        scenario_name: str,
) -> None:
    """
    Verify capability-room workstation and mixed-frame failure contracts.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    _assert_failure_scenario(scenario_name)


@pytest.mark.parametrize(
    "scenario_name",
    (
        "default_object_binding_survives_cleanup_retrieval",
        "default_object_target_call_survives_cleanup",
        "default_attribute_binding_survives_cleanup",
        "default_method_binding_survives_cleanup",
        "default_cleaned_conduit_target_raises",
        "nexus_object_binding_survives_cleanup_retrieval",
        "nexus_object_target_call_survives_cleanup",
        "nexus_attribute_binding_survives_cleanup",
        "nexus_method_binding_survives_cleanup",
        "nexus_cleaned_conduit_target_raises",
    ),
)
def test_capability_cleanup_after_binding_matrix(
        scenario_name: str,
) -> None:
    """
    Verify capability-room workstation behavior after conduit/frame cleanup.

    Args:
        scenario_name:
            Stable scenario name.

    Returns:
        None.
    """
    _assert_cleanup_scenario(scenario_name)
