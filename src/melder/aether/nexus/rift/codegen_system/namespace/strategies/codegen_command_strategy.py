from typing import Any, Dict

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)


class CodegenCommandStrategy:
    """
    Internal

    Namespace exposure strategy for the room-facing command surface.

    Purpose:
        Expose the existing room-local command object into the codegen
        namespace when enabled by configuration.
    """

    __slots__ = []

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
            *,
            space: Any,
    ) -> Dict[str, object]:
        """
        Build command namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Command namespace entries.

        Raises:
            TypeError:
                If `configuration` or `space` is None.
        """
        if configuration is None:
            raise TypeError("configuration cannot be None.")
        if space is None:
            raise TypeError("space cannot be None.")
        if "command" not in configuration.exposed_names:
            return {}
        return {
            "command": space.command_system,
        }

