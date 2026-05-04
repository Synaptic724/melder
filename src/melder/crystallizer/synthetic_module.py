import hashlib
import importlib
import importlib.abc
import importlib.util
import sys
import threading
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, Dict, List, Mapping, Optional, Sequence

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.interfaces.interfaces import ISyntheticModule


class _SyntheticModuleImportLoader(importlib.abc.Loader):
    """
    Loader bridge from importlib into the `SyntheticModule` registry.

    Purpose:
        Let normal importlib machinery create and execute registered synthetic
        modules without forcing callers to manually juggle `sys.modules`,
        `ModuleSpec`, or package-shell setup themselves.
    """

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        """
        Return the registered synthetic module object for one spec.

        Purpose:
            Hand importlib the already-registered world object rather than
            allocating a second disconnected module instance.

        Args:
            spec:
                Importlib spec for one registered synthetic module.

        Returns:
            ModuleType:
                The registered synthetic module object.

        Raises:
            ImportError:
                If the spec name is not registered.
        """
        module = SyntheticModule.create_module_for_spec(spec)
        if module is None:
            raise ImportError(
                "No registered synthetic module exists for '{0}'.".format(
                    spec.name,
                )
            )
        return module

    def exec_module(self, module: ModuleType) -> None:
        """
        Execute one registered synthetic module into its live namespace.

        Purpose:
            Delegate execution back to the registered synthetic module so the
            same world object owns publication, parent binding, and executed
            state.

        Args:
            module:
                Module object supplied by importlib.

        Returns:
            None.

        Raises:
            ImportError:
                If the supplied module is not a registered synthetic module.
        """
        if not isinstance(module, SyntheticModule):
            raise ImportError(
                "Synthetic loader can only execute SyntheticModule objects."
            )
        SyntheticModule.exec_registered_module(module.__name__)


class _SyntheticModuleMetaPathFinder(importlib.abc.MetaPathFinder):
    """
    Finder exposing registered synthetic modules to importlib.

    Purpose:
        Allow normal `import ...` / `importlib.import_module(...)` flows to
        discover crystallizer-owned synthetic modules through the registry.
    """

    def find_spec(
            self,
            fullname: str,
            path: object = None,
            target: object = None,
    ) -> Optional[ModuleSpec]:
        """
        Return a spec when the requested module is registered synthetically.

        Args:
            fullname:
                Fully qualified module name being imported.
            path:
                Parent package search path from importlib. It is accepted for
                protocol compatibility but not used directly because lookup is
                registry-driven.
            target:
                Optional importlib reload target. It is accepted for protocol
                compatibility but not used directly.

        Returns:
            Optional[ModuleSpec]:
                Registered synthetic module spec, or None when the name is not
                owned by the synthetic registry.
        """
        return SyntheticModule.build_registered_spec(fullname)


