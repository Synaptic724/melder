from typing import Any, Dict

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)


class CodegenRoomObjectsStrategy:
    """
    Internal

    Namespace exposure strategy for stable room/runtime objects.

    Purpose:
        Expose the stable room/runtime objects that belong in the initial
        codegen namespace contract.

    Contract:
        - Exposes only names enabled by the namespace configuration.
        - Owns room-object exposure only:
          `rift`, `space`, `viewer`, and `frame_name`.
    """

    __slots__ = []

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
            *,
            rift: Any,
            space: Any,
    ) -> Dict[str, object]:
        """
        Build room-object namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            rift:
                Owning `Rift`.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Room-object namespace entries.

        Raises:
            TypeError:
                If `configuration`, `rift`, or `space` is None.
        """
        if configuration is None:
            raise TypeError("configuration cannot be None.")
        if rift is None:
            raise TypeError("rift cannot be None.")
        if space is None:
            raise TypeError("space cannot be None.")
        namespace_entries: Dict[str, object] = {}
        exposed_names = configuration.exposed_names
        if "rift" in exposed_names:
            namespace_entries["rift"] = rift
        if "space" in exposed_names:
            namespace_entries["space"] = space
        if "viewer" in exposed_names:
            namespace_entries["viewer"] = space.frame_viewer
        if "frame_name" in exposed_names:
            namespace_entries["frame_name"] = configuration.frame_name
        return namespace_entries

