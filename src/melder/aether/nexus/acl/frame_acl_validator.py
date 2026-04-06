from typing import Dict, Optional, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLValidator(Cleanable):
    """
    Purpose:
        Validate that frame-local ACL configuration nodes are structurally
        compatible with one owning frame.

    Contract:
        - Confirms that a configuration node belongs to the expected frame.
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
        "_frame_name",
        "_last_validated_configuration_id",
    ]
    _SUPPORTED_FRAME_PAYLOAD_CONTRACTS: Set[Tuple[str, str]] = {
        ("frame", "0.0.1"),
    }
    _SUPPORTED_CONDUIT_PAYLOAD_CONTRACTS: Set[Tuple[str, str]] = {
        ("conduit", "0.0.1"),
    }
    _SUPPORTED_SPELL_PAYLOAD_PROFILE_ORDER: Dict[str, int] = {
        "general": 0,
        "detailed": 1,
    }
    _SUPPORTED_SPELL_PAYLOAD_PROFILE_VERSIONS: Set[str] = {
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
            "dynamic_access",
            "mutation",
            "contract_override",
            "unsafe_reflection",
            "dunder_access",
        },
    }
    _SAFE_VIEW_FORBIDDEN_OVERRIDES: Dict[str, Set[str]] = {
        "conduit": {"show_policy", "show_peer_links"},
        "spell": {
            "show_class_profile",
            "show_callable_profile",
            "show_instance_members",
            "show_dynamic_access",
        },
    }
    _SAFE_CODEGEN_FORBIDDEN_OVERRIDES: Dict[str, Set[str]] = {
        "conduit": {
            "link",
            "unlink",
            "create_lesser_conduit",
            "transfer_ownership",
        },
        "spell": {
            "local_create",
            "invoke_method",
            "read_attribute",
            "write_attribute",
        },
        "capability": {
            "dynamic_access",
            "mutation",
            "contract_override",
            "unsafe_reflection",
            "dunder_access",
        },
    }

    def __init__(self, frame_name: str) -> None:
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
        self._id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
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
        self._cleaned = True
        self._frame_name = None
        self._last_validated_configuration_id = None

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

        Args:
            configuration:
                Candidate frame ACL configuration node.

        Returns:
            bool: True when the configuration belongs to the same frame.

        Raises:
            TypeError:
                If `configuration` is not a `FrameACLConfiguration`.
            ValueError:
                If the configuration targets another frame.
        """
        self.check_cleaned()
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
        self.validate_configuration(configuration)
        if not isinstance(frame_descriptor, FrameDescriptor):
            raise TypeError("frame_descriptor must be a FrameDescriptor.")
        if frame_descriptor.frame_name != self._frame_name:
            raise ValueError(
                "FrameDescriptor targets frame '{0}', expected '{1}'.".format(
                    frame_descriptor.frame_name,
                    self._frame_name,
                )
            )
        self._validate_descriptor_payload_contracts(
            frame_descriptor,
            configuration.view_configuration,
        )
        return True

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
        if not isinstance(view_configuration, FrameACLViewConfiguration):
            raise TypeError(
                "view_configuration must be a FrameACLViewConfiguration."
            )
        if (
                view_configuration.required_frame_payload_profile_name,
                view_configuration.required_frame_payload_profile_version,
        ) not in self._SUPPORTED_FRAME_PAYLOAD_CONTRACTS:
            raise ValueError(
                "Unsupported required frame payload contract '{0}:{1}'.".format(
                    view_configuration.required_frame_payload_profile_name,
                    view_configuration.required_frame_payload_profile_version,
                )
            )
        if (
                view_configuration.required_conduit_payload_profile_name,
                view_configuration.required_conduit_payload_profile_version,
        ) not in self._SUPPORTED_CONDUIT_PAYLOAD_CONTRACTS:
            raise ValueError(
                "Unsupported required conduit payload contract '{0}:{1}'.".format(
                    view_configuration.required_conduit_payload_profile_name,
                    view_configuration.required_conduit_payload_profile_version,
                )
            )
        if (
                view_configuration.minimum_spell_payload_profile_name
                not in self._SUPPORTED_SPELL_PAYLOAD_PROFILE_ORDER
        ):
            raise ValueError(
                "Unsupported minimum_spell_payload_profile_name '{0}'.".format(
                    view_configuration.minimum_spell_payload_profile_name
                )
            )
        if (
                view_configuration.minimum_spell_payload_profile_version
                not in self._SUPPORTED_SPELL_PAYLOAD_PROFILE_VERSIONS
        ):
            raise ValueError(
                "Unsupported minimum_spell_payload_profile_version '{0}'.".format(
                    view_configuration.minimum_spell_payload_profile_version
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
        if view_configuration.profile_name == "safe":
            self._validate_safe_view_configuration(view_configuration)

    def _validate_descriptor_payload_contracts(
            self,
            frame_descriptor: FrameDescriptor,
            view_configuration: FrameACLViewConfiguration,
    ) -> None:
        """
        Validate descriptor payload contracts against one ACL view config.

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
                "FrameDescriptor for frame '{0}' has no frame_overview for payload validation.".format(
                    frame_descriptor.frame_name
                )
            )
        self._assert_exact_descriptor_payload_contract(
            actual_profile_name=frame_overview.payload.profile_name,
            actual_profile_version=frame_overview.payload.profile_version,
            required_profile_name=(
                view_configuration.required_frame_payload_profile_name
            ),
            required_profile_version=(
                view_configuration.required_frame_payload_profile_version
            ),
            label="frame",
            frame_name=frame_descriptor.frame_name,
        )
        for conduit_record in frame_descriptor.conduit_records_by_id.values():
            self._assert_exact_descriptor_payload_contract(
                actual_profile_name=conduit_record.payload.profile_name,
                actual_profile_version=conduit_record.payload.profile_version,
                required_profile_name=(
                    view_configuration.required_conduit_payload_profile_name
                ),
                required_profile_version=(
                    view_configuration.required_conduit_payload_profile_version
                ),
                label="conduit",
                frame_name=frame_descriptor.frame_name,
            )
        for spell_record in frame_descriptor.spell_records_by_key.values():
            self._assert_spell_payload_floor(
                actual_profile_name=spell_record.payload.profile_name,
                actual_profile_version=spell_record.payload.profile_version,
                minimum_profile_name=(
                    view_configuration.minimum_spell_payload_profile_name
                ),
                minimum_profile_version=(
                    view_configuration.minimum_spell_payload_profile_version
                ),
                frame_name=frame_descriptor.frame_name,
            )

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
        if codegen_configuration.profile_name == "safe":
            self._validate_safe_codegen_configuration(codegen_configuration)

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
    def _assert_exact_descriptor_payload_contract(
            *,
            actual_profile_name: str,
            actual_profile_version: str,
            required_profile_name: str,
            required_profile_version: str,
            label: str,
            frame_name: str,
    ) -> None:
        """
        Fail when one descriptor payload contract does not match exactly.

        Args:
            actual_profile_name:
                Actual descriptor payload family name.
            actual_profile_version:
                Actual descriptor payload contract version.
            required_profile_name:
                Required ACL payload family name.
            required_profile_version:
                Required ACL payload contract version.
            label:
                Human-readable payload family label.
            frame_name:
                Owning frame name.

        Returns:
            None.
        """
        if (
                actual_profile_name != required_profile_name
                or actual_profile_version != required_profile_version
        ):
            raise ValueError(
                "Descriptor {0} payload contract '{1}:{2}' does not match required ACL contract '{3}:{4}' for frame '{5}'.".format(
                    label,
                    actual_profile_name,
                    actual_profile_version,
                    required_profile_name,
                    required_profile_version,
                    frame_name,
                )
            )

    def _assert_spell_payload_floor(
            self,
            *,
            actual_profile_name: str,
            actual_profile_version: str,
            minimum_profile_name: str,
            minimum_profile_version: str,
            frame_name: str,
    ) -> None:
        """
        Fail when one descriptor spell payload does not satisfy the ACL floor.

        Args:
            actual_profile_name:
                Actual spell payload family name.
            actual_profile_version:
                Actual spell payload contract version.
            minimum_profile_name:
                Required minimum spell payload family name.
            minimum_profile_version:
                Required minimum spell payload contract version.
            frame_name:
                Owning frame name.

        Returns:
            None.
        """
        actual_rank = self._SUPPORTED_SPELL_PAYLOAD_PROFILE_ORDER.get(
            actual_profile_name
        )
        required_rank = self._SUPPORTED_SPELL_PAYLOAD_PROFILE_ORDER.get(
            minimum_profile_name
        )
        if actual_rank is None:
            raise ValueError(
                "Unsupported descriptor spell payload profile '{0}' for frame '{1}'.".format(
                    actual_profile_name,
                    frame_name,
                )
            )
        if actual_profile_version != minimum_profile_version:
            raise ValueError(
                "Descriptor spell payload version '{0}' does not match required ACL spell payload version '{1}' for frame '{2}'.".format(
                    actual_profile_version,
                    minimum_profile_version,
                    frame_name,
                )
            )
        if required_rank is None or actual_rank < required_rank:
            raise ValueError(
                "Descriptor spell payload profile '{0}:{1}' does not satisfy minimum ACL spell payload contract '{2}:{3}' for frame '{4}'.".format(
                    actual_profile_name,
                    actual_profile_version,
                    minimum_profile_name,
                    minimum_profile_version,
                    frame_name,
                )
            )
