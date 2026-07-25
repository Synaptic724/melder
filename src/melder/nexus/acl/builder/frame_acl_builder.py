import json
import threading
from typing import TYPE_CHECKING, Optional, Union

from melder.nexus.acl.builder.frame_acl_command_builder import (
    FrameACLCommandBuilder,
)
from melder.nexus.acl.builder.frame_acl_codegen_builder import (
    FrameACLCodegenBuilder,
)
from melder.nexus.acl.builder.frame_acl_view_builder import (
    FrameACLViewBuilder,
)
from melder.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.frame_acl_command_configuration import FrameACLCommandConfiguration
from melder.nexus.acl.configurations.frame_acl_codegen_configuration import FrameACLCodegenConfiguration
from melder.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.nexus.acl.configurations.frame_acl_view_configuration import FrameACLViewConfiguration

if TYPE_CHECKING:
    from melder.nexus.acl.frame_acl_container import FrameACLContainer

FrameACLDraftConfiguration = Optional[
    Union[
        FrameACLViewConfiguration,
        FrameACLCommandConfiguration,
        FrameACLCodegenConfiguration,
    ]
]
FrameACLCommittedConfiguration = Union[
    FrameACLViewConfiguration,
    FrameACLCommandConfiguration,
    FrameACLCodegenConfiguration,
]


