import threading
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
    SiteInstanceKey,
    SpellSiteGraphAnalysis,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.executor_code_cache import get_or_compile_executor_code
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
        OverrideKeyResolution,
    )

PlanCallable = Callable[[Any, Dict[str, Any]], Any]


class SitePlanOverrideRuntime(Cleanable):
    """
    Per-root override runtime: one compiled plan per override key set.

    Purpose:
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
        - Per call: one key tuple, one dict read, one call. A miss compiles the
          key set under `_compile_lock` (resolution, emission, code-object
          cache, exec; no user code runs) and stores it; at `MAX_PLANS` stored
          key sets the oldest is evicted first.
        - A key set containing `"__args__"` maps to an arity dispatcher that
          compiles one plan per `__args__` length. `__args__` None counts as
          absent; a value that is not a list or tuple raises today's error.
        - Key errors raise `MeldExecutionError("Failed to apply overrides.")`
          chained from the resolver's error, and are not stored.
        - A key set with no winning operand (for example `__args__=[]`) runs
          the normal plan.
        - The site graph is built once, at construction, and kept for later
          key sets.

    Threading:
        Plan lookups are lock-free dict reads. Compiles and evictions hold
        `_compile_lock`; a thread that finds a plan compiled while it waited
        uses it. Emitted plans take the normal lane's build locks.

    Lifecycle / Cleanup:
        Built by the family hydrator at first meld and kept alive by the
        executors it hands out (the plans' namespaces reference its steps), for
        the executor lifetime. `cleanup()` is idempotent: it clears the plans,
        cleans the site graph and every step it owns (built or masked), then
        deletes its fields; plans called after it are invalid. The root spell
        is borrowed.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Built by `many_only_hydrator._build_site_plan_runtime` and
        `generalized_hydrator._build_site_plan_runtime`.

    System Context:
        Phase-11 override lane (design v2 step S3); CreationContext override
        slots and doors are unchanged.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Key-set dispatcher for override melds: lazily compiled
        per-key-set plans over the lane's no-overrides steps.
    """

    __slots__ = Cleanable.__slots__ + [
        "execute_with_overrides",
        "execute_normal",
        "_steps",
        "_root_spell",
        "_root_spell_id",
        "_root_instance_key",
        "_plans",
        "_compile_lock",
        "_site_graph",
        "_owned_masked_steps",
    ]

    MAX_PLANS: ClassVar[int] = 256
    ARGS_KEY: ClassVar[str] = "__args__"

    def __init__(
            self,
            *,
            steps: Tuple[SitePlanStep, ...],
            root_spell: Spell,
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

        Returns:
            None.
        """
        super().__init__()
        if not any(step.instance_key == root_instance_key for step in steps):
            raise RuntimeError(
                f"Override runtime has no step for root instance {root_instance_key!r}."
            )
        self._steps: Tuple[SitePlanStep, ...] = steps
        self._root_spell: Spell = root_spell
        self._root_spell_id: str = root_spell.spell_index.selected_spell_id or root_spell.spell_id
        self._root_instance_key: SiteInstanceKey = root_instance_key
        self._plans: Dict[Tuple[str, ...], PlanCallable] = {}
        self._compile_lock: threading.Lock = threading.Lock()
        self._site_graph: Optional[SpellSiteGraphAnalysis] = None
        self._owned_masked_steps: List[SitePlanStep] = []
        self.execute_normal: Callable[[Any], Any] = self._compile_normal_plan()
        self.execute_with_overrides: Callable[[Any, Optional[Dict[str, Any]]], Any] = (
            self._build_dispatcher()
        )

    def cleanup(self) -> None:
        """
        Release plans, the site graph and owned steps, then delete every field.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._compile_lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._plans.clear()
            if self._site_graph is not None:
                self._site_graph.cleanup()
            for step in self._owned_masked_steps:
                step.cleanup()
            self._owned_masked_steps.clear()
            for step in self._steps:
                step.cleanup()
        del self.execute_with_overrides
        del self.execute_normal
        del self._steps
        del self._root_spell
        del self._root_spell_id
        del self._root_instance_key
        del self._plans
        del self._site_graph
        del self._owned_masked_steps
        del self._compile_lock

    def _build_dispatcher(self) -> Callable[[Any, Optional[Dict[str, Any]]], Any]:
        """
        Return the per-call dispatcher bound to this runtime's plan table.

        Contract:
            The returned function reads the plan table and the compile entry as
            default arguments (fast locals); it holds no lock on a hit.
        """

        def execute_with_overrides(
                meld: Any,
                overrides: Optional[Dict[str, Any]],
                plans: Dict[Tuple[str, ...], PlanCallable] = self._plans,
                plan_for: Callable[[Dict[str, Any]], PlanCallable] = self._plan_for_payload,
                inner: Callable[[Any], Any] = self.execute_normal,
        ) -> Any:
            if overrides is None:
                return inner(meld)
            plan = plans.get(tuple(overrides))
            if plan is None:
                plan = plan_for(overrides)
            return plan(meld, overrides)

        return execute_with_overrides

    def _plan_for_payload(self, overrides: Dict[str, Any]) -> PlanCallable:
        """
        Return the stored plan for this payload's key set, compiling it on a miss.

        Raises:
            MeldExecutionError: When a key does not resolve (not stored).
        """
        self.check_cleaned()
        keys = tuple(overrides)
        with self._compile_lock:
            plan = self._plans.get(keys)
            if plan is not None:
                return plan
            if self.ARGS_KEY in keys:
                plan = self._arity_dispatcher(keys)
            else:
                plan = self._compile_plan(keys, 0)
            plans = self._plans
            while len(plans) >= self.MAX_PLANS:
                plans.pop(next(iter(plans)))
            plans[keys] = plan
            return plan

    def _arity_dispatcher(self, keys: Tuple[str, ...]) -> PlanCallable:
        """
        Return a plan that selects a per-arity plan from `len(ov["__args__"])`.

        Contract:
            Resolves the key set once for arity 0 first, so bad keys fail
            before any dispatcher is stored.
        """
        by_arity: Dict[int, PlanCallable] = {0: self._compile_plan(keys, 0)}
        root_spell = self._root_spell
        root_spell_id = self._root_spell_id
        compile_arity = self._compile_arity

        def arity_plan(
                meld: Any,
                ov: Dict[str, Any],
                by_arity: Dict[int, PlanCallable] = by_arity,
        ) -> Any:
            raw_args = ov["__args__"]
            if raw_args is None:
                arity = 0
            elif isinstance(raw_args, (tuple, list)):
                arity = len(raw_args)
            else:
                raise MeldExecutionError(
                    spell_id=root_spell_id,
                    spell_name=root_spell.spell_name,
                    message="__args__ override must be a list or tuple.",
                )
            plan = by_arity.get(arity)
            if plan is None:
                plan = compile_arity(keys, arity, by_arity)
            return plan(meld, ov)

        return arity_plan

    def _compile_arity(
            self,
            keys: Tuple[str, ...],
            arity: int,
            by_arity: Dict[int, PlanCallable],
    ) -> PlanCallable:
        """
        Compile and store one per-arity plan under the compile lock.
        """
        self.check_cleaned()
        with self._compile_lock:
            plan = by_arity.get(arity)
            if plan is None:
                plan = self._compile_plan(keys, arity)
                by_arity[arity] = plan
            return plan

    def _resolve(self, keys: Tuple[str, ...], arity: int) -> OverrideKeyResolution:
        """
        Resolve one key set, wrapping key errors as today's override error.

        Raises:
            MeldExecutionError: "Failed to apply overrides.", chained from the cause.
        """
        try:
            return OverrideKeyResolver.resolve(self._site_graph_or_build(), keys, arity)
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=self._root_spell_id,
                spell_name=self._root_spell.spell_name,
                message="Failed to apply overrides.",
                inner=exc,
            ) from exc

    def _site_graph_or_build(self) -> SpellSiteGraphAnalysis:
        """
        Return the site graph, building it on first use.

        Contract:
            Called from construction (before the runtime is shared) or under the
            compile lock; since S2b-2 construction always builds it.
        """
        site_graph = self._site_graph
        if site_graph is None:
            topology_for = self._root_spell._spellbook._spell_system_states.get_local_topology_by_id
            site_graph = SitePlanLowering.build_site_graph(
                root_spell_id=self._root_instance_key[0],
                root_instance_key=self._root_instance_key,
                steps=self._steps,
                topology_for=topology_for,
            )
            self._site_graph = site_graph
        return site_graph

    def _compile_plan(self, keys: Tuple[str, ...], arity: int) -> PlanCallable:
        """
        Compile one plan for (keys, arity) (caller holds the compile lock).

        Returns:
            PlanCallable: The emitted plan, or an inner-executor adapter when the
                key set has no winning operand.
        """
        resolution = self._resolve(keys, arity)
        if not resolution.winners:
            inner = self.execute_normal

            def normal_plan(meld: Any, ov: Dict[str, Any], inner: Callable[[Any], Any] = inner) -> Any:
                return inner(meld)

            return normal_plan
        site_graph = self._site_graph_or_build()
        source, namespace, masked = SitePlanLowering.emit(
            steps=self._steps,
            site_graph=site_graph,
            resolution=resolution,
            root_instance_key=self._root_instance_key,
            root_spell_id=self._root_spell_id,
            root_spell_name=self._root_spell.spell_name,
            arity=arity,
        )
        self._owned_masked_steps.extend(masked)
        code = get_or_compile_executor_code(source=source, source_name=SitePlanLowering.PLAN_SOURCE_NAME)
        exec(code, namespace)
        plan: PlanCallable = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
        return plan

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
