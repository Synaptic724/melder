import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLConfiguration(Cleanable):
    """
    Internal

    One frame-scoped ACL configuration node.

    Purpose:
        Represent one committed or draft ACL configuration in the frame-level
        configuration chain.

    Contract:
        - Carries its own configuration id and linked-list metadata.
        - Stores the canonical normalized JSON payload string used for display,
          persistence, and copy-forward mechanics.
        - May exist in an unlocked draft state before finalize.
        - Must be locked before the chain may own it.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_configuration_id",
        "_frame_name",
        "_source_configuration_id",
        "_previous_configuration_id",
        "_created_at",
        "_reason",
        "_locked",
        "_normalized_json_configuration_string",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            normalized_json_configuration_string: str,
            source_configuration_id: Optional[str],
            previous_configuration_id: Optional[str],
            reason: str,
            locked: bool,
    ) -> None:
        """
        Initialize one frame-scoped ACL configuration node.

        Args:
            frame_name:
                Owning frame name.
            normalized_json_configuration_string:
                Canonical normalized JSON payload string.
            source_configuration_id:
                Source configuration id when copied from another config.
            previous_configuration_id:
                Previous linked-list configuration id.
            reason:
                Human-readable creation reason.
            locked:
                True when the configuration is finalized and safe for chain
                ownership.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(normalized_json_configuration_string, str):
            raise TypeError(
                "normalized_json_configuration_string must be a string."
            )
        if not isinstance(reason, str) or not reason:
            raise ValueError("reason cannot be empty.")
        if not isinstance(locked, bool):
            raise TypeError("locked must be a bool.")

        self._configuration_id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._source_configuration_id: Optional[str] = source_configuration_id
        self._previous_configuration_id: Optional[str] = previous_configuration_id
        self._created_at: str = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._reason: str = reason
        self._locked: bool = locked
        self._normalized_json_configuration_string: str = (
            normalized_json_configuration_string
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
                Owning frame name.

        Returns:
            FrameACLConfiguration: Default locked configuration node.
        """
        default_payload = {
            "frame_name": frame_name,
            "view_acl": {},
            "codegen_acl": {},
        }
        return cls(
            frame_name=frame_name,
            normalized_json_configuration_string=json.dumps(
                default_payload,
                sort_keys=True,
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
                JSON payload string to normalize and store.
            source_configuration_id:
                Source configuration id when copied from another config.
            previous_configuration_id:
                Previous linked-list configuration id.
            reason:
                Human-readable creation reason.
            locked:
                True when the created node should start finalized.

        Returns:
            FrameACLConfiguration: Normalized configuration node.
        """
        if not isinstance(json_configuration_string, str):
            raise TypeError("json_configuration_string must be a string.")
        try:
            parsed_payload = json.loads(json_configuration_string)
        except json.JSONDecodeError as exc:
            raise ValueError("json_configuration_string must be valid JSON.") from exc

        normalized_json_configuration_string = json.dumps(
            parsed_payload,
            sort_keys=True,
        )
        return cls(
            frame_name=frame_name,
            normalized_json_configuration_string=normalized_json_configuration_string,
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
                Existing source configuration to copy.
            reason:
                Human-readable creation reason.

        Returns:
            FrameACLConfiguration: New unlocked draft configuration node.
        """
        if not isinstance(source_configuration, FrameACLConfiguration):
            raise TypeError(
                "source_configuration must be a FrameACLConfiguration."
            )
        return cls(
            frame_name=source_configuration.frame_name,
            normalized_json_configuration_string=(
                source_configuration.normalized_json_configuration_string
            ),
            source_configuration_id=source_configuration.configuration_id,
            previous_configuration_id=None,
            reason=reason,
            locked=False,
        )

    @property
    def configuration_id(self) -> str:
        """
        Return the stable configuration id.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._configuration_id

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def source_configuration_id(self) -> Optional[str]:
        """
        Return the source configuration id when this node was copied forward.

        Returns:
            Optional[str]: Source configuration id.
        """
        self.check_cleaned()
        return self._source_configuration_id

    @property
    def previous_configuration_id(self) -> Optional[str]:
        """
        Return the previous linked-list configuration id.

        Returns:
            Optional[str]: Previous linked-list configuration id.
        """
        self.check_cleaned()
        return self._previous_configuration_id

    @property
    def created_at(self) -> str:
        """
        Return the UTC creation timestamp for this node.

        Returns:
            str: UTC timestamp string.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def reason(self) -> str:
        """
        Return the human-readable creation reason.

        Returns:
            str: Creation reason.
        """
        self.check_cleaned()
        return self._reason

    @property
    def locked(self) -> bool:
        """
        Return whether the configuration node is finalized.

        Returns:
            bool: True when finalized/locked.
        """
        self.check_cleaned()
        return self._locked

    @property
    def normalized_json_configuration_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return self._normalized_json_configuration_string

    def set_previous_configuration_id(
            self,
            previous_configuration_id: Optional[str],
    ) -> None:
        """
        Set the linked-list previous pointer while the config is still mutable.

        Args:
            previous_configuration_id:
                Previous linked-list configuration id.

        Returns:
            None.

        Raises:
            RuntimeError: If the configuration is already locked.
        """
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change previous_configuration_id on a locked configuration."
            )
        self._previous_configuration_id = previous_configuration_id

    def finalize(self) -> None:
        """
        Lock the configuration node so the chain may own it.

        Returns:
            None.
        """
        self.check_cleaned()
        self._locked = True

    def set_json_configuration_string(
            self,
            json_configuration_string: str,
    ) -> None:
        """
        Replace the JSON payload string while the configuration is still
        mutable.

        Args:
            json_configuration_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            RuntimeError: If the configuration is already locked.
            TypeError: If the payload is not a string.
            ValueError: If the payload is not valid JSON.
        """
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change JSON payload on a locked configuration."
            )
        if not isinstance(json_configuration_string, str):
            raise TypeError("json_configuration_string must be a string.")
        try:
            parsed_payload = json.loads(json_configuration_string)
        except json.JSONDecodeError as exc:
            raise ValueError("json_configuration_string must be valid JSON.") from exc
        self._normalized_json_configuration_string = json.dumps(
            parsed_payload,
            sort_keys=True,
        )

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the configuration payload as a detached JSON-compatible dict.

        Returns:
            Dict[str, Any]: Parsed JSON payload.
        """
        self.check_cleaned()
        return json.loads(self._normalized_json_configuration_string)

    def to_json_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return self._normalized_json_configuration_string

    def cleanup(self) -> None:
        """
        Idempotently clear the configuration node.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._configuration_id = None
        self._frame_name = None
        self._source_configuration_id = None
        self._previous_configuration_id = None
        self._created_at = None
        self._reason = None
        self._locked = None
        self._normalized_json_configuration_string = None