class FrameACLBuilder(Cleanable):
    """

    Purpose:
        Provide the frame-local mutable ACL authoring surface for one
        `FrameACLContainer`.

    Contract:
        - One builder object exists per container.
        - At most one draft change session may be active at a time.
        - Draft state targets one ACL family and one contract name.
        - Family-specific fluent builders layer over this object; they do not
          own persistence or chain installation directly.
        - Final installation and validation are delegated to the owning
          container.
        - Uses an instance lock because draft lifecycle transitions mutate
          multiple builder-owned fields together in a nogil runtime.

    Threading:
        All grouped draft lifecycle transitions execute under the builder's
        instance `RLock`.

    Lifecycle:
        Cleanup is idempotent, cleans any still-open draft configuration, and
        then drops the borrowed container reference.

    Registration:
        MELDER KERNEL - guarded. One builder per `FrameACLContainer`; obtained
        through the container, not constructed directly.

    Subsystem Context:
        The mutable authoring surface over one frame's ACL container.
        Family-specific fluent builders layer on top of it, and the container
        itself owns persistence and chain installation.

    System Context:
        AT MOST ONE DRAFT AT A TIME, targeting one family and one contract name,
        is the invariant that makes ACL authoring safe to reason about.
        Concurrent drafts against the same container could interleave into a
        contract nobody authored, and because a chain bump fans out a projection
        refresh across every impacted Rift, a half-authored contract would
        propagate before it was coherent.
        Delegating final installation and validation to the OWNING CONTAINER is
        the matching rule: the builder stages, the container commits. That keeps
        one writer for chain state even though several fluent surfaces layer
        above it.
        The instance lock is explicitly justified by the free-threaded runtime -
        draft lifecycle transitions mutate several builder-owned fields
        together, and under 3.14t there is no GIL making that grouping
        incidentally atomic.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLBuilder runtime object. Melder kernel machinery: read it to "
        "understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_container",
        "_change_active",
        "_draft_family_name",
        "_draft_contract_name",
        "_draft_configuration",
    ]

    def __init__(self, container: FrameACLContainer) -> None:
        """
        Initialize one frame-local ACL builder.

        Args:
            container:
                Owning frame ACL container that supplies current family
                revisions, profile registries, and chain-installation methods.

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
        self._container: FrameACLContainer = container
        self._change_active: bool = False
        self._draft_family_name: Optional[str] = None
        self._draft_contract_name: Optional[str] = None
        self._draft_configuration: FrameACLDraftConfiguration = None

    def cleanup(self) -> None:
        """
        Idempotently tear down the builder and any still-open draft.

        Contract:
            - If a draft configuration is still open, it is cleaned before the
              builder drops its references.
            - After cleanup, the builder must not be used again.

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
            del self._draft_configuration
            del self._draft_family_name
            del self._draft_contract_name
            del self._container
            del self._change_active
        del self._lock

    @property
    def change_active(self) -> bool:
        """
        Return whether the builder currently owns one open change session.

        Returns:
            bool: True when a change session is active.
        """
        self.check_cleaned()
        with self._lock:
            return self._change_active

    @property
    def draft_family_name(self) -> Optional[str]:
        """
        Return the ACL family currently targeted by the draft session.

        Returns:
            Optional[str]: Draft family name when one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._draft_family_name

    @property
    def draft_contract_name(self) -> Optional[str]:
        """
        Return the contract name currently targeted by the draft session.

        Returns:
            Optional[str]: Draft contract name when one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._draft_contract_name

    def begin_change(
            self,
            family_name: str,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> None:
        """
        Start one builder-owned family draft session.

        Args:
            family_name:
                ACL family to edit: `view`, `command`, or `codegen`.
            contract_name:
                Named contract inside that family.
            reason:
                Human-readable reason recorded on the new draft node.

        Returns:
            None.

        Raises:
            RuntimeError:
                If another draft session is already active.
            ValueError:
                If `family_name` is not one of the supported ACL families.
        """
        self.check_cleaned()
        with self._lock:
            if self._change_active:
                raise RuntimeError("FrameACLBuilder already has an active change.")
            if family_name == "view":
                self._draft_configuration = (
                    self._container.create_new_from_view_configuration(
                        self._container.get_current_view_configuration(
                            contract_name
                        ).configuration_id,
                        contract_name=contract_name,
                        reason=reason,
                    )
                )
            elif family_name == "command":
                self._draft_configuration = (
                    self._container.create_new_from_command_configuration(
                        self._container.get_current_command_configuration(
                            contract_name
                        ).configuration_id,
                        contract_name=contract_name,
                        reason=reason,
                    )
                )
            elif family_name == "codegen":
                self._draft_configuration = (
                    self._container.create_new_from_codegen_configuration(
                        self._container.get_current_codegen_configuration(
                            contract_name
                        ).configuration_id,
                        contract_name=contract_name,
                        reason=reason,
                    )
                )
            else:
                raise ValueError(
                    "family_name must be 'view', 'command', or 'codegen'."
                )
            self._draft_family_name = family_name
            self._draft_contract_name = contract_name
            self._change_active = True

    def begin_view_change(
            self,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> FrameACLViewBuilder:
        """
        Start one view-family draft and return its fluent builder.

        Args:
            contract_name:
                Named view contract to edit.
            reason:
                Human-readable draft reason.

        Returns:
            FrameACLViewBuilder: Fluent builder over the active view draft.
        """
        self.begin_change(
            "view",
            contract_name=contract_name,
            reason=reason,
        )
        return FrameACLViewBuilder(self)

    def begin_command_change(
            self,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> FrameACLCommandBuilder:
        """
        Start one command-family draft and return its fluent builder.

        Args:
            contract_name:
                Named command contract to edit.
            reason:
                Human-readable draft reason.

        Returns:
            FrameACLCommandBuilder: Fluent builder over the active command draft.
        """
        self.begin_change(
            "command",
            contract_name=contract_name,
            reason=reason,
        )
        return FrameACLCommandBuilder(self)

    def begin_codegen_change(
            self,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> FrameACLCodegenBuilder:
        """
        Start one codegen-family draft and return its fluent builder.

        Args:
            contract_name:
                Named codegen contract to edit.
            reason:
                Human-readable draft reason.

        Returns:
            FrameACLCodegenBuilder: Fluent builder over the active codegen draft.
        """
        self.begin_change(
            "codegen",
            contract_name=contract_name,
            reason=reason,
        )
        return FrameACLCodegenBuilder(self)

    def _require_active_codegen_configuration(
            self,
    ) -> FrameACLCodegenConfiguration:
        """
        Return the active codegen draft configuration or raise.

        Returns:
            FrameACLCodegenConfiguration: Active codegen draft configuration.

        Raises:
            RuntimeError:
                If there is no active draft or the active draft is not codegen.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name != "codegen":
                raise RuntimeError("FrameACLBuilder has no active codegen change.")
            if not isinstance(
                    self._draft_configuration,
                    FrameACLCodegenConfiguration,
            ):
                raise RuntimeError(
                    "FrameACLBuilder active codegen draft does not satisfy "
                    "FrameACLCodegenConfiguration."
                )
            return self._draft_configuration

    def _require_active_view_configuration(
            self,
    ) -> FrameACLViewConfiguration:
        """
        Return the active view draft configuration or raise.

        Returns:
            FrameACLViewConfiguration: Active view draft configuration.

        Raises:
            RuntimeError:
                If there is no active draft or the active draft is not view.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name != "view":
                raise RuntimeError("FrameACLBuilder has no active view change.")
            if not isinstance(
                    self._draft_configuration,
                    FrameACLViewConfiguration,
            ):
                raise RuntimeError(
                    "FrameACLBuilder active view draft does not satisfy "
                    "FrameACLViewConfiguration."
                )
            return self._draft_configuration

    def _require_active_command_configuration(
            self,
    ) -> FrameACLCommandConfiguration:
        """
        Return the active command draft configuration or raise.

        Returns:
            FrameACLCommandConfiguration: Active command draft configuration.

        Raises:
            RuntimeError:
                If there is no active draft or the active draft is not command.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name != "command":
                raise RuntimeError("FrameACLBuilder has no active command change.")
            if not isinstance(
                    self._draft_configuration,
                    FrameACLCommandConfiguration,
            ):
                raise RuntimeError(
                    "FrameACLBuilder active command draft does not satisfy "
                    "FrameACLCommandConfiguration."
                )
            return self._draft_configuration

    def _require_active_contract_name(self) -> str:
        """
        Return the active draft contract name or raise.

        Returns:
            str: Active draft contract name.

        Raises:
            RuntimeError:
                If there is no active draft or the contract name is missing.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_contract_name is None:
                raise RuntimeError("FrameACLBuilder has no active contract name.")
            return self._draft_contract_name

    def apply_frame_acl_profile(
            self,
            frame_acl_profile: FrameACLProfile,
    ) -> None:
        """
        Apply one composed ACL profile into the active family draft.

        Args:
            frame_acl_profile:
                Composed ACL profile to apply.

        Returns:
            None.

        Raises:
            TypeError:
                If `frame_acl_profile` does not satisfy the composed ACL
                profile contract.
            RuntimeError:
                If no draft session is active.
        """
        self.check_cleaned()
        if not isinstance(frame_acl_profile, FrameACLProfile):
            raise TypeError(
                "frame_acl_profile must be a FrameACLProfile instance."
            )
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name == "view":
                view_configuration = self._require_active_view_configuration()
                view_configuration.cleanup()
                self._draft_configuration = FrameACLViewConfiguration.from_profile(
                    frame_acl_profile.view_profile,
                    frame_override_ruleset=(
                        frame_acl_profile.view_override_ruleset.clone()
                    ),
                    reason="builder_profile_apply",
                    locked=False,
                )
                return
            if self._draft_family_name == "command":
                command_configuration = self._require_active_command_configuration()
                command_configuration.cleanup()
                self._draft_configuration = (
                    FrameACLCommandConfiguration.from_profile(
                        frame_acl_profile.command_profile,
                        member_override_ruleset=(
                            frame_acl_profile.command_override_ruleset.clone()
                        ),
                        reason="builder_profile_apply",
                        locked=False,
                    )
                )
                return
            if self._draft_family_name == "codegen":
                codegen_configuration = self._require_active_codegen_configuration()
                codegen_configuration.cleanup()
                self._draft_configuration = (
                    FrameACLCodegenConfiguration.from_profile(
                        frame_acl_profile.codegen_profile,
                        capability_override_ruleset=(
                            frame_acl_profile.codegen_override_ruleset.clone()
                        ),
                        reason="builder_profile_apply",
                        locked=False,
                    )
                )
                return
            raise RuntimeError("FrameACLBuilder has no draft family.")

    def set_profile_name(self, profile_name: str) -> None:
        """
        Replace the base profile identity on the active family draft.

        Args:
            profile_name:
                Registered base profile name for the active family.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no draft session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            profile_builder = self._container.frame_acl_profile_builder
            if self._draft_family_name == "view":
                view_configuration = self._require_active_view_configuration()
                view_configuration.set_profiles(
                    profile_builder.get_required_view_profile(profile_name),
                    precision_profile=(
                        profile_builder.get_required_view_precision_profile(
                            view_configuration.precision_profile_name
                        )
                        if view_configuration.precision_profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "command":
                command_configuration = self._require_active_command_configuration()
                command_configuration.set_profiles(
                    profile_builder.get_required_command_profile(profile_name),
                    precision_profile=(
                        profile_builder.get_required_command_precision_profile(
                            command_configuration.precision_profile_name
                        )
                        if command_configuration.precision_profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "codegen":
                codegen_configuration = self._require_active_codegen_configuration()
                codegen_configuration.set_profiles(
                    profile_builder.get_required_codegen_profile(profile_name),
                    precision_profile=(
                        profile_builder.get_required_codegen_precision_profile(
                            codegen_configuration.precision_profile_name
                        )
                        if codegen_configuration.precision_profile_name is not None
                        else None
                    ),
                )
                return
            raise RuntimeError("FrameACLBuilder has no draft family.")

    def set_precision_profile_name(
            self,
            profile_name: Optional[str],
    ) -> None:
        """
        Replace the precision profile identity on the active family draft.

        Args:
            profile_name:
                Registered precision profile name for the active family, or
                None to clear precision selection.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no draft session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            profile_builder = self._container.frame_acl_profile_builder
            if self._draft_family_name == "view":
                view_configuration = self._require_active_view_configuration()
                view_configuration.set_profiles(
                    profile_builder.get_required_view_profile(
                        view_configuration.profile_name
                    ),
                    precision_profile=(
                        profile_builder.get_required_view_precision_profile(profile_name)
                        if profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "command":
                command_configuration = self._require_active_command_configuration()
                command_configuration.set_profiles(
                    profile_builder.get_required_command_profile(
                        command_configuration.profile_name
                    ),
                    precision_profile=(
                        profile_builder.get_required_command_precision_profile(
                            profile_name
                        )
                        if profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "codegen":
                codegen_configuration = self._require_active_codegen_configuration()
                codegen_configuration.set_profiles(
                    profile_builder.get_required_codegen_profile(
                        codegen_configuration.profile_name
                    ),
                    precision_profile=(
                        profile_builder.get_required_codegen_precision_profile(
                            profile_name
                        )
                        if profile_name is not None
                        else None
                    ),
                )
                return
            raise RuntimeError("FrameACLBuilder has no draft family.")

    def load_json_configuration_string(
            self,
            json_configuration_string: str,
    ) -> None:
        """
        Replace the active family draft from a JSON payload string.

        Args:
            json_configuration_string:
                JSON payload string for the current draft family.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no draft session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            self._draft_configuration.cleanup()
            payload = json.loads(json_configuration_string)
            if self._draft_family_name == "view":
                self._draft_configuration = FrameACLViewConfiguration.from_json_dict(
                    payload,
                    reason="builder_json_load",
                    locked=False,
                )
            elif self._draft_family_name == "command":
                self._draft_configuration = (
                    FrameACLCommandConfiguration.from_json_dict(
                        payload,
                        reason="builder_json_load",
                        locked=False,
                    )
                )
            elif self._draft_family_name == "codegen":
                self._draft_configuration = (
                    FrameACLCodegenConfiguration.from_json_dict(
                        payload,
                        reason="builder_json_load",
                        locked=False,
                    )
                )
            else:
                raise RuntimeError("FrameACLBuilder has no draft family.")

    def commit_change(self) -> FrameACLCommittedConfiguration:
        """
        Finalize and install the next family configuration revision.

        Returns:
            FrameACLCommittedConfiguration: Newly installed family configuration
            revision for the active family.

        Raises:
            RuntimeError:
                If no draft session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            contract_name = self._require_active_contract_name()
            next_configuration: FrameACLCommittedConfiguration
            if self._draft_family_name == "view":
                view_configuration = self._require_active_view_configuration()
                view_configuration.finalize()
                next_configuration = self._container.insert_head_view_configuration(
                    view_configuration,
                    contract_name=contract_name,
                    select_as_current=True,
                )
            elif self._draft_family_name == "command":
                command_configuration = self._require_active_command_configuration()
                command_configuration.finalize()
                next_configuration = self._container.insert_head_command_configuration(
                    command_configuration,
                    contract_name=contract_name,
                    select_as_current=True,
                )
            elif self._draft_family_name == "codegen":
                codegen_configuration = self._require_active_codegen_configuration()
                codegen_configuration.finalize()
                next_configuration = self._container.insert_head_codegen_configuration(
                    codegen_configuration,
                    contract_name=contract_name,
                    select_as_current=True,
                )
            else:
                raise RuntimeError("FrameACLBuilder has no draft family.")
            self._draft_configuration = None
            self._draft_family_name = None
            self._draft_contract_name = None
            self._change_active = False
            return next_configuration

    def discard_change(self) -> None:
        """
        Discard the current builder-owned change session.

        Contract:
            - Cleans the draft configuration when one exists.
            - Clears draft family/session state so a later draft may begin.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._draft_configuration is not None:
                self._draft_configuration.cleanup()
            self._draft_configuration = None
            self._draft_family_name = None
            self._draft_contract_name = None
            self._change_active = False
