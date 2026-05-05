from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclcommandconfiguration import IFrameACLCommandConfiguration

@runtime_checkable
class IFrameACLCommandBuilder(ICleanable, Protocol):
    """
    Fluent builder contract for one active command-family ACL draft.
    """

    id: str
    draft_configuration: IFrameACLCommandConfiguration

    def use_profile(self, profile_name: str) -> "IFrameACLCommandBuilder":
        ...

    def use_precision_profile(
            self,
            profile_name: Optional[str],
    ) -> "IFrameACLCommandBuilder":
        ...

    def set_frame_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCommandBuilder":
        ...

    def set_conduit_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCommandBuilder":
        ...

    def set_spell_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCommandBuilder":
        ...

    def set_member_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCommandBuilder":
        ...

    def allow_frame_enable(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_frame_enable(self) -> "IFrameACLCommandBuilder":
        ...

    def allow_conduit_enable(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_conduit_enable(self) -> "IFrameACLCommandBuilder":
        ...

    def allow_spell_enable(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_spell_enable(self) -> "IFrameACLCommandBuilder":
        ...

    def allow_member_read_attribute(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_member_read_attribute(self) -> "IFrameACLCommandBuilder":
        ...

    def allow_member_invoke_method(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_member_invoke_method(self) -> "IFrameACLCommandBuilder":
        ...

    def allow_member_write_attribute(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_member_write_attribute(self) -> "IFrameACLCommandBuilder":
        ...

    def allow_member_dunder_access(self) -> "IFrameACLCommandBuilder":
        ...

    def deny_member_dunder_access(self) -> "IFrameACLCommandBuilder":
        ...

    def remove_member_rule(self, rule_name: str) -> "IFrameACLCommandBuilder":
        ...

    def commit_change(self) -> IFrameACLCommandConfiguration:
        ...

    def discard_change(self) -> None:
        ...
