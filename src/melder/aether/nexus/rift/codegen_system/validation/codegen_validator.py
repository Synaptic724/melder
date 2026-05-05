import ast
import threading
from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_recursive_control_strategy import (
    CodegenRecursiveControlStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_reflection_policy_strategy import (
    CodegenReflectionPolicyStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import (
    ICodegenTransactionContext,
    ICodegenValidationResult,
)


class CodegenValidator(Cleanable):
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

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_ast_structure_strategy",
        "_import_policy_strategy",
        "_builtin_policy_strategy",
        "_name_resolution_strategy",
        "_attribute_access_strategy",
        "_reflection_policy_strategy",
        "_recursive_control_strategy",
    ]

    def __init__(self) -> None:
        """
        Initialize the validator and its strategy family.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
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
        self._reflection_policy_strategy: CodegenReflectionPolicyStrategy = (
            CodegenReflectionPolicyStrategy()
        )
        self._recursive_control_strategy: CodegenRecursiveControlStrategy = (
            CodegenRecursiveControlStrategy()
        )

    def cleanup(self) -> None:
        """
        Idempotently cleanup the validator and its strategies.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._ast_structure_strategy.cleanup()
            self._import_policy_strategy.cleanup()
            self._builtin_policy_strategy.cleanup()
            self._name_resolution_strategy.cleanup()
            self._attribute_access_strategy.cleanup()
            self._reflection_policy_strategy.cleanup()
            self._recursive_control_strategy.cleanup()
            self._ast_structure_strategy = None
            self._import_policy_strategy = None
            self._builtin_policy_strategy = None
            self._name_resolution_strategy = None
            self._attribute_access_strategy = None
            self._reflection_policy_strategy = None
            self._recursive_control_strategy = None
        self._lock = None

    def validate(
            self,
            transaction_context: ICodegenTransactionContext,
    ) -> ICodegenValidationResult:
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
        self.check_cleaned()
        with self._lock:
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
            validation_result = self._run_strategy(
                self._reflection_policy_strategy,
                transaction_context,
                syntax_tree,
            )
            if validation_result is not None:
                return validation_result
            validation_result = self._run_strategy(
                self._recursive_control_strategy,
                transaction_context,
                syntax_tree,
            )
            if validation_result is not None:
                return validation_result
            return CodegenValidationResult.validation_accepted(
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
            transaction_context: ICodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[ICodegenValidationResult]:
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
