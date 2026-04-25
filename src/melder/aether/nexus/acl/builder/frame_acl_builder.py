import json
import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.builder.frame_acl_command_builder import (
    FrameACLCommandBuilder,
)
from melder.aether.nexus.acl.builder.frame_acl_codegen_builder import (
    FrameACLCodegenBuilder,
)
from melder.aether.nexus.acl.builder.frame_acl_view_builder import (
    FrameACLViewBuilder,
)
from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.frame_acl_profile import FrameACLProfile
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
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
        - Draft state targets one ACL family and one contract name.
        - Final installation and validation are delegated to the owning
          container.
        - Uses an instance lock because draft lifecycle transitions and cleanup
          mutate multiple fields together in a nogil runtime.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_container",
        "_change_active",
        "_draft_family_name",
        "_draft_contract_name",
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
        """
        super().__init__()
        if container is None:
            raise TypeError("container cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._container: IFrameACLContainer = container
        self._change_active: bool = False
        self._draft_family_name: Optional[str] = None
        self._draft_contract_name: Optional[str] = None
        self._draft_configuration: Optional[object] = None

    def cleanup(self) -> None:
        """
        Idempotently clear builder state.

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
            self._draft_family_name = None
            self._draft_contract_name = None
            self._container = None
            self._change_active = None
        self._lock = None

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
        Start one view draft session and return the fluent view builder.

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
        Start one command draft session and return the fluent command builder.

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
        Start one codegen draft session and return the fluent codegen builder.

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
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name != "codegen":
                raise RuntimeError("FrameACLBuilder has no active codegen change.")
            return self._draft_configuration

    def _require_active_view_configuration(
            self,
    ) -> FrameACLViewConfiguration:
        """
        Return the active view draft configuration or raise.

        Returns:
            FrameACLViewConfiguration: Active view draft configuration.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name != "view":
                raise RuntimeError("FrameACLBuilder has no active view change.")
            return self._draft_configuration

    def _require_active_command_configuration(
            self,
    ) -> FrameACLCommandConfiguration:
        """
        Return the active command draft configuration or raise.

        Returns:
            FrameACLCommandConfiguration: Active command draft configuration.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name != "command":
                raise RuntimeError("FrameACLBuilder has no active command change.")
            return self._draft_configuration

    def apply_frame_acl_profile(
            self,
            frame_acl_profile: FrameACLProfile,
    ) -> None:
        """
        Apply one reusable ACL profile into an active family draft.

        Args:
            frame_acl_profile:
                Composed ACL profile to apply.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(frame_acl_profile, FrameACLProfile):
            raise TypeError("frame_acl_profile must be a FrameACLProfile.")
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if self._draft_family_name == "view":
                self._draft_configuration.cleanup()
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
                self._draft_configuration.cleanup()
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
                self._draft_configuration.cleanup()
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
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            profile_builder = self._container.frame_acl_profile_builder
            if self._draft_family_name == "view":
                self._draft_configuration.set_profiles(
                    profile_builder.get_required_view_profile(profile_name),
                    precision_profile=(
                        profile_builder.get_required_view_precision_profile(
                            self._draft_configuration.precision_profile_name
                        )
                        if self._draft_configuration.precision_profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "command":
                self._draft_configuration.set_profiles(
                    profile_builder.get_required_command_profile(profile_name),
                    precision_profile=(
                        profile_builder.get_required_command_precision_profile(
                            self._draft_configuration.precision_profile_name
                        )
                        if self._draft_configuration.precision_profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "codegen":
                self._draft_configuration.set_profiles(
                    profile_builder.get_required_codegen_profile(profile_name),
                    precision_profile=(
                        profile_builder.get_required_codegen_precision_profile(
                            self._draft_configuration.precision_profile_name
                        )
                        if self._draft_configuration.precision_profile_name is not None
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
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            profile_builder = self._container.frame_acl_profile_builder
            if self._draft_family_name == "view":
                self._draft_configuration.set_profiles(
                    profile_builder.get_required_view_profile(
                        self._draft_configuration.profile_name
                    ),
                    precision_profile=(
                        profile_builder.get_required_view_precision_profile(profile_name)
                        if profile_name is not None
                        else None
                    ),
                )
                return
            if self._draft_family_name == "command":
                self._draft_configuration.set_profiles(
                    profile_builder.get_required_command_profile(
                        self._draft_configuration.profile_name
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
                self._draft_configuration.set_profiles(
                    profile_builder.get_required_codegen_profile(
                        self._draft_configuration.profile_name
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
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            self._draft_configuration.cleanup()
            if self._draft_family_name == "view":
                self._draft_configuration = FrameACLViewConfiguration.from_json_dict(
                    json.loads(json_configuration_string),
                    reason="builder_json_load",
                    locked=False,
                )
            elif self._draft_family_name == "command":
                self._draft_configuration = (
                    FrameACLCommandConfiguration.from_json_dict(
                        json.loads(json_configuration_string),
                        reason="builder_json_load",
                        locked=False,
                    )
                )
            elif self._draft_family_name == "codegen":
                self._draft_configuration = (
                    FrameACLCodegenConfiguration.from_json_dict(
                        json.loads(json_configuration_string),
                        reason="builder_json_load",
                        locked=False,
                    )
                )
            else:
                raise RuntimeError("FrameACLBuilder has no draft family.")

    def commit_change(self) -> object:
        """
        Finalize and install the next family configuration revision.

        Returns:
            object: Newly installed family configuration revision.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active or self._draft_configuration is None:
                raise RuntimeError("FrameACLBuilder has no active change.")
            self._draft_configuration.finalize()
            if self._draft_family_name == "view":
                next_configuration = self._container.insert_head_view_configuration(
                    self._draft_configuration,
                    contract_name=self._draft_contract_name,
                    select_as_current=True,
                )
            elif self._draft_family_name == "command":
                next_configuration = self._container.insert_head_command_configuration(
                    self._draft_configuration,
                    contract_name=self._draft_contract_name,
                    select_as_current=True,
                )
            elif self._draft_family_name == "codegen":
                next_configuration = self._container.insert_head_codegen_configuration(
                    self._draft_configuration,
                    contract_name=self._draft_contract_name,
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
