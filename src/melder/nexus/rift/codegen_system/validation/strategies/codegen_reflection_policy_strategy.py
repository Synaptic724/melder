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


class CodegenReflectionPolicyStrategy(Cleanable):
    """
    Internal

    Reflection-policy validation strategy.

    Purpose:
        Reject obvious reflection/introspection helper usage when the selected
        codegen posture denies unsafe reflection.

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
        This strategy is a STATIC gate: it rejects reflection and introspection helpers when the posture denies unsafe reflection. It reads the AST rather than the
        live namespace, which is the whole point of validating first - the
        execution environment does not exist yet, and building it to find out
        would be exactly the escape the gate exists to prevent.
        Reflection defeats every name-based control at once - it turns a string into an object - so a posture that denies dangerous builtins while permitting reflection would not actually be denying anything.
        Its checks are deliberately described as rejecting OBVIOUS violations.
        That honesty matters: static analysis of Python cannot be exhaustive, so
        the validation chain is defence in depth alongside the namespace
        denylists and the ACL posture, not a proof of safety on its own.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Reflection-policy validation strategy. Melder kernel machinery: read "
        "it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]
    _REFLECTION_MODULE_NAMES = frozenset(
        (
            "inspect",
            "importlib",
            "builtins",
        )
    )
    _REFLECTION_BUILTIN_NAMES = frozenset(
        (
            "dir",
            "getattr",
            "hasattr",
            "setattr",
            "delattr",
            "globals",
            "locals",
            "vars",
            "type",
        )
    )
    _REFLECTION_HELPER_NAMES_BY_MODULE = {
        "inspect": frozenset(
            (
                "getmembers",
                "getmodule",
                "getsource",
                "getsourcelines",
                "signature",
                "stack",
            )
        ),
        "importlib": frozenset(
            (
                "import_module",
                "reload",
            )
        ),
        "builtins": frozenset(
            (
                "dir",
                "getattr",
                "hasattr",
                "setattr",
                "delattr",
                "globals",
                "locals",
                "vars",
                "type",
            )
        ),
    }

    def __init__(self) -> None:
        """
        Initialize the strategy with its own reentrant guard lock.

        Contract:
            Stateless beyond the guard lock: the reflection module/helper
            alias sets are recomputed per `validate` call from the request
            AST, so one instance serves every request in the strategy set.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently release the strategy's guard lock.

        Contract:
            Double-checked under the lock and terminal; the lock is deleted
            last. Cleanup touches neither the owning validator nor any
            in-flight transaction context.

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
        Validate reflection-policy rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when reflection is disallowed and a direct
                reflection helper call is used; otherwise None.
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
            if namespace_configuration.allow_unsafe_reflection:
                return None
            reflection_module_aliases = self._collect_reflection_module_aliases(
                syntax_tree
            )
            reflection_helper_aliases = self._collect_reflection_helper_aliases(
                syntax_tree,
            )
            for node in ast.walk(syntax_tree):
                if not isinstance(node, ast.Call):
                    continue
                function_node = node.func
                if isinstance(function_node, ast.Name):
                    if (
                            function_node.id in self._REFLECTION_BUILTIN_NAMES
                            or function_node.id in reflection_helper_aliases
                    ):
                        return CodegenValidationResult.validation_failed(
                            frame_name=transaction_context.frame_name,
                            message=(
                                "Reflection helper '{0}' is not allowed in this codegen mode.".format(
                                    function_node.id
                                )
                            ),
                            transaction_id=transaction_context.transaction_id,
                        )
                    continue
                if not isinstance(function_node, ast.Attribute):
                    continue
                owner_node = function_node.value
                if not isinstance(owner_node, ast.Name):
                    continue
                if owner_node.id not in reflection_module_aliases:
                    continue
                return CodegenValidationResult.validation_failed(
                    frame_name=transaction_context.frame_name,
                    message=(
                        "Reflection helper '{0}.{1}' is not allowed in this codegen mode.".format(
                            owner_node.id,
                            function_node.attr,
                        )
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
            return None

    def _collect_reflection_module_aliases(
            self,
            syntax_tree: ast.AST,
    ) -> set[str]:
        """
        Collect names bound to reflection-capable modules.

        Args:
            syntax_tree:
                Parsed AST for the request.

        Returns:
            set[str]: Names bound to reflection-capable modules.
        """
        self.check_cleaned()
        with self._lock:
            reflection_module_aliases = set(self._REFLECTION_MODULE_NAMES)
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_root = alias.name.split(".")[0]
                        if module_root not in self._REFLECTION_MODULE_NAMES:
                            continue
                        reflection_module_aliases.add(
                            alias.asname if alias.asname is not None else module_root
                        )
                if isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        continue
                    module_root = node.module.split(".")[0]
                    if module_root not in self._REFLECTION_MODULE_NAMES:
                        continue
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        reflection_module_aliases.add(
                            alias.asname if alias.asname is not None else alias.name
                        )
                if isinstance(node, ast.Assign):
                    if len(node.targets) != 1:
                        continue
                    target_node = node.targets[0]
                    if not isinstance(target_node, ast.Name):
                        continue
                    value_node = node.value
                    if not isinstance(value_node, ast.Name):
                        continue
                    if value_node.id in reflection_module_aliases:
                        reflection_module_aliases.add(target_node.id)
            return reflection_module_aliases

    def _collect_reflection_helper_aliases(
            self,
            syntax_tree: ast.AST,
    ) -> set[str]:
        """
        Collect direct names bound to reflection helper callables.

        Args:
            syntax_tree:
                Parsed AST for the request.

        Returns:
            set[str]: Names bound to reflection helper callables.
        """
        self.check_cleaned()
        with self._lock:
            reflection_helper_aliases = set(self._REFLECTION_BUILTIN_NAMES)
            for node in ast.walk(syntax_tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        continue
                    module_root = node.module.split(".")[0]
                    helper_names = self._REFLECTION_HELPER_NAMES_BY_MODULE.get(
                        module_root,
                        frozenset(),
                    )
                    for alias in node.names:
                        if alias.name not in helper_names:
                            continue
                        reflection_helper_aliases.add(
                            alias.asname if alias.asname is not None else alias.name
                        )
                if isinstance(node, ast.Assign):
                    if len(node.targets) != 1:
                        continue
                    target_node = node.targets[0]
                    if not isinstance(target_node, ast.Name):
                        continue
                    value_node = node.value
                    if not isinstance(value_node, ast.Name):
                        continue
                    if value_node.id in reflection_helper_aliases:
                        reflection_helper_aliases.add(target_node.id)
            return reflection_helper_aliases
