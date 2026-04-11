from typing import Dict, Mapping, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.class_surface_ast_describer import (
    ClassSurfaceAstDescriber,
)
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewerProfile(Cleanable):
    """
    Purpose:
        Represent one reusable agent-facing posture profile for `FrameViewer`.

    Contract:
        - Owns the stable tool-routing metadata exposed to the agent.
        - Maps public tool ids to host-side handler method names without
          redefining frame permissions or ACL policy.
        - Starts life as an unbound reusable template and may later be bound by
          reference to one frame's descriptor + ACL state.
        - Carries stable profile identity, version, and compatibility
          requirements across clone and bind operations.

    Lifecycle:
        Cleanup is idempotent, clears only owned profile metadata, and never
        disposes bound descriptor or ACL objects because they are not owned here.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Reusable viewer profile template that defines the "
        "agent-facing method surface and binds that surface to one frame's "
        "descriptor and ACL state."
    )
    __slots__ = Cleanable.__slots__ + [
        "_profile_id",
        "_name",
        "_version",
        "_required_nexus_label",
        "_required_nexus_version",
        "_required_acl_view_profile_name",
        "_required_acl_view_profile_version",
        "_tool_handler_names_by_name",
        "_default_grouping",
        "_default_detail_level",
        "_bound_frame_name",
        "_frame_descriptor",
        "_frame_acl_configuration",
        "_compiled_access_surface",
    ]

    def __init__(
            self,
            name: str,
            *,
            version: str = "0.0.1",
            required_nexus_label: Optional[str] = None,
            required_nexus_version: Optional[str] = None,
            required_acl_view_profile_name: Optional[str] = None,
            required_acl_view_profile_version: Optional[str] = None,
            enabled_helpers: Optional[Sequence[str]] = None,
            tool_handler_names_by_name: Optional[Mapping[str, str]] = None,
            default_grouping: str = "frame",
            default_detail_level: str = "summary",
    ) -> None:
        """
        Initialize one reusable frame-viewer profile template.

        Purpose:
            Capture the stable tool-routing and compatibility contract for one
            named viewer posture before it is cloned or bound to a specific
            frame.

        Contract:
            - Construction always produces an unbound template; frame-specific
              references are attached later through `bind_to_frame(...)`.
            - Accepts either the `enabled_helpers` shorthand or an explicit
              `tool_handler_names_by_name` mapping, but never both.
            - Normalizes the tool map into profile-owned metadata that later
              clones and bindings reuse.

        Args:
            name:
                Stable profile name.
            version:
                Profile version string.
            required_nexus_label:
                Optional required Nexus dataset label for frame binding.
            required_nexus_version:
                Optional required Nexus dataset version for frame binding.
            required_acl_view_profile_name:
                Optional required ACL view profile name for frame binding.
            required_acl_view_profile_version:
                Optional required ACL view profile version for frame binding.
            enabled_helpers:
                Backward-compatible shorthand for a tool surface where each
                tool id maps directly to the same-named host handler.
            tool_handler_names_by_name:
                Optional explicit tool-id -> host handler-name mapping for this
                viewer posture.
            default_grouping:
                Default grouping mode.
            default_detail_level:
                Default detail posture.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        if not default_grouping:
            raise ValueError("default_grouping cannot be empty.")
        if not default_detail_level:
            raise ValueError("default_detail_level cannot be empty.")
        if (
                required_nexus_version is not None
                and required_nexus_label is None
        ):
            raise ValueError(
                "required_nexus_version requires required_nexus_label."
            )
        if (
                required_acl_view_profile_version is not None
                and required_acl_view_profile_name is None
        ):
            raise ValueError(
                "required_acl_view_profile_version requires required_acl_view_profile_name."
            )
        if enabled_helpers is not None and tool_handler_names_by_name is not None:
            raise ValueError(
                "enabled_helpers and tool_handler_names_by_name cannot both be provided."
            )
        self._profile_id: str = IDBuilder.create_id()
        self._name: str = name
        self._version: str = version
        self._required_nexus_label: Optional[str] = required_nexus_label
        self._required_nexus_version: Optional[str] = required_nexus_version
        self._required_acl_view_profile_name: Optional[str] = (
            required_acl_view_profile_name
        )
        self._required_acl_view_profile_version: Optional[str] = (
            required_acl_view_profile_version
        )
        if tool_handler_names_by_name is not None:
            if len(tool_handler_names_by_name) == 0:
                raise ValueError("tool_handler_names_by_name cannot be empty.")
            normalized_tool_handler_names_by_name: Dict[str, str] = {}
            for tool_name, handler_name in tool_handler_names_by_name.items():
                if not tool_name:
                    raise ValueError("tool_handler_names_by_name cannot contain empty tool names.")
                if not handler_name:
                    raise ValueError(
                        "tool_handler_names_by_name cannot contain empty handler names."
                    )
                normalized_tool_handler_names_by_name[tool_name] = handler_name
            self._tool_handler_names_by_name: Dict[str, str] = (
                normalized_tool_handler_names_by_name
            )
        else:
            normalized_enabled_helpers = tuple(
                enabled_helpers or (
                    "list_frame_names",
                    "list_links",
                    "list_links_by_kind",
                    "list_links_grouped_by_frame",
                    "list_links_grouped_by_kind",
                    "list_display_names",
                    "count_links",
                    "describe_frame",
                    "describe_frames",
                    "get_required_link_by_source",
                )
            )
            if len(normalized_enabled_helpers) == 0:
                raise ValueError("enabled_helpers cannot be empty.")
            self._tool_handler_names_by_name = {
                helper_name: helper_name
                for helper_name in normalized_enabled_helpers
            }
        self._default_grouping: str = default_grouping
        self._default_detail_level: str = default_detail_level
        self._bound_frame_name: Optional[str] = None
        self._frame_descriptor: Optional[FrameDescriptor] = None
        self._frame_acl_configuration: Optional[FrameACLConfiguration] = None
        self._compiled_access_surface: Optional[CompiledFrameACLAccessSurface] = None

    @classmethod
    def create_general(cls) -> "FrameViewerProfile":
        """
        Return the canonical unbound `general` frame-viewer profile template.

        Contract:
            - Imports the `general` profile factory lazily so this base module
              does not eagerly depend on the helper-profile implementation.
            - Returns a fresh reusable template, not a frame-bound instance.

        Returns:
            FrameViewerProfile: Seeded `general` frame-viewer profile.
        """
        from melder.aether.nexus.rift.frame_viewer.profiles.general.general_profile import (
            create_general_profile,
        )

        return create_general_profile()

    @property
    def name(self) -> str:
        """
        Return the stable public name for this profile template.

        Returns:
            str: Profile name used for registry lookup and compatibility checks.
        """
        self.check_cleaned()
        return self._name

    @property
    def version(self) -> str:
        """
        Return the profile version carried across clones and bindings.

        Returns:
            str: Stable profile version string.
        """
        self.check_cleaned()
        return self._version

    @property
    def required_acl_view_profile_name(self) -> Optional[str]:
        """
        Return the optional ACL view profile name required by this profile.

        Returns:
            Optional[str]: Required ACL view profile name when constrained.
        """
        self.check_cleaned()
        return self._required_acl_view_profile_name

    @property
    def required_nexus_label(self) -> Optional[str]:
        """
        Return the optional Nexus dataset label required by this profile.

        Returns:
            Optional[str]: Required Nexus dataset label when constrained.
        """
        self.check_cleaned()
        return self._required_nexus_label

    @property
    def required_nexus_version(self) -> Optional[str]:
        """
        Return the optional Nexus dataset version required by this profile.

        Returns:
            Optional[str]: Required Nexus dataset version when constrained.
        """
        self.check_cleaned()
        return self._required_nexus_version

    @property
    def required_acl_view_profile_version(self) -> Optional[str]:
        """
        Return the optional ACL view profile version required by this profile.

        Returns:
            Optional[str]: Required ACL view profile version when constrained.
        """
        self.check_cleaned()
        return self._required_acl_view_profile_version

    @property
    def enabled_helpers(self) -> Tuple[str, ...]:
        """
        Return the enabled tool ids exposed by this profile.

        Returns:
            Tuple[str, ...]: Enabled tool ids.
        """
        self.check_cleaned()
        return tuple(self._tool_handler_names_by_name.keys())

    @property
    def tool_handler_names_by_name(self) -> Dict[str, str]:
        """
        Return the tool-id -> host handler-name mapping.

        Returns:
            Dict[str, str]: Tool surface mapping for this profile.
        """
        self.check_cleaned()
        return dict(self._tool_handler_names_by_name)

    @property
    def default_grouping(self) -> str:
        """
        Return the default grouping posture exposed to viewer callers.

        Returns:
            str: Default grouping mode suggested by this profile.
        """
        self.check_cleaned()
        return self._default_grouping

    @property
    def default_detail_level(self) -> str:
        """
        Return the default detail posture exposed to viewer callers.

        Returns:
            str: Default detail level suggested by this profile.
        """
        self.check_cleaned()
        return self._default_detail_level

    @property
    def bound_frame_name(self) -> Optional[str]:
        """
        Return the currently bound frame name when this profile is frame-bound.

        Returns:
            Optional[str]: Bound frame name.
        """
        self.check_cleaned()
        return self._bound_frame_name

    @property
    def frame_descriptor(self) -> Optional[FrameDescriptor]:
        """
        Return the bound frame descriptor reference when this profile is bound.

        Returns:
            Optional[FrameDescriptor]: Bound frame descriptor.
        """
        self.check_cleaned()
        return self._frame_descriptor

    @property
    def frame_acl_configuration(self) -> Optional[FrameACLConfiguration]:
        """
        Return the bound frame ACL configuration when this profile is bound.

        Returns:
            Optional[FrameACLConfiguration]: Bound frame ACL configuration.
        """
        self.check_cleaned()
        return self._frame_acl_configuration

    @property
    def compiled_access_surface(self) -> Optional[CompiledFrameACLAccessSurface]:
        """
        Return the bound compiled ACL surface when this profile is bound.

        Returns:
            Optional[CompiledFrameACLAccessSurface]: Bound compiled ACL surface.
        """
        self.check_cleaned()
        return self._compiled_access_surface

    @property
    def is_bound(self) -> bool:
        """
        Return whether this profile is currently bound to one frame.

        Returns:
            bool: True when frame-bound.
        """
        self.check_cleaned()
        return self._bound_frame_name is not None

    def list_tool_names(self) -> Tuple[str, ...]:
        """
        Return a snapshot of the tool ids exposed by this profile.

        Returns:
            Tuple[str, ...]: Public tool ids in deterministic tuple form.
        """
        self.check_cleaned()
        return self.enabled_helpers

    def list_class_method_names_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON list of this profile class's method names.

        Purpose:
            Expose the profile's own source-defined public method surface for
            agent consumption without walking runtime state or method bodies.

        Args:
            include_private:
                Whether `_private` methods should be included.
            include_dunder:
                Whether `__dunder__` methods should be included.

        Returns:
            str: Minified JSON list of source-defined profile method names.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.list_class_method_names_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_agent_purpose_json(self) -> str:
        """
        Return the minified JSON agent-purpose surface for this profile.

        Returns:
            str: Minified JSON agent-purpose surface for the profile.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_purpose_json(self)

    def describe_class_surface_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON description of this profile class surface.

        Purpose:
            Expose the profile's source-defined class surface, including method
            signatures, properties, and docstrings, for direct agent use.

        Args:
            include_private:
                Whether `_private` members should be included.
            include_dunder:
                Whether `__dunder__` members should be included.

        Returns:
            str: Minified JSON description of the profile class surface.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_class_surface_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def list_helper_object_names(self) -> Tuple[str, ...]:
        """
        Return the dynamic helper-object names exposed by this profile.

        Purpose:
            Provide one dynamic discovery seam for any composed helper objects
            whose public property names follow the `view_*` convention.

        Contract:
            - Uses runtime only to discover helper-object property values.
            - Includes only public names that start with `view_`.
            - Includes only bound non-None values that satisfy `Cleanable`.

        Returns:
            Tuple[str, ...]: Sorted helper-object property names.
        """
        self.check_cleaned()
        helper_object_names = []
        for current_name in dir(type(self)):
            if not current_name.startswith("view_"):
                continue
            current_value = getattr(self, current_name, None)
            if current_value is None:
                continue
            if not isinstance(current_value, Cleanable):
                continue
            helper_object_names.append(current_name)
        return tuple(sorted(helper_object_names))

    def describe_helper_class_surfaces_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return minified JSON descriptions for each composed helper class.

        Purpose:
            Expose the AST-described helper-object class surfaces for any
            `view_*` helper objects currently composed into the profile.

        Args:
            include_private:
                Whether `_private` helper members should be included.
            include_dunder:
                Whether `__dunder__` helper members should be included.

        Returns:
            str: Minified JSON mapping of helper-object names to class-surface
            descriptions.
        """
        self.check_cleaned()
        helper_surfaces = {
            helper_object_name: ClassSurfaceAstDescriber.describe_class_surface_ast_json(
                getattr(self, helper_object_name),
                include_private=include_private,
                include_dunder=include_dunder,
            )
            for helper_object_name in self.list_helper_object_names()
        }
        return "{" + ",".join(
            "\"{0}\":{1}".format(helper_object_name, helper_surface_json)
            for helper_object_name, helper_surface_json in helper_surfaces.items()
        ) + "}"

    def has_tool(self, tool_name: str) -> bool:
        """
        Return whether one tool id is exposed by this profile.

        Args:
            tool_name:
                Tool id to inspect.

        Returns:
            bool: True when the tool is exposed.
        """
        self.check_cleaned()
        if not tool_name:
            raise ValueError("tool_name cannot be empty.")
        return tool_name in self._tool_handler_names_by_name

    def get_required_tool_handler_name(self, tool_name: str) -> str:
        """
        Return the host handler name for one exposed tool id or raise.

        Args:
            tool_name:
                Tool id to resolve.

        Returns:
            str: Host handler method name.
        """
        self.check_cleaned()
        if not tool_name:
            raise ValueError("tool_name cannot be empty.")
        try:
            return self._tool_handler_names_by_name[tool_name]
        except KeyError as exc:
            raise ValueError(
                "FrameViewerProfile tool '{0}' is not exposed by profile '{1}'.".format(
                    tool_name,
                    self._name,
                )
            ) from exc

    def bind_to_frame(
            self,
            *,
            frame_name: str,
            frame_descriptor: FrameDescriptor,
            frame_acl_configuration: FrameACLConfiguration,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> None:
        """
        Bind this profile by reference to one frame's descriptor + ACL state.

        Purpose:
            Turn a reusable profile template into a frame-scoped viewer posture
            after verifying that the descriptor, ACL configuration, compiled ACL
            surface, and optional Nexus/profile requirements all agree.

        Contract:
            - Stores the bound objects by reference; it does not clone or own
              them.
            - Fails fast if the frame names, configuration ids, view-profile
              versions, or required Nexus contract do not align.
            - Leaves prior state untouched until all compatibility checks pass.

        Args:
            frame_name:
                Target frame name this profile is being bound to.
            frame_descriptor:
                Descriptor truth for the frame.
            frame_acl_configuration:
                Current ACL configuration for the frame.
            compiled_access_surface:
                Compiled ACL surface for the same frame/configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(frame_descriptor, FrameDescriptor):
            raise TypeError("frame_descriptor must be a FrameDescriptor.")
        if not isinstance(frame_acl_configuration, FrameACLConfiguration):
            raise TypeError(
                "frame_acl_configuration must be a FrameACLConfiguration."
            )
        if not isinstance(
                compiled_access_surface,
                CompiledFrameACLAccessSurface,
        ):
            raise TypeError(
                "compiled_access_surface must be a CompiledFrameACLAccessSurface."
            )
        if frame_descriptor.frame_name != frame_name:
            raise ValueError(
                "FrameDescriptor targets frame '{0}', expected '{1}'.".format(
                    frame_descriptor.frame_name,
                    frame_name,
                )
            )
        if frame_acl_configuration.frame_name != frame_name:
            raise ValueError(
                "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                    frame_acl_configuration.frame_name,
                    frame_name,
                )
            )
        if compiled_access_surface.frame_name != frame_name:
            raise ValueError(
                "CompiledFrameACLAccessSurface targets frame '{0}', expected '{1}'.".format(
                    compiled_access_surface.frame_name,
                    frame_name,
                )
            )
        if (
                compiled_access_surface.configuration_id
                != frame_acl_configuration.configuration_id
        ):
            raise ValueError(
                "CompiledFrameACLAccessSurface configuration_id '{0}' does not match FrameACLConfiguration '{1}'.".format(
                    compiled_access_surface.configuration_id,
                    frame_acl_configuration.configuration_id,
                )
            )
        required_nexus_label = (
            self._required_nexus_label
            or frame_acl_configuration.view_configuration.required_nexus_label
        )
        required_nexus_version = (
            self._required_nexus_version
            or frame_acl_configuration.view_configuration.required_nexus_version
        )
        self._assert_descriptor_records_match_nexus_contract(
            frame_descriptor=frame_descriptor,
            required_nexus_label=required_nexus_label,
            required_nexus_version=required_nexus_version,
        )
        bound_view_configuration = frame_acl_configuration.view_configuration
        if (
                compiled_access_surface.view_profile_name
                != bound_view_configuration.profile_name
                or compiled_access_surface.view_profile_version
                != bound_view_configuration.profile_version
        ):
            raise ValueError(
                "Compiled ACL view profile '{0}:{1}' does not match bound FrameACLViewConfiguration '{2}:{3}'.".format(
                    compiled_access_surface.view_profile_name,
                    compiled_access_surface.view_profile_version,
                    bound_view_configuration.profile_name,
                    bound_view_configuration.profile_version,
                )
            )
        if self._required_acl_view_profile_name is not None:
            required_version = (
                self._required_acl_view_profile_version
                or compiled_access_surface.view_profile_version
            )
            if (
                    compiled_access_surface.view_profile_name
                    != self._required_acl_view_profile_name
                    or compiled_access_surface.view_profile_version
                    != required_version
            ):
                raise ValueError(
                    "FrameViewerProfile '{0}' requires ACL view profile '{1}:{2}', got '{3}:{4}'.".format(
                        self._name,
                        self._required_acl_view_profile_name,
                        required_version,
                        compiled_access_surface.view_profile_name,
                        compiled_access_surface.view_profile_version,
                    )
                )
        self._bound_frame_name = frame_name
        self._frame_descriptor = frame_descriptor
        self._frame_acl_configuration = frame_acl_configuration
        self._compiled_access_surface = compiled_access_surface

    def clone_bound_to_frame(
            self,
            *,
            frame_name: str,
            frame_descriptor: FrameDescriptor,
            frame_acl_configuration: FrameACLConfiguration,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> "FrameViewerProfile":
        """
        Return a detached profile copy already bound to one frame by reference.

        Contract:
            - Clones the reusable template first.
            - Applies the normal `bind_to_frame(...)` contract to the clone.
            - Leaves the source profile unmodified and still reusable.

        Args:
            frame_name:
                Bound frame name.
            frame_descriptor:
                Descriptor truth for the frame.
            frame_acl_configuration:
                Current ACL configuration for the frame.
            compiled_access_surface:
                Compiled ACL surface for the same frame/configuration.

        Returns:
            FrameViewerProfile: Detached bound profile copy.
        """
        cloned_profile = self.clone()
        cloned_profile.bind_to_frame(
            frame_name=frame_name,
            frame_descriptor=frame_descriptor,
            frame_acl_configuration=frame_acl_configuration,
            compiled_access_surface=compiled_access_surface,
        )
        return cloned_profile

    def clone(self) -> "FrameViewerProfile":
        """
        Return a detached unbound copy of this viewer profile template.

        Returns:
            FrameViewerProfile: Unbound copy that preserves the same tool
            routing and compatibility requirements.
        """
        self.check_cleaned()
        return FrameViewerProfile(
            self._name,
            version=self._version,
            required_nexus_label=self._required_nexus_label,
            required_nexus_version=self._required_nexus_version,
            required_acl_view_profile_name=self._required_acl_view_profile_name,
            required_acl_view_profile_version=self._required_acl_view_profile_version,
            tool_handler_names_by_name=self._tool_handler_names_by_name,
            default_grouping=self._default_grouping,
            default_detail_level=self._default_detail_level,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the profile-owned template and binding metadata.

        Contract:
            - Clears only data owned by the profile.
            - Never cleans the bound descriptor, ACL configuration, or compiled
              access surface because those objects are borrowed references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._tool_handler_names_by_name.clear()
        self._tool_handler_names_by_name = None
        self._default_grouping = None
        self._default_detail_level = None
        self._required_nexus_label = None
        self._required_nexus_version = None
        self._required_acl_view_profile_name = None
        self._required_acl_view_profile_version = None
        self._bound_frame_name = None
        self._frame_descriptor = None
        self._frame_acl_configuration = None
        self._compiled_access_surface = None
        self._version = None
        self._name = None
        self._profile_id = None

    @staticmethod
    def _assert_descriptor_records_match_nexus_contract(
            *,
            frame_descriptor: FrameDescriptor,
            required_nexus_label: str,
            required_nexus_version: str,
    ) -> None:
        """
        Validate that all bound descriptor records match one Nexus contract.

        Contract:
            - Uses the frame overview plus every conduit and spell record in the
              descriptor.
            - Raises as soon as one record advertises a different Nexus label or
              version than the profile requires.

        Args:
            frame_descriptor:
                Descriptor whose records should be inspected.
            required_nexus_label:
                Required record/event Nexus label.
            required_nexus_version:
                Required record/event Nexus version.

        Returns:
            None.
        """
        frame_overview = frame_descriptor.frame_overview
        if frame_overview is None:
            raise ValueError(
                "FrameDescriptor for frame '{0}' has no frame_overview for Nexus contract validation.".format(
                    frame_descriptor.frame_name
                )
            )
        FrameViewerProfile._assert_record_nexus_contract(
            record_label="frame record",
            actual_nexus_label=frame_overview.nexus_label,
            actual_nexus_version=frame_overview.nexus_version,
            required_nexus_label=required_nexus_label,
            required_nexus_version=required_nexus_version,
            frame_name=frame_descriptor.frame_name,
        )
        for conduit_record in frame_descriptor.conduit_records_by_id.values():
            FrameViewerProfile._assert_record_nexus_contract(
                record_label="conduit record",
                actual_nexus_label=conduit_record.nexus_label,
                actual_nexus_version=conduit_record.nexus_version,
                required_nexus_label=required_nexus_label,
                required_nexus_version=required_nexus_version,
                frame_name=frame_descriptor.frame_name,
            )
        for spell_record in frame_descriptor.spell_records_by_key.values():
            FrameViewerProfile._assert_record_nexus_contract(
                record_label="spell record",
                actual_nexus_label=spell_record.nexus_label,
                actual_nexus_version=spell_record.nexus_version,
                required_nexus_label=required_nexus_label,
                required_nexus_version=required_nexus_version,
                frame_name=frame_descriptor.frame_name,
            )

    @staticmethod
    def _assert_record_nexus_contract(
            *,
            record_label: str,
            actual_nexus_label: str,
            actual_nexus_version: str,
            required_nexus_label: str,
            required_nexus_version: str,
            frame_name: str,
    ) -> None:
        """
        Fail when one bound record does not match the required Nexus contract.

        Args:
            record_label:
                Human-readable record label.
            actual_nexus_label:
                Actual bound record Nexus label.
            actual_nexus_version:
                Actual bound record Nexus version.
            required_nexus_label:
                Required Nexus label.
            required_nexus_version:
                Required Nexus version.
            frame_name:
                Owning frame name.

        Returns:
            None.
        """
        if (
                actual_nexus_label != required_nexus_label
                or actual_nexus_version != required_nexus_version
        ):
            raise ValueError(
                "FrameViewerProfile bound {0} Nexus contract '{1}:{2}' does not match required '{3}:{4}' for frame '{5}'.".format(
                    record_label,
                    actual_nexus_label,
                    actual_nexus_version,
                    required_nexus_label,
                    required_nexus_version,
                    frame_name,
                )
            )
