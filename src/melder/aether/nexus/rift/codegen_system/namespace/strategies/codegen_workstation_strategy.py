from typing import Any, Dict

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)


class CodegenWorkstationStrategy:
    """
    Internal

    Namespace exposure strategy for the room-local workstation.

    Purpose:
        Expose the existing workstation object into the codegen namespace when
        enabled by configuration.
    """

    __slots__ = []

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
            *,
            space: Any,
    ) -> Dict[str, object]:
        """
        Build workstation namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Workstation namespace entries.

        Raises:
            TypeError:
                If `configuration` or `space` is None.
        """
        if configuration is None:
            raise TypeError("configuration cannot be None.")
        if space is None:
            raise TypeError("space cannot be None.")
        if "workstation" not in configuration.exposed_names:
            return {}
        return {
            "workstation": space.workstation,
        }

