import threading
from typing import Callable, Dict, Optional, Set, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.validator.profiles.common import (
    validate_noop_profile_configuration,
)
from melder.aether.nexus.acl.validator.profiles.codegen.precision_strategy import (
    validate_profile_configuration as validate_precision_codegen_profile_configuration,
)
from melder.aether.nexus.acl.validator.profiles.codegen.safe_strategy import (
    validate_profile_configuration as validate_safe_codegen_profile_configuration,
)
from melder.aether.nexus.acl.validator.profiles.command.precision_strategy import (
    validate_profile_configuration as validate_precision_command_profile_configuration,
)
from melder.aether.nexus.acl.validator.profiles.command.safe_strategy import (
    validate_profile_configuration as validate_safe_command_profile_configuration,
)
from melder.aether.nexus.acl.validator.profiles.view.precision_strategy import (
    validate_profile_configuration as validate_precision_view_profile_configuration,
)
from melder.aether.nexus.acl.validator.profiles.view.safe_strategy import (
    validate_profile_configuration as validate_safe_view_profile_configuration,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLValidator(Cleanable):
    """
    Purpose:
        Validate that frame-local ACL configuration nodes are structurally
        compatible with one owning frame.

    Contract:
        - Confirms that a configuration node belongs to the expected frame.
        - Validates the typed view, command, and codegen child objects carried
          by one frame ACL bundle.
        - Records the last validated configuration id for diagnostics.
        - Does not attempt to implement the full ACL rule engine in this
          placeholder slice.

    Lifecycle:
        Cleanup is idempotent and clears the last-validation marker plus the
        owning frame reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_profile_builder",
        "_owns_profile_builder",
        "_view_profile_validation_strategies_by_name",
        "_command_profile_validation_strategies_by_name",
        "_codegen_profile_validation_strategies_by_name",
        "_last_validated_configuration_id",
    ]
    _SUPPORTED_NEXUS_RECORD_CONTRACTS: Set[Tuple[str, str]] = {
        ("default", "0.0.1"),
    }
    _SUPPORTED_SPELL_PAYLOAD_TYPE_ORDER: Dict[str, int] = {
        "general": 0,
        "detailed": 1,
    }
    _SUPPORTED_SPELL_PAYLOAD_VERSIONS: Set[str] = {
        "0.0.1",
    }
    _VIEW_ALLOWED_OPERATIONS_BY_RULESET: Dict[str, Set[str]] = {
        "frame": {"visible", "show_payload"},
        "conduit": {
            "visible",
            "show_payload",
            "show_policy",
            "show_peer_links",
        },
        "spell": {
            "visible",
            "show_binding_payload",
            "show_resolution_payload",
            "show_class_profile",
            "show_callable_profile",
            "show_metadata",
            "show_instance_members",
            "show_dynamic_access",
        },
        "member": {"show_member"},
    }
    _CODEGEN_ALLOWED_OPERATIONS_BY_RULESET: Dict[str, Set[str]] = {
        "frame": {"query"},
        "conduit": {
            "query",
            "link",
            "unlink",
            "create_lesser_conduit",
            "transfer_ownership",
        },
        "spell": {
            "resolve_existing",
            "bind_existing",
            "local_create",
            "invoke_method",
            "read_attribute",
            "write_attribute",
        },
        "capability": {
            "enable_imports",
            "import_modules",
            "builtin_names",
            "dynamic_access",
            "mutation",
            "contract_override",
            "unsafe_reflection",
            "dunder_access",
            "recursive_codegen",
        },
    }
    _COMMAND_ALLOWED_OPERATIONS_BY_RULESET: Dict[str, Set[str]] = {
        "frame": {"enable"},
        "conduit": {"enable"},
        "spell": {"enable"},
        "member": {
            "invoke_method",
            "read_attribute",
            "write_attribute",
            "dunder_access",
        },
    }
    def __init__(
            self,
            frame_name: str,
            profile_builder: Optional[FrameACLProfileBuilder] = None,
    ) -> None:
        """
        Initialize one frame-scoped ACL validator.

        Purpose:
            Bind the validator to one owning frame name.

        Contract:
            `frame_name` must be a non-empty stable frame identity.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._owns_profile_builder: bool = profile_builder is None
        if profile_builder is None:
            profile_builder = FrameACLProfileBuilder()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._profile_builder: FrameACLProfileBuilder = profile_builder
        self._view_profile_validation_strategies_by_name = {
            "generic": validate_noop_profile_configuration,
            "safe": validate_safe_view_profile_configuration,
            "precision": validate_precision_view_profile_configuration,
        }
        self._command_profile_validation_strategies_by_name = {
            "generic": validate_noop_profile_configuration,
            "safe": validate_safe_command_profile_configuration,
            "precision": validate_precision_command_profile_configuration,
        }
        self._codegen_profile_validation_strategies_by_name = {
            "generic": validate_noop_profile_configuration,
            "safe": validate_safe_codegen_profile_configuration,
            "precision": validate_precision_codegen_profile_configuration,
        }
        self._last_validated_configuration_id: Optional[str] = None

    def cleanup(self) -> None:
        """
        Idempotently clear validator state.

        Purpose:
            Tear down the validator's frame binding and last-validation marker.

        Contract:
            Safe to call more than once.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._owns_profile_builder and self._profile_builder is not None:
                self._profile_builder.cleanup()
            del self._frame_name
            del self._profile_builder
            del self._owns_profile_builder
            del self._view_profile_validation_strategies_by_name
            del self._command_profile_validation_strategies_by_name
            del self._codegen_profile_validation_strategies_by_name
            del self._last_validated_configuration_id
            del self._id
        del self._lock

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Purpose:
            Expose the stable frame identity this validator enforces.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def last_validated_configuration_id(self) -> Optional[str]:
        """
        Return the last validated configuration id when known.

        Purpose:
            Expose the most recent successful validation target for diagnostics.

        Returns:
            Optional[str]: Last validated configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._last_validated_configuration_id

    def validate_configuration(
            self,
            configuration: FrameACLConfiguration,
    ) -> bool:
        """
        Validate one frame ACL configuration against this validator's frame.

        Purpose:
            Confirm that a candidate configuration node belongs to the same
            frame as the validator.

        Contract:
            - Enforces frame-name alignment for the root bundle.
            - Validates view, command, and codegen child configurations as one
              coherent bundle.
            - Records the validated configuration id only after all child
              validation passes.

        Args:
            configuration:
                Candidate frame ACL configuration node.

        Returns:
            bool: True when the configuration belongs to the same frame.

        Raises:
            TypeError:
                If `configuration` is not a `FrameACLConfiguration`.
            ValueError:
                If the configuration targets another frame or one child
                configuration violates its ruleset contract.
        """
        self.check_cleaned()
        with self._lock:
            if not isinstance(configuration, FrameACLConfiguration):
                raise TypeError("configuration must be a FrameACLConfiguration.")
            if configuration.frame_name != self._frame_name:
                raise ValueError(
                    "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                        configuration.frame_name,
                        self._frame_name,
                    )
                )
            self._validate_view_configuration(configuration.view_configuration)
            self._validate_command_configuration(configuration.command_configuration)
            self._validate_codegen_configuration(configuration.codegen_configuration)
            self._last_validated_configuration_id = configuration.configuration_id
            return True

    def validate_configuration_against_descriptor(
            self,
            configuration: FrameACLConfiguration,
            frame_descriptor: FrameDescriptor,
    ) -> bool:
        """
        Validate one frame ACL configuration against descriptor payload truth.

        Args:
            configuration:
                Candidate frame ACL configuration node.
            frame_descriptor:
                Descriptor truth for the same frame.

        Returns:
            bool: True when the configuration is structurally valid and the
                descriptor payload contracts satisfy the ACL requirements.
        """
        self._validate_configuration_shape_only(configuration)
        if not isinstance(frame_descriptor, FrameDescriptor):
            raise TypeError("frame_descriptor must be a FrameDescriptor.")
        if frame_descriptor.frame_name != self._frame_name:
            raise ValueError(
                "FrameDescriptor targets frame '{0}', expected '{1}'.".format(
                    frame_descriptor.frame_name,
                    self._frame_name,
                )
            )
        self._validate_descriptor_record_contracts(
            frame_descriptor,
            configuration.view_configuration,
        )
        self._validate_spell_selector_rules_against_descriptor(
            frame_descriptor,
            configuration,
        )
        return True

    def _validate_configuration_shape_only(
            self,
            configuration: FrameACLConfiguration,
    ) -> None:
        """
        Validate the configuration bundle without resolving reusable profiles.

        Returns:
            None.
        """
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError("configuration must be a FrameACLConfiguration.")
        if configuration.frame_name != self._frame_name:
            raise ValueError(
                "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                    configuration.frame_name,
                    self._frame_name,
                )
            )
        self._validate_view_configuration_shape_only(
            configuration.view_configuration
        )
        self._validate_command_configuration_shape_only(
            configuration.command_configuration
        )
        self._validate_codegen_configuration_shape_only(
            configuration.codegen_configuration
        )

    def _validate_view_configuration(
            self,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate the typed view-side configuration object.

        Args:
            view_configuration:
                Typed view-side configuration to validate.

        Returns:
            None.
        """
        self._validate_view_configuration_shape_only(view_configuration)
        base_profile = self._profile_builder.get_required_view_profile(
            view_configuration.profile_name
        )
        if view_configuration.profile_version != base_profile.version:
            raise ValueError(
                "View configuration profile version '{0}' does not match reusable profile version '{1}' for '{2}'.".format(
                    view_configuration.profile_version,
                    base_profile.version,
                    view_configuration.profile_name,
                )
            )
        precision_profile = None
        if view_configuration.precision_profile_name is not None:
            precision_profile = self._profile_builder.get_required_view_precision_profile(
                view_configuration.precision_profile_name
            )
            if (
                    view_configuration.precision_profile_version !=
                    precision_profile.version
            ):
                raise ValueError(
                    "View configuration precision profile version '{0}' does not match reusable precision profile version '{1}' for '{2}'.".format(
                        view_configuration.precision_profile_version,
                        precision_profile.version,
                        view_configuration.precision_profile_name,
                    )
                )
        (
            expected_nexus_label,
            expected_nexus_version,
            expected_payload_type,
            expected_payload_version,
        ) = FrameACLViewConfiguration._resolve_effective_contract_fields(
            base_profile,
            precision_profile,
        )
        if view_configuration.required_nexus_label != expected_nexus_label:
            raise ValueError(
                "View configuration required_nexus_label does not match selected base/precision profiles."
            )
        if view_configuration.required_nexus_version != expected_nexus_version:
            raise ValueError(
                "View configuration required_nexus_version does not match selected base/precision profiles."
            )
        if view_configuration.minimum_spell_payload_type != expected_payload_type:
            raise ValueError(
                "View configuration minimum_spell_payload_type does not match selected base/precision profiles."
            )
        if (
                view_configuration.minimum_spell_payload_version !=
                expected_payload_version
        ):
            raise ValueError(
                "View configuration minimum_spell_payload_version does not match selected base/precision profiles."
            )
        self._run_view_profile_validation(base_profile, view_configuration)
        if precision_profile is not None:
            self._run_view_profile_validation(
                precision_profile,
                view_configuration,
            )

    def _validate_descriptor_record_contracts(
            self,
            frame_descriptor: FrameDescriptor,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate descriptor record contracts against one ACL view config.

        Args:
            frame_descriptor:
                Descriptor truth for the target frame.
            view_configuration:
                Typed ACL view configuration with required payload contracts.

        Returns:
            None.
        """
        frame_overview = frame_descriptor.frame_overview
        if frame_overview is None:
            raise ValueError(
                "FrameDescriptor for frame '{0}' has no frame_overview for record-contract validation.".format(
                    frame_descriptor.frame_name
                )
            )
        self._assert_exact_nexus_record_contract(
            actual_nexus_label=frame_overview.nexus_label,
            actual_nexus_version=frame_overview.nexus_version,
            required_nexus_label=view_configuration.required_nexus_label,
            required_nexus_version=view_configuration.required_nexus_version,
            label="frame record",
            frame_name=frame_descriptor.frame_name,
        )
        for conduit_record in frame_descriptor.conduit_records_by_id.values():
            self._assert_exact_nexus_record_contract(
                actual_nexus_label=conduit_record.nexus_label,
                actual_nexus_version=conduit_record.nexus_version,
                required_nexus_label=view_configuration.required_nexus_label,
                required_nexus_version=view_configuration.required_nexus_version,
                label="conduit record",
                frame_name=frame_descriptor.frame_name,
            )
        for spell_record in frame_descriptor.spell_records_by_key.values():
            self._assert_exact_nexus_record_contract(
                actual_nexus_label=spell_record.nexus_label,
                actual_nexus_version=spell_record.nexus_version,
                required_nexus_label=view_configuration.required_nexus_label,
                required_nexus_version=view_configuration.required_nexus_version,
                label="spell record",
                frame_name=frame_descriptor.frame_name,
            )
            self._assert_spell_payload_floor(
                actual_payload_type=spell_record.payload.payload_type,
                actual_payload_version=spell_record.payload.payload_version,
                minimum_payload_type=(
                    view_configuration.minimum_spell_payload_type
                ),
                minimum_payload_version=(
                    view_configuration.minimum_spell_payload_version
                ),
                frame_name=frame_descriptor.frame_name,
            )

    def _validate_spell_selector_rules_against_descriptor(
            self,
            frame_descriptor: FrameDescriptor,
            configuration: FrameACLConfiguration,
    ) -> None:
        """
        Validate selector-aware spell rules against published descriptor truth.

        Returns:
            None.
        """
        self._validate_view_spell_selector_rules(
            frame_descriptor,
            configuration.view_configuration,
        )
        self._validate_command_spell_selector_rules(
            frame_descriptor,
            configuration.command_configuration,
        )
        self._validate_codegen_spell_selector_rules(
            frame_descriptor,
            configuration.codegen_configuration,
        )

    def _validate_view_spell_selector_rules(
            self,
            frame_descriptor: FrameDescriptor,
            configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate selector-aware spell rules from one view config.

        Returns:
            None.
        """
        profile_rulesets = []
        try:
            profile_rulesets.append(
                self._profile_builder.get_required_view_profile(
                    configuration.profile_name
                ).spell_ruleset
            )
        except KeyError:
            pass
        if configuration.precision_profile_name is not None:
            try:
                profile_rulesets.append(
                    self._profile_builder.get_required_view_precision_profile(
                        configuration.precision_profile_name
                    ).spell_ruleset
                )
            except KeyError:
                pass
        for index, ruleset in enumerate(profile_rulesets):
            self._validate_spell_rule_selectors(
                frame_descriptor,
                ruleset,
                "view.profile.{0}".format(index),
            )
        self._validate_spell_rule_selectors(
            frame_descriptor,
            configuration.spell_override_ruleset,
            "view.override",
        )

    def _validate_command_spell_selector_rules(
            self,
            frame_descriptor: FrameDescriptor,
            configuration: FrameACLCommandConfiguration,
    ) -> None:
        """
        Validate selector-aware spell rules from one command config.

        Returns:
            None.
        """
        profile_rulesets = []
        try:
            profile_rulesets.append(
                self._profile_builder.get_required_command_profile(
                    configuration.profile_name
                ).spell_ruleset
            )
        except KeyError:
            pass
        if configuration.precision_profile_name is not None:
            try:
                profile_rulesets.append(
                    self._profile_builder.get_required_command_precision_profile(
                        configuration.precision_profile_name
                    ).spell_ruleset
                )
            except KeyError:
                pass
        for index, ruleset in enumerate(profile_rulesets):
            self._validate_spell_rule_selectors(
                frame_descriptor,
                ruleset,
                "command.profile.{0}".format(index),
            )
        self._validate_spell_rule_selectors(
            frame_descriptor,
            configuration.spell_override_ruleset,
            "command.override",
        )

    def _validate_codegen_spell_selector_rules(
            self,
            frame_descriptor: FrameDescriptor,
            configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Validate selector-aware spell rules from one codegen config.

        Returns:
            None.
        """
        profile_rulesets = []
        try:
            profile_rulesets.append(
                self._profile_builder.get_required_codegen_profile(
                    configuration.profile_name
                ).spell_ruleset
            )
        except KeyError:
            pass
        if configuration.precision_profile_name is not None:
            try:
                profile_rulesets.append(
                    self._profile_builder.get_required_codegen_precision_profile(
                        configuration.precision_profile_name
                    ).spell_ruleset
                )
            except KeyError:
                pass
        for index, ruleset in enumerate(profile_rulesets):
            self._validate_spell_rule_selectors(
                frame_descriptor,
                ruleset,
                "codegen.profile.{0}".format(index),
            )
        self._validate_spell_rule_selectors(
            frame_descriptor,
            configuration.spell_override_ruleset,
            "codegen.override",
        )

    def _validate_spell_rule_selectors(
            self,
            frame_descriptor: FrameDescriptor,
            ruleset: FrameACLRuleSet,
            label: str,
    ) -> None:
        """
        Validate selector-aware spell rules in one spell ruleset.

        Returns:
            None.
        """
        for rule in ruleset.rules_by_name.values():
            selector = self._extract_spell_selector(rule.conditions, label)
            if selector is None:
                continue
            matches = self._resolve_spell_records_by_selector(
                frame_descriptor,
                selector,
            )
            if len(matches) == 0:
                raise ValueError(
                    "Spell selector in {0} rule '{1}' matched no published spells.".format(
                        label,
                        rule.rule_name,
                    )
                )
            if len(matches) > 1:
                raise ValueError(
                    "Spell selector in {0} rule '{1}' is ambiguous.".format(
                        label,
                        rule.rule_name,
                    )
                )

    @staticmethod
    def _extract_spell_selector(
            conditions: Dict[str, object],
            label: str,
    ) -> Optional[Dict[str, object]]:
        """
        Extract one supported spell selector from rule conditions.

        Returns:
            Optional[Dict[str, object]]: Selector dict when one is present.
        """
        selector_keys = {
            "spell_id",
            "spell_index_id",
            "spellframe",
            "spell_name",
            "binding_name",
        }
        if len(conditions) == 0:
            return None
        unsupported_keys = set(conditions.keys()).difference(selector_keys)
        if len(unsupported_keys) > 0:
            raise ValueError(
                "Unsupported spell selector key(s) {0} in {1}.".format(
                    sorted(unsupported_keys),
                    label,
                )
            )
        if not any(key in conditions for key in selector_keys):
            return None
        return {
            key: conditions[key]
            for key in selector_keys
            if key in conditions
        }

    @staticmethod
    def _resolve_spell_records_by_selector(
            frame_descriptor: FrameDescriptor,
            selector: Dict[str, object],
    ) -> Tuple[object, ...]:
        """
        Resolve published spell records that match one selector dict.

        Returns:
            Tuple[object, ...]: Matching spell records.
        """
        matches = []
        for spell_record in frame_descriptor.spell_records_by_key.values():
            if (
                    "spell_id" in selector and
                    selector["spell_id"] != spell_record.spell_id
            ):
                continue
            if (
                    "spell_index_id" in selector and
                    selector["spell_index_id"] != spell_record.spell_index_id
            ):
                continue
            if "spellframe" in selector:
                if spell_record.spellframe is None:
                    continue
                if (
                        SpellInputUtils.normalize_frame_key(selector["spellframe"]) !=
                        SpellInputUtils.normalize_frame_key(spell_record.spellframe)
                ):
                    continue
            if "spell_name" in selector:
                if str(selector["spell_name"]).lower() != str(spell_record.spell_name).lower():
                    continue
            if "binding_name" in selector:
                if (
                        SpellInputUtils.normalize_binding_name(
                            selector["binding_name"]
                        ) !=
                        SpellInputUtils.normalize_binding_name(
                            spell_record.binding_name
                        )
                ):
                    continue
            matches.append(spell_record)
        return tuple(matches)

    def _validate_codegen_configuration(
            self,
            codegen_configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Validate the typed codegen-side configuration object.

        Args:
            codegen_configuration:
                Typed codegen-side configuration to validate.

        Returns:
            None.
        """
        self._validate_codegen_configuration_shape_only(codegen_configuration)
        base_profile = self._profile_builder.get_required_codegen_profile(
            codegen_configuration.profile_name
        )
        if codegen_configuration.profile_version != base_profile.version:
            raise ValueError(
                "Codegen configuration profile version '{0}' does not match reusable profile version '{1}' for '{2}'.".format(
                    codegen_configuration.profile_version,
                    base_profile.version,
                    codegen_configuration.profile_name,
                )
            )
        precision_profile = None
        if codegen_configuration.precision_profile_name is not None:
            precision_profile = self._profile_builder.get_required_codegen_precision_profile(
                codegen_configuration.precision_profile_name
            )
            if (
                    codegen_configuration.precision_profile_version !=
                    precision_profile.version
            ):
                raise ValueError(
                    "Codegen configuration precision profile version '{0}' does not match reusable precision profile version '{1}' for '{2}'.".format(
                        codegen_configuration.precision_profile_version,
                        precision_profile.version,
                        codegen_configuration.precision_profile_name,
                    )
                )
        self._run_codegen_profile_validation(
            base_profile,
            codegen_configuration,
        )
        if precision_profile is not None:
            self._run_codegen_profile_validation(
                precision_profile,
                codegen_configuration,
            )

    def _validate_command_configuration(
            self,
            command_configuration: FrameACLCommandConfiguration,
    ) -> None:
        """
        Validate the typed command-side configuration object.

        Contract:
            - Treats command policy as a separate validation family from view
              visibility and codegen policy.
            - Enforces the first-cut command operation whitelist by ruleset
              family:
                frame, conduit, spell, and member.
            - Requires member-scoped command rules to include selector shape
              (`pattern` or `member_name`) so later runtime consumers can map
              the rule deterministically.

        Args:
            command_configuration:
                Typed command-side configuration to validate.

        Returns:
            None.

        Raises:
            TypeError:
                If `command_configuration` is not a
                `FrameACLCommandConfiguration`.
            ValueError:
                If one ruleset contains an unsupported command operation or one
                member rule omits selector shape.
        """
        self._validate_command_configuration_shape_only(command_configuration)
        base_profile = self._profile_builder.get_required_command_profile(
            command_configuration.profile_name
        )
        if command_configuration.profile_version != base_profile.version:
            raise ValueError(
                "Command configuration profile version '{0}' does not match reusable profile version '{1}' for '{2}'.".format(
                    command_configuration.profile_version,
                    base_profile.version,
                    command_configuration.profile_name,
                )
            )
        precision_profile = None
        if command_configuration.precision_profile_name is not None:
            precision_profile = self._profile_builder.get_required_command_precision_profile(
                command_configuration.precision_profile_name
            )
            if (
                    command_configuration.precision_profile_version !=
                    precision_profile.version
            ):
                raise ValueError(
                    "Command configuration precision profile version '{0}' does not match reusable precision profile version '{1}' for '{2}'.".format(
                        command_configuration.precision_profile_version,
                        precision_profile.version,
                        command_configuration.precision_profile_name,
                    )
                )
        self._run_command_profile_validation(
            base_profile,
            command_configuration,
        )
        if precision_profile is not None:
            self._run_command_profile_validation(
                precision_profile,
                command_configuration,
            )

    def _run_view_profile_validation(
            self,
            profile: FrameACLViewProfile,
            configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Run the validator-owned strategy for one resolved view profile.

        Returns:
            None.
        """
        strategy = self._view_profile_validation_strategies_by_name.get(
            profile.validation_strategy_name
        )
        if strategy is None:
            raise ValueError(
                "Unknown view validation strategy '{0}' for profile '{1}'.".format(
                    profile.validation_strategy_name,
                    profile.name,
                )
            )
        strategy(profile, configuration)

    def _validate_view_configuration_shape_only(
            self,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate only the intrinsic shape of one view configuration.

        Returns:
            None.
        """
        if not isinstance(view_configuration, FrameACLViewConfiguration):
            raise TypeError(
                "view_configuration must be a FrameACLViewConfiguration."
            )
        if (
                view_configuration.required_nexus_label,
                view_configuration.required_nexus_version,
        ) not in self._SUPPORTED_NEXUS_RECORD_CONTRACTS:
            raise ValueError(
                "Unsupported required Nexus record contract '{0}:{1}'.".format(
                    view_configuration.required_nexus_label,
                    view_configuration.required_nexus_version,
                )
            )
        if (
                view_configuration.minimum_spell_payload_type
                not in self._SUPPORTED_SPELL_PAYLOAD_TYPE_ORDER
        ):
            raise ValueError(
                "Unsupported minimum_spell_payload_type '{0}'.".format(
                    view_configuration.minimum_spell_payload_type
                )
            )
        if (
                view_configuration.minimum_spell_payload_version
                not in self._SUPPORTED_SPELL_PAYLOAD_VERSIONS
        ):
            raise ValueError(
                "Unsupported minimum_spell_payload_version '{0}'.".format(
                    view_configuration.minimum_spell_payload_version
                )
            )
        self._validate_ruleset_family(
            view_configuration.frame_override_ruleset,
            self._VIEW_ALLOWED_OPERATIONS_BY_RULESET["frame"],
            "view.frame",
        )
        self._validate_ruleset_family(
            view_configuration.conduit_override_ruleset,
            self._VIEW_ALLOWED_OPERATIONS_BY_RULESET["conduit"],
            "view.conduit",
        )
        self._validate_ruleset_family(
            view_configuration.spell_override_ruleset,
            self._VIEW_ALLOWED_OPERATIONS_BY_RULESET["spell"],
            "view.spell",
        )
        self._validate_ruleset_family(
            view_configuration.member_override_ruleset,
            self._VIEW_ALLOWED_OPERATIONS_BY_RULESET["member"],
            "view.member",
            require_member_shape=True,
        )

    def _run_command_profile_validation(
            self,
            profile: FrameACLCommandProfile,
            configuration: FrameACLCommandConfiguration,
    ) -> None:
        """
        Run the validator-owned strategy for one resolved command profile.

        Returns:
            None.
        """
        strategy = self._command_profile_validation_strategies_by_name.get(
            profile.validation_strategy_name
        )
        if strategy is None:
            raise ValueError(
                "Unknown command validation strategy '{0}' for profile '{1}'.".format(
                    profile.validation_strategy_name,
                    profile.name,
                )
            )
        strategy(profile, configuration)

    def _validate_command_configuration_shape_only(
            self,
            command_configuration: FrameACLCommandConfiguration,
    ) -> None:
        """
        Validate only the intrinsic shape of one command configuration.

        Returns:
            None.
        """
        if not isinstance(command_configuration, FrameACLCommandConfiguration):
            raise TypeError(
                "command_configuration must be a FrameACLCommandConfiguration."
            )
        self._validate_ruleset_family(
            command_configuration.frame_override_ruleset,
            self._COMMAND_ALLOWED_OPERATIONS_BY_RULESET["frame"],
            "command.frame",
        )
        self._validate_ruleset_family(
            command_configuration.conduit_override_ruleset,
            self._COMMAND_ALLOWED_OPERATIONS_BY_RULESET["conduit"],
            "command.conduit",
        )
        self._validate_ruleset_family(
            command_configuration.spell_override_ruleset,
            self._COMMAND_ALLOWED_OPERATIONS_BY_RULESET["spell"],
            "command.spell",
        )
        self._validate_ruleset_family(
            command_configuration.member_override_ruleset,
            self._COMMAND_ALLOWED_OPERATIONS_BY_RULESET["member"],
            "command.member",
            require_member_shape=True,
        )

    def _run_codegen_profile_validation(
            self,
            profile: FrameACLCodegenProfile,
            configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Run the validator-owned strategy for one resolved codegen profile.

        Returns:
            None.
        """
        strategy = self._codegen_profile_validation_strategies_by_name.get(
            profile.validation_strategy_name
        )
        if strategy is None:
            raise ValueError(
                "Unknown codegen validation strategy '{0}' for profile '{1}'.".format(
                    profile.validation_strategy_name,
                    profile.name,
                )
            )
        strategy(profile, configuration)

    def _validate_codegen_configuration_shape_only(
            self,
            codegen_configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Validate only the intrinsic shape of one codegen configuration.

        Returns:
            None.
        """
        if not isinstance(codegen_configuration, FrameACLCodegenConfiguration):
            raise TypeError(
                "codegen_configuration must be a FrameACLCodegenConfiguration."
            )
        self._validate_ruleset_family(
            codegen_configuration.frame_override_ruleset,
            self._CODEGEN_ALLOWED_OPERATIONS_BY_RULESET["frame"],
            "codegen.frame",
        )
        self._validate_ruleset_family(
            codegen_configuration.conduit_override_ruleset,
            self._CODEGEN_ALLOWED_OPERATIONS_BY_RULESET["conduit"],
            "codegen.conduit",
        )
        self._validate_ruleset_family(
            codegen_configuration.spell_override_ruleset,
            self._CODEGEN_ALLOWED_OPERATIONS_BY_RULESET["spell"],
            "codegen.spell",
        )
        self._validate_ruleset_family(
            codegen_configuration.capability_override_ruleset,
            self._CODEGEN_ALLOWED_OPERATIONS_BY_RULESET["capability"],
            "codegen.capability",
        )

    def _validate_ruleset_family(
            self,
            ruleset: FrameACLRuleSet,
            allowed_operations: Set[str],
            label: str,
            *,
            require_member_shape: bool = False,
    ) -> None:
        """
        Validate that one ruleset contains only allowed operations.

        Args:
            ruleset:
                Typed ruleset to validate.
            allowed_operations:
                Supported operation names for the target ruleset family.
            label:
                Human-readable validation label.
            require_member_shape:
                True when `show_member` rules must include `pattern` or
                `member_name`.

        Returns:
            None.
        """
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("{0} ruleset must be a FrameACLRuleSet.".format(label))
        for rule in ruleset.rules_by_name.values():
            if rule.operation not in allowed_operations:
                raise ValueError(
                    "Unsupported operation '{0}' in {1} ruleset.".format(
                        rule.operation,
                        label,
                    )
                )
            if require_member_shape:
                conditions = rule.conditions
                if "pattern" not in conditions and "member_name" not in conditions:
                    raise ValueError(
                        "Member rules in {0} must declare 'pattern' or 'member_name'.".format(
                            label
                        )
                    )
            if rule.operation == "import_modules":
                self._validate_import_module_rule_conditions(rule, label)
            if rule.operation == "builtin_names":
                self._validate_builtin_names_rule_conditions(rule, label)

    @staticmethod
    def _validate_import_module_rule_conditions(
            rule: FrameACLRule,
            label: str,
    ) -> None:
        """
        Validate the condition payload for one import-module ACL rule.

        Args:
            rule:
                Rule to validate.
            label:
                Human-readable validation label.

        Returns:
            None.
        """
        module_roots = rule.conditions.get("module_roots")
        if not isinstance(module_roots, (list, tuple)) or len(module_roots) == 0:
            raise ValueError(
                "Import-module rules in {0} must declare non-empty 'module_roots'.".format(
                    label
                )
            )
        for module_root in module_roots:
            if not isinstance(module_root, str) or not module_root:
                raise ValueError(
                    "Import-module rules in {0} must use non-empty module-root strings.".format(
                        label
                    )
                )

    @staticmethod
    def _validate_builtin_names_rule_conditions(
            rule: FrameACLRule,
            label: str,
    ) -> None:
        """
        Validate the condition payload for one builtin-name ACL rule.

        Args:
            rule:
                Rule to validate.
            label:
                Human-readable validation label.

        Returns:
            None.
        """
        builtin_names = rule.conditions.get("builtin_names")
        if not isinstance(builtin_names, (list, tuple)) or len(builtin_names) == 0:
            raise ValueError(
                "Builtin-name rules in {0} must declare non-empty 'builtin_names'.".format(
                    label
                )
            )
        for builtin_name in builtin_names:
            if not isinstance(builtin_name, str) or not builtin_name:
                raise ValueError(
                    "Builtin-name rules in {0} must use non-empty builtin-name strings.".format(
                        label
                    )
                )

    def _validate_safe_view_configuration(
            self,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate that the seeded safe view configuration stays restrictive.

        Args:
            view_configuration:
                Safe view configuration to validate.

        Returns:
            None.
        """
        self._assert_forbidden_operations_are_not_allowed(
            view_configuration.conduit_override_ruleset,
            self._SAFE_VIEW_FORBIDDEN_OVERRIDES["conduit"],
            "safe view conduit",
        )
        self._assert_forbidden_operations_are_not_allowed(
            view_configuration.spell_override_ruleset,
            self._SAFE_VIEW_FORBIDDEN_OVERRIDES["spell"],
            "safe view spell",
        )
        self._assert_safe_member_access_not_widened(view_configuration)

    def _validate_safe_codegen_configuration(
            self,
            codegen_configuration: FrameACLCodegenConfiguration,
    ) -> None:
        """
        Validate that the seeded safe codegen configuration stays restrictive.

        Args:
            codegen_configuration:
                Safe codegen configuration to validate.

        Returns:
            None.
        """
        self._assert_forbidden_operations_are_not_allowed(
            codegen_configuration.conduit_override_ruleset,
            self._SAFE_CODEGEN_FORBIDDEN_OVERRIDES["conduit"],
            "safe codegen conduit",
        )
        self._assert_forbidden_operations_are_not_allowed(
            codegen_configuration.spell_override_ruleset,
            self._SAFE_CODEGEN_FORBIDDEN_OVERRIDES["spell"],
            "safe codegen spell",
        )
        self._assert_forbidden_operations_are_not_allowed(
            codegen_configuration.capability_override_ruleset,
            self._SAFE_CODEGEN_FORBIDDEN_OVERRIDES["capability"],
            "safe codegen capability",
        )

    @staticmethod
    def _assert_forbidden_operations_are_not_allowed(
            ruleset: FrameACLRuleSet,
            forbidden_operations: Set[str],
            label: str,
    ) -> None:
        """
        Fail when one forbidden operation is explicitly allowed.

        Args:
            ruleset:
                Ruleset to inspect.
            forbidden_operations:
                Operations that must not be allowed for the named safe layer.
            label:
                Human-readable validation label.

        Returns:
            None.
        """
        for rule in ruleset.rules_by_name.values():
            if rule.effect == "allow" and rule.operation in forbidden_operations:
                raise ValueError(
                    "Safe profile cannot allow '{0}' in {1} ruleset.".format(
                        rule.operation,
                        label,
                    )
                )

    @staticmethod
    def _assert_safe_member_access_not_widened(
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate that safe view overrides do not re-open dunder member access.

        Args:
            view_configuration:
                Safe view configuration to inspect.

        Returns:
            None.
        """
        for rule in view_configuration.member_override_ruleset.rules_by_name.values():
            conditions = rule.conditions
            if (
                    rule.operation == "show_member"
                    and rule.effect == "allow"
                    and (
                        conditions.get("pattern") == "__*"
                        or str(conditions.get("member_name", "")).startswith("__")
                    )
            ):
                raise ValueError(
                    "Safe profile cannot allow dunder member access in safe view member ruleset."
                )

    @staticmethod
    def _assert_exact_nexus_record_contract(
            *,
            actual_nexus_label: str,
            actual_nexus_version: str,
            required_nexus_label: str,
            required_nexus_version: str,
            label: str,
            frame_name: str,
    ) -> None:
        """
        Fail when one record-level Nexus contract does not match exactly.

        Args:
            actual_nexus_label:
                Actual record/event Nexus label.
            actual_nexus_version:
                Actual record/event Nexus version.
            required_nexus_label:
                Required ACL Nexus label.
            required_nexus_version:
                Required ACL Nexus version.
            label:
                Human-readable payload family label.
            frame_name:
                Owning frame name.

        Returns:
            None.
        """
        if (
                actual_nexus_label != required_nexus_label
                or actual_nexus_version != required_nexus_version
        ):
            raise ValueError(
                "Descriptor {0} Nexus contract '{1}:{2}' does not match required ACL contract '{3}:{4}' for frame '{5}'.".format(
                    label,
                    actual_nexus_label,
                    actual_nexus_version,
                    required_nexus_label,
                    required_nexus_version,
                    frame_name,
                )
            )

    def _assert_spell_payload_floor(
            self,
            *,
            actual_payload_type: str,
            actual_payload_version: str,
            minimum_payload_type: str,
            minimum_payload_version: str,
            frame_name: str,
    ) -> None:
        """
        Fail when one descriptor spell payload does not satisfy the ACL floor.

        Args:
            actual_payload_type:
                Actual spell payload family name.
            actual_payload_version:
                Actual spell payload contract version.
            minimum_payload_type:
                Required minimum spell payload family name.
            minimum_payload_version:
                Required minimum spell payload contract version.
            frame_name:
                Owning frame name.

        Returns:
            None.
        """
        actual_rank = self._SUPPORTED_SPELL_PAYLOAD_TYPE_ORDER.get(
            actual_payload_type
        )
        required_rank = self._SUPPORTED_SPELL_PAYLOAD_TYPE_ORDER.get(
            minimum_payload_type
        )
        if actual_rank is None:
            raise ValueError(
                "Unsupported descriptor spell payload type '{0}' for frame '{1}'.".format(
                    actual_payload_type,
                    frame_name,
                )
            )
        if actual_payload_version != minimum_payload_version:
            raise ValueError(
                "Descriptor spell payload version '{0}' does not match required ACL spell payload version '{1}' for frame '{2}'.".format(
                    actual_payload_version,
                    minimum_payload_version,
                    frame_name,
                )
            )
        if required_rank is None or actual_rank < required_rank:
            raise ValueError(
                "Descriptor spell payload type '{0}:{1}' does not satisfy minimum ACL spell payload contract '{2}:{3}' for frame '{4}'.".format(
                    actual_payload_type,
                    actual_payload_version,
                    minimum_payload_type,
                    minimum_payload_version,
                    frame_name,
                )
            )
