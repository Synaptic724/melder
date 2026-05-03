import threading
from typing import Dict, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ICodegenNamespaceConfiguration


class CodegenNamespaceConfiguration(Cleanable, ICodegenNamespaceConfiguration):
    """
    Internal

    Namespace exposure policy for one codegen request.

    Purpose:
        Represent the policy/configuration view of which stable names the
        codegen runtime intends to expose before any live namespace objects are
        assembled.

    Contract:
        - Keeps stable namespace-name exposure explicit.
        - Separates policy/configuration from the live namespace object.
        - Returns exposed names in stable first-class order.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_include_viewer",
        "_include_workstation",
        "_include_target",
        "_include_command",
        "_include_codegen",
        "_imports_enabled",
        "_allowed_import_module_roots",
        "_denied_import_module_roots",
        "_denied_builtin_names",
        "_allow_unsafe_reflection",
        "_allow_dunder_access",
        "_allow_recursive_codegen",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            include_viewer: bool = True,
            include_workstation: bool = True,
            include_target: bool = True,
            include_command: bool = True,
            include_codegen: bool = True,
            imports_enabled: bool = False,
            allowed_import_module_roots: Tuple[str, ...] = tuple(),
            denied_import_module_roots: Tuple[str, ...] = tuple(),
            denied_builtin_names: Tuple[str, ...] = tuple(),
            allow_unsafe_reflection: bool = False,
            allow_dunder_access: bool = False,
            allow_recursive_codegen: bool = False,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one namespace configuration.

        Args:
            frame_name:
                Target frame name for this configuration.
            include_viewer:
                Whether to expose `viewer`.
            include_workstation:
                Whether to expose `workstation`.
            include_target:
                Whether to expose `target`.
            include_command:
                Whether to expose `command`.
            include_codegen:
                Whether to expose `codegen`.
            imports_enabled:
                Whether import statements are enabled.
            allowed_import_module_roots:
                Allowed import module roots.
            denied_import_module_roots:
                Denied import module roots.
            denied_builtin_names:
                Denied builtin names.
            allow_unsafe_reflection:
                Whether unsafe reflection helpers are allowed.
            allow_dunder_access:
                Whether dunder attribute access is allowed.
            allow_recursive_codegen:
                Whether recursive codegen is allowed.
            metadata:
                Optional configuration metadata.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._include_viewer: bool = include_viewer
        self._include_workstation: bool = include_workstation
        self._include_target: bool = include_target
        self._include_command: bool = include_command
        self._include_codegen: bool = include_codegen
        self._imports_enabled: bool = imports_enabled
        self._allowed_import_module_roots: Tuple[str, ...] = tuple(
            allowed_import_module_roots
        )
        self._denied_import_module_roots: Tuple[str, ...] = tuple(
            denied_import_module_roots
        )
        self._denied_builtin_names: Tuple[str, ...] = tuple(
            denied_builtin_names
        )
        self._allow_unsafe_reflection: bool = allow_unsafe_reflection
        self._allow_dunder_access: bool = allow_dunder_access
        self._allow_recursive_codegen: bool = allow_recursive_codegen
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear namespace-configuration-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_name = None
            self._include_viewer = None
            self._include_workstation = None
            self._include_target = None
            self._include_command = None
            self._include_codegen = None
            self._imports_enabled = None
            self._allowed_import_module_roots = None
            self._denied_import_module_roots = None
            self._denied_builtin_names = None
            self._allow_unsafe_reflection = None
            self._allow_dunder_access = None
            self._allow_recursive_codegen = None
            self._metadata.clear()
            self._metadata = None
        self._lock = None

    @classmethod
    def create_default(
            cls,
            *,
            frame_name: str,
            include_target: bool = True,
            imports_enabled: bool = False,
            allowed_import_module_roots: Tuple[str, ...] = tuple(),
            denied_import_module_roots: Tuple[str, ...] = tuple(),
            denied_builtin_names: Tuple[str, ...] = tuple(),
            allow_unsafe_reflection: bool = False,
            allow_dunder_access: bool = False,
            allow_recursive_codegen: bool = False,
            metadata: Optional[Dict[str, object]] = None,
    ) -> "CodegenNamespaceConfiguration":
        """
        Build the current stable default namespace contract.

        Args:
            frame_name:
                Target frame name for the configuration.
            include_target:
                Whether to expose `target`.
            imports_enabled:
                Whether import statements are enabled.
            allowed_import_module_roots:
                Allowed import module roots.
            denied_import_module_roots:
                Denied import module roots.
            denied_builtin_names:
                Denied builtin names.
            allow_unsafe_reflection:
                Whether unsafe reflection helpers are allowed.
            allow_dunder_access:
                Whether dunder access is allowed.
            allow_recursive_codegen:
                Whether recursive codegen is allowed.
            metadata:
                Optional configuration metadata.

        Returns:
            CodegenNamespaceConfiguration: Default configuration.
        """
        return cls(
            frame_name=frame_name,
            include_target=include_target,
            imports_enabled=imports_enabled,
            allowed_import_module_roots=allowed_import_module_roots,
            denied_import_module_roots=denied_import_module_roots,
            denied_builtin_names=denied_builtin_names,
            allow_unsafe_reflection=allow_unsafe_reflection,
            allow_dunder_access=allow_dunder_access,
            allow_recursive_codegen=allow_recursive_codegen,
            metadata=metadata,
        )

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this namespace configuration.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def exposed_names(self) -> Tuple[str, ...]:
        """
        Return the stable ordered namespace names enabled by this config.

        Returns:
            Tuple[str, ...]: Enabled namespace names.
        """
        self.check_cleaned()
        with self._lock:
            enabled_names = []
            if self._include_viewer:
                enabled_names.append("viewer")
            if self._include_workstation:
                enabled_names.append("workstation")
            if self._include_target:
                enabled_names.append("target")
            if self._include_command:
                enabled_names.append("command")
            if self._include_codegen:
                enabled_names.append("codegen")
            return tuple(enabled_names)

    @property
    def imports_enabled(self) -> bool:
        """
        Return whether import statements are enabled for this namespace.

        Returns:
            bool: True when imports are enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._imports_enabled

    @property
    def allowed_import_module_roots(self) -> Tuple[str, ...]:
        """
        Return the allowed import module roots.

        Returns:
            Tuple[str, ...]: Allowed import module roots.
        """
        self.check_cleaned()
        with self._lock:
            return self._allowed_import_module_roots

    @property
    def denied_import_module_roots(self) -> Tuple[str, ...]:
        """
        Return the denied import module roots.

        Returns:
            Tuple[str, ...]: Denied import module roots.
        """
        self.check_cleaned()
        with self._lock:
            return self._denied_import_module_roots

    @property
    def denied_builtin_names(self) -> Tuple[str, ...]:
        """
        Return builtin names denied to codegen.

        Returns:
            Tuple[str, ...]: Denied builtin names.
        """
        self.check_cleaned()
        with self._lock:
            return self._denied_builtin_names

    @property
    def allow_unsafe_reflection(self) -> bool:
        """
        Return whether unsafe reflection helpers are allowed.

        Returns:
            bool: True when unsafe reflection is allowed.
        """
        self.check_cleaned()
        with self._lock:
            return self._allow_unsafe_reflection

    @property
    def allow_dunder_access(self) -> bool:
        """
        Return whether dunder access is allowed.

        Returns:
            bool: True when dunder access is allowed.
        """
        self.check_cleaned()
        with self._lock:
            return self._allow_dunder_access

    @property
    def allow_recursive_codegen(self) -> bool:
        """
        Return whether recursive codegen is allowed.

        Returns:
            bool: True when recursive codegen is allowed.
        """
        self.check_cleaned()
        with self._lock:
            return self._allow_recursive_codegen

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached configuration metadata copy.

        Returns:
            Dict[str, object]: Detached metadata copy.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)
