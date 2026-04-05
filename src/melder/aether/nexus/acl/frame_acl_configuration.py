import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLConfiguration(Cleanable):
    """
    Purpose:
        Represent one frame-scoped ACL configuration node owned by a
        `FrameACLConfigurationChain`.

    Contract:
        - Carries stable node identity plus linked-history metadata.
        - Stores one canonical normalized JSON payload string that represents
          the authored ACL state.
        - May exist as an unlocked draft while being prepared by a builder or
          chain-copy operation.
        - Must be locked before a chain may commit and own it.

    Lifecycle:
        Cleanup is idempotent and clears all node metadata and payload
        references.
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

        Purpose:
            Construct a single ACL configuration node with normalized payload
            storage and chain-link metadata.

        Contract:
            - Generates a fresh configuration id at construction time.
            - Records creation time immediately.
            - Does not normalize or validate JSON beyond what the caller
              already supplied in `normalized_json_configuration_string`.

        Args:
            frame_name:
                Stable frame name that owns this configuration node.
            normalized_json_configuration_string:
                Canonical normalized JSON payload string for this node.
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

        Raises:
            ValueError:
                If `frame_name` or `reason` is empty.
            TypeError:
                If the JSON payload is not a string or `locked` is not a bool.
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
        self._normalized_json_configuration_string: str = (
            normalized_json_configuration_string
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the configuration node.

        Purpose:
            Tear down the node metadata and payload once the node is no longer
            usable.

        Contract:
            - Safe to call more than once.
            - Clears identity, history metadata, timestamps, and payload
              references.

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

    @classmethod
    def create_default(
            cls,
            frame_name: str,
    ) -> "FrameACLConfiguration":
        """
        Create the default locked ACL configuration for a frame.

        Purpose:
            Seed a frame chain with one well-known empty ACL configuration node.

        Contract:
            - Produces a locked node immediately.
            - Uses an empty `view_acl` and `codegen_acl` payload.

        Args:
            frame_name:
                Stable frame name that will own the default node.

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

        Purpose:
            Normalize a JSON payload string into a new configuration node.

        Contract:
            - Parses and re-emits the payload in normalized sorted-key form.
            - Preserves the caller-provided frame, source, previous pointer,
              reason, and locked state.

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
            FrameACLConfiguration: Normalized configuration node.

        Raises:
            TypeError:
                If `json_configuration_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
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

        Purpose:
            Copy one existing node into a new unlocked draft node for later
            modification and commit.

        Args:
            source_configuration:
                Existing source configuration node to copy from.
            reason:
                Human-readable creation reason recorded with the new draft.

        Returns:
            FrameACLConfiguration: New unlocked draft configuration node.

        Raises:
            TypeError:
                If `source_configuration` is not a `FrameACLConfiguration`.
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

        Purpose:
            Expose the stable node identity generated at construction time.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._configuration_id

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Purpose:
            Expose the stable frame identity that owns this node.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def source_configuration_id(self) -> Optional[str]:
        """
        Return the source configuration id when this node was copied forward.

        Purpose:
            Expose the derivation source for copy-forward or rollback-style
            draft creation.

        Returns:
            Optional[str]: Source configuration id.
        """
        self.check_cleaned()
        return self._source_configuration_id

    @property
    def previous_configuration_id(self) -> Optional[str]:
        """
        Return the previous linked-list configuration id.

        Purpose:
            Expose the prior chain node pointer used for newest-to-oldest
            traversal.

        Returns:
            Optional[str]: Previous linked-list configuration id.
        """
        self.check_cleaned()
        return self._previous_configuration_id

    @property
    def created_at(self) -> str:
        """
        Return the UTC creation timestamp for this node.

        Purpose:
            Expose the node creation timestamp for diagnostics and history
            inspection.

        Returns:
            str: UTC timestamp string.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def reason(self) -> str:
        """
        Return the human-readable creation reason.

        Purpose:
            Expose the reason recorded when the node was created.

        Returns:
            str: Creation reason.
        """
        self.check_cleaned()
        return self._reason

    @property
    def locked(self) -> bool:
        """
        Return whether the configuration node is finalized.

        Purpose:
            Expose whether the node may still be mutated by builder/chain prep
            code.

        Returns:
            bool: True when finalized/locked.
        """
        self.check_cleaned()
        return self._locked

    @property
    def normalized_json_configuration_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Purpose:
            Expose the normalized payload form used for persistence, display,
            and copy-forward mechanics.

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

        Purpose:
            Allow chain-preparation code to attach the prior-node pointer before
            the node is finalized.

        Args:
            previous_configuration_id:
                Previous chain node id or None.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is already locked.
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

        Purpose:
            Mark the node as finalized so it is safe for chain ownership.

        Contract:
            Finalization is one-way; this method does not support unlocking.

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

        Purpose:
            Overwrite the draft payload and normalize it into canonical
            sorted-key JSON form.

        Args:
            json_configuration_string:
                JSON payload string to parse, normalize, and store.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is already locked.
            TypeError:
                If the payload is not a string.
            ValueError:
                If the payload is not valid JSON.
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

        Purpose:
            Provide a parsed payload view that callers may inspect without
            mutating the stored normalized string.

        Returns:
            Dict[str, Any]: Parsed JSON payload.
        """
        self.check_cleaned()
        return json.loads(self._normalized_json_configuration_string)

    def to_json_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Purpose:
            Provide the stored normalized payload for persistence, logging, or
            display.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return self._normalized_json_configuration_string
