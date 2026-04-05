import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLBuilder(Cleanable):
    """
    Purpose:
        Provide the frame-local mutable ACL authoring surface owned by one
        `FrameACLContainer`.

    Contract:
        - One builder object exists per container.
        - At most one draft change session may be active at a time.
        - Draft state is represented as a JSON payload string seeded from the
          current configuration.
        - Final installation and validation are delegated to the owning
          container.

    Threading:
        Uses one instance `threading.RLock` to serialize draft-session state
        changes.

    Lifecycle:
        Cleanup is idempotent and clears draft state plus the container
        reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_container",
        "_change_active",
        "_draft_json_configuration_string",
    ]

    def __init__(self, container: object) -> None:
        """
        Initialize one frame ACL builder for the owning container.

        Purpose:
            Bind the builder to one frame-local ACL container and prepare its
            mutable draft-session state.

        Contract:
            - `container` must be a live owning container object.
            - No draft is active at construction time.

        Args:
            container:
                Owning frame ACL container.

        Returns:
            None.

        Raises:
            TypeError:
                If `container` is None.
        """
        super().__init__()
        if container is None:
            raise TypeError("container cannot be None.")

        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._container = container
        self._change_active: bool = False
        self._draft_json_configuration_string: Optional[str] = None

    def cleanup(self) -> None:
        """
        Idempotently clear builder state.

        Purpose:
            Tear down the builder's mutable draft-session state and ownership
            references.

        Contract:
            - Safe to call more than once.
            - Discards any in-flight draft state.
            - Leaves the builder unusable after completion.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._lock = None
        self._container = None
        self._change_active = None
        self._draft_json_configuration_string = None

    @property
    def change_active(self) -> bool:
        """
        Return whether the builder currently owns one open change session.

        Purpose:
            Expose whether the builder is currently holding mutable draft state.

        Returns:
            bool: True when a change session is active.
        """
        self.check_cleaned()
        with self._lock:
            return self._change_active

    def begin_change(self) -> None:
        """
        Start one builder-owned change session.

        Purpose:
            Seed draft state from the container's current configuration and
            mark the builder as actively editing.

        Contract:
            - Fails if another change session is already active.
            - Uses the current configuration JSON payload as the draft seed.

        Returns:
            None.

        Raises:
            RuntimeError:
                If a change session is already active.
        """
        self.check_cleaned()
        with self._lock:
            if self._change_active:
                raise RuntimeError("FrameACLBuilder already has an active change.")
            current_configuration = self._container.frame_acl_configuration
            self._draft_json_configuration_string = (
                current_configuration.to_json_string()
            )
            self._change_active = True

    def load_json_configuration_string(
            self,
            json_configuration_string: str,
    ) -> None:
        """
        Replace the draft JSON payload string for the active change session.

        Purpose:
            Overwrite the builder-held draft payload during an active change
            session.

        Args:
            json_configuration_string:
                JSON payload string for the next configuration revision.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no change session is active.
            TypeError:
                If `json_configuration_string` is not a string.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if not isinstance(json_configuration_string, str):
                raise TypeError("json_configuration_string must be a string.")
            self._draft_json_configuration_string = json_configuration_string

    def commit_change(self) -> FrameACLConfiguration:
        """
        Build and install the next frame ACL configuration revision.

        Purpose:
            Materialize the current draft payload into a new configuration node
            and install it through the owning container.

        Contract:
            - Requires an active change session.
            - Copies from the current configuration node.
            - Finalizes the new node before installation.
            - Clears builder draft state after successful installation.

        Returns:
            FrameACLConfiguration: Newly installed configuration.

        Raises:
            RuntimeError:
                If no change session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active:
                raise RuntimeError("FrameACLBuilder has no active change.")

            current_configuration = self._container.frame_acl_configuration
            next_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
                current_configuration,
                reason="builder_commit",
            )
            next_configuration.set_json_configuration_string(
                self._draft_json_configuration_string
            )
            next_configuration.finalize()
            self._container.install_configuration(next_configuration)
            self._draft_json_configuration_string = None
            self._change_active = False
            return next_configuration

    def discard_change(self) -> None:
        """
        Discard the current builder-owned change session.

        Purpose:
            Drop any active draft payload without creating a new configuration
            node.

        Contract:
            Always clears builder draft state, even if no payload changes were
            made after `begin_change()`.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._draft_json_configuration_string = None
            self._change_active = False
