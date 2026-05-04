from typing import runtime_checkable, Protocol, Optional, List, Dict, Any, Mapping, Sequence

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class ISyntheticModule(ICleanable, Protocol):
    """
    Protocol definition for one live synthetic module embodiment.

    This protocol mirrors the public runtime contract exposed by
    `SyntheticModule` so crystallizer code can reason over a real type seam
    instead of a magic marker attribute.
    """

    __name__: str
    _lock: Optional[RLock]
    _cleaned: bool
    _spell_crystal_id: Optional[str]
    _source_text: Optional[str]
    _source_sha256: Optional[str]
    _binding_signature: Optional[str]
    _export_names: Optional[List[str]]
    _internal_dependency_names: Optional[List[str]]
    _external_dependency_names: Optional[List[str]]
    _physical_file_path: Optional[str]
    _materialized_directory_path: Optional[str]
    _published_in_sys_modules: bool

    @property
    def cleaned(self) -> bool:
        """Return whether the module has already been cleaned."""
        ...

    @property
    def is_cleaned(self) -> bool:
        """Alias for the cleaned-state flag."""
        ...

    def check_cleaned(self) -> None:
        """
        Raise when the module has already been cleaned.

        Raises:
            RuntimeError: If the module has already been cleaned.
        """
        ...

    def cleanup(self) -> None:
        """
        Cleanup the synthetic module.

        Returns:
            None.
        """
        ...

    @property
    def spell_crystal_id(self) -> str:
        """Return the crystal identity backing this live module."""
        ...

    @property
    def source_text(self) -> str:
        """Return the current source text attached to this module."""
        ...

    @property
    def source_sha256(self) -> str:
        """Return the SHA256 fingerprint of the current source text."""
        ...

    @property
    def binding_signature(self) -> str:
        """Return the binding-signature string attached to this module."""
        ...

    @property
    def export_names(self) -> List[str]:
        """Return the current export/public-surface names."""
        ...

    @property
    def internal_dependency_names(self) -> List[str]:
        """Return the internal managed dependency names."""
        ...

    @property
    def external_dependency_names(self) -> List[str]:
        """Return the external/environment dependency names."""
        ...

    @property
    def physical_file_path(self) -> Optional[str]:
        """Return the physical file path backing the module, if any."""
        ...

    @property
    def materialized_directory_path(self) -> Optional[str]:
        """Return the materialized directory path, if any."""
        ...

    @property
    def published_in_sys_modules(self) -> bool:
        """Return whether the module is currently published in sys.modules."""
        ...

    @property
    def parent_name(self) -> Optional[str]:
        """Return the parent package name, if any."""
        ...

    @property
    def is_package(self) -> bool:
        """Return whether the module behaves like a package shell."""
        ...

    @property
    def executed_source(self) -> bool:
        """Return whether the module source has executed at least once."""
        ...

    def update_source_text(self, source_text: str, source_sha256: str) -> None:
        """
        Replace the module source text and fingerprint.

        Returns:
            None.
        """
        ...

    def update_analysis(
            self,
            export_names: Optional[Sequence[str]] = None,
            internal_dependency_names: Optional[Sequence[str]] = None,
            external_dependency_names: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Replace the derived export and dependency metadata for this module.

        Returns:
            None.
        """
        ...

    def set_materialization_location(
            self,
            physical_file_path: Optional[str],
            materialized_directory_path: Optional[str],
    ) -> None:
        """
        Update filesystem materialization metadata for this module.

        Returns:
            None.
        """
        ...

    def merge_namespace(self, namespace_values: Mapping[str, Any]) -> None:
        """
        Merge runtime namespace values into the live module namespace.

        Returns:
            None.
        """
        ...

    def execute_source(self) -> None:
        """
        Execute the module source into the live namespace.

        Returns:
            None.
        """
        ...

    def publish_to_sys_modules(self) -> None:
        """
        Publish this module object into sys.modules.

        Returns:
            None.
        """
        ...

    def unpublish_from_sys_modules(self) -> None:
        """
        Remove this module from sys.modules if it is currently published.

        Returns:
            None.
        """
        ...

    def register_in_import_registry(
            self,
            auto_parent_package_shells: bool = True,
    ) -> None:
        """
        Register this module in the synthetic import registry.

        Returns:
            None.
        """
        ...

    def unregister_from_import_registry(self) -> None:
        """
        Remove this module from the synthetic import registry.

        Returns:
            None.
        """
        ...

    def materialize(
            self,
            auto_parent_package_shells: bool = True,
            install_import_hook: bool = False,
    ) -> "ISyntheticModule":
        """
        Register, publish, and execute this module as live world state.

        Returns:
            ISyntheticModule: This live module object.
        """
        ...

    def reload_via_importlib(
            self,
            install_import_hook: bool = True,
    ) -> "ISyntheticModule":
        """
        Reload this registered module through importlib.

        Returns:
            ISyntheticModule: The reloaded live module object.
        """
        ...

    def describe(self) -> Dict[str, Any]:
        """
        Return a snapshot of the live synthetic-module state.

        Returns:
            Dict[str, Any]: Synthetic-module state snapshot.
        """
        ...
