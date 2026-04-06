import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


def _parse_json_configuration_string(
        json_configuration_string: str,
) -> Dict[str, Any]:
    """
    Parse one JSON configuration string into a dictionary.

    Args:
        json_configuration_string:
            JSON configuration string to parse.

    Returns:
        Dict[str, Any]: Parsed JSON payload dictionary.
    """
    if not isinstance(json_configuration_string, str):
        raise TypeError("json_configuration_string must be a string.")
    try:
        parsed_payload = json.loads(json_configuration_string)
    except json.JSONDecodeError as exc:
        raise ValueError("json_configuration_string must be valid JSON.") from exc
    if not isinstance(parsed_payload, dict):
        raise ValueError("json_configuration_string must decode to a JSON object.")
    return parsed_payload


class FrameACLConfiguration(Cleanable):
    """
    Purpose:
        Represent one frame-scoped typed ACL configuration node owned by a
        `FrameACLConfigurationChain`.

    Contract:
        - Carries stable node identity plus linked-history metadata.
        - Owns typed view and codegen child configuration objects.
        - May exist as an unlocked draft while being prepared by a builder or
          chain-copy operation.
        - Must be locked before a chain may commit and own it.

    Lifecycle:
        Cleanup is idempotent and clears all node metadata and owned child
        configuration objects.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_configuration_id",
        "_frame_name",
        "_source_configuration_id",
        "_previous_configuration_id",
        "_created_at",
        "_reason",
        "_locked",
        "_view_configuration",
        "_codegen_configuration",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            view_configuration: FrameACLViewConfiguration,
            codegen_configuration: FrameACLCodegenConfiguration,
            source_configuration_id: Optional[str],
            previous_configuration_id: Optional[str],
            reason: str,
            locked: bool,
    ) -> None:
        """
        Initialize one frame-scoped typed ACL configuration node.

        Args:
            frame_name:
                Stable frame name that owns this configuration node.
            view_configuration:
                Typed applied view-side configuration object.
            codegen_configuration:
                Typed applied codegen-side configuration object.
            source_configuration_id:
                Source configuration id when this node was copied from another
                node; otherwise None.
            previous_configuration_id:
                Previous chain node id when already known; otherwise None.
            reason:
                Human-readable creation reason recorded with the node.
            locked:
                True when the node starts finalized and safe for chain
                ownership.

        Returns:
            None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(view_configuration, FrameACLViewConfiguration):
            raise TypeError(
                "view_configuration must be a FrameACLViewConfiguration."
            )
        if not isinstance(codegen_configuration, FrameACLCodegenConfiguration):
            raise TypeError(
                "codegen_configuration must be a FrameACLCodegenConfiguration."
            )
        if not isinstance(reason, str) or not reason:
            raise ValueError("reason cannot be empty.")
        if not isinstance(locked, bool):
            raise TypeError("locked must be a bool.")
        self._id: str = IDBuilder.create_id()
        self._configuration_id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._source_configuration_id: Optional[str] = source_configuration_id
        self._previous_configuration_id: Optional[str] = previous_configuration_id
        self._created_at: str = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._reason: str = reason
        self._locked: bool = locked
        self._view_configuration: FrameACLViewConfiguration = view_configuration
        self._codegen_configuration: FrameACLCodegenConfiguration = (
            codegen_configuration
        )

    @classmethod
    def create_default(
            cls,
            frame_name: str,
    ) -> "FrameACLConfiguration":
        """
        Create the default locked ACL configuration for a frame.

        Args:
            frame_name:
                Stable frame name that will own the default node.

        Returns:
            FrameACLConfiguration: Default locked configuration node.
        """
        return cls(
            frame_name=frame_name,
            view_configuration=FrameACLViewConfiguration.from_profile(
                FrameACLViewProfile.create_default()
            ),
            codegen_configuration=FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_default()
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="default",
            locked=True,
        )

    @classmethod
    def from_json_configuration_string(
            cls,
            *,
            frame_name: str,
            json_configuration_string: str,
            source_configuration_id: Optional[str],
            previous_configuration_id: Optional[str],
            reason: str,
            locked: bool,
    ) -> "FrameACLConfiguration":
        """
        Build one ACL configuration node from a JSON payload string.

        Args:
            frame_name:
                Owning frame name.
            json_configuration_string:
                JSON payload string to parse and normalize.
            source_configuration_id:
                Source configuration id when the new node is derived from an
                older node; otherwise None.
            previous_configuration_id:
                Previous chain node id when already known; otherwise None.
            reason:
                Human-readable creation reason recorded with the new node.
            locked:
                True when the new node should start finalized.

        Returns:
            FrameACLConfiguration: Typed configuration node reconstructed from
            JSON.
        """
        parsed_payload = _parse_json_configuration_string(
            json_configuration_string
        )
        return cls(
            frame_name=frame_name,
            view_configuration=FrameACLViewConfiguration.from_json_dict(
                parsed_payload.get("view_configuration", {})
            ),
            codegen_configuration=FrameACLCodegenConfiguration.from_json_dict(
                parsed_payload.get("codegen_configuration", {})
            ),
            source_configuration_id=source_configuration_id,
            previous_configuration_id=previous_configuration_id,
            reason=reason,
            locked=locked,
        )

    @classmethod
    def create_new_from_acl_configuration(
            cls,
            source_configuration: "FrameACLConfiguration",
            *,
            reason: str,
    ) -> "FrameACLConfiguration":
        """
        Create a new draft configuration node from an existing configuration.

        Args:
            source_configuration:
                Existing source configuration node to copy from.
            reason:
                Human-readable creation reason recorded with the new draft.

        Returns:
            FrameACLConfiguration: New unlocked draft configuration node.
        """
        if not isinstance(source_configuration, FrameACLConfiguration):
            raise TypeError(
                "source_configuration must be a FrameACLConfiguration."
            )
        return cls(
            frame_name=source_configuration.frame_name,
            view_configuration=source_configuration.view_configuration.clone(),
            codegen_configuration=source_configuration.codegen_configuration.clone(),
            source_configuration_id=source_configuration.configuration_id,
            previous_configuration_id=None,
            reason=reason,
            locked=False,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the configuration node.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._view_configuration.cleanup()
        self._codegen_configuration.cleanup()
        self._configuration_id = None
        self._frame_name = None
        self._source_configuration_id = None
        self._previous_configuration_id = None
        self._created_at = None
        self._reason = None
        self._locked = None
        self._view_configuration = None
        self._codegen_configuration = None

    @property
    def configuration_id(self) -> str:
        self.check_cleaned()
        return self._configuration_id

    @property
    def frame_name(self) -> str:
        self.check_cleaned()
        return self._frame_name

    @property
    def source_configuration_id(self) -> Optional[str]:
        self.check_cleaned()
        return self._source_configuration_id

    @property
    def previous_configuration_id(self) -> Optional[str]:
        self.check_cleaned()
        return self._previous_configuration_id

    @property
    def created_at(self) -> str:
        self.check_cleaned()
        return self._created_at

    @property
    def reason(self) -> str:
        self.check_cleaned()
        return self._reason

    @property
    def locked(self) -> bool:
        self.check_cleaned()
        return self._locked

    @property
    def view_configuration(self) -> FrameACLViewConfiguration:
        self.check_cleaned()
        return self._view_configuration

    @property
    def codegen_configuration(self) -> FrameACLCodegenConfiguration:
        self.check_cleaned()
        return self._codegen_configuration

    @property
    def normalized_json_configuration_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return self.to_json_string()

    def set_previous_configuration_id(
            self,
            previous_configuration_id: Optional[str],
    ) -> None:
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change previous_configuration_id on a locked configuration."
            )
        self._previous_configuration_id = previous_configuration_id

    def finalize(self) -> None:
        self.check_cleaned()
        self._locked = True

    def set_view_configuration(
            self,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change view_configuration on a locked configuration."
            )
        if not isinstance(view_configuration, FrameACLViewConfiguration):
            raise TypeError(
                "view_configuration must be a FrameACLViewConfiguration."
            )
        self._view_configuration.cleanup()
        self._view_configuration = view_configuration

    def set_codegen_configuration(
            self,
            codegen_configuration: FrameACLCodegenConfiguration,
    ) -> None:
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change codegen_configuration on a locked configuration."
            )
        if not isinstance(codegen_configuration, FrameACLCodegenConfiguration):
            raise TypeError(
                "codegen_configuration must be a FrameACLCodegenConfiguration."
            )
        self._codegen_configuration.cleanup()
        self._codegen_configuration = codegen_configuration

    def set_json_configuration_string(
            self,
            json_configuration_string: str,
    ) -> None:
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change JSON payload on a locked configuration."
            )
        parsed_payload = _parse_json_configuration_string(
            json_configuration_string
        )
        self.set_view_configuration(
            FrameACLViewConfiguration.from_json_dict(
                parsed_payload.get("view_configuration", {})
            )
        )
        self.set_codegen_configuration(
            FrameACLCodegenConfiguration.from_json_dict(
                parsed_payload.get("codegen_configuration", {})
            )
        )

    def to_json_dict(self) -> Dict[str, Any]:
        self.check_cleaned()
        return {
            "frame_name": self._frame_name,
            "view_configuration": self._view_configuration.to_json_dict(),
            "codegen_configuration": self._codegen_configuration.to_json_dict(),
        }

    def to_json_string(self) -> str:
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)
