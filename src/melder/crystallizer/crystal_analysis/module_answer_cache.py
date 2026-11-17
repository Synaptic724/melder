"""
Process-wide answers about modules, reused across crystal analyses (GitHub #331).

Purpose:
    Stop every bind from asking the same module-world questions again. With the
    Crystallizer recording, each bind analyses its spell module's whole world.
    Before this cache every analysis resolved each module's path again (a
    `Path.resolve`, about 0.1-0.2 ms on Windows), matched its custody again (more
    resolves and `Path.is_relative_to` root walks), re-ran the member-submodule
    `find_spec` probe of every `from x import name`, resolved the policy roots
    again, and a site-package root read the installed distributions again, so a
    configure binding N spells over M modules paid N x M of each.

Contract:
    - An answer is reused only while what it was derived from is unchanged: a
      module's path while the same module object (held weakly) has the same
      `__file__`, or - for a module not imported, found by `find_spec` - while
      `sys.path` is the same; a path's custody kind under the same policy roots; a
      physical module's facts while its module object, resolved path and file
      (mtime_ns, size) are unchanged; resolved roots for the same raw input and
      interpreter state; distribution provenance while the site roots'
      directories keep their modification times. A mismatch is a miss, and the
      caller's fresh answer replaces the entry.
    - Value-only: entries hold strings, ints, tuples and weak references. They
      never hold a module object (a weak reference does not keep a module alive),
      source text, AST nodes, crystals, analysis results or strategy instances.
    - Synthetic modules are never kept (callers do not store them): their source
      lives in memory and changes without a file stat to notice it.
    - Accepted residuals (owner decision 2026-11-17, #331): a member probe, a path
      resolution or a custody match re-runs only when its module or file changes,
      so a submodule file created later, a re-pointed symlink or junction, a
      package installed without touching a site root directory, or an edit that
      keeps both mtime_ns and size is not seen until then - the stat bet
      `PhysicalSourceCache` already makes.
    - Every map is LRU-bounded by `_MAX_ENTRIES`.

Threading:
    One class RLock serializes map access; callers compute answers outside it, so
    concurrent misses may compute the same deterministic answer and the last
    store wins.

Lane: crystal_analysis_reuse_2026_11_17.
"""

import sys
import threading
import types
import weakref
from collections import OrderedDict
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


# Weak reference to the module object an answer was derived from; None means the
# answer was derived with no module object (the module was not imported).
ModuleReference = Optional[weakref.ref[Any]]
# (module reference, the object's `__file__` text or None, resolved path text or None,
# the `sys.path` the answer was found on - kept only when there was no module object,
# because then the answer came from `find_spec`, which searches `sys.path`)
RememberedModulePath = Tuple[ModuleReference, Optional[str], Optional[str], Optional[Tuple[str, ...]]]
# One physical module's walk facts: dependency candidates (after member probes),
# from-import diagnostics, source sha256 (None for an empty source) and export
# surface (all_declared, public_names; None when none was recorded).
ModuleWalkFacts = Tuple[
    Tuple[str, ...],
    Tuple[Tuple[str, Tuple[str, ...]], ...],
    Optional[str],
    Optional[Tuple[Tuple[str, ...], Tuple[str, ...]]],
]
# (module reference, resolved path text, mtime_ns, size, facts)
RememberedModuleFacts = Tuple[ModuleReference, str, int, int, ModuleWalkFacts]
# The default custody chain's inputs: user roots, environment roots, site roots.
CustodyPolicyKey = Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]
# (which roots, raw inputs, the interpreter state they resolve against)
ResolvedRootsKey = Tuple[str, Tuple[str, ...], Tuple[str, ...]]
# Each site root's path text with its directory mtime_ns (-1 when it cannot be stat'ed).
SiteRootSignature = Tuple[Tuple[str, int], ...]
# (distribution name, version or None, every mapped distribution, top-level name)
ProvenanceValues = Tuple[str, Optional[str], Tuple[str, ...], str]


