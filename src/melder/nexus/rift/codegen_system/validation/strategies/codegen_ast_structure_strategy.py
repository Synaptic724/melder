import ast
import threading
from typing import TYPE_CHECKING, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )


class CodegenAstStructureStrategy(Cleanable):
    """
    Internal

    Structural AST validation strategy.

    Purpose:
        Reject code shapes that are outside the current governed execution
        contract before deeper policy checks run.

    Threading:
        Stateless validation strategy; it inspects the parsed AST and holds no
        state between calls.

    Registration:
        MELDER KERNEL - guarded. Registered in the `CodegenValidator` strategy
        set; never user-constructed.

    Subsystem Context:
        One rung of the codegen validation chain, which runs BEFORE compilation
        and before any namespace is built. Its verdict feeds a
        `CodegenValidationResult`, which `CodegenValidationReporter` formats for
        the room-facing command.

    System Context:
        This strategy is a STATIC gate: it rejects code SHAPES that fall outside the governed execution contract. It reads the AST rather than the
        live namespace, which is the whole point of validating first - the
        execution environment does not exist yet, and building it to find out
        would be exactly the escape the gate exists to prevent.
        Shape is checked first because later policy strategies reason about specific node kinds; a construct nobody anticipated would otherwise pass unexamined simply because no strategy claimed it.
        Its checks are deliberately described as rejecting OBVIOUS violations.
        That honesty matters: static analysis of Python cannot be exhaustive, so
        the validation chain is defence in depth alongside the namespace
        denylists and the ACL posture, not a proof of safety on its own.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Structural AST validation strategy. Melder kernel machinery: read it "
        "to understand the runtime, do not drive it directly."
    )

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
        del self._lock

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
