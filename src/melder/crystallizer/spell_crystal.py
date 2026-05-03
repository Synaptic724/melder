import ast
import importlib.util
import inspect
import site
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell


class SpellCrystal(Cleanable):
    """
    Loader-facing module dependency manifest for one concrete spell version.

    Purpose:
        Build a narrow retained view of the module world one spell depends on
        so loaders can validate and activate that world before bind/conjure
        work continues.

    Contract:
        - constructed from one live `ISpell`
        - anchored to the spell's concrete SHA256 identity
        - resolves the root target module
        - recursively walks tracked module dependencies
        - retains flat module/path/classification targets plus direct
          dependency maps
        - does not mirror the mutable live `Spell` object
    """

    __melder_internal__ = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_id",
        "_root_module_name",
        "_root_module_path",
        "_root_module_kind",
        "_root_file_extension",
        "_root_target_name",
        "_root_target_qualname",
        "_root_target_kind",
        "_module_targets",
        "_path_targets",
        "_synthetic_module_targets",
        "_user_source_targets",
        "_site_package_targets",
        "_unknown_targets",
        "_module_to_path",
        "_module_to_kind",
        "_module_to_extension",
        "_module_to_direct_dependencies",
        "_ast_import_targets_by_module",
        "_ast_from_import_targets_by_module",
        "_walk_errors",
        "_created_from_synthetic_root",
        "_created_from_site_package_root",
        "_created_from_user_source_root",
        "_user_root_paths",
        "_site_package_root_paths",
    ]

    def __init__(
            self,
            spell: ISpell,
    ) -> None:
        """
        Initialize one spell-targeted module dependency manifest.

        Args:
            spell:
                Live spell whose module world should be captured.

        Raises:
            TypeError:
                If `spell` is None.
            ValueError:
                If the spell has no concrete SHA256 identity or no resolvable
                root module name.
        """
        super().__init__()
        if spell is None:
            raise TypeError("spell cannot be None.")

        self._lock: Optional[threading.RLock] = threading.RLock()
        self._spell_id: Optional[str] = getattr(spell, "spell_id", None)
        if not self._spell_id:
            raise ValueError("spell must expose a non-empty spell_id.")

        self._module_targets: Optional[List[str]] = []
        self._path_targets: Optional[List[str]] = []
        self._synthetic_module_targets: Optional[List[str]] = []
        self._user_source_targets: Optional[List[str]] = []
        self._site_package_targets: Optional[List[str]] = []
        self._unknown_targets: Optional[List[str]] = []
        self._module_to_path: Optional[Dict[str, str]] = {}
        self._module_to_kind: Optional[Dict[str, str]] = {}
        self._module_to_extension: Optional[Dict[str, str]] = {}
        self._module_to_direct_dependencies: Optional[Dict[str, List[str]]] = {}
        self._ast_import_targets_by_module: Optional[Dict[str, List[str]]] = {}
        self._ast_from_import_targets_by_module: Optional[Dict[str, Dict[str, List[str]]]] = {}
        self._walk_errors: Optional[List[str]] = []

        self._created_from_synthetic_root: bool = False
        self._created_from_site_package_root: bool = False
        self._created_from_user_source_root: bool = False

        self._user_root_paths: Optional[Tuple[Path, ...]] = self._resolve_user_root_paths()
        self._site_package_root_paths: Optional[Tuple[Path, ...]] = self._resolve_site_package_root_paths()

        (
            root_target,
            root_target_name,
            root_target_qualname,
            root_target_kind,
            root_module_name,
        ) = self._resolve_root_target_from_spell(spell)

        self._root_target_name: Optional[str] = root_target_name
        self._root_target_qualname: Optional[str] = root_target_qualname
        self._root_target_kind: Optional[str] = root_target_kind
        self._root_module_name: Optional[str] = root_module_name

        root_module_obj, root_module_path = self._resolve_root_module(
            root_target=root_target,
            root_module_name=root_module_name,
        )
        root_module_kind = self._classify_module_target(
            module_name=root_module_name,
            module_obj=root_module_obj,
            module_path=root_module_path,
        )

        self._root_module_path: Optional[str] = (
            str(root_module_path) if root_module_path is not None else None
        )
        self._root_module_kind: Optional[str] = root_module_kind
        self._root_file_extension: Optional[str] = self._resolve_file_extension(
            root_module_path
        )
        self._created_from_synthetic_root = root_module_kind == "synthetic_module"
        self._created_from_site_package_root = root_module_kind == "site_package"
        self._created_from_user_source_root = root_module_kind == "user_source"

        self._walk_module_dependencies(
            module_name=root_module_name,
            module_obj=root_module_obj,
            module_path=root_module_path,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the retained manifest state.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._spell_id = None
            self._root_module_name = None
            self._root_module_path = None
            self._root_module_kind = None
            self._root_file_extension = None
            self._root_target_name = None
            self._root_target_qualname = None
            self._root_target_kind = None
            self._module_targets = None
            self._path_targets = None
            self._synthetic_module_targets = None
            self._user_source_targets = None
            self._site_package_targets = None
            self._unknown_targets = None
            self._module_to_path = None
            self._module_to_kind = None
            self._module_to_extension = None
            self._module_to_direct_dependencies = None
            self._ast_import_targets_by_module = None
            self._ast_from_import_targets_by_module = None
            self._walk_errors = None
            self._created_from_synthetic_root = False
            self._created_from_site_package_root = False
            self._created_from_user_source_root = False
            self._user_root_paths = None
            self._site_package_root_paths = None
        self._lock = None

    @staticmethod
    def _resolve_user_root_paths() -> Tuple[Path, ...]:
        """
        Resolve the current user-source roots for the first manifest slice.
        """
        return (Path.cwd().resolve(),)

    @staticmethod
    def _resolve_site_package_root_paths() -> Tuple[Path, ...]:
        """
        Resolve known site-package roots for classification.
        """
        resolved_paths: List[Path] = []
        try:
            for candidate in site.getsitepackages():
                resolved_paths.append(Path(candidate).resolve())
        except Exception:
            pass
        try:
            resolved_paths.append(Path(site.getusersitepackages()).resolve())
        except Exception:
            pass
        unique_paths: List[Path] = []
        seen_paths: Set[Path] = set()
        for path in resolved_paths:
            if path in seen_paths:
                continue
            seen_paths.add(path)
            unique_paths.append(path)
        return tuple(unique_paths)

    @staticmethod
    def _resolve_target_name(target: Any) -> str:
        """
        Resolve a short target name from one bound spell object.
        """
        return getattr(target, "__name__", type(target).__name__)

    @staticmethod
    def _resolve_target_qualname(target: Any) -> str:
        """
        Resolve the qualified target name from one bound spell object.
        """
        return getattr(target, "__qualname__", SpellCrystal._resolve_target_name(target))

    @staticmethod
    def _resolve_target_kind(target: Any) -> str:
        """
        Classify the root bound target in broad runtime terms.
        """
        if inspect.isclass(target):
            return "class"
        if inspect.ismethod(target):
            return "method"
        if inspect.isfunction(target):
            return "lambda" if getattr(target, "__name__", "") == "<lambda>" else "function"
        if callable(target):
            return "callable_object"
        return "instance"

    def _resolve_root_target_from_spell(
            self,
            spell: ISpell,
    ) -> Tuple[Any, str, str, str, str]:
        """
        Resolve the root bound target and its root module identity from `ISpell`.
        """
        root_target = getattr(spell, "spell", None)
        if root_target is None:
            raise ValueError("spell must expose a live spell target.")

        root_target_name = self._resolve_target_name(root_target)
        root_target_qualname = self._resolve_target_qualname(root_target)
        root_target_kind = self._resolve_target_kind(root_target)

        root_module_name = getattr(root_target, "__module__", None)
        if not root_module_name:
            root_module = inspect.getmodule(root_target)
            if root_module is not None:
                root_module_name = getattr(root_module, "__name__", None)
        if not root_module_name:
            raise ValueError("spell target must expose a resolvable module name.")

        return (
            root_target,
            root_target_name,
            root_target_qualname,
            root_target_kind,
            root_module_name,
        )

    @staticmethod
    def _resolve_module_path(
            module_name: str,
            module_obj: Optional[Any],
    ) -> Optional[Path]:
        """
        Resolve the physical path backing one module when available.
        """
        if module_obj is not None:
            if bool(getattr(module_obj, "__melder_synthetic_module__", False)):
                physical_file_path = getattr(module_obj, "physical_file_path", None)
                if isinstance(physical_file_path, str) and physical_file_path:
                    try:
                        return Path(physical_file_path).resolve()
                    except Exception:
                        return Path(physical_file_path)
                return None
            module_file = getattr(module_obj, "__file__", None)
            if module_file:
                try:
                    path = Path(module_file)
                    return path.resolve() if path.is_absolute() or path.exists() else path
                except Exception:
                    pass
        try:
            spec = importlib.util.find_spec(module_name)
        except Exception:
            spec = None
        if spec is None:
            return None
        origin = getattr(spec, "origin", None)
        if not origin or origin in ("built-in", "frozen"):
            return None
        try:
            return Path(origin).resolve()
        except Exception:
            return None

    def _resolve_root_module(
            self,
            *,
            root_target: Any,
            root_module_name: str,
    ) -> Tuple[Optional[Any], Optional[Path]]:
        """
        Resolve the root module object and path backing the spell target.
        """
        root_module_obj = sys.modules.get(root_module_name)
        if root_module_obj is None:
            root_module_obj = inspect.getmodule(root_target)
        root_module_path = self._resolve_module_path(
            root_module_name,
            root_module_obj,
        )
        return root_module_obj, root_module_path

    @staticmethod
    def _resolve_file_extension(module_path: Optional[Path]) -> Optional[str]:
        """
        Resolve the file extension for one module path when present.
        """
        if module_path is None:
            return None
        return module_path.suffix.lower()

    @staticmethod
    def _is_synthetic_module(module_obj: Optional[Any]) -> bool:
        """
        Return whether one module object is explicitly marked synthetic.
        """
        if module_obj is None:
            return False
        return bool(getattr(module_obj, "__melder_synthetic_module__", False))

    def _classify_module_target(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> str:
        """
        Classify one module target for the loader-facing manifest.
        """
        if self._is_synthetic_module(module_obj):
            return "synthetic_module"
        if module_path is None:
            return "unknown"
        try:
            resolved_path = module_path.resolve()
        except Exception:
            resolved_path = module_path
        if any(
                resolved_path.is_relative_to(root_path)
                for root_path in self._user_root_paths
        ):
            return "user_source"
        if any(
                resolved_path.is_relative_to(root_path)
                for root_path in self._site_package_root_paths
        ):
            return "site_package"
        if "site-packages" in str(resolved_path) or "dist-packages" in str(resolved_path):
            return "site_package"
        return "unknown"

    def _resolve_module_source_text(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Optional[str]:
        """
        Resolve source text for AST analysis when the module format supports it.
        """
        if self._is_synthetic_module(module_obj):
            source_text = getattr(module_obj, "source_text", None)
            if isinstance(source_text, str):
                return source_text
            fallback_text = getattr(module_obj, "_source_text", None)
            return fallback_text if isinstance(fallback_text, str) else None

        extension = self._resolve_file_extension(module_path)
        if extension not in (".py", ".pyi"):
            return None
        if module_path is None or not module_path.exists():
            return None
        try:
            return module_path.read_text(encoding="utf-8")
        except Exception as exc:
            self._walk_errors.append(
                "Failed to read source text for module '{0}': {1}: {2}".format(
                    module_name,
                    exc.__class__.__name__,
                    exc,
                )
            )
            return None

    @staticmethod
    def _resolve_relative_import_target(
            *,
            current_package: str,
            relative_module_name: str,
    ) -> Optional[str]:
        """
        Resolve one relative import target into an absolute module name.
        """
        try:
            return importlib.util.resolve_name(relative_module_name, current_package)
        except Exception:
            return None

    def _extract_import_targets_from_ast(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Parse import targets from one module source.
        """
        source_text = self._resolve_module_source_text(
            module_name=module_name,
            module_obj=module_obj,
            module_path=module_path,
        )
        if not source_text:
            return [], {}

        try:
            syntax_tree = ast.parse(source_text)
        except SyntaxError as exc:
            self._walk_errors.append(
                "Failed to parse AST for module '{0}': SyntaxError: {1}".format(
                    module_name,
                    exc,
                )
            )
            return [], {}

        direct_import_targets: List[str] = []
        from_import_targets: Dict[str, List[str]] = {}
        current_package = getattr(module_obj, "__package__", None)
        if not current_package:
            current_package = module_name if getattr(module_obj, "__path__", None) else module_name.rpartition(".")[0]

        for node in ast.walk(syntax_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    direct_import_targets.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    relative_name = "." * node.level
                    if node.module:
                        relative_name += node.module
                    resolved_base = self._resolve_relative_import_target(
                        current_package=current_package,
                        relative_module_name=relative_name,
                    )
                else:
                    resolved_base = node.module
                if not resolved_base:
                    continue
                imported_names: List[str] = []
                for alias in node.names:
                    imported_names.append(alias.name)
                    if alias.name != "*":
                        candidate_module_name = "{0}.{1}".format(
                            resolved_base,
                            alias.name,
                        )
                        try:
                            spec = importlib.util.find_spec(candidate_module_name)
                        except Exception:
                            spec = None
                        if spec is not None:
                            direct_import_targets.append(candidate_module_name)
                from_import_targets.setdefault(resolved_base, []).extend(imported_names)
                direct_import_targets.append(resolved_base)

        deduped_import_targets: List[str] = []
        seen_targets: Set[str] = set()
        for target_name in direct_import_targets:
            if target_name in seen_targets:
                continue
            seen_targets.add(target_name)
            deduped_import_targets.append(target_name)
        return deduped_import_targets, from_import_targets

    def _record_module_target(
            self,
            *,
            module_name: str,
            module_path: Optional[Path],
            module_kind: str,
            direct_dependencies: Sequence[str],
            ast_import_targets: Sequence[str],
            ast_from_import_targets: Mapping[str, Sequence[str]],
    ) -> None:
        """
        Record one module target into the loader-facing manifest fields.
        """
        if module_name not in self._module_targets:
            self._module_targets.append(module_name)
        if module_path is not None:
            path_text = str(module_path)
            if path_text not in self._path_targets:
                self._path_targets.append(path_text)
            self._module_to_path[module_name] = path_text

        extension = self._resolve_file_extension(module_path)
        if extension:
            self._module_to_extension[module_name] = extension

        self._module_to_kind[module_name] = module_kind
        self._module_to_direct_dependencies[module_name] = list(direct_dependencies)
        self._ast_import_targets_by_module[module_name] = list(ast_import_targets)
        self._ast_from_import_targets_by_module[module_name] = {
            imported_module_name: list(imported_names)
            for imported_module_name, imported_names in ast_from_import_targets.items()
        }

        target_list_by_kind: Dict[str, List[str]] = {
            "synthetic_module": self._synthetic_module_targets,
            "user_source": self._user_source_targets,
            "site_package": self._site_package_targets,
            "unknown": self._unknown_targets,
        }
        target_list = target_list_by_kind[module_kind]
        if module_name not in target_list:
            target_list.append(module_name)

    def _walk_module_dependencies(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> None:
        """
        Walk the tracked module dependency graph rooted at one spell module.
        """
        pending: List[Tuple[str, Optional[Any], Optional[Path]]] = [
            (module_name, module_obj, module_path),
        ]
        visited_module_names: Set[str] = set()

        while pending:
            current_module_name, current_module_obj, current_module_path = pending.pop()
            if current_module_name in visited_module_names:
                continue
            visited_module_names.add(current_module_name)

            current_module_kind = self._classify_module_target(
                module_name=current_module_name,
                module_obj=current_module_obj,
                module_path=current_module_path,
            )

            ast_import_targets, ast_from_import_targets = (
                self._extract_import_targets_from_ast(
                    module_name=current_module_name,
                    module_obj=current_module_obj,
                    module_path=current_module_path,
                )
            )

            tracked_dependencies: List[str] = []
            for dependency_module_name in ast_import_targets:
                dependency_module_obj = sys.modules.get(dependency_module_name)
                dependency_module_path = self._resolve_module_path(
                    dependency_module_name,
                    dependency_module_obj,
                )
                dependency_kind = self._classify_module_target(
                    module_name=dependency_module_name,
                    module_obj=dependency_module_obj,
                    module_path=dependency_module_path,
                )
                if dependency_kind == "unknown":
                    continue
                tracked_dependencies.append(dependency_module_name)
                if dependency_module_name not in visited_module_names:
                    pending.append(
                        (
                            dependency_module_name,
                            dependency_module_obj,
                            dependency_module_path,
                        )
                    )

            self._record_module_target(
                module_name=current_module_name,
                module_path=current_module_path,
                module_kind=current_module_kind,
                direct_dependencies=tracked_dependencies,
                ast_import_targets=ast_import_targets,
                ast_from_import_targets=ast_from_import_targets,
            )

    @property
    def spell_crystal_id(self) -> str:
        """
        Return the concrete spell SHA used as the crystal identity in this slice.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_id

    @property
    def spell_id(self) -> str:
        """
        Return the concrete spell SHA for this manifest.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_id

    @property
    def root_module_name(self) -> str:
        """
        Return the root module name for the bound spell target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_name

    @property
    def root_module_path(self) -> Optional[str]:
        """
        Return the root module path when one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_path

    @property
    def root_module_kind(self) -> str:
        """
        Return the root module classification.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_kind

    @property
    def root_file_extension(self) -> Optional[str]:
        """
        Return the root module file extension when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_file_extension

    @property
    def root_target_name(self) -> str:
        """
        Return the short name of the bound root target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_target_name

    @property
    def root_target_qualname(self) -> str:
        """
        Return the qualified name of the bound root target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_target_qualname

    @property
    def root_target_kind(self) -> str:
        """
        Return the broad kind of the bound root target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_target_kind

    @property
    def module_targets(self) -> List[str]:
        """
        Return the full tracked module-name list.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._module_targets)

    @property
    def path_targets(self) -> List[str]:
        """
        Return the full tracked path-target list.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._path_targets)

    @property
    def synthetic_module_targets(self) -> List[str]:
        """
        Return the tracked synthetic module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._synthetic_module_targets)

    @property
    def user_source_targets(self) -> List[str]:
        """
        Return the tracked user-source module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._user_source_targets)

    @property
    def site_package_targets(self) -> List[str]:
        """
        Return the tracked site-package module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._site_package_targets)

    @property
    def unknown_targets(self) -> List[str]:
        """
        Return the tracked unresolved/unknown module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._unknown_targets)

    @property
    def module_to_path(self) -> Dict[str, str]:
        """
        Return a detached copy of the module-name -> path mapping.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_path)

    @property
    def module_to_kind(self) -> Dict[str, str]:
        """
        Return a detached copy of the module-name -> kind mapping.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_kind)

    @property
    def module_to_extension(self) -> Dict[str, str]:
        """
        Return a detached copy of the module-name -> file-extension mapping.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_extension)

    @property
    def module_to_direct_dependencies(self) -> Dict[str, List[str]]:
        """
        Return a detached copy of the direct dependency map.
        """
        self.check_cleaned()
        with self._lock:
            return {
                module_name: list(dependency_names)
                for module_name, dependency_names in self._module_to_direct_dependencies.items()
            }

    @property
    def walk_errors(self) -> List[str]:
        """
        Return the dependency-walk diagnostics collected so far.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._walk_errors)

    def describe(self) -> Dict[str, Any]:
        """
        Return a loader-facing snapshot of the manifest state.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "spell_id": self._spell_id,
                "spell_crystal_id": self._spell_id,
                "root_module_name": self._root_module_name,
                "root_module_path": self._root_module_path,
                "root_module_kind": self._root_module_kind,
                "root_file_extension": self._root_file_extension,
                "root_target_name": self._root_target_name,
                "root_target_qualname": self._root_target_qualname,
                "root_target_kind": self._root_target_kind,
                "module_targets": list(self._module_targets),
                "path_targets": list(self._path_targets),
                "synthetic_module_targets": list(self._synthetic_module_targets),
                "user_source_targets": list(self._user_source_targets),
                "site_package_targets": list(self._site_package_targets),
                "unknown_targets": list(self._unknown_targets),
                "module_to_path": dict(self._module_to_path),
                "module_to_kind": dict(self._module_to_kind),
                "module_to_extension": dict(self._module_to_extension),
                "module_to_direct_dependencies": {
                    module_name: list(dependency_names)
                    for module_name, dependency_names in self._module_to_direct_dependencies.items()
                },
                "walk_errors": list(self._walk_errors),
                "created_from_synthetic_root": self._created_from_synthetic_root,
                "created_from_site_package_root": self._created_from_site_package_root,
                "created_from_user_source_root": self._created_from_user_source_root,
            }
