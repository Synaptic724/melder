"""S2b-2: normal melds on the site-plan lowering (design v2 S2) - anchored edits.

Usage: python apply_s2b2_edits.py <tree_root> [--check]

site_plan_lowering.py: `emit(..., normal_mode=True)` emits the empty key set as `def _site_plan_executor(meld)` with
misses that take no `ov`. site_plan_override_runtime.py: the runtime builds its site graph and that normal plan at
construction (`execute_normal`) and no longer takes an inner executor. generalized_hydrator.py and
many_only_hydrator.py: the runtime is built at hydration; `execute_normal` is the inner no-overrides executor and the
override lane reuses the runtime. Each anchor must match exactly once (either line ending) or nothing is written.
Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

BASE = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/"
LOWERING = BASE + "shared_assets/site_plan_lowering.py"
RUNTIME = BASE + "shared_assets/site_plan_override_runtime.py"
GENERALIZED = BASE + "strategies/generalized/hydration/generalized_hydrator.py"
MANY_ONLY = BASE + "strategies/many_only/hydration/many_only_hydrator.py"

# --------------------------------------------------------------------------------------------------------------------
# site_plan_lowering.py
# --------------------------------------------------------------------------------------------------------------------

EMIT_OLD = '''            root_spell_name: str,
            arity: int,
    ) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        """
        Emit one key-set plan: `def _site_plan_executor(meld, ov) -> instance`.

        The plan reads its constants (spells, ids, helpers) as globals of the
        returned namespace, so the caller must exec the code into that namespace.

        Args:
            steps: The lane's no-overrides steps in providers-first order.
            site_graph: Site graph built from those steps.
            resolution: The key set's resolution (winners, positional, conflicts).
            root_instance_key: Instance key of the root step.
            root_spell_id: Selected root spell id (P2 root message, error ids).
            root_spell_name: Root spell name for wrapped conflict errors.
            arity: Length of `__args__` for this plan (0 when absent).

        Raises:
            RuntimeError: When the root step is missing from `steps`.
'''
EMIT_NEW = '''            root_spell_name: str,
            arity: int,
            normal_mode: bool = False,
    ) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        """
        Emit one key-set plan: `def _site_plan_executor(meld, ov) -> instance`.

        The plan reads its constants (spells, ids, helpers) as globals of the
        returned namespace, so the caller must exec the code into that namespace.
        In normal mode (S2b-2, 2026-09-26) the empty key set is emitted as
        `def _site_plan_executor(meld)`: the normal-lane executor, whose misses
        take no `ov` either, since nothing reads it without winners.

        Args:
            steps: The lane's no-overrides steps in providers-first order.
            site_graph: Site graph built from those steps.
            resolution: The key set's resolution (winners, positional, conflicts).
            root_instance_key: Instance key of the root step.
            root_spell_id: Selected root spell id (P2 root message, error ids).
            root_spell_name: Root spell name for wrapped conflict errors.
            arity: Length of `__args__` for this plan (0 when absent).
            normal_mode: Emit the `(meld)` normal-lane form; requires a
                resolution with no winners and no conflicts, and arity 0.

        Raises:
            RuntimeError: When the root step is missing from `steps`, or
                `normal_mode` is asked for a key set that supplies anything.
'''

EMIT_BODY_OLD = '''        demanded = cls.demanded_instance_keys(site_graph, resolution)
        kept = tuple(step for step in steps if step.instance_key in demanded)
'''
EMIT_BODY_NEW = '''        if normal_mode and (resolution.winners or resolution.conflicts or arity):
            raise RuntimeError("A normal-mode plan is only emitted for a key set that supplies nothing.")
        demanded = cls.demanded_instance_keys(site_graph, resolution)
        kept = tuple(step for step in steps if step.instance_key in demanded)
'''

EMISSION_CALL_OLD = '''            root_spell_name=root_spell_name,
            arity=arity,
        )
        try:
            return emission.render()
'''
EMISSION_CALL_NEW = '''            root_spell_name=root_spell_name,
            arity=arity,
            normal_mode=normal_mode,
        )
        try:
            return emission.render()
'''

EMISSION_DOC_OLD = '''        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],
          v...)`: the outer values its sites read, in step order. It builds the
'''
EMISSION_DOC_NEW = '''        - Normal mode (S2b-2, 2026-09-26) drops `ov` from the plan and from
          every miss signature and call; nothing else changes.
        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],
          v...)`: the outer values its sites read, in step order. It builds the
'''

SLOTS_OLD = '''        "_root_index",
        "_miss_lines",
    ]
'''
SLOTS_NEW = '''        "_root_index",
        "_miss_lines",
        "_context_params",
    ]
'''

INIT_SIG_OLD = '''            root_spell_name: str,
            arity: int,
    ) -> None:
        """
        Prepare emission state; nothing is emitted until `render`.
