import threading
from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLViewBuilder(Cleanable):
    """
    Purpose:
        Provide a fluent authoring surface for one active view ACL draft.

    Contract:
        - Layers over one active view draft owned by `FrameACLBuilder`.
        - Does not replace the generic builder draft/commit lifecycle.
        - Mutates the live draft configuration in place under the owning
          builder's lock.
        - Returns itself from fluent mutation methods.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_acl_builder",
    ]

    def __init__(self, frame_acl_builder: object) -> None:
        """
        Initialize one fluent view ACL builder.

        Args:
            frame_acl_builder:
                Owning generic frame ACL builder with an active view draft.

        Returns:
            None.
        """
        from melder.aether.nexus.acl.builder.frame_acl_builder import (
            FrameACLBuilder,
        )

        super().__init__()
        if not isinstance(frame_acl_builder, FrameACLBuilder):
            raise TypeError("frame_acl_builder must be a FrameACLBuilder.")
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
            self._frame_acl_builder = None
            self._id = None
        self._lock = None

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
    def draft_configuration(self) -> FrameACLViewConfiguration:
        """
        Return the active view draft configuration.

        Returns:
            FrameACLViewConfiguration: Active view draft.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_acl_builder._require_active_view_configuration()

    def use_profile(self, profile_name: str) -> "FrameACLViewBuilder":
        """
        Replace the base view profile on the active draft.

        Args:
            profile_name:
                Registered base view profile name.

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
    ) -> "FrameACLViewBuilder":
        """
        Replace or clear the precision view profile on the active draft.

        Args:
            profile_name:
                Precision profile name, or None to clear.

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
    ) -> "FrameACLViewBuilder":
        """
        Upsert one frame-family rule on the active draft.

        Args:
            operation_name:
                Target operation name.
            allow:
                True for allow, False for deny.
            rule_name:
                Optional stable rule name.
            conditions:
                Optional condition payload.

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
    ) -> "FrameACLViewBuilder":
        """
        Upsert one conduit-family rule on the active draft.
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
    ) -> "FrameACLViewBuilder":
        """
        Upsert one spell-family rule on the active draft.
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
    ) -> "FrameACLViewBuilder":
        """
        Upsert one member-family rule on the active draft.
        """
        return self._set_ruleset_operation(
            self.draft_configuration.member_override_ruleset,
            operation_name=operation_name,
            allow=allow,
            rule_name=rule_name,
            conditions=conditions,
        )

    def allow_frame_visibility(self) -> "FrameACLViewBuilder":
        return self.set_frame_operation("visible", allow=True)

    def deny_frame_visibility(self) -> "FrameACLViewBuilder":
        return self.set_frame_operation("visible", allow=False)

    def allow_frame_payload(self) -> "FrameACLViewBuilder":
        return self.set_frame_operation("show_payload", allow=True)

    def deny_frame_payload(self) -> "FrameACLViewBuilder":
        return self.set_frame_operation("show_payload", allow=False)

    def allow_conduit_policy(self) -> "FrameACLViewBuilder":
        return self.set_conduit_operation("show_policy", allow=True)

    def deny_conduit_policy(self) -> "FrameACLViewBuilder":
        return self.set_conduit_operation("show_policy", allow=False)

    def allow_conduit_peer_links(self) -> "FrameACLViewBuilder":
        return self.set_conduit_operation("show_peer_links", allow=True)

    def deny_conduit_peer_links(self) -> "FrameACLViewBuilder":
        return self.set_conduit_operation("show_peer_links", allow=False)

    def allow_spell_class_profile(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_class_profile", allow=True)

    def deny_spell_class_profile(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_class_profile", allow=False)

    def allow_spell_callable_profile(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_callable_profile", allow=True)

    def deny_spell_callable_profile(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_callable_profile", allow=False)

    def allow_spell_instance_members(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_instance_members", allow=True)

    def deny_spell_instance_members(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_instance_members", allow=False)

    def allow_spell_dynamic_access(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_dynamic_access", allow=True)

    def deny_spell_dynamic_access(self) -> "FrameACLViewBuilder":
        return self.set_spell_operation("show_dynamic_access", allow=False)

    def allow_member_name(
            self,
            member_name: str,
            *,
            rule_name: Optional[str] = None,
    ) -> "FrameACLViewBuilder":
        """
        Allow one explicit member name in the active draft.
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
    ) -> "FrameACLViewBuilder":
        """
        Deny one explicit member name in the active draft.
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
    ) -> "FrameACLViewBuilder":
        """
        Allow one member pattern in the active draft.
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
    ) -> "FrameACLViewBuilder":
        """
        Deny one member pattern in the active draft.
        """
        if not pattern:
            raise ValueError("pattern cannot be empty.")
        return self.set_member_operation(
            "show_member",
            allow=False,
            rule_name=rule_name,
            conditions={"pattern": pattern},
        )

    def remove_member_rule(self, rule_name: str) -> "FrameACLViewBuilder":
        """
        Remove one member-family rule from the active draft.
        """
        return self._remove_ruleset_rule(
            self.draft_configuration.member_override_ruleset,
            rule_name,
        )

    def commit_change(self) -> FrameACLViewConfiguration:
        """
        Commit the active view draft through the owning generic builder.

        Returns:
            FrameACLViewConfiguration: Newly installed view revision.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_acl_builder.commit_change()

    def discard_change(self) -> None:
        """
        Discard the active view draft through the owning generic builder.

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
    ) -> "FrameACLViewBuilder":
        """
        Upsert one typed rule into the supplied ruleset.
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
    ) -> "FrameACLViewBuilder":
        """
        Remove one named rule from the supplied ruleset.
        """
        self.check_cleaned()
        with self._lock:
            if not rule_name:
                raise ValueError("rule_name cannot be empty.")
            ruleset.remove_rule(rule_name)
            return self
