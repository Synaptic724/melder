import ast
from typing import Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenAstStructureStrategy:
    """
    Internal

    Structural AST validation strategy.

    Purpose:
        Reject code shapes that are outside the initial governed codegen
        contract before deeper policy checks run.
    """

    __slots__ = []

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
        """
        Validate structural AST rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when a rule is violated; otherwise None.
        """
        for node in ast.walk(syntax_tree):
            if isinstance(node, ast.FunctionDef):
                return self._reject(
                    transaction_context,
                    "Function definitions are not allowed in this codegen mode.",
                )
            if isinstance(node, ast.AsyncFunctionDef):
                return self._reject(
                    transaction_context,
                    "Async function definitions are not allowed in this codegen mode.",
                )
            if isinstance(node, ast.ClassDef):
                return self._reject(
                    transaction_context,
                    "Class definitions are not allowed in this codegen mode.",
                )
            if isinstance(node, ast.Global):
                return self._reject(
                    transaction_context,
                    "global statements are not allowed in this codegen mode.",
                )
            if isinstance(node, ast.Nonlocal):
                return self._reject(
                    transaction_context,
                    "nonlocal statements are not allowed in this codegen mode.",
                )
        return None

    @staticmethod
    def _reject(
            transaction_context: CodegenTransactionContext,
            message: str,
    ) -> CodegenValidationResult:
        """
        Build one structural validation failure result.

        Args:
            transaction_context:
                Per-call transaction context.
            message:
                Failure message.

        Returns:
            CodegenValidationResult: Structural validation failure.
        """
        return CodegenValidationResult.validation_failed(
            frame_name=transaction_context.frame_name,
            message=message,
            transaction_id=transaction_context.transaction_id,
        )