class SyntheticModule(ModuleType, ISyntheticModule):
    """
    Live in-memory module embodiment for crystallized source.

    Purpose:
        `SyntheticModule` is the world-first runtime embodiment of one managed
        software unit. It owns:
        - module identity
        - source text and source hash
        - dependency metadata
        - package-shell semantics when needed
        - importlib-capable activation mechanics

    Contract:
        - the module name is the canonical runtime identity while the module is
          live in this process
        - source and dependency metadata are owned directly by the module object
        - publication into `sys.modules` is explicit, reversible, and available
          through both manual and importlib-driven paths
        - importlib support is registry-backed and cycle-aware because modules
          are published before execution
        - cleanup mirrors the repo `Cleanable` contract even though this class
          cannot inherit `Cleanable` directly because `ModuleType` has a
          conflicting instance layout
        - cleanup is deterministic, unregisters the module from the synthetic
          import registry, unpublishes it, detaches parent bindings, and then
          drops owned metadata

    Why this exists:
        The experiments proved that world-first module behavior depends on more
        than storing source text on a `ModuleType`. We need one runtime object
        that can:
        - exist as a real importable module
        - participate in package graphs
        - survive importlib-style circular activation semantics
        - reload cleanly at explicit boundaries
        - still expose the crystallizer-owned metadata that ties the live
          module back to durable truth
    """

    __melder_internal__ = _mrg.sentinel
    _registry_lock = threading.RLock()
    _registered_modules_by_name: Dict[str, "SyntheticModule"] = {}
    _load_order: List[str] = []
    _import_loader: Optional[_SyntheticModuleImportLoader] = None
    _meta_path_finder: Optional[_SyntheticModuleMetaPathFinder] = None

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
            parent_name: Optional[str] = None,
            is_package: bool = False,
    ) -> None:
        """
        Initialize one live synthetic module object.

        Purpose:
            Build one in-memory managed module that can later be:
            - manually published
            - importlib-loaded
            - reloaded
            - unloaded cleanly

        Args:
            module_name:
                Canonical runtime/import name for the module. This is the live
                world identity while the module is registered.
            spell_crystal_id:
                Crystal identity that produced or owns this module source. This
                is the bridge back to durable world truth.
            source_text:
                Current source text for the module. This is what later
                `execute_source()` and reload flows run.
            source_sha256:
                SHA256 fingerprint of the current source text. It should match
                the current `source_text`, not some older persisted revision.
            binding_signature:
                Spell-facing binding-signature string associated with this
                module's primary bound surface. This is loader/bind metadata,
                not importlib metadata.
            export_names:
                Optional export/public-surface names already known from crystal
                analysis.
            internal_dependency_names:
                Optional internal managed dependency names that belong to the
                same synthetic or crystallized world.
            external_dependency_names:
                Optional external/environment dependency names outside the
                managed synthetic world.
            physical_file_path:
                Optional physical file path backing the module when the live
                module is a projection of file-backed truth.
            materialized_directory_path:
                Optional directory where the module has been materialized as a
                file-backed projection.
            module_docstring:
                Optional module docstring exposed through `__doc__` on the live
                module object.
            parent_name:
                Optional explicit parent package name. This matters for dotted
                module graphs and package attachment.
            is_package:
                True when the module should behave like a package shell rather
                than a leaf module.

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
        self._parent_name: Optional[str] = (
            parent_name if parent_name is not None else module_name.rpartition(".")[0] or None
        )
        self._is_package: bool = is_package
        self._executed_source: bool = False

        self.__file__ = "<synthetic:{0}>".format(module_name)
        self.__package__ = module_name if is_package else (self._parent_name or "")
        if is_package:
            self.__path__ = [self.__file__]
        self.__loader__ = None
        self.__spec__ = None

    def cleanup(self) -> None:
        """
        Unregister, unpublish, and clear owned metadata.

        Cleanup contract:
        - idempotent
        - removes the module from the synthetic import registry
        - removes the module from `sys.modules` when this exact object is
          currently published
        - detaches the module from its parent package binding when applicable
        - removes non-dunder runtime namespace values
        - clears owned metadata and then drops the lock reference

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self.unregister_from_import_registry()
            self._detach_from_parent_package()
            published_module = sys.modules.get(self.__name__)
            if published_module is self:
                del sys.modules[self.__name__]

            removable_names = [
                name
                for name in self.__dict__.keys()
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
            self._parent_name = None
            self._is_package = False
            self._executed_source = False
            self.__loader__ = None
            self.__spec__ = None
            if hasattr(self, "__path__"):
                delattr(self, "__path__")
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

    @property
    def parent_name(self) -> Optional[str]:
        """
        Return the parent package name, if any.

        Returns:
            Optional[str]:
                Parent package name for this module.
        """
        self.check_cleaned()
        with self._lock:
            return self._parent_name

    @property
    def is_package(self) -> bool:
        """
        Return whether this module should behave as a package shell.

        Returns:
            bool:
                True when the module is package-shaped.
        """
        self.check_cleaned()
        with self._lock:
            return self._is_package

    @property
    def executed_source(self) -> bool:
        """
        Return whether the module source has been executed at least once.

        Returns:
            bool:
                True after one successful source execution.
        """
        self.check_cleaned()
        with self._lock:
            return self._executed_source

    def update_source_text(self, source_text: str, source_sha256: str) -> None:
        """
        Replace the module source text and fingerprint.

        Purpose:
            Swap the live module's source truth before a later explicit
            execution or reload boundary.

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
            self._executed_source = False

    def update_analysis(
            self,
            export_names: Optional[Sequence[str]] = None,
            internal_dependency_names: Optional[Sequence[str]] = None,
            external_dependency_names: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Replace the derived export and dependency metadata for this module.

        Purpose:
            Refresh the analysis-side manifest fields after a crystal-analysis
            pass without rebuilding the live module object itself.

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

        Purpose:
            Record where this live module came from or where it has been
            projected back out into the filesystem.

        Args:
            physical_file_path:
                Physical module file path, if any.
            materialized_directory_path:
                Directory path where the module has been materialized, if any.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._physical_file_path = physical_file_path
            self._materialized_directory_path = materialized_directory_path

    def merge_namespace(self, namespace_values: Mapping[str, Any]) -> None:
        """
        Merge runtime namespace values into the live module namespace.

        Purpose:
            Inject additional runtime values into the live module object without
            re-running source execution.

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

    def _attach_to_parent_package(self) -> None:
        """
        Attach this module to its parent package object when available.

        Purpose:
            Keep parent package attribute exposure aligned with normal import
            semantics for dotted module names.

        Returns:
            None.
        """
        if not self._parent_name:
            return
        parent_module = sys.modules.get(self._parent_name)
        if parent_module is None:
            return
        setattr(parent_module, self.__name__.rsplit(".", 1)[-1], self)

    def _detach_from_parent_package(self) -> None:
        """
        Remove this module from its parent package object when attached.

        Purpose:
            Undo parent-package attribute publication during unpublish or
            cleanup so the synthetic world tears down cleanly.

        Returns:
            None.
        """
        if not self._parent_name:
            return
        parent_module = sys.modules.get(self._parent_name)
        if parent_module is None:
            return
        child_name = self.__name__.rsplit(".", 1)[-1]
        if hasattr(parent_module, child_name):
            try:
                if getattr(parent_module, child_name) is self:
                    delattr(parent_module, child_name)
            except AttributeError:
                pass

    def execute_source(self) -> None:
        """
        Execute the current module source into the live module namespace.

        Purpose:
            This is the core world-activation step. The module is assumed to be
            published already so circular imports can see the partially
            initialized object the same way importlib-managed modules do.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the module has already been cleaned.

        Notes:
            This method assumes the module is already published in
            `sys.modules` when circular-import-safe behavior is required.
        """
        self.check_cleaned()
        with self._lock:
            self._attach_to_parent_package()
            exec(self._source_text, self.__dict__, self.__dict__)
            self._executed_source = True

    def publish_to_sys_modules(self) -> None:
        """
        Publish this module object into `sys.modules` under its canonical name.

        Purpose:
            Make this exact live world object visible to import machinery and
            sibling modules by canonical name.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            sys.modules[self.__name__] = self
            self._published_in_sys_modules = True
            self._attach_to_parent_package()

    def unpublish_from_sys_modules(self) -> None:
        """
        Remove this module from `sys.modules` if this exact object is published.

        Purpose:
            Withdraw this live module from import visibility without destroying
            the object itself.

        Raises:
            RuntimeError:
                If the module has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            published_module = sys.modules.get(self.__name__)
            if published_module is self:
                del sys.modules[self.__name__]
            self._detach_from_parent_package()
            self._published_in_sys_modules = False

    def register_in_import_registry(
            self,
            auto_parent_package_shells: bool = True,
    ) -> None:
        """
        Register this module in the synthetic import registry.

        Purpose:
            Make the module discoverable through the class-level
            importlib-backed finder/loader path.

        Args:
            auto_parent_package_shells:
                When True, register missing parent package shells for dotted
                module names.

        Returns:
            None.

        Notes:
            Registration is what makes a module discoverable through the
            synthetic finder/loader path. It is not the same thing as
            publication or source execution.
        """
        self.check_cleaned()
        with self.__class__._registry_lock:
            if auto_parent_package_shells:
                self.__class__._ensure_registered_parent_package_shells(
                    self.__name__,
                    self._spell_crystal_id,
                )
            self.__class__._registered_modules_by_name[self.__name__] = self
            if self.__name__ not in self.__class__._load_order:
                self.__class__._load_order.append(self.__name__)

    def unregister_from_import_registry(self) -> None:
        """
        Remove this module from the synthetic import registry.

        Purpose:
            Stop importlib-driven discovery of this module without requiring an
            immediate object destruction.

        Returns:
            None.
        """
        with self.__class__._registry_lock:
            registered_module = self.__class__._registered_modules_by_name.get(
                self.__name__
            )
            if registered_module is self:
                del self.__class__._registered_modules_by_name[self.__name__]
            self.__class__._load_order = [
                module_name
                for module_name in self.__class__._load_order
                if module_name != self.__name__
            ]

    def materialize(
            self,
            auto_parent_package_shells: bool = True,
            install_import_hook: bool = False,
    ) -> "SyntheticModule":
        """
        Register, publish, and execute this module as live world state.

        Purpose:
            Provide one direct first-load path without forcing the caller to
            juggle registry, publication, and execution manually.

        Args:
            auto_parent_package_shells:
                When True, register missing parent package shells for dotted
                module names.
            install_import_hook:
                When True, ensure the synthetic finder/loader is installed so
                downstream imports can resolve through importlib.

        Returns:
            SyntheticModule:
                This live module object.

        Notes:
            This is the simplest full activation path:
            register -> optional hook install -> parent shell materialization
            -> publish -> execute -> attach importlib metadata.
        """
        self.check_cleaned()
        self.register_in_import_registry(
            auto_parent_package_shells=auto_parent_package_shells
        )
        if install_import_hook:
            self.__class__.install_import_hook()
        self.__class__._materialize_registered_parent_package_shells(self.__name__)
        self.publish_to_sys_modules()
        self.execute_source()
        self.__class__._attach_importlib_metadata(self)
        return self

    def reload_via_importlib(
            self,
            install_import_hook: bool = True,
    ) -> "SyntheticModule":
        """
        Reload this registered module through importlib.

        Purpose:
            Use the standard reload boundary once the module is already known to
            the synthetic finder/loader.

        Args:
            install_import_hook:
                When True, ensure the synthetic finder is installed before
                reload.

        Returns:
            SyntheticModule:
                The reloaded live module object.

        Notes:
            Reload is an explicit refresh boundary, not a first-load
            substitute. The module must already be registered and published
            coherently for this to be meaningful.
        """
        self.check_cleaned()
        self.register_in_import_registry(auto_parent_package_shells=True)
        if install_import_hook:
            self.__class__.install_import_hook()
        if sys.modules.get(self.__name__) is not self:
            self.publish_to_sys_modules()
        self.__class__._attach_importlib_metadata(self)
        return importlib.reload(self)

    @classmethod
    def _hash_source_text(cls, source_text: str) -> str:
        """
        Return the SHA256 fingerprint for one source string.

        Args:
            source_text:
                Source text to fingerprint.

        Returns:
            str:
                SHA256 hex digest.
        """
        return hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    @classmethod
    def create_package_shell(
            cls,
            module_name: str,
            spell_crystal_id: str,
            module_docstring: Optional[str] = None,
    ) -> "SyntheticModule":
        """
        Create one minimal synthetic package shell module.

        Args:
            module_name:
                Package module name to create.
            spell_crystal_id:
                Crystal identity used for the shell.
            module_docstring:
                Optional package docstring.

        Returns:
            SyntheticModule:
                New package-shell module object.

        Notes:
            Package shells are first-class because dotted module graphs and
            circular imports depend on them being materialized honestly.
        """
        source_text = "PACKAGE_NAME = '{0}'\n".format(module_name)
        return cls(
            module_name=module_name,
            spell_crystal_id=spell_crystal_id,
            source_text=source_text,
            source_sha256=cls._hash_source_text(source_text),
            binding_signature="package-shell::{0}".format(module_name),
            module_docstring=module_docstring,
            is_package=True,
        )

    @classmethod
    def _ensure_registered_parent_package_shells(
            cls,
            module_name: str,
            spell_crystal_id: str,
    ) -> None:
        """
        Ensure dotted parent packages exist in the registry or live world.

        Args:
            module_name:
                Fully qualified child module name.
            spell_crystal_id:
                Crystal identity used when synthesizing missing package shells.

        Returns:
            None.

        Notes:
            This only registers missing parent shells. It does not materialize
            them into `sys.modules` yet.
        """
        parent_name = module_name.rpartition(".")[0]
        if not parent_name:
            return
        cls._ensure_registered_parent_package_shells(parent_name, spell_crystal_id)
        if (
                parent_name in cls._registered_modules_by_name
                or parent_name in sys.modules
        ):
            return
        package_shell = cls.create_package_shell(
            module_name=parent_name,
            spell_crystal_id="{0}::{1}".format(spell_crystal_id, parent_name),
        )
        package_shell.register_in_import_registry(auto_parent_package_shells=False)

    @classmethod
    def _materialize_registered_parent_package_shells(
            cls,
            module_name: str,
    ) -> None:
        """
        Materialize any registered ancestor package shells for one module.

        Purpose:
            Satisfy importlib and reload expectations for dotted modules by
            ensuring ancestor package shells are actually live before child
            execution.

        Args:
            module_name:
                Child module name whose parent package chain should be made
                live before child execution.

        Returns:
            None.
        """
        parent_name = module_name.rpartition(".")[0]
        if not parent_name:
            return

        cls._materialize_registered_parent_package_shells(parent_name)
        with cls._registry_lock:
            parent_module = cls._registered_modules_by_name.get(parent_name)
        if parent_module is None:
            return
        if sys.modules.get(parent_name) is parent_module and parent_module.executed_source:
            return
        parent_module.publish_to_sys_modules()
        parent_module.execute_source()
        cls._attach_importlib_metadata(parent_module)

    @classmethod
    def _get_import_loader(cls) -> _SyntheticModuleImportLoader:
        """
        Return the singleton importlib loader for synthetic modules.

        Purpose:
            Preserve one stable loader identity for all synthetic-module specs
            and reload flows in this interpreter.

        Returns:
            _SyntheticModuleImportLoader:
                Shared loader object.
        """
        with cls._registry_lock:
            if cls._import_loader is None:
                cls._import_loader = _SyntheticModuleImportLoader()
            return cls._import_loader

    @classmethod
    def _get_meta_path_finder(cls) -> _SyntheticModuleMetaPathFinder:
        """
        Return the singleton meta-path finder for synthetic modules.

        Purpose:
            Preserve one stable finder identity for synthetic-module discovery
            in this interpreter.

        Returns:
            _SyntheticModuleMetaPathFinder:
                Shared finder object.
        """
        with cls._registry_lock:
            if cls._meta_path_finder is None:
                cls._meta_path_finder = _SyntheticModuleMetaPathFinder()
            return cls._meta_path_finder

    @classmethod
    def install_import_hook(cls) -> None:
        """
        Install the synthetic finder at the front of `sys.meta_path`.

        Purpose:
            Make registered synthetic modules discoverable through normal import
            machinery.

        Returns:
            None.
        """
        finder = cls._get_meta_path_finder()
        with cls._registry_lock:
            if finder in sys.meta_path:
                return
            sys.meta_path.insert(0, finder)

    @classmethod
    def remove_import_hook(cls) -> None:
        """
        Remove the synthetic finder from `sys.meta_path`.

        Purpose:
            Stop synthetic-module discovery through importlib without deleting
            the registered/live modules themselves.

        Returns:
            None.
        """
        with cls._registry_lock:
            finder = cls._meta_path_finder
            if finder is None:
                return
            sys.meta_path = [entry for entry in sys.meta_path if entry is not finder]

    @classmethod
    def build_registered_spec(
            cls,
            module_name: str,
    ) -> Optional[ModuleSpec]:
        """
        Build a `ModuleSpec` for one registered synthetic module.

        Args:
            module_name:
                Registered synthetic module name.

        Returns:
            Optional[ModuleSpec]:
                Importlib spec when the module is registered, otherwise None.

        Notes:
            The spec is built from the registered live module, not from a
            second detached record object.
        """
        with cls._registry_lock:
            module = cls._registered_modules_by_name.get(module_name)
        if module is None:
            return None

        spec = importlib.util.spec_from_loader(
            module_name,
            cls._get_import_loader(),
            is_package=module.is_package,
        )
        if spec is None:
            return None
        spec.origin = module.__file__
        if module.is_package:
            spec.submodule_search_locations = [module.__file__]
        return spec

    @classmethod
    def _attach_importlib_metadata(cls, module: "SyntheticModule") -> None:
        """
        Attach the current loader/spec metadata to one registered module.

        Purpose:
            Keep the live module object aligned with importlib expectations so
            `import_module(...)` and `reload(...)` can treat it like a normal
            managed module.

        Args:
            module:
                Registered synthetic module.

        Returns:
            None.
        """
        spec = cls.build_registered_spec(module.__name__)
        module.__loader__ = cls._get_import_loader()
        module.__spec__ = spec
        if module.is_package:
            module.__package__ = module.__name__
            module.__path__ = [module.__file__]
        else:
            module.__package__ = module.parent_name or ""

    @classmethod
    def create_module_for_spec(
            cls,
            spec: ModuleSpec,
    ) -> Optional["SyntheticModule"]:
        """
        Return the registered module object for one importlib spec.

        Args:
            spec:
                Importlib spec created for one registered synthetic module.

        Returns:
            Optional[SyntheticModule]:
                Registered module object, or None when absent.

        Notes:
            This returns the existing live module object rather than allocating
            a second module for the same identity.
        """
        with cls._registry_lock:
            module = cls._registered_modules_by_name.get(spec.name)
        if module is None:
            return None
        cls._attach_importlib_metadata(module)
        if sys.modules.get(spec.name) is not module:
            module.publish_to_sys_modules()
        return module

    @classmethod
    def exec_registered_module(cls, module_name: str) -> None:
        """
        Execute one registered synthetic module by name.

        Purpose:
            Bridge importlib loader execution back onto the registered world
            object that owns the source text and execution state.

        Args:
            module_name:
                Registered synthetic module name.

        Returns:
            None.

        Raises:
            ImportError:
                If the requested module is not registered.
        """
        with cls._registry_lock:
            module = cls._registered_modules_by_name.get(module_name)
        if module is None:
            raise ImportError(
                "No registered synthetic module exists for '{0}'.".format(
                    module_name,
                )
            )
        module.execute_source()

    @classmethod
    def import_registered_module(
            cls,
            module_name: str,
            install_import_hook: bool = True,
    ) -> ModuleType:
        """
        Import one registered synthetic module through importlib.

        Args:
            module_name:
                Registered synthetic module name.
            install_import_hook:
                When True, ensure the synthetic finder is installed first.

        Returns:
            ModuleType:
                Imported module object.

        Notes:
            This is the preferred importlib-style activation path once the
            module graph is already registered.
        """
        if install_import_hook:
            cls.install_import_hook()
        return importlib.import_module(module_name)

    @classmethod
    def loaded_module_names(cls) -> List[str]:
        """
        Return the registered synthetic module names in load order.

        Purpose:
            Expose one deterministic view of synthetic-module registration
            order for diagnostics, tests, and bench visibility.

        Returns:
            List[str]:
                Registered module names in the order they were first
                registered.
        """
        with cls._registry_lock:
            return list(cls._load_order)

    @classmethod
    def clear_import_registry(cls) -> None:
        """
        Clear the synthetic import registry and installed hook state.

        Purpose:
            Reset the synthetic import system for isolated tests or runtime
            teardown without keeping stale finder state around.

        Returns:
            None.
        """
        cls.remove_import_hook()
        with cls._registry_lock:
            registered_modules = list(cls._registered_modules_by_name.values())
            cls._registered_modules_by_name = {}
            cls._load_order = []
        for module in reversed(registered_modules):
            if not module.cleaned:
                module.unpublish_from_sys_modules()

    def describe(self) -> Dict[str, Any]:
        """
        Return a snapshot of the live synthetic module state.

        Purpose:
            Provide one detached, inspection-friendly snapshot of the live
            module world state, including package posture, executed state, and
            publication state, without exposing the internal mutable fields
            themselves.

        Returns:
            Dict[str, Any]:
                Dictionary snapshot of the module metadata, package posture,
                execution state, and publication state.
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
                "parent_name": self._parent_name,
                "is_package": self._is_package,
                "executed_source": self._executed_source,
            }