class ModuleAnswerCache:
    """
    Shared, guarded answers about modules that crystal analyses would otherwise recompute.

    Purpose:
        One process-wide place where an analysis finds what an earlier analysis
        already derived about a module - its resolved path, its custody kind, its
        import facts - plus the resolved policy roots and the installed
        distribution provenance, each reused only while its inputs are unchanged.

    Contract:
        - Lookups never raise for a missing or stale entry; they report a miss.
        - Stores refresh an entry's LRU position; a map past `_MAX_ENTRIES`
          evicts its least recently used entries. Eviction releases only values
          and weak references.
        - A module object that cannot be weakly referenced is never stored, so
          its answers are always computed fresh.
        - Returned values are immutable tuples or a read-only mapping view.

    Threading / Concurrency:
        All map access is serialized by one class RLock. Computation happens in
        the callers, outside the lock, so a slow disk never convoys unrelated
        lookups; concurrent misses compute the same answer and the last store
        wins.

    Lifecycle / Cleanup:
        Class-hosted state like `PhysicalSourceCache` and the analyzer's syntax
        memo; no instance lifecycle. `_clear_for_tests` empties every map and
        counter.

    Registration:
        MELDER KERNEL - guarded. A process-wide shared cache used by
        `CrystalAnalyzer` and the site-package custody strategy; never
        user-constructed or bound.

    Subsystem Context:
        The third IO-economy cache of the `crystal_analysis` subsystem. The
        analyzer's syntax memo replays a module's import events by source digest
        and `PhysicalSourceCache` serves a file's sha256 from its stat; this cache
        keeps the answers derived from them - path, custody kind, dependency
        candidates after the member probes, fingerprint and export surface - so a
        warm analysis does lookups plus one stat per physical module.

    System Context:
        Each bind with the Crystallizer recording builds a spell crystal whose
        analysis walks the spell module's world. Spells share modules, so without
        reuse a configure pays spells x modules of path resolution and probing
        (#331 measured 58,915 `realpath` calls for 600 binds over 150 modules).
        Reuse moves the analyzer's contract from "current on every analysis" to
        "current as of each module object and its file's stat" - the owner's
        decision of 2026-11-17.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Process-wide guarded answers about modules for crystal analyses.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    _MAX_ENTRIES = 8192
    _lock = threading.RLock()
    _module_paths: OrderedDict[str, RememberedModulePath] = OrderedDict()
    _custody_kinds: OrderedDict[Tuple[CustodyPolicyKey, str], str] = OrderedDict()
    _module_facts: OrderedDict[str, RememberedModuleFacts] = OrderedDict()
    _resolved_roots: OrderedDict[ResolvedRootsKey, Tuple[str, ...]] = OrderedDict()
    _distribution_maps: OrderedDict[SiteRootSignature, Dict[str, Tuple[str, ...]]] = OrderedDict()
    _provenance: OrderedDict[Tuple[SiteRootSignature, str], Tuple[Optional[ProvenanceValues]]] = OrderedDict()
    _hits = 0
    _misses = 0

    # ------------------------------------------------------------------
    # Module identity
    # ------------------------------------------------------------------

    @staticmethod
    def _reference_for(module_obj: Optional[Any]) -> Tuple[bool, ModuleReference]:
        """
        Return the weak reference an entry keeps for one module object.

        Contract:
            - No object gives `(True, None)`: the answer is kept for "no object".
            - An object that cannot be weakly referenced gives `(False, None)`:
              the caller must not store an answer for it.

        Args:
            module_obj:
                The module object the answer was derived from, or None.

        Returns:
            Tuple[bool, ModuleReference]: Whether the answer may be kept, and
            the reference to keep.
        """
        if module_obj is None:
            return True, None
        try:
            return True, weakref.ref(module_obj)
        except TypeError:
            return False, None

    @staticmethod
    def _same_module(reference: ModuleReference, module_obj: Optional[Any]) -> bool:
        """
        Return whether a kept reference names the module object in play now.

        Contract:
            A None reference matches only no object; a live reference matches
            only the very same object (`is`); a dead reference matches nothing.

        Args:
            reference:
                The reference kept with the answer.
            module_obj:
                The module object of the current question, or None.

        Returns:
            bool: True when the answer was derived from this object.
        """
        if reference is None:
            return module_obj is None
        return module_obj is not None and reference() is module_obj

    # ------------------------------------------------------------------
    # LRU helpers (callers hold the lock)
    # ------------------------------------------------------------------

    @classmethod
    def _count(cls, hit: bool) -> None:
        """
        Count one lookup as a hit or a miss.

        Args:
            hit:
                True for a hit.

        Returns:
            None.

        Threading:
            Callers hold the class lock.
        """
        if hit:
            cls._hits += 1
        else:
            cls._misses += 1

    @classmethod
    def _bound(cls, table: OrderedDict[Any, Any]) -> None:
        """
        Evict a map's least recently used entries beyond the capacity.

        Args:
            table:
                The map just stored into.

        Returns:
            None.

        Threading:
            Callers hold the class lock.
        """
        while len(table) > cls._MAX_ENTRIES:
            table.popitem(last=False)

    # ------------------------------------------------------------------
    # Module paths
    # ------------------------------------------------------------------

    @classmethod
    def lookup_module_path(
            cls,
            module_name: str,
            module_obj: Optional[Any],
            file_text: Optional[str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Return the resolved path kept for one module, when it still applies.

        Contract:
            A hit requires the same module object (or none) and the same
            `__file__` text as when the path was kept. With no module object
            the path came from `find_spec`, so a hit also requires the same
            `sys.path`.

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The live module object, or None.
            file_text:
                The object's `__file__` text now, or None.

        Returns:
            Tuple[bool, Optional[str]]: Whether the answer was found, and the
            kept resolved path text (None for a pathless module).
        """
        search_path = tuple(sys.path) if module_obj is None else None
        with cls._lock:
            entry = cls._module_paths.get(module_name)
            if (
                    entry is None
                    or entry[1] != file_text
                    or entry[3] != search_path
                    or not cls._same_module(entry[0], module_obj)
            ):
                cls._count(False)
                return False, None
            cls._module_paths.move_to_end(module_name)
            cls._count(True)
            return True, entry[2]

    @classmethod
    def store_module_path(
            cls,
            module_name: str,
            module_obj: Optional[Any],
            file_text: Optional[str],
            path_text: Optional[str],
    ) -> None:
        """
        Keep one module's resolved path for later analyses.

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The module object the path was resolved for, or None.
            file_text:
                The object's `__file__` text used, or None.
            path_text:
                The resolved path text, or None for a pathless module.

        Returns:
            None.
        """
        keepable, reference = cls._reference_for(module_obj)
        if not keepable:
            return
        search_path = tuple(sys.path) if module_obj is None else None
        with cls._lock:
            cls._module_paths[module_name] = (reference, file_text, path_text, search_path)
            cls._module_paths.move_to_end(module_name)
            cls._bound(cls._module_paths)

    # ------------------------------------------------------------------
    # Custody kinds
    # ------------------------------------------------------------------

    @classmethod
    def lookup_custody_kind(cls, policy_key: CustodyPolicyKey, path_text: str) -> Optional[str]:
        """
        Return the custody kind kept for one resolved path under one policy.

        Args:
            policy_key:
                The default custody chain's roots (user, environment, site).
            path_text:
                The module's resolved path text.

        Returns:
            Optional[str]: The kept kind, or None on a miss.
        """
        key = (policy_key, path_text)
        with cls._lock:
            kind = cls._custody_kinds.get(key)
            if kind is None:
                cls._count(False)
                return None
            cls._custody_kinds.move_to_end(key)
            cls._count(True)
            return kind

    @classmethod
    def store_custody_kind(cls, policy_key: CustodyPolicyKey, path_text: str, kind: str) -> None:
        """
        Keep the custody kind the default chain gave one resolved path.

        Contract:
            Callers store only non-synthetic kinds: a synthetic match depends on
            the module object, not the path.

        Args:
            policy_key:
                The default custody chain's roots.
            path_text:
                The module's resolved path text.
            kind:
                The matched strategy's kind.

        Returns:
            None.
        """
        key = (policy_key, path_text)
        with cls._lock:
            cls._custody_kinds[key] = kind
            cls._custody_kinds.move_to_end(key)
            cls._bound(cls._custody_kinds)

    # ------------------------------------------------------------------
    # Module facts
    # ------------------------------------------------------------------

    @classmethod
    def lookup_module_facts(
            cls,
            module_name: str,
            module_obj: Optional[Any],
            path_text: str,
            mtime_ns: int,
            size: int,
    ) -> Optional[ModuleWalkFacts]:
        """
        Return the facts kept for one physical module, when they still apply.

        Contract:
            A hit requires the same module object (or none), the same resolved
            path and the file's current (mtime_ns, size).

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The live module object, or None.
            path_text:
                The module's resolved path text.
            mtime_ns:
                The file's modification time now.
            size:
                The file's size now.

        Returns:
            Optional[ModuleWalkFacts]: The kept facts, or None on a miss.
        """
        with cls._lock:
            entry = cls._module_facts.get(module_name)
            if (
                    entry is None
                    or entry[1] != path_text
                    or entry[2] != mtime_ns
                    or entry[3] != size
                    or not cls._same_module(entry[0], module_obj)
            ):
                cls._count(False)
                return None
            cls._module_facts.move_to_end(module_name)
            cls._count(True)
            return entry[4]

    @classmethod
    def store_module_facts(
            cls,
            module_name: str,
            module_obj: Optional[Any],
            path_text: str,
            mtime_ns: int,
            size: int,
            facts: ModuleWalkFacts,
    ) -> None:
        """
        Keep one physical module's facts for later analyses.

        Contract:
            `mtime_ns` and `size` must come from a stat taken before the source
            was read, so a write landing mid-read leaves a guard that misses.

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The module object the facts were derived from, or None.
            path_text:
                The module's resolved path text.
            mtime_ns:
                The file's modification time before the read.
            size:
                The file's size before the read.
            facts:
                The derived facts.

        Returns:
            None.
        """
        keepable, reference = cls._reference_for(module_obj)
        if not keepable:
            return
        with cls._lock:
            cls._module_facts[module_name] = (reference, path_text, mtime_ns, size, facts)
            cls._module_facts.move_to_end(module_name)
            cls._bound(cls._module_facts)

    # ------------------------------------------------------------------
    # Resolved policy roots
    # ------------------------------------------------------------------

    @classmethod
    def lookup_resolved_roots(cls, key: ResolvedRootsKey) -> Optional[Tuple[str, ...]]:
        """
        Return the resolved roots kept for one raw input and interpreter state.

        Args:
            key:
                (which roots, raw inputs, interpreter state) as the resolver
                builds it.

        Returns:
            Optional[Tuple[str, ...]]: The resolved root texts, or None on a miss.
        """
        with cls._lock:
            roots = cls._resolved_roots.get(key)
            if roots is None:
                cls._count(False)
                return None
            cls._resolved_roots.move_to_end(key)
            cls._count(True)
            return roots

    @classmethod
    def store_resolved_roots(cls, key: ResolvedRootsKey, roots: Tuple[str, ...]) -> None:
        """
        Keep resolved roots for one raw input and interpreter state.

        Args:
            key:
                (which roots, raw inputs, interpreter state).
            roots:
                The resolved root texts, in order.

        Returns:
            None.
        """
        with cls._lock:
            cls._resolved_roots[key] = roots
            cls._resolved_roots.move_to_end(key)
            cls._bound(cls._resolved_roots)

    # ------------------------------------------------------------------
    # Installed distributions
    # ------------------------------------------------------------------

    @classmethod
    def lookup_distribution_map(cls, signature: SiteRootSignature) -> Optional[Mapping[str, Tuple[str, ...]]]:
        """
        Return the top-level-to-distributions map read under one site-root state.

        Args:
            signature:
                Each site root's path text and directory mtime_ns.

        Returns:
            Optional[Mapping[str, Tuple[str, ...]]]: A read-only view of the kept
            map, or None on a miss.
        """
        with cls._lock:
            mapping = cls._distribution_maps.get(signature)
            if mapping is None:
                cls._count(False)
                return None
            cls._distribution_maps.move_to_end(signature)
            cls._count(True)
            return types.MappingProxyType(mapping)

    @classmethod
    def store_distribution_map(
            cls,
            signature: SiteRootSignature,
            mapping: Mapping[str, Sequence[str]],
    ) -> Mapping[str, Tuple[str, ...]]:
        """
        Keep a copy of `importlib.metadata.packages_distributions()` for one site-root state.

        Args:
            signature:
                Each site root's path text and directory mtime_ns, taken before
                the map was read.
            mapping:
                The map as read: top-level name to distribution names.

        Returns:
            Mapping[str, Tuple[str, ...]]: A read-only view of the kept copy.
        """
        kept = {str(name): tuple(str(item) for item in names) for name, names in mapping.items()}
        with cls._lock:
            cls._distribution_maps[signature] = kept
            cls._distribution_maps.move_to_end(signature)
            cls._bound(cls._distribution_maps)
        return types.MappingProxyType(kept)

    @classmethod
    def lookup_provenance(
            cls,
            signature: SiteRootSignature,
            top_level: str,
    ) -> Tuple[bool, Optional[ProvenanceValues]]:
        """
        Return the provenance kept for one top-level name under one site-root state.

        Args:
            signature:
                Each site root's path text and directory mtime_ns.
            top_level:
                The module's top-level package name.

        Returns:
            Tuple[bool, Optional[ProvenanceValues]]: Whether the answer was
            found, and the kept values (None when no distribution provides the
            name).
        """
        key = (signature, top_level)
        with cls._lock:
            entry = cls._provenance.get(key)
            if entry is None:
                cls._count(False)
                return False, None
            cls._provenance.move_to_end(key)
            cls._count(True)
            return True, entry[0]

    @classmethod
    def store_provenance(
            cls,
            signature: SiteRootSignature,
            top_level: str,
            values: Optional[ProvenanceValues],
    ) -> None:
        """
        Keep the provenance resolved for one top-level name under one site-root state.

        Args:
            signature:
                Each site root's path text and directory mtime_ns.
            top_level:
                The module's top-level package name.
            values:
                The resolved values, or None when no distribution provides it.

        Returns:
            None.
        """
        key = (signature, top_level)
        with cls._lock:
            cls._provenance[key] = (values,)
            cls._provenance.move_to_end(key)
            cls._bound(cls._provenance)

    # ------------------------------------------------------------------
    # Test hooks
    # ------------------------------------------------------------------

    @classmethod
    def _clear_for_tests(cls) -> None:
        """
        Empty every map and counter for deterministic test isolation.

        Contract:
            Test-only hook; never runs in production lanes. Releases only values
            and weak references.

        Returns:
            None.
        """
        with cls._lock:
            cls._module_paths.clear()
            cls._custody_kinds.clear()
            cls._module_facts.clear()
            cls._resolved_roots.clear()
            cls._distribution_maps.clear()
            cls._provenance.clear()
            cls._hits = 0
            cls._misses = 0

    @classmethod
    def _stats_for_tests(cls) -> Dict[str, int]:
        """
        Return detached sizes and counters for regression assertions.

        Returns:
            Dict[str, int]: Each map's size, the capacity, hits and misses.
        """
        with cls._lock:
            return {
                "module_paths": len(cls._module_paths),
                "custody_kinds": len(cls._custody_kinds),
                "module_facts": len(cls._module_facts),
                "resolved_roots": len(cls._resolved_roots),
                "distribution_maps": len(cls._distribution_maps),
                "provenance": len(cls._provenance),
                "capacity": cls._MAX_ENTRIES,
                "hits": cls._hits,
                "misses": cls._misses,
            }
