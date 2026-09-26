from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, FrozenSet, List, Optional, Set, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
    SpellInjectionAnalysis,
    SpellInjectionInstanceSpec,
    SpellInjectionParamSource,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
    SiteInstanceKey,
    SpellSiteGraphAnalysis,
    SpellSiteParam,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_site_graph_processor_strategy import (
    SpellSiteGraphProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_kwargs_no_overrides,
    _construct_spell_instance,
    _raise_meld_construction_error,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
        OverrideKeyResolution,
    )
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
        SpellLocalTopology,
    )

DependencyOrder = Tuple[Tuple[str, Tuple[SiteInstanceKey, ...]], ...]


class SitePlanStep(Cleanable):
    """
    One family-neutral construction step read by the key-set plan lowering.

    Purpose:
        The many_only and generalized families hydrate their no-overrides step
        rows into different objects (many_only rows carry no existence because
        the family is all-many). This view gives the lowering one shape. It is
        also a valid `plan_step` for the no-overrides generic helpers
        (`_construct_spell_instance`, `_build_kwargs_no_overrides`), which read
        exactly these attributes.

    Contract:
        - Fields are copied from the family row when the view is built; `spell`
          and the contract payload dict are borrowed references.
        - `dependency_resolution_order` holds `(param_name, dependency_keys)` in
          the family's order, each key a `(spell_id, path_id)` tuple.

    Lifecycle / Cleanup:
        Owned by the `SitePlanOverrideRuntime` that built it (directly, or as a
        masked copy for one plan). `cleanup()` is idempotent and deletes every
        field; the spell and the payload dict are borrowed and never cleaned here.

    Registration:
        MELDER KERNEL - internal lowering input; never bound as a spell.

    Subsystem Context:
        Input rows of `SitePlanLowering`, built by the family hydrators.

    System Context:
        Phase-11 override lane (design v2 step S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Family-neutral step view (instance key, spell, existence, dependency
        order, collection params, contract payload, lock hint) for key-set plans.
    """

    __slots__ = Cleanable.__slots__ + [
        "instance_key",
        "spell",
        "existence",
        "dependency_resolution_order",
        "collection_param_names",
        "uses_positional_override",
        "contract_positional_override",
        "has_contract_payload",
        "contract_payload",
        "use_spell_lock_hint",
    ]

    def __init__(
            self,
            *,
            instance_key: SiteInstanceKey,
            spell: Spell,
            existence: Existence,
            dependency_resolution_order: DependencyOrder,
            collection_param_names: FrozenSet[str],
            uses_positional_override: bool,
            contract_positional_override: Optional[Any],
            has_contract_payload: bool,
            contract_payload: Optional[Dict[str, Any]],
            use_spell_lock_hint: bool,
    ) -> None:
        """
        Store one step view.

        Args:
            instance_key: `(spell_id, path_id)`; `path_id` is None for shared existences.
            spell: The step's Spell (borrowed).
            existence: The step's Existence.
            dependency_resolution_order: `(param_name, dependency_keys)` pairs.
            collection_param_names: Parameters that always receive a list.
            uses_positional_override: Whether a contract payload carries `__args__`.
            contract_positional_override: Contract positional payload, or None.
            has_contract_payload: Whether a contract payload applies.
            contract_payload: Contract payload values by parameter (borrowed), or None.
            use_spell_lock_hint: Whether a `unique` build holds `Spell._lock`.

        Returns:
            None.
        """
        super().__init__()
        self.instance_key: SiteInstanceKey = instance_key
        self.spell: Spell = spell
        self.existence: Existence = existence
        self.dependency_resolution_order: DependencyOrder = dependency_resolution_order
        self.collection_param_names: FrozenSet[str] = collection_param_names
        self.uses_positional_override: bool = uses_positional_override
        self.contract_positional_override: Optional[Any] = contract_positional_override
        self.has_contract_payload: bool = has_contract_payload
        self.contract_payload: Optional[Dict[str, Any]] = contract_payload
        self.use_spell_lock_hint: bool = use_spell_lock_hint

    def cleanup(self) -> None:
        """
        Delete every field; the spell and the payload are borrowed and not cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.instance_key
        del self.spell
        del self.existence
        del self.dependency_resolution_order
        del self.collection_param_names
        del self.uses_positional_override
        del self.contract_positional_override
        del self.has_contract_payload
        del self.contract_payload
        del self.use_spell_lock_hint

    @staticmethod
    def _normalized_order(dependency_resolution_order: Any) -> DependencyOrder:
        """
        Return `(param, keys)` pairs with every key as a 2-tuple.
        """
        return tuple(
            (param_name, tuple((key[0], key[1]) for key in dependency_keys))
            for param_name, dependency_keys in dependency_resolution_order
        )

    @classmethod
    def from_generalized_row(cls, row: Any) -> SitePlanStep:
        """
        Build the view from one hydrated generalized step row.

        Args:
            row: One step from the generalized compiler's `_hydrate_steps_from_rows`
                (or any object with the same attributes, such as a runtime row).

        Returns:
            SitePlanStep: The view.
        """
        return cls(
            instance_key=(row.instance_key[0], row.instance_key[1]),
            spell=row.spell,
            existence=row.existence,
            dependency_resolution_order=cls._normalized_order(row.dependency_resolution_order),
            collection_param_names=frozenset(row.collection_param_names),
            uses_positional_override=bool(row.uses_positional_override),
            contract_positional_override=row.contract_positional_override,
            has_contract_payload=bool(row.has_contract_payload),
            contract_payload=row.contract_payload,
            use_spell_lock_hint=bool(row.use_spell_lock_hint),
        )

    @classmethod
    def from_many_only_row(cls, row: Any) -> SitePlanStep:
        """
        Build the view from one hydrated many_only step row.

        Contract:
            Every many_only step is `Existence.many` (phase-10 discovery admits
            only all-many graphs to this family), stores into the innermost
            scope and takes no build lock.

        Args:
            row: One step from the many_only compiler's `_hydrate_steps_from_rows`.

        Returns:
            SitePlanStep: The view.
        """
        return cls(
            instance_key=(row.instance_key[0], row.instance_key[1]),
            spell=row.spell,
            existence=Existence.many,
            dependency_resolution_order=cls._normalized_order(row.dependency_resolution_order),
            collection_param_names=frozenset(row.collection_param_names),
            uses_positional_override=bool(row.uses_positional_override),
            contract_positional_override=row.contract_positional_override,
            has_contract_payload=bool(row.has_contract_payload),
            contract_payload=row.contract_payload,
            use_spell_lock_hint=False,
        )

    def masked(self, overridden: FrozenSet[str], drop_contract_positional: bool) -> SitePlanStep:
        """
        Return a copy without the overridden parameters' dependency and contract operands.

        Purpose:
            The generic construct path builds kwargs with the no-overrides
            builder; removing overridden parameters keeps it from reading
            dependencies the plan never built. Supplied values are applied after.

        Args:
            overridden: Parameter names that receive supplied values.
            drop_contract_positional: True when the root `__args__` is supplied, so
                a contract positional payload must not compete with it.

        Returns:
            SitePlanStep: The masked copy (owned by the caller).
        """
        contract_payload = self.contract_payload
        if contract_payload:
            contract_payload = {
                name: value for name, value in contract_payload.items() if name not in overridden
            }
        contract_positional_override = self.contract_positional_override
        uses_positional_override = self.uses_positional_override
        if drop_contract_positional:
            contract_positional_override = None
            uses_positional_override = False
        return SitePlanStep(
            instance_key=self.instance_key,
            spell=self.spell,
            existence=self.existence,
            dependency_resolution_order=tuple(
                (name, keys) for name, keys in self.dependency_resolution_order if name not in overridden
            ),
            collection_param_names=self.collection_param_names,
            uses_positional_override=uses_positional_override,
            contract_positional_override=contract_positional_override,
            has_contract_payload=bool(contract_payload),
            contract_payload=contract_payload,
            use_spell_lock_hint=self.use_spell_lock_hint,
        )


class SitePlanRuntimeHelpers:
    """
    Out-of-line helpers called by emitted key-set plans.

    Purpose:
        Hold the cold-path helpers a plan reads from its namespace: the
        generic construct with supplied values, the P2 refusal and the
        equal-rank conflict guard. None of them runs on a direct-call step.

    Contract:
        - Stateless static methods; the class is never instantiated.
        - Error types and messages match today's override lane.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Referenced by `SitePlanLowering` emission namespaces.

    System Context:
        Phase-11 override lane (design v2 step S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Generic construct with supplied values, P2 refusal and the E1
        conflict guard for emitted key-set plans.
    """

    __slots__ = ()

    SCALAR_TYPES: ClassVar[Tuple[type, ...]] = (int, float, str, bool, bytes, type(None))

    @staticmethod
    def construct_with_supplied_values(
            *,
            plan_step: SitePlanStep,
            instance_results: Dict[SiteInstanceKey, Any],
            supplied_values: Dict[str, Any],
    ) -> Any:
        """
        Construct one masked step with supplied values applied last (generic path).

        Contract:
            - Kwargs come from the no-overrides builder on the masked step (its
              overridden parameters removed), then supplied values overwrite
              them: supplied > contract payload > dependency.
            - `__args__` in `supplied_values` is the root positional payload.
            - Existing creations return their bound object and non-callable
              spells return the spell object, as the no-overrides helper does.

        Args:
            plan_step: The masked step.
            instance_results: Values of the plan's steps by instance key.
            supplied_values: Supplied values by parameter name (plus `__args__`).

        Raises:
            MeldExecutionError: When `__args__` is not a list or tuple, or the
                constructor fails (through `_raise_meld_construction_error`).
            UnresolvedInputError: When the failed call left out an unresolved input.

        Returns:
            Any: The constructed (or bound) instance.
        """
        spell = plan_step.spell
        if spell.is_existing_creation or not (
                spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell
        ):
            return _construct_spell_instance(plan_step=plan_step, instance_results=instance_results)
        kwargs = _build_kwargs_no_overrides(plan_step=plan_step, instance_results=instance_results)
        kwargs.update(supplied_values)
        raw_args = kwargs.pop("__args__", None)
        if raw_args is None:
            args: Tuple[Any, ...] = ()
        elif isinstance(raw_args, (tuple, list)):
            args = tuple(raw_args)
        else:
            raise MeldExecutionError(
                spell_id=spell.spell_index.selected_spell_id,
                spell_name=spell.spell_name,
                message="__args__ override must be a list or tuple.",
            )
        try:
            return spell.spell(*args, **kwargs)
        except Exception as exc:
            _raise_meld_construction_error(spell, exc, tuple(kwargs), len(args))

    @staticmethod
    def raise_existing_override(spell: Spell, root_spell_id: str) -> None:
        """
        Raise today's error for a supplied value on a stored shared instance (P2).

        Args:
            spell: The stored shared site's spell.
            root_spell_id: Selected id of the melded root.

        Raises:
            MeldExecutionError: Always; the root message for the root spell,
                otherwise the instance message (texts unchanged).
        """
        spell_id = spell.spell_index.selected_spell_id
        if spell_id == root_spell_id:
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell.spell_name,
                node_id=spell_id,
                message=(
                    "Overrides were supplied for a root spell that already exists. "
                    "Shared instances cannot be overridden after creation."
                ),
            )
        raise MeldExecutionError(
            spell_id=spell_id,
            spell_name=spell.spell_name,
            node_id=spell_id,
            message=(
                "Overrides were supplied for a spell instance that already exists. "
                "Shared instances cannot be overridden after creation."
            ),
        )

    @staticmethod
    def conflict_guard(
            first: Any,
            second: Any,
            target: str,
            root_spell_id: str,
            root_spell_name: str,
    ) -> None:
        """
        Refuse two equal-rank keys that supply different values to one parameter (E1).

        Contract:
            The same object is accepted; plain scalars of one type that compare
            equal are accepted. Nothing else about a supplied value is read.

        Args:
            first: Value of the winning key.
            second: Value of the other equal-rank key.
            target: `spell_id.param` description of the parameter.
            root_spell_id: Selected id of the melded root.
            root_spell_name: Name of the melded root.

        Raises:
            MeldExecutionError: "Failed to apply overrides.", chained from a
                RuntimeError naming the parameter, when the values differ.
        """
        if first is second:
            return
        first_type = type(first)
        if first_type is type(second) and first_type in SitePlanRuntimeHelpers.SCALAR_TYPES:
            if first == second:
                return
        conflict = RuntimeError(
            f"Conflicting overrides for socket {target}: multiple rules with the same specificity."
        )
        raise MeldExecutionError(
            spell_id=root_spell_id,
            spell_name=root_spell_name,
            message="Failed to apply overrides.",
            inner=conflict,
        ) from conflict


class SitePlanLowering:
    """
    Build the site graph from steps, compute demand and emit one key-set plan.

    Purpose:
        The shared lowering of design v2 for the override lane: given the
        lane's no-overrides steps and one resolved key set, emit Python that
        builds only the demanded steps and reads supplied values by literal key
        (`ov["a"]`, `args[0]`). A shared site is an inline hit read plus an
        out-of-line miss function, and the sites only it needs are built inside
        that miss, so a stored shared site's children are never built (S2b-1,
        design L1/L3, B2).

    Contract:
        - Steps keep the family's providers-first order; a step is emitted only
          when its instance key is demanded (reachable from the root without
          crossing a parameter that has a winning override).
        - Store routing, reuse reads, build guards and publication mirror the
          live generalized manifest lowering for each existence.
        - A shared step with a winning override raises today's "already exists"
          error when its instance is stored (P2).
        - Steps that are not a plain call of a class, method or lambda spell
          (existing creations, non-callable spells, contract payloads, a
          parameter that cannot be passed in order) use the generic helpers;
          with supplied values the step is masked and the values applied last.
        - Emission is a pure function of its inputs; the returned source names
          no identities, so equal shapes share one code object.

    Threading:
        Compile-time only; emitted plans take the same locks as the normal lane.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Used by `SitePlanOverrideRuntime` (shared_assets).

    System Context:
        Phase-11 override lane (design v2 step S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Site graph from steps, demand walk and key-set plan source emission
        for override melds.
    """

    __slots__ = ()

    PLAN_FUNCTION_NAME: ClassVar[str] = "_site_plan_executor"
    PLAN_SOURCE_NAME: ClassVar[str] = "<melder_site_plan_executor>"
    POSITIONAL_KINDS: ClassVar[Tuple[str, ...]] = ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
    VARIADIC_KINDS: ClassVar[Tuple[str, ...]] = ("VAR_POSITIONAL", "VAR_KEYWORD")

    @staticmethod
    def build_site_graph(
            *,
            root_spell_id: str,
            root_instance_key: SiteInstanceKey,
            steps: Tuple[SitePlanStep, ...],
            topology_for: Callable[[str], Optional[SpellLocalTopology]],
    ) -> SpellSiteGraphAnalysis:
        """
        Build the S1 site graph from no-overrides steps and live Phase-3 topologies.

        Contract:
            - Every step becomes an injection spec whose dependency sources are
              its dependency order; the S1 builder then produces the section, so
              fresh and cache-hit plans read one structure.
            - The temporary injection section is cleaned before returning.

        Args:
            root_spell_id: Selected root spell id.
            root_instance_key: Instance key of the root step.
            steps: The lane's no-overrides steps.
            topology_for: Spell id -> live Phase-3 topology (or None).

        Raises:
            RuntimeError: When a reachable instance key has no step.

        Returns:
            SpellSiteGraphAnalysis: The site graph (the caller owns cleanup).
        """
        specs: Dict[SiteInstanceKey, SpellInjectionInstanceSpec] = {}
        for step in steps:
            sources: Dict[str, SpellInjectionParamSource] = {}
            for param_name, dependency_keys in step.dependency_resolution_order:
                sources[param_name] = SpellInjectionParamSource(
                    kind="dependency",
                    dependency_keys=dependency_keys,
                    is_collection=param_name in step.collection_param_names,
                )
            specs[step.instance_key] = SpellInjectionInstanceSpec(
                param_sources=sources,
                allow_list_aggregation=False,
                uses_positional_override=step.uses_positional_override,
            )
        injection = SpellInjectionAnalysis(
            root_spell_id=root_spell_id,
            root_instance_key=root_instance_key,
            instance_specs_by_instance_key=specs,
        )
        try:
            return SpellSiteGraphProcessorStrategy.build_site_graph(
                root_instance_key=root_instance_key,
                injection_shape=injection,
                topology_for=topology_for,
            )
        finally:
            injection.cleanup()

    @staticmethod
    def demanded_instance_keys(
            site_graph: SpellSiteGraphAnalysis,
            resolution: OverrideKeyResolution,
    ) -> Set[SiteInstanceKey]:
        """
        Return the instance keys a key set needs (P1 demand walk from the root).

        Contract:
            A parameter with a winning override (including `__args__`) demands
            nothing; every other parameter demands all its dependency sites.

        Returns:
            Set[SiteInstanceKey]: Demanded instance keys, root included.
        """
        winners = resolution.winners
        sites = site_graph.sites
        demanded: Set[int] = {site_graph.root_site_index}
        stack: List[int] = [site_graph.root_site_index]
        while stack:
            site = sites[stack.pop()]
            for param in site.params:
                if (site.index, param.name) in winners:
                    continue
                for dependency in param.dependency_sites:
                    if dependency not in demanded:
                        demanded.add(dependency)
                        stack.append(dependency)
        return {sites[index].instance_key for index in demanded}

    @classmethod
    def emit(
            cls,
            *,
            steps: Tuple[SitePlanStep, ...],
            site_graph: SpellSiteGraphAnalysis,
            resolution: OverrideKeyResolution,
            root_instance_key: SiteInstanceKey,
            root_spell_id: str,
            root_spell_name: str,
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

        Returns:
            Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
                Identity-free source, its namespace, and the masked steps the
                namespace references (owned by the caller).
        """
        if normal_mode and (resolution.winners or resolution.conflicts or arity):
            raise RuntimeError("A normal-mode plan is only emitted for a key set that supplies nothing.")
        demanded = cls.demanded_instance_keys(site_graph, resolution)
        kept = tuple(step for step in steps if step.instance_key in demanded)
        if not any(step.instance_key == root_instance_key for step in kept):
            raise RuntimeError(
                f"Key-set plan has no step for root instance {root_instance_key!r}."
            )
        emission = SitePlanEmission(
            steps=kept,
            site_graph=site_graph,
            resolution=resolution,
            root_instance_key=root_instance_key,
            root_spell_id=root_spell_id,
            root_spell_name=root_spell_name,
            arity=arity,
            normal_mode=normal_mode,
        )
        try:
            return emission.render()
        finally:
            emission.cleanup()


class SitePlanEmission(Cleanable):
    """
    Mutable emission state for one key-set plan.

    Purpose:
        Accumulate source lines and the namespace for one plan while
        `SitePlanLowering.emit` walks the kept steps.

    Contract:
        - Local `v{n}` holds kept step n's value; step constants and helpers are
          globals of the plan's own namespace (the plan is exec'd into it), as
          the inner no-overrides executor reads module globals. Default
          arguments were used until 2026-09-26: they cost one fill per constant
          on every call, hundreds on deep graphs. Spells ride one `spells`
          tuple read only on cold paths (errors, shared-site routing for
          `unique`, locks). No namespace name is assigned in the plan body.
        - Dict mode (`instance_results`) is emitted only when a generic step
          needs dependency values by instance key; misses then receive the dict
          and record their sites in it.
        - Placement (2026-09-26): every kept step lives at top level or inside
          exactly one shared site's `_miss{i}`. The root is top level; a many
          site lives where its one consumer is built (inside the consumer's miss
          when the consumer is shared); a shared site lives at the lowest context
          common to all its consumers; a shared site with a winning override is
          pinned to top level so its P2 refusal and build are exactly today's.
          Within a context steps keep the family's providers-first order.
        - Normal mode (S2b-2, 2026-09-26) drops `ov` from the plan and from
          every miss signature and call; nothing else changes.
        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],
          v...)`: the outer values its sites read, in step order. It builds the
          sites placed inside it first, then takes the site's build guard for
          recheck, construction and publication only, and returns the site's
          value. So a plan never holds a build lock while another site's
          constructor runs (today's locking; design risk R2 retired
          2026-09-26); a cold race may build and drop the loser's children, as
          the straight-line lowering does.

    Lifecycle / Cleanup:
        Created and cleaned inside one `emit` call. The namespace and masked
        steps it produced are handed to the caller before cleanup and are not
        touched by it.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Private worker of `SitePlanLowering`.

    System Context:
        Phase-11 override lane (design v2 step S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Per-plan emission buffer: operands, direct calls, shared-site
        routing and generic construct fallbacks.
    """

    __slots__ = Cleanable.__slots__ + [
        "_steps",
        "_site_graph",
        "_winners",
        "_positional",
        "_conflicts",
        "_root_instance_key",
        "_arity",
        "_local_by_key",
        "_namespace",
        "_lines",
        "_masked",
        "_direct",
        "_dict_mode",
        "_shared",
        "_home",
        "_children",
        "_miss_value_params",
        "_root_index",
        "_miss_lines",
        "_context_params",
    ]

    def __init__(
            self,
            *,
            steps: Tuple[SitePlanStep, ...],
            site_graph: SpellSiteGraphAnalysis,
            resolution: OverrideKeyResolution,
            root_instance_key: SiteInstanceKey,
            root_spell_id: str,
            root_spell_name: str,
            arity: int,
            normal_mode: bool = False,
    ) -> None:
        """
        Prepare emission state; nothing is emitted until `render`.

        Args:
            steps: Kept (demanded) steps in providers-first order.
            site_graph: Site graph of the root (borrowed).
            resolution: The key set's resolution (borrowed).
            root_instance_key: Instance key of the root step.
            root_spell_id: Selected root spell id.
            root_spell_name: Root spell name.
            arity: Length of `__args__` for this plan (0 when absent).
            normal_mode: Emit `(meld)` signatures without `ov` (the caller has
                checked that the key set supplies nothing).

        Returns:
            None.
        """
        super().__init__()
        self._steps: Tuple[SitePlanStep, ...] = steps
        self._site_graph: SpellSiteGraphAnalysis = site_graph
        self._winners: Dict[Tuple[int, str], str] = resolution.winners
        self._positional: Dict[str, int] = resolution.positional
        self._conflicts: Tuple[Tuple[int, str, str, str], ...] = resolution.conflicts
        self._root_instance_key: SiteInstanceKey = root_instance_key
        self._arity: int = arity
        self._local_by_key: Dict[SiteInstanceKey, str] = {
            step.instance_key: f"v{index}" for index, step in enumerate(steps)
        }
        self._namespace: Dict[str, Any] = {
            "_raise_meld_construction_error": _raise_meld_construction_error,
            "_construct_spell_instance": _construct_spell_instance,
            "_construct_with_supplied_values": SitePlanRuntimeHelpers.construct_with_supplied_values,
            "_raise_existing_override": SitePlanRuntimeHelpers.raise_existing_override,
            "_conflict_guard": SitePlanRuntimeHelpers.conflict_guard,
            "root_spell_id": root_spell_id,
            "root_spell_name": root_spell_name,
            "spells": tuple(step.spell for step in steps),
        }
        self._lines: List[str] = []
        self._masked: List[SitePlanStep] = []
        # Placement state; filled by `render` (`_place`).
        self._direct: List[bool] = []
        self._dict_mode: bool = False
        self._shared: List[bool] = [step.existence is not Existence.many for step in steps]
        self._home: Dict[int, Optional[int]] = {}
        self._children: Dict[Optional[int], List[int]] = {}
        self._miss_value_params: Dict[int, Tuple[int, ...]] = {}
        self._root_index: int = -1
        self._miss_lines: List[str] = []
        # Leading parameters of the plan and of every miss.
        self._context_params: Tuple[str, ...] = ("meld",) if normal_mode else ("meld", "ov")

    def cleanup(self) -> None:
        """
        Delete emission state; the namespace and masked steps belong to the caller.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._lines.clear()
        del self._steps
        del self._site_graph
        del self._winners
        del self._positional
        del self._conflicts
        del self._root_instance_key
        del self._arity
        del self._local_by_key
        del self._namespace
        del self._lines
        del self._masked
        self._miss_lines.clear()
        del self._direct
        del self._dict_mode
        del self._shared
        del self._home
        del self._children
        del self._miss_value_params
        del self._root_index
        del self._miss_lines
        del self._context_params

    def _site_index(self, step: SitePlanStep) -> int:
        """
        Return the site index of one step.
        """
        return self._site_graph.site_index_by_instance_key[step.instance_key]

    def _supplied_names(self, step: SitePlanStep) -> FrozenSet[str]:
        """
        Return the parameters of one step that receive supplied values.
        """
        site_index = self._site_index(step)
        winners = self._winners
        return frozenset(
            param.name for param in self._site_graph.sites[site_index].params
            if (site_index, param.name) in winners
        )

    def _operand(self, step: SitePlanStep, site_index: int, param: SpellSiteParam) -> Optional[str]:
        """
        Return the source expression for one parameter, or None when it is omitted.

        Contract:
            Supplied value (`ov[key]`, `args[i]`) > dependency locals. A
            collection, or several dependencies, is a list; zero dependencies of
            a collection is `[]`; zero dependencies otherwise omits the parameter.
        """
        winner = self._winners.get((site_index, param.name))
        if winner == "__args__":
            return f"args[{self._positional[param.name]}]"
        if winner is not None:
            return f"ov[{winner!r}]"
        for param_name, dependency_keys in step.dependency_resolution_order:
            if param_name != param.name:
                continue
            locals_ = [self._local_by_key[key] for key in dependency_keys]
            if param_name in step.collection_param_names or len(locals_) > 1:
                return "[" + ", ".join(locals_) + "]"
            if not locals_:
                return None
            return locals_[0]
        return None

    def _call_arguments(
            self,
            step: SitePlanStep,
    ) -> Optional[Tuple[List[str], List[Tuple[str, str]], bool]]:
        """
        Return `(positional, keyword, star_args)` for a direct call, or None when not expressible.

        Contract:
            Parameters are taken in signature order; operands go positionally
            until the first omitted parameter, then by keyword. A root whose
            `__args__` is longer than its positional parameters passes `*args`
            (extra values fail in the constructor, as today). A variadic,
            unknown-kind or out-of-order positional-only operand is not
            expressible.
        """
        site_index = self._site_index(step)
        site = self._site_graph.sites[site_index]
        ordered = sorted(
            (param for param in site.params if param.position >= 0),
            key=lambda param: param.position,
        )
        trailing = [param for param in site.params if param.position < 0]
        positional: List[str] = []
        keyword: List[Tuple[str, str]] = []
        star_args = False
        positional_open = True
        if step.instance_key == self._root_instance_key and self._arity > 0:
            capable = [
                param for param in ordered if param.parameter_kind in SitePlanLowering.POSITIONAL_KINDS
            ]
            if self._arity > len(capable):
                star_args = True
                positional_open = False
        for param in ordered:
            kind = param.parameter_kind
            if star_args and kind in SitePlanLowering.POSITIONAL_KINDS:
                continue
            expression = self._operand(step, site_index, param)
            if expression is None:
                positional_open = False
                continue
            if kind is None or kind in SitePlanLowering.VARIADIC_KINDS:
                return None
            if positional_open and kind in SitePlanLowering.POSITIONAL_KINDS:
                positional.append(expression)
                continue
            if kind == "POSITIONAL_ONLY":
                return None
            keyword.append((param.name, expression))
        for param in trailing:
            expression = self._operand(step, site_index, param)
            if expression is not None:
                keyword.append((param.name, expression))
        return positional, keyword, star_args

    def _is_direct(self, step: SitePlanStep) -> bool:
        """
        Return True when a step is a plain call of a class, method or lambda spell.
        """
        spell = step.spell
        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            return False
        if spell.is_existing_creation:
            return False
        if step.has_contract_payload or step.uses_positional_override:
            return False
        if step.contract_positional_override is not None:
            return False
        return self._call_arguments(step) is not None

    def render(self) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        """
        Emit the plan and return `(source, namespace, masked steps)`.

        Contract:
            The source defines one `_miss{i}` per kept shared site, then the plan
            `def _site_plan_executor(meld, ov)` (`(meld)` in normal mode); all
            of it is exec'd into the returned namespace. Placement is computed
            first (see `_place`).

        Returns:
            Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]: See `SitePlanLowering.emit`.
        """
        self._direct = [self._is_direct(step) for step in self._steps]
        self._dict_mode = not all(self._direct)
        self._place()
        body = self._lines
        if self._arity > 0:
            body.append('    args = ov["__args__"]')
        sites = self._site_graph.sites
        for number, (site_index, param_name, winner, other) in enumerate(self._conflicts):
            target_name = self._bind(f"cf{number}", f"{sites[site_index].spell_id}.{param_name}")
            body.append(
                f"    _conflict_guard(ov[{winner!r}], ov[{other!r}], {target_name}, "
                "root_spell_id, root_spell_name)"
            )
        if self._dict_mode:
            body.append("    instance_results = {}")
        uses_many_store = self._emit_context(None, "    ", body)
        body.append(f"    return {self._local_by_key[self._root_instance_key]}")
        # Constants are read as globals of the plan's namespace; see the class contract.
        source_lines = list(self._miss_lines)
        signature = ", ".join(self._context_params)
        source_lines.append(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}({signature}):")
        if uses_many_store:
            source_lines.extend(self._many_store_prologue("    "))
        source_lines.extend(body)
        return "\n".join(source_lines) + "\n", self._namespace, tuple(self._masked)

    def _bind(self, name: str, value: Any) -> str:
        """
        Bind one plan constant into the namespace, which is the plan's globals.
        """
        self._namespace[name] = value
        return name

    def _place(self) -> None:
        """
        Place every kept step at top level (None) or inside one shared site's miss.

        Contract:
            - Steps are visited consumers before providers (reverse step order).
              The root and every shared site with a winning override are top
              level. Any other step lives at the lowest context common to its
              consumers, where a shared consumer's context is its own miss and a
              many consumer's context is where that consumer lives.
            - A consumer reads a provider through each non-supplied parameter's
              dependency keys, exactly the operands `_operand` emits.
            - Then each shared site's outer values are computed bottom-up: the
              direct operands of the steps built inside its miss (and of its own
              construction) that live outside it, plus what its nested misses need.

        Raises:
            RuntimeError: When a dependency key has no kept step, or a provider
                does not precede its consumer (the family order is providers-first).

        Returns:
            None.
        """
        steps = self._steps
        index_by_key = {step.instance_key: index for index, step in enumerate(steps)}
        providers_by_consumer: List[List[int]] = []
        consumers: List[List[int]] = [[] for _ in steps]
        for consumer, step in enumerate(steps):
            providers = self._direct_providers(step, index_by_key)
            for provider in providers:
                if provider >= consumer:
                    raise RuntimeError(
                        f"Key-set plan step {provider} does not precede its consumer {consumer}."
                    )
                consumers[provider].append(consumer)
            providers_by_consumer.append(providers)
        root_index = index_by_key[self._root_instance_key]
        home: Dict[int, Optional[int]] = {}
        for index in range(len(steps) - 1, -1, -1):
            if index == root_index or (self._shared[index] and self._supplied_names(steps[index])):
                home[index] = None
                continue
            contexts = [
                consumer if self._shared[consumer] else home[consumer] for consumer in consumers[index]
            ]
            home[index] = self._common_context(contexts, home)
        children: Dict[Optional[int], List[int]] = {}
        for index in range(len(steps)):
            children.setdefault(home[index], []).append(index)
        value_params: Dict[int, Tuple[int, ...]] = {}
        for index in range(len(steps)):
            if not self._shared[index]:
                continue
            inside = children.get(index, [])
            needed = set()
            for member in inside:
                # A nested shared site builds inside its own miss: only what that
                # miss needs from outside passes through here.
                if self._shared[member]:
                    needed.update(value_params[member])
                elif self._direct[member]:
                    needed.update(providers_by_consumer[member])
            if self._direct[index]:
                needed.update(providers_by_consumer[index])
            needed.difference_update(inside)
            needed.discard(index)
            value_params[index] = tuple(sorted(needed))
        self._home = home
        self._children = children
        self._miss_value_params = value_params
        self._root_index = root_index

    def _direct_providers(self, step: SitePlanStep, index_by_key: Dict[SiteInstanceKey, int]) -> List[int]:
        """
        Return the kept step indexes one step reads through its non-supplied parameters.

        Raises:
            RuntimeError: When a dependency key has no kept step.
        """
        supplied = self._supplied_names(step)
        providers: List[int] = []
        for param_name, dependency_keys in step.dependency_resolution_order:
            if param_name in supplied:
                continue
            for key in dependency_keys:
                provider = index_by_key.get(key)
                if provider is None:
                    raise RuntimeError(
                        f"Key-set plan dependency {key!r} of {step.instance_key!r} has no kept step."
                    )
                providers.append(provider)
        return providers

    @staticmethod
    def _common_context(
            contexts: List[Optional[int]],
            home: Dict[int, Optional[int]],
    ) -> Optional[int]:
        """
        Return the lowest context common to `contexts` (None is top level).

        Contract:
            A miss context's parent is its site's home. Top level wins as soon as
            one context is top level; no contexts at all is top level too.
        """
        if not contexts or None in contexts:
            return None
        chains: List[List[int]] = []
        for context in contexts:
            chain: List[int] = []
            current: Optional[int] = context
            while current is not None:
                chain.append(current)
                current = home[current]
            chains.append(chain)
        others = [set(chain) for chain in chains[1:]]
        for candidate in chains[0]:
            if all(candidate in other for other in others):
                return candidate
        return None

    def _miss_arguments(self, index: int) -> List[str]:
        """
        Return the parameter/argument names after `(meld, ov, c{i})` for one miss.

        Contract:
            `instance_results` in dict mode, `args` for the root when `__args__` is
            supplied, then the outer values in step order.
        """
        names: List[str] = []
        if self._dict_mode:
            names.append("instance_results")
        if self._arity > 0 and index == self._root_index:
            names.append("args")
        names.extend(f"v{value}" for value in self._miss_value_params[index])
        return names

    def _emit_context(self, context: Optional[int], indent: str, lines: List[str]) -> bool:
        """
        Emit the steps placed in one context (top level or one miss body) into `lines`.

        Returns:
            bool: True when a disposal-bearing many step here reads `many_store`.
        """
        uses_many_store = False
        for index in self._children.get(context, []):
            step = self._steps[index]
            if self._shared[index]:
                self._emit_shared_hit(index, step, indent, lines)
            elif self._emit_many(index, step, indent, lines):
                uses_many_store = True
            if self._dict_mode:
                key_name = self._bind(f"key{index}", step.instance_key)
                lines.append(f"{indent}instance_results[{key_name}] = v{index}")
        return uses_many_store

    def _emit_many(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> bool:
        """
        Emit one many step: construction, then disposal registration in the innermost scope.

        Returns:
            bool: True when the step registers through `many_store`.
        """
        self._emit_construct(index, step, self._direct[index], self._supplied_names(step), indent, lines)
        if not step.spell.has_disposal_methods:
            return False
        sid_name = self._bind(f"sid{index}", step.spell.spell_id)
        disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
        lines.append(
            f"{indent}many_store.add_many_creations({sid_name}, v{index}, "
            f"has_disposal_methods=True, disposal_methods={disposal_name})"
        )
        return True

    def _emit_shared_hit(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> None:
        """
        Emit one shared site where it lives: store read, P2 when pinned, miss call; then its miss.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        sid_name = self._bind(f"sid{index}", step.spell.spell_id)
        lines.append(f"{indent}{store} = {self._route(step.existence, spell_name)}")
        lines.append(f"{indent}v{index} = {store}._creations.get({sid_name})")
        if self._supplied_names(step):
            lines.append(f"{indent}if v{index} is not None:")
            lines.append(f"{indent}    _raise_existing_override({spell_name}, root_spell_id)")
        arguments = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        lines.append(f"{indent}if v{index} is None:")
        lines.append(f"{indent}    v{index} = _miss{index}({arguments})")
        self._emit_miss(index, step, sid_name)

    def _emit_miss(self, index: int, step: SitePlanStep, sid_name: str) -> None:
        """
        Emit `_miss{index}`: children, then guard, recheck (P2 when pinned), construction, publication.

        Contract:
            The sites placed inside the miss are built before the guard is taken,
            so the guard covers only this site's recheck, construction and
            publication, as every build lock does in the straight-line lowering.
            A user constructor never runs under another site's build lock.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        supplied = self._supplied_names(step)
        children: List[str] = []
        uses_many_store = self._emit_context(index, "    ", children)
        inner: List[str] = []
        self._emit_construct(index, step, self._direct[index], supplied, "            ", inner)
        if step.spell.has_disposal_methods:
            disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
            inner.append(
                f"            {store}.add_creation({sid_name}, v{index}, "
                f"has_disposal_methods=True, disposal_methods={disposal_name})"
            )
        else:
            inner.append(f"            {store}._creations[{sid_name}] = v{index}")
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        lines = self._miss_lines
        lines.append(f"def _miss{index}({parameters}):")
        if uses_many_store:
            lines.extend(self._many_store_prologue("    "))
        lines.extend(children)
        lines.append(f"    with {self._guard(step, store, sid_name, spell_name)}:")
        lines.append(f"        v{index} = {store}._creations.get({sid_name})")
        if supplied:
            lines.append(f"        if v{index} is not None:")
            lines.append(f"            _raise_existing_override({spell_name}, root_spell_id)")
        lines.append(f"        if v{index} is None:")
        lines.extend(inner)
        lines.append(f"        return v{index}")

    @staticmethod
    def _many_store_prologue(indent: str) -> List[str]:
        """
        Return the innermost-scope store selection for disposal-bearing many steps.
        """
        return [
            f"{indent}many_store = meld._spellspace_creations",
            f"{indent}if many_store is None:",
            f"{indent}    many_store = meld._conduit_creations",
        ]

    @staticmethod
    def _route(existence: Existence, spell_name: str) -> str:
        """
        Return the store expression for one shared existence (the manifest lowering's routing).

        Raises:
            RuntimeError: For an existence without a store route.
        """
        if existence is Existence.unique_per_conduit:
            return "meld._conduit_creations"
        if existence is Existence.unique_per_spell_space:
            return "meld._spellspace_creations"
        if existence is Existence.unique_per_conduit_lineage:
            return "meld._root_creations"
        if existence is Existence.unique_per_conduit_cluster:
            return "meld._cluster_creations.resolved_store()"
        if existence is Existence.unique:
            return f"{spell_name}._owner_creations"
        raise RuntimeError(f"Unsupported existence for a key-set plan step: {existence!r}")

    @staticmethod
    def _guard(step: SitePlanStep, store: str, sid_name: str, spell_name: str) -> str:
        """
        Return the build-lock expression for one shared step.

        Contract:
            Per-conduit, spellspace, cluster and lineage slots use the store's
            slot guard; `unique` uses `Spell._lock` with the lock hint, otherwise
            its store's slot guard (the manifest lowering's rule).
        """
        if step.existence is Existence.unique and step.use_spell_lock_hint:
            return f"{spell_name}._lock"
        return f"({store}._slot_guards.get({sid_name}) or {store}.slot_guard({sid_name}))"

    def _emit_construct(
            self,
            index: int,
            step: SitePlanStep,
            direct: bool,
            supplied: FrozenSet[str],
            indent: str,
            lines: List[str],
    ) -> None:
        """
        Emit the construction of kept step `index` into `v{index}`, appending to `lines`.

        Contract:
            Direct steps call the spell with operands and route failures through
            `_raise_meld_construction_error` with this call's keyword names and
            positional count. Generic steps call the no-overrides helper, or the
            supplied-values helper on a masked copy when the step has winners.
        """
        local = f"v{index}"
        if not direct:
            is_root_args = step.instance_key == self._root_instance_key and self._arity > 0
            if not supplied and not is_root_args:
                step_name = self._bind(f"st{index}", step)
                lines.append(
                    f"{indent}{local} = _construct_spell_instance(plan_step={step_name}, "
                    "instance_results=instance_results)"
                )
                return
            masked = step.masked(supplied, is_root_args)
            self._masked.append(masked)
            masked_name = self._bind(f"st{index}", masked)
            site_index = self._site_index(step)
            values: List[str] = []
            for name in sorted(supplied):
                winner = self._winners[(site_index, name)]
                if winner != "__args__":
                    values.append(f"{name!r}: ov[{winner!r}]")
            if is_root_args:
                values.append("'__args__': args")
            lines.append(
                f"{indent}{local} = _construct_with_supplied_values(plan_step={masked_name}, "
                f"instance_results=instance_results, supplied_values={{{', '.join(values)}}})"
            )
            return
        arguments = self._call_arguments(step)
        if arguments is None:
            raise RuntimeError(f"Step {index} was classified direct but has no call arguments.")
        positional, keyword, star_args = arguments
        call_name = self._bind(f"t{index}", step.spell.spell)
        parts: List[str] = []
        if star_args:
            parts.append("*args")
        parts.extend(positional)
        parts.extend(f"{name}={expression}" for name, expression in keyword)
        keyword_names = tuple(name for name, _ in keyword)
        count_expression = "len(args)" if star_args else str(len(positional))
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    {local} = {call_name}({', '.join(parts)})")
        lines.append(f"{indent}except Exception as exc:")
        lines.append(
            f"{indent}    _raise_meld_construction_error(spells[{index}], exc, "
            f"{keyword_names!r}, {count_expression})"
        )
