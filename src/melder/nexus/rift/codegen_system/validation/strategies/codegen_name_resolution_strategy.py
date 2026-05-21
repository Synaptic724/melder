import ast
import builtins
import threading
from typing import Optional, Set
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.nexus.rift.codegen_system.codegen_transaction_context import CodegenTransactionContext
from melder.nexus.rift.codegen_system.validation.codegen_validation_result import CodegenValidationResult


class CodegenNameResolutionStrategy(Cleanable):
    """
    Internal

    Name-resolution validation strategy.

    Purpose:
        Validate `ast.Name` usage against the namespace configuration contract
        rather than the live namespace object.
    """

    __melder_internal__ = _mrg.sentinel
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
        del self._lock

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
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
            allowed_names.update(self._collect_locally_declared_names(syntax_tree))
            allowed_names.update(self._collect_local_parameter_names(syntax_tree))
            allowed_names.update(self._collect_imported_names(syntax_tree))
            allowed_names.update(
                self._collect_allowed_builtin_names(namespace_configuration)
            )
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

    def _collect_locally_declared_names(self, syntax_tree: ast.AST) -> Set[str]:
        """
        Collect names introduced by local function and class declarations.

        Args:
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Set[str]: Declared local function and class names.
        """
        self.check_cleaned()
        with self._lock:
            declared_names: Set[str] = set()
            for node in ast.walk(syntax_tree):
                if isinstance(
                        node,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                            ast.ClassDef,
                        ),
                ):
                    declared_names.add(node.name)
            return declared_names

    def _collect_imported_names(self, syntax_tree: ast.AST) -> Set[str]:
        """
        Collect imported names introduced by import statements.

        Args:
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Set[str]: Imported local names.
        """
        self.check_cleaned()
        with self._lock:
            imported_names: Set[str] = set()
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_names.add(
                            alias.asname if alias.asname is not None else alias.name.split(".")[0]
                        )
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        imported_names.add(
                            alias.asname if alias.asname is not None else alias.name
                        )
            return imported_names

    def _collect_local_parameter_names(self, syntax_tree: ast.AST) -> Set[str]:
        """
        Collect function and lambda parameter names defined locally.

        Args:
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Set[str]: Parameter names introduced by local callable scopes.
        """
        self.check_cleaned()
        with self._lock:
            parameter_names: Set[str] = set()
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.arg):
                    parameter_names.add(node.arg)
            return parameter_names

    def _collect_allowed_builtin_names(
            self,
            namespace_configuration: CodegenNamespaceConfiguration,
    ) -> Set[str]:
        """
        Collect builtin names still available under the current configuration.

        Args:
            namespace_configuration:
                Current namespace configuration.

        Returns:
            Set[str]: Allowed builtin names.
        """
        self.check_cleaned()
        with self._lock:
            denied_builtin_names = set(namespace_configuration.denied_builtin_names)
            return {
                builtin_name
                for builtin_name in vars(builtins).keys()
                if builtin_name not in denied_builtin_names
            }
