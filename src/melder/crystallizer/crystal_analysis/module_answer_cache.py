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
      loaded module's facts while its module object and import spec (`__spec__`,
      which `importlib.reload` replaces) and resolved path are unchanged, and a
      not-imported module's facts while its file's (mtime_ns, size) is (owner
      direction 2026-11-17: repeat work works off in-memory data); resolved roots
      for the same raw input and interpreter state; distribution provenance while
      the site roots' directories keep their modification times; a whole analysed
      world while every module it touched passes those same checks. A mismatch is
      a miss, and the caller's fresh answer replaces the entry.
    - Value-only: entries hold strings, ints, tuples and weak references. They
      never hold a module object (a weak reference does not keep a module alive),
      source text, AST nodes, crystals, analysis results or strategy instances.
    - Synthetic modules are never kept (callers do not store them): their source
      lives in memory and changes without a file stat to notice it.
    - Accepted residuals (owner decisions 2026-11-17, #331): a member probe, a path
      resolution or a custody match re-runs only when its module changes, so a
      submodule file created later, a re-pointed symlink or junction, or a package
      installed without touching a site root directory is not seen until then; a
      loaded module's file edited without a reload keeps its earlier analysis - the
      running module is still the code it describes - until the module is reloaded
      or re-imported; a not-imported file edited without changing mtime_ns or size
      is not seen (the stat bet `PhysicalSourceCache` makes).
    - Every map is LRU-bounded by `_MAX_ENTRIES`, except kept worlds, which are
      larger and bounded by `_MAX_WORLDS`.

Threading:
    One class RLock serializes map access; callers compute answers outside it, so
    concurrent misses may compute the same deterministic answer and the last
    store wins.

Lane: crystal_analysis_reuse_2026_11_17.
"""

import os
import sys
import threading
import types
import weakref
from collections import OrderedDict
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


# Weak reference to the module object an answer was derived from; None means the
# answer was derived with no module object (the module was not imported).
ModuleReference = Optional[weakref.ref[Any]]
# Weak reference to that module object's import spec (`__spec__`); None when the
# module has no spec or there is no module object. A reload installs a new spec.
SpecReference = Optional[weakref.ref[Any]]
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
# (module reference, spec reference, resolved path text, (mtime_ns, size) of the
# file - kept only for a module with no object - and the facts)
RememberedModuleFacts = Tuple[ModuleReference, SpecReference, str, Optional[Tuple[int, int]], ModuleWalkFacts]
# The default custody chain's inputs: user roots, environment roots, site roots.
CustodyPolicyKey = Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]
# (which roots, raw inputs, the interpreter state they resolve against)
ResolvedRootsKey = Tuple[str, Tuple[str, ...], Tuple[str, ...]]
# Each site root's path text with its directory mtime_ns (-1 when it cannot be stat'ed).
SiteRootSignature = Tuple[Tuple[str, int], ...]
# (distribution name, version or None, every mapped distribution, top-level name)
ProvenanceValues = Tuple[str, Optional[str], Tuple[str, ...], str]
# (policy key, site-package descent, root module name, root module path text)
WorldKey = Tuple[CustodyPolicyKey, bool, str, Optional[str]]
# One module an analysed world touched: (name, module reference, spec reference,
# the `sys.path` it was found on - kept only with no module object - and, for a
# file read with no module object, (path text, mtime_ns, size)).
WorldEntry = Tuple[str, ModuleReference, SpecReference, Optional[Tuple[str, ...]], Optional[Tuple[str, int, int]]]
# (root entry, every other touched module, the site-root signature when the world
# carries distribution provenance, the finished result's describe() payload)
RememberedWorld = Tuple[WorldEntry, Tuple[WorldEntry, ...], Optional[SiteRootSignature], Dict[str, Any]]


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
        candidates after the member probes, fingerprint and export surface - and
        whole analysed worlds, so a repeat bind copies a finished result after
        checking its modules in memory, and a new world's walk does lookups.

    System Context:
        Each bind with the Crystallizer recording builds a spell crystal whose
        analysis walks the spell module's world. Spells share modules, so without
        reuse a configure pays spells x modules of path resolution and probing
        (#331 measured 58,915 `realpath` calls for 600 binds over 150 modules).
        Reuse moves the analyzer's contract from "current on every analysis" to
        "current as of each module object and its import spec" (a module not
        imported: its file's stat) - the owner's decisions of 2026-11-17.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Process-wide guarded answers about modules for crystal analyses.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    _MAX_ENTRIES = 8192
    # A kept world carries a full describe() payload (hundreds of modules), so
    # far fewer are kept than single answers; spells of one module bind together.
    _MAX_WORLDS = 128
    _lock = threading.RLock()
    _module_paths: OrderedDict[str, RememberedModulePath] = OrderedDict()
    _custody_kinds: OrderedDict[Tuple[CustodyPolicyKey, str], str] = OrderedDict()
    _module_facts: OrderedDict[str, RememberedModuleFacts] = OrderedDict()
    _resolved_roots: OrderedDict[ResolvedRootsKey, Tuple[str, ...]] = OrderedDict()
    _distribution_maps: OrderedDict[SiteRootSignature, Dict[str, Tuple[str, ...]]] = OrderedDict()
    _provenance: OrderedDict[Tuple[SiteRootSignature, str], Tuple[Optional[ProvenanceValues]]] = OrderedDict()
    _worlds: OrderedDict[WorldKey, RememberedWorld] = OrderedDict()
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

    @staticmethod
    def _current_spec(module_obj: Any) -> Optional[Any]:
        """
        Return a module object's import spec, or None when it has none.

        Contract:
            Reads `__spec__` directly; an object without the attribute (a
            non-module placed in `sys.modules`) counts as having no spec.

        Args:
            module_obj:
                A module object.

        Returns:
            Optional[Any]: The `ModuleSpec`, or None.
        """
        try:
            return module_obj.__spec__
        except AttributeError:
            return None

    @classmethod
    def _spec_reference_for(cls, module_obj: Optional[Any]) -> Tuple[bool, SpecReference]:
        """
        Return the weak reference an entry keeps for a module object's import spec.

        Contract:
            - No object, or an object with no spec, gives `(True, None)`.
            - A spec that cannot be weakly referenced gives `(False, None)`: the
              caller must not keep an answer that depends on it.

        Args:
            module_obj:
                The module object the answer was derived from, or None.

        Returns:
            Tuple[bool, SpecReference]: Whether the answer may be kept, and the
            reference to keep.
        """
        if module_obj is None:
            return True, None
        spec = cls._current_spec(module_obj)
        if spec is None:
            return True, None
        try:
            return True, weakref.ref(spec)
        except TypeError:
            return False, None

    @classmethod
    def _same_spec(cls, reference: SpecReference, module_obj: Any) -> bool:
        """
        Return whether a module object still carries the import spec an answer was derived under.

        Contract:
            `importlib.reload` installs a new spec on the same module object, so a
            reloaded module fails this check while an untouched one passes it.

        Args:
            reference:
                The spec reference kept with the answer.
            module_obj:
                The module object of the current question.

        Returns:
            bool: True when the module's current spec is the kept one.
        """
        spec = cls._current_spec(module_obj)
        if reference is None:
            return spec is None
        return spec is not None and reference() is spec

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
            file_stat: Optional[Tuple[int, int]],
    ) -> Optional[ModuleWalkFacts]:
        """
        Return the facts kept for one physical module, when they still apply.

        Contract:
            - A hit requires the same module object (or none) and the same
              resolved path.
            - A loaded module (an object) also needs the same import spec; its
              file is not consulted (`file_stat` is None): repeat work runs from
              memory, and a reload installs a new spec (owner direction
              2026-11-17).
            - A module with no object also needs the file's current
              (mtime_ns, size).

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The live module object, or None.
            path_text:
                The module's resolved path text.
            file_stat:
                (mtime_ns, size) of the file now when there is no module object;
                None for a loaded module.

        Returns:
            Optional[ModuleWalkFacts]: The kept facts, or None on a miss.
        """
        with cls._lock:
            entry = cls._module_facts.get(module_name)
            current = (
                entry is not None
                and entry[2] == path_text
                and entry[3] == file_stat
                and cls._same_module(entry[0], module_obj)
                and (module_obj is None or cls._same_spec(entry[1], module_obj))
            )
            if not current or entry is None:
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
            file_stat: Optional[Tuple[int, int]],
            facts: ModuleWalkFacts,
    ) -> None:
        """
        Keep one physical module's facts for later analyses.

        Contract:
            - A loaded module's facts are kept with its object and import spec
              and `file_stat` None.
            - A module with no object keeps `file_stat`, which must come from a
              stat taken before the source was read, so a write landing mid-read
              leaves a guard that misses.
            - Nothing is kept for an object, or a spec, that cannot be weakly
              referenced.

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The module object the facts were derived from, or None.
            path_text:
                The module's resolved path text.
            file_stat:
                (mtime_ns, size) before the read when there is no module object;
                None for a loaded module.
            facts:
                The derived facts.

        Returns:
            None.
        """
        keepable, reference = cls._reference_for(module_obj)
        spec_keepable, spec_reference = cls._spec_reference_for(module_obj)
        if not keepable or not spec_keepable:
            return
        with cls._lock:
            cls._module_facts[module_name] = (reference, spec_reference, path_text, file_stat, facts)
            cls._module_facts.move_to_end(module_name)
            cls._bound(cls._module_facts)

    # ------------------------------------------------------------------
    # Whole analysed worlds
    # ------------------------------------------------------------------

    @classmethod
    def make_world_entry(
            cls,
            module_name: str,
            module_obj: Optional[Any],
            file_guard: Optional[Tuple[str, int, int]],
    ) -> Optional[WorldEntry]:
        """
        Build the entry a kept world uses to check one touched module.

        Contract:
            - A loaded module keeps weak references to its object and spec.
            - A module with no object keeps the current `sys.path` and, when the
              walk read its file, `file_guard` (path text, mtime_ns, size).
            - Returns None when the object or its spec cannot be weakly
              referenced: such a world is not kept.

        Args:
            module_name:
                Canonical module name.
            module_obj:
                The object the walk saw for the name, or None.
            file_guard:
                The stat the walk took before reading the file of a module with
                no object; ignored for a loaded module.

        Returns:
            Optional[WorldEntry]: The entry, or None when it cannot be kept.
        """
        keepable, reference = cls._reference_for(module_obj)
        spec_keepable, spec_reference = cls._spec_reference_for(module_obj)
        if not keepable or not spec_keepable:
            return None
        if module_obj is not None:
            return module_name, reference, spec_reference, None, None
        return module_name, None, None, tuple(sys.path), file_guard

    @classmethod
    def lookup_world(cls, key: WorldKey, root_obj: Optional[Any]) -> Optional[Mapping[str, Any]]:
        """
        Return a kept world's `describe()` payload when every module it touched is unchanged.

        Contract:
            - The root entry is checked against `root_obj`, the object the caller
              analyses (a crystal may take it from the spell, not `sys.modules`);
              every other entry against `sys.modules` now, as the walk would.
            - Loaded modules are checked in memory (object and spec identity);
              modules with no object by `sys.path` and, when read, file stat;
              recorded provenance by the site roots' directory times.
            - The returned payload is the kept one, read-only by contract: callers
              copy it (`CrystalAnalysisResult.load_described_payload`) and never
              mutate it.

        Args:
            key:
                (policy key, descent flag, root name, root path text).
            root_obj:
                The root module object of this analysis, or None.

        Returns:
            Optional[Mapping[str, Any]]: The kept payload, or None on a miss.

        Threading:
            Validation reads `sys.modules` and stats outside the lock.
        """
        with cls._lock:
            world = cls._worlds.get(key)
        current = world is not None and cls._world_is_current(world, root_obj)
        with cls._lock:
            if not current or world is None:
                cls._count(False)
                return None
            if key in cls._worlds:
                cls._worlds.move_to_end(key)
            cls._count(True)
        return world[3]

    @classmethod
    def store_world(
            cls,
            key: WorldKey,
            root_entry: WorldEntry,
            entries: Tuple[WorldEntry, ...],
            site_signature: Optional[SiteRootSignature],
            payload: Dict[str, Any],
    ) -> None:
        """
        Keep one analysed world for later analyses rooted at the same module.

        Args:
            key:
                (policy key, descent flag, root name, root path text).
            root_entry:
                The root module's entry.
            entries:
                Every other module the walk touched.
            site_signature:
                The site-root signature, when the world carries distribution
                provenance; else None.
            payload:
                The finished result's `describe()` payload; the cache owns it from
                here and never hands it out for mutation.

        Returns:
            None.
        """
        with cls._lock:
            cls._worlds[key] = (root_entry, entries, site_signature, payload)
            cls._worlds.move_to_end(key)
            while len(cls._worlds) > cls._MAX_WORLDS:
                cls._worlds.popitem(last=False)

    @classmethod
    def _world_is_current(cls, world: RememberedWorld, root_obj: Optional[Any]) -> bool:
        """
        Return whether every module a kept world touched is unchanged.

        Args:
            world:
                The kept world.
            root_obj:
                The root module object of this analysis, or None.

        Returns:
            bool: True when the kept payload is what a walk would record now.
        """
        root_entry, entries, site_signature, _payload = world
        search_path = tuple(sys.path)
        if not cls._entry_is_current(root_entry, root_obj, search_path):
            return False
        modules = sys.modules
        for entry in entries:
            if not cls._entry_is_current(entry, modules.get(entry[0]), search_path):
                return False
        return site_signature is None or cls._site_signature_is_current(site_signature)

    @classmethod
    def _entry_is_current(cls, entry: WorldEntry, module_obj: Optional[Any], search_path: Tuple[str, ...]) -> bool:
        """
        Check one touched module against what is in play now.

        Args:
            entry:
                The kept entry.
            module_obj:
                The object in play for the name now, or None.
            search_path:
                The current `sys.path` as a tuple.

        Returns:
            bool: True when the module is unchanged for the walk's purposes.
        """
        _name, reference, spec_reference, kept_search_path, file_guard = entry
        if reference is not None:
            return (
                module_obj is not None
                and reference() is module_obj
                and cls._same_spec(spec_reference, module_obj)
            )
        if module_obj is not None or kept_search_path != search_path:
            return False
        if file_guard is None:
            return True
        path_text, modified_ns, size = file_guard
        try:
            stat_result = os.stat(path_text)
        except OSError:
            return False
        return stat_result.st_mtime_ns == modified_ns and stat_result.st_size == size

    @staticmethod
    def _site_signature_is_current(site_signature: SiteRootSignature) -> bool:
        """
        Return whether each site root still has the directory time a world recorded.

        Args:
            site_signature:
                (path text, directory mtime_ns or -1) per site root.

        Returns:
            bool: True when no site root changed.
        """
        for path_text, modified_ns in site_signature:
            try:
                current_ns = os.stat(path_text).st_mtime_ns
            except OSError:
                current_ns = -1
            if current_ns != modified_ns:
                return False
        return True

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
            cls._worlds.clear()
            cls._hits = 0
            cls._misses = 0

    @classmethod
    def _stats_for_tests(cls) -> Dict[str, int]:
        """
        Return detached sizes and counters for regression assertions.

        Returns:
            Dict[str, int]: Each map's size, both capacities, hits and misses.
        """
        with cls._lock:
            return {
                "module_paths": len(cls._module_paths),
                "custody_kinds": len(cls._custody_kinds),
                "module_facts": len(cls._module_facts),
                "resolved_roots": len(cls._resolved_roots),
                "distribution_maps": len(cls._distribution_maps),
                "provenance": len(cls._provenance),
                "worlds": len(cls._worlds),
                "capacity": cls._MAX_ENTRIES,
                "world_capacity": cls._MAX_WORLDS,
                "hits": cls._hits,
                "misses": cls._misses,
            }