'''
INIT_SIG_NEW = '''            root_spell_name: str,
            arity: int,
            normal_mode: bool = False,
    ) -> None:
        """
        Prepare emission state; nothing is emitted until `render`.
'''

INIT_ARGS_OLD = '''            arity: Length of `__args__` for this plan (0 when absent).

        Returns:
            None.
        """
        super().__init__()
        self._steps: Tuple[SitePlanStep, ...] = steps
'''
INIT_ARGS_NEW = '''            arity: Length of `__args__` for this plan (0 when absent).
            normal_mode: Emit `(meld)` signatures without `ov` (the caller has
                checked that the key set supplies nothing).

        Returns:
            None.
        """
        super().__init__()
        self._steps: Tuple[SitePlanStep, ...] = steps
'''

INIT_TAIL_OLD = '''        self._root_index: int = -1
        self._miss_lines: List[str] = []
'''
INIT_TAIL_NEW = '''        self._root_index: int = -1
        self._miss_lines: List[str] = []
        # Leading parameters of the plan and of every miss.
        self._context_params: Tuple[str, ...] = ("meld",) if normal_mode else ("meld", "ov")
'''

CLEANUP_OLD = '''        del self._root_index
        del self._miss_lines
'''
CLEANUP_NEW = '''        del self._root_index
        del self._miss_lines
        del self._context_params
'''

RENDER_DOC_OLD = '''            The source defines one `_miss{i}` per kept shared site, then the plan
            `def _site_plan_executor(meld, ov)`; all of it is exec'd into the
            returned namespace. Placement is computed first (see `_place`).
'''
RENDER_DOC_NEW = '''            The source defines one `_miss{i}` per kept shared site, then the plan
            `def _site_plan_executor(meld, ov)` (`(meld)` in normal mode); all
            of it is exec'd into the returned namespace. Placement is computed
            first (see `_place`).
'''

RENDER_DEF_OLD = '''        source_lines.append(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}(meld, ov):")
'''
RENDER_DEF_NEW = '''        signature = ", ".join(self._context_params)
        source_lines.append(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}({signature}):")
'''

HIT_ARGS_OLD = '''        arguments = ", ".join(["meld", "ov", store] + self._miss_arguments(index))
'''
HIT_ARGS_NEW = '''        arguments = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
'''

MISS_PARAMS_OLD = '''        parameters = ", ".join(["meld", "ov", store] + self._miss_arguments(index))
'''
MISS_PARAMS_NEW = '''        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
'''

# --------------------------------------------------------------------------------------------------------------------
# site_plan_override_runtime.py
# --------------------------------------------------------------------------------------------------------------------

RT_DOC_OLD = '''    Purpose:
        Replace the per-call targeting runtime of the many_only and generalized
        families. An override meld looks up the plan for its payload's key
        tuple and calls it; the plan builds only what the key set leaves
        unsupplied (design v2 step S3).

    Contract:
        - `execute_with_overrides(meld, overrides) -> instance` keeps the
          signature the CreationContext override doors call. `overrides` None
          runs the inner no-overrides executor.
'''
RT_DOC_NEW = '''    Purpose:
        Replace the per-call targeting runtime of the many_only and generalized
        families. An override meld looks up the plan for its payload's key
        tuple and calls it; the plan builds only what the key set leaves
        unsupplied (design v2 step S3). Since S2b-2 (2026-09-26) the runtime
        also owns the normal lane: its empty-key-set plan is the family's
        inner no-overrides executor.

    Contract:
        - Construction builds the site graph from the steps and the live
          Phase-3 topologies and compiles the normal plan, exposed as
          `execute_normal(meld) -> instance`; the family hydrators install it as
          the inner no-overrides executor. Site-graph errors raise unwrapped.
        - `execute_with_overrides(meld, overrides) -> instance` keeps the
          signature the CreationContext override doors call. `overrides` None
          runs the normal plan.
'''

RT_DOC2_OLD = '''        - A key set with no winning operand (for example `__args__=[]`) runs
          the inner no-overrides executor.
        - The site graph is built once, on the first compile, from the steps
          and the live Phase-3 topologies.
'''
RT_DOC2_NEW = '''        - A key set with no winning operand (for example `__args__=[]`) runs
          the normal plan.
        - The site graph is built once, at construction, and kept for later
          key sets.
'''

RT_LIFE_OLD = '''    Lifecycle / Cleanup:
        Owned by the lazy override door that hydrated it, for the executor's
        lifetime (as the old closure runtime was). `cleanup()` is idempotent:
        it clears the plans, cleans the site graph and every step it owns
        (built or masked), then deletes its fields. The root spell and the
        inner executor are borrowed.
'''
RT_LIFE_NEW = '''    Lifecycle / Cleanup:
        Built by the family hydrator at first meld and kept alive by the
        executors it hands out (the plans' namespaces reference its steps), for
        the executor lifetime. `cleanup()` is idempotent: it clears the plans,
        cleans the site graph and every step it owns (built or masked), then
        deletes its fields; plans called after it are invalid. The root spell
        is borrowed.
'''

RT_SUBSYS_OLD = '''    Subsystem Context:
        Built by `many_only_hydrator._hydrate_overrides_runtime` and
        `generalized_hydrator._hydrate_overrides_runtime`.
'''
RT_SUBSYS_NEW = '''    Subsystem Context:
        Built by `many_only_hydrator._build_site_plan_runtime` and
        `generalized_hydrator._build_site_plan_runtime`.
'''

RT_SLOTS_OLD = '''        "execute_with_overrides",
        "_steps",
        "_root_spell",
        "_root_spell_id",
        "_root_instance_key",
        "_inner_no_overrides_executor",
        "_plans",
'''
RT_SLOTS_NEW = '''        "execute_with_overrides",
        "execute_normal",
        "_steps",
        "_root_spell",
        "_root_spell_id",
        "_root_instance_key",
        "_plans",
'''

RT_INIT_OLD = '''            root_spell: Spell,
            root_instance_key: SiteInstanceKey,
            inner_no_overrides_executor: Callable[[Any], Any],
    ) -> None:
        """
        Build the runtime; no plan or site graph is compiled yet.

        Args:
            steps: The lane's no-overrides steps in providers-first order (owned).
            root_spell: The melded root spell (borrowed).
            root_instance_key: Instance key of the root step.
            inner_no_overrides_executor: The lane's inner `(meld) -> instance`
                executor (borrowed), used for payloads with no winning operand.

        Raises:
            RuntimeError: When no step carries `root_instance_key`.
