import ast
from typing import Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenBuiltinPolicyStrategy:
    """
    Internal

    Builtins-policy validation strategy.

    Purpose:
        Block dangerous builtin usage in the current governed codegen mode.
    """

    __slots__ = []
    _DENIED_BUILTIN_NAMES = frozenset(
        (
            "__import__",
            "eval",
            "exec",
            "compile",
            "globals",
            "locals",
            "vars",
            "getattr",
            "setattr",
            "delattr",
        )
    )

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
        """
        Validate builtin-policy rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when a denied builtin is used; otherwise None.
        """
        for node in ast.walk(syntax_tree):
            if not isinstance(node, ast.Call):
                continue
            function_node = node.func
            if not isinstance(function_node, ast.Name):
                continue
            builtin_name = function_node.id
            if builtin_name not in self._DENIED_BUILTIN_NAMES:
                continue
            return self._reject(
                transaction_context,
                "Builtin '{0}' is not allowed in this codegen mode.".format(
                    builtin_name
                ),
            )
        return None

    @staticmethod
    def _reject(
            transaction_context: CodegenTransactionContext,
            message: str,
    ) -> CodegenValidationResult:
        """
        Build one builtins-policy validation failure result.

        Args:
            transaction_context:
                Per-call transaction context.
            message:
                Failure message.

        Returns:
            CodegenValidationResult: Builtins-policy validation failure.
        """
        return CodegenValidationResult.validation_failed(
            frame_name=transaction_context.frame_name,
            message=message,
            transaction_id=transaction_context.transaction_id,
        )

