from types import FunctionType, MethodType
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, FrozenSet, List, Optional, Set, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
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
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
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
        Phase-11 normal and override lanes of the many_only and generalized
        families (design v2 S2/S3).

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
        generic construct with supplied values, the P2 refusal, the
        unresolved-input refusal and the equal-rank conflict guard. None of
        them runs on a direct-call step. Plans with a leasing managed site
        also read the lease returns and the missing-pool refusal
        (managed_spell_quantity S5, 2026-10-15); every other plan binds none
        of the three.

    Contract:
        - Stateless static methods; the class is never instantiated.
        - Error types and messages match today's override lane.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Referenced by `SitePlanLowering` emission namespaces.

    System Context:
        Phase-11 normal and override lanes of the many_only and generalized
        families (design v2 S2/S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Generic construct with supplied values, P2 refusal, the E1
        conflict guard, and the managed lease returns and missing-pool refusal for emitted
        key-set plans.
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
            _raise_meld_construction_error(spell, exc)

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
    def raise_unresolved_input(spell: Spell, param_names: Tuple[str, ...]) -> None:
        """
        Raise today's `UnresolvedInputError` for a site the plan is about to build (S4a, B6).

        Contract:
            Emitted before anything under the site is constructed, so the
            error has no TypeError cause (`UnresolvedInputError.for_unsupplied`,
            the same decision the solo lane's call target makes).

        Args:
            spell: The consumer whose unresolved inputs have no winning key.
            param_names: Those parameters, in signature order.

        Raises:
            UnresolvedInputError: Always.
        """
        raise UnresolvedInputError.for_unsupplied(spell, param_names)

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

    @staticmethod
    def return_leases(
            error: BaseException,
            leases: Tuple[Tuple[ManagedSpellQuantity, Any], ...],
    ) -> None:
        """
        Put back the objects a plan leased for a holder that was never built (F9).

        Purpose:
            Called from the `except BaseException` of a lease group: the holder's
            construction region (a later lease's build, the construction, a
            pinned refusal, the publication) raised after some of its leases
            were taken. Melder gives back what it leased for an object that does
            not exist; leases already passed to a built object are the holder's.

        Contract:
            - Every `(pool, object)` pair whose object is not None goes back
              through `pool.put_back` (the pool's resets run). None marks a lease
              the group never took (a class spell's construction never yields
              None) and is skipped.
            - A put-back that raises (a pool torn down meanwhile, a raising
              reset) becomes one note on `error` - "Returning an object leased
              from managed spell '<name>' failed: <failure>" - and the remaining
              pairs still go back. Nothing new is raised; the caller re-raises
              `error`.

        Args:
            error: The exception propagating from the holder's region.
            leases: The group's `(pool, object)` pairs in lease order.

        Returns:
            None.
        """
        for pool, obj in leases:
            if obj is None:
                continue
            try:
                pool.put_back(obj)
            except Exception as failure:
                # Best effort on an exception path: report on the propagating
                # error instead of replacing it.
                error.add_note(
                    f"Returning an object leased from managed spell '{pool.spell_name}' failed: {failure}"
                )

    @staticmethod
    def return_unused_leases(leases: Tuple[Tuple[ManagedSpellQuantity, Any], ...]) -> None:
        """
        Put back the leases of a shared holder whose cold race another meld won.

        Purpose:
            A shared consumer's miss leases its managed dependencies before its
            build guard. When the recheck under the guard finds the holder
            already published, the plan returns that holder and gives these
            leases back.

        Contract:
            - Every pair goes back through `pool.put_back`, even after one fails.
            - Failures are raised once all were tried, as one ExceptionGroup
              "Returning objects leased for a construction another meld finished
              first failed" of RuntimeErrors ("Returning an object leased from
              managed spell '<name>' failed: <failure>"), each chained from its
              failure.

        Args:
            leases: The `(pool, object)` pairs taken for the holder; every object is set.

        Raises:
            ExceptionGroup: When any put-back raised.

        Returns:
            None.
        """
        failures: List[Exception] = []
        for pool, obj in leases:
            try:
                pool.put_back(obj)
            except Exception as failure:
                error = RuntimeError(
                    f"Returning an object leased from managed spell '{pool.spell_name}' failed: {failure}"
                )
                error.__cause__ = failure
                failures.append(error)
        if failures:
            raise ExceptionGroup(
                "Returning objects leased for a construction another meld finished first failed",
                failures,
            )

    @staticmethod
    def raise_missing_managed_pool(spell: Spell) -> None:
        """
        Raise the named error for a managed site whose pool cannot be read.

        Contract:
            Called by a per-creation pool read
            (`spells[i]._owner_creations._managed_quantities[sid]`) that raised
            AttributeError or KeyError, and by `Conduit.managed_spell_meld`: the
            version has no owner store (its owner root's store was torn down, or
            it was never stamped - since 0.2.8248, when conjure also stamps the
            versions staged before it, only after a stamp that raised and was
            logged) or its store holds no pool under the id. Nothing was leased
            or built for the site.

        Args:
            spell: The managed spell.

        Raises:
            MeldExecutionError: Always.
        """
        raise MeldExecutionError(
            spell_id=spell.spell_id,
            spell_name=spell.spell_name,
            node_id=spell.spell_id,
            message=(
                f"Managed spell '{spell.spell_name}' has no pool to lease from: its owner root was torn down, "
                "or its owner store holds no pool for this version. Meld it through a live root that owns it."
            ),
        )


class SitePlanLowering:
    """
    Build the site graph from steps, compute demand and emit one key-set plan.

    Purpose:
        The shared lowering of design v2 for normal and override melds: given
        the lane's no-overrides steps and one resolved key set (empty for the
        normal plan), emit Python that
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
        - A site with UNRESOLVED_INPUT parameters and no winning key for them
          raises `UnresolvedInputError` before anything under it is built
          (S4a, 2026-09-26; B6); OVERRIDE_REQUIRED parameters keep the
          constructor's own error.
        - Emission is a pure function of its inputs; the returned source names
          no identities, so equal shapes share one code object.
        - A `managed_spell_quantity` step is leased from its pool, one site per
          path (managed_spell_quantity S5, 2026-10-15): see "Managed sites" in
          `SitePlanEmission`.

    Threading:
        Compile-time only; emitted plans take the same locks as the normal lane,
        with one exception (2026-09-26, 0.2.73): the normal plan emitted for a
        `door_route_key` of "unique_per_conduit" or "spellspace" whose root has
        that route's existence builds its root without taking the root's slot
        guard, because the route door that calls it already holds that same
        guard across the call. See `SitePlanEmission`. A managed site's warm
        lease takes no lock; its miss takes only its pool's leaf lock (in
        `reserve`, `abandon` and `adopt`), never across user code.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Used by `SitePlanOverrideRuntime` (shared_assets).

    System Context:
        Phase-11 normal and override lanes of the many_only and generalized
        families (design v2 S2/S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Site graph from steps, demand walk and key-set plan source emission
        for normal and override melds.
    """

    __slots__ = ()

    PLAN_FUNCTION_NAME: ClassVar[str] = "_site_plan_executor"
    PLAN_SOURCE_NAME: ClassVar[str] = "<melder_site_plan_executor>"
    POSITIONAL_KINDS: ClassVar[Tuple[str, ...]] = ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
    VARIADIC_KINDS: ClassVar[Tuple[str, ...]] = ("VAR_POSITIONAL", "VAR_KEYWORD")

    @staticmethod
    def positional_run(target: Any, names: Tuple[str, ...]) -> int:
        """
        Return how many leading `names` the code that receives a call of `target` binds by position.

        Purpose:
            Decide where an emitted call may pass operands positionally. Injection is by parameter
            name, so a value goes positionally only where the receiving code provably binds that
            position to that name; code that can observe argument names (a custom `__new__`, a
            metaclass `__call__`, a signature-preserving `*args, **kwargs` wrapper) gets names.
            Positional class calls are the fast path on CPython 3.14 (P1, melder_2).

        Contract:
            - A class qualifies when its metaclass keeps `type.__call__`, its `__new__` is
              `object.__new__` and its `__init__` is a plain Python function; the receiving names
              are that `__init__`'s positional parameters after `self`.
            - A plain function or lambda gives its own positional parameters; a bound method of a
              plain function gives its function's positional parameters after the bound one.
            - Anything else receives no positional operands (returns 0).
            - Counts the leading `names` equal, in order, to the receiving names; positional-only
              parameters count like the others.
            - Pure attribute reads: annotations, `__signature__` and `__wrapped__` are never read.

        Args:
            target: The step's call target (`Spell.spell`).
            names: The call site's positional-capable parameter names in signature order.

        Returns:
            int: The length of the matching leading run (0 when `target` does not qualify).
        """
        receiving: Tuple[str, ...] = ()
        if isinstance(target, type):
            initializer = target.__init__
            if (
                    type(target).__call__ is type.__call__
                    and target.__new__ is object.__new__
                    and type(initializer) is FunctionType
            ):
                code = initializer.__code__
                receiving = code.co_varnames[1:code.co_argcount]
        elif type(target) is FunctionType:
            code = target.__code__
            receiving = code.co_varnames[:code.co_argcount]
        elif type(target) is MethodType and type(target.__func__) is FunctionType:
            code = target.__func__.__code__
            receiving = code.co_varnames[1:code.co_argcount]
        run = 0
        for name, received in zip(names, receiving):
            if name != received:
                break
            run += 1
        return run

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
            door_route_key: Optional[str] = None,
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
            door_route_key: Normal mode only. The route key of the
                CreationContext doors that call this plan (they hold that
                route's build lock across the call), or None when a caller may
                not hold it. For "unique_per_conduit" and "spellspace" with a
                root of the matching existence, the root site takes no guard of
                its own (see `SitePlanEmission`); anything else keeps it.

        Raises:
            RuntimeError: When the root step is missing from `steps`,
                `normal_mode` is asked for a key set that supplies anything, or
                `door_route_key` is given outside normal mode.

        Returns:
            Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
                Identity-free source, its namespace, and the masked steps the
                namespace references (owned by the caller).
        """
        if normal_mode and (resolution.winners or resolution.conflicts or arity):
            raise RuntimeError("A normal-mode plan is only emitted for a key set that supplies nothing.")
        if door_route_key is not None and not normal_mode:
            raise RuntimeError("A door route key applies only to the normal-mode plan.")
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
            door_route_key=door_route_key,
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
        - Generic steps read their dependency values through a dict LITERAL
          (lazy `instance_results`, 2026-10-03): each generic construction is
          preceded by `instance_results = {key: v, ...}` holding exactly the
          (masked) step's dependency keys, built where the step runs from
          locals the plan already holds. No dict is allocated at the plan top,
          nothing is stored per step and misses take no dict parameter, so a
          warm creation whose shared sites all hit builds no dict at all.
          Direct-mode plans are unchanged.
        - Owner-store constants (S9, 2026-10-03): a `unique` site whose provider
          Spell is owned by an automatic conduit and has an owner store binds
          `c{i}` to that store in the namespace and emits no alias line, so the
          warm read is `c{i}._creations.get(sid{i})` on a global; every other
          shared site (the `meld.<store>` routes, a provider in a dynamic
          environment, where ownership transfer repoints the store, or one not
          yet owned) emits `c{i} = <route>` as before. The miss keeps its
          `c{i}` parameter; the call passes the global. Measured on the VM:
          8-10 ns per unique site per creation.
        - Placement (2026-09-26): every kept step lives at top level or inside
          exactly one shared site's `_miss{i}`. The root is top level; a many
          site lives where its one consumer is built (inside the consumer's miss
          when the consumer is shared); a shared site lives at the lowest context
          common to all its consumers; a shared site with a winning override is
          pinned to top level so its P2 refusal and build are exactly today's.
          Within a context steps keep the family's providers-first order.
        - Child registration (many_child_follows_holder, 2026-10-14): a
          disposal-bearing many step registers in the store that owns its
          context. At the top level that is the meld's innermost scope
          (`many_store`: the spellspace store, else the conduit store), where a
          many root registers too. Inside `_miss{i}` it is `c{i}`, the store
          shared site i publishes to - the spell owner's for `unique`, the
          conduit's for `unique_per_conduit`, the spellspace's for
          `unique_per_spell_space`, the lineage root's, the cluster's team
          store (0.2.8237) - so a holder's `many` children belong to whatever
          owns the holder and are disposed with that store, never by a narrower
          scope that happened to meld the holder first. Until 0.2.8235 a miss
          registered them in the innermost scope, whose end disposed a child
          its holder still used.
        - Child adoption (slotted_lifetime_ownership, 0.2.8238): right after a
          miss publishes its site, still under the site's build lock, it calls
          `c{i}.adopt_children(sid{i}, v{i}, ((sidN, vN), ...))` for exactly
          the children it registered, which moves them from their spells'
          `many` buckets into the holder's disposal record. Purge, an ownership
          transfer's move and disposal of the holder then take them with it. A
          lost cold race, a pinned-override refusal or a raising holder
          constructor never reaches the call: those children stay in their
          bucket and are disposed with the store. Only misses with
          disposal-bearing children gain the line; every `_site_plan_executor`
          body is unchanged.
        - Normal mode (S2b-2, 2026-09-26) drops `ov` from the plan and from
          every miss signature and call; nothing else changes.
        - Unresolved inputs (S4a, 2026-09-26): a context (the plan top, or a
          shared site's miss) raises first for the first site it builds
          unconditionally, in step order, whose UNRESOLVED_INPUT parameters
          have no winning key: its many children, then (in a miss) the site
          itself. A stored site's miss never runs, so it never demands.
        - A miss function takes `(meld, ov, c{i}, [args], v...)`: the outer
          values its sites read (call operands or dict-literal values), in
          step order. It builds the
          sites placed inside it first, then takes the site's build guard for
          recheck, construction and publication only, and returns the site's
          value. So a plan never holds a build lock while another site's
          constructor runs (today's locking; design risk R2 retired
          2026-09-26); a cold race may build and drop the loser's children, as
          the straight-line lowering does.
        - Door-held root (2026-09-26, 0.2.73): in normal mode with a
          `door_route_key` from `DOOR_HELD_ROOT_EXISTENCE` and a root of that
          existence, the root's miss takes no guard. The route door that calls
          the plan holds the root's slot guard from its recheck until the plan
          returns; the plan's root store read (`meld._conduit_creations` or
          `meld._spellspace_creations`, each assigned once per Meld) yields the
          same store and so the same guard, and a second take would only
          re-enter it. The root miss still rechecks after building its
          children, so a same-thread nested meld that published the root
          meanwhile is returned. The children's constructors run under the
          door's root guard, as they did when the plan re-entered it. Every
          other site, root and key-set plan keeps its guard.
        - Managed sites (managed_spell_quantity S5, 2026-10-15): a
          `managed_spell_quantity` step is LEASING unless a winning key targets
          one of its own parameters, which makes it FRESH: constructed where a
          many step would be, never pooled, counted, registered or adopted (the
          caller's object). A leasing site has its own `_miss{i}` (like a shared
          site) and exactly one consumer, per path; it is not emitted where it
          is placed but in its consumer's lease group, right before the
          consumer's construction region (inside the consumer's miss, after its
          children, when the consumer has one). The lease is an inline
          `pp{i}()` - the pool and its `_idle.pop` bound as plan constants under
          the owner-store rule (automatic owner, owner store set, pool present
          at emission) - or, per creation, a read of
          `spells[i]._owner_creations._managed_quantities[sid{i}]` (a missing
          store or pool raises the named MeldExecutionError) and
          `h{i}._idle.pop()`; an empty pool calls `_miss{i}(meld, [ov,] h{i},
          ...)`. The miss checks unresolved inputs, then `reserve()` (an object
          served returns at once), then builds its children, its own lease group
          and its construction inside `try`, whose handler calls
          `h{i}.abandon(kids{i} or [], exc)` and re-raises. Disposal-bearing many
          children placed in the miss are appended to `kids{i}` as `(v, dm)` and
          adopted with the object (`h{i}.adopt`), never registered in a store. A
          lease group takes its first lease, sets the others to None, then runs
          the rest and the consumer's construction region inside `try`; on any
          exception `_return_leases` puts back what was taken and the error is
          re-raised. For a shared consumer the region is its guard block, which
          returns from inside; a recheck that finds the holder published (a lost
          race) falls through to `_return_unused_leases`. A plan with no managed
          step takes none of these branches and binds none of the three helpers,
          so its source and namespace are unchanged.

    Lifecycle / Cleanup:
        Created and cleaned inside one `emit` call. The namespace and masked
        steps it produced are handed to the caller before cleanup and are not
        touched by it.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Private worker of `SitePlanLowering`.

    System Context:
        Phase-11 normal and override lanes of the many_only and generalized
        families (design v2 S2/S3).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Per-plan emission buffer: operands, direct calls, shared-site
        routing and generic construct fallbacks.
    """

    # Door route key -> the root existence whose normal-plan root miss relies on
    # the calling door's slot guard. Both routes read their store from a Meld
    # attribute assigned once in `Meld.__init__`; lineage (repointed at link and
    # upgrade), cluster (store re-resolved per call) and unique (Spell lock in
    # the door) are deliberately absent.
    DOOR_HELD_ROOT_EXISTENCE: ClassVar[Dict[str, Existence]] = {
        "unique_per_conduit": Existence.unique_per_conduit,
        "spellspace": Existence.unique_per_spell_space,
    }

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
        "_index_by_key",
        "_shared",
        "_home",
        "_children",
        "_miss_value_params",
        "_root_index",
        "_miss_lines",
        "_context_params",
        "_root_guard_held_by_door",
        "_leasing",
        "_fresh",
        "_has_miss",
        "_leases_by_consumer",
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
            door_route_key: Optional[str] = None,
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
            door_route_key: Normal mode only: the route key of the doors that
                call this plan, or None. Decides whether the root's miss relies
                on the door's guard (see the class contract).

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
            "_raise_unresolved_input": SitePlanRuntimeHelpers.raise_unresolved_input,
            "_conflict_guard": SitePlanRuntimeHelpers.conflict_guard,
            "root_spell_id": root_spell_id,
            "root_spell_name": root_spell_name,
            "spells": tuple(step.spell for step in steps),
        }
        self._lines: List[str] = []
        self._masked: List[SitePlanStep] = []
        # Placement state; filled by `render` (`_place`).
        self._direct: List[bool] = []
        self._index_by_key: Dict[SiteInstanceKey, int] = {}
        # Site kinds (managed_spell_quantity S5): shared (slotted existences),
        # many, leasing managed (its own miss, leased per path) and fresh managed
        # (a winning key on its own parameters: built like many, never pooled).
        self._shared: List[bool] = []
        self._leasing: List[bool] = []
        self._fresh: List[bool] = []
        for step in steps:
            existence = step.existence
            managed = existence is Existence.managed_spell_quantity
            fresh = managed and bool(self._supplied_names(step))
            self._shared.append(existence is not Existence.many and not managed)
            self._leasing.append(managed and not fresh)
            self._fresh.append(fresh)
        # Sites built in an out-of-line `_miss{i}`: shared and leasing managed.
        self._has_miss: List[bool] = [
            shared or leasing for shared, leasing in zip(self._shared, self._leasing)
        ]
        self._leases_by_consumer: Dict[int, Tuple[int, ...]] = {}
        if any(self._leasing):
            # Bound only into plans that lease, so every other namespace is unchanged.
            self._namespace["_return_leases"] = SitePlanRuntimeHelpers.return_leases
            self._namespace["_return_unused_leases"] = SitePlanRuntimeHelpers.return_unused_leases
            self._namespace["_raise_missing_managed_pool"] = SitePlanRuntimeHelpers.raise_missing_managed_pool
        self._home: Dict[int, Optional[int]] = {}
        self._children: Dict[Optional[int], List[int]] = {}
        self._miss_value_params: Dict[int, Tuple[int, ...]] = {}
        self._root_index: int = -1
        self._miss_lines: List[str] = []
        # Leading parameters of the plan and of every miss.
        self._context_params: Tuple[str, ...] = ("meld",) if normal_mode else ("meld", "ov")
        # True when the calling door holds the root's slot guard across the plan
        # call (normal mode, eligible route, matching root existence).
        held_existence: Optional[Existence] = None
        if normal_mode and door_route_key is not None:
            held_existence = self.DOOR_HELD_ROOT_EXISTENCE.get(door_route_key)
        root_existence = next(
            step.existence for step in steps if step.instance_key == root_instance_key
        )
        self._root_guard_held_by_door: bool = (
            held_existence is not None and root_existence is held_existence
        )

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
        del self._index_by_key
        del self._shared
        del self._leasing
        del self._fresh
        del self._has_miss
        del self._leases_by_consumer
        del self._home
        del self._children
        del self._miss_value_params
        del self._root_index
        del self._miss_lines
        del self._context_params
        del self._root_guard_held_by_door

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
            Parameters are taken in signature order. An operand goes positionally
            while positionals are open and it is either a caller's root
            `__args__` value or bound to that position by name in the target's
            receiving code (`SitePlanLowering.positional_run`); the first
            operand that does not qualify, or the first omitted parameter,
            closes positionals and the rest go by keyword. A root whose
            `__args__` is longer than its positional parameters passes `*args`
            (extra values fail in the constructor, as today). A variadic or
            unknown-kind operand, or a positional-only operand that cannot go
            positionally, is not expressible (the step uses the generic helper).
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
        run = SitePlanLowering.positional_run(
            step.spell.spell,
            tuple(param.name for param in ordered if param.parameter_kind in SitePlanLowering.POSITIONAL_KINDS),
        )
        winners = self._winners
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
                if len(positional) < run or winners.get((site_index, param.name)) == "__args__":
                    positional.append(expression)
                    continue
                positional_open = False
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
            The source defines one `_miss{i}` per kept shared or leasing managed site, then the plan
            `def _site_plan_executor(meld, ov)` (`(meld)` in normal mode); all
            of it is exec'd into the returned namespace. Placement is computed
            first (see `_place`).

        Returns:
            Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]: See `SitePlanLowering.emit`.
        """
        self._direct = [self._is_direct(step) for step in self._steps]
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
        body.extend(self._unresolved_check_lines(None, "    "))
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
              operands - call operands or dict-literal values - of the steps built
              inside its miss (and of its own construction) that live outside it,
              plus what its nested misses need. A leasing managed site has a miss
              too and is placed by the same rule: with its one consumer, its home
              is that consumer's miss when the consumer has one, else the
              consumer's home. A fresh managed site is placed like a many step.
            - Leases by consumer: each consumer's leasing providers in operand
              order, without repeats (`_leases_by_consumer`).

        Raises:
            RuntimeError: When a dependency key has no kept step, a provider
                does not precede its consumer (the family order is providers-first),
                or a leasing managed step has other than one consumer (managed
                sites are per path).

        Returns:
            None.
        """
        steps = self._steps
        index_by_key = {step.instance_key: index for index, step in enumerate(steps)}
        self._index_by_key = index_by_key
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
            if self._leasing[index] and len(set(consumers[index])) != 1:
                raise RuntimeError(
                    f"Key-set plan managed step {index} has {len(set(consumers[index]))} consumers; "
                    "a managed site is per path and feeds exactly one."
                )
            contexts = [
                consumer if self._has_miss[consumer] else home[consumer] for consumer in consumers[index]
            ]
            home[index] = self._common_context(contexts, home)
        children: Dict[Optional[int], List[int]] = {}
        for index in range(len(steps)):
            children.setdefault(home[index], []).append(index)
        value_params: Dict[int, Tuple[int, ...]] = {}
        for index in range(len(steps)):
            if not self._has_miss[index]:
                continue
            inside = children.get(index, [])
            needed = set()
            for member in inside:
                # A nested shared or leasing site builds inside its own miss: only
                # what that miss needs from outside passes through here. A generic
                # member reads its providers through its dict literal, so they pass
                # through exactly like a direct member's call operands.
                if self._has_miss[member]:
                    needed.update(value_params[member])
                else:
                    needed.update(providers_by_consumer[member])
            needed.update(providers_by_consumer[index])
            needed.difference_update(inside)
            needed.discard(index)
            value_params[index] = tuple(sorted(needed))
        leases_by_consumer: Dict[int, Tuple[int, ...]] = {}
        for consumer, providers in enumerate(providers_by_consumer):
            leased: List[int] = []
            for provider in providers:
                if self._leasing[provider] and provider not in leased:
                    leased.append(provider)
            if leased:
                leases_by_consumer[consumer] = tuple(leased)
        self._home = home
        self._children = children
        self._miss_value_params = value_params
        self._root_index = root_index
        self._leases_by_consumer = leases_by_consumer

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
        Return the parameter/argument names after `(meld, ov, c{i})` (`h{i}` for a leasing site) for one miss.

        Contract:
            `args` for the root when `__args__` is supplied, then the outer
            values in step order (a generic member's providers included).
        """
        names: List[str] = []
        if self._arity > 0 and index == self._root_index:
            names.append("args")
        names.extend(f"v{value}" for value in self._miss_value_params[index])
        return names

    def _unsupplied_unresolved(self, index: int) -> Tuple[str, ...]:
        """
        Return kept step `index`'s UNRESOLVED_INPUT parameters that have no winning key, in signature order.
        """
        site_index = self._site_index(self._steps[index])
        winners = self._winners
        unresolved = SocketKind.UNRESOLVED_INPUT.value
        return tuple(
            param.name for param in self._site_graph.sites[site_index].params
            if param.socket_kind_value == unresolved and (site_index, param.name) not in winners
        )

    def _unresolved_check_lines(self, context: Optional[int], indent: str) -> List[str]:
        """
        Return the unresolved-input refusal for one context, or no lines.

        Contract:
            The sites a context builds unconditionally are its many children
            (in step order) and, for a miss, the shared site itself (after
            them, as providers precede consumers). The first with unsupplied
            unresolved inputs gets one unconditional raise at the context top,
            before any construction; shared and leasing managed children check
            in their own miss. A leasing miss checks before `reserve`, so a
            refusal takes no place from the pool.
        """
        candidates = [child for child in self._children.get(context, []) if not self._has_miss[child]]
        if context is not None:
            candidates.append(context)
        for index in candidates:
            names = self._unsupplied_unresolved(index)
            if names:
                return [f"{indent}_raise_unresolved_input(spells[{index}], {names!r})"]
        return []

    def _emit_context(self, context: Optional[int], indent: str, lines: List[str]) -> bool:
        """
        Emit the steps placed in one context (top level or one miss body) into `lines`.

        Contract:
            A disposal-bearing many step registers in the store that owns the
            context (see "Child registration" in the class contract): the
            top level (`context` None) registers through `many_store`, which the
            plan prologue points at the meld's innermost scope; shared site i's
            miss registers through `c{i}`, the store that site publishes to.
            Inside leasing managed site i's miss it is appended to `kids{i}`
            instead, to be adopted with the object (managed_spell_quantity S5).
            A leasing site is emitted by its consumer's lease group, not where
            it is placed; only a leasing root leases here.

        Args:
            context: None for the plan's top level, else the shared or leasing
                site whose miss body is being emitted.
            indent: Indentation of the emitted lines.
            lines: Target line list, appended in place.

        Returns:
            bool: True when a disposal-bearing many step at the top level reads
            `many_store` (the caller then emits the prologue); always False
            for a miss, whose children use its `c{i}` parameter or `kids{i}`.
        """
        store = "many_store" if context is None else f"c{context}"
        kids_name = self._kids_name(context) if context is not None and self._leasing[context] else None
        uses_many_store = False
        for index in self._children.get(context, []):
            step = self._steps[index]
            if self._shared[index]:
                self._emit_shared_hit(index, step, indent, lines)
            elif self._leasing[index]:
                if index == self._root_index:
                    self._emit_root_lease(index, indent, lines)
            elif self._emit_many(index, step, indent, lines, store, kids_name) and context is None:
                uses_many_store = True
        return uses_many_store

    def _emit_many(
            self,
            index: int,
            step: SitePlanStep,
            indent: str,
            lines: List[str],
            store: str,
            kids_name: Optional[str] = None,
    ) -> bool:
        """
        Emit one many (or fresh managed) step: construction, then its disposal registration in `store`.

        Contract:
            A step without disposal methods is constructed and not recorded
            anywhere. A disposal-bearing step is recorded through
            `<store>.register_many(sidN, vN, dmN)` right after construction,
            before any build lock of the context is taken - or, inside a leasing
            managed miss, appended as `(vN, dmN)` to `kids_name`. A fresh
            managed step (a winning key on its own parameters) is recorded
            nowhere: it is the caller's object. The construction runs inside
            the step's lease group when it reads leasing managed sites
            (managed_spell_quantity S5).

        Args:
            index: Kept step index.
            step: The step.
            indent: Indentation of the emitted lines.
            lines: Target line list, appended in place.
            store: The store expression the registration targets - `many_store`
                (the meld's innermost scope) at the top level, `c{i}` inside
                shared site i's miss (the store the holder belongs to).
            kids_name: `kids{i}` inside leasing managed site i's miss, else None.

        Returns:
            bool: True when the step registers in `store`.
        """
        self._emit_leased_region(index, indent, lines, self._construct_region(index, step))
        if self._fresh[index] or not step.spell.has_disposal_methods:
            return False
        if kids_name is not None:
            kids_disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
            lines.append(f"{indent}{kids_name}.append((v{index}, {kids_disposal_name}))")
            return False
        sid_name = self._bind(f"sid{index}", step.spell.spell_id)
        disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
        # `register_many` (2026-10-01): the positional hot verb; the key's
        # disposal list is recorded once by the store, not carried per entry.
        lines.append(f"{indent}{store}.register_many({sid_name}, v{index}, {disposal_name})")
        return True

    @staticmethod
    def _owner_store_constant(step: SitePlanStep) -> bool:
        """
        Decide whether one shared site's store is bound as a plan constant (S9, 2026-10-03).

        Contract:
            True only for `Existence.unique` - the one route that reads
            `spells[i]._owner_creations` - when the provider Spell is owned by an
            automatic conduit (`_dynamic_environment` False) and already has an
            owner store. In a dynamic environment ownership transfer repoints
            the store, so the per-creation read stays; a provider not yet owned
            keeps the read too, so its failure mode is unchanged.

        Args:
            step: The shared step.

        Returns:
            bool: True when `c{i}` is bound in the namespace instead of read per creation.
        """
        spell = step.spell
        return (
            step.existence is Existence.unique
            and not spell._dynamic_environment
            and spell._owner_creations is not None
        )

    def _emit_shared_hit(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> None:
        """
        Emit one shared site where it lives: store read (or the bound store), P2 when pinned, miss call;
        then its miss.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        sid_name = self._bind(f"sid{index}", step.spell.spell_id)
        if self._owner_store_constant(step):
            # S9: the owner store of a spell owned by an automatic conduit cannot
            # move after conjure, so the plan reads it as a global bound here
            # instead of `spells[i]._owner_creations` on every creation.
            self._bind(store, step.spell._owner_creations)
        else:
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
            Within the plan, a user constructor never runs under another site's
            build lock.
            Door-held root (0.2.73): when this is the root's miss and
            `_root_guard_held_by_door` is set, the `with` line is omitted and the
            recheck, construction and publication run at the miss's top level.
            The calling door holds this same slot guard for the whole call (see
            the class contract), so nothing else changes: the recheck still
            follows the children, and publication is the same statement.
            Children (many_child_follows_holder, 2026-10-14): the disposal-bearing
            many steps placed in the miss register in `c{index}`, the store this
            site publishes to, so they live and die with the holder's owner; the
            miss therefore needs no innermost-scope prologue. A losing thread in
            a cold race has registered its children there too, and they stay
            until that store is disposed.
            Adoption (0.2.8238): after publication, inside the guard and the
            miss branch, `c{index}.adopt_children(...)` hands exactly those
            registered children to the holder's disposal record (see the class
            contract); a miss without disposal-bearing children emits no call.
            Leases (managed_spell_quantity S5): when this site reads leasing
            managed sites they are leased after its children and before the
            guard, and the guard block runs inside the lease group's `try`. It
            returns the site from inside once published; any exception puts the
            leases back; a recheck that finds the site already published falls
            out of the block to `_return_unused_leases` and returns that site.
            Without leases the emitted miss is unchanged.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        supplied = self._supplied_names(step)
        children: List[str] = []
        self._emit_context(index, "    ", children)
        guarded = not (index == self._root_index and self._root_guard_held_by_door)
        leases = self._leases_by_consumer.get(index, ())

        def guard_region(region_indent: str, target: List[str]) -> None:
            # Guard, recheck (P2 when pinned), construction, publication, adoption.
            body_indent = region_indent + "    " if guarded else region_indent
            inner_indent = body_indent + "    "
            inner: List[str] = []
            self._emit_construct(index, step, self._direct[index], supplied, inner_indent, inner)
            if step.spell.has_disposal_methods:
                disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
                inner.append(
                    f"{inner_indent}{store}.add_creation({sid_name}, v{index}, "
                    f"has_disposal_methods=True, disposal_methods={disposal_name})"
                )
            else:
                inner.append(f"{inner_indent}{store}._creations[{sid_name}] = v{index}")
            adopted = [
                child for child in self._children.get(index, [])
                if self._is_plain_many(child) and self._steps[child].spell.has_disposal_methods
            ]
            if adopted:
                # The children `_emit_many` registered in this store move into the
                # holder's disposal record once it is published (0.2.8238).
                pairs = ", ".join(f"(sid{child}, v{child})" for child in adopted)
                trailing = "," if len(adopted) == 1 else ""
                inner.append(f"{inner_indent}{store}.adopt_children({sid_name}, v{index}, ({pairs}{trailing}))")
            if leases:
                # Return from inside: falling out of the block means another meld
                # published this site first (a lost cold race).
                inner.append(f"{inner_indent}return v{index}")
            if guarded:
                target.append(f"{region_indent}with {self._guard(step, store, sid_name, spell_name)}:")
            target.append(f"{body_indent}v{index} = {store}._creations.get({sid_name})")
            if supplied:
                target.append(f"{body_indent}if v{index} is not None:")
                target.append(f"{body_indent}    _raise_existing_override({spell_name}, root_spell_id)")
            target.append(f"{body_indent}if v{index} is None:")
            target.extend(inner)
            if not leases:
                target.append(f"{body_indent}return v{index}")

        body: List[str] = self._unresolved_check_lines(index, "    ")
        body.extend(children)
        if self._emit_leased_region(index, "    ", body, guard_region):
            body.append(f"    _return_unused_leases({self._lease_pairs(leases)})")
            body.append(f"    return v{index}")
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        self._miss_lines.append(f"def _miss{index}({parameters}):")
        self._miss_lines.extend(body)

    def _is_plain_many(self, index: int) -> bool:
        """
        Return True for a kept `many` step (not shared, and not a managed site of either kind).
        """
        return not (self._shared[index] or self._leasing[index] or self._fresh[index])

    def _kids_name(self, index: int) -> Optional[str]:
        """
        Return `kids{index}` when leasing site `index`'s miss builds a disposal-bearing many child, else None.
        """
        for child in self._children.get(index, []):
            if self._is_plain_many(child) and self._steps[child].spell.has_disposal_methods:
                return f"kids{index}"
        return None

    def _construct_region(self, index: int, step: SitePlanStep) -> Callable[[str, List[str]], None]:
        """
        Return the emitter of one step's construction (`v{index} = ...`) at the indentation it is given.
        """

        def region(indent: str, lines: List[str]) -> None:
            self._emit_construct(index, step, self._direct[index], self._supplied_names(step), indent, lines)

        return region

    def _emit_leased_region(
            self,
            consumer: int,
            indent: str,
            lines: List[str],
            region: Callable[[str, List[str]], None],
    ) -> bool:
        """
        Emit a consumer's construction region, inside its lease group when it reads leasing sites.

        Contract:
            - Without leases the region is emitted as is (every non-managed plan).
            - With leases m1..mn (operand order): the per-creation pool reads,
              the lease of m1, `v{m2..mn} = None`, then `try:` the remaining
              leases and the region, `except BaseException as exc:
              _return_leases(exc, ((h{m}, v{m}), ...))` and `raise`. Nothing but
              the consumer's other leases runs between a lease and the region,
              and a pool read that raises does so before anything is leased.

        Args:
            consumer: Kept index of the step whose region is emitted.
            indent: Indentation of the group; the region is one level deeper
                inside the `try`.
            lines: Target line list, appended in place.
            region: Emits the region at the indentation it is given.

        Returns:
            bool: True when a lease group was emitted.
        """
        leases = self._leases_by_consumer.get(consumer)
        if not leases:
            region(indent, lines)
            return False
        constant = {lease: self._bind_lease_pool(lease) for lease in leases}
        for lease in leases:
            if not constant[lease]:
                self._emit_pool_read(lease, indent, lines)
        first = leases[0]
        self._emit_lease(first, constant[first], indent, lines)
        for lease in leases[1:]:
            lines.append(f"{indent}v{lease} = None")
        inner = indent + "    "
        lines.append(f"{indent}try:")
        for lease in leases[1:]:
            self._emit_lease(lease, constant[lease], inner, lines)
        region(inner, lines)
        lines.append(f"{indent}except BaseException as exc:")
        lines.append(f"{indent}    _return_leases(exc, {self._lease_pairs(leases)})")
        lines.append(f"{indent}    raise")
        return True

    @staticmethod
    def _managed_pool_constant(step: SitePlanStep) -> Optional[ManagedSpellQuantity]:
        """
        Return the pool bound as a plan constant for one leasing site, or None for the per-creation read.

        Contract:
            The owner-store rule of `_owner_store_constant` (S9): only a provider
            owned by an automatic conduit (`_dynamic_environment` False) whose
            owner store already holds the pool. Such a store cannot move, and a
            pool is replaced under its id only by an ownership transfer's
            restore, which needs a dynamic world. The pool's `_idle` deque is
            assigned once and drained, never swapped, so its bound `pop` stays
            valid; a pool torn down with its root has a drained deque, so a
            constant lease misses and `reserve` raises the pool's own error.

        Args:
            step: The leasing managed step.

        Returns:
            Optional[ManagedSpellQuantity]: The pool, or None.
        """
        spell = step.spell
        if spell._dynamic_environment:
            return None
        owner = spell._owner_creations
        if owner is None:
            return None
        return owner.get_managed_quantity(spell.spell_id)

    def _bind_lease_pool(self, index: int) -> bool:
        """
        Bind one leasing site's spell_id, and its pool and pop when they are plan constants.

        Returns:
            bool: True when `h{index}` and `pp{index}` are bound (the constant shape).
        """
        step = self._steps[index]
        self._bind(f"sid{index}", step.spell.spell_id)
        pool = self._managed_pool_constant(step)
        if pool is None:
            return False
        self._bind(f"h{index}", pool)
        self._bind(f"pp{index}", pool._idle.pop)
        return True

    @staticmethod
    def _emit_pool_read(index: int, indent: str, lines: List[str]) -> None:
        """
        Emit the per-creation pool read of one leasing site: `h{index}`, or the named missing-pool error.
        """
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    h{index} = spells[{index}]._owner_creations._managed_quantities[sid{index}]")
        lines.append(f"{indent}except (AttributeError, KeyError):")
        lines.append(f"{indent}    _raise_missing_managed_pool(spells[{index}])")

    def _emit_lease(self, index: int, constant: bool, indent: str, lines: List[str]) -> None:
        """
        Emit one lease - the inline pop, else the miss call - and define the site's miss.
        """
        pop = f"pp{index}()" if constant else f"h{index}._idle.pop()"
        arguments = ", ".join(list(self._context_params) + [f"h{index}"] + self._miss_arguments(index))
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    v{index} = {pop}")
        lines.append(f"{indent}except IndexError:")
        lines.append(f"{indent}    v{index} = _miss{index}({arguments})")
        self._emit_leasing_miss(index, self._steps[index])

    def _emit_root_lease(self, index: int, indent: str, lines: List[str]) -> None:
        """
        Emit a leasing root's pool read and lease at the plan top; the plan returns the leased object.
        """
        constant = self._bind_lease_pool(index)
        if not constant:
            self._emit_pool_read(index, indent, lines)
        self._emit_lease(index, constant, indent, lines)

    def _emit_leasing_miss(self, index: int, step: SitePlanStep) -> None:
        """
        Emit `_miss{index}` of one leasing managed site.

        Contract:
            `def _miss{i}(meld, [ov,] h{i}, <outer values>)`: the unresolved-input
            check (before anything is reserved); `v = h.reserve()` and an early
            return of an object it serves; `kids{i} = []` when disposal-bearing
            many children are built inside; then `try:` the children, the site's
            own lease group and its construction, `except BaseException as exc:
            h.abandon(kids or [], exc)` and `raise` (an inner lease group has
            already put its leases back); then `h.adopt(v, kids)` when kids
            exist, and `return v`. `adopt` on a pool torn down meanwhile disposes
            the object and its kids and raises the pool's error.
        """
        pool = f"h{index}"
        kids = self._kids_name(index)
        body: List[str] = self._unresolved_check_lines(index, "    ")
        body.append(f"    v{index} = {pool}.reserve()")
        body.append(f"    if v{index} is not None:")
        body.append(f"        return v{index}")
        if kids is not None:
            body.append(f"    {kids} = []")
        body.append("    try:")
        self._emit_context(index, "        ", body)
        self._emit_leased_region(index, "        ", body, self._construct_region(index, step))
        body.append("    except BaseException as exc:")
        body.append(f"        {pool}.abandon({kids if kids is not None else '[]'}, exc)")
        body.append("        raise")
        if kids is not None:
            body.append(f"    {pool}.adopt(v{index}, {kids})")
        body.append(f"    return v{index}")
        parameters = ", ".join(list(self._context_params) + [pool] + self._miss_arguments(index))
        self._miss_lines.append(f"def _miss{index}({parameters}):")
        self._miss_lines.extend(body)

    @staticmethod
    def _lease_pairs(leases: Tuple[int, ...]) -> str:
        """
        Return the `((h{m}, v{m}), ...)` tuple literal of one lease group.
        """
        pairs = ", ".join(f"(h{lease}, v{lease})" for lease in leases)
        trailing = "," if len(leases) == 1 else ""
        return f"({pairs}{trailing})"

    @staticmethod
    def _many_store_prologue(indent: str) -> List[str]:
        """
        Return the innermost-scope store selection for the plan's top-level disposal-bearing many steps.

        Contract:
            Emitted once at the top of the plan body when a top-level many step
            registers. A miss never emits it: its children register in its own
            `c{i}` (see `_emit_context`).
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

    def _emit_results_literal(self, step: SitePlanStep, indent: str, lines: List[str]) -> None:
        """
        Emit the dict literal one generic construction reads: its dependency values by instance key.

        Contract:
            `step` is the step the construct helper receives (the masked copy
            when values are supplied), so the literal carries exactly the keys
            `_build_kwargs_no_overrides` reads from `dependency_resolution_order`,
            in that order, each bound to its provider's local; a provider feeding
            two parameters appears once. A step that reads no key gets `{}`.
            Every provider is a local in scope where the step is constructed:
            providers precede consumers, and `_place` passes outer providers into
            a miss. The literal is rebuilt per construction; nothing shared is
            held in the namespace.

        Args:
            step: The step (or masked copy) handed to the construct helper.
            indent: Indentation of the emitted line.
            lines: Target line list, appended in place.

        Raises:
            RuntimeError: When a dependency key has no kept step.

        Returns:
            None.
        """
        entries: List[str] = []
        providers: List[int] = []
        for _, dependency_keys in step.dependency_resolution_order:
            for key in dependency_keys:
                provider = self._index_by_key.get(key)
                if provider is None:
                    raise RuntimeError(
                        f"Key-set plan dependency {key!r} of {step.instance_key!r} has no kept step."
                    )
                if provider in providers:
                    continue
                providers.append(provider)
                key_name = self._bind(f"key{provider}", key)
                entries.append(f"{key_name}: v{provider}")
        lines.append(f"{indent}instance_results = {{{', '.join(entries)}}}")

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
            `_raise_meld_construction_error`. Generic steps first get their dict literal
            (`_emit_results_literal`), then call the no-overrides helper, or the
            supplied-values helper on a masked copy when the step has winners.
        """
        local = f"v{index}"
        if not direct:
            is_root_args = step.instance_key == self._root_instance_key and self._arity > 0
            if not supplied and not is_root_args:
                self._emit_results_literal(step, indent, lines)
                step_name = self._bind(f"st{index}", step)
                lines.append(
                    f"{indent}{local} = _construct_spell_instance(plan_step={step_name}, "
                    "instance_results=instance_results)"
                )
                return
            masked = step.masked(supplied, is_root_args)
            self._masked.append(masked)
            self._emit_results_literal(masked, indent, lines)
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
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    {local} = {call_name}({', '.join(parts)})")
        lines.append(f"{indent}except Exception as exc:")
        lines.append(f"{indent}    _raise_meld_construction_error(spells[{index}], exc)")
