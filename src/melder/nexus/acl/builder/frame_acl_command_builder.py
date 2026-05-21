import threading
from typing import TYPE_CHECKING, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.frame_acl_command_configuration import FrameACLCommandConfiguration
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet

if TYPE_CHECKING:
    from melder.nexus.acl.builder.frame_acl_builder import FrameACLBuilder


class FrameACLCommandBuilder(Cleanable):
    """
    Purpose:
        Provide fluent authoring for one active command-family ACL draft.

    Contract:
        - Borrows one active command draft from the generic ACL builder.
        - Mutates the borrowed typed command configuration in place.
        - Does not own persistence or configuration-chain installation.
        - Returns itself from fluent mutation methods so authoring remains
          chainable.

    Threading:
        All grouped draft mutations execute under the builder's instance
        `RLock` because multiple builder-owned fields can change together in a
        nogil runtime.

    Lifecycle:
        Cleanup is idempotent. It only drops borrowed references and does not
        clean or commit the underlying draft automatically.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_acl_builder",
    ]

    def __init__(self, frame_acl_builder: FrameACLBuilder) -> None:
        """
        Initialize one fluent command ACL builder.

        Args:
            frame_acl_builder:
                Borrowed generic ACL builder that currently owns one active
                command-family draft session.

        Returns:
            None.

        Raises:
            TypeError:
                If `frame_acl_builder` does not satisfy `FrameACLBuilder`.
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

        Contract:
            - Does not discard or commit the borrowed draft.
            - Only drops this builder's local references.

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
        Return the stable identifier for this fluent builder instance.

        Returns:
            str: Stable fluent-builder identifier.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def draft_configuration(self) -> FrameACLCommandConfiguration:
        """
        Return the currently borrowed active command configuration draft.

        Returns:
            FrameACLCommandConfiguration: Active mutable command draft.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_acl_builder._require_active_command_configuration()

    def use_profile(self, profile_name: str) -> FrameACLCommandBuilder:
        """
        Replace the base command profile on the active draft.

        Args:
            profile_name:
                Registered reusable base command profile name.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_acl_builder.set_profile_name(profile_name)
            return self

    def use_precision_profile(
            self,
            profile_name: Optional[str],
    ) -> FrameACLCommandBuilder:
        """
        Replace or clear the precision command profile on the active draft.

        Args:
            profile_name:
                Registered precision profile name, or None to clear the current
                precision selection.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
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
    ) -> FrameACLCommandBuilder:
        """
        Upsert one frame-family rule on the active draft.

        Args:
            operation_name:
                Target command-frame operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
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
    ) -> FrameACLCommandBuilder:
        """
        Upsert one conduit-family rule on the active draft.

        Args:
            operation_name:
                Target command-conduit operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
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
    ) -> FrameACLCommandBuilder:
        """
        Upsert one spell-family rule on the active draft.

        Args:
            operation_name:
                Target command-spell operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.spell_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def set_member_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, object]] = None,
    ) -> FrameACLCommandBuilder:
        """
        Upsert one member-family rule on the active draft.

        Args:
            operation_name:
                Target command-member operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload. Member rules should be
                selector-shaped so runtime consumers can map them
                deterministically.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.member_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def allow_frame_enable(self) -> FrameACLCommandBuilder:
        """
        Allow command access to the frame in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_frame_operation("enable", allow=True)

    def deny_frame_enable(self) -> FrameACLCommandBuilder:
        """
        Deny command access to the frame in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_frame_operation("enable", allow=False)

    def allow_conduit_enable(self) -> FrameACLCommandBuilder:
        """
        Allow command access to conduits in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_conduit_operation("enable", allow=True)

    def deny_conduit_enable(self) -> FrameACLCommandBuilder:
        """
        Deny command access to conduits in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_conduit_operation("enable", allow=False)

    def allow_spell_enable(self) -> FrameACLCommandBuilder:
        """
        Allow command access to spells in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_spell_operation("enable", allow=True)

    def deny_spell_enable(self) -> FrameACLCommandBuilder:
        """
        Deny command access to spells in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_spell_operation("enable", allow=False)

    def allow_member_read_attribute(self) -> FrameACLCommandBuilder:
        """
        Allow attribute reads for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "read_attribute",
            allow=True,
            conditions={"pattern": "*"},
        )

    def deny_member_read_attribute(self) -> FrameACLCommandBuilder:
        """
        Deny attribute reads for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "read_attribute",
            allow=False,
            conditions={"pattern": "*"},
        )

    def allow_member_invoke_method(self) -> FrameACLCommandBuilder:
        """
        Allow method invocation for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "invoke_method",
            allow=True,
            conditions={"pattern": "*"},
        )

    def deny_member_invoke_method(self) -> FrameACLCommandBuilder:
        """
        Deny method invocation for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "invoke_method",
            allow=False,
            conditions={"pattern": "*"},
        )

    def allow_member_write_attribute(self) -> FrameACLCommandBuilder:
        """
        Allow attribute writes for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "write_attribute",
            allow=True,
            conditions={"pattern": "*"},
        )

    def deny_member_write_attribute(self) -> FrameACLCommandBuilder:
        """
        Deny attribute writes for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "write_attribute",
            allow=False,
            conditions={"pattern": "*"},
        )

    def allow_member_dunder_access(self) -> FrameACLCommandBuilder:
        """
        Allow dunder-member access for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "dunder_access",
            allow=True,
            conditions={"pattern": "*"},
        )

    def deny_member_dunder_access(self) -> FrameACLCommandBuilder:
        """
        Deny dunder-member access for any member name in the active draft.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self.set_member_operation(
            "dunder_access",
            allow=False,
            conditions={"pattern": "*"},
        )

    def remove_member_rule(self, rule_name: str) -> FrameACLCommandBuilder:
        """
        Remove one member-family rule from the active draft.

        Args:
            rule_name:
                Stable member-rule name to remove.

        Returns:
            FrameACLCommandBuilder: This fluent builder.
        """
        return self._remove_ruleset_rule(
            self.draft_configuration.member_override_ruleset,
            rule_name,
        )

    def commit_change(self) -> FrameACLCommandConfiguration:
        """
        Commit the active command draft through the borrowed generic builder.

        Returns:
            FrameACLCommandConfiguration: Newly installed command revision.
        """
        self.check_cleaned()
        with self._lock:
            configuration = self._frame_acl_builder.commit_change()
            if not isinstance(configuration, FrameACLCommandConfiguration):
                raise RuntimeError(
                    "FrameACLCommandBuilder commit returned a non-command "
                    "configuration."
                )
            return configuration

    def discard_change(self) -> None:
        """
        Discard the active command draft through the borrowed generic builder.

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
    ) -> FrameACLCommandBuilder:
        """
        Upsert one typed rule into the supplied ruleset.

        Args:
            ruleset:
                Borrowed ruleset from the active command configuration.
            operation_name:
                Target operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLCommandBuilder: This fluent builder.

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

    def _remove_ruleset_rule(
            self,
            ruleset: FrameACLRuleSet,
            rule_name: str,
    ) -> FrameACLCommandBuilder:
        """
        Remove one named rule from the supplied ruleset.

        Args:
            ruleset:
                Borrowed ruleset from the active command configuration.
            rule_name:
                Stable rule name to remove.

        Returns:
            FrameACLCommandBuilder: This fluent builder.

        Raises:
            ValueError:
                If `rule_name` is empty.
        """
        self.check_cleaned()
        with self._lock:
            if not rule_name:
                raise ValueError("rule_name cannot be empty.")
            ruleset.remove_rule(rule_name)
            return self
