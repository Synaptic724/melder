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


class CodegenAttributeAccessStrategy(Cleanable):
    """
    Internal

    Attribute-access validation strategy.

    Purpose:
        Reject obviously unsafe attribute-access patterns in the current
        governed codegen mode.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the attribute-access strategy.

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
        self.check_cleaned()
        with self._lock:
            namespace_configuration = transaction_context.namespace_configuration
            if namespace_configuration is None:
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message="Namespace configuration is missing for validation.",
                    transaction_id=transaction_context.transaction_id,
                )
            if namespace_configuration.allow_dunder_access:
                return None
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
