import ast
from typing import Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenAttributeAccessStrategy:
    """
    Internal

    Attribute-access validation strategy.

    Purpose:
        Reject obviously unsafe attribute-access patterns in the current
        governed codegen mode.
    """

    __slots__ = []

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
        """
        Validate attribute-access rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when a disallowed attribute pattern is used;
                otherwise None.
        """
        for node in ast.walk(syntax_tree):
            if not isinstance(node, ast.Attribute):
                continue
            if node.attr.startswith("__"):
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message="Dunder attribute access '{0}' is not allowed in this codegen mode.".format(
                        node.attr
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
        return None

