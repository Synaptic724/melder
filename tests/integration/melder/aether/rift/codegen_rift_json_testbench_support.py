import json
from typing import Any, Dict, List, Optional

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace
from melder.aether.spellbook.spellbook import Spellbook


class CodegenRiftJsonBench:
    """
    Real codegen-room integration harness with a JSON-like request driver.

    Purpose:
        Build one reusable runtime stack for codegen-room integration tests:
        Nexus, Rift, `CodegenRiftSpace`, live managed frames, the room viewer,
        the room workstation, the codegen command surface, and a small hook
        recorder so turn-script scenarios can exercise codegen the way an agent
        would actually use it.
    """

    def __init__(self) -> None:
        """
        Initialize one codegen-room integration harness.

        Returns:
            None.
        """
        self.aether = Aether()
        Spellbook._aether = self.aether
        Conduit._aether = self.aether
        self.nexus = self._build_nexus()
        self.rift = self._build_rift()
        self.ops_root_conduit = self.rift.create_nexus_frame(frame_name="ops")
        self.finance_root_conduit = self.rift.create_nexus_frame(
            frame_name="finance"
        )
        self.rift.create_frame_link("ops")
        self.space = self.rift.space
        if not isinstance(self.space, CodegenRiftSpace):
            raise RuntimeError("Codegen Rift bench did not create a codegen room.")
        self.viewer = self.space.frame_viewer
        if self.viewer is None:
            raise RuntimeError("Codegen Rift bench room has no attached viewer.")
        self.command = self.space.command_system
        self.workstation = self.space.workstation
        self.codegen_system = self.space.codegen_system
        self._hook_events: List[str] = []
        self.manifest = self._build_manifest()

    def cleanup(self) -> None:
        """
        Cleanup the harness-owned runtime objects.

        Returns:
            None.
        """
        for conduit in (
            self.ops_root_conduit,
            self.finance_root_conduit,
        ):
            if conduit is not None and not conduit.cleaned:
                conduit.cleanup()
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
        surface = self._resolve_surface(surface_name)
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
            surface = self._resolve_surface(surface_name)
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

    def set_codegen_profile(
            self,
            profile_name: str,
            *,
            precision_profile_name: Optional[str] = None,
            frame_name: str = "ops",
    ) -> None:
        """
        Install one codegen profile selection for the requested frame.

        Args:
            profile_name:
                Base codegen profile name.
            precision_profile_name:
                Optional precision profile name.
            frame_name:
                Target frame name.

        Returns:
            None.
        """
        container = self.nexus._frame_acl_manager._get_required_frame_acl_container(
            frame_name
        )
        contract_name = (
            frame_name
            if frame_name in self.rift.list_assigned_frame_names()
            else "default"
        )
        builder = container.frame_acl_builder.begin_codegen_change(
            contract_name=contract_name,
            reason="codegen_json_bench",
        )
        builder.use_profile(profile_name)
        if precision_profile_name is not None:
            builder.use_precision_profile(precision_profile_name)
        builder.commit_change()
        if frame_name in self.rift.list_assigned_frame_names():
            self.rift.refresh_runtime_projections(frame_names=(frame_name,))

    def register_category_pre_hook(self, category: str, tag: str) -> str:
        """
        Register one category pre-hook that records a tag.
        """
        return self.space.register_category_pre_hook(
            category,
            lambda: self._hook_events.append(tag),
        )

    def register_category_post_hook(self, category: str, tag: str) -> str:
        """
        Register one category post-hook that records a tag.
        """
        return self.space.register_category_post_hook(
            category,
            lambda: self._hook_events.append(tag),
        )

    def register_action_pre_hook(
            self,
            category: str,
            action_name: str,
            tag: str,
    ) -> str:
        """
        Register one action pre-hook that records a tag.
        """
        return self.space.register_action_pre_hook(
            category,
            action_name,
            lambda: self._hook_events.append(tag),
        )

    def register_action_post_hook(
            self,
            category: str,
            action_name: str,
            tag: str,
    ) -> str:
        """
        Register one action post-hook that records a tag.
        """
        return self.space.register_action_post_hook(
            category,
            action_name,
            lambda: self._hook_events.append(tag),
        )

    def list_hook_events(self) -> List[str]:
        """
        Return the recorded hook-event tags.

        Returns:
            List[str]: Recorded hook tags in registration/execution order.
        """
        return list(self._hook_events)

    def clear_hook_events(self) -> None:
        """
        Clear the recorded hook-event tags.

        Returns:
            None.
        """
        self._hook_events.clear()

    def _build_nexus(self) -> Nexus:
        """
        Build one enabled Nexus for this harness.

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
        configuration.with_nexus_frame_mode("indexed")
        configuration.with_max_nexus_frame_count(8)
        nexus.enable(configuration)
        return nexus

    def _build_rift(self) -> Rift:
        """
        Build one codegen Rift for this harness.

        Returns:
            Rift: Live codegen Rift.
        """
        configuration = self.nexus.create_rift_configuration().with_space_type(
            RiftSpaceType.codegen
        )
        return self.nexus.create_rift(
            configuration=configuration,
            rift_name="codegen_json_bench",
        )

    def _build_manifest(self) -> Dict[str, object]:
        """
        Build one manifest of frame and conduit placeholders for request scripts.

        Returns:
            Dict[str, object]: Harness manifest.
        """
        return {
            "frames": {
                "ops": {
                    "frame_name": "ops",
                },
                "finance": {
                    "frame_name": "finance",
                },
            },
            "conduits": {
                "ops_root": {
                    "id": self.ops_root_conduit.id,
                    "name": self.ops_root_conduit.name,
                    "frame_name": self.ops_root_conduit._aetheric_frame,
                },
                "finance_root": {
                    "id": self.finance_root_conduit.id,
                    "name": self.finance_root_conduit.name,
                    "frame_name": self.finance_root_conduit._aetheric_frame,
                },
            },
        }

    def _resolve_surface(self, surface_name: str) -> Any:
        """
        Resolve one dispatch surface name to a live API object.

        Args:
            surface_name:
                Requested surface name.

        Returns:
            Any: Live dispatch surface.
        """
        if surface_name == "bench":
            return self
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
