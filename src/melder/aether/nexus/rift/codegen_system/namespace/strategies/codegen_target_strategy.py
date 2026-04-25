from typing import Any, Dict

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)


class CodegenTargetStrategy:
    """
    Internal

    Namespace exposure strategy for the current room target.

    Purpose:
        Expose the currently selected workstation target into the namespace
        while keeping missing-target behavior non-fatal.
    """

    __slots__ = []

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
            *,
            space: Any,
    ) -> Dict[str, object]:
        """
        Build target namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Target namespace entries.

        Raises:
            TypeError:
                If `configuration` or `space` is None.
        """
        if configuration is None:
            raise TypeError("configuration cannot be None.")
        if space is None:
            raise TypeError("space cannot be None.")
        if "target" not in configuration.exposed_names:
            return {}
        try:
            target = space.workstation.get_target()
        except ValueError:
            target = None
        return {
            "target": target,
        }

