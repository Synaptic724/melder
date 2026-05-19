from types import SimpleNamespace
from typing import Dict, Tuple

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook


class EventSystemDouble:
    """
    Small event-system double used by codegen-system tests.
    """

    def __init__(self) -> None:
        self.events = []

    def create_and_emit_event(
            self,
            event_type: str,
            *,
            frame_name: str,
            payload: Dict[str, object],
    ) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "frame_name": frame_name,
                "payload": dict(payload),
            }
        )


class MemorySystemDouble:
    """
    Small memory-system double used by codegen command-system tests.
    """

    def __init__(self) -> None:
        self.memory_enabled = True
        self.records = []

    def create_and_emit_memory(
            self,
            *,
            frame_name: str,
            action_name: str,
            metadata: Dict[str, object],
    ) -> None:
        self.records.append(
            {
                "frame_name": frame_name,
                "action_name": action_name,
                "metadata": dict(metadata),
            }
        )


class FrameViewerDouble:
    """
    Minimal frame-viewer double for namespace and codegen-system tests.
    """

    def __init__(self) -> None:
        self.calls = []

    def list_nexus_frame_names(self) -> Tuple[str, ...]:
        self.calls.append("list_nexus_frame_names")
        return ("ops",)


class WorkstationDouble:
    """
    Minimal workstation double for namespace tests.
    """

    def __init__(self) -> None:
        self.bindings = {}
        self._target = None

    def bind_object(self, name: str, value: object) -> None:
        self.bindings[name] = value

    def set_target(self, value: object) -> None:
        self._target = value

    def get_target(self) -> object:
        if self._target is None:
            raise ValueError("no target is selected")
        return self._target


class CommandSystemDouble:
    """
    Minimal command-system double for namespace and codegen tests.
    """

    def __init__(self) -> None:
        self.calls = []

    def link_frame(self, frame_name: str) -> str:
        self.calls.append(("link_frame", frame_name))
        return frame_name


class CodegenSpaceDouble:
    """
    Small room double with the attributes the codegen-system uses.
    """

    def __init__(self, *, space_id: str = "space-1") -> None:
        self.space_id = space_id
        self.frame_viewer = FrameViewerDouble()
        self.workstation = WorkstationDouble()
        self.command_system = CommandSystemDouble()
        self.event_system = EventSystemDouble()
        self.memory_system = MemorySystemDouble()
        self.codegen_system = None


class DetachedRiftProjectionOwner:
    """
    Small Rift-like double that serves codegen projections by frame name.
    """

    def __init__(self) -> None:
        self._codegen_projections_by_frame_name = {}

    def _get_required_codegen_projection(self, frame_name: str) -> object:
        return self._codegen_projections_by_frame_name[frame_name]


def build_compiled_access_surface(
        *,
        imports_enabled: bool = False,
        allowed_import_module_roots: Tuple[str, ...] = tuple(),
        denied_import_module_roots: Tuple[str, ...] = tuple(),
        denied_builtin_names: Tuple[str, ...] = tuple(),
        unsafe_reflection_allowed: bool = False,
        dunder_access_allowed: bool = False,
        recursive_codegen_allowed: bool = False,
) -> object:
    """
    Build one compiled-access-surface double with the codegen fields in use.
    """
    return SimpleNamespace(
        codegen_imports_enabled=imports_enabled,
        allowed_import_module_roots=tuple(allowed_import_module_roots),
        denied_import_module_roots=tuple(denied_import_module_roots),
        denied_builtin_names=tuple(denied_builtin_names),
        codegen_unsafe_reflection_allowed=unsafe_reflection_allowed,
        codegen_dunder_access_allowed=dunder_access_allowed,
        codegen_recursive_codegen_allowed=recursive_codegen_allowed,
    )


def build_codegen_projection(
        *,
        imports_enabled: bool = False,
        allowed_import_module_roots: Tuple[str, ...] = tuple(),
        denied_import_module_roots: Tuple[str, ...] = tuple(),
        denied_builtin_names: Tuple[str, ...] = tuple(),
        unsafe_reflection_allowed: bool = False,
        dunder_access_allowed: bool = False,
        recursive_codegen_allowed: bool = False,
) -> object:
    """
    Build one codegen-projection double with the compiled access surface in use.
    """
    return SimpleNamespace(
        compiled_access_surface=build_compiled_access_surface(
            imports_enabled=imports_enabled,
            allowed_import_module_roots=allowed_import_module_roots,
            denied_import_module_roots=denied_import_module_roots,
            denied_builtin_names=denied_builtin_names,
            unsafe_reflection_allowed=unsafe_reflection_allowed,
            dunder_access_allowed=dunder_access_allowed,
            recursive_codegen_allowed=recursive_codegen_allowed,
        )
    )


def build_namespace_configuration(
        *,
        frame_name: str = "ops",
        include_target: bool = True,
        imports_enabled: bool = False,
        allowed_import_module_roots: Tuple[str, ...] = tuple(),
        denied_import_module_roots: Tuple[str, ...] = tuple(),
        denied_builtin_names: Tuple[str, ...] = tuple(),
        allow_unsafe_reflection: bool = False,
        allow_dunder_access: bool = False,
        allow_recursive_codegen: bool = False,
    ) -> CodegenNamespaceConfiguration:
    """
    Build one namespace configuration for codegen-system tests.
    """
    return CodegenNamespaceConfiguration.create_default(
        frame_name=frame_name,
        include_target=include_target,
        imports_enabled=imports_enabled,
        allowed_import_module_roots=allowed_import_module_roots,
        denied_import_module_roots=denied_import_module_roots,
        denied_builtin_names=denied_builtin_names,
        allow_unsafe_reflection=allow_unsafe_reflection,
        allow_dunder_access=allow_dunder_access,
        allow_recursive_codegen=allow_recursive_codegen,
    )


def reset_runtime_singletons() -> None:
    """
    Reset Melder/Nexus singletons for integration-style codegen tests.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def create_enabled_nexus() -> Nexus:
    """
    Create one enabled Nexus suitable for codegen-room integration tests.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode(NexusFrameMode.indexed)
    configuration.with_max_nexus_frame_count(8)
    nexus.enable(configuration)
    return nexus


def create_codegen_rift(nexus: Nexus, *, rift_name: str = "alpha"):
    """
    Create one real codegen room through the live Nexus creation path.
    """
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type("codegen")
    return nexus.create_rift(configuration=configuration, rift_name=rift_name)
