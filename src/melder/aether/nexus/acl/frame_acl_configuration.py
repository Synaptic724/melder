import json
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
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
        - Owns typed view, command, and codegen child configuration objects.
        - May exist as an unlocked draft while being prepared by a builder or
          chain-copy operation.
        - Must be locked before a chain may commit and own it.
        - Acts as the selected named ACL bundle for one frame; downstream
          selection binds this object as a unit rather than selecting child
          configs independently.

    Lifecycle:
        Cleanup is idempotent and clears all node metadata and owned child
        configuration objects.

    Threading / Concurrency:
        - Owns one instance lock for grouped cleanup and lifecycle mutation.
        - Still relies on owning container/builder lifecycle rules for higher-
          level serialized draft/chain mutation.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_configuration_id",
        "_lock",
        "_frame_name",
        "_source_configuration_id",
        "_previous_configuration_id",
        "_created_at",
        "_reason",
        "_locked",
        "_view_configuration",
        "_command_configuration",
        "_codegen_configuration",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            view_configuration: FrameACLViewConfiguration,
            command_configuration: FrameACLCommandConfiguration,
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
            command_configuration:
                Typed applied command-side configuration object.
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
        if not isinstance(command_configuration, FrameACLCommandConfiguration):
            raise TypeError(
                "command_configuration must be a FrameACLCommandConfiguration."
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
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._source_configuration_id: Optional[str] = source_configuration_id
        self._previous_configuration_id: Optional[str] = previous_configuration_id
        self._created_at: str = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._reason: str = reason
        self._locked: bool = locked
        self._view_configuration: FrameACLViewConfiguration = view_configuration
        self._command_configuration: FrameACLCommandConfiguration = (
            command_configuration
        )
        self._codegen_configuration: FrameACLCodegenConfiguration = (
            codegen_configuration
        )

    @classmethod
    def create_default(
            cls,
            frame_name: str,
    ) -> "FrameACLConfiguration":
        """
        Create the default locked ACL configuration bundle for a frame.

        Contract:
            - Produces a complete typed ACL bundle for the frame.
            - Seeds the default view, command, and codegen child
              configurations.
            - Returns a locked node that is immediately safe for chain/container
              ownership.

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
            command_configuration=FrameACLCommandConfiguration.create_default(),
            codegen_configuration=FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_default()
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="default",
            locked=True,
        )

    @classmethod
    def create_from_selected_configurations(
            cls,
            *,
            frame_name: str,
            view_configuration: FrameACLViewConfiguration,
            command_configuration: FrameACLCommandConfiguration,
            codegen_configuration: FrameACLCodegenConfiguration,
            reason: str,
            locked: bool = True,
            configuration_id: Optional[str] = None,
    ) -> "FrameACLConfiguration":
        """
        Assemble one full ACL bundle snapshot from selected child configs.

        Contract:
            - Clones the supplied child configurations so the returned bundle
              is detached from live chain-owned family revisions.
            - Supports an explicit `configuration_id` override so callers can
              bind the assembled bundle identity to the selected child revision
              tuple instead of generating a fresh random id every time.
            - Does not imply chain ownership; this is an assembled snapshot for
              compilation, validation, or export.

        Args:
            frame_name:
                Owning frame name for the assembled bundle.
            view_configuration:
                Selected view configuration revision.
            command_configuration:
                Selected command configuration revision.
            codegen_configuration:
                Selected codegen configuration revision.
            reason:
                Human-readable creation reason.
            locked:
                True when the assembled bundle should start finalized.
            configuration_id:
                Optional explicit configuration id for the assembled bundle.

        Returns:
            FrameACLConfiguration: Detached assembled ACL bundle snapshot.
        """
        configuration = cls(
            frame_name=frame_name,
            view_configuration=view_configuration.clone(),
            command_configuration=command_configuration.clone(),
            codegen_configuration=codegen_configuration.clone(),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason=reason,
            locked=locked,
        )
        if configuration_id is not None:
            configuration._configuration_id = configuration_id
        return configuration

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

        Notes:
            Missing `command_configuration` payloads are normalized to the
            default command configuration in this first cut so older serialized
            ACL documents can still be reconstructed into a complete typed
            bundle.

        Raises:
            TypeError:
                If the JSON payload input is not a string.
            ValueError:
                If the JSON payload is malformed or does not decode to an
                object.
        """
        parsed_payload = _parse_json_configuration_string(
            json_configuration_string
        )
        return cls(
            frame_name=frame_name,
            view_configuration=FrameACLViewConfiguration.from_json_dict(
                parsed_payload.get("view_configuration", {})
            ),
            command_configuration=FrameACLCommandConfiguration.from_json_dict(
                parsed_payload.get("command_configuration", {})
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
            view_configuration=source_configuration.view_configuration.clone(),
            command_configuration=(
                source_configuration.command_configuration.clone()
            ),
            codegen_configuration=source_configuration.codegen_configuration.clone(),
            source_configuration_id=source_configuration.configuration_id,
            previous_configuration_id=None,
            reason=reason,
            locked=False,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the configuration node and its owned child configs.

        Contract:
            - Safe to call more than once.
            - Cleans the owned view, command, and codegen child
              configurations before dropping references.
            - Clears node identity/history metadata so future callers fail
              through `check_cleaned()`.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._view_configuration.cleanup()
            self._command_configuration.cleanup()
            self._codegen_configuration.cleanup()
            self._configuration_id = None
            self._frame_name = None
            self._source_configuration_id = None
            self._previous_configuration_id = None
            self._created_at = None
            self._reason = None
            self._locked = None
            self._view_configuration = None
            self._command_configuration = None
            self._codegen_configuration = None
            self._lock = None

    @property
    def configuration_id(self) -> str:
        """
        Return the stable configuration-node id.

        Returns:
            str: Unique id for this ACL configuration node.
        """
        self.check_cleaned()
        return self._configuration_id

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name for this ACL bundle.

        Returns:
            str: Stable frame name that owns this configuration node.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def source_configuration_id(self) -> Optional[str]:
        """
        Return the source configuration id when this node was copied.

        Returns:
            Optional[str]: Source node id when derived from another node.
        """
        self.check_cleaned()
        return self._source_configuration_id

    @property
    def previous_configuration_id(self) -> Optional[str]:
        """
        Return the previous chain node id when known.

        Returns:
            Optional[str]: Previous node id in the configuration chain.
        """
        self.check_cleaned()
        return self._previous_configuration_id

    @property
    def created_at(self) -> str:
        """
        Return the UTC creation timestamp string for this node.

        Returns:
            str: ISO-8601 UTC creation timestamp.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def reason(self) -> str:
        """
        Return the human-readable reason recorded for this node.

        Returns:
            str: Creation/change reason for this configuration node.
        """
        self.check_cleaned()
        return self._reason

    @property
    def locked(self) -> bool:
        """
        Return whether this configuration node is finalized.

        Returns:
            bool: True when the node is locked against further mutation.
        """
        self.check_cleaned()
        return self._locked

    @property
    def view_configuration(self) -> FrameACLViewConfiguration:
        """
        Return the typed view-side ACL configuration.

        Contract:
            Read-only accessor for the bundle-owned view child configuration.
            The returned object is live bundle state, not a detached copy.

        Returns:
            FrameACLViewConfiguration: Applied view configuration.
        """
        self.check_cleaned()
        return self._view_configuration

    @property
    def command_configuration(self) -> FrameACLCommandConfiguration:
        """
        Return the typed command-side ACL configuration.

        Contract:
            Read-only accessor for the bundle-owned command child
            configuration. The returned object is live bundle state, not a
            detached copy.

        Returns:
            FrameACLCommandConfiguration: Applied command configuration.
        """
        self.check_cleaned()
        return self._command_configuration

    @property
    def codegen_configuration(self) -> FrameACLCodegenConfiguration:
        """
        Return the typed codegen-side ACL configuration.

        Contract:
            Read-only accessor for the bundle-owned codegen child
            configuration. The returned object is live bundle state, not a
            detached copy.

        Returns:
            FrameACLCodegenConfiguration: Applied codegen configuration.
        """
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
        """
        Update the previous-node pointer while the bundle is mutable.

        Contract:
            - Allowed only while the bundle is unlocked.
            - Changes only the linked-history pointer; all child configs remain
              untouched.

        Args:
            previous_configuration_id:
                Previous chain node id or None.

        Raises:
            RuntimeError:
                If the configuration node is already locked.
        """
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change previous_configuration_id on a locked configuration."
            )
        self._previous_configuration_id = previous_configuration_id

    def finalize(self) -> None:
        """
        Lock the configuration node against further mutation.

        Contract:
            - Finalization is one-way for this node.
            - Does not rebuild child configs; it only flips the mutability gate.
        """
        self.check_cleaned()
        self._locked = True

    def set_view_configuration(
            self,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Replace the typed view configuration while the node is mutable.

        Contract:
            - Allowed only while the bundle is unlocked.
            - Cleans the displaced view configuration before replacing it.
            - Preserves bundle identity/history metadata while swapping only the
              view child.

        Args:
            view_configuration:
                Replacement typed view configuration.

        Raises:
            RuntimeError:
                If the configuration node is already locked.
            TypeError:
                If `view_configuration` is not a `FrameACLViewConfiguration`.
        """
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

    def set_command_configuration(
            self,
            command_configuration: FrameACLCommandConfiguration,
    ) -> None:
        """
        Replace the typed command configuration while the node is mutable.

        Contract:
            - Allowed only while the bundle is unlocked.
            - Cleans the displaced command configuration before replacing it.
            - Preserves bundle identity/history metadata while swapping only the
              command child.

        Args:
            command_configuration:
                Replacement typed command configuration.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration node is already locked.
            TypeError:
                If `command_configuration` is not a
                `FrameACLCommandConfiguration`.
        """
        self.check_cleaned()
        if self._locked:
            raise RuntimeError(
                "Cannot change command_configuration on a locked configuration."
            )
        if not isinstance(command_configuration, FrameACLCommandConfiguration):
            raise TypeError(
                "command_configuration must be a FrameACLCommandConfiguration."
            )
        self._command_configuration.cleanup()
        self._command_configuration = command_configuration

    def set_codegen_configuration(
            self,
            codegen_configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Replace the typed codegen configuration while the node is mutable.

        Contract:
            - Allowed only while the bundle is unlocked.
            - Cleans the displaced codegen configuration before replacing it.
            - Preserves bundle identity/history metadata while swapping only the
              codegen child.

        Args:
            codegen_configuration:
                Replacement typed codegen configuration.

        Raises:
            RuntimeError:
                If the configuration node is already locked.
            TypeError:
                If `codegen_configuration` is not a
                `FrameACLCodegenConfiguration`.
        """
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
        """
        Replace all child configurations from a JSON payload string.

        Contract:
            - Allowed only while the bundle is unlocked.
            - Rebuilds view, command, and codegen child configurations from the
              parsed JSON payload.
            - Uses the typed child `from_json_dict(...)` constructors so the
              bundle remains normalized after replacement.

        Args:
            json_configuration_string:
                JSON object string describing the ACL bundle.

        Raises:
            RuntimeError:
                If the configuration node is already locked.
            TypeError:
                If the payload input is not a string.
            ValueError:
                If the payload is malformed or does not decode to an object.
        """
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
        self.set_command_configuration(
            FrameACLCommandConfiguration.from_json_dict(
                parsed_payload.get("command_configuration", {})
            )
        )
        self.set_codegen_configuration(
            FrameACLCodegenConfiguration.from_json_dict(
                parsed_payload.get("codegen_configuration", {})
            )
        )

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the ACL bundle as a detached JSON-compatible dictionary.

        Contract:
            - Returns detached JSON-ready child payloads for view, command, and
              codegen.
            - Preserves the current bundle frame identity in the payload.

        Returns:
            Dict[str, Any]: JSON-compatible ACL bundle payload.
        """
        self.check_cleaned()
        return {
            "frame_name": self._frame_name,
            "view_configuration": self._view_configuration.to_json_dict(),
            "command_configuration": (
                self._command_configuration.to_json_dict()
            ),
            "codegen_configuration": self._codegen_configuration.to_json_dict(),
        }

    def to_json_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Sorted-key JSON string for the current ACL bundle.
        """
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)
