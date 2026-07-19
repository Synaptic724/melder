"""
Value-only carrier for one crystal analysis pass.

This module holds `CrystalAnalysisResult`, the detached payload produced by
`CrystalAnalyzer` and CARRIED by crystals (SpellCrystal stores exactly one).
Per the V3 philosophy carrier law, crystals never own analyzers, strategy
maps, or walk logic - they own one of these results.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1
(crystal-analysis-extraction). Field set mirrors the manifest surface that
previously lived as twelve slots on SpellCrystal, plus the S1 additions:
physical module fingerprints, export surfaces, and topological load order.
"""

import threading
from typing import Any, Dict, List, Mapping, Optional, Sequence, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class CrystalAnalysisResult(Cleanable):
    """
    Detached, serialization-friendly result of one module-world analysis.

    Purpose:
        Hold every analysis-derived fact about one spell's module world so
        crystals can carry analysis OUTPUT without owning analysis MACHINERY,
        and so MutationResearch can consume the same payload shape when
        re-analyzing retained historical versions.

    Contract:
        - Value-only: every retained field is a plain str/list/dict/bool
          structure; no live module objects, spells, or strategies are held.
        - Write phase then read phase: `CrystalAnalyzer` fills the result via
          the `record_*`/`set_*` verbs during one analysis pass; after the
          analyzer returns, holders treat the result as effectively frozen
          (no freeze bit is enforced in this first cut - the analyzer is the
          only intended writer and it never retains the result).
        - All read surfaces return DETACHED copies under the instance lock.
        - `describe()` is the persistence-facing payload and is a strict
          superset of the pre-decomposition SpellCrystal manifest keys for
          the fields this object owns.

    Threading:
        One instance `RLock` guards every mutation and detached read.

    Lifecycle / Cleanup:
        Owned by exactly one crystal (or one transient analyzer caller).
        `cleanup()` is idempotent, deletes owned field surfaces (del
        posture), and deletes the lock last.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = (
        "_lock",
        "_root_module_kind",
        "_module_targets",
        "_path_targets",
        "_synthetic_module_targets",
        "_synthetic_module_sources",
        "_user_module_sources",
        "_distribution_provenance",
        "_user_source_targets",
        "_site_package_targets",
        "_unknown_targets",
        "_module_to_path",
        "_module_to_kind",
        "_module_to_extension",
        "_module_to_direct_dependencies",
        "_ast_import_targets_by_module",
        "_ast_from_import_targets_by_module",
        "_physical_module_fingerprints",
        "_export_surfaces",
        "_module_load_order",
        "_walk_errors",
    )

    def __init__(self) -> None:
        """
        Initialize one empty analysis result awaiting analyzer writes.

        Contract:
            - Every field is initialized deterministically and empty.
            - `root_module_kind` starts None and is populated by the analyzer's
              root-classification step.
            - Construction does not retain a spell, module, AST, analyzer, or
              strategy; all later writes accept value-shaped inputs.

        Returns:
            None.

        Lifecycle / Cleanup:
            The analyzer creates one result per analysis and transfers it to
            the caller without retaining a back-reference.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        # Root classification is analysis truth (the owning crystal keeps
        # root IDENTITY - names, paths, target kinds - itself).
        self._root_module_kind: Optional[str] = None
        # Flat manifest views (order preserved, deduplicated on record).
        self._module_targets: List[str] = []
        self._path_targets: List[str] = []
        self._synthetic_module_targets: List[str] = []
        self._user_source_targets: List[str] = []
        self._site_package_targets: List[str] = []
        self._unknown_targets: List[str] = []
        # Loader chain M3 custody: synthetic modules have no files, so their
        # rebuildable truth (source + identity metadata) rides the result.
        self._synthetic_module_sources: Dict[str, Dict[str, object]] = {}
        # S2 physical custody (opt-in): retained user-module source
        # payloads; empty when retention is off or no user modules walked.
        self._user_module_sources: Dict[str, Dict[str, object]] = {}
        # Always-on distribution provenance for site-package modules
        # (finishing slice 1): module -> {distribution_name, ...}.
        self._distribution_provenance: Dict[str, Dict[str, object]] = {}
        # Per-module lookup maps.
        self._module_to_path: Dict[str, str] = {}
        self._module_to_kind: Dict[str, str] = {}
        self._module_to_extension: Dict[str, str] = {}
        self._module_to_direct_dependencies: Dict[str, List[str]] = {}
        self._ast_import_targets_by_module: Dict[str, List[str]] = {}
        self._ast_from_import_targets_by_module: Dict[str, Dict[str, List[str]]] = {}
        # S1 additions: drift-detectable physical custody, export surfaces
        # for MR's impact engine, and the explicit unfold ordering the
        # restore engine previously approximated with heuristics.
        self._physical_module_fingerprints: Dict[str, str] = {}
        self._export_surfaces: Dict[str, Dict[str, List[str]]] = {}
        self._module_load_order: List[str] = []
        # Honesty channel: read/parse/walk failures are reported, never
        # raised mid-walk.
        self._walk_errors: List[str] = []

    def cleanup(self) -> None:
        """
        Idempotently release every retained analysis field.

        Contract:
            - Idempotent; safe to call multiple times.
            - Deletes owned field surfaces (del posture); the lock is
              deleted last.
            - The object is unusable after cleanup completes.

        Returns:
            None.

        Threading:
            Serialized by the instance lock. Callers must not begin new reads
            after cleanup starts.

        Lifecycle / Cleanup:
            The owning crystal or transient analysis caller releases the
            result. Cleanup does not reach back into an analyzer or module.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._root_module_kind
            del self._module_targets
            del self._path_targets
            del self._synthetic_module_targets
            del self._synthetic_module_sources
            del self._user_module_sources
            del self._distribution_provenance
            del self._user_source_targets
            del self._site_package_targets
            del self._unknown_targets
            del self._module_to_path
            del self._module_to_kind
            del self._module_to_extension
            del self._module_to_direct_dependencies
            del self._ast_import_targets_by_module
            del self._ast_from_import_targets_by_module
            del self._physical_module_fingerprints
            del self._export_surfaces
            del self._module_load_order
            del self._walk_errors
        del self._lock

    # ------------------------------------------------------------------
    # Analyzer write surface (one writer: CrystalAnalyzer, during the pass)
    # ------------------------------------------------------------------

    def set_root_module_kind(self, root_module_kind: str) -> None:
        """
        Record the classified authority kind of the root module.

        Args:
            root_module_kind:
                One of `synthetic_module`, `user_source`, `site_package`,
                or `unknown` as produced by the custody strategy that
                matched the root module.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._root_module_kind = root_module_kind

    def record_module_target(
            self,
            *,
            module_name: str,
            module_path: Optional[str],
            module_kind: str,
            module_extension: Optional[str],
            direct_dependencies: Sequence[str],
            ast_import_targets: Sequence[str],
            ast_from_import_targets: Mapping[str, Sequence[str]],
    ) -> None:
        """
        Record one walked module into the manifest views and lookup maps.

        Contract:
            - Appends deduplicated module/path targets preserving first-seen
              order (walk order is the historical manifest order).
            - Mirrors the module into the kind-specific flat list.
            - Later records for the same module overwrite its lookup-map
              entries (last write wins, matching the pre-decomposition
              behavior of the SpellCrystal recorder).

        Args:
            module_name:
                Canonical module name being recorded.
            module_path:
                Physical backing path as text, if one exists.
            module_kind:
                Classified authority bucket for the module. Must be one of
                the four recognized kinds.
            module_extension:
                Backing file extension (with dot) when one exists.
            direct_dependencies:
                Flat direct dependency module names for the module.
            ast_import_targets:
                AST-derived flat import targets retained for diagnostics.
            ast_from_import_targets:
                AST-derived `from ... import ...` map retained for
                diagnostics.

        Raises:
            RuntimeError: If the result was cleaned.
            KeyError: If `module_kind` is not a recognized authority kind.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if module_name not in self._module_targets:
                self._module_targets.append(module_name)
            if module_path is not None:
                if module_path not in self._path_targets:
                    self._path_targets.append(module_path)
                self._module_to_path[module_name] = module_path
            if module_extension:
                self._module_to_extension[module_name] = module_extension

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

    def record_synthetic_module_source(
            self,
            module_name: str,
            source_payload: Mapping[str, object],
    ) -> None:
        """
        Record the rebuildable source custody payload for one synthetic module.

        Args:
            module_name:
                Canonical synthetic module name.
            source_payload:
                Value-only payload (source_text, source_sha256,
                binding_signature, spell_crystal_id, parent_name,
                is_package) as harvested by the synthetic custody strategy.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._synthetic_module_sources[module_name] = dict(source_payload)

    def record_user_module_source(
            self,
            module_name: str,
            source_payload: Mapping[str, object],
    ) -> None:
        """
        Record the retained source payload for one user module (S2).

        Purpose:
            Opt-in physical custody: mirror of the synthetic source store
            for user-owned files, so a fresh pod whose user source tree
            is ABSENT can rebuild the module world through the synthetic
            lane (retained text never overrides a live file).

        Args:
            module_name:
                Canonical user-source module name.
            source_payload:
                Value-only payload (source_text, source_sha256,
                module_path, is_package) as harvested by the user-source
                custody strategy.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._user_module_sources[module_name] = dict(source_payload)

    def record_distribution_provenance(
            self,
            module_name: str,
            provenance_payload: Mapping[str, object],
    ) -> None:
        """
        Record one module's third-party identity payload.

        Purpose:
            Dependency-environment provenance (finishing slices 1+2,
            2026-07-11): always-on identity capture so a restored world
            can diff its environment against the sealed one (the
            third-party sibling of source drift). Site-package modules
            carry distribution identity; compiled-extension leaves
            carry file identity.

        Args:
            module_name:
                Canonical module name (site_package or unknown-kind
                binary leaf).
            provenance_payload:
                Value-only payload: {distribution_name,
                distribution_version, all_distributions, top_level}
                from SitePackageCustodyStrategy.harvest_provenance, OR
                {binary_path, binary_sha256, top_level} from
                BinaryUnknownCustodyStrategy.harvest_binary_identity -
                consumers distinguish by keys.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._distribution_provenance[module_name] = dict(
                provenance_payload
            )

    def record_physical_fingerprint(
            self,
            module_name: str,
            source_sha256: str,
    ) -> None:
        """
        Record the bind-time source fingerprint of one physical module.

        Purpose:
            Make on-disk drift DETECTABLE: preflight can recompute the
            file's SHA256 at load time and flag a mismatch instead of
            silently restoring against changed code.

        Args:
            module_name:
                Canonical user-source module name.
            source_sha256:
                Hex SHA256 of the module's source text at analysis time.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._physical_module_fingerprints[module_name] = source_sha256

    def record_export_surface(
            self,
            module_name: str,
            all_declared: Sequence[str],
            public_names: Sequence[str],
    ) -> None:
        """
        Record the statically-derived export surface of one module.

        Args:
            module_name:
                Module whose export surface was analyzed.
            all_declared:
                Names statically resolvable from a top-level `__all__`
                assignment; empty when `__all__` is absent or dynamic.
            public_names:
                Public (non-underscore) top-level class/function/assignment
                names derived from the module body.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._export_surfaces[module_name] = {
                "all_declared": list(all_declared),
                "public_names": list(public_names),
            }

    def set_module_load_order(self, module_load_order: Sequence[str]) -> None:
        """
        Record the topological unfold order over the walked module graph.

        Contract:
            - Dependencies appear BEFORE their dependents.
            - Cycle breaks are deterministic and reported separately through
              `record_walk_error` by the producing strategy.

        Args:
            module_load_order:
                Topologically ordered module names.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._module_load_order = list(module_load_order)

    def record_walk_error(self, error_text: str) -> None:
        """
        Append one honesty-channel diagnostic from the analysis pass.

        Args:
            error_text:
                Human-readable description of a read/parse/walk failure.

        Raises:
            RuntimeError: If the result was cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._walk_errors.append(error_text)

    # ------------------------------------------------------------------
    # Read surface (detached copies; property names preserve the
    # pre-decomposition SpellCrystal vocabulary for parity)
    # ------------------------------------------------------------------

    @property
    def root_module_kind(self) -> Optional[str]:
        """
        Return the classified authority kind of the root module.

        Returns:
            Optional[str]:
                Root classification, or None when analysis never ran.
        """
        self.check_cleaned()
        with self._lock:
            return self._root_module_kind

    @property
    def module_targets(self) -> List[str]:
        """
        Return every walked module name in first-seen walk order.

        Returns:
            List[str]: Detached list of module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._module_targets)

    @property
    def path_targets(self) -> List[str]:
        """
        Return every physical backing path recorded during the walk.

        Returns:
            List[str]: Detached list of path texts.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._path_targets)

    @property
    def synthetic_module_targets(self) -> List[str]:
        """
        Return module names classified as synthetic modules.

        Returns:
            List[str]: Detached list of synthetic module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._synthetic_module_targets)

    @property
    def synthetic_module_sources(self) -> Dict[str, Dict[str, object]]:
        """
        Return the rebuildable synthetic source custody payloads.

        Returns:
            Dict[str, Dict[str, object]]:
                Detached map of module name to custody payload.
        """
        self.check_cleaned()
        with self._lock:
            return {
                name: dict(payload)
                for name, payload in self._synthetic_module_sources.items()
            }

    @property
    def user_module_sources(self) -> Dict[str, Dict[str, object]]:
        """
        Return the retained user-module source payloads (S2 custody).

        Returns:
            Dict[str, Dict[str, object]]:
                Detached map of module name to retention payload; empty
                when retention was off or no user modules were walked.
        """
        self.check_cleaned()
        with self._lock:
            return {
                name: dict(payload)
                for name, payload in self._user_module_sources.items()
            }

    @property
    def distribution_provenance(self) -> Dict[str, Dict[str, object]]:
        """
        Return the dependency-environment provenance map.

        Returns:
            Dict[str, Dict[str, object]]:
                Detached map of module name to its identity payload -
                distribution rows ({distribution_name, ...}) for
                site-package modules, file-identity rows ({binary_path,
                binary_sha256, ...}) for compiled leaves; empty when
                nothing resolved.
        """
        self.check_cleaned()
        with self._lock:
            return {
                name: dict(payload)
                for name, payload in self._distribution_provenance.items()
            }

    @property
    def user_source_targets(self) -> List[str]:
        """
        Return module names classified as user source.

        Returns:
            List[str]: Detached list of user-source module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._user_source_targets)

    @property
    def site_package_targets(self) -> List[str]:
        """
        Return module names classified as site packages.

        Returns:
            List[str]: Detached list of site-package module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._site_package_targets)

    @property
    def unknown_targets(self) -> List[str]:
        """
        Return module names whose authority could not be classified.

        Returns:
            List[str]: Detached list of unknown-target module names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._unknown_targets)

    @property
    def module_to_path(self) -> Dict[str, str]:
        """
        Return the module-to-backing-path lookup map.

        Returns:
            Dict[str, str]: Detached copy of the path map.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_path)

    @property
    def module_to_kind(self) -> Dict[str, str]:
        """
        Return the module-to-authority-kind lookup map.

        Returns:
            Dict[str, str]: Detached copy of the kind map.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_kind)

    @property
    def module_to_extension(self) -> Dict[str, str]:
        """
        Return the module-to-file-extension lookup map.

        Returns:
            Dict[str, str]: Detached copy of the extension map.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._module_to_extension)

    @property
    def module_to_direct_dependencies(self) -> Dict[str, List[str]]:
        """
        Return the per-module direct dependency edge map.

        Returns:
            Dict[str, List[str]]: Detached copy of the dependency edges.
        """
        self.check_cleaned()
        with self._lock:
            return {
                module_name: list(dependency_names)
                for module_name, dependency_names in self._module_to_direct_dependencies.items()
            }

    @property
    def ast_import_targets_by_module(self) -> Dict[str, List[str]]:
        """
        Return the AST-derived flat import diagnostics map.

        Returns:
            Dict[str, List[str]]: Detached copy of the import targets map.
        """
        self.check_cleaned()
        with self._lock:
            return {
                module_name: list(import_targets)
                for module_name, import_targets in self._ast_import_targets_by_module.items()
            }

    @property
    def ast_from_import_targets_by_module(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Return the AST-derived `from ... import ...` diagnostics map.

        Returns:
            Dict[str, Dict[str, List[str]]]:
                Detached copy of the from-import map.
        """
        self.check_cleaned()
        with self._lock:
            return {
                module_name: {
                    imported_module_name: list(imported_names)
                    for imported_module_name, imported_names in from_targets.items()
                }
                for module_name, from_targets in self._ast_from_import_targets_by_module.items()
            }

    @property
    def physical_module_fingerprints(self) -> Dict[str, str]:
        """
        Return the bind-time SHA256 fingerprints of physical modules.

        Returns:
            Dict[str, str]: Detached map of module name to hex SHA256.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._physical_module_fingerprints)

    @property
    def export_surfaces(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Return the statically-derived export surfaces per module.

        Returns:
            Dict[str, Dict[str, List[str]]]:
                Detached map of module name to
                {"all_declared": [...], "public_names": [...]}.
        """
        self.check_cleaned()
        with self._lock:
            return {
                module_name: {
                    surface_key: list(surface_names)
                    for surface_key, surface_names in surface.items()
                }
                for module_name, surface in self._export_surfaces.items()
            }

    @property
    def module_load_order(self) -> List[str]:
        """
        Return the topological unfold order over the walked module graph.

        Returns:
            List[str]: Detached ordered list (dependencies first).
        """
        self.check_cleaned()
        with self._lock:
            return list(self._module_load_order)

    @property
    def walk_errors(self) -> List[str]:
        """
        Return the honesty-channel diagnostics from the analysis pass.

        Returns:
            List[str]: Detached list of walk error texts.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._walk_errors)

    def describe(self) -> Dict[str, Any]:
        """
        Return the full detached analysis payload.

        Purpose:
            Persistence-facing view consumed by SpellCrystal.describe()
            (which merges it with crystal-owned identity fields) and by
            MutationResearch when re-analyzing retained versions.

        Contract:
            Every list and dictionary layer owned by this result is recreated
            for the response. Mutating the returned payload cannot alter the
            carried analysis, and no lock, module, AST, analyzer, or strategy
            crosses the boundary.

        Returns:
            Dict[str, Any]:
                Detached, serialization-friendly analysis payload.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "root_module_kind": self._root_module_kind,
                "module_targets": list(self._module_targets),
                "path_targets": list(self._path_targets),
                "synthetic_module_targets": list(self._synthetic_module_targets),
                "synthetic_module_sources": {
                    name: dict(payload)
                    for name, payload in self._synthetic_module_sources.items()
                },
                "user_module_sources": {
                    name: dict(payload)
                    for name, payload in self._user_module_sources.items()
                },
                # Finishing slice 1 (2026-07-11): always-on site-package
                # distribution provenance (additive; consumers use .get).
                "distribution_provenance": {
                    name: dict(payload)
                    for name, payload in self._distribution_provenance.items()
                },
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
                "ast_import_targets_by_module": {
                    module_name: list(import_targets)
                    for module_name, import_targets in self._ast_import_targets_by_module.items()
                },
                "ast_from_import_targets_by_module": {
                    module_name: {
                        imported_module_name: list(imported_names)
                        for imported_module_name, imported_names in from_targets.items()
                    }
                    for module_name, from_targets in self._ast_from_import_targets_by_module.items()
                },
                "physical_module_fingerprints": dict(self._physical_module_fingerprints),
                "export_surfaces": {
                    module_name: {
                        surface_key: list(surface_names)
                        for surface_key, surface_names in surface.items()
                    }
                    for module_name, surface in self._export_surfaces.items()
                },
                "module_load_order": list(self._module_load_order),
                "walk_errors": list(self._walk_errors),
            }
