import ast
import threading
from typing import Optional, Set

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


class CodegenNameResolutionStrategy(Cleanable):
    """
    Internal

    Name-resolution validation strategy.

    Purpose:
        Validate `ast.Name` usage against the namespace configuration contract
        rather than the live namespace object.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
    _ALWAYS_ALLOWED_NAME_NODES = frozenset(
        (
            "True",
            "False",
            "None",
            "result",
        )
    )

    def __init__(self) -> None:
        """
        Initialize the name-resolution strategy.

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
        Validate namespace-name rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when a name is not allowed; otherwise None.
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
            allowed_names = set(namespace_configuration.exposed_names)
            allowed_names.update(self._ALWAYS_ALLOWED_NAME_NODES)
            allowed_names.update(self._collect_locally_assigned_names(syntax_tree))
            for node in ast.walk(syntax_tree):
                if not isinstance(node, ast.Name):
                    continue
                if not isinstance(node.ctx, ast.Load):
                    continue
                if node.id in allowed_names:
                    continue
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message="Name '{0}' is not available in the codegen namespace.".format(
                        node.id
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
            return None

    def _collect_locally_assigned_names(self, syntax_tree: ast.AST) -> Set[str]:
        """
        Collect names that are assigned locally inside the submitted code.

        Args:
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Set[str]: Names introduced locally through assignment-style nodes.
        """
        self.check_cleaned()
        with self._lock:
            assigned_names: Set[str] = set()
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    assigned_names.add(node.id)
            return assigned_names
