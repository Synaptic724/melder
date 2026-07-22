import threading
from typing import TYPE_CHECKING, Dict, Optional, Sequence
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.frame_acl_codegen_configuration import FrameACLCodegenConfiguration
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet

if TYPE_CHECKING:
    from melder.nexus.acl.builder.frame_acl_builder import FrameACLBuilder


class FrameACLCodegenBuilder(Cleanable):
    """

    Purpose:
        Provide a fluent authoring surface for one active codegen ACL draft.

    Contract:
        - Layers over one active codegen draft owned by the generic ACL
          builder contract.
        - Does not replace the generic builder draft/commit lifecycle.
        - Mutates the borrowed typed codegen configuration in place.
        - Returns itself from fluent mutation methods so authoring remains
          chainable.

    Threading:
        All grouped mutations execute under the builder's instance `RLock`.

    Lifecycle:
        Cleanup is idempotent and only drops borrowed references; it does not
        own persistence or chain installation.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLCodegenBuilder runtime object. Melder kernel machinery: read "
        "it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_acl_builder",
    ]
    _DEFAULT_IMPORTS_RULE_NAME = "builder_enable_imports"
    _DEFAULT_ALLOW_IMPORT_MODULES_RULE_NAME = "builder_allow_import_modules"
    _DEFAULT_DENY_IMPORT_MODULES_RULE_NAME = "builder_deny_import_modules"
    _DEFAULT_ALLOW_BUILTINS_RULE_NAME = "builder_allow_builtin_names"
    _DEFAULT_DENY_BUILTINS_RULE_NAME = "builder_deny_builtin_names"
    _DEFAULT_UNSAFE_REFLECTION_RULE_NAME = "builder_unsafe_reflection"
    _DEFAULT_DUNDER_ACCESS_RULE_NAME = "builder_dunder_access"
    _DEFAULT_RECURSIVE_CODEGEN_RULE_NAME = "builder_recursive_codegen"

    def __init__(self, frame_acl_builder: FrameACLBuilder) -> None:
        """
        Initialize one fluent codegen ACL builder.

        Args:
            frame_acl_builder:
                Borrowed generic ACL builder that currently owns one active
                codegen-family draft session.

        Returns:
            None.

        Raises:
            TypeError:
                If `frame_acl_builder` does not satisfy the builder protocol.
        """

        super().__init__()
        from melder.nexus.acl.builder.frame_acl_builder import FrameACLBuilder as _FrameACLBuilder
        if not isinstance(frame_acl_builder, _FrameACLBuilder):
            raise TypeError("frame_acl_builder must satisfy FrameACLBuilder.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_acl_builder: FrameACLBuilder = frame_acl_builder

    def cleanup(self) -> None:
        """
        Idempotently clear fluent-builder-owned references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._frame_acl_builder
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable fluent-builder identifier.

        Returns:
            str: Stable fluent-builder id.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def draft_configuration(self) -> FrameACLCodegenConfiguration:
        """
        Return the active codegen draft configuration.

        Returns:
            FrameACLCodegenConfiguration: Active codegen draft.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_acl_builder._require_active_codegen_configuration()

    def use_profile(self, profile_name: str) -> FrameACLCodegenBuilder:
        """
        Replace the base codegen profile on the active draft.

        Args:
            profile_name:
                Registered base codegen profile name.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_acl_builder.set_profile_name(profile_name)
            return self

    def use_precision_profile(
            self,
            profile_name: Optional[str],
    ) -> FrameACLCodegenBuilder:
        """
        Replace or clear the precision codegen profile on the active draft.

        Args:
            profile_name:
                Precision profile name, or None to clear.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_acl_builder.set_precision_profile_name(profile_name)
            return self

    def set_frame_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, object]] = None,
    ) -> FrameACLCodegenBuilder:
        """
        Upsert one frame-family rule on the active draft.

        Args:
            operation_name:
                Target operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional condition payload.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.frame_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def set_conduit_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, object]] = None,
    ) -> FrameACLCodegenBuilder:
        """
        Upsert one conduit-family rule on the active draft.

        Args:
            operation_name:
                Target conduit operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector/condition payload carried by the rule.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.conduit_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def set_spell_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, object]] = None,
    ) -> FrameACLCodegenBuilder:
        """
        Upsert one spell-family rule on the active draft.

        Args:
            operation_name:
                Target spell operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector/condition payload carried by the rule.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.spell_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def set_capability_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, object]] = None,
    ) -> FrameACLCodegenBuilder:
        """
        Upsert one capability-family rule on the active draft.

        Args:
            operation_name:
                Target capability operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector/condition payload carried by the rule.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.capability_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def enable_imports(self) -> FrameACLCodegenBuilder:
        """
        Allow import statements for the active draft.
        """
        return self.set_capability_operation(
            "enable_imports",
            allow=True,
            rule_name=self._DEFAULT_IMPORTS_RULE_NAME,
        )

    def disable_imports(self) -> FrameACLCodegenBuilder:
        """
        Deny import statements for the active draft.
        """
        return self.set_capability_operation(
            "enable_imports",
            allow=False,
            rule_name=self._DEFAULT_IMPORTS_RULE_NAME,
        )

    def allow_import_module_roots(
            self,
            *module_roots: str,
    ) -> FrameACLCodegenBuilder:
        """
        Merge allowed import roots into the active draft.

        Args:
            *module_roots: Import module root names to allow.

        Returns:
            FrameACLCodegenBuilder: This builder, for fluent chaining.
        """
        return self._merge_condition_values_rule(
            self.draft_configuration.capability_override_ruleset,
            rule_name=self._DEFAULT_ALLOW_IMPORT_MODULES_RULE_NAME,
            operation_name="import_modules",
            effect="allow",
            condition_key="module_roots",
            values=module_roots,
        )

    def deny_import_module_roots(
            self,
            *module_roots: str,
    ) -> FrameACLCodegenBuilder:
        """
        Merge denied import roots into the active draft.

        Args:
            *module_roots: Import module root names to deny.

        Returns:
            FrameACLCodegenBuilder: This builder, for fluent chaining.
        """
        return self._merge_condition_values_rule(
            self.draft_configuration.capability_override_ruleset,
            rule_name=self._DEFAULT_DENY_IMPORT_MODULES_RULE_NAME,
            operation_name="import_modules",
            effect="deny",
            condition_key="module_roots",
            values=module_roots,
        )

    def allow_builtin_names(
            self,
            *builtin_names: str,
    ) -> FrameACLCodegenBuilder:
        """
        Merge explicitly allowed builtin names into the active draft.

        Args:
            *builtin_names: Builtin names to allow.

        Returns:
            FrameACLCodegenBuilder: This builder, for fluent chaining.
        """
        return self._merge_condition_values_rule(
            self.draft_configuration.capability_override_ruleset,
            rule_name=self._DEFAULT_ALLOW_BUILTINS_RULE_NAME,
            operation_name="builtin_names",
            effect="allow",
            condition_key="builtin_names",
            values=builtin_names,
        )

    def deny_builtin_names(
            self,
            *builtin_names: str,
    ) -> FrameACLCodegenBuilder:
        """
        Merge explicitly denied builtin names into the active draft.

        Args:
            *builtin_names: Builtin names to deny.

        Returns:
            FrameACLCodegenBuilder: This builder, for fluent chaining.
        """
        return self._merge_condition_values_rule(
            self.draft_configuration.capability_override_ruleset,
            rule_name=self._DEFAULT_DENY_BUILTINS_RULE_NAME,
            operation_name="builtin_names",
            effect="deny",
            condition_key="builtin_names",
            values=builtin_names,
        )

    def allow_unsafe_reflection(self) -> FrameACLCodegenBuilder:
        """
        Allow unsafe reflection for the active draft.
        """
        return self.set_capability_operation(
            "unsafe_reflection",
            allow=True,
            rule_name=self._DEFAULT_UNSAFE_REFLECTION_RULE_NAME,
        )

    def deny_unsafe_reflection(self) -> FrameACLCodegenBuilder:
        """
        Deny unsafe reflection for the active draft.
        """
        return self.set_capability_operation(
            "unsafe_reflection",
            allow=False,
            rule_name=self._DEFAULT_UNSAFE_REFLECTION_RULE_NAME,
        )

    def allow_dunder_access(self) -> FrameACLCodegenBuilder:
        """
        Allow dunder access for the active draft.
        """
        return self.set_capability_operation(
            "dunder_access",
            allow=True,
            rule_name=self._DEFAULT_DUNDER_ACCESS_RULE_NAME,
        )

    def deny_dunder_access(self) -> FrameACLCodegenBuilder:
        """
        Deny dunder access for the active draft.
        """
        return self.set_capability_operation(
            "dunder_access",
            allow=False,
            rule_name=self._DEFAULT_DUNDER_ACCESS_RULE_NAME,
        )

    def allow_recursive_codegen(self) -> FrameACLCodegenBuilder:
        """
        Allow recursive codegen for the active draft.
        """
        return self.set_capability_operation(
            "recursive_codegen",
            allow=True,
            rule_name=self._DEFAULT_RECURSIVE_CODEGEN_RULE_NAME,
        )

    def deny_recursive_codegen(self) -> FrameACLCodegenBuilder:
        """
        Deny recursive codegen for the active draft.
        """
        return self.set_capability_operation(
            "recursive_codegen",
            allow=False,
            rule_name=self._DEFAULT_RECURSIVE_CODEGEN_RULE_NAME,
        )

    def remove_capability_rule(self, rule_name: str) -> FrameACLCodegenBuilder:
        """
        Remove one capability-family rule from the active draft.

        Args:
            rule_name:
                Stable rule name to remove from the capability ruleset.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.

        Raises:
            ValueError:
                If `rule_name` is empty.
        """
        self.check_cleaned()
        with self._lock:
            if not rule_name:
                raise ValueError("rule_name cannot be empty.")
            self.draft_configuration.capability_override_ruleset.remove_rule(
                rule_name
            )
            return self

    def commit_change(self) -> FrameACLCodegenConfiguration:
        """
        Commit the active codegen draft through the owning generic builder.

        Returns:
            FrameACLCodegenConfiguration: Newly installed codegen revision.
        """
        self.check_cleaned()
        with self._lock:
            configuration = self._frame_acl_builder.commit_change()
            if not isinstance(configuration, FrameACLCodegenConfiguration):
                raise RuntimeError(
                    "FrameACLCodegenBuilder commit returned a non-codegen "
                    "configuration."
                )
            return configuration

    def discard_change(self) -> None:
        """
        Discard the active codegen draft through the owning generic builder.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_acl_builder.discard_change()

    def _set_ruleset_operation(
            self,
            ruleset: FrameACLRuleSet,
            *,
            operation_name: str,
            allow: bool,
            rule_name: Optional[str],
            conditions: Optional[Dict[str, object]],
    ) -> FrameACLCodegenBuilder:
        """
        Upsert one typed rule into the supplied ruleset.

        Args:
            ruleset:
                Borrowed ruleset from the active codegen configuration.
            operation_name:
                Target operation name.
            allow:
                True for allow; False for deny.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional condition payload.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.

        Raises:
            ValueError:
                If the operation or resolved rule name is empty.
        """
        self.check_cleaned()
        with self._lock:
            if not operation_name:
                raise ValueError("operation_name cannot be empty.")
            resolved_rule_name = (
                rule_name if rule_name is not None else operation_name
            )
            if not resolved_rule_name:
                raise ValueError("rule_name cannot be empty.")
            ruleset.register_rule(
                FrameACLRule(
                    rule_name=resolved_rule_name,
                    operation=operation_name,
                    effect="allow" if allow else "deny",
                    conditions=conditions,
                )
            )
            return self

    def _merge_condition_values_rule(
            self,
            ruleset: FrameACLRuleSet,
            *,
            rule_name: str,
            operation_name: str,
            effect: str,
            condition_key: str,
            values: Sequence[str],
    ) -> FrameACLCodegenBuilder:
        """
        Merge string condition values into one stable named rule.

        Args:
            ruleset:
                Borrowed ruleset from the active codegen configuration.
            rule_name:
                Stable rule name.
            operation_name:
                Target operation.
            effect:
                `allow` or `deny`.
            condition_key:
                Condition key holding the string values.
            values:
                Values to merge.

        Returns:
            FrameACLCodegenBuilder: This fluent builder.

        Raises:
            ValueError:
                If `values` is empty or contains empty/non-string entries.
        """
        self.check_cleaned()
        with self._lock:
            if not values:
                raise ValueError("values cannot be empty.")
            normalized_values = []
            for value in values:
                if not isinstance(value, str) or not value:
                    raise ValueError(
                        "{0} values must be non-empty strings.".format(
                            condition_key
                        )
                    )
                if value not in normalized_values:
                    normalized_values.append(value)
            existing_values = []
            if rule_name in ruleset.rules_by_name:
                existing_rule = ruleset.get_required_rule(rule_name)
                if (
                        existing_rule.operation == operation_name
                        and existing_rule.effect == effect
                ):
                    existing_values = list(
                        existing_rule.conditions.get(condition_key, tuple())
                    )
            merged_values = list(existing_values)
            for value in normalized_values:
                if value not in merged_values:
                    merged_values.append(value)
            return self._set_ruleset_operation(
                ruleset,
                operation_name=operation_name,
                allow=(effect == "allow"),
                rule_name=rule_name,
                conditions={
                    condition_key: tuple(merged_values),
                },
            )
