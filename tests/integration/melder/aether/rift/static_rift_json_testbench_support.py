import json
from typing import Any, Dict, List, Optional

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


class _BaseBenchService:
    """
    Base runtime service used by the static Rift integration testbench.

    Purpose:
        Provide one stable runtime object shape with a marker and callable
        method so the harness can assert identity and execution contracts.
    """

    kind_name: str = "base"

    def __init__(self) -> None:
        """
        Initialize the stable service marker.

        Returns:
            None.
        """
        self.kind = self.kind_name
        self.calls: List[str] = []

    def run(self, prefix: str = "ok") -> str:
        """
        Record one call and return a stable string.

        Args:
            prefix:
                Prefix value used in the return payload.

        Returns:
            str: Stable return string for assertions.
        """
        self.calls.append(prefix)
        return "{0}:{1}".format(self.kind, prefix)


class UniqueLiveService(_BaseBenchService):
    """Unique service that will be materialized as live in the harness."""

    kind_name = "unique_live"


class UniquePerConduitLiveService(_BaseBenchService):
    """unique_per_conduit service that will be materialized as live."""

    kind_name = "unique_per_conduit_live"


class UniquePerLineageLiveService(_BaseBenchService):
    """unique_per_conduit_lineage service that will be materialized as live."""

    kind_name = "unique_per_lineage_live"


class ManyLiveService(_BaseBenchService):
    """many service that will be materialized but hidden in static mode."""

    kind_name = "many_live"


class SpellSpaceLiveService(_BaseBenchService):
    """unique_per_spell_space service that will be materialized but hidden."""

    kind_name = "spellspace_live"


class UniqueDeadService(_BaseBenchService):
    """Unique service that stays published but never materialized."""

    kind_name = "unique_dead"


class ManualTarget:
    """
    Manual runtime object used for workstation JSON-driver interaction tests.
    """

    def __init__(self, name: str = "manual_target") -> None:
        """
        Initialize the manual target.

        Args:
            name:
                Stable target name for assertions.

        Returns:
            None.
        """
        self.name = name
        self.calls: List[str] = []

    def run(self, prefix: str = "manual") -> str:
        """
        Record one call and return a stable object.

        Args:
            prefix:
                Prefix used in the returned value.

        Returns:
            object: Stable return object.
        """
        self.calls.append(prefix)
        return ManualResult("{0}:{1}".format(self.name, prefix))


class ManualResult:
    """
    Weak-referenceable result object for workstation execution tests.
    """

    def __init__(self, value: str) -> None:
        """
        Initialize the result value.

        Args:
            value:
                Stable result payload.

        Returns:
            None.
        """
        self.value = value


