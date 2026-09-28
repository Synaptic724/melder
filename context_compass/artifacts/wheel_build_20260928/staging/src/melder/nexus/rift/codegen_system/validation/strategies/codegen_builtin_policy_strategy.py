import ast
import threading
from typing import TYPE_CHECKING, Optional

from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )


class CodegenBuiltinPolicyStrategy(Cleanable):
    """
    Internal

    Builtins-policy validation strategy.

    Purpose:
        Block dangerous builtin usage in the selected codegen posture.

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
        This strategy is a STATIC gate: it blocks dangerous builtin usage for the selected posture. It reads the AST rather than the
        live namespace, which is the whole point of validating first - the
        execution environment does not exist yet, and building it to find out
        would be exactly the escape the gate exists to prevent.
        It pairs with `CodegenBuiltinsStrategy` on the namespace side: this rejects the call statically, that withholds the name at runtime. Neither alone is sufficient, because a denied name can still be reached indirectly and a statically-missed call still needs the name absent.
        Its checks are deliberately described as rejecting OBVIOUS violations.
        That honesty matters: static analysis of Python cannot be exhaustive, so
        the validation chain is defence in depth alongside the namespace
        denylists and the ACL posture, not a proof of safety on its own.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Builtins-policy validation strategy. Melder kernel machinery: read it
        to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
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
        del self._lock

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
        self.check_cleaned()
        with self._lock:
            namespace_configuration = transaction_context.namespace_configuration
            if namespace_configuration is None:
                return self._reject(
                    transaction_context,
                    "Namespace configuration is missing for validation.",
                )
            denied_builtin_names = set(namespace_configuration.denied_builtin_names)
            for node in ast.walk(syntax_tree):
                if not isinstance(node, ast.Call):
                    continue
                function_node = node.func
                if not isinstance(function_node, ast.Name):
                    continue
                builtin_name = function_node.id
                if builtin_name not in denied_builtin_names:
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
