import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class IFrameACLViewBuilder(ICleanable, Protocol):
    """
    Fluent builder contract for one active view-family ACL draft.
    """

    id: str
    draft_configuration: IFrameACLViewConfiguration

    def use_profile(self, profile_name: str) -> "IFrameACLViewBuilder":
        ...

    def use_precision_profile(
            self,
            profile_name: Optional[str],
    ) -> "IFrameACLViewBuilder":
        ...

    def set_frame_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def set_conduit_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def set_spell_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def set_member_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def allow_frame_visibility(self) -> "IFrameACLViewBuilder":
        ...

    def deny_frame_visibility(self) -> "IFrameACLViewBuilder":
        ...

    def allow_frame_payload(self) -> "IFrameACLViewBuilder":
        ...

    def deny_frame_payload(self) -> "IFrameACLViewBuilder":
        ...

    def allow_conduit_policy(self) -> "IFrameACLViewBuilder":
        ...

    def deny_conduit_policy(self) -> "IFrameACLViewBuilder":
        ...

    def allow_conduit_peer_links(self) -> "IFrameACLViewBuilder":
        ...

    def deny_conduit_peer_links(self) -> "IFrameACLViewBuilder":
        ...

    def allow_spell_class_profile(self) -> "IFrameACLViewBuilder":
        ...

    def deny_spell_class_profile(self) -> "IFrameACLViewBuilder":
        ...

    def allow_spell_callable_profile(self) -> "IFrameACLViewBuilder":
        ...

    def deny_spell_callable_profile(self) -> "IFrameACLViewBuilder":
        ...

    def allow_spell_instance_members(self) -> "IFrameACLViewBuilder":
        ...

    def deny_spell_instance_members(self) -> "IFrameACLViewBuilder":
        ...

    def allow_spell_dynamic_access(self) -> "IFrameACLViewBuilder":
        ...

    def deny_spell_dynamic_access(self) -> "IFrameACLViewBuilder":
        ...

    def allow_member_name(
            self,
            member_name: str,
            *,
            rule_name: Optional[str] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def deny_member_name(
            self,
            member_name: str,
            *,
            rule_name: Optional[str] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def allow_member_pattern(
            self,
            pattern: str,
            *,
            rule_name: Optional[str] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def deny_member_pattern(
            self,
            pattern: str,
            *,
            rule_name: Optional[str] = None,
    ) -> "IFrameACLViewBuilder":
        ...

    def remove_member_rule(self, rule_name: str) -> "IFrameACLViewBuilder":
        ...

    def commit_change(self) -> IFrameACLViewConfiguration:
        ...

    def discard_change(self) -> None:
        ...
