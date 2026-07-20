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


class CodegenRecursiveControlStrategy(Cleanable):
    """
    Internal

    Recursive-codegen validation strategy.

    Purpose:
        Reject obvious direct recursive-codegen calls when the selected
        codegen posture denies recursive execution.

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
        This strategy is a STATIC gate: it rejects direct recursive-codegen calls when the posture denies them. It reads the AST rather than the
        live namespace, which is the whole point of validating first - the
        execution environment does not exist yet, and building it to find out
        would be exactly the escape the gate exists to prevent.
        It is the static half of a two-part control; `CodegenControlSurface` applies the same permission at runtime, so indirect reachings are still refused even when static analysis cannot see the call.
        Its checks are deliberately described as rejecting OBVIOUS violations.
        That honesty matters: static analysis of Python cannot be exhaustive, so
        the validation chain is defence in depth alongside the namespace
        denylists and the ACL posture, not a proof of safety on its own.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
    _RECURSIVE_METHOD_NAMES = frozenset(
        (
            "validate_codegen",
            "execute_codegen",
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
        del self._lock

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
        """
        Validate recursive-codegen posture for one request.

        Args:
            transaction_context:
                Per-call transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when direct recursive codegen is denied;
                otherwise None.
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
            if namespace_configuration.allow_recursive_codegen:
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
                if owner_node.id != "codegen":
                    continue
                if function_node.attr not in self._RECURSIVE_METHOD_NAMES:
                    continue
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message=(
                        "Recursive codegen call '{0}.{1}' is not allowed in this codegen mode.".format(
                            owner_node.id,
                            function_node.attr,
                        )
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
            return None
