import ast
import threading
from typing import Optional

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
from melder.utilities.interfaces.interfaces import (
    ICodegenTransactionContext,
    ICodegenValidationResult,
)


class CodegenReflectionPolicyStrategy(Cleanable):
    """
    Internal

    Reflection-policy validation strategy.

    Purpose:
        Reject obvious reflection/introspection helper usage when the selected
        codegen posture denies unsafe reflection.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
    _REFLECTION_MODULE_NAMES = frozenset(
        (
            "inspect",
            "importlib",
            "builtins",
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
        Validate reflection-policy rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when reflection is disallowed and a direct
                reflection helper call is used; otherwise None.
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
            if namespace_configuration.allow_unsafe_reflection:
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
                if owner_node.id not in self._REFLECTION_MODULE_NAMES:
                    continue
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message=(
                        "Reflection helper '{0}.{1}' is not allowed in this codegen mode.".format(
                            owner_node.id,
                            function_node.attr,
                        )
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
            return None
