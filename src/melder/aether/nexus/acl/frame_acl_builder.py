import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.profiles.frame_acl_profile import FrameACLProfile
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IFrameACLContainer


class FrameACLBuilder(Cleanable):
    """
    Purpose:
        Provide the frame-local mutable ACL authoring surface owned by one
        `FrameACLContainer`.

    Contract:
        - One builder object exists per container.
        - At most one draft change session may be active at a time.
        - Draft state is represented as a typed `FrameACLConfiguration` seeded
          from the current configuration.
        - Draft bundles preserve view, command, and codegen child
          configurations together.
        - Final installation and validation are delegated to the owning
          container.
        - Uses an instance lock because draft lifecycle transitions and cleanup
          mutate multiple fields together in a nogil runtime.

    Notes:
        - The builder still applies reusable view/codegen profiles only.
        - The command child remains draft state owned by the bundle until a
          dedicated reusable command-profile layer exists.

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
        "_draft_configuration",
    ]

    def __init__(self, container: IFrameACLContainer) -> None:
        """
        Initialize one frame ACL builder for the owning container.

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
        self._container: IFrameACLContainer = container
        self._change_active: bool = False
        self._draft_configuration: Optional[FrameACLConfiguration] = None

    def cleanup(self) -> None:
        """
        Idempotently clear builder state.

        Contract:
            - Safe to call more than once.
            - Cleans the current draft configuration when one exists.
            - Leaves the builder unusable after completion.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._draft_configuration is not None:
                self._draft_configuration.cleanup()
            self._draft_configuration = None
            self._container = None
            self._change_active = None
        self._lock = None

    @property
    def change_active(self) -> bool:
        """
        Return whether the builder currently owns one open change session.

        Contract:
            Reflects draft-session ownership only; it does not imply the draft
            has been committed.

        Returns:
            bool: True when a change session is active.
        """
        self.check_cleaned()
        with self._lock:
            return self._change_active

    def begin_change(self) -> None:
        """
        Start one builder-owned change session.

        Contract:
            - Creates one detached draft bundle cloned from the current
              container-selected configuration.
            - Preserves view, command, and codegen child state from the current
              bundle.

        Returns:
            None.

        Raises:
            RuntimeError:
                If another change session is already active.
        """
        self.check_cleaned()
        with self._lock:
            if self._change_active:
                raise RuntimeError("FrameACLBuilder already has an active change.")
            current_configuration = self._container.frame_acl_configuration
            self._draft_configuration = (
                FrameACLConfiguration.create_new_from_acl_configuration(
                    current_configuration,
                    reason="builder_draft",
                )
            )
            self._change_active = True

    def apply_frame_acl_profile(
            self,
            frame_acl_profile: FrameACLProfile,
    ) -> None:
        """
        Apply one composed reusable ACL profile into the active typed draft.

        Contract:
            - Replaces the draft view and codegen configurations from the
              reusable profile input.
            - Preserves the current draft command configuration because the
              reusable profile layer does not yet expose a typed command
              profile in this first cut.

        Args:
            frame_acl_profile:
                Composed ACL profile to apply into the active draft.

        Returns:
            None.

        Raises:
            TypeError:
                If `frame_acl_profile` is not a `FrameACLProfile`.
            RuntimeError:
                If no draft change session is active.
        """
        self.check_cleaned()
        if not isinstance(frame_acl_profile, FrameACLProfile):
            raise TypeError("frame_acl_profile must be a FrameACLProfile.")
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            self._draft_configuration.set_view_configuration(
                FrameACLViewConfiguration.from_profile(
                    frame_acl_profile.view_profile,
                    frame_override_ruleset=(
                        frame_acl_profile.view_override_ruleset.clone()
                    ),
                )
            )
            self._draft_configuration.set_codegen_configuration(
                FrameACLCodegenConfiguration.from_profile(
                    frame_acl_profile.codegen_profile,
                    capability_override_ruleset=(
                        frame_acl_profile.codegen_override_ruleset.clone()
                    ),
                )
            )

    def load_json_configuration_string(
            self,
            json_configuration_string: str,
    ) -> None:
        """
        Replace the active typed draft from a JSON payload string.

        Contract:
            - Allowed only while a draft change session is active.
            - Rebuilds the draft's typed child configuration objects from the
              provided JSON payload.
            - Preserves the draft node's identity/history metadata while
              replacing only the typed child configuration state.

        Args:
            json_configuration_string:
                JSON payload string for the next configuration revision.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no draft change session is active.
            TypeError:
                Propagates when the payload is not a string.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            self._draft_configuration.set_json_configuration_string(
                json_configuration_string
            )

    def commit_change(self) -> FrameACLConfiguration:
        """
        Finalize and install the next frame ACL configuration revision.

        Contract:
            - Finalizes the current draft bundle before installation.
            - Delegates validation and current-selection update to the owning
              container.
            - Clears builder-owned draft state after a successful install.

        Returns:
            FrameACLConfiguration: Newly installed configuration.

        Raises:
            RuntimeError:
                If no draft change session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            self._draft_configuration.finalize()
            self._container.install_configuration(self._draft_configuration)
            next_configuration = self._draft_configuration
            self._draft_configuration = None
            self._change_active = False
            return next_configuration

    def discard_change(self) -> None:
        """
        Discard the current builder-owned change session.

        Contract:
            - Best-effort cleanup of the current draft when present.
            - Leaves the builder with no active change session.
            - Safe to call even when no draft exists.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._draft_configuration is not None:
                self._draft_configuration.cleanup()
            self._draft_configuration = None
            self._change_active = False
