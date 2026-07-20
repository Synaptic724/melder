import threading
from typing import TYPE_CHECKING, Optional, Set, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.validator.compatibility.frame_acl_set_compatibility_report import (
    FrameACLSetCompatibilityReport,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)

class FrameACLSetCompatibilityValidator(Cleanable):
    """

    Purpose:
        Validate whether one selected frame ACL bundle is internally coherent
        across view, command, and codegen policy layers.

    Contract:
        - Operates on a fully typed `FrameACLConfiguration` bundle.
        - Resolves reusable view/codegen profiles through the shared ACL
          profile builder so warnings/errors reflect effective policy, not just
          local overrides.
        - Produces a detached compatibility report for diagnostics.
        - Raises on compatibility-report errors while preserving warnings for
          caller inspection.

    Lifecycle:
        Cleanup is idempotent and clears the last report plus the profile
        builder reference.

    Registration:
        MELDER KERNEL - guarded. A container-owned validator service.

    Subsystem Context:
        The CROSS-FAMILY coherence check, paired with the structural
        `FrameACLValidator`. It produces a detached
        `FrameACLSetCompatibilityReport`.

    System Context:
        This validator exists because the three ACL families are independently
        versioned, and independence permits incoherence. A command chain may
        grant an operation whose results the view chain will not surface, or a
        codegen posture may assume reach the command posture denies. Neither
        chain is wrong alone; the BUNDLE is.
        Resolving reusable profiles rather than reading local overrides alone is
        essential to that judgement, since effective policy is profile plus
        override.
        The severity split is deliberate: it RAISES on errors while preserving
        warnings for the caller. An incoherent bundle must not commit, but a
        merely suspicious one should be reported and allowed - ACL authoring
        legitimately passes through intermediate shapes an operator understands
        better than the validator does.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLSetCompatibilityValidator runtime object. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_profile_builder",
        "_last_report",
    ]

    def __init__(
            self,
            frame_name: str,
            profile_builder: IFrameACLProfileBuilder,
    ) -> None:
        """
        Initialize one frame-scoped ACL set compatibility validator.

        Args:
            frame_name:
                Owning frame name.
            profile_builder:
                Shared ACL profile builder/library used to resolve effective
                view and codegen profile semantics.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
            TypeError:
                If `profile_builder` is None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if profile_builder is None:
            raise TypeError("profile_builder cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._profile_builder: IFrameACLProfileBuilder = profile_builder
        self._last_report: Optional[FrameACLSetCompatibilityReport] = None

    def cleanup(self) -> None:
        """
        Idempotently clear validator-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._last_report is not None:
                self._last_report.cleanup()
            del self._last_report
            del self._profile_builder
            del self._frame_name
            del self._id
        del self._lock

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name for this validator.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def last_report(self) -> Optional[FrameACLSetCompatibilityReport]:
        """
        Return the most recent compatibility report when one exists.

        Returns:
            Optional[FrameACLSetCompatibilityReport]: Last report snapshot.
        """
        self.check_cleaned()
        with self._lock:
            return self._last_report

    def validate_configuration(
            self,
            configuration: FrameACLConfiguration,
    ) -> FrameACLSetCompatibilityReport:
        """
        Validate one selected frame ACL bundle for cross-set compatibility.

        Contract:
            - Confirms frame-name alignment for the bundle.
            - Builds a detached report of warnings/errors based on effective
              view, command, and codegen policy.
            - Raises if the report contains errors.

        Args:
            configuration:
                Typed frame ACL bundle to validate.

        Returns:
            FrameACLSetCompatibilityReport: Compatibility validation report.

        Raises:
            TypeError:
                If `configuration` is not a `FrameACLConfiguration`.
            ValueError:
                If the bundle targets another frame or compatibility errors are
                detected.
        """
        self.check_cleaned()
        with self._lock:
            if not isinstance(configuration, FrameACLConfiguration):
                raise TypeError(
                    "configuration must be a FrameACLConfiguration instance."
                )
            if configuration.frame_name != self._frame_name:
                raise ValueError(
                    "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                        configuration.frame_name,
                        self._frame_name,
                    )
                )
            report = FrameACLSetCompatibilityReport(
                frame_name=configuration.frame_name,
                configuration_id=configuration.configuration_id,
            )
            if self._last_report is not None:
                self._last_report.cleanup()
            self._last_report = report

            self._validate_view_and_command(
                report,
                configuration.view_configuration,
                configuration.command_configuration,
            )
            self._validate_command_and_codegen(
                report,
                configuration.command_configuration,
                configuration.codegen_configuration,
            )

            if report.has_errors:
                raise ValueError(
                    "Frame ACL bundle compatibility validation failed for frame '{0}': {1}".format(
                        configuration.frame_name,
                        "; ".join(report.errors),
                    )
                )
            return report

    def _validate_view_and_command(
            self,
            report: FrameACLSetCompatibilityReport,
            view_configuration: FrameACLViewConfiguration,
            command_configuration: FrameACLCommandConfiguration,
    ) -> None:
        """
        Validate view/command compatibility for the effective bundle.

        Args:
            report:
                Report collecting warnings/errors.
            view_configuration:
                Typed view-side configuration.
            command_configuration:
                Typed command-side configuration.

        Returns:
            None.
        """
        view_profile = self._profile_builder.get_required_view_profile(
            view_configuration.profile_name
        )
        view_precision_profile = (
            self._profile_builder.get_required_view_precision_profile(
                view_configuration.precision_profile_name
            )
            if view_configuration.precision_profile_name is not None
            else None
        )
        command_profile = self._profile_builder.get_required_command_profile(
            command_configuration.profile_name
        )
        command_precision_profile = (
            self._profile_builder.get_required_command_precision_profile(
                command_configuration.precision_profile_name
            )
            if command_configuration.precision_profile_name is not None
            else None
        )
        self._check_visibility_vs_enable(
            report,
            family_label="frame",
            view_rulesets=(
                view_profile.frame_ruleset,
                view_precision_profile.frame_ruleset
                if view_precision_profile is not None
                else None,
            ),
            view_override_ruleset=view_configuration.frame_override_ruleset,
            command_rulesets=(
                command_profile.frame_ruleset,
                command_precision_profile.frame_ruleset
                if command_precision_profile is not None
                else None,
            ),
            command_override_ruleset=command_configuration.frame_override_ruleset,
            view_operation="visible",
            command_operation="enable",
        )
        self._check_visibility_vs_enable(
            report,
            family_label="conduit",
            view_rulesets=(
                view_profile.conduit_ruleset,
                view_precision_profile.conduit_ruleset
                if view_precision_profile is not None
                else None,
            ),
            view_override_ruleset=view_configuration.conduit_override_ruleset,
            command_rulesets=(
                command_profile.conduit_ruleset,
                command_precision_profile.conduit_ruleset
                if command_precision_profile is not None
                else None,
            ),
            command_override_ruleset=command_configuration.conduit_override_ruleset,
            view_operation="visible",
            command_operation="enable",
        )
        self._check_visibility_vs_enable(
            report,
            family_label="spell",
            view_rulesets=(
                view_profile.spell_ruleset,
                view_precision_profile.spell_ruleset
                if view_precision_profile is not None
                else None,
            ),
            view_override_ruleset=view_configuration.spell_override_ruleset,
            command_rulesets=(
                command_profile.spell_ruleset,
                command_precision_profile.spell_ruleset
                if command_precision_profile is not None
                else None,
            ),
            command_override_ruleset=command_configuration.spell_override_ruleset,
            view_operation="visible",
            command_operation="enable",
        )
        self._check_member_visibility_vs_command(
            report,
            view_rulesets=(
                view_profile.member_ruleset,
                view_precision_profile.member_ruleset
                if view_precision_profile is not None
                else None,
            ),
            view_override_ruleset=view_configuration.member_override_ruleset,
            command_rulesets=(
                command_profile.member_ruleset,
                command_precision_profile.member_ruleset
                if command_precision_profile is not None
                else None,
            ),
            command_override_ruleset=command_configuration.member_override_ruleset,
        )

    def _validate_command_and_codegen(
            self,
            report: FrameACLSetCompatibilityReport,
            command_configuration: FrameACLCommandConfiguration,
            codegen_configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Validate command/codegen compatibility for the effective bundle.

        Args:
            report:
                Report collecting warnings/errors.
            command_configuration:
                Typed command-side configuration.
            codegen_configuration:
                Typed codegen-side configuration.

        Returns:
            None.
        """
        command_profile = self._profile_builder.get_required_command_profile(
            command_configuration.profile_name
        )
        command_precision_profile = (
            self._profile_builder.get_required_command_precision_profile(
                command_configuration.precision_profile_name
            )
            if command_configuration.precision_profile_name is not None
            else None
        )
        codegen_profile = self._profile_builder.get_required_codegen_profile(
            codegen_configuration.profile_name
        )
        codegen_precision_profile = (
            self._profile_builder.get_required_codegen_precision_profile(
                codegen_configuration.precision_profile_name
            )
            if codegen_configuration.precision_profile_name is not None
            else None
        )
        command_spell_allows, command_spell_denies = self._collect_effective_operation_effects_from_rulesets(
            command_profile.spell_ruleset,
            (
                command_precision_profile.spell_ruleset
                if command_precision_profile is not None
                else None
            ),
            command_configuration.spell_override_ruleset,
        )
        command_member_allows, command_member_denies = (
            self._collect_effective_operation_effects_from_rulesets(
                command_profile.member_ruleset,
                (
                    command_precision_profile.member_ruleset
                    if command_precision_profile is not None
                    else None
                ),
                command_configuration.member_override_ruleset,
            )
        )
        codegen_spell_allows, codegen_spell_denies = self._collect_effective_operation_effects_from_rulesets(
            codegen_profile.spell_ruleset,
            (
                codegen_precision_profile.spell_ruleset
                if codegen_precision_profile is not None
                else None
            ),
            codegen_configuration.spell_override_ruleset,
        )
        if (
                "enable" not in command_spell_allows
                or "enable" in command_spell_denies
        ):
            if len(command_member_allows) > 0:
                report.add_error(
                    "command.member enables actions while command.spell does not enable spell access."
                )
        codegen_action_ops = {
            "invoke_method",
            "read_attribute",
            "write_attribute",
        }
        effective_codegen_actions = (
            codegen_spell_allows.intersection(codegen_action_ops).difference(
                codegen_spell_denies
            )
        )
        effective_command_actions = command_member_allows.difference(
            command_member_denies
        )
        if len(effective_codegen_actions.difference(effective_command_actions)) > 0:
            report.add_warning(
                "codegen.spell allows action operations that command.member does not permit."
            )

    def _check_visibility_vs_enable(
            self,
            report: FrameACLSetCompatibilityReport,
            *,
            family_label: str,
            view_rulesets: Tuple[Optional[FrameACLRuleSet], ...],
            view_override_ruleset: FrameACLRuleSet,
            command_rulesets: Tuple[Optional[FrameACLRuleSet], ...],
            command_override_ruleset: FrameACLRuleSet,
            view_operation: str,
            command_operation: str,
    ) -> None:
        """
        Compare one view visibility family to one command enable family.

        Args:
            report:
                Report collecting warnings/errors.
            family_label:
                Human-readable family name.
            view_rulesets:
                Base and precision reusable view rulesets.
            view_override_ruleset:
                View override ruleset for the family.
            command_rulesets:
                Base and precision reusable command rulesets.
            command_override_ruleset:
                Command override ruleset for the family.
            view_operation:
                View operation to evaluate.
            command_operation:
                Command operation to evaluate.

        Returns:
            None.
        """
        view_allows, view_denies = self._collect_effective_operation_effects_from_rulesets(
            *view_rulesets,
            view_override_ruleset,
        )
        command_allows, command_denies = self._collect_effective_operation_effects_from_rulesets(
            *command_rulesets,
            command_override_ruleset,
        )
        command_has_policy = len(command_allows.union(command_denies)) > 0
        view_enabled = (
            view_operation in view_allows
            and view_operation not in view_denies
        )
        command_enabled = (
            command_operation in command_allows
            and command_operation not in command_denies
        )
        if view_enabled and not command_enabled and command_has_policy:
            report.add_warning(
                "view.{0} is visible while command.{0} is not enabled.".format(
                    family_label
                )
            )
        if command_enabled and not view_enabled:
            report.add_warning(
                "command.{0} is enabled while view.{0} is not visible.".format(
                    family_label
                )
            )

    def _check_member_visibility_vs_command(
            self,
            report: FrameACLSetCompatibilityReport,
            *,
            view_rulesets: Tuple[Optional[FrameACLRuleSet], ...],
            view_override_ruleset: FrameACLRuleSet,
            command_rulesets: Tuple[Optional[FrameACLRuleSet], ...],
            command_override_ruleset: FrameACLRuleSet,
    ) -> None:
        """
        Compare member-level view exposure to member-level command actions.

        Args:
            report:
                Report collecting warnings/errors.
            view_ruleset:
                Base reusable member-view ruleset.
            view_override_ruleset:
                View override member ruleset.
            command_ruleset:
                Command member ruleset.

        Returns:
            None.
        """
        view_allows, view_denies = self._collect_effective_operation_effects_from_rulesets(
            *view_rulesets,
            view_override_ruleset,
        )
        command_allows, command_denies = self._collect_effective_operation_effects_from_rulesets(
            *command_rulesets,
            command_override_ruleset,
        )
        command_has_policy = len(command_allows.union(command_denies)) > 0
        view_members_visible = (
            "show_member" in view_allows
            and "show_member" not in view_denies
        )
        command_member_actions = command_allows.difference(command_denies)
        if (
                view_members_visible
                and len(command_member_actions) == 0
                and command_has_policy
        ):
            report.add_warning(
                "view.member exposes members while command.member permits no member actions."
            )
        if len(command_member_actions) > 0 and not view_members_visible:
            report.add_warning(
                "command.member permits actions while view.member does not expose members."
            )

    @staticmethod
    def _collect_operation_effects(
            ruleset: FrameACLRuleSet,
    ) -> Tuple[Set[str], Set[str]]:
        """
        Collect allow/deny operations from one ruleset.

        Args:
            ruleset:
                Ruleset to inspect.

        Returns:
            Tuple[Set[str], Set[str]]: Allow and deny operation names.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for rule in ruleset.rules_by_name.values():
            if rule.effect == "allow":
                allow_operations.add(rule.operation)
            elif rule.effect == "deny":
                deny_operations.add(rule.operation)
        return allow_operations, deny_operations

    @staticmethod
    def _collect_effective_operation_effects(
            base_ruleset: FrameACLRuleSet,
            override_ruleset: FrameACLRuleSet,
    ) -> Tuple[Set[str], Set[str]]:
        """
        Collect effective allow/deny operations from base plus override rules.

        Args:
            base_ruleset:
                Base reusable profile ruleset.
            override_ruleset:
                Applied configuration override ruleset.

        Returns:
            Tuple[Set[str], Set[str]]: Effective allow and deny operation names.
        """
        base_allows, base_denies = (
            FrameACLSetCompatibilityValidator._collect_operation_effects(
                base_ruleset
            )
        )
        override_allows, override_denies = (
            FrameACLSetCompatibilityValidator._collect_operation_effects(
                override_ruleset
            )
        )
        return (
            base_allows.union(override_allows),
            base_denies.union(override_denies),
        )

    @staticmethod
    def _collect_effective_operation_effects_from_rulesets(
            *rulesets: Optional[FrameACLRuleSet],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Merge an ordered list of base/precision/override rulesets into one effect set.

        Returns:
            Tuple[Set[str], Set[str]]: Effective allow and deny operation names.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for ruleset in rulesets:
            if ruleset is None:
                continue
            ruleset_allows, ruleset_denies = (
                FrameACLSetCompatibilityValidator._collect_operation_effects(
                    ruleset
                )
            )
            allow_operations.update(ruleset_allows)
            deny_operations.update(ruleset_denies)
        return allow_operations, deny_operations


