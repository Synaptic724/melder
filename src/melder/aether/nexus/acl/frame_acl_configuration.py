import json
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLConfiguration(Cleanable):
    """
    Internal

    Frame-scoped ACL configuration placeholder.

    Purpose:
        Hold one normalized ACL configuration payload for one frame so later
        ACL propagation work has a concrete runtime object instead of only a
        design note.

    Contract:
        - Represents one frame-scoped ACL configuration revision.
        - Stores the normalized JSON payload string as the canonical payload.
        - Stores a pointer to the previous configuration id when the current
          object was built from an earlier revision.
        - Is data-focused in this placeholder slice; mutation should happen
          through the builder, not by direct field rewrites.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_configuration_id",
        "_frame_name",
        "_previous_configuration_id",
        "_normalized_json_configuration_string",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            normalized_json_configuration_string: str,
            previous_configuration_id: Optional[str],
    ) -> None:
        """
        Initialize one frame-scoped ACL configuration object.

        Args:
            frame_name:
                Owning frame name.
            normalized_json_configuration_string:
                Canonical normalized JSON payload string.
            previous_configuration_id:
                Previous configuration id when this object supersedes an
                earlier revision.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(normalized_json_configuration_string, str):
            raise TypeError(
                "normalized_json_configuration_string must be a string."
            )

        self._configuration_id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._previous_configuration_id: Optional[str] = previous_configuration_id
        self._normalized_json_configuration_string: str = (
            normalized_json_configuration_string
        )

    @classmethod
    def create_default(
            cls,
            frame_name: str,
    ) -> "FrameACLConfiguration":
        """
        Create one default empty ACL configuration for a frame.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            FrameACLConfiguration:
                Default frame ACL configuration.
        """
        default_payload = {
            "frame_name": frame_name,
            "frame_acl": {},
            "conduit_acls": [],
            "spellbook_acls": [],
            "spell_acls": [],
        }
        normalized_json_configuration_string = json.dumps(
            default_payload,
            sort_keys=True,
        )
        return cls(
            frame_name=frame_name,
            normalized_json_configuration_string=normalized_json_configuration_string,
            previous_configuration_id=None,
        )

    @classmethod
    def from_json_configuration_string(
            cls,
            *,
            frame_name: str,
            json_configuration_string: str,
            previous_configuration_id: Optional[str],
    ) -> "FrameACLConfiguration":
        """
        Build one configuration object from a JSON payload string.

        Args:
            frame_name:
                Owning frame name.
            json_configuration_string:
                JSON payload string to normalize and store.
            previous_configuration_id:
                Previous configuration id when this payload supersedes an
                earlier revision.

        Returns:
            FrameACLConfiguration:
                Normalized frame ACL configuration.

        Raises:
            TypeError: If the payload is not a string.
            ValueError: If the payload is not valid JSON.
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
            previous_configuration_id=previous_configuration_id,
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
    def previous_configuration_id(self) -> Optional[str]:
        """
        Return the previous configuration id when known.

        Returns:
            Optional[str]: Previous configuration id.
        """
        self.check_cleaned()
        return self._previous_configuration_id

    @property
    def normalized_json_configuration_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return self._normalized_json_configuration_string

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the configuration payload as a detached JSON-compatible dict.

        Returns:
            Dict[str, Any]: Parsed JSON payload.
        """
        self.check_cleaned()
        return json.loads(self._normalized_json_configuration_string)

    def cleanup(self) -> None:
        """
        Idempotently clear the configuration object.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._configuration_id = None
        self._frame_name = None
        self._previous_configuration_id = None
        self._normalized_json_configuration_string = None
