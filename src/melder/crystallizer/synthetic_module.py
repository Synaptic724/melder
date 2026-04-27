import sys
import threading
from types import ModuleType
from typing import Any, Dict, List, Mapping, Optional, Sequence

class SyntheticModule(ModuleType):
    """
    Live in-memory module embodiment for crystallized source.

    `SyntheticModule` is the runtime-facing counterpart to `SpellCrystal`. It
    owns one synthetic module namespace, the persisted source/hash metadata that
    produced it, and the minimal publication state needed to expose the module
    through normal Python import machinery when desired.

    Contract:
    - the module name is the canonical runtime identity while the module is
      live in this process
    - source and dependency metadata are owned directly by the module object
    - publication into `sys.modules` is explicit and reversible
    - cleanup mirrors the repo `Cleanable` contract even though this class
      cannot inherit `Cleanable` directly because `ModuleType` has a
      conflicting instance layout
    - cleanup is deterministic and unpublishes the module before dropping owned
      metadata
    """

    def __init__(
            self,
            module_name: str,
            spell_crystal_id: str,
            source_text: str,
            source_sha256: str,
            binding_signature: str,
            export_names: Optional[Sequence[str]] = None,
            internal_dependency_names: Optional[Sequence[str]] = None,
            external_dependency_names: Optional[Sequence[str]] = None,
            physical_file_path: Optional[str] = None,
            materialized_directory_path: Optional[str] = None,
            module_docstring: Optional[str] = None,
    ) -> None:
        """
        Initialize one live synthetic module object.

        Args:
            module_name:
                Canonical runtime/import name for the module.
            spell_crystal_id:
                Crystal identity that produced or owns this module source.
            source_text:
                Current source text for the module.
            source_sha256:
                SHA256 fingerprint of the current source text.
            binding_signature:
                Spell-facing binding-signature string associated with this
                module's primary bound surface.
            export_names:
                Optional export/public-surface names.
            internal_dependency_names:
                Optional internal managed dependency names.
            external_dependency_names:
                Optional external/environment dependency names.
            physical_file_path:
                Optional file path backing the module.
            materialized_directory_path:
                Optional directory where the module has been materialized.
            module_docstring:
                Optional module docstring exposed through `__doc__`.

        Raises:
            ValueError:
                If required identity or source values are empty.
        """
        if not module_name:
            raise ValueError("module_name must not be empty.")
        if not spell_crystal_id:
            raise ValueError("spell_crystal_id must not be empty.")
        if not source_text:
            raise ValueError("source_text must not be empty.")
        if not source_sha256:
            raise ValueError("source_sha256 must not be empty.")
        if not binding_signature:
            raise ValueError("binding_signature must not be empty.")

        ModuleType.__init__(self, module_name, module_docstring)

        self._lock: Optional[threading.RLock] = threading.RLock()
        self._cleaned: bool = False
        self._spell_crystal_id: Optional[str] = spell_crystal_id
        self._source_text: Optional[str] = source_text
        self._source_sha256: Optional[str] = source_sha256
        self._binding_signature: Optional[str] = binding_signature
        self._export_names: Optional[List[str]] = (
            list(export_names) if export_names is not None else []
        )
        self._internal_dependency_names: Optional[List[str]] = (
            list(internal_dependency_names)
            if internal_dependency_names is not None
            else []
        )
        self._external_dependency_names: Optional[List[str]] = (
            list(external_dependency_names)
            if external_dependency_names is not None
            else []
        )
        self._physical_file_path: Optional[str] = physical_file_path
        self._materialized_directory_path: Optional[str] = materialized_directory_path
        self._published_in_sys_modules: bool = False

    def cleanup(self) -> None:
        """
        Unpublish the module and clear owned metadata.

        Cleanup contract:
        - idempotent
        - removes the module from `sys.modules` when this exact object is
          currently published
        - removes non-dunder runtime namespace values
        - clears owned metadata and then drops the lock reference
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            published_module = sys.modules.get(self.__name__)
            if published_module is self:
                del sys.modules[self.__name__]

            removable_names = [
                name for name in self.__dict__.keys()
                if not (name.startswith("__") and name.endswith("__"))
                and not name.startswith("_")
            ]
            for name in removable_names:
                del self.__dict__[name]

            self._spell_crystal_id = None
            self._source_text = None
            self._source_sha256 = None
            self._binding_signature = None
            self._export_names = None
            self._internal_dependency_names = None
            self._external_dependency_names = None
            self._physical_file_path = None
            self._materialized_directory_path = None
            self._published_in_sys_modules = False
            self._lock = None
    @property
    def cleaned(self) -> bool:
        """
        Return whether the module has already been cleaned.

        Returns:
            bool:
                True when cleanup has completed.
        """
        return self._cleaned

    @property
    def is_cleaned(self) -> bool:
        """
        Return the cleaned-state alias used elsewhere in the runtime.

        Returns:
            bool:
                Current cleaned-state flag.
        """
        return self._cleaned

    def check_cleaned(self) -> None:
        """
        Raise when the module has already been cleaned.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        if self._cleaned:
            raise RuntimeError("SyntheticModule has already been cleaned.")

    @property
    def spell_crystal_id(self) -> str:
        """
        Return the crystal identity backing this live module.

        Returns:
            str:
                Stable `SpellCrystal` id associated with this module.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_crystal_id

    @property
    def source_text(self) -> str:
        """
        Return the current source text attached to this module.

        Returns:
            str:
                Current module source text.
        """
        self.check_cleaned()
        with self._lock:
            return self._source_text

    @property
    def source_sha256(self) -> str:
        """
        Return the SHA256 fingerprint of the current module source.

        Returns:
            str:
                SHA256 fingerprint of `source_text`.
        """
        self.check_cleaned()
        with self._lock:
            return self._source_sha256

    @property
    def binding_signature(self) -> str:
        """
        Return the binding-signature string attached to this module.

        Returns:
            str:
                Binding-signature string associated with the module.
        """
        self.check_cleaned()
        with self._lock:
            return self._binding_signature

    @property
    def export_names(self) -> List[str]:
        """
        Return the current export/public-surface names.

        Returns:
            List[str]:
                Copy of the module export names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._export_names)

    @property
    def internal_dependency_names(self) -> List[str]:
        """
        Return the internal managed dependency names for this module.

        Returns:
            List[str]:
                Copy of internal dependency names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._internal_dependency_names)

    @property
    def external_dependency_names(self) -> List[str]:
        """
        Return the external/environment dependency names for this module.

        Returns:
            List[str]:
                Copy of external dependency names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._external_dependency_names)

    @property
    def physical_file_path(self) -> Optional[str]:
        """
        Return the physical file path backing the module, if any.

        Returns:
            Optional[str]:
                Physical file path, if one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._physical_file_path

    @property
    def materialized_directory_path(self) -> Optional[str]:
        """
        Return the materialized directory path, if any.

        Returns:
            Optional[str]:
                Materialized directory path, if one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._materialized_directory_path

    @property
    def published_in_sys_modules(self) -> bool:
        """
        Return whether the module is currently published in `sys.modules`.

        Returns:
            bool:
                True when this exact module object is currently registered in
                `sys.modules` under its canonical name.
        """
        self.check_cleaned()
        with self._lock:
            return self._published_in_sys_modules

    def update_source_text(self, source_text: str, source_sha256: str) -> None:
        """
        Replace the module source text and fingerprint.

        Args:
            source_text:
                Replacement source text.
            source_sha256:
                SHA256 fingerprint for the replacement source text.

        Raises:
            ValueError:
                If either value is empty.
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if not source_text:
                raise ValueError("source_text must not be empty.")
            if not source_sha256:
                raise ValueError("source_sha256 must not be empty.")

            self._source_text = source_text
            self._source_sha256 = source_sha256

    def update_analysis(
            self,
            export_names: Optional[Sequence[str]] = None,
            internal_dependency_names: Optional[Sequence[str]] = None,
            external_dependency_names: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Replace the derived export and dependency metadata for this module.

        Args:
            export_names:
                Replacement export/public-surface names, if provided.
            internal_dependency_names:
                Replacement internal dependency names, if provided.
            external_dependency_names:
                Replacement external dependency names, if provided.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if export_names is not None:
                self._export_names = list(export_names)
            if internal_dependency_names is not None:
                self._internal_dependency_names = list(internal_dependency_names)
            if external_dependency_names is not None:
                self._external_dependency_names = list(external_dependency_names)

    def set_materialization_location(
            self,
            physical_file_path: Optional[str],
            materialized_directory_path: Optional[str],
    ) -> None:
        """
        Update filesystem materialization metadata for this module.

        Args:
            physical_file_path:
                Physical module file path, if any.
            materialized_directory_path:
                Directory path where the module has been materialized, if any.
        """
        self.check_cleaned()
        with self._lock:
            self._physical_file_path = physical_file_path
            self._materialized_directory_path = materialized_directory_path

    def merge_namespace(self, namespace_values: Mapping[str, Any]) -> None:
        """
        Merge runtime namespace values into the live module namespace.

        Args:
            namespace_values:
                Mapping of names to values that should be inserted into the
                module namespace.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.__dict__.update(namespace_values)

    def publish_to_sys_modules(self) -> None:
        """
        Publish this module object into `sys.modules` under its canonical name.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            sys.modules[self.__name__] = self
            self._published_in_sys_modules = True

    def unpublish_from_sys_modules(self) -> None:
        """
        Remove this module from `sys.modules` if this exact object is published.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            published_module = sys.modules.get(self.__name__)
            if published_module is self:
                del sys.modules[self.__name__]
            self._published_in_sys_modules = False

    def describe(self) -> Dict[str, Any]:
        """
        Return a snapshot of the live synthetic module state.

        Returns:
            Dict[str, Any]:
                Dictionary snapshot of the module metadata and publication state.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "module_name": self.__name__,
                "spell_crystal_id": self._spell_crystal_id,
                "source_text": self._source_text,
                "source_sha256": self._source_sha256,
                "binding_signature": self._binding_signature,
                "export_names": list(self._export_names),
                "internal_dependency_names": list(self._internal_dependency_names),
                "external_dependency_names": list(self._external_dependency_names),
                "physical_file_path": self._physical_file_path,
                "materialized_directory_path": self._materialized_directory_path,
                "published_in_sys_modules": self._published_in_sys_modules,
            }
