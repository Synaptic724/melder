import ast
from typing import Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_ast_structure_strategy import (
    CodegenAstStructureStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_attribute_access_strategy import (
    CodegenAttributeAccessStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_builtin_policy_strategy import (
    CodegenBuiltinPolicyStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_import_policy_strategy import (
    CodegenImportPolicyStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_name_resolution_strategy import (
    CodegenNameResolutionStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenValidator:
    """
    Internal

    Root validation orchestrator for one codegen request.

    Purpose:
        Own the validation boundary for generated Python without absorbing
        later execution or reporting responsibilities.

    Contract:
        - Validates one `CodegenTransactionContext`.
        - Performs AST parse as the first live validation step.
        - Returns syntax failure when parsing fails.
        - Returns the current not-implemented result when syntax is valid but
          the deeper strategy family is not yet implemented.
    """

    __slots__ = [
        "_ast_structure_strategy",
        "_import_policy_strategy",
        "_builtin_policy_strategy",
        "_name_resolution_strategy",
        "_attribute_access_strategy",
    ]

    def __init__(self) -> None:
        """
        Initialize the validator and its strategy family.

        Returns:
            None.
        """
        self._ast_structure_strategy: CodegenAstStructureStrategy = (
            CodegenAstStructureStrategy()
        )
        self._import_policy_strategy: CodegenImportPolicyStrategy = (
            CodegenImportPolicyStrategy()
        )
        self._builtin_policy_strategy: CodegenBuiltinPolicyStrategy = (
            CodegenBuiltinPolicyStrategy()
        )
        self._name_resolution_strategy: CodegenNameResolutionStrategy = (
            CodegenNameResolutionStrategy()
        )
        self._attribute_access_strategy: CodegenAttributeAccessStrategy = (
            CodegenAttributeAccessStrategy()
        )

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> CodegenValidationResult:
        """
        Validate one codegen transaction context.

        Args:
            transaction_context:
                Per-call transaction context to validate.

        Returns:
            CodegenValidationResult: Validation result for the request.

        Raises:
            TypeError:
                If `transaction_context` is None.
        """
        if transaction_context is None:
            raise TypeError("transaction_context cannot be None.")
        try:
            syntax_tree = ast.parse(transaction_context.code, mode="exec")
        except SyntaxError as exc:
            return CodegenValidationResult.syntax_error(
                frame_name=transaction_context.frame_name,
                transaction_id=transaction_context.transaction_id,
                message=self._build_syntax_error_message(exc),
            )
        validation_result = self._run_strategy(
            self._ast_structure_strategy,
            transaction_context,
            syntax_tree,
        )
        if validation_result is not None:
            return validation_result
        validation_result = self._run_strategy(
            self._import_policy_strategy,
            transaction_context,
            syntax_tree,
        )
        if validation_result is not None:
            return validation_result
        validation_result = self._run_strategy(
            self._builtin_policy_strategy,
            transaction_context,
            syntax_tree,
        )
        if validation_result is not None:
            return validation_result
        validation_result = self._run_strategy(
            self._name_resolution_strategy,
            transaction_context,
            syntax_tree,
        )
        if validation_result is not None:
            return validation_result
        validation_result = self._run_strategy(
            self._attribute_access_strategy,
            transaction_context,
            syntax_tree,
        )
        if validation_result is not None:
            return validation_result
        return CodegenValidationResult.not_implemented(
            frame_name=transaction_context.frame_name,
            transaction_id=transaction_context.transaction_id,
        )

    @staticmethod
    def _build_syntax_error_message(exc: SyntaxError) -> str:
        """
        Build one stable syntax-error message for codegen validation output.

        Args:
            exc:
                Raised syntax error.

        Returns:
            str: Stable syntax-error message.
        """
        line_number = exc.lineno
        offset = exc.offset
        if line_number is None or offset is None:
            return "SyntaxError: {0}".format(exc.msg)
        return "SyntaxError at line {0}, column {1}: {2}".format(
            line_number,
            offset,
            exc.msg,
        )

    @staticmethod
    def _run_strategy(
            strategy: object,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
        """
        Execute one validation strategy and return its optional failure result.

        Args:
            strategy:
                Strategy object exposing `validate(...)`.
            transaction_context:
                Per-call transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]: Failure result when the strategy
            rejects the request; otherwise None.
        """
        return strategy.validate(transaction_context, syntax_tree)
