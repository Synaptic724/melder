from typing import Dict, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class ICodegenNamespaceConfiguration(ICleanable, Protocol):
    """
    Interface for the codegen namespace policy object.
    """

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this configuration.
        """
        ...

    @property
    def exposed_names(self) -> Tuple[str, ...]:
        """
        Return the stable ordered namespace names enabled by this configuration.
        """
        ...

    @property
    def imports_enabled(self) -> bool:
        """
        Return whether import statements are enabled.
        """
        ...

    @property
    def allowed_import_module_roots(self) -> Tuple[str, ...]:
        """
        Return the allowed import module roots.
        """
        ...

    @property
    def denied_import_module_roots(self) -> Tuple[str, ...]:
        """
        Return the denied import module roots.
        """
        ...

    @property
    def denied_builtin_names(self) -> Tuple[str, ...]:
        """
        Return builtin names denied to codegen.
        """
        ...

    @property
    def allow_unsafe_reflection(self) -> bool:
        """
        Return whether unsafe reflection helpers are allowed.
        """
        ...

    @property
    def allow_dunder_access(self) -> bool:
        """
        Return whether dunder attribute access is allowed.
        """
        ...

    @property
    def allow_recursive_codegen(self) -> bool:
        """
        Return whether recursive codegen is allowed.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return detached metadata for this configuration.
        """
        ...

