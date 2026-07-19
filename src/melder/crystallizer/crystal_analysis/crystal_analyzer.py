"""
Standalone crystal analyzer: custody dispatch + single-pass fact extraction.

This is the machinery that previously lived welded inside the SpellCrystal
constructor (classification, source resolution, AST extraction, dependency
walk, synthetic harvest). It now runs as one composable service with two
entry points: a live spell root, or a RETAINED describe() payload - the
seam MutationResearch needs to re-analyze historical versions without a
living object.

Per the V3 carrier law, crystals CALL this service at construction and own
the returned result; they never own the machinery.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

import ast
import hashlib
import importlib.util
import site
import sys
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.synthetic_module import SyntheticModule
from melder.crystallizer.crystal_analysis.physical_source_cache import (
    PhysicalSourceCache,
)
from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.custody.source_custody_strategy import (
    SourceCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy import (
    SyntheticCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy import (
    UserSourceCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy import (
    SitePackageCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy import (
    BinaryUnknownCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.base_strategy import (
    CrystalFactStrategy,
    FactContext,
    ImportEvent,
)
from melder.crystallizer.crystal_analysis.strategies.import_statement_strategy import (
    ImportStatementStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.from_import_statement_strategy import (
    FromImportStatementStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.export_surface_strategy import (
    ExportSurfaceStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.dependency_view_strategy import (
    DependencyViewStrategy,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


MemoizedModuleFactKey = Tuple[int, str]
MemoizedModuleFacts = Tuple[
    Tuple[ImportEvent, ...],
    Tuple[str, ...],
    Tuple[str, ...],
]


class CrystalAnalyzer(Cleanable):
    """
    Compose custody and fact strategies into one analysis pass.

    Purpose:
        Produce one `CrystalAnalysisResult` for a module world, either
        from a live spell root (bind-time custody) or from a retained
        payload (historical re-analysis for MutationResearch).

    Contract:
        - SINGLE-USE by convention: one analyzer instance serves one
          `analyze_spell_root(...)` or `analyze_payload(...)` call, then
          is cleaned by its caller (SpellCrystal cleans in a finally).
        - Custody strategies are consulted in priority order and the FIRST
          match classifies the module - the order [synthetic, user_source,
          site_package, fallback] reproduces the historical
          `_classify_module_target` decision table exactly.
        - On a memo miss or custom-strategy path, each parsed module AST is
          walked ONCE and nodes dispatch in strategy registration order,
          preserving historical manifest ordering. Memo hits skip AST work.
        - The analyzer is the only writer of manifest-structural records
          (module targets); strategies write only their own fact channels.
        - The default fact-strategy family participates in a shared bounded
          LRU keyed by the analysis-fact schema version and SHA-256 of current
          source text. Explicitly supplied fact strategies bypass that memo
          because their purity and environment dependencies are unknown.
        - Memo entries contain only ordered import-event descriptors and
          export-name tuples. They never retain source text, AST nodes,
          modules, paths, functions, classes, crystals, analysis results, or
          strategy instances, so the memo cannot extend those objects'
          lifetimes or interfere with module garbage collection.
        - A cache hit replays plain imports but resolves relative imports and
          probes member submodules against the live package environment.
          Custody classification, source resolution, source fingerprinting,
          dependency traversal, provenance capture, and result construction
          therefore remain current on every analysis.
        - Source edits invalidate entries naturally because the digest changes;
          fact-schema changes invalidate them by incrementing
          '_MEMOIZED_MODULE_FACT_SCHEMA_VERSION'.

    Threading:
        Each analyzer instance is thread-confined to its caller. The shared
        value-only syntax memo is guarded by a class lock; expensive parsing
        occurs outside that lock and concurrent misses may compute the same
        deterministic fact entry before one wins publication.

    Lifecycle / Cleanup:
        Owns its strategy instances; cleanup cleans strategies
        children-first then deletes the owned lists (del posture). The shared
        bounded memo is not owned by an analyzer instance and therefore
        survives individual analyzer cleanup.
    """

    __melder_internal__ = _mrg.sentinel
    # Process-local memo of immutable syntax facts. Capacity bounds retained
    # value data; LRU eviction releases only tuples/strings and has no effect
    # on imported modules or their sys.modules residency.
    _MEMOIZED_MODULE_FACT_SCHEMA_VERSION = 1
    # Empty-source law anchor (IO-economy lane, 2026-07-19): empty
    # modules never enter the syntax memo, so the stat fast path must
    # short-circuit them BEFORE the memo lookup - otherwise every warm
    # pass counts a phantom miss per empty __init__.py (and pays a
    # pointless read). sha256 of zero bytes == sha256 of the empty str.
    _EMPTY_SOURCE_SHA256 = hashlib.sha256(b"").hexdigest()
    _MAX_MEMOIZED_MODULE_FACTS = 2048
    _memoized_module_fact_lock = threading.RLock()
    _memoized_module_facts: OrderedDict[
        MemoizedModuleFactKey,
        MemoizedModuleFacts,
    ] = OrderedDict()
    _memoized_module_fact_hits = 0
    _memoized_module_fact_misses = 0

    __slots__ = (
        "_custody_strategies",
        "_fact_strategies",
        "_retain_user_sources",
        "_site_package_dependency_descent",
        "_uses_default_fact_strategies",
    )

    def __init__(
            self,
            *,
            user_source_root_paths: Tuple[Path, ...],
            site_package_root_paths: Tuple[Path, ...],
            custody_strategies: Optional[Sequence[SourceCustodyStrategy]] = None,
            fact_strategies: Optional[Sequence[CrystalFactStrategy]] = None,
            retain_user_sources: bool = False,
            site_package_dependency_descent: bool = True,
    ) -> None:
        """
        Initialize one analyzer with its strategy families.

        Purpose:
            Bind one analysis pass to explicit custody policy and fact
            strategies while selecting whether the safe default-strategy memo
            may participate.

        Contract:
            - Strategy sequences are copied into analyzer-owned lists; callers
              retain ownership only of any objects they supplied explicitly.
            - Omitting fact strategies installs the known default family and
              enables value-only syntax memoization.
            - Supplying any fact-strategy sequence, including an empty one,
              disables memoization rather than assuming custom behavior is
              source-pure.
            - Construction does not read modules, parse source, or populate
              the shared memo; work begins at an analysis entry point.

        Args:
            user_source_root_paths:
                Resolved roots defining `user_source` authority (policy
                input; resolve via `resolve_user_root_paths`).
            site_package_root_paths:
                Resolved interpreter site roots (resolve via
                `resolve_site_package_root_paths`).
            custody_strategies:
                Optional override of the custody priority chain. When
                omitted, the default four-strategy chain is built. The
                LAST strategy must match unconditionally.
            fact_strategies:
                Optional override of the fact passes. When omitted, the
                default set is built: import_statement,
                from_import_statement, export_surface, dependency_view.
            retain_user_sources:
                Opt-in S2 physical custody: True harvests the source
                TEXT of every walked user_source module (mirror of the
                M3 synthetic harvest); False (default) harvests nothing
                user-side - byte-identical to the pre-S2 result.
            site_package_dependency_descent:
                Descent policy for installed third-party packages: True
                (raw-analyzer default, byte-compatible) walks INTO their
                dependencies; False records site-package nodes as
                provenance-carrying leaves with no source read. The
                shipped default lives on CrystallizerConfiguration
                (False) and threads through SpellCrystal.

        Returns:
            None.

        Threading:
            The constructed analyzer is thread-confined. Shared memo locking
            occurs only if a later live analysis uses the default strategies.

        Lifecycle / Cleanup:
            The analyzer owns its strategy instances and must be cleaned after
            its single analysis pass. It does not own the class-level memo.
        """
        super().__init__()
        self._retain_user_sources: bool = bool(retain_user_sources)
        # Descent policy for installed third-party packages: when False
        # the walk records site-package nodes as provenance-carrying
        # LEAVES (no source read, no interior enqueue). Raw analyzer
        # constructions default True (byte-compatible); the shipped
        # default lives on CrystallizerConfiguration (False) and is
        # threaded through SpellCrystal.
        self._site_package_dependency_descent: bool = bool(
            site_package_dependency_descent
        )
        self._uses_default_fact_strategies: bool = fact_strategies is None
        if custody_strategies is None:
            self._custody_strategies: List[SourceCustodyStrategy] = [
                SyntheticCustodyStrategy(),
                UserSourceCustodyStrategy(user_source_root_paths),
                SitePackageCustodyStrategy(site_package_root_paths),
                BinaryUnknownCustodyStrategy(),
            ]
        else:
            self._custody_strategies = list(custody_strategies)
        if fact_strategies is None:
            self._fact_strategies: List[CrystalFactStrategy] = [
                ImportStatementStrategy(),
                FromImportStatementStrategy(),
                ExportSurfaceStrategy(),
                DependencyViewStrategy(),
            ]
        else:
            self._fact_strategies = list(fact_strategies)

    def cleanup(self) -> None:
        """
        Idempotently clean owned strategies (children first), then fields.

        Contract:
            - Repeated calls return without touching deleted fields.
            - Cleans every owned custody and fact strategy before deleting the
              owned strategy lists and memo-eligibility flag.
            - Does not clear, mutate, or otherwise own the shared memoized
              syntax facts; they remain available to later analyzer instances.
            - After cleanup, live analysis methods are invalid through the
              inherited Cleanable contract.

        Returns:
            None.

        Threading:
            Analyzer instances are thread-confined; callers must not race
            cleanup with active analysis.

        Lifecycle / Cleanup:
            Child strategies are released first. The process-local memo keeps
            only immutable values and follows its independent bounded-LRU
            lifetime.
        """
        if self._cleaned:
            return
        self._cleaned = True
        for custody_strategy in self._custody_strategies:
            custody_strategy.cleanup()
        for fact_strategy in self._fact_strategies:
            fact_strategy.cleanup()
        del self._custody_strategies
        del self._fact_strategies
        del self._uses_default_fact_strategies

    @classmethod
    def _clear_memoized_module_facts_for_tests(cls) -> None:
        """
        Clear the shared syntax-fact memo for deterministic test isolation.

        Purpose:
            Give regression tests a known empty memo without coupling normal
            analyzer cleanup to shared-cache lifetime.

        Contract:
            This test-only hook removes value entries and resets counters. It
            never unloads modules or mutates any live analysis result.

        Returns:
            None.

        Threading:
            Serialized by the memo lock.
        """
        with cls._memoized_module_fact_lock:
            cls._memoized_module_facts.clear()
            cls._memoized_module_fact_hits = 0
            cls._memoized_module_fact_misses = 0

    @classmethod
    def _memoized_module_fact_stats_for_tests(cls) -> Dict[str, int]:
        """
        Return detached counters for memoization regression assertions.

        Purpose:
            Expose deterministic observability for tests without returning the
            mutable OrderedDict or its lock.

        Contract:
            The returned dictionary is newly allocated and contains exactly
            size, capacity, hits, and misses as integer values. Mutating it
            cannot affect the memo.

        Returns:
            Dict[str, int]:
                Current entry count, capacity, hits, and misses.

        Threading:
            Captures one consistent snapshot under the memo lock.
        """
        with cls._memoized_module_fact_lock:
            return {
                "size": len(cls._memoized_module_facts),
                "capacity": cls._MAX_MEMOIZED_MODULE_FACTS,
                "hits": cls._memoized_module_fact_hits,
                "misses": cls._memoized_module_fact_misses,
            }

    @classmethod
    def _lookup_memoized_module_facts(
            cls,
            source_digest: str,
    ) -> Optional[MemoizedModuleFacts]:
        """
        Look up immutable syntax facts for the current source digest.

        Purpose:
            Reuse source-derived work across independent analyzer instances
            while preserving live custody and import-environment decisions.

        Contract:
            - The effective key combines the fact-schema version with the
              supplied digest.
            - A miss increments misses and returns None without publishing.
            - A hit promotes the entry to most-recently-used, increments hits,
              and returns the immutable tuple already stored.
            - Lookup never stores source text or receives a module reference.

        Args:
            source_digest:
                SHA-256 of the current source text.

        Returns:
            Optional[MemoizedModuleFacts]:
                Value-only facts on a hit, otherwise None.

        Threading:
            Lookup, LRU promotion, and counters are serialized by the memo
            lock. Returned tuples are immutable and safe to replay after the
            lock is released.
        """
        key = (cls._MEMOIZED_MODULE_FACT_SCHEMA_VERSION, source_digest)
        with cls._memoized_module_fact_lock:
            facts = cls._memoized_module_facts.get(key)
            if facts is None:
                cls._memoized_module_fact_misses += 1
                return None
            cls._memoized_module_facts.move_to_end(key)
            cls._memoized_module_fact_hits += 1
            return facts

    @classmethod
    def _store_memoized_module_facts(
            cls,
            source_digest: str,
            facts: MemoizedModuleFacts,
    ) -> None:
        """
        Publish one immutable syntax-fact entry into the bounded LRU.

        Purpose:
            Make a completed cold-path extraction reusable without retaining
            any live analysis machinery.

        Contract:
            Concurrent misses may compute the same deterministic value. The
            first published value wins; later publishers only promote it.
            Eviction removes value tuples only and never touches modules.

        Args:
            source_digest:
                SHA-256 of the source that produced the facts.
            facts:
                Immutable import events and export names. No source text, AST,
                module, function, class, path, crystal, or result references.

        Returns:
            None.

        Threading:
            Publication and eviction are serialized by the memo lock.

        Lifecycle / Cleanup:
            Entries survive analyzer-instance cleanup and remain until LRU
            eviction or the explicit test reset. Eviction releases value data
            only; it never unloads or destroys a Python module.
        """
        key = (cls._MEMOIZED_MODULE_FACT_SCHEMA_VERSION, source_digest)
        with cls._memoized_module_fact_lock:
            if key in cls._memoized_module_facts:
                cls._memoized_module_facts.move_to_end(key)
                return
            cls._memoized_module_facts[key] = facts
            while (
                    len(cls._memoized_module_facts)
                    > cls._MAX_MEMOIZED_MODULE_FACTS
            ):
                cls._memoized_module_facts.popitem(last=False)

    @staticmethod
    def _source_digest(source_text: str) -> str:
        """
        Return the memo key digest without retaining the source text.

        Purpose:
            Create a stable content identity for safe syntax-fact reuse without
            placing the source itself in the memo key or value.

        Contract:
            Encodes source as UTF-8 and returns the lowercase SHA-256
            hexadecimal digest. The method is pure and retains no state.

        Args:
            source_text:
                Current source resolved by the custody strategy.

        Returns:
            str: SHA-256 hexadecimal digest.
        """
        return hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Policy-root resolution (moved from SpellCrystal; crystals call these
    # once, keep the tuples for describe() parity, and pass them here)
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_user_root_paths(
            user_source_root_paths: Optional[Sequence[Union[str, Path]]],
    ) -> Tuple[Path, ...]:
        """
        Resolve the user-source classification roots from bind policy.

        Contract:
            - Falls back to the current working directory when omitted
              (first-slice fallback, unchanged from the historical
              resolver).
            - Entries must be str or Path.
            - Resolves every value to an absolute path and deduplicates
              while preserving first-seen order (exact parity with the
              historical SpellCrystal resolver).

        Args:
            user_source_root_paths:
                Optional explicit source roots from the bind seam.

        Returns:
            Tuple[Path, ...]: Resolved, deduplicated user roots.

        Raises:
            TypeError: If an entry is not a str or Path value.
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
    def resolve_site_package_root_paths() -> Tuple[Path, ...]:
        """
        Resolve known site-package roots for classification.

        Contract:
            - Best-effort only; site/user-site lookup failures never abort
              analysis.
            - Deduplicates resolved roots preserving first-seen order.

        Returns:
            Tuple[Path, ...]: Normalized site-package roots.
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

    # ------------------------------------------------------------------
    # Entry points
    # ------------------------------------------------------------------

    def analyze_spell_root(
            self,
            *,
            root_module_name: str,
            root_module_obj: Optional[Any],
            root_module_path: Optional[Path],
    ) -> CrystalAnalysisResult:
        """
        Analyze the live module world rooted at one spell's module.

        Args:
            root_module_name:
                Canonical root module name (resolved by the crystal from
                the spell target's identity).
            root_module_obj:
                Live root module object when available.
            root_module_path:
                Physical root module path when available.

        Returns:
            CrystalAnalysisResult:
                Fully populated result; ownership transfers to the caller.

        Raises:
            RuntimeError: If the analyzer was cleaned.
        """
        self.check_cleaned()
        result = CrystalAnalysisResult()
        root_kind = self._match_custody(
            module_name=root_module_name,
            module_obj=root_module_obj,
            module_path=root_module_path,
        ).kind
        result.set_root_module_kind(root_kind)
        self._walk_module_dependencies(
            result=result,
            module_name=root_module_name,
            module_obj=root_module_obj,
            module_path=root_module_path,
        )
        for fact_strategy in self._fact_strategies:
            fact_strategy.finalize(result)
        return result

    def analyze_payload(
            self,
            payload: Mapping[str, Any],
    ) -> CrystalAnalysisResult:
        """
        Rebuild an analysis result from a retained describe() payload.

        Purpose:
            Let MutationResearch (and preflight tooling) re-derive a
            queryable result for a HISTORICAL version with no live spell:
            recorded facts are restored verbatim and source-free derived
            facts (load order) are recomputed from the recorded edges.

        Contract:
            - Recorded truths (targets, kinds, maps, synthetic sources,
              fingerprints, export surfaces, walk errors) copy through.
            - `module_load_order` is RECOMPUTED from the recorded edges by
              the finalize passes, never trusted from the payload.

        Args:
            payload:
                A retained analysis payload - either a full SpellCrystal
                describe() dict or a bare CrystalAnalysisResult payload.

        Returns:
            CrystalAnalysisResult:
                Reconstructed result; ownership transfers to the caller.

        Raises:
            RuntimeError: If the analyzer was cleaned.
            ValueError:
                If the payload lacks `module_to_direct_dependencies` - the
                one key BOTH accepted payload shapes carry (crystal
                describe() dicts add identity keys like `root_module_name`
                on top; bare result payloads do not).
        """
        self.check_cleaned()
        if "module_to_direct_dependencies" not in payload:
            raise ValueError(
                "analyze_payload requires the 'module_to_direct_dependencies' "
                "key; got a payload with keys {0}. Pass a SpellCrystal "
                "describe() dict or a CrystalAnalysisResult describe() "
                "payload.".format(sorted(payload.keys()))
            )
        result = CrystalAnalysisResult()
        recorded_root_kind = payload.get("root_module_kind")
        if isinstance(recorded_root_kind, str):
            result.set_root_module_kind(recorded_root_kind)

        module_to_path = dict(payload.get("module_to_path", {}))
        module_to_kind = dict(payload.get("module_to_kind", {}))
        module_to_extension = dict(payload.get("module_to_extension", {}))
        dependency_edges = dict(payload.get("module_to_direct_dependencies", {}))
        ast_imports = dict(payload.get("ast_import_targets_by_module", {}))
        ast_from_imports = dict(
            payload.get("ast_from_import_targets_by_module", {})
        )
        module_targets = list(payload.get("module_targets", []))
        if not module_targets:
            module_targets = list(dependency_edges.keys())

        for module_name in module_targets:
            result.record_module_target(
                module_name=module_name,
                module_path=module_to_path.get(module_name),
                module_kind=module_to_kind.get(module_name, "unknown"),
                module_extension=module_to_extension.get(module_name),
                direct_dependencies=list(
                    dependency_edges.get(module_name, [])
                ),
                ast_import_targets=list(ast_imports.get(module_name, [])),
                ast_from_import_targets={
                    base_name: list(member_names)
                    for base_name, member_names in ast_from_imports.get(
                        module_name, {}
                    ).items()
                },
            )
        for module_name, source_payload in dict(
                payload.get("synthetic_module_sources", {})
        ).items():
            result.record_synthetic_module_source(module_name, source_payload)
        # S2 physical custody: re-fold retained user sources (absent in
        # pre-S2 and retention-off payloads - .get keeps them empty).
        for module_name, source_payload in dict(
                payload.get("user_module_sources", {})
        ).items():
            result.record_user_module_source(module_name, source_payload)
        # Finishing slice 1: re-fold distribution provenance (absent in
        # pre-slice payloads - .get keeps the map empty; refold parity
        # with the live walk is the MR re-analysis seam's law).
        for module_name, provenance_payload in dict(
                payload.get("distribution_provenance", {})
        ).items():
            result.record_distribution_provenance(
                module_name, provenance_payload
            )
        for module_name, fingerprint in dict(
                payload.get("physical_module_fingerprints", {})
        ).items():
            result.record_physical_fingerprint(module_name, fingerprint)
        for module_name, surface in dict(
                payload.get("export_surfaces", {})
        ).items():
            result.record_export_surface(
                module_name,
                list(surface.get("all_declared", [])),
                list(surface.get("public_names", [])),
            )
        for error_text in list(payload.get("walk_errors", [])):
            result.record_walk_error(error_text)

        for fact_strategy in self._fact_strategies:
            fact_strategy.finalize(result)
        return result

    # ------------------------------------------------------------------
    # Walk (ported from SpellCrystal._walk_module_dependencies)
    # ------------------------------------------------------------------

    def _custody_descends(self, custody: SourceCustodyStrategy) -> bool:
        """
        Apply the descent policy on top of the strategy's own contract.

        Contract:
            A strategy that does not descend never descends. Site-package
            custody additionally answers to the analyzer's
            `site_package_dependency_descent` policy knob: when the knob
            is off, installed third-party modules become honest
            provenance-carrying leaves (no source read, no interior
            enqueue) - their file identity and distribution provenance
            still record.

        Args:
            custody:
                Matched custody strategy for the module.

        Returns:
            bool: True when the walk may extract facts and enqueue the
            module's dependencies.
        """
        if not custody.descends:
            return False
        if (
                custody.kind == "site_package"
                and not self._site_package_dependency_descent
        ):
            return False
        return True

    def _walk_module_dependencies(
            self,
            *,
            result: CrystalAnalysisResult,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> None:
        """
        Walk the module graph rooted at one module, recording targets.

        Contract:
            - Module names are the cycle-protection identity.
            - Dependencies come from source-level imports, never runtime
              object traversal.
            - Non-descending custody (unknown fallback) records honest
              leaves without enqueueing them.

        Args:
            result:
                Result receiving every record.
            module_name:
                Root module name for the walk.
            module_obj:
                Live root module object, if available.
            module_path:
                Physical root module path, if available.

        Returns:
            None.
        """
        pending: List[Tuple[str, Optional[Any], Optional[Path]]] = [
            (module_name, module_obj, module_path),
        ]
        visited_module_names: Set[str] = set()

        while pending:
            current_name, current_obj, current_path = pending.pop()
            if current_name in visited_module_names:
                continue
            visited_module_names.add(current_name)

            custody = self._match_custody(
                module_name=current_name,
                module_obj=current_obj,
                module_path=current_path,
            )
            if self._custody_descends(custody):
                flat_targets, from_targets = self._extract_module_facts(
                    result=result,
                    custody=custody,
                    module_name=current_name,
                    module_obj=current_obj,
                    module_path=current_path,
                )
            else:
                # Descent-off site-package root/node: an honest leaf -
                # no source read, no facts; provenance still harvests
                # below and the node still records.
                flat_targets, from_targets = [], {}

            tracked_dependencies: List[str] = []
            for dependency_name in flat_targets:
                dependency_obj = sys.modules.get(dependency_name)
                dependency_path = self.resolve_module_path(
                    dependency_name,
                    dependency_obj,
                )
                dependency_custody = self._match_custody(
                    module_name=dependency_name,
                    module_obj=dependency_obj,
                    module_path=dependency_path,
                )
                tracked_dependencies.append(dependency_name)
                if not self._custody_descends(dependency_custody):
                    # Honest leaf (historical unknown-target law).
                    result.record_module_target(
                        module_name=dependency_name,
                        module_path=(
                            str(dependency_path)
                            if dependency_path is not None
                            else None
                        ),
                        module_kind=dependency_custody.kind,
                        module_extension=self.resolve_file_extension(
                            dependency_path
                        ),
                        direct_dependencies=[],
                        ast_import_targets=[],
                        ast_from_import_targets={},
                    )
                    continue
                if dependency_name not in visited_module_names:
                    pending.append(
                        (dependency_name, dependency_obj, dependency_path)
                    )

            synthetic_payload = SyntheticCustodyStrategy.harvest_payload(
                current_obj
            )
            if synthetic_payload is not None:
                result.record_synthetic_module_source(
                    current_name,
                    synthetic_payload,
                )
            # S2 physical custody (opt-in mirror of the M3 synthetic
            # harvest above): retain the TEXT of every walked user_source
            # module so absent files can rebuild on fresh pods. `custody`
            # is the matched strategy; the base default returns None, so
            # only the user-source class ever yields a payload here.
            if self._retain_user_sources and custody.kind == "user_source":
                user_payload = custody.harvest_payload(
                    module_name=current_name,
                    module_path=current_path,
                )
                if user_payload is not None:
                    result.record_user_module_source(
                        current_name,
                        user_payload,
                    )
            # Finishing slice 1 (2026-07-11): ALWAYS-ON distribution
            # provenance for site-package modules - identity capture,
            # never retention, no config knob (a sealed world must know
            # which dependency versions it was built against).
            if custody.kind == "site_package":
                provenance_payload = custody.harvest_provenance(
                    module_name=current_name,
                    module_path=current_path,
                )
                if provenance_payload is not None:
                    result.record_distribution_provenance(
                        current_name,
                        provenance_payload,
                    )
            # Finishing slice 2 (2026-07-11): compiled-extension leaves
            # land their FILE identity (path + bytes sha) in the same
            # provenance channel - consumers distinguish by keys.
            elif custody.kind == "unknown":
                binary_payload = custody.harvest_binary_identity(
                    module_name=current_name,
                    module_path=current_path,
                )
                if binary_payload is not None:
                    result.record_distribution_provenance(
                        current_name,
                        binary_payload,
                    )
            result.record_module_target(
                module_name=current_name,
                module_path=(
                    str(current_path) if current_path is not None else None
                ),
                module_kind=custody.kind,
                module_extension=self.resolve_file_extension(current_path),
                direct_dependencies=tracked_dependencies,
                ast_import_targets=flat_targets,
                ast_from_import_targets=from_targets,
            )

    def _extract_module_facts(
            self,
            *,
            result: CrystalAnalysisResult,
            custody: SourceCustodyStrategy,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Resolve current source, reuse or derive syntax facts, and collect
        module output.

        Purpose:
            Reuse source-stable syntax work without weakening the analyzer's
            live custody, import-resolution, provenance, or result contracts.

        Contract:
            - Source/read errors and AST parse failures land in the
              result's walk-error honesty channel; the method returns
              empty facts in those cases (historical behavior).
            - Custody fingerprints record only when the strategy makes a
              claim (user_source in S1).
            - Source is resolved on every call. Empty or unavailable source
              returns empty dependency facts and never enters the memo.
            - Default strategies look up the current source digest before
              parsing. Hits skip AST construction and replay immutable facts
              into the fresh result.
            - Misses parse once, dispatch every node in historical order, and
              freeze only ordered import descriptors and export-name values.
            - Explicit custom fact strategies bypass lookup and publication;
              their behavior is never assumed to be source-pure.
            - Relative imports and member-submodule find_spec probes remain
              live on memo hits, while plain import names and static exports
              replay from source-derived values.
            - The cache never receives module_obj, module_path, source_text,
              syntax_tree, FactContext, or result.

        Args:
            result:
                Result receiving fingerprints and walk errors.
            custody:
                Matched custody strategy for the module.
            module_name:
                Module being analyzed.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            Tuple[List[str], Dict[str, List[str]]]:
                Deduplicated flat dependency candidates (first-seen order)
                and the `from ... import ...` diagnostics map.

        Raises:
            RuntimeError:
                If a memo entry contains an unknown internal event kind.

        Threading:
            The analyzer instance and result are thread-confined. Shared memo
            lookup/publication uses the class lock; parsing occurs outside it.

        Lifecycle / Cleanup:
            Cold-path FactContext ownership is released in a finally block.
            Memo hits allocate a fresh export record and retain no result.
        """
        # IO-economy lanes (crystallizer_analysis_io_cache lane,
        # 2026-07-19): physical readers route through the shared
        # stat-guarded PhysicalSourceCache. FAST PATH: an unchanged stat
        # plus a syntax-memo hit replays facts with ZERO reads and ZERO
        # hashes (the cached sha IS the memo digest - same UTF-8 SHA256
        # law). COLD PATH: one read through the cache computes ONE sha
        # reused as memo digest AND fingerprint claim (the historical
        # double hash is gone). Non-physical lanes (synthetic module
        # text, binary leaves) keep custody.resolve_source verbatim.
        physical_lane = (
            custody.reads_physical_source and module_path is not None
        )
        current_package = self._derive_current_package(
            module_name,
            module_obj,
        )
        if physical_lane and self._uses_default_fact_strategies:
            cached_sha = PhysicalSourceCache.fingerprint_if_unchanged(
                module_path
            )
            if cached_sha is not None:
                if cached_sha == self._EMPTY_SOURCE_SHA256:
                    # Cold-path parity for empty sources: no facts, no
                    # fingerprint, no memo participation - and now also
                    # no read.
                    return [], {}
                memoized_facts = self._lookup_memoized_module_facts(
                    cached_sha
                )
                if memoized_facts is not None:
                    if custody.claims_sha256_source_fingerprint:
                        result.record_physical_fingerprint(
                            module_name,
                            cached_sha,
                        )
                    return self._replay_memoized_module_facts(
                        result=result,
                        module_name=module_name,
                        current_package=current_package,
                        facts=memoized_facts,
                    )
        if physical_lane:
            source_text, source_sha, error_text = (
                PhysicalSourceCache.read_text_and_fingerprint(
                    module_name,
                    module_path,
                )
            )
        else:
            source_text, error_text = custody.resolve_source(
                module_name=module_name,
                module_obj=module_obj,
                module_path=module_path,
            )
            source_sha = None
        if error_text:
            result.record_walk_error(error_text)
        if not source_text:
            return [], {}

        source_digest = (
            (
                source_sha
                if source_sha is not None
                else self._source_digest(source_text)
            )
            if self._uses_default_fact_strategies
            else None
        )
        if source_digest is not None:
            memoized_facts = self._lookup_memoized_module_facts(source_digest)
            if memoized_facts is not None:
                fingerprint = custody.fingerprint(source_text)
                if fingerprint is not None:
                    result.record_physical_fingerprint(
                        module_name,
                        fingerprint,
                    )
                return self._replay_memoized_module_facts(
                    result=result,
                    module_name=module_name,
                    current_package=current_package,
                    facts=memoized_facts,
                )

        try:
            syntax_tree = ast.parse(source_text)
        except SyntaxError as exc:
            result.record_walk_error(
                "Failed to parse AST for module '{0}': SyntaxError: {1}".format(
                    module_name,
                    exc,
                )
            )
            return [], {}

        fingerprint = custody.fingerprint(source_text)
        if fingerprint is not None:
            result.record_physical_fingerprint(module_name, fingerprint)

        context = FactContext(
            module_name=module_name,
            current_package=current_package,
            source_text=source_text,
            syntax_tree=syntax_tree,
        )
        try:
            for node in ast.walk(syntax_tree):
                for fact_strategy in self._fact_strategies:
                    fact_strategy.visit_node(node, context)
            for fact_strategy in self._fact_strategies:
                fact_strategy.analyze_module(context, result)

            if source_digest is not None:
                facts: MemoizedModuleFacts = (
                    tuple(context.import_events),
                    tuple(context.export_all_declared),
                    tuple(context.export_public_names),
                )
                self._store_memoized_module_facts(source_digest, facts)
            return self._deduplicate_import_facts(
                context.flat_import_targets,
                context.from_import_targets,
            )
        finally:
            context.cleanup()

    @staticmethod
    def _replay_memoized_module_facts(
            *,
            result: CrystalAnalysisResult,
            module_name: str,
            current_package: str,
            facts: MemoizedModuleFacts,
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Replay immutable syntax facts against the live import environment.

        Purpose:
            Reconstruct the default strategies' observable module facts on a
            cache hit without rebuilding or retaining an AST.

        Contract:
            Plain imports replay verbatim. From-import bases, relative names,
            and member-submodule probes are resolved again for every analysis,
            so memoization cannot freeze find_spec or package-context truth.
            A fresh result receives a detached export-surface record.
            Import events retain mixed AST-walk order and have the value-only
            shape (kind, relative level, raw module name, imported-name tuple).
            Star members enter diagnostics but are never probed as submodules.
            Unknown relative bases are skipped exactly as on the cold path.
            Input tuples are never mutated; output lists/dictionaries and the
            export-surface record are newly allocated for the current result.
            The method never explicitly unloads, destroys, or retains a
            module. Any import-system side effects come only from the same
            find_spec probing already used by cold analysis.

        Args:
            result:
                Fresh per-crystal result receiving the export surface.
            module_name:
                Current module identity used only as the result key.
            current_package:
                Live package context for relative imports.
            facts:
                Value-only ordered import events, statically declared
                __all__ names, and public top-level names.

        Returns:
            Tuple[List[str], Dict[str, List[str]]]:
                Deduplicated dependency candidates and from-import diagnostics.

        Raises:
            RuntimeError:
                If an internally published event has an unknown kind.

        Threading:
            Called by one thread-confined analyzer. It reads immutable tuples
            without holding the memo lock.

        Lifecycle / Cleanup:
            Returned containers and the recorded export surface belong to the
            current analysis result; no reference back to the memo is stored.
        """
        import_events, all_declared, public_names = facts
        flat_import_targets: List[str] = []
        from_import_targets: Dict[str, List[str]] = {}
        for event_kind, level, raw_module_name, imported_names in import_events:
            if event_kind == "import":
                flat_import_targets.extend(imported_names)
                continue
            if event_kind != "from":
                raise RuntimeError(
                    "CrystalAnalyzer memo contains unknown import event kind "
                    "'{0}'.".format(event_kind)
                )
            if level > 0:
                relative_name = "." * level
                if raw_module_name:
                    relative_name += raw_module_name
                resolved_base = (
                    FromImportStatementStrategy._resolve_relative_import_target(
                        current_package=current_package,
                        relative_module_name=relative_name,
                    )
                )
            else:
                resolved_base = raw_module_name
            if not resolved_base:
                continue
            for imported_name in imported_names:
                if imported_name == "*":
                    continue
                candidate_module_name = "{0}.{1}".format(
                    resolved_base,
                    imported_name,
                )
                try:
                    spec = importlib.util.find_spec(candidate_module_name)
                except Exception:
                    spec = None
                if spec is not None:
                    flat_import_targets.append(candidate_module_name)
            from_import_targets.setdefault(resolved_base, []).extend(
                imported_names
            )
            flat_import_targets.append(resolved_base)

        result.record_export_surface(
            module_name,
            list(all_declared),
            list(public_names),
        )
        return CrystalAnalyzer._deduplicate_import_facts(
            flat_import_targets,
            from_import_targets,
        )

    @staticmethod
    def _deduplicate_import_facts(
            flat_import_targets: Sequence[str],
            from_import_targets: Mapping[str, Sequence[str]],
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Detach and deduplicate import outputs with first-seen ordering.

        Purpose:
            Normalize cold and warm extraction paths through the same ordering
            and ownership boundary before module facts enter a result.

        Contract:
            - Preserves the first occurrence of each flat dependency.
            - Preserves mapping insertion order and member order.
            - Never mutates either input collection.
            - Always returns new list and dictionary containers, so callers
              cannot mutate strategy accumulators or memoized tuples.

        Args:
            flat_import_targets:
                Dependency candidates in AST visit order.
            from_import_targets:
                Resolved bases mapped to imported member names.

        Returns:
            Tuple[List[str], Dict[str, List[str]]]:
                First-seen dependency candidates and detached member lists.

        Threading:
            Pure value transformation; no shared analyzer state is accessed.
        """
        deduped_targets: List[str] = []
        seen_targets: Set[str] = set()
        for target_name in flat_import_targets:
            if target_name in seen_targets:
                continue
            seen_targets.add(target_name)
            deduped_targets.append(target_name)
        detached_from_targets = {
            base_name: list(member_names)
            for base_name, member_names in from_import_targets.items()
        }
        return deduped_targets, detached_from_targets

    # ------------------------------------------------------------------
    # Shared resolution helpers (ported from SpellCrystal)
    # ------------------------------------------------------------------

    def _match_custody(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> SourceCustodyStrategy:
        """
        Return the first custody strategy claiming one module.

        Args:
            module_name:
                Module being classified.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            SourceCustodyStrategy: The matched strategy.

        Raises:
            RuntimeError:
                If no strategy matched - a misconfigured chain whose
                terminal fallback is missing.
        """
        for custody_strategy in self._custody_strategies:
            if custody_strategy.matches(
                    module_name=module_name,
                    module_obj=module_obj,
                    module_path=module_path,
            ):
                return custody_strategy
        raise RuntimeError(
            "No custody strategy matched module '{0}'. The custody chain "
            "must terminate in an unconditional fallback strategy.".format(
                module_name
            )
        )

    @staticmethod
    def _derive_current_package(
            module_name: str,
            module_obj: Optional[Any],
    ) -> str:
        """
        Derive the package context for relative import resolution.

        Contract:
            Ports the historical fallback chain: prefer `__package__`;
            otherwise treat the module as its own package when it has a
            `__path__` (package modules), else use its parent name.

        Args:
            module_name:
                Canonical module name being parsed.
            module_obj:
                Live module object when available.

        Returns:
            str: Package context (possibly empty for top-level modules).
        """
        try:
            current_package = module_obj.__package__
        except AttributeError:
            current_package = None
        if current_package:
            return current_package
        try:
            module_path_entries = module_obj.__path__
        except AttributeError:
            module_path_entries = None
        return (
            module_name
            if module_path_entries
            else module_name.rpartition(".")[0]
        )

    @staticmethod
    def resolve_module_path(
            module_name: str,
            module_obj: Optional[Any],
    ) -> Optional[Path]:
        """
        Resolve the physical path backing one module when available.

        Contract:
            - PUBLIC static: crystals use this to resolve their root
              module path before delegating analysis.
            - Synthetic modules use their crystallizer-managed physical
              path when one exists.
            - Non-synthetic modules prefer `__file__` on the live object.
            - Falls back to `importlib.util.find_spec(...)`.
            - Returns None for built-in/frozen/pathless modules.

        Args:
            module_name:
                Canonical module name to resolve.
            module_obj:
                Live module object when one is already available.

        Returns:
            Optional[Path]: Best-effort resolved path, or None.
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
                    return (
                        path.resolve()
                        if path.is_absolute() or path.exists()
                        else path
                    )
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

    @staticmethod
    def resolve_file_extension(module_path: Optional[Path]) -> Optional[str]:
        """
        Resolve the lowercased file extension for one module path.

        Contract:
            PUBLIC static: crystals use this for their root-extension
            identity field.

        Args:
            module_path:
                Physical module path, if one exists.

        Returns:
            Optional[str]: Lowercased suffix, or None when pathless.
        """
        if module_path is None:
            return None
        return module_path.suffix.lower()
