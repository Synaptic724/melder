import ast
import threading
from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.icodegentransactioncontext import ICodegenTransactionContext
from melder.utilities.interfaces.icodegenvalidationresult import ICodegenValidationResult


class CodegenImportPolicyStrategy(Cleanable):
    """
    Internal

    Import-policy validation strategy.

    Purpose:
        Validate import statements against the selected codegen posture.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the import-policy strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the strategy.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        del self._lock

    def validate(
            self,
            transaction_context: ICodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[ICodegenValidationResult]:
        """
        Validate import policy rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when a rule is violated; otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            namespace_configuration = transaction_context.namespace_configuration
            if namespace_configuration is None:
                return self._reject(
                    transaction_context,
                    "Namespace configuration is missing for validation.",
                )
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.Import):
                    if not namespace_configuration.imports_enabled:
                        return self._reject(
                            transaction_context,
                            "Import statements are not allowed in this codegen mode.",
                        )
                    for alias in node.names:
                        module_root = alias.name.split(".")[0]
                        if self._import_root_is_denied(
                                module_root,
                                namespace_configuration,
                        ):
                            return self._reject(
                                transaction_context,
                                "Import root '{0}' is not allowed in this codegen mode.".format(
                                    module_root
                                ),
                            )
                if isinstance(node, ast.ImportFrom):
                    if not namespace_configuration.imports_enabled:
                        return self._reject(
                            transaction_context,
                            "Import-from statements are not allowed in this codegen mode.",
                        )
                    if node.level != 0:
                        return self._reject(
                            transaction_context,
                            "Relative imports are not allowed in this codegen mode.",
                        )
                    if any(alias.name == "*" for alias in node.names):
                        return self._reject(
                            transaction_context,
                            "Wildcard imports are not allowed in this codegen mode.",
                        )
                    module_root = (
                        node.module.split(".")[0]
                        if node.module is not None
                        else None
                    )
                    if module_root is None:
                        return self._reject(
                            transaction_context,
                            "Import-from statements must resolve to a module root.",
                        )
                    if self._import_root_is_denied(
                            module_root,
                            namespace_configuration,
                    ):
                        return self._reject(
                            transaction_context,
                            "Import root '{0}' is not allowed in this codegen mode.".format(
                                module_root
                            ),
                        )
            return None

    @staticmethod
    def _import_root_is_denied(
            module_root: str,
            namespace_configuration: CodegenNamespaceConfiguration,
    ) -> bool:
        """
        Return whether one import root is denied by the current config.

        Args:
            module_root:
                Root module name being imported.
            namespace_configuration:
                Current namespace configuration.

        Returns:
            bool: True when the module root is denied.
        """
        denied_module_roots = set(namespace_configuration.denied_import_module_roots)
        if module_root in denied_module_roots:
            return True
        allowed_module_roots = set(namespace_configuration.allowed_import_module_roots)
        if len(allowed_module_roots) == 0:
            return False
        return module_root not in allowed_module_roots

    @staticmethod
    def _reject(
            transaction_context: ICodegenTransactionContext,
            message: str,
    ) -> ICodegenValidationResult:
        """
        Build one import-policy validation failure result.

        Args:
            transaction_context:
                Per-call transaction context.
            message:
                Failure message.

        Returns:
            CodegenValidationResult: Import-policy validation failure.
        """
        return CodegenValidationResult.validation_failed(
            frame_name=transaction_context.frame_name,
            message=message,
            transaction_id=transaction_context.transaction_id,
        )