'''
RT_INIT_NEW = '''            root_spell: Spell,
            root_instance_key: SiteInstanceKey,
    ) -> None:
        """
        Build the runtime: the site graph and the normal plan; override plans compile per key set later.

        Args:
            steps: The lane's no-overrides steps in providers-first order (owned).
            root_spell: The melded root spell (borrowed); its Spellbook's live
                Phase-3 topologies are read here.
            root_instance_key: Instance key of the root step.

        Raises:
            RuntimeError: When no step carries `root_instance_key`, or the site
                graph cannot be built from the steps.
'''

RT_FIELDS_OLD = '''        self._root_instance_key: SiteInstanceKey = root_instance_key
        self._inner_no_overrides_executor: Callable[[Any], Any] = inner_no_overrides_executor
        self._plans: Dict[Tuple[str, ...], PlanCallable] = {}
        self._compile_lock: threading.Lock = threading.Lock()
        self._site_graph: Optional[SpellSiteGraphAnalysis] = None
        self._owned_masked_steps: List[SitePlanStep] = []
        self.execute_with_overrides: Callable[[Any, Optional[Dict[str, Any]]], Any] = (
'''
RT_FIELDS_NEW = '''        self._root_instance_key: SiteInstanceKey = root_instance_key
        self._plans: Dict[Tuple[str, ...], PlanCallable] = {}
        self._compile_lock: threading.Lock = threading.Lock()
        self._site_graph: Optional[SpellSiteGraphAnalysis] = None
        self._owned_masked_steps: List[SitePlanStep] = []
        self.execute_normal: Callable[[Any], Any] = self._compile_normal_plan()
        self.execute_with_overrides: Callable[[Any, Optional[Dict[str, Any]]], Any] = (
'''

RT_CLEANUP_OLD = '''        del self.execute_with_overrides
        del self._steps
        del self._root_spell
        del self._root_spell_id
        del self._root_instance_key
        del self._inner_no_overrides_executor
        del self._plans
'''
RT_CLEANUP_NEW = '''        del self.execute_with_overrides
        del self.execute_normal
        del self._steps
        del self._root_spell
        del self._root_spell_id
        del self._root_instance_key
        del self._plans
'''

RT_DISPATCH_OLD = '''                inner: Callable[[Any], Any] = self._inner_no_overrides_executor,
'''
RT_DISPATCH_NEW = '''                inner: Callable[[Any], Any] = self.execute_normal,
'''

RT_GRAPH_OLD = '''    def _site_graph_or_build(self) -> SpellSiteGraphAnalysis:
        """
        Return the site graph, building it on first use (caller holds the compile lock).
        """
'''
RT_GRAPH_NEW = '''    def _site_graph_or_build(self) -> SpellSiteGraphAnalysis:
        """
        Return the site graph, building it on first use.

        Contract:
            Called from construction (before the runtime is shared) or under the
            compile lock; since S2b-2 construction always builds it.
        """
'''

RT_COMPILE_OLD = '''        resolution = self._resolve(keys, arity)
        if not resolution.winners:
            inner = self._inner_no_overrides_executor

            def normal_plan(meld: Any, ov: Dict[str, Any], inner: Callable[[Any], Any] = inner) -> Any:
                return inner(meld)

            return normal_plan
'''
RT_COMPILE_NEW = '''        resolution = self._resolve(keys, arity)
        if not resolution.winners:
            inner = self.execute_normal

            def normal_plan(meld: Any, ov: Dict[str, Any], inner: Callable[[Any], Any] = inner) -> Any:
                return inner(meld)

            return normal_plan
'''

RT_TAIL_OLD = '''        self._owned_masked_steps.extend(masked)
        code = get_or_compile_executor_code(source=source, source_name=SitePlanLowering.PLAN_SOURCE_NAME)
        exec(code, namespace)
        plan: PlanCallable = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
        return plan
'''
RT_TAIL_NEW = RT_TAIL_OLD + '''
    def _compile_normal_plan(self) -> Callable[[Any], Any]:
        """
        Build the site graph and compile the empty key set in normal mode (S2b-2).

        Contract:
            - Runs at construction, before the runtime is shared, so no lock is
              taken. Site-graph build errors propagate unwrapped: they are not
              override key errors.
            - The plan is `(meld) -> instance`: every demanded step, shared sites
              as hit reads with out-of-line misses (B2), the family's store
              routing, build guards and registration.

        Returns:
            Callable[[Any], Any]: The normal-lane executor.
        """
        site_graph = self._site_graph_or_build()
        source, namespace, masked = SitePlanLowering.emit(
            steps=self._steps,
            site_graph=site_graph,
            resolution=OverrideKeyResolver.resolve(site_graph, ()),
            root_instance_key=self._root_instance_key,
            root_spell_id=self._root_spell_id,
            root_spell_name=self._root_spell.spell_name,
            arity=0,
            normal_mode=True,
        )
        self._owned_masked_steps.extend(masked)
        code = get_or_compile_executor_code(source=source, source_name=SitePlanLowering.PLAN_SOURCE_NAME)
        exec(code, namespace)
        normal: Callable[[Any], Any] = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
        return normal
'''

# --------------------------------------------------------------------------------------------------------------------
# generalized_hydrator.py
# --------------------------------------------------------------------------------------------------------------------

GEN_DOC_OLD = '''    1. Resolve live identity (spells, path registry) through the resolver.
    2. Build slotted runtime rows from manifest rows.
    3. Hydrate the inner no-overrides executor through the family compiler
       (row-driven emission, process-wide factory cache).
    4. Build the family override runtime lazily at the first override meld:
       `SitePlanOverrideRuntime` over the same no-overrides rows, one
       compiled plan per override key set (2026-09-26).
    5. Wrap both lanes in the shared route-keyed CreationContext doors.
'''
GEN_DOC_NEW = '''    1. Resolve live identity (spells, path registry) through the resolver.
    2. Hydrate the manifest's no-overrides rows into site-plan steps.
    3. Build `SitePlanOverrideRuntime` over them (2026-09-26, S2b-2): its
       normal plan (the empty key set) is the inner no-overrides executor, and
       it compiles one plan per override key set at first use.
    4. Wrap both lanes in the shared route-keyed CreationContext doors (the
       override door is compiled at the first override meld).
    5. Optionally (configuration flag) install the singleton warm-tail
       specializer; its body comes from the family's old step emitter and it
       deopts to the normal plan.
'''

GEN_IMPORT_OLD = '''    build_specialized_no_overrides_executor,
    hydrate_no_overrides_executor,
    resolve_root_instance_key_from_rows,
'''
GEN_IMPORT_NEW = '''    build_specialized_no_overrides_executor,
    resolve_root_instance_key_from_rows,
'''

GEN_HYD_OLD = '''    no_overrides_payload = manifest["no_overrides"]
    no_overrides_spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
    )
    inner_no_overrides_executor = hydrate_no_overrides_executor(
        rows=no_overrides_payload["steps_rows"],
        transient_schema=no_overrides_payload["transient_schema"],
        root_instance_key=no_overrides_payload["root_instance_key"],
        root_spell_id=no_overrides_payload["root_spell_id"],
        spell_lookup=no_overrides_spell_lookup,
    )
'''
GEN_HYD_NEW = '''    no_overrides_payload = manifest["no_overrides"]
    no_overrides_spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
    )
    # One runtime per root serves both lanes (S2b-2, 2026-09-26): its normal
    # plan is the inner no-overrides executor; override key sets compile on it.
    site_plan_runtime = _build_site_plan_runtime(
        no_overrides_payload=no_overrides_payload,
        spell_lookup=no_overrides_spell_lookup,
        root_spell=root_spell,
    )
    inner_no_overrides_executor = site_plan_runtime.execute_normal
'''

GEN_OVDOOR_CALL_OLD = '''    overrides_door = _build_lazy_overrides_door(
        manifest=manifest,
        root_spell=root_spell,
        route_key=route_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
'''
GEN_OVDOOR_CALL_NEW = '''    overrides_door = _build_lazy_overrides_door(
        root_spell=root_spell,
        route_key=route_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
        execute_with_overrides=site_plan_runtime.execute_with_overrides,
    )
'''

GEN_RUNTIME_START = '''def _hydrate_overrides_runtime(
        *,
        manifest: Dict[str, Any],
'''
GEN_RUNTIME_STOP = '''def _resolve_spell_lookup(
        *,
        resolver: Any,
'''
GEN_RUNTIME_NEW = '''def _build_site_plan_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell_lookup: Dict[str, Any],
        root_spell: Any,
) -> SitePlanOverrideRuntime:
    """
    Build the root's site-plan runtime: the normal plan now, override plans per key set later.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's
          step-row hydration (`_hydrate_steps_from_rows`), which also resolves
          contract payload references to live values where rows carry them, so
          normal and override plans see the same steps (design v2 S3a, S2b-2).
          The manifest's overrides payload is not read.
        - The runtime builds its site graph and normal plan at construction
          (first meld); requires phases 1-7 live, which meld's structural gates
          guarantee on every path that reaches hydration.

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell_lookup:
            Live spell per step spell id.
        root_spell:
            Live root spell.

    Raises:
        RuntimeError:
            When rows, the root instance key or the site graph cannot be
            resolved.

    Returns:
        SitePlanOverrideRuntime: The runtime (kept alive by the executors it
        hands out).
    """
    steps_rows = no_overrides_payload["steps_rows"]
    rows = _hydrate_steps_from_rows(
        steps_rows=steps_rows,
        spell_lookup=spell_lookup,
    )
    root_instance_key = resolve_root_instance_key_from_rows(
        rows=steps_rows,
        explicit_root_instance_key=no_overrides_payload["root_instance_key"],
        root_spell_id=no_overrides_payload["root_spell_id"],
    )
    return SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_generalized_row(row) for row in rows),
        root_spell=root_spell,
        root_instance_key=root_instance_key,
    )


'''

GEN_LAZY_SIG_OLD = '''def _build_lazy_overrides_door(
        *,
        manifest: Dict[str, Any],
        root_spell: Any,
        route_key: str,
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build a cold overrides door that hydrates the overrides runtime lazily.

    Purpose:
        Defer the overrides-lane hydration cost (no-overrides row hydration,
        root-instance-key resolution, and the key-set plan runtime build)
        from FIRST MELD to FIRST OVERRIDE MELD, so override-free workloads
        never pay for the lane at all.

    Contract:
        - Zero hydration work at build time: closure construction only.
        - The first override call hydrates exactly once (leader under the
          lock, followers wait), builds the real route-keyed overrides door
          through the same door compiler the eager path used, then swaps it
          into the spell's currently published `CreationContext`
          `_overrides_executor` slot (self-replacing slot contract), so the
          shim vanishes from later override melds.
        - Hydration resolves through a fresh `SpellbookBindingResolver` at
          first override call, mirroring `_hydrate_once`; phases 1-7 liveness
          is guaranteed by meld's structural gates on every path that can
          reach an executor.
        - When no context is published (publish=False cache loads), the shim
          keeps delegating correctly; only the swap optimization is skipped.
        - Behavior delta vs the eager path is TIMING ONLY: overrides-lane
          hydration errors surface at the first override meld instead of the
          first meld. Result values, error types, and the no-overrides lane
          are unchanged.

    Args:
        manifest:
            Validated family manifest; its no-overrides rows feed the
            override runtime.
        root_spell:
            Live root spell whose published context receives the hot swap.
        route_key:
            Family route key for the door compiler.
        inner_no_overrides_executor:
            Already-hydrated inner no-overrides executor the overrides door
            falls back to for empty payloads.
'''
GEN_LAZY_SIG_NEW = '''def _build_lazy_overrides_door(
        *,
        root_spell: Any,
        route_key: str,
        inner_no_overrides_executor: Callable[..., Any],
        execute_with_overrides: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build a cold overrides door that compiles the real overrides door lazily.

    Purpose:
        Defer the overrides door compile from FIRST MELD to FIRST OVERRIDE
        MELD. The site-plan runtime itself is built at hydration (its normal
        plan is the inner executor since S2b-2), so only the door is deferred.

    Contract:
        - Zero work at build time: closure construction only.
        - The first override call compiles exactly once (leader under the
          lock, followers wait) the real route-keyed overrides door through
          the same door compiler the eager path used, then swaps it into the
          spell's currently published `CreationContext` `_overrides_executor`
          slot (self-replacing slot contract), so the shim vanishes from later
          override melds.
        - When no context is published (publish=False cache loads), the shim
          keeps delegating correctly; only the swap optimization is skipped.

    Args:
        root_spell:
            Live root spell whose published context receives the hot swap.
        route_key:
            Family route key for the door compiler.
        inner_no_overrides_executor:
            The normal plan the overrides door falls back to for empty payloads.
        execute_with_overrides:
            The runtime's `(meld, overrides) -> instance` dispatcher.
'''

GEN_LAZY_BODY_OLD = '''            real_door = door_cell[0]
            if real_door is not None:
                return real_door
            resolver = SpellbookBindingResolver(spell=root_spell)
            execute_with_overrides = _hydrate_overrides_runtime(
                manifest=manifest,
                resolver=resolver,
                root_spell=root_spell,
                inner_no_overrides_executor=inner_no_overrides_executor,
            )
            resolver.cleanup()
            real_door = compile_creation_context_hooks_overrides_only_executor(
'''
GEN_LAZY_BODY_NEW = '''            real_door = door_cell[0]
            if real_door is not None:
                return real_door
            real_door = compile_creation_context_hooks_overrides_only_executor(
'''

# --------------------------------------------------------------------------------------------------------------------
# many_only_hydrator.py
# --------------------------------------------------------------------------------------------------------------------

MO_DOC_OLD = '''The no-overrides lane hydrates through the many_only compiler's public
Codegen IR entrypoint (the manifest stores that IR verbatim). The override
runtime is `SitePlanOverrideRuntime` over those same rows: one compiled plan
per override key set, built at first use (2026-09-26), as in the generalized
family.
'''
MO_DOC_NEW = '''Both lanes run on `SitePlanOverrideRuntime` over the manifest's no-overrides
rows (the Codegen IR the manifest stores verbatim): its normal plan (the empty
key set) is the inner no-overrides executor since S2b-2 (2026-09-26), and it
compiles one plan per override key set at first use, as in the generalized
family.
'''

MO_IMPORT_OLD = '''    _hydrate_steps_from_rows,
    _resolve_root_instance_key,
    compile_no_overrides_codegen_creation_executor,
)
'''
MO_IMPORT_NEW = '''    _hydrate_steps_from_rows,
    _resolve_root_instance_key,
)
'''

MO_HYD_OLD = '''    inner_no_overrides_executor = compile_no_overrides_codegen_creation_executor(
        codegen_ir={
            "steps_rows": no_overrides_payload["steps_rows"],
            "root_spell_id": no_overrides_payload["root_spell_id"],
            "transient_schema": no_overrides_payload["transient_schema"],
        },
        spell_lookup=spell_lookup,
    )
    if inner_no_overrides_executor is None:
        raise RuntimeError(
            "many_only manifest hydration produced no no-overrides executor."
        )

    execute_with_overrides = _hydrate_overrides_runtime(
        no_overrides_payload=no_overrides_payload,
        spell=spell,
        spell_lookup=spell_lookup,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
'''
MO_HYD_NEW = '''    # One runtime serves both lanes (S2b-2, 2026-09-26): its normal plan is the
    # inner no-overrides executor; override key sets compile on it.
    site_plan_runtime = _build_site_plan_runtime(
        no_overrides_payload=no_overrides_payload,
        spell=spell,
        spell_lookup=spell_lookup,
    )
    inner_no_overrides_executor = site_plan_runtime.execute_normal
    execute_with_overrides = site_plan_runtime.execute_with_overrides
'''

MO_RT_OLD = '''def _hydrate_overrides_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell: Any,
        spell_lookup: Dict[str, Any],
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build the many_only override runtime: one compiled plan per override key set.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's own
          row hydration, so override plans and the normal lane see the same
          steps (design v2 S3a). The manifest's overrides payload is not read.
        - Returns `SitePlanOverrideRuntime.execute_with_overrides`; plans
          compile lazily per key set at meld time, and the runtime lives as
          long as the returned callable (the lazy override door holds it).

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell:
            Live root spell.
        spell_lookup:
            Live spell per step spell id (already resolved for the no-overrides
            lane).
        inner_no_overrides_executor:
            The lane's inner `(meld) -> instance` executor.

    Raises:
        RuntimeError:
            When no step carries the root instance key.

    Returns:
        Callable[..., Any]:
            `(meld, overrides) -> instance`.
    """
