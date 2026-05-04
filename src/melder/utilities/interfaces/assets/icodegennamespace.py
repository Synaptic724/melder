from typing import runtime_checkable, Protocol, Optional, Dict

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class ICodegenNamespace(ICleanable, Protocol):
    """
    Interface for one live codegen namespace.
    """

    @property
    def configuration(self) -> ICodegenNamespaceConfiguration:
        """
        Return the configuration that produced this namespace.
        """
        ...

    @property
    def globals_dict(self) -> Dict[str, object]:
        """
        Return the live globals dictionary.
        """
        ...

    @property
    def locals_dict(self) -> Dict[str, object]:
        """
        Return the live locals dictionary.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return detached metadata for this namespace.
        """
        ...

    def get_result(self) -> Optional[object]:
        """
        Return the optional `result` value from this namespace.
        """
        ...
