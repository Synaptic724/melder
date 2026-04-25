import ast
import threading
from typing import Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import (
    ICodegenTransactionContext,
    ICodegenValidationResult,
)


class CodegenBuiltinPolicyStrategy(Cleanable):
    """
    Internal

    Builtins-policy validation strategy.

    Purpose:
        Block dangerous builtin usage in the current governed codegen mode.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
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

    def __init__(self) -> None:
        """
        Initialize the builtins-policy strategy.

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
        self._lock = None

    def validate(
            self,
            transaction_context: ICodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[ICodegenValidationResult]:
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
        self.check_cleaned()
        with self._lock:
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
            transaction_context: ICodegenTransactionContext,
            message: str,
    ) -> ICodegenValidationResult:
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