'''
MO_RT_NEW = '''def _build_site_plan_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell: Any,
        spell_lookup: Dict[str, Any],
) -> SitePlanOverrideRuntime:
    """
    Build the many_only site-plan runtime: the normal plan now, override plans per key set later.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's own
          row hydration, so normal and override plans see the same steps
          (design v2 S3a, S2b-2). The manifest's overrides payload is not read.
        - The runtime builds its site graph and normal plan at construction
          (first meld); it lives as long as the executors it hands out.

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell:
            Live root spell.
        spell_lookup:
            Live spell per step spell id.

    Raises:
        RuntimeError:
            When no step carries the root instance key, or the site graph
            cannot be built.

    Returns:
        SitePlanOverrideRuntime: The runtime.
    """
'''

MO_RT_TAIL_OLD = '''    runtime = SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_many_only_row(row) for row in rows),
        root_spell=spell,
        root_instance_key=root_instance_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )
    return runtime.execute_with_overrides
'''
MO_RT_TAIL_NEW = '''    return SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_many_only_row(row) for row in rows),
        root_spell=spell,
        root_instance_key=root_instance_key,
    )
'''

EDITS = {
    LOWERING: [
        ("replace", EMIT_OLD, EMIT_NEW),
        ("replace", EMIT_BODY_OLD, EMIT_BODY_NEW),
        ("replace", EMISSION_CALL_OLD, EMISSION_CALL_NEW),
        ("replace", EMISSION_DOC_OLD, EMISSION_DOC_NEW),
        ("replace", SLOTS_OLD, SLOTS_NEW),
        ("replace", INIT_SIG_OLD, INIT_SIG_NEW),
        ("replace", INIT_ARGS_OLD, INIT_ARGS_NEW),
        ("replace", INIT_TAIL_OLD, INIT_TAIL_NEW),
        ("replace", CLEANUP_OLD, CLEANUP_NEW),
        ("replace", RENDER_DOC_OLD, RENDER_DOC_NEW),
        ("replace", RENDER_DEF_OLD, RENDER_DEF_NEW),
        ("replace", HIT_ARGS_OLD, HIT_ARGS_NEW),
        ("replace", MISS_PARAMS_OLD, MISS_PARAMS_NEW),
    ],
    RUNTIME: [
        ("replace", RT_DOC_OLD, RT_DOC_NEW),
        ("replace", RT_DOC2_OLD, RT_DOC2_NEW),
        ("replace", RT_LIFE_OLD, RT_LIFE_NEW),
        ("replace", RT_SUBSYS_OLD, RT_SUBSYS_NEW),
        ("replace", RT_SLOTS_OLD, RT_SLOTS_NEW),
        ("replace", RT_INIT_OLD, RT_INIT_NEW),
        ("replace", RT_FIELDS_OLD, RT_FIELDS_NEW),
        ("replace", RT_CLEANUP_OLD, RT_CLEANUP_NEW),
        ("replace", RT_DISPATCH_OLD, RT_DISPATCH_NEW),
        ("replace", RT_GRAPH_OLD, RT_GRAPH_NEW),
        ("replace", RT_COMPILE_OLD, RT_COMPILE_NEW),
        ("replace", RT_TAIL_OLD, RT_TAIL_NEW),
    ],
    GENERALIZED: [
        ("replace", GEN_DOC_OLD, GEN_DOC_NEW),
        ("replace", GEN_IMPORT_OLD, GEN_IMPORT_NEW),
        ("replace", GEN_HYD_OLD, GEN_HYD_NEW),
        ("replace", GEN_OVDOOR_CALL_OLD, GEN_OVDOOR_CALL_NEW),
        ("cut", GEN_RUNTIME_START, GEN_RUNTIME_STOP),
        ("replace", GEN_RUNTIME_STOP, GEN_RUNTIME_NEW + GEN_RUNTIME_STOP),
        ("replace", GEN_LAZY_SIG_OLD, GEN_LAZY_SIG_NEW),
        ("replace", GEN_LAZY_BODY_OLD, GEN_LAZY_BODY_NEW),
    ],
    MANY_ONLY: [
        ("replace", MO_DOC_OLD, MO_DOC_NEW),
        ("replace", MO_IMPORT_OLD, MO_IMPORT_NEW),
        ("replace", MO_HYD_OLD, MO_HYD_NEW),
        ("replace", MO_RT_OLD, MO_RT_NEW),
        ("replace", MO_RT_TAIL_OLD, MO_RT_TAIL_NEW),
    ],
}

STALE = {
    LOWERING: ('"meld", "ov", store',),
    RUNTIME: ("_inner_no_overrides_executor", "inner_no_overrides_executor="),
    GENERALIZED: ("_hydrate_overrides_runtime", "hydrate_no_overrides_executor("),
    MANY_ONLY: ("_hydrate_overrides_runtime", "compile_no_overrides_codegen_creation_executor"),
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        newline = "\r\n" if "\r\n" in data else "\n"
        for edit in edits:
            if edit[0] == "cut":
                # The engine searches a cut's stop verbatim; match the file's line ending.
                edit = ("cut", edit[1].replace("\n", newline), edit[2].replace("\n", newline))
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        for stale in STALE[rel]:
            if stale in data:
                raise SystemExit(f"{rel}: stale reference left: {stale}")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
