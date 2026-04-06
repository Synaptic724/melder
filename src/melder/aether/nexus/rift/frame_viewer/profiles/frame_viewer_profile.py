from typing import Dict, Mapping, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewerProfile(Cleanable):
    """
    Purpose:
        Represent one reusable posture profile for `FrameViewer`.

    Contract:
        - Owns the viewer tool surface exposed to the agent.
        - Maps stable tool ids to host-side handler method names.
        - Does not redefine permissions.
        - Carries stable profile identity and version.

    Lifecycle:
        Cleanup is idempotent and clears owned metadata only.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_profile_id",
        "_name",
        "_version",
        "_tool_handler_names_by_name",
        "_default_grouping",
        "_default_detail_level",
    ]

    def __init__(
            self,
            name: str,
            *,
            version: str = "0.0.1",
            enabled_helpers: Optional[Sequence[str]] = None,
            tool_handler_names_by_name: Optional[Mapping[str, str]] = None,
            default_grouping: str = "frame",
            default_detail_level: str = "summary",
    ) -> None:
        """
        Initialize one frame-viewer profile.

        Args:
            name:
                Stable profile name.
            version:
                Profile version string.
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
        if enabled_helpers is not None and tool_handler_names_by_name is not None:
            raise ValueError(
                "enabled_helpers and tool_handler_names_by_name cannot both be provided."
            )
        self._profile_id: str = IDBuilder.create_id()
        self._name: str = name
        self._version: str = version
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

    @classmethod
    def create_general(cls) -> "FrameViewerProfile":
        """
        Create the seeded `general` frame-viewer profile.

        Returns:
            FrameViewerProfile: Seeded `general` frame-viewer profile.
        """
        return cls(
            "general",
            default_grouping="frame",
            default_detail_level="summary",
        )

    @property
    def name(self) -> str:
        self.check_cleaned()
        return self._name

    @property
    def version(self) -> str:
        self.check_cleaned()
        return self._version

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
        self.check_cleaned()
        return self._default_grouping

    @property
    def default_detail_level(self) -> str:
        self.check_cleaned()
        return self._default_detail_level

    def list_tool_names(self) -> Tuple[str, ...]:
        """
        Return the tool ids exposed by this profile.

        Returns:
            Tuple[str, ...]: Exposed tool ids.
        """
        self.check_cleaned()
        return self.enabled_helpers

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

    def clone(self) -> "FrameViewerProfile":
        """
        Return a detached copy of this viewer profile.

        Returns:
            FrameViewerProfile: Detached profile copy.
        """
        self.check_cleaned()
        return FrameViewerProfile(
            self._name,
            version=self._version,
            tool_handler_names_by_name=self._tool_handler_names_by_name,
            default_grouping=self._default_grouping,
            default_detail_level=self._default_detail_level,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the frame-viewer profile.

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
        self._version = None
        self._name = None
        self._profile_id = None
