import inspect
import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, Union

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
        CrystalAnalysisResult,
    )

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class SpellCrystal(Cleanable):
    """
    Loader-facing module dependency manifest for one concrete spell version.

    Purpose:
        Build a narrow retained view of the module world one spell depends on
        so loaders can validate and activate that world before bind/conjure
        work continues.

    Guidance:
        Obtain crystals through `Crystallizer.create_spell_crystal(...)` when
        capturing a live spell or `Crystallizer.get_spell_crystal(...)` when
        reading recorded custody. Direct construction is primarily an internal
        analysis seam because the facade supplies the installed source-authority
        and retention policy. Treat a returned crystal as a current custody
        snapshot: replace-on-emit may clean a displaced instance, so fetch fresh
        for each independent operation instead of retaining it indefinitely.

        Use `describe()` for persistence, diagnostics, or agent inspection. The
        individual properties are convenient focused reads over the same carried
        truth; neither surface is a live `Spell` or executable replay plan.

    Contract:
        - constructed from one live `Spell`
        - anchored to the spell's concrete SHA256 identity
        - resolves the root target module (crystal-side identity work)
        - DELEGATES the module-world analysis to `CrystalAnalyzer`
          (crystal_analysis subsystem) and CARRIES the returned
          `CrystalAnalysisResult` - per the V3 carrier law, crystals own
          analysis RESULTS, never analyzer machinery
        - retains flat module/path/classification targets plus direct
          dependency maps through that carried result
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

    Threading:
        One instance `RLock` guards the carried identity and analysis result.
        Read surfaces return value copies, but cleanup must not race with reads.

    Lifecycle / Cleanup:
        A persistence profile owns recorded instances. Cleanup releases the
        carried `CrystalAnalysisResult` first, then identity and policy fields;
        it never cleans the original spell, module, or analyzer.

    Registration:
        MELDER KERNEL - guarded. Obtained through
        `Crystallizer.create_spell_crystal(...)` / `get_spell_crystal(...)` and
        owned by a `PersistenceProfile`; direct construction is an internal
        analysis seam only, never user-bound.

    Subsystem Context:
        One member of the crystal-twin family - the CUSTODY twin for one concrete
        spell version and the loader-facing manifest of the module world that
        spell depends on. Per the V3 CARRIER law it owns analysis RESULTS, not
        machinery: it resolves the root target module itself but DELEGATES
        module-world analysis to `CrystalAnalyzer` (the crystal_analysis
        subsystem) and CARRIES the returned `CrystalAnalysisResult`, exposing flat
        module/path/classification targets and direct-dependency edges over it. It
        rides under its `SpellbookCrystal` and pairs with the `SpellIndexCrystal`
        grouping twin.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, and the
        object the loader chain reads to validate a spell's module world BEFORE
        bind/conjure - what it imports, which targets are
        synthetic/user-owned/site-package/unresolved, which direct-dependency
        edges must activate. The carrier law (own results, never analyzers) keeps
        a durable custody record from dragging live analysis machinery across a
        boot; anchoring to the spell's concrete SHA256 makes the record
        content-addressed, so identical spell worlds compare identical and
        record-local ULIDs normalize out of the seal.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Loader-facing module dependency manifest for one concrete spell "
        "version. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )

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
        "_analysis",
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
            retain_user_sources: bool = False,
            site_package_dependency_descent: bool = True,
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
            - Resolves the root bound target and its root module
              (crystal-side identity work).
            - DELEGATES classification, source resolution, the dependency
              walk, and synthetic harvest to a single-use `CrystalAnalyzer`
              and stores the returned result (V3 carrier law).
            - Does not retain the live `Spell`, the live root target
              reference, or the analyzer after construction.
            - Captures the root module classification and all direct-dependency
              edges needed for later loader validation and world activation
              through the carried analysis result.

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
            retain_user_sources:
                Opt-in S2 physical custody: True harvests the source
                TEXT of every walked user_source module into the carried
                analysis ("user_module_sources") so fresh pods can
                rebuild absent user files through the synthetic module
                lane. False (default) records paths and fingerprints
                only - byte-identical to the pre-S2 record.
            site_package_dependency_descent:
                Analysis walk policy for installed third-party
                packages (IO-economy lane, 2026-07-19): True (raw
                default, byte-compatible) walks into their
                dependencies; False records them as
                provenance-carrying leaves with no source read. The
                crystallizer facade passes the configuration truth
                (schema default False).

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
        # The analysis maps that used to live here as twelve crystal slots
        # (module targets, kind buckets, dependency/AST maps, synthetic
        # sources, walk errors) now ride ONE carried result assigned at the
        # end of construction - see the delegation block below.

        self._created_from_synthetic_root: bool = False
        self._created_from_site_package_root: bool = False
        self._created_from_user_source_root: bool = False

        # The analyzer is imported lazily so the crystals vocabulary stays
        # import-light for emitters that never construct spell custody.
        from melder.crystallizer.crystal_analysis.crystal_analyzer import (
            CrystalAnalyzer,
        )

        # Classification policy roots resolve through the analyzer's public
        # statics; the crystal keeps the tuples for describe()/payload parity.
        self._user_root_paths: Tuple[Path, ...] = (
            CrystalAnalyzer.resolve_user_root_paths(user_source_root_paths)
        )
        self._site_package_root_paths: Tuple[Path, ...] = (
            CrystalAnalyzer.resolve_site_package_root_paths()
        )

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

        # Root-module resolution stays crystal-side (identity work): the
        # live object comes from sys.modules or the target itself, the
        # path from the analyzer's public resolver.
        root_module_obj = sys.modules.get(root_module_name)
        if root_module_obj is None:
            root_module_obj = inspect.getmodule(root_target)
        root_module_path = CrystalAnalyzer.resolve_module_path(
            root_module_name,
            root_module_obj,
        )

        self._root_module_path: Optional[str] = (
            str(root_module_path) if root_module_path is not None else None
        )
        self._root_file_extension: Optional[str] = (
            CrystalAnalyzer.resolve_file_extension(root_module_path)
        )

        # Delegate the module-world analysis (classification, source
        # resolution, dependency walk, synthetic harvest, fact passes) to
        # one single-use analyzer; the crystal owns the RESULT only. The
        # analyzer is cleaned even when analysis raises mid-construction.
        analyzer = CrystalAnalyzer(
            user_source_root_paths=self._user_root_paths,
            site_package_root_paths=self._site_package_root_paths,
            retain_user_sources=retain_user_sources,
            site_package_dependency_descent=site_package_dependency_descent,
        )
        try:
            self._analysis: CrystalAnalysisResult = analyzer.analyze_spell_root(
                root_module_name=root_module_name,
                root_module_obj=root_module_obj,
                root_module_path=root_module_path,
            )
        finally:
            analyzer.cleanup()

        root_module_kind = self._analysis.root_module_kind
        self._root_module_kind: Optional[str] = root_module_kind
        self._created_from_synthetic_root = root_module_kind == "synthetic_module"
        self._created_from_site_package_root = root_module_kind == "site_package"
        self._created_from_user_source_root = root_module_kind == "user_source"

    def cleanup(self) -> None:
        """
        Idempotently clear the retained manifest state.

        Contract:
            - Idempotent and terminal.
            - Cleans the owned analysis result before dropping crystal identity,
              bind signature, classification flags, and policy-root caches.
            - Does not unpublish modules, remove persisted files, or clean the
              live spell from which the snapshot was captured.

        Returns:
            None.

        Threading:
            Serialized by the crystal lock; callers must finish reads first.

        Lifecycle / Cleanup:
            Invoked when custody is replaced/evicted or its owning profile is
            torn down. A cleaned crystal must be fetched or reconstructed anew.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            # Children first: the carried analysis result cleans before the
            # crystal's identity surface drops.
            self._analysis.cleanup()
            del self._analysis

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
    def root_module_kind(self) -> Optional[str]:
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

        Contract:
            - The crystal's parent edge inside a PersistenceProfile; None when
              built outside a bind context.

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

        Contract:
            - Part of the retained bind signature replayed at restore; None when
              the spell was unnamed.

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

        Contract:
            - Bind-signature field replayed at restore; None means the default
              binding.

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

        Contract:
            - The frame-type NAME (class `__name__` or string form), not the
              type object; None when bound unframed.

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

        Contract:
            - Existence enum NAME (a string, not the member); bind replay passes
              it back to reconstruct the lifetime posture.

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

        Contract:
            - Permissions enum NAME (a string, not the member); bind replay
              passes it back to reconstruct the borrow posture.

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

        Contract:
            - Derived from the spell's profile TYPE NAME at construction, so this
              module never imports examiner types; bind replay passes it to the
              `profile` argument.

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

        Contract:
            - Fixed at construction: class/function roots are "hydratable";
              method/lambda/callable-object/instance roots are "replay_required"
              (they need live code participation at restore).

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
            return self._analysis.module_targets

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
            return self._analysis.path_targets

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
            return self._analysis.synthetic_module_targets

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
            return self._analysis.user_source_targets

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
            return self._analysis.site_package_targets

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
            return self._analysis.unknown_targets

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
            return self._analysis.module_to_path

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
            return self._analysis.module_to_kind

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
            return self._analysis.module_to_extension

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
            return self._analysis.module_to_direct_dependencies

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
            return self._analysis.walk_errors


    # NOTE (S1 decomposition): the user-source and site-package root
    # resolvers moved to CrystalAnalyzer.resolve_user_root_paths /
    # resolve_site_package_root_paths (crystal_analysis subsystem); the
    # constructor calls them through the analyzer's public statics.

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

    # NOTE (S1 decomposition): module-path resolution, file-extension
    # resolution, synthetic-protocol detection, and root-module resolution
    # moved to the crystal_analysis subsystem (CrystalAnalyzer public
    # statics + the synthetic custody strategy); root-module resolution is
    # now inlined in __init__ using those statics.

    # NOTE (S1 decomposition): authority classification moved to the
    # custody strategy chain (crystal_analysis/custody/), source-text
    # resolution moved to the per-class custody strategies, and
    # relative-import resolution moved to FromImportStatementStrategy.

    # NOTE (S1 decomposition): AST import extraction moved to the fact
    # strategies (ImportStatementStrategy + FromImportStatementStrategy)
    # dispatched by CrystalAnalyzer's single shared AST walk, which
    # preserves the historical single-pass candidate ordering.

    # NOTE (S1 decomposition): manifest recording moved to
    # CrystalAnalysisResult.record_module_target (same dedupe and
    # last-write-wins semantics; the analyzer is the single caller).

    # NOTE (S1 decomposition): the dependency walk moved to
    # CrystalAnalyzer._walk_module_dependencies (same LIFO order, cycle
    # protection, and honest-leaf law for unknown targets) and the
    # synthetic-source harvest (loader chain M3) moved to
    # SyntheticCustodyStrategy.harvest_payload.

    def describe(self) -> Dict[str, Any]:
        """
        Return a loader-facing snapshot of the manifest state.

        Purpose:
            Provide the complete value-shaped custody document consumed by
            persistence, restore preflight, impact analysis, diagnostics, and
            agent inspection without exposing the crystal's mutable containers.

        Contract:
            Combines crystal-owned identity/bind-policy fields with a detached
            `CrystalAnalysisResult` payload. Returned lists and dictionaries are
            independent of the carried manifest; no live spell, module, target,
            analyzer, strategy, or synchronization object crosses the boundary.

        Returns:
            Dict[str, Any]:
                Complete detached manifest snapshot suitable for durable record
                capture and read-only inspection.
        """
        self.check_cleaned()
        with self._lock:
            # The carried analysis result supplies every analysis-derived
            # key (already detached); the crystal supplies identity, bind
            # signature, policy roots, and root-derived flags. Every
            # pre-decomposition key is preserved verbatim; the tail adds
            # the S1 analysis capabilities (fingerprints, export surfaces,
            # load order, persisted AST maps).
            analysis_payload = self._analysis.describe()
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
                "module_targets": analysis_payload["module_targets"],
                "path_targets": analysis_payload["path_targets"],
                "synthetic_module_targets": analysis_payload[
                    "synthetic_module_targets"
                ],
                "synthetic_module_sources": analysis_payload[
                    "synthetic_module_sources"
                ],
                # S2 physical custody (opt-in): retained user-module
                # sources; empty dict when retention is off (additive,
                # byte-compatible for consumers using .get).
                "user_module_sources": analysis_payload[
                    "user_module_sources"
                ],
                # Finishing slice 1 (2026-07-11): always-on site-package
                # distribution provenance (additive; consumers use .get).
                "distribution_provenance": analysis_payload.get(
                    "distribution_provenance", {}
                ),
                "user_source_targets": analysis_payload["user_source_targets"],
                "site_package_targets": analysis_payload["site_package_targets"],
                "unknown_targets": analysis_payload["unknown_targets"],
                "user_source_root_paths": [
                    str(root_path) for root_path in self._user_root_paths
                ],
                "site_package_root_paths": [
                    str(root_path) for root_path in self._site_package_root_paths
                ],
                "module_to_path": analysis_payload["module_to_path"],
                "module_to_kind": analysis_payload["module_to_kind"],
                "module_to_extension": analysis_payload["module_to_extension"],
                "module_to_direct_dependencies": analysis_payload[
                    "module_to_direct_dependencies"
                ],
                "walk_errors": analysis_payload["walk_errors"],
                "created_from_synthetic_root": self._created_from_synthetic_root,
                "created_from_site_package_root": self._created_from_site_package_root,
                "created_from_user_source_root": self._created_from_user_source_root,
                "physical_module_fingerprints": analysis_payload[
                    "physical_module_fingerprints"
                ],
                "export_surfaces": analysis_payload["export_surfaces"],
                "module_load_order": analysis_payload["module_load_order"],
                "ast_import_targets_by_module": analysis_payload[
                    "ast_import_targets_by_module"
                ],
                "ast_from_import_targets_by_module": analysis_payload[
                    "ast_from_import_targets_by_module"
                ],
            }


