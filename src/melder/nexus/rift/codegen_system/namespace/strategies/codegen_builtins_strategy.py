import builtins
import threading
from typing import TYPE_CHECKING, Callable, Dict, Optional, Sequence, Tuple

from melder.nexus.acl.configurations.profiles.codegen.stdlib_import_sets import (
    IMPORT_BUILTIN_NAMES,
)

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )


class CodegenBuiltinsStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for Python builtins.

    Purpose:
        Build the runtime `__builtins__` mapping from the current namespace
        configuration so codegen execution respects the compiled builtin
        denylist.

    Threading:
        Stateless exposure strategy; it contributes names to a namespace under
        construction and retains nothing.

    Registration:
        MELDER KERNEL - guarded. Consumed by `CodegenNamespaceBuilder`; never
        user-constructed.

    Subsystem Context:
        One member of the namespace-exposure strategy family. The builder
        composes them instead of hand-building one large globals dict, so each
        exposure decision has exactly one owner.

    System Context:
        It builds the runtime `__builtins__` mapping from the current configuration so execution respects the compiled builtin denylist. Every strategy exposes ONLY what the namespace configuration
        enables, which is what keeps the exposed surface a declared policy
        rather than an emergent consequence of construction order.
        This is the runtime half of builtin control, paired with the static `CodegenBuiltinPolicyStrategy`. Withholding the name is what makes the denial real even where static analysis missed the call.
        The strategy split is what makes the namespace auditable: reading which
        strategies ran, and what configuration enabled, answers "what could this
        code reach" without tracing builder code.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Namespace exposure strategy for Python builtins. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the builtins exposure strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the builtins strategy.

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

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
    ) -> Dict[str, object]:
        """
        Build builtins namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.

        Returns:
            Dict[str, object]: Builtins namespace entries.

        Raises:
            TypeError:
                If `configuration` is None.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is None:
                raise TypeError("configuration cannot be None.")
            builtins_dict = dict(vars(builtins))
            for builtin_name in configuration.denied_builtin_names:
                builtins_dict.pop(builtin_name, None)
            self._install_import_guard(builtins_dict, configuration)
            return {
                "__builtins__": builtins_dict,
            }

    def _install_import_guard(
            self,
            builtins_dict: Dict[str, object],
            configuration: CodegenNamespaceConfiguration,
    ) -> None:
        """
        Replace the runtime `__import__` with a root-checking wrapper when an import list applies.

        Purpose:
            This is the runtime half of the import gate (D-11, B). The static gates refuse the `__import__` name
            wherever an import list applies, but an import statement still calls `__builtins__['__import__']` at
            run time, so that callable must itself check each import's root against the compiled roots.

        Contract:
            - Installs the wrapper only when imports are enabled AND at least one of the allowed or denied
              import-root sets is non-empty (hybrid, precision, permissive). full_access (imports on, no list)
              and safe (imports off, `__import__` already stripped) keep the plain builtin.
            - Replaces each name in `IMPORT_BUILTIN_NAMES` in-place; no name is added that was not present.
            - Mutates `builtins_dict` in place and returns None. Policy and defence in depth, run in the room's
              own process, not isolation.

        Args:
            builtins_dict:
                The runtime builtins mapping under construction, already stripped of `denied_builtin_names`.
            configuration:
                The namespace configuration carrying the imports flag and the compiled import roots.

        Returns:
            None.
        """
        import_list_applies = (
            len(configuration.allowed_import_module_roots) > 0
            or len(configuration.denied_import_module_roots) > 0
        )
        if not (configuration.imports_enabled and import_list_applies):
            return
        real_import = builtins_dict.get("__import__")
        if real_import is None:
            return
        guarded_import = self._build_guarded_import(
            real_import,
            configuration.allowed_import_module_roots,
            configuration.denied_import_module_roots,
        )
        for import_builtin_name in IMPORT_BUILTIN_NAMES:
            builtins_dict[import_builtin_name] = guarded_import

    @staticmethod
    def _build_guarded_import(
            real_import: Callable[..., object],
            allowed_import_module_roots: Tuple[str, ...],
            denied_import_module_roots: Tuple[str, ...],
    ) -> Callable[..., object]:
        """
        Build one `__import__` wrapper that checks each import's root against the compiled roots.

        Purpose:
            Enforce the codegen import posture at run time (D-11, B), so an import statement of an allowed root
            loads normally while a denied or unlisted root is refused with an ImportError naming it.

        Contract:
            - Returns a callable with the `__import__` call shape; the IMPORT_NAME opcode and a direct call both
              reach it. A denied root is refused before the real import runs; an allowed root delegates to it.
            - The root-denial rule matches `CodegenImportPolicyStrategy._import_root_is_denied`: denied when the
              root is in the denied set, or when the allowed set is non-empty and the root is not in it.
            - Pure per call: it closes over the real import and the two immutable root sets, holds no mutable
              state, and raises `ImportError` (never a bare import side effect) when a root is refused.

        Args:
            real_import:
                The real `__import__` the wrapper delegates allowed roots to.
            allowed_import_module_roots:
                Allowed import roots; an empty tuple means "no allow list, only the deny list applies".
            denied_import_module_roots:
                Denied import roots, always refused.

        Returns:
            Callable[..., object]: The guarded `__import__` wrapper.
        """
        allowed_roots = frozenset(allowed_import_module_roots)
        denied_roots = frozenset(denied_import_module_roots)

        def _guarded_import(
                name: str,
                module_globals: Optional[Dict[str, object]] = None,
                module_locals: Optional[Dict[str, object]] = None,
                fromlist: Sequence[str] = (),
                level: int = 0,
        ) -> object:
            """
            Check one import's root, then delegate to the real import or refuse it.

            Args:
                name:
                    The module name being imported; its root is the segment before the first dot.
                module_globals:
                    The importing module's globals, as the import system passes them.
                module_locals:
                    The importing module's locals, as the import system passes them.
                fromlist:
                    The `from`-import names, as the import system passes them.
                level:
                    The relative-import level (0 for absolute imports).

            Returns:
                object: The module the real import returns for an allowed root.

            Raises:
                ImportError:
                    When the root is denied or not on a non-empty allow list.
            """
            module_root = name.split(".")[0] if name else name
            root_is_denied = (
                module_root in denied_roots
                or (len(allowed_roots) > 0 and module_root not in allowed_roots)
            )
            if root_is_denied:
                raise ImportError(
                    "Import root '{0}' is not allowed in this codegen mode.".format(
                        module_root
                    )
                )
            return real_import(
                name,
                module_globals,
                module_locals,
                fromlist,
                level,
            )

        return _guarded_import
