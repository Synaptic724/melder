from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclcodegenconfiguration import IFrameACLCodegenConfiguration

@runtime_checkable
class IFrameACLCodegenBuilder(ICleanable, Protocol):
    """
    Fluent builder contract for one active codegen-family ACL draft.
    """

    @property
    def id(self) -> str:
        ...

    @property
    def draft_configuration(self) -> IFrameACLCodegenConfiguration:
        ...

    def use_profile(self, profile_name: str) -> "IFrameACLCodegenBuilder":
        ...

    def use_precision_profile(
            self,
            profile_name: Optional[str],
    ) -> "IFrameACLCodegenBuilder":
        ...

    def set_frame_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def set_conduit_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def set_spell_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def set_capability_operation(
            self,
            operation_name: str,
            *,
            allow: bool,
            rule_name: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def enable_imports(self) -> "IFrameACLCodegenBuilder":
        ...

    def disable_imports(self) -> "IFrameACLCodegenBuilder":
        ...

    def allow_import_module_roots(
            self,
            *module_roots: str,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def deny_import_module_roots(
            self,
            *module_roots: str,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def allow_builtin_names(
            self,
            *builtin_names: str,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def deny_builtin_names(
            self,
            *builtin_names: str,
    ) -> "IFrameACLCodegenBuilder":
        ...

    def allow_unsafe_reflection(self) -> "IFrameACLCodegenBuilder":
        ...

    def deny_unsafe_reflection(self) -> "IFrameACLCodegenBuilder":
        ...

    def allow_dunder_access(self) -> "IFrameACLCodegenBuilder":
        ...

    def deny_dunder_access(self) -> "IFrameACLCodegenBuilder":
        ...

    def allow_recursive_codegen(self) -> "IFrameACLCodegenBuilder":
        ...

    def deny_recursive_codegen(self) -> "IFrameACLCodegenBuilder":
        ...

    def remove_capability_rule(self, rule_name: str) -> "IFrameACLCodegenBuilder":
        ...

    def commit_change(self) -> IFrameACLCodegenConfiguration:
        ...

    def discard_change(self) -> None:
        ...

