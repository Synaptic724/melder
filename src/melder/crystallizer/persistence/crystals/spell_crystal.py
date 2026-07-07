import ast
import importlib.util
import inspect
import site
import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union

from melder.crystallizer.synthetic_module import SyntheticModule

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class SpellCrystal(Cleanable):
    """
    Loader-facing module dependency manifest for one concrete spell version.

    Purpose:
        Build a narrow retained view of the module world one spell depends on
        so loaders can validate and activate that world before bind/conjure
        work continues.

    Contract:
        - constructed from one live `Spell`
        - anchored to the spell's concrete SHA256 identity
        - resolves the root target module
        - recursively walks tracked module dependencies
        - retains flat module/path/classification targets plus direct
          dependency maps
        - does not mirror the mutable live `Spell` object
        - Runtime identities (ULIDs) are RECORD-LOCAL: they express edges
          and log correlation within the recorded session only. Restore
          translates them to fresh identities (never reuses them), and
          seal fingerprinting normalizes them out so identical worlds
          compare identical across boots.

    Why this exists:
        The crystal is the durable loader-facing truth for one spell's module
        world. It is the object that answers:
        - what module world does this spell depend on?
        - which targets are synthetic, user-owned, site-package-backed, or
          still unresolved?
        - what exact direct-dependency edges should the loader validate before
          activation?

    Non-goals:
        - it is not a live `Spell` replay object
        - it is not the mutation engine
        - it is not a package manager
        - it does not prove runtime reachability beyond source/import truth
    """

    __melder_internal__ = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "_root_module_name",
        "_root_module_path",
        "_root_module_kind",
        "_root_file_extension",
        "_root_target_name",
        "_root_target_qualname",
        "_root_target_kind",
        "_spellbook_id",
        "_spell_name",
        "_binding_name",
        "_spellframe_name",
        "_existence_name",
        "_permissions_name",
        "_disposal_method_names",
        "_profile_family",
        "_rebindability",
        "_module_targets",
        "_path_targets",
        "_synthetic_module_targets",
        "_synthetic_module_sources",
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
            spell: Spell,
            user_source_root_paths: Optional[Sequence[Union[str, Path]]] = None,
            spellbook_id: Optional[str] = None,
    ) -> None:
        """
        Initialize one spell-targeted module dependency manifest.

        Purpose:
            Snapshot the module world that one concrete spell version depends
            on so a loader can later validate that world before a rebuild or
            activation step.

        Contract:
            - Accepts exactly one live `Spell`.
            - Uses the spell's concrete `spell_id` as the current manifest id.
            - Resolves the root bound target and its root module.
            - Classifies the root module into user-source, site-package,
              synthetic, or unknown.
            - Walks tracked imports and records the flat manifest fields the
              current loader slice needs.
            - Does not retain the live `Spell` or the live root target
              reference after construction.
            - Captures the root module classification and all direct-dependency
              edges needed for later loader validation and world activation.

        Args:
            spell:
                Live spell whose concrete bound target should be used as the
                root of the module dependency walk. The constructor consumes
                only the stable spell-facing identity and target/module
                semantics it needs for the manifest.
            user_source_root_paths:
                Optional explicit source roots used to classify user-controlled
                modules. These roots are the policy input for
                `user_source` classification. When omitted, the first-slice
                fallback is the current working directory.
            spellbook_id:
                Optional owning-spellbook identity supplied by the bind
                seam. It is the crystal's parent edge inside a
                PersistenceProfile; None when the crystal is built
                outside a bind context.

        Returns:
            None.

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

        self._lock: threading.RLock = threading.RLock()
        if spell.spell_id is None:
            raise ValueError("spell must expose a non-empty spell_id.")
        self._id: str = spell.spell_id
        self._module_targets: List[str] = []
        self._path_targets: List[str] = []
        self._synthetic_module_targets: List[str] = []
        # Loader chain M3: synthetic modules have no files, so their
        # rebuildable truth (source + identity metadata) rides the crystal.
        self._synthetic_module_sources: Dict[str, Dict[str, object]] = {}
        self._user_source_targets: List[str] = []
        self._site_package_targets: List[str] = []
        self._unknown_targets: List[str] = []
        self._module_to_path: Dict[str, str] = {}
        self._module_to_kind: Dict[str, str] = {}
        self._module_to_extension: Dict[str, str] = {}
        self._module_to_direct_dependencies: Dict[str, List[str]] = {}
        self._ast_import_targets_by_module: Dict[str, List[str]] = {}
        self._ast_from_import_targets_by_module: Dict[str, Dict[str, List[str]]] = {}
        self._walk_errors: List[str] = []

        self._created_from_synthetic_root: bool = False
        self._created_from_site_package_root: bool = False
        self._created_from_user_source_root: bool = False

        self._user_root_paths: Tuple[Path, ...] = (
            self._resolve_user_root_paths(user_source_root_paths)
        )
        self._site_package_root_paths: Tuple[Path, ...] = self._resolve_site_package_root_paths()

        (
            root_target,
            root_target_name,
            root_target_qualname,
            root_target_kind,
            root_module_name,
        ) = self._resolve_root_target_from_spell(spell)

        self._root_target_name: str = root_target_name
        self._root_target_qualname: str = root_target_qualname
        self._root_target_kind: str = root_target_kind
        self._root_module_name: str = root_module_name

        # Bind-signature capture: the replayable facts bind consumed for
        # this spell version, retained so a profile can rebind from the
        # crystal alone (or truthfully report replay_required).
        self._spellbook_id: Optional[str] = spellbook_id
        self._spell_name: Optional[str] = spell.spell_name
        self._binding_name: Optional[str] = spell.binding_name
        spellframe = spell.spellframe
        self._spellframe_name: Optional[str] = (
            getattr(spellframe, "__name__", str(spellframe))
            if spellframe is not None
            else None
        )
        self._existence_name: str = spell.existence.name
        self._permissions_name: str = spell.permissions.name
        # Capture-gap fields (restore_engine_2026_07_07 patch lane): the two
        # bind inputs the record previously dropped. Disposal names preserve
        # the spell's cleanup contract across a restore; the profile family
        # preserves examination depth (bind's `profile` argument). The family
        # is derived from the attached profile object's TYPE NAME so this
        # module never imports examiner types (typing-only pressure stays
        # zero and the crystal remains pure data).
        self._disposal_method_names: List[str] = sorted(
            spell.disposal_method_names
        )
        self._profile_family: str = (
            "detailed"
            if type(spell.profile).__name__ == "SpellDetailedProfile"
            else "general"
        )
        # class/function targets re-import (or rematerialize) cleanly;
        # method/lambda/callable-object/instance targets need live code
        # participation at restore time.
        self._rebindability: str = (
            "hydratable"
            if root_target_kind in ("class", "function")
            else "replay_required"
        )

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

        Contract:
            - Idempotent.
            - Clears all retained manifest fields and diagnostics.
            - Drops classification flags and resolved root-path caches.
            - Leaves the object unusable after cleanup completes.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            self._created_from_synthetic_root = False
            self._created_from_site_package_root = False
            self._created_from_user_source_root = False
            del self._id
            del self._root_module_name
            del self._root_module_path
            del self._root_module_kind
            del self._root_file_extension
            del self._root_target_name
            del self._root_target_qualname
            del self._root_target_kind
            del self._spellbook_id
            del self._spell_name
            del self._binding_name
            del self._spellframe_name
            del self._existence_name
            del self._permissions_name
            del self._disposal_method_names
            del self._profile_family
            del self._rebindability
            del self._module_targets
            del self._path_targets
            del self._synthetic_module_targets
            del self._synthetic_module_sources
            del self._user_source_targets
            del self._site_package_targets
            del self._unknown_targets
            del self._module_to_path
            del self._module_to_kind
            del self._module_to_extension
            del self._module_to_direct_dependencies
            del self._ast_import_targets_by_module
            del self._ast_from_import_targets_by_module
            del self._walk_errors
            del self._user_root_paths
            del self._site_package_root_paths
        del self._lock


    @property
    def id(self) -> str:
        """
        Return the concrete spell version identity the manifest was built from.

        Purpose:
            Expose the live spell SHA that anchored crystal construction
            without forcing callers to inspect `describe()`.

        Returns:
            str:
                Concrete SHA256 identity of the spell that
                produced this manifest.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def root_module_name(self) -> str:
        """
        Return the canonical root module name for the bound target.

        Purpose:
            Tell loaders and diagnostics which module the bound spell target
            was rooted in before dependency walking expanded the manifest.

        Returns:
            str:
                Canonical dotted module name for the root spell target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_name

    @property
    def root_module_path(self) -> Optional[str]:
        """
        Return the resolved physical path for the root module when one exists.

        Purpose:
            Expose the root module's backing file location for file-backed or
            site-package-backed targets.

        Returns:
            Optional[str]:
                Physical root-module path when the root has one, otherwise
                `None` for pathless or purely synthetic roots.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_path

    @property
    def root_module_kind(self) -> str | None:
        """
        Return the classified authority kind for the root module.

        Purpose:
            Expose whether the root target lives in synthetic, user-source,
            site-package, or unknown authority space.

        Returns:
            str:
                Root module classification such as `synthetic_module`,
                `user_source`, `site_package`, or `unknown`.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_kind

    @property
    def root_file_extension(self) -> Optional[str]:
        """
        Return the root module file extension when the root is path-backed.

        Purpose:
            Expose the file-format hint the manifest resolved for the root
            module.

        Returns:
            Optional[str]:
                Lowercased root module suffix such as `.py` or `.pyi`, or
                `None` when the root has no physical path.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_file_extension

    @property
    def root_target_name(self) -> str:
        """
        Return the short bound-target name at the root of the manifest.

        Purpose:
            Expose the human-readable target name resolved from the spell
            object before module walking began.

        Returns:
            str:
                Short class/function/method/object name for the root target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_target_name

    @property
    def root_target_qualname(self) -> str:
        """
        Return the qualified root-target name resolved from the spell object.

        Purpose:
            Preserve the fully qualified target identity needed for later
            diagnostics or loader-facing reporting.

        Returns:
            str:
                Qualified root-target name such as a class or method
                `__qualname__`.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_target_qualname

    @property
    def root_target_kind(self) -> str:
        """
        Return the broad runtime kind of the root target.

        Purpose:
            Tell callers whether the root target was resolved as a class,
            function, method, lambda, callable object, or instance.

        Returns:
            str:
                Broad target-kind label for the root spell target.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_target_kind

    @property
    def spellbook_id(self) -> Optional[str]:
        """
        Return the owning-spellbook identity supplied at construction.

        Returns:
            Optional[str]:
                Parent spellbook id, or None outside a bind context.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellbook_id

    @property
    def spell_name(self) -> Optional[str]:
        """
        Return the logical spell name recorded at bind.

        Returns:
            Optional[str]:
                Recorded spell name, or None when unnamed.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_name

    @property
    def binding_name(self) -> Optional[str]:
        """
        Return the binding name recorded at bind.

        Returns:
            Optional[str]:
                Recorded binding name, or None for the default binding.
        """
        self.check_cleaned()
        with self._lock:
            return self._binding_name

    @property
    def spellframe_name(self) -> Optional[str]:
        """
        Return the spellframe name recorded at bind.

        Returns:
            Optional[str]:
                Frame-type name (class __name__ or string form), or
                None when the spell was bound unframed.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellframe_name

    @property
    def existence_name(self) -> str:
        """
        Return the Existence enum name recorded at bind.

        Returns:
            str:
                Lifetime posture name consumed by bind replay.
        """
        self.check_cleaned()
        with self._lock:
            return self._existence_name

    @property
    def permissions_name(self) -> str:
        """
        Return the Permissions enum name recorded at bind.

        Returns:
            str:
                Borrow posture name consumed by bind replay.
        """
        self.check_cleaned()
        with self._lock:
            return self._permissions_name

    @property
    def disposal_method_names(self) -> List[str]:
        """
        Return the disposal method names recorded at bind.

        Purpose:
            Preserve the spell's cleanup contract across a restore: the
            engine passes these straight back into bind's
            `disposal_method_names` so restored creations dispose exactly
            like the originals.

        Returns:
            List[str]:
                Detached, sorted disposal method-name list (empty when the
                spell declared none).
        """
        self.check_cleaned()
        with self._lock:
            return list(self._disposal_method_names)

    @property
    def profile_family(self) -> str:
        """
        Return the examination-profile family recorded at bind.

        Returns:
            str:
                "detailed" when the spell carried a SpellDetailedProfile at
                emission, else "general" (bind replay passes this to the
                `profile` argument).
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_family

    @property
    def rebindability(self) -> str:
        """
        Return the restore-honesty class derived at construction.

        Returns:
            str:
                "hydratable" (class/function targets) or
                "replay_required" (method/lambda/object targets).
        """
        self.check_cleaned()
        with self._lock:
            return self._rebindability

    @property
    def module_targets(self) -> List[str]:
        """
        Return the full tracked module-name list.

        Purpose:
            Expose the flat ordered module inventory retained by the current
            manifest.

        Returns:
            List[str]:
                Detached list of all tracked module names, including the root
                module and any discovered dependencies.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._module_targets)

    @property
    def path_targets(self) -> List[str]:
        """
        Return the tracked physical path inventory for the manifest.

        Purpose:
            Expose every physical module path the current dependency walk was
            able to resolve.

        Returns:
            List[str]:
                Detached list of resolved path targets for file-backed
                modules.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._path_targets)

    @property
    def synthetic_module_targets(self) -> List[str]:
        """
        Return the tracked synthetic-module names.

        Purpose:
            Expose the subset of `module_targets` currently classified as
            synthetic world material.

        Returns:
            List[str]:
                Detached list of module names classified as
                `synthetic_module`.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._synthetic_module_targets)

    @property
    def user_source_targets(self) -> List[str]:
        """
        Return the tracked user-source module names.

        Purpose:
            Expose the subset of `module_targets` that fell under the
            configured user-source roots.

        Returns:
            List[str]:
                Detached list of module names classified as `user_source`.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._user_source_targets)

    @property
    def site_package_targets(self) -> List[str]:
        """
        Return the tracked site-package module names.

        Purpose:
            Expose the subset of `module_targets` classified as external
            environment/package modules.

        Returns:
            List[str]:
                Detached list of module names classified as `site_package`.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._site_package_targets)

    @property
    def unknown_targets(self) -> List[str]:
        """
        Return the tracked unresolved or unknown module names.

        Purpose:
            Expose the imports and module targets the manifest could name but
            could not classify into a stronger authority bucket.

        Returns:
            List[str]:
                Detached list of unknown target names, including unresolved
                AST-discovered dependencies.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._unknown_targets)

    @property
    def user_source_root_paths(self) -> List[str]:
        """
        Return the normalized user-source roots used for classification.

        Purpose:
            Expose the exact configured roots that drove `user_source`
            classification for this manifest.

        Returns:
            List[str]:
                Detached list of normalized user-source root paths.
        """
        self.check_cleaned()
        with self._lock:
            return [str(root_path) for root_path in self._user_root_paths]

    @property
    def site_package_root_paths(self) -> List[str]:
        """
        Return the normalized site-package roots used for classification.

        Purpose:
            Expose the resolved site-package roots used when classifying
            environment-backed modules.

        Returns:
            List[str]:
                Detached list of normalized site-package root paths.
        """
        self.check_cleaned()
        with self._lock:
            return [str(root_path) for root_path in self._site_package_root_paths]

    @property
    def module_to_path(self) -> Dict[str, str]:
        """
        Return a detached copy of the module-name -> path mapping.

        Purpose:
            Expose the resolved physical path for each path-backed tracked
            module.

        Returns:
            Dict[str, str]:
                Detached mapping from module name to resolved physical path.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_path)

    @property
    def module_to_kind(self) -> Dict[str, str]:
        """
        Return a detached copy of the module-name -> kind mapping.

        Purpose:
            Expose the authority classification assigned to every tracked
            module.

        Returns:
            Dict[str, str]:
                Detached mapping from module name to classification kind.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_kind)

    @property
    def module_to_extension(self) -> Dict[str, str]:
        """
        Return a detached copy of the module-name -> file-extension mapping.

        Purpose:
            Expose the resolved file suffix for each path-backed tracked
            module.

        Returns:
            Dict[str, str]:
                Detached mapping from module name to file extension.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_extension)

    @property
    def module_to_direct_dependencies(self) -> Dict[str, List[str]]:
        """
        Return a detached copy of the direct dependency map.

        Purpose:
            Expose the direct source-level dependency edges retained for each
            tracked module.

        Returns:
            Dict[str, List[str]]:
                Detached mapping from module name to its flat direct dependency
                module-name list.
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

        Purpose:
            Expose non-fatal source-read, parse, or walk issues captured while
            building the manifest.

        Returns:
            List[str]:
                Detached list of dependency-walk diagnostic strings.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._walk_errors)


    @staticmethod
    def _resolve_user_root_paths(
            user_source_root_paths: Optional[Sequence[Union[str, Path]]],
    ) -> Tuple[Path, ...]:
        """
        Resolve the configured user-source roots for the current manifest.

        Purpose:
            Normalize the source-root inputs used for classifying user-owned
            physical modules into one stable tuple used throughout the
            dependency walk.

        Contract:
            - accepts only `str` or `Path` values
            - resolves every value to an absolute path
            - deduplicates roots while preserving first-seen order
            - falls back to the current working directory when no explicit
              roots are supplied

        Args:
            user_source_root_paths:
                Optional explicit source-root sequence. Each element must be a
                string path or `Path`.

        Returns:
            Tuple[Path, ...]:
                Normalized, deduplicated root paths.

        Raises:
            TypeError:
                If any configured root is not a string path or `Path`.
        """
        if not user_source_root_paths:
            return (Path.cwd().resolve(),)

        normalized_paths: List[Path] = []
        seen_paths: Set[Path] = set()
        for candidate in user_source_root_paths:
            if not isinstance(candidate, (str, Path)):
                raise TypeError(
                    "user_source_root_paths entries must be str or Path values."
                )
            root_path = Path(candidate).resolve()
            if root_path in seen_paths:
                continue
            seen_paths.add(root_path)
            normalized_paths.append(root_path)
        return tuple(normalized_paths)

    @staticmethod
    def _resolve_site_package_root_paths() -> Tuple[Path, ...]:
        """
        Resolve known site-package roots for classification.

        Purpose:
            Build the physical roots that should count as `site_package`
            authority during module classification.

        Contract:
            - best-effort only; site/user-site lookup failures do not abort
              crystal construction
            - deduplicates resolved roots while preserving first-seen order

        Returns:
            Tuple[Path, ...]:
                Normalized site-package root paths used for module-kind
                classification.
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
    def _resolve_target_identity(target: Any) -> Tuple[str, str, str, str]:
        """
        Resolve stable target identity data from one bound spell object.

        Purpose:
            Reduce one live spell target to the minimal stable identity the
            crystal needs before module walking begins.

        Contract:
            - classes, methods, functions, and lambdas keep their natural
              module identity
            - callable and non-callable instances fall back to their concrete
              runtime type
            - the returned tuple is intentionally small and stable enough to
              survive past the live target object itself

        Returns:
            Tuple[str, str, str, str]:
                `(name, qualname, kind, module_name)` for the bound target.
        """
        if inspect.isclass(target):
            return (
                target.__name__,
                target.__qualname__,
                "class",
                target.__module__,
            )
        if inspect.ismethod(target):
            return (
                target.__name__,
                target.__qualname__,
                "method",
                target.__module__,
            )
        if inspect.isfunction(target):
            target_kind = "lambda" if target.__name__ == "<lambda>" else "function"
            return (
                target.__name__,
                target.__qualname__,
                target_kind,
                target.__module__,
            )

        target_type = type(target)
        target_kind = "callable_object" if callable(target) else "instance"
        return (
            target_type.__name__,
            target_type.__qualname__,
            target_kind,
            target_type.__module__,
        )

    def _resolve_root_target_from_spell(
            self,
            spell: Spell,
    ) -> Tuple[Any, str, str, str, str]:
        """
        Resolve the root bound target and its root module identity from `Spell`.

        Purpose:
            Convert one live spell into the smallest target-identity tuple the
            manifest needs before any module walking happens.

        Returns:
            Tuple[Any, str, str, str, str]:
                `(root_target, target_name, target_qualname, target_kind,
                root_module_name)`.

        Raises:
            ValueError:
                If the spell exposes no live target or no resolvable module
                name for that target.

        Notes:
            The live target reference is used only long enough to resolve the
            stable root identity and the initial root module object/path.
        """
        root_target = spell.spell
        if root_target is None:
            raise ValueError("spell must expose a live spell target.")

        (
            root_target_name,
            root_target_qualname,
            root_target_kind,
            root_module_name,
        ) = self._resolve_target_identity(root_target)

        if not root_module_name:
            root_module = inspect.getmodule(root_target)
            if root_module is not None:
                root_module_name = root_module.__name__
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

        Contract:
            - Synthetic modules use their crystallizer-managed physical path
              when one exists.
            - Non-synthetic modules prefer `__file__` on the live module
              object.
            - Falls back to `importlib.util.find_spec(...)` when a live module
              object is missing or incomplete.
            - Returns None for built-in/frozen modules and for modules without
              a usable physical origin.

        Args:
            module_name:
                Canonical module name to resolve.
            module_obj:
                Live module object when one is already available.

        Returns:
            Optional[Path]:
                Best-effort resolved physical path, or None when the module is
                synthetic, built-in, frozen, or otherwise pathless.
        """
        if module_obj is not None:
            if isinstance(module_obj, SyntheticModule):
                physical_file_path = module_obj.physical_file_path
                if isinstance(physical_file_path, str) and physical_file_path:
                    try:
                        return Path(physical_file_path).resolve()
                    except Exception:
                        return Path(physical_file_path)
                return None
            try:
                module_file = module_obj.__file__
            except AttributeError:
                module_file = None
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
        try:
            origin = spec.origin
        except AttributeError:
            origin = None
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

        Purpose:
            Find the live module object and the best available path for the
            spell's root target before classification and dependency walking.

        Args:
            root_target:
                Live target object currently bound by the spell.
            root_module_name:
                Canonical module name resolved from the target identity.

        Returns:
            Tuple[Optional[Any], Optional[Path]]:
                `(root_module_obj, root_module_path)` where either side may be
                None when only partial information is available.
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

        Args:
            module_path:
                Physical module path, if one exists.

        Returns:
            Optional[str]:
                Lowercased suffix for the path, or None when the module is
                pathless.
        """
        if module_path is None:
            return None
        return module_path.suffix.lower()

    @staticmethod
    def _is_synthetic_module(module_obj: Optional[Any]) -> bool:
        """
        Return whether one module object is explicitly marked synthetic.

        Args:
            module_obj:
                Live module object to check.

        Returns:
            bool:
                True when the object satisfies the shared synthetic-module
                protocol.
        """
        if module_obj is None:
            return False
        return isinstance(module_obj, SyntheticModule)

    def _classify_module_target(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> str:
        """
        Classify one module target for the loader-facing manifest.

        Purpose:
            Decide which authority bucket a module belongs to so loaders can
            treat synthetic, user-source, site-package, and unresolved targets
            differently.

        Contract:
            - synthetic modules win first because their authority is explicit
            - user-source and site-package classifications are path-driven
            - modules without usable source/path truth remain `unknown`

        Args:
            module_name:
                Canonical module name being classified.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            str:
                One of:
                - `synthetic_module`
                - `user_source`
                - `site_package`
                - `unknown`

        Notes:
            `user_source` classification is policy-driven by the configured
            root paths, not by import location alone.
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

        Contract:
            - Synthetic modules provide source through the protocol surface.
            - Physical modules are only read when their backing file extension
              is source-like (`.py` / `.pyi`).
            - Read failures are recorded into `walk_errors` instead of raising
              immediately.

        Args:
            module_name:
                Canonical module name whose source is being requested.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            Optional[str]:
                Source text used for AST import analysis, or None when the
                module format does not expose source safely.
        """
        if isinstance(module_obj, SyntheticModule):
            source_text = module_obj.source_text
            return source_text if isinstance(source_text, str) else None

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

        Args:
            current_package:
                Package context of the module being parsed.
            relative_module_name:
                Relative import string such as `.helper` or `..pkg.mod`.

        Returns:
            Optional[str]:
                Absolute module name, or None when the relative path cannot be
                resolved safely.
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

        Purpose:
            Build the direct source-level import view used by the loader
            manifest, including both flat dependency candidates and the richer
            `from ... import ...` shape retained for diagnostics.

        Contract:
            - works from source text only
            - deduplicates flat dependency targets
            - records `from ... import ...` imports even when the imported
              member is not itself a resolvable submodule
            - records AST/parse failures into `walk_errors` instead of raising

        Args:
            module_name:
                Canonical module name being parsed.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            Tuple[List[str], Dict[str, List[str]]]:
                - flat direct/candidate dependency module names
                - `from ... import ...` mapping for diagnostics and later
                  inspection

        Notes:
            This is intentionally a source-level import walk. It is not a full
            object graph or runtime reachability analysis.
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
        try:
            current_package = module_obj.__package__
        except AttributeError:
            current_package = None
        if not current_package:
            try:
                module_path_entries = module_obj.__path__
            except AttributeError:
                module_path_entries = None
            current_package = (
                module_name
                if module_path_entries
                else module_name.rpartition(".")[0]
            )

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

        Contract:
            - Appends deduplicated module/path targets.
            - Updates kind/extension/dependency lookup maps.
            - Mirrors the module into the kind-specific flat list used by the
              loader-facing manifest surface.

        Args:
            module_name:
                Module being recorded.
            module_path:
                Physical backing path, if one exists.
            module_kind:
                Classified authority bucket for the module.
            direct_dependencies:
                Flat direct dependency module names for the module.
            ast_import_targets:
                AST-derived flat import targets recorded for diagnostics.
            ast_from_import_targets:
                AST-derived `from ... import ...` map recorded for diagnostics.

        Returns:
            None.
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

        Purpose:
            Produce the actual loader-facing module graph for the crystal by
            following source-level imports and classifying every reachable
            module target.

        Contract:
            - Uses module names as the cycle-protection identity.
            - Reads dependencies from source imports, not from runtime object
              traversal.
            - Records the dependency classes the current manifest cares about.
            - Unknown imports are still recorded explicitly so the manifest
              does not silently imply a more complete dependency picture than
              the source actually provides.

        Args:
            module_name:
                Root module name for the current walk step.
            module_obj:
                Live module object for the current walk step, if available.
            module_path:
                Physical module path for the current walk step, if available.

        Returns:
            None.
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
                    tracked_dependencies.append(dependency_module_name)
                    self._record_module_target(
                        module_name=dependency_module_name,
                        module_path=dependency_module_path,
                        module_kind=dependency_kind,
                        direct_dependencies=[],
                        ast_import_targets=[],
                        ast_from_import_targets={},
                    )
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

            self._harvest_synthetic_source(
                current_module_name, current_module_obj
            )
            self._record_module_target(
                module_name=current_module_name,
                module_path=current_module_path,
                module_kind=current_module_kind,
                direct_dependencies=tracked_dependencies,
                ast_import_targets=ast_import_targets,
                ast_from_import_targets=ast_from_import_targets,
            )

    def _harvest_synthetic_source(
            self,
            module_name: str,
            module_obj: Optional[Any],
    ) -> None:
        """
        Capture one synthetic module's rebuildable truth (loader chain M3).

        Purpose:
            Synthetic modules have no files - their source IS the record.
            Without this harvest a fresh process can never re-import a
            synthetic-rooted spell; with it the restore engine rebuilds
            the module world (construct -> register -> publish -> execute)
            before hydrating the bind target.

        Contract:
            - NO-OP for non-synthetic modules.
            - Captures everything SyntheticModule's constructor needs:
              source_text, source_sha256, binding_signature,
              spell_crystal_id, parent_name, is_package.
            - Plain values only; detached copies.

        Args:
            module_name:
                Canonical module name being walked.
            module_obj:
                Live module object when available.

        Returns:
            None.
        """
        if not isinstance(module_obj, SyntheticModule):
            return
        self._synthetic_module_sources[module_name] = {
            "source_text": module_obj.source_text,
            "source_sha256": module_obj.source_sha256,
            "binding_signature": module_obj.binding_signature,
            "spell_crystal_id": module_obj.spell_crystal_id,
            "parent_name": module_obj.parent_name,
            "is_package": module_obj.is_package,
        }

    def describe(self) -> Dict[str, Any]:
        """
        Return a loader-facing snapshot of the manifest state.

        Purpose:
            Provide one detached, serialization-friendly view of the current
            crystal manifest so tests, diagnostics, and later persistence work
            can inspect the manifest without mutating the live object.

        Returns:
            Dict[str, Any]:
                Detached manifest snapshot suitable for debugging, inspection,
                or future persistence/loader handoff work.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "id": self._id,
                "root_module_name": self._root_module_name,
                "root_module_path": self._root_module_path,
                "root_module_kind": self._root_module_kind,
                "root_file_extension": self._root_file_extension,
                "root_target_name": self._root_target_name,
                "root_target_qualname": self._root_target_qualname,
                "root_target_kind": self._root_target_kind,
                "spellbook_id": self._spellbook_id,
                "spell_name": self._spell_name,
                "binding_name": self._binding_name,
                "spellframe_name": self._spellframe_name,
                "existence_name": self._existence_name,
                "permissions_name": self._permissions_name,
                "disposal_method_names": list(self._disposal_method_names),
                "profile_family": self._profile_family,
                "rebindability": self._rebindability,
                "module_targets": list(self._module_targets),
                "path_targets": list(self._path_targets),
                "synthetic_module_targets": list(self._synthetic_module_targets),
                "synthetic_module_sources": {
                    name: dict(payload)
                    for name, payload in self._synthetic_module_sources.items()
                },
                "user_source_targets": list(self._user_source_targets),
                "site_package_targets": list(self._site_package_targets),
                "unknown_targets": list(self._unknown_targets),
                "user_source_root_paths": [
                    str(root_path) for root_path in self._user_root_paths
                ],
                "site_package_root_paths": [
                    str(root_path) for root_path in self._site_package_root_paths
                ],
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