class StaticRiftJsonBench:
    """
    Real static-room integration harness with a JSON-like request driver.

    Purpose:
        Build one reusable runtime stack for static-room integration tests:
        Spellbook, Conduit, Nexus, Rift, StaticRiftSpace, and the associated
        viewer/command/workstation surfaces.
    """

    def __init__(self, *, frame_name: str, dynamic_frame: bool) -> None:
        """
        Initialize one static-room integration harness.

        Args:
            frame_name:
                Target frame name for this harness.
            dynamic_frame:
                Whether the underlying Melder frame uses dynamic posture.

        Returns:
            None.
        """
        self.frame_name = frame_name
        self.dynamic_frame = bool(dynamic_frame)
        self.aether = Aether()
        Spellbook._aether = self.aether
        Conduit._aether = self.aether
        self.spellbook = Spellbook(
            aetheric_frame=frame_name,
            configuration=self._build_configuration(),
        )
        self._bound_spell_ids_by_case_name: Dict[str, str] = {}
        self._bind_spells()
        self.root_conduit = self.spellbook.conjure(
            name="root",
            automatic=not self.dynamic_frame,
        )
        self.lesser_conduit = self.root_conduit.create_lesser_conduit()
        self._live_objects_by_case_name: Dict[str, object] = {}
        self._materialize_live_objects()
        self.nexus = self._build_nexus()
        self.rift = self._build_rift()
        self.space = self.rift.space
        if not isinstance(self.space, StaticRiftSpace):
            raise RuntimeError("Static Rift bench did not create a static room.")
        self.viewer = self.space.frame_viewer
        if self.viewer is None:
            raise RuntimeError("Static Rift bench room has no attached viewer.")
        self.command = self.space.command_system
        self.workstation = self.space.workstation
        self._objects_by_name: Dict[str, object] = {
            "manual_target": ManualTarget(),
        }
        self.manifest = self._build_manifest()

    def cleanup(self) -> None:
        """
        Cleanup the harness-owned runtime objects.

        Returns:
            None.
        """
        if self.spellbook is not None and not self.spellbook.cleaned:
            self.spellbook.cleanup()
        if self.rift is not None and not self.rift.cleaned:
            self.rift.cleanup()
        if self.root_conduit is not None and not self.root_conduit.cleaned:
            self.root_conduit.cleanup()

    def dispatch_json(self, request_json: str) -> Any:
        """
        Dispatch one JSON-like API request against the harness.

        Args:
            request_json:
                JSON payload containing `surface`, `method`, `args`, and
                `kwargs`.

        Returns:
            Any: API return value.
        """
        request = json.loads(request_json)
        surface_name = request["surface"]
        method_name = request["method"]
        args = self._resolve_request_value(request.get("args", []))
        kwargs = self._resolve_request_value(request.get("kwargs", {}))
        surface = self._resolve_surface(surface_name, kwargs)
        method = getattr(surface, method_name)
        return method(*args, **kwargs)

    def dispatch_turn_script_json(self, script_json: str) -> Dict[str, Any]:
        """
        Dispatch one multistep turn script against the harness.

        Args:
            script_json:
                JSON payload containing a `turns` list.

        Returns:
            Dict[str, Any]: Saved turn results keyed by `save_as`.
        """
        script = json.loads(script_json)
        return self.dispatch_turn_script(script)

    def dispatch_turn_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch one multistep turn script against the harness.

        Args:
            script:
                Parsed turn-script payload.

        Returns:
            Dict[str, Any]: Saved turn results keyed by `save_as`.
        """
        turns = script.get("turns")
        if not isinstance(turns, list) or len(turns) == 0:
            raise ValueError("turn script must include a non-empty 'turns' list.")
        saved_results: Dict[str, Any] = {}
        for turn in turns:
            if not isinstance(turn, dict):
                raise ValueError("each turn must be a mapping.")
            save_as = turn.get("save_as")
            expect_error_contains = turn.get("expect_error_contains")
            surface_name = turn["surface"]
            method_name = turn["method"]
            args = self._resolve_turn_value(turn.get("args", []), saved_results)
            kwargs = self._resolve_turn_value(turn.get("kwargs", {}), saved_results)
            surface = self._resolve_surface(surface_name, kwargs)
            method = getattr(surface, method_name)
            try:
                result = method(*args, **kwargs)
            except ValueError as exc:
                if expect_error_contains is None:
                    raise
                if expect_error_contains not in str(exc):
                    raise
                result = {"error": str(exc)}
            else:
                if expect_error_contains is not None:
                    raise AssertionError(
                        "Expected ValueError containing '{0}'.".format(
                            expect_error_contains
                        )
                    )
            if save_as is not None:
                saved_results[save_as] = result
        return saved_results

    def drop_object_reference(self, object_name: str) -> None:
        """
        Drop one managed object reference from the harness.

        Args:
            object_name:
                Managed object name to drop.

        Returns:
            None.
        """
        self._objects_by_name.pop(object_name, None)

    def _build_configuration(self) -> Configuration:
        """
        Build the Spellbook configuration for this harness.

        Returns:
            Configuration: Publishable frame configuration.
        """
        configuration = Configuration(aether_frame=self.frame_name)
        if self.dynamic_frame:
            configuration.dynamic_defaults()
        else:
            configuration.automatic_defaults()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        configuration.set_property("rift_enabled", True)
        return configuration

    def _bind_spells(self) -> None:
        """
        Bind the reusable spell set used by the harness.

        Returns:
            None.
        """
        self._bound_spell_ids_by_case_name["unique_live"] = self.spellbook.bind(
            spell=UniqueLiveService,
            spellframe="StaticBench",
            binding_name="unique_live",
            existence=Existence.unique,
            permissions="create",
        )
        self._bound_spell_ids_by_case_name["unique_per_conduit_live"] = (
            self.spellbook.bind(
                spell=UniquePerConduitLiveService,
                spellframe="StaticBench",
                binding_name="unique_per_conduit_live",
                existence=Existence.unique_per_conduit,
                permissions="create",
            )
        )
        self._bound_spell_ids_by_case_name["unique_per_lineage_live"] = (
            self.spellbook.bind(
                spell=UniquePerLineageLiveService,
                spellframe="StaticBench",
                binding_name="unique_per_lineage_live",
                existence=Existence.unique_per_conduit_lineage,
                permissions="create",
            )
        )
        self._bound_spell_ids_by_case_name["many_live"] = self.spellbook.bind(
            spell=ManyLiveService,
            spellframe="StaticBench",
            binding_name="many_live",
            existence=Existence.many,
            permissions="create",
        )
        self._bound_spell_ids_by_case_name["spellspace_live"] = self.spellbook.bind(
            spell=SpellSpaceLiveService,
            spellframe="StaticBench",
            binding_name="spellspace_live",
            existence=Existence.unique_per_spell_space,
            permissions="create",
        )
        self._bound_spell_ids_by_case_name["unique_dead"] = self.spellbook.bind(
            spell=UniqueDeadService,
            spellframe="StaticBench",
            binding_name="unique_dead",
            existence=Existence.unique,
            permissions="create",
        )

    def _build_nexus(self) -> Nexus:
        """
        Build one enabled Nexus for this harness frame.

        Returns:
            Nexus: Enabled Nexus.
        """
        nexus = Nexus()
        configuration = nexus.create_system_configuration()
        configuration.with_rift_creation_enabled(True)
        configuration.with_direct_rift_access(True)
        configuration.with_target_frame_override(True)
        configuration.with_multiple_target_frames(True)
        configuration.with_max_target_frame_count(8)
        configuration.with_allowed_target_frame_names(("default", self.frame_name))
        nexus.enable(configuration)
        return nexus

    def _build_rift(self) -> Rift:
        """
        Build one targeted static Rift for this harness.

        Returns:
            Rift: Targeted static Rift.
        """
        configuration = self.nexus.create_rift_configuration().with_space_type(
            RiftSpaceType.static
        )
        rift = self.nexus.create_rift(
            configuration=configuration,
            rift_name="{0}_rift".format(self.frame_name),
        )
        rift.create_frame_link(self.frame_name)
        return rift

    def _materialize_live_objects(self) -> None:
        """
        Materialize the live spell cases used by this harness.

        Returns:
            None.
        """
        self._live_objects_by_case_name["unique_live"] = self.root_conduit.meld(
            spell=self._bound_spell_ids_by_case_name["unique_live"]
        )
        self._live_objects_by_case_name["unique_per_conduit_live"] = (
            self.root_conduit.meld(
                spell=self._bound_spell_ids_by_case_name["unique_per_conduit_live"]
            )
        )
        self._live_objects_by_case_name["unique_per_lineage_live"] = (
            self.root_conduit.meld(
                spell=self._bound_spell_ids_by_case_name["unique_per_lineage_live"]
            )
        )
        self._live_objects_by_case_name["many_live"] = self.root_conduit.meld(
            spell=self._bound_spell_ids_by_case_name["many_live"]
        )
        with self.root_conduit.enter_spellspace() as spellspace:
            self._live_objects_by_case_name["spellspace_live"] = spellspace.meld(
                spell=self._bound_spell_ids_by_case_name["spellspace_live"]
            )

    def _build_manifest(self) -> Dict[str, object]:
        """
        Build one manifest of ids and source ids for request placeholders.

        Returns:
            Dict[str, object]: Harness manifest.
        """
        spell_entries: Dict[str, Dict[str, object]] = {}
        for case_name, spell_id in self._bound_spell_ids_by_case_name.items():
            spell_object = self.root_conduit.get_spell_by_id(
                spell_id,
                self.frame_name,
            )
            spell_entries[case_name] = {
                "spell_id": spell_id,
                "spell_index_id": spell_object.spell_index.id,
                "spell_name": spell_object.spell_name,
                "binding_name": spell_object.binding_name,
                "source_id": "{0}:{1}".format(self.spellbook.id, spell_id),
            }
        return {
            "frame_name": self.frame_name,
            "frame_mode": "dynamic" if self.dynamic_frame else "automatic",
            "conduits": {
                "root": {
                    "id": self.root_conduit.id,
                    "name": self.root_conduit.name,
                },
                "lesser": {
                    "id": self.lesser_conduit.id,
                },
            },
            "spells": spell_entries,
        }

    def _resolve_surface(self, surface_name: str, kwargs: Dict[str, object]) -> Any:
        """
        Resolve one dispatch surface name to a live API object.

        Args:
            surface_name:
                Requested surface name.
            kwargs:
                Resolved kwargs for the request.

        Returns:
            Any: Live dispatch surface.
        """
        if surface_name == "rift":
            return self.rift
        if surface_name == "space":
            return self.space
        if surface_name == "viewer":
            return self.viewer
        if surface_name == "command":
            return self.command
        if surface_name == "workstation":
            return self.workstation
        raise ValueError("Unsupported surface '{0}'.".format(surface_name))

    def _resolve_request_value(self, value: Any) -> Any:
        """
        Resolve manifest/object placeholders inside one request value.

        Args:
            value:
                Raw request value.

        Returns:
            Any: Resolved value.
        """
        if isinstance(value, list):
            return [self._resolve_request_value(item) for item in value]
        if isinstance(value, dict):
            return {
                key: self._resolve_request_value(current_value)
                for key, current_value in value.items()
            }
        if isinstance(value, str) and value.startswith("@manifest."):
            return self._resolve_manifest_path(value[len("@manifest."):])
        if isinstance(value, str) and value.startswith("@objects."):
            return self._resolve_object_path(value[len("@objects."):])
        return value

    def _resolve_turn_value(
            self,
            value: Any,
            saved_results: Dict[str, Any],
    ) -> Any:
        """
        Resolve manifest/object/turn placeholders inside one turn payload.

        Args:
            value:
                Raw turn value.
            saved_results:
                Saved results from earlier turns.

        Returns:
            Any: Resolved value.
        """
        if isinstance(value, list):
            return [self._resolve_turn_value(item, saved_results) for item in value]
        if isinstance(value, dict):
            return {
                key: self._resolve_turn_value(current_value, saved_results)
                for key, current_value in value.items()
            }
        if isinstance(value, str) and value.startswith("@turns."):
            return self._resolve_turn_path(value[len("@turns."):], saved_results)
        return self._resolve_request_value(value)

    def _resolve_manifest_path(self, path: str) -> Any:
        """
        Resolve one manifest placeholder path.

        Args:
            path:
                Manifest path after the `@manifest.` prefix.

        Returns:
            Any: Resolved manifest value.
        """
        current_value: Any = self.manifest
        for current_part in path.split("."):
            current_value = current_value[current_part]
        return current_value

    def _resolve_object_path(self, path: str) -> object:
        """
        Resolve one managed object placeholder path.

        Args:
            path:
                Object path after the `@objects.` prefix.

        Returns:
            object: Managed object reference.
        """
        return self._objects_by_name[path]

    def _resolve_turn_path(
            self,
            path: str,
            saved_results: Dict[str, Any],
    ) -> Any:
        """
        Resolve one saved-turn placeholder path.

        Args:
            path:
                Placeholder path after the `@turns.` prefix.
            saved_results:
                Saved results from earlier turns.

        Returns:
            Any: Resolved saved-turn value.
        """
        current_value: Any = saved_results
        for current_part in path.split("."):
            if isinstance(current_value, dict):
                current_value = current_value[current_part]
                continue
            if isinstance(current_value, (list, tuple)):
                current_value = current_value[int(current_part)]
                continue
            current_value = getattr(current_value, current_part)
        return current_value

