import ast
import threading
from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import (
    ICodegenTransactionContext,
    ICodegenValidationResult,
)


class CodegenAstStructureStrategy(Cleanable):
    """
    Internal

    Structural AST validation strategy.

    Purpose:
        Reject code shapes that are outside the current governed execution
        contract before deeper policy checks run.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the structural validation strategy.

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
        self.check_cleaned()
        with self._lock:
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    return self._reject(
                        transaction_context,
                        "Async function definitions are not allowed in this codegen mode.",
                    )
                if isinstance(node, ast.Await):
                    return self._reject(
                        transaction_context,
                        "await expressions are not allowed in this codegen mode.",
                    )
                if isinstance(node, ast.AsyncFor):
                    return self._reject(
                        transaction_context,
                        "async for statements are not allowed in this codegen mode.",
                    )
                if isinstance(node, ast.AsyncWith):
                    return self._reject(
                        transaction_context,
                        "async with statements are not allowed in this codegen mode.",
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
            transaction_context: ICodegenTransactionContext,
            message: str,
    ) -> ICodegenValidationResult:
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
