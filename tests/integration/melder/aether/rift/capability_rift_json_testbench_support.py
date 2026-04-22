import json
from typing import Any, Dict, List

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.rift.rift_space.capability_rift_space import (
    CapabilityRiftSpace,
)
from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


class CapabilityBenchService:
    """
    Stable runtime service used by the capability integration harness.

    Purpose:
        Give the capability bench one live spell object with a deterministic
        callable method so the JSON driver can assert direct spell-runtime
        access through the capability room.
    """

    def __init__(self, kind_name: str = "capability_live") -> None:
        """
        Initialize the stable service marker.

        Args:
            kind_name:
                Stable marker used in assertions.

        Returns:
            None.
        """
        self.kind = kind_name
        self.calls: List[str] = []

    def run(self, prefix: str = "ok") -> str:
        """
        Record one call and return a stable value.

        Args:
            prefix:
                Prefix used in the returned payload.

        Returns:
            str: Stable return value.
        """
        self.calls.append(prefix)
        return "{0}:{1}".format(self.kind, prefix)

    def make_payload(self, label: str) -> Dict[str, str]:
        """
        Return one stable payload dictionary for workstation attribute binding.

        Args:
            label:
                Stable label included in the returned payload.

        Returns:
            Dict[str, str]: Deterministic payload dictionary.
        """
        return {
            "kind": self.kind,
            "label": label,
        }

    def make_runner(self, prefix: str):
        """
        Return one deterministic callable for workstation method binding.

        Args:
            prefix:
                Stable prefix captured by the returned callable.

        Returns:
            object: Callable that appends its suffix to the captured prefix.
        """

        def _runner(suffix: str = "tail") -> str:
            return "{0}:{1}:{2}".format(self.kind, prefix, suffix)

        return _runner


class CapabilityRiftJsonBench:
    """
    Real capability-room integration harness with a JSON-like request driver.

    Purpose:
        Build one reusable runtime stack for capability-room integration tests:
        Spellbook, root conduits, Nexus, Rift, `CapabilityRiftSpace`, and the
        shared command/workstation surfaces.
    """

    def __init__(self, *, frame_name: str, dynamic_frame: bool) -> None:
        """
        Initialize one capability-room integration harness.

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
        CommandSystem._aether = self.aether

        self.left_spellbook = Spellbook(
            aetheric_frame=frame_name,
            configuration=self._build_configuration(),
        )
        self.right_spellbook = Spellbook(
            aetheric_frame=frame_name,
            configuration=self._build_configuration(),
        )
        self.left_spell_id = self.left_spellbook.bind(
            spell=CapabilityBenchService,
            spellframe="CapabilityBench",
            binding_name="live_spell",
            existence=Existence.unique,
            permissions="create",
        )

        automatic = not self.dynamic_frame
        self.left_conduit = self.left_spellbook.conjure(
            name="left",
            automatic=automatic,
        )
        self.right_conduit = self.right_spellbook.conjure(
            name="right",
            automatic=automatic,
        )
        self.initial_lesser = self.left_conduit.create_lesser_conduit()
        self.live_spell_object = self.left_conduit.meld(spell=self.left_spell_id)

        self.nexus = self._build_nexus()
        self.rift = self._build_rift()
        self.space = self.rift.space
        if not isinstance(self.space, CapabilityRiftSpace):
            raise RuntimeError("Capability Rift bench did not create a capability room.")
        self.viewer = self.space.frame_viewer
        if self.viewer is None:
            raise RuntimeError("Capability Rift bench room has no attached viewer.")
        self.command = self.space.command_system
        self.workstation = self.space.workstation
        self.manifest = self._build_manifest()

    def cleanup(self) -> None:
        """
        Cleanup the harness-owned runtime objects.

        Returns:
            None.
        """
        for conduit in (
            self.initial_lesser,
            self.left_conduit,
            self.right_conduit,
        ):
            if conduit is not None and not conduit.cleaned:
                conduit.cleanup()
        for spellbook in (
            self.left_spellbook,
            self.right_spellbook,
        ):
            if spellbook is not None and not spellbook.cleaned:
                spellbook.cleanup()
        if self.rift is not None and not self.rift.cleaned:
            self.rift.cleanup()

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
                JSON payload containing one `turns` list.

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
            expect_error_type = turn.get("expect_error_type")
            surface_name = turn["surface"]
            method_name = turn["method"]
            args = self._resolve_turn_value(turn.get("args", []), saved_results)
            kwargs = self._resolve_turn_value(turn.get("kwargs", {}), saved_results)
            surface = self._resolve_surface(surface_name, kwargs)
            method = getattr(surface, method_name)
            try:
                result = method(*args, **kwargs)
            except Exception as exc:
                if expect_error_contains is None:
                    raise
                if expect_error_contains not in str(exc):
                    raise
                if expect_error_type is not None and type(exc).__name__ != expect_error_type:
                    raise
                result = {
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            else:
                if expect_error_contains is not None:
                    raise AssertionError(
                        "Expected error containing '{0}'.".format(
                            expect_error_contains
                        )
                    )
            if save_as is not None:
                saved_results[save_as] = result
        return saved_results

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
        configuration.with_nexus_frame_mode("indexed")
        nexus.enable(configuration)
        return nexus

    def _build_rift(self) -> Rift:
        """
        Build one targeted capability Rift for this harness.

        Returns:
            Rift: Targeted capability Rift.
        """
        configuration = self.nexus.create_rift_configuration().with_space_type(
            RiftSpaceType.capability
        )
        rift = self.nexus.create_rift(
            configuration=configuration,
            rift_name="{0}_capability_rift".format(self.frame_name),
        )
        rift.create_frame_link(self.frame_name)
        return rift

    def _build_manifest(self) -> Dict[str, object]:
        """
        Build one manifest of ids and names for request placeholders.

        Returns:
            Dict[str, object]: Harness manifest.
        """
        left_spell = self.left_conduit.get_spell_by_id(
            self.left_spell_id,
            self.frame_name,
        )
        return {
            "frame_name": self.frame_name,
            "frame_mode": "dynamic" if self.dynamic_frame else "automatic",
            "conduits": {
                "left": {
                    "id": self.left_conduit.id,
                    "name": self.left_conduit.name,
                },
                "right": {
                    "id": self.right_conduit.id,
                    "name": self.right_conduit.name,
                },
                "initial_lesser": {
                    "id": self.initial_lesser.id,
                },
            },
            "spell": {
                "spell_id": self.left_spell_id,
                "spell_index_id": left_spell.spell_index.id,
                "source_id": "{0}:{1}".format(
                    self.left_spellbook.id,
                    self.left_spell_id,
                ),
                "spell_name": left_spell.spell_name,
            },
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
        if surface_name == "cloud":
            frame_name = kwargs.pop("frame_name", None)
            return self.command.get_conduit_cloud(frame_name=frame_name)
        raise ValueError("Unsupported surface '{0}'.".format(surface_name))

    def _resolve_request_value(self, value: Any) -> Any:
        """
        Resolve manifest placeholders inside one request value.

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
        return value

    def _resolve_turn_value(
            self,
            value: Any,
            saved_results: Dict[str, Any],
    ) -> Any:
        """
        Resolve manifest and saved-turn placeholders inside one turn payload.

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

