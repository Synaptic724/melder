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
from melder.utilities.interfaces import (
    ICodegenTransactionContext,
    ICodegenValidationResult,
)


class CodegenRecursiveControlStrategy(Cleanable):
    """
    Internal

    Recursive-codegen validation strategy.

    Purpose:
        Reject obvious direct recursive-codegen calls when the selected
        codegen posture denies recursive execution.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
    _RECURSIVE_METHOD_NAMES = frozenset(
        (
            "validate_codegen",
            "execute_codegen",
        )
    )

    def __init__(self) -> None:
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        self._lock = None

    def validate(
            self,
            transaction_context: ICodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[ICodegenValidationResult]:
        """
        Validate recursive-codegen posture for one request.

        Args:
            transaction_context:
                Per-call transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when direct recursive codegen is denied;
                otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            namespace_configuration = transaction_context.namespace_configuration
            if namespace_configuration is None:
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message="Namespace configuration is missing for validation.",
                    transaction_id=transaction_context.transaction_id,
                )
            if namespace_configuration.allow_recursive_codegen:
                return None
            for node in ast.walk(syntax_tree):
                if not isinstance(node, ast.Call):
                    continue
                function_node = node.func
                if not isinstance(function_node, ast.Attribute):
                    continue
                owner_node = function_node.value
                if not isinstance(owner_node, ast.Name):
                    continue
                if owner_node.id != "codegen":
                    continue
                if function_node.attr not in self._RECURSIVE_METHOD_NAMES:
                    continue
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message=(
                        "Recursive codegen call '{0}.{1}' is not allowed in this codegen mode.".format(
                            owner_node.id,
                            function_node.attr,
                        )
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
            return None
