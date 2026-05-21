import threading
from typing import TYPE_CHECKING, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet

if TYPE_CHECKING:
    from melder.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.utilities.interfaces.iframeaclviewconfiguration import IFrameACLViewConfiguration


class FrameACLViewBuilder(Cleanable):
    """
    Purpose:
        Provide fluent authoring for one active view-family ACL draft.

    Contract:
        - Borrows one active view draft from the generic ACL builder.
        - Mutates the borrowed typed view configuration in place.
        - Does not own persistence or configuration-chain installation.
        - Returns itself from fluent mutation methods so callers can author one
          draft in a chained style.

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
        Initialize one fluent view ACL builder.

        Args:
            frame_acl_builder:
                Borrowed generic ACL builder that currently owns one active
                view-family draft session.

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
    def draft_configuration(self) -> IFrameACLViewConfiguration:
        """
        Return the currently borrowed active view configuration draft.

        Returns:
            IFrameACLViewConfiguration: Active mutable view draft.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_acl_builder._require_active_view_configuration()

    def use_profile(self, profile_name: str) -> FrameACLViewBuilder:
        """
        Replace the base view profile on the active draft.

        Args:
            profile_name:
                Registered reusable base view profile name.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_acl_builder.set_profile_name(profile_name)
            return self

    def use_precision_profile(
            self,
            profile_name: Optional[str],
    ) -> FrameACLViewBuilder:
        """
        Replace or clear the precision view profile on the active draft.

        Args:
            profile_name:
                Registered precision profile name, or None to clear the current
                precision selection.

        Returns:
            FrameACLViewBuilder: This fluent builder.
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
    ) -> FrameACLViewBuilder:
        """
        Upsert one frame-family rule on the active draft.

        Args:
            operation_name:
                Target view-frame operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLViewBuilder: This fluent builder.
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
    ) -> FrameACLViewBuilder:
        """
        Upsert one conduit-family rule on the active draft.

        Args:
            operation_name:
                Target view-conduit operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLViewBuilder: This fluent builder.
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
    ) -> FrameACLViewBuilder:
        """
        Upsert one spell-family rule on the active draft.

        Args:
            operation_name:
                Target view-spell operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLViewBuilder: This fluent builder.
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
    ) -> FrameACLViewBuilder:
        """
        Upsert one member-family rule on the active draft.

        Args:
            operation_name:
                Target view-member operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload. Member rules are usually
                shaped by `member_name` or `pattern`.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.member_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def allow_frame_visibility(self) -> FrameACLViewBuilder:
        """
        Allow frame visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_frame_operation("visible", allow=True)

    def deny_frame_visibility(self) -> FrameACLViewBuilder:
        """
        Deny frame visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_frame_operation("visible", allow=False)

    def allow_frame_payload(self) -> FrameACLViewBuilder:
        """
        Allow frame payload visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_frame_operation("show_payload", allow=True)

    def deny_frame_payload(self) -> FrameACLViewBuilder:
        """
        Deny frame payload visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_frame_operation("show_payload", allow=False)

    def allow_conduit_policy(self) -> FrameACLViewBuilder:
        """
        Allow conduit policy visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_conduit_operation("show_policy", allow=True)

    def deny_conduit_policy(self) -> FrameACLViewBuilder:
        """
        Deny conduit policy visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_conduit_operation("show_policy", allow=False)

    def allow_conduit_peer_links(self) -> FrameACLViewBuilder:
        """
        Allow conduit peer-link visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_conduit_operation("show_peer_links", allow=True)

    def deny_conduit_peer_links(self) -> FrameACLViewBuilder:
        """
        Deny conduit peer-link visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_conduit_operation("show_peer_links", allow=False)

    def allow_spell_class_profile(self) -> FrameACLViewBuilder:
        """
        Allow class-profile visibility for spells in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_class_profile", allow=True)

    def deny_spell_class_profile(self) -> FrameACLViewBuilder:
        """
        Deny class-profile visibility for spells in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_class_profile", allow=False)

    def allow_spell_callable_profile(self) -> FrameACLViewBuilder:
        """
        Allow callable-profile visibility for spells in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_callable_profile", allow=True)

    def deny_spell_callable_profile(self) -> FrameACLViewBuilder:
        """
        Deny callable-profile visibility for spells in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_callable_profile", allow=False)

    def allow_spell_instance_members(self) -> FrameACLViewBuilder:
        """
        Allow spell instance-member visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_instance_members", allow=True)

    def deny_spell_instance_members(self) -> FrameACLViewBuilder:
        """
        Deny spell instance-member visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_instance_members", allow=False)

    def allow_spell_dynamic_access(self) -> FrameACLViewBuilder:
        """
        Allow spell dynamic-access visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_dynamic_access", allow=True)

    def deny_spell_dynamic_access(self) -> FrameACLViewBuilder:
        """
        Deny spell dynamic-access visibility in the active draft.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self.set_spell_operation("show_dynamic_access", allow=False)

    def allow_member_name(
            self,
            member_name: str,
            *,
            rule_name: Optional[str] = None,
    ) -> FrameACLViewBuilder:
        """
        Allow one exact member name in the active draft.

        Args:
            member_name:
                Exact member name to allow.
            rule_name:
                Optional stable rule name.

        Returns:
            FrameACLViewBuilder: This fluent builder.

        Raises:
            ValueError:
                If `member_name` is empty.
        """
        if not member_name:
            raise ValueError("member_name cannot be empty.")
        return self.set_member_operation(
            "show_member",
            allow=True,
            rule_name=rule_name,
            conditions={"member_name": member_name},
        )

    def deny_member_name(
            self,
            member_name: str,
            *,
            rule_name: Optional[str] = None,
    ) -> FrameACLViewBuilder:
        """
        Deny one exact member name in the active draft.

        Args:
            member_name:
                Exact member name to deny.
            rule_name:
                Optional stable rule name.

        Returns:
            FrameACLViewBuilder: This fluent builder.

        Raises:
            ValueError:
                If `member_name` is empty.
        """
        if not member_name:
            raise ValueError("member_name cannot be empty.")
        return self.set_member_operation(
            "show_member",
            allow=False,
            rule_name=rule_name,
            conditions={"member_name": member_name},
        )

    def allow_member_pattern(
            self,
            pattern: str,
            *,
            rule_name: Optional[str] = None,
    ) -> FrameACLViewBuilder:
        """
        Allow one member-pattern rule in the active draft.

        Args:
            pattern:
                Pattern to allow.
            rule_name:
                Optional stable rule name.

        Returns:
            FrameACLViewBuilder: This fluent builder.

        Raises:
            ValueError:
                If `pattern` is empty.
        """
        if not pattern:
            raise ValueError("pattern cannot be empty.")
        return self.set_member_operation(
            "show_member",
            allow=True,
            rule_name=rule_name,
            conditions={"pattern": pattern},
        )

    def deny_member_pattern(
            self,
            pattern: str,
            *,
            rule_name: Optional[str] = None,
    ) -> FrameACLViewBuilder:
        """
        Deny one member-pattern rule in the active draft.

        Args:
            pattern:
                Pattern to deny.
            rule_name:
                Optional stable rule name.

        Returns:
            FrameACLViewBuilder: This fluent builder.

        Raises:
            ValueError:
                If `pattern` is empty.
        """
        if not pattern:
            raise ValueError("pattern cannot be empty.")
        return self.set_member_operation(
            "show_member",
            allow=False,
            rule_name=rule_name,
            conditions={"pattern": pattern},
        )

    def remove_member_rule(self, rule_name: str) -> FrameACLViewBuilder:
        """
        Remove one member-family rule from the active draft.

        Args:
            rule_name:
                Stable member-rule name to remove.

        Returns:
            FrameACLViewBuilder: This fluent builder.
        """
        return self._remove_ruleset_rule(
            self.draft_configuration.member_override_ruleset,
            rule_name,
        )

    def commit_change(self) -> IFrameACLViewConfiguration:
        """
        Commit the active view draft through the borrowed generic builder.

        Returns:
            IFrameACLViewConfiguration: Newly installed view revision.
        """
        self.check_cleaned()
        with self._lock:
            configuration = self._frame_acl_builder.commit_change()
            if not isinstance(configuration, IFrameACLViewConfiguration):
                raise RuntimeError(
                    "FrameACLViewBuilder commit returned a non-view "
                    "configuration."
                )
            return configuration

    def discard_change(self) -> None:
        """
        Discard the active view draft through the borrowed generic builder.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._frame_acl_builder.discard_change()

    def _set_ruleset_operation(
            self,
            ruleset: IFrameACLRuleSet,
            *,
            operation_name: str,
            allow: bool,
            rule_name: Optional[str],
            conditions: Optional[Dict[str, object]],
    ) -> FrameACLViewBuilder:
        """
        Upsert one typed rule into the supplied ruleset.

        Args:
            ruleset:
                Borrowed ruleset from the active view configuration.
            operation_name:
                Target operation name.
            allow:
                True for an allow rule, False for a deny rule.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional selector or condition payload.

        Returns:
            FrameACLViewBuilder: This fluent builder.

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
            ruleset: IFrameACLRuleSet,
            rule_name: str,
    ) -> FrameACLViewBuilder:
        """
        Remove one named rule from the supplied ruleset.

        Args:
            ruleset:
                Borrowed ruleset from the active view configuration.
            rule_name:
                Stable rule name to remove.

        Returns:
            FrameACLViewBuilder: This fluent builder.

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
