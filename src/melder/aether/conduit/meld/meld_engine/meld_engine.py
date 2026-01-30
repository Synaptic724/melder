from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Sequence

# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.interfaces import ISpell
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    build_kwargs_from_injection_spec,
)
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanStep,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError

_OccurrenceKey = tuple[str, tuple[str, ...]]
_InstanceKey = tuple[str, Optional[tuple[str, ...]]]


class MeldEngine(Cleanable):
    """
    Per-meld-call execution engine.

    This class executes Phase 11 `ExecutionPlan` steps to construct instances.
    It applies overrides, resolves dependencies from previously constructed
    instances, and registers creations according to Existence semantics.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_context",
        "_root_spell",
        "_dag",
        "_resolution_frame",
        "_requirements",
        "_frame",
        "_logger",
        "_blueprint",
        "_override_map",
        "_spell_lookup",
        "_system_states",
        "_instance_results",
        "_override_targets_by_spell_id",
        "_any_overrides_present",
    ]

    def __init__(
            self,
            *,
            context: "MeldContext",
            root_spell: ISpell,
            dag: Any,
            resolution_frame: Any,
            requirements: Any,
            frame: ResolutionFrame,
            blueprint: Optional[RootResolutionBlueprint],
            override_map: Dict[SocketRef, Any],
            spell_lookup: Dict[str, ISpell],
            system_states: Any,
    ) -> None:
        """
        Initialize a new `MeldEngine` for a single meld call.

        Args:
            context: The per-call `MeldContext` carrying creations,
                overrides, cancellation, etc.
            root_spell: The root `ISpell` being activated.
            dag: The `DirectedAcyclicWorkGraph` describing the local
                dependency graph for this spell (currently unused in the
                MVP, but kept for future DAG-based execution).
            resolution_frame: The `SpellResolutionFrame` describing the
                root spell's DAG metadata (root node id, ordering, etc.).
            requirements: The `SpellRequirements` object describing the
                root spell's parameter requirements (currently not used
                directly in the MVP constructor path).
            frame: The per-execution `ResolutionFrame` that holds
                overrides, node results, and errors.
            blueprint: RootResolutionBlueprint for deep DAG execution (may be None).
            override_map: SocketRef -> value overrides computed by SpellOverrider.
            spell_lookup: mapping of spell_id -> ISpell for all nodes in the DAG.
            system_states: SpellSystemStates handle (used to resolve topologies).
        Raises:
            ValueError: If any of the required arguments (`context`,
                `root_spell`, `frame`) is `None`.
        """
        super().__init__()

        if context is None:
            raise ValueError("context cannot be None.")
        if root_spell is None:
            raise ValueError("root_spell cannot be None.")
        if frame is None:
            raise ValueError("frame cannot be None.")

        self._lock: RLock = RLock()
        self._context: "MeldContext" = context
        self._root_spell: ISpell = root_spell

        self._dag: Any = dag
        self._resolution_frame: Any = resolution_frame
        self._requirements: Any = requirements
        self._frame: ResolutionFrame = frame
        self._blueprint: Optional[RootResolutionBlueprint] = blueprint
        self._override_map: Dict[SocketRef, Any] = override_map or {}
        self._spell_lookup: Dict[str, ISpell] = spell_lookup or {}
        self._system_states = system_states
        self._instance_results: Dict[_InstanceKey, Any] = {}
        self._override_targets_by_spell_id: Dict[str, List[SocketRef]] = {}
        self._any_overrides_present: bool = False

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically clear references held by this engine.

        The runtime owns the lifetime of the engine; after execution has
        completed (success or error), it is responsible for calling
        `cleanup()` to drop references to the context, spell, DAG, and
        frame so they are eligible for GC.

        This method is:

            * Idempotent – calling it multiple times is safe.
            * Thread-safe – guarded by an internal `RLock`.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._context = None
            self._root_spell = None
            self._dag = None
            self._resolution_frame = None
            self._requirements = None
            self._frame = None
            self._blueprint = None
            self._override_map = None
            self._spell_lookup = None
            self._system_states = None
            self._instance_results = None
            self._override_targets_by_spell_id = None
            self._any_overrides_present = None
            self._cleaned = True

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def context(self) -> "MeldContext":
        """
        Return the per-call `MeldContext` associated with this engine.

        The context is owned by the caller (typically `MeldRuntime`) and
        is expected to be cleaned up by the caller after execution has
        finished.
        """
        return self._context

    @property
    def root_spell(self) -> ISpell:
        """
        Return the root spell being activated for this meld call.
        """
        return self._root_spell

    @property
    def frame(self) -> ResolutionFrame:
        """
        Return the `ResolutionFrame` that holds overrides, per-node
        results, and errors for this meld call.
        """
        return self._frame

    # ------------------------------------------------------------------ #
    # Core execution
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    # Instance planning
    # ------------------------------------------------------------------ #

    def _has_overrides_for_spell(self, spell_id: str) -> bool:
        """
        Purpose:
            Determine whether any overrides target the given spell.
        Contract:
            - Socket overrides are resolved by spell id.
            - Root-level overrides apply to the root spell id only.
        Args:
            spell_id: Spell version id to check.
        Returns:
            bool: True if overrides target the spell id.
        """
        if self._override_targets_by_spell_id.get(spell_id):
            return True
        root_id = self._root_spell.spell_index.current
        if spell_id != root_id:
            return False
        overrides = self._frame.overrides
        return bool(overrides)

    @staticmethod
    def _is_shared_existence(existence: Existence) -> bool:
        """
        Purpose:
            Determine whether an existence policy yields a shared instance.
        Contract:
            - Existence.many is treated as non-shared (per-path instances).
            - All other existences are treated as shared for override validation.
        Args:
            existence: Existence policy for the spell.
        Returns:
            bool: True when the existence is shared; False otherwise.
        """
        return existence is not Existence.many

    def _build_instance_override_map(
            self,
            *,
            spell_id: str,
            occurrence_path: tuple[str, ...],
            shared: bool,
    ) -> Dict[str, Any]:
        """
        Purpose:
            Select overrides applicable to a specific spell instance.
        Contract:
            - Shared instances accept path-agnostic overrides for their params.
            - Per-path instances accept overrides whose param_path matches the
              occurrence path.
        Args:
            spell_id: Spell id being constructed.
            occurrence_path: Path to the occurrence from the root.
            shared: Whether the instance is shared.
        Returns:
            Dict[str, Any]: Parameter name to override value mapping.
        """
        overrides: Dict[str, Any] = {}
        for socket_ref, value in (self._override_map or {}).items():
            if socket_ref.node_id != spell_id:
                continue
            if shared:
                overrides[socket_ref.param_name] = value
                continue
            if not socket_ref.param_path:
                continue
            if tuple(socket_ref.param_path[:-1]) == occurrence_path:
                overrides[socket_ref.param_name] = value
        return overrides

    def _store_instance_result(
            self,
            instance_key: _InstanceKey,
            instance: Any,
    ) -> None:
        """
        Purpose:
            Store a resolved instance for the given instance key.
        Contract:
            - Instance results are stored in a path-aware map.
            - The first instance for a spell id is also stored in ResolutionFrame.
        Args:
            instance_key: Instance key for the constructed spell.
            instance: Constructed instance.
        Returns:
            None.
        """
        self._instance_results[instance_key] = instance
        spell_id = instance_key[0]
        if not self._frame.has_result(spell_id):
            self._frame.set_result(spell_id, instance)

    def _get_instance_result(self, instance_key: _InstanceKey) -> Any:
        """
        Purpose:
            Retrieve a resolved instance by instance key.
        Contract:
            - Returns the instance when present.
        Args:
            instance_key: Instance key to retrieve.
        Returns:
            Any: The resolved instance.
        Raises:
            MeldExecutionError: If the instance is missing from the results map.
        """
        if instance_key not in self._instance_results:
            spell_id, _ = instance_key
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell_id,
                message=f"Instance result missing for spell '{spell_id}'.",
            )
        return self._instance_results[instance_key]

    def _raise_override_on_existing(self, spell: ISpell) -> None:
        """
        Purpose:
            Raise when overrides target an already-instantiated shared spell.
        Contract:
            - Shared spell instances cannot accept overrides after creation.
            - Root-level overrides are rejected when the root already exists.
        Args:
            spell: The spell whose instance is being reused.
        Returns:
            None.
        Raises:
            MeldExecutionError: If overrides target an existing shared instance.
        """
        if not self._is_shared_existence(spell.existence):
            return

        spell_id = spell.spell_index.current
        root_id = self._root_spell.spell_index.current
        if spell_id == root_id and self._any_overrides_present:
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell.spell_name,
                node_id=spell_id,
                message=(
                    "Overrides were supplied for a root spell that already exists. "
                    "Shared instances cannot be overridden after creation."
                ),
            )

        if self._has_overrides_for_spell(spell_id):
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell.spell_name,
                node_id=spell_id,
                message=(
                    "Overrides were supplied for a shared spell that already exists. "
                    "Shared instances cannot be overridden after creation."
                ),
            )

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #

    def run_execution_plan(
            self,
            execution_plan: ExecutionPlan,
            *,
            override_targets_by_spell_id: Dict[str, List[SocketRef]],
            any_overrides_present: bool,
    ) -> Any:
        """
        Execute a Phase 11 ExecutionPlan using precompiled step metadata.

        Args:
            execution_plan:
                Phase 11 execution plan to execute.
            override_targets_by_spell_id:
                Precomputed override targets grouped by spell id.
            any_overrides_present:
                Override presence flag for reuse/override gating.
        """
        self.check_cleaned()

        cancel_event: Optional[CancellationEvent] = self._context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        self._override_targets_by_spell_id = override_targets_by_spell_id
        self._any_overrides_present = any_overrides_present

        for step in execution_plan.steps:
            if step.instance_key in self._instance_results:
                continue
            spell = self._spell_lookup.get(step.spell_id)
            if spell is None:
                raise MeldExecutionError(
                    spell_id=step.spell_id,
                    spell_name=step.spell_id,
                    message=f"Spell with id '{step.spell_id}' not found in spellbook for meld.",
                )

            def _construct_node(
                    *,
                    plan_step: ExecutionPlanStep = step,
                    plan_spell: ISpell = spell,
            ) -> Any:
                kwargs: Dict[str, Any] = {}
                occurrence = plan_step.occurrence
                shared = plan_step.instance_key[1] is None
                override_values = self._build_instance_override_map(
                    spell_id=plan_step.spell_id,
                    occurrence_path=occurrence[1],
                    shared=shared,
                )
                if plan_step.inject_spec is not None:
                    kwargs = build_kwargs_from_injection_spec(
                        instance_key=plan_step.instance_key,
                        occurrence=occurrence,
                        injection_spec=plan_step.inject_spec,
                        instance_results=self._instance_results,
                        override_values=override_values,
                    )
                elif override_values:
                    kwargs.update(override_values)
                return self._construct_spell(plan_spell, kwargs)

            instance, _ = self._resolve_spell_instance_with_plan(
                spell,
                step,
                construct_fn=_construct_node,
            )
            self._store_instance_result(step.instance_key, instance)

        return self._get_instance_result(execution_plan.root_instance_key)

    def _construct_spell(self, spell: ISpell, kwargs: Dict[str, Any]) -> Any:
        """
        Purpose:
            Construct a spell instance using the provided arguments.
        Side Effects:
            - Invokes the spell callable to create an instance.
        Args:
            spell: Spell to construct.
            kwargs: Keyword argument payload (may include "__args__" for positional args).
        Returns:
            Any: Constructed spell instance.
        Raises:
            MeldExecutionError: If construction fails or required data is missing.
        """
        if spell.is_existing_creation:
            if spell.user_created_object is None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message="EXISTING_CREATION spell has no backing object.",
                )
            return spell.user_created_object

        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            return spell.spell

        try:
            call_kwargs = dict(kwargs)
            raw_args = call_kwargs.pop("__args__", [])
            if isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes)):
                args = list(raw_args)
            else:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message="__args__ override must be a list or tuple.",
                )
            return spell.spell(*args, **call_kwargs)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=f"Error invoking spell '{spell.spell_name}'.",
                inner=exc,
            ) from exc

    def _resolve_spell_instance_with_plan(
            self,
            spell: ISpell,
            plan_step: ExecutionPlanStep,
            *,
            construct_fn: Callable[[], Any],
    ) -> tuple[Any, bool]:
        """
        Internal

        Resolve a spell instance using Phase 11 plan metadata for creations targets
        and lock hints to avoid recomputing routing decisions.
        """
        creations = self._select_creations_by_target_kind(
            spell=spell,
            target_kind=plan_step.creations_target_kind,
        )
        existence: Existence = spell.existence
        instance: Any = None
        created = False

        if existence is Existence.many:
            instance = construct_fn()
            if creations is not None and plan_step.must_register:
                with creations._lock:
                    self._register_spell(spell, instance, creations)
            return instance, True

        if existence in (
                Existence.unique_per_conduit,
                Existence.unique_per_spell_space,
        ):
            if creations is None:
                instance = construct_fn()
                return instance, True
            with creations._lock:
                instance = self._get_existing_creation(spell, creations)
                if instance is None:
                    instance = construct_fn()
                    self._register_spell(spell, instance, creations)
                    created = True
                else:
                    self._raise_override_on_existing(spell)
            return instance, created

        use_spell_lock = plan_step.lock_hint == "spell_lock"
        if (
                use_spell_lock
                and self._context.caller_creations_lock_held
                and creations is self._context.caller_creations
        ):
            use_spell_lock = False

        if use_spell_lock:
            with spell._lock:
                if creations is not None:
                    with creations._lock:
                        instance = self._get_existing_creation(spell, creations)
                else:
                    instance = self._get_existing_creation(spell, None)

                if instance is None:
                    instance = construct_fn()
                    if creations is not None:
                        with creations._lock:
                            self._register_spell(spell, instance, creations)
                    created = True
                else:
                    self._raise_override_on_existing(spell)
            return instance, created

        if creations is None:
            instance = construct_fn()
            return instance, True

        with creations._lock:
            instance = self._get_existing_creation(spell, creations)
            if instance is None:
                instance = construct_fn()
                self._register_spell(spell, instance, creations)
                created = True
            else:
                self._raise_override_on_existing(spell)

        return instance, created

    def _select_creations_by_target_kind(
            self,
            *,
            spell: ISpell,
            target_kind: str,
    ) -> Any:
        """
        Select the appropriate creations container based on a precomputed target kind.

        Raises:
            ValueError: If the target kind is not recognized.
        """
        if target_kind == "caller":
            return self._context.caller_creations
        if target_kind in ("owner", "spellspace"):
            owner_creations = spell._owner_creations
            if owner_creations is None:
                owner_creations = self._context.owner_creations
            return owner_creations
        raise ValueError(
            f"Unsupported creations target kind '{target_kind}' for spell '{spell.spell_id}'."
        )

    def _get_existing_creation(
            self,
            spell: ISpell,
            creations: Any | None,
    ) -> Optional[Any]:
        """
        Attempt reuse from creations manager based on Existence.
        """
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        # many never reuses
        if existence is Existence.many:
            return None
        if creations is None:
            return None

        if isinstance(creations, Creations):
            if existence is Existence.unique:
                found = creations._unique.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_conduit:
                found = creations._unique_per_scope.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_conduit_cluster:
                found = creations._unique_per_cluster.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_conduit_lineage:
                found = creations._unique_per_lineage.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_spell_space:
                spellspace = creations._conduit.get_active_spellspace()
                if spellspace is None:
                    raise SpellSpaceScopeError(
                        "Existence.unique_per_spell_space requires an active SpellSpace. "
                        "Use 'with conduit.enter_spellspace()' when melding."
                    )
                if spellspace.owner_conduit is not creations._conduit:
                    raise SpellSpaceScopeError(
                        "Active SpellSpace belongs to a different conduit."
                    )
                found = creations.get_spellspace_creation(spellspace.id, spell_id)
                return found.value if found is not None else None
            return None

        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_conduit:
                found = creations._unique_per_scope.get(spell_id)
                return found.value if found is not None else None
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique:
                    found = parent_creations._unique.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_conduit_cluster:
                    found = parent_creations._unique_per_cluster.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_conduit_lineage:
                    found = parent_creations._unique_per_lineage.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_spell_space:
                    spellspace = creations._conduit.get_active_spellspace()
                    if spellspace is None:
                        raise SpellSpaceScopeError(
                            "Existence.unique_per_spell_space requires an active SpellSpace. "
                            "Use 'with conduit.enter_spellspace()' when melding."
                        )
                    if spellspace.owner_conduit is not creations._conduit:
                        raise SpellSpaceScopeError(
                            "Active SpellSpace belongs to a different conduit."
                        )
                    found = creations.get_spellspace_creation(spellspace.id, spell_id)
                    return found.value if found is not None else None
            return None

        return None

    def _register_spell(
            self,
            spell: ISpell,
            instance: Any,
            creations: Any | None,
    ) -> None:
        """
        Register a constructed instance into the appropriate creations container.

        Contract:
            - Per-conduit lifetimes register against the caller creations container.
            - Shared lifetimes register against the owner creations container.
            - Unknown creations containers are treated as no-ops.
            - Existence.many registration is skipped when the spell declares
              no disposal methods.

        Args:
            spell: The spell that produced the instance.
            instance: The newly constructed instance to register.
            creations: Creations container used for registration (must be provided).

        Returns:
            None.
        """
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id
        has_disposal_methods: bool = spell.has_disposal_methods
        disposal_methods: list[str] = spell.disposal_method_names

        if creations is None:
            return None

        if isinstance(creations, Creations):
            if existence is Existence.unique:
                creations.add_unique(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit:
                creations.add_unique_per_scope(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.many:
                if not has_disposal_methods:
                    return
                creations.add_many(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit_cluster:
                creations.add_unique_per_cluster(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit_lineage:
                creations.add_unique_per_lineage(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_spell_space:
                spellspace = creations._conduit.get_active_spellspace()
                if spellspace is None:
                    raise SpellSpaceScopeError(
                        "Existence.unique_per_spell_space requires an active SpellSpace. "
                        "Use 'with conduit.enter_spellspace()' when melding."
                    )
                if spellspace.owner_conduit is not creations._conduit:
                    raise SpellSpaceScopeError(
                        "Active SpellSpace belongs to a different conduit."
                    )
                creations.register_spellspace_creation(
                    spellspace.id,
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            return

        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_conduit:
                creations.add_unique_per_scope(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.many:
                if not has_disposal_methods:
                    return
                creations.add_many(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique:
                    parent_creations.add_unique(
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
                if existence is Existence.unique_per_conduit_cluster:
                    parent_creations.add_unique_per_cluster(
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
                if existence is Existence.unique_per_conduit_lineage:
                    parent_creations.add_unique_per_lineage(
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
                if existence is Existence.unique_per_spell_space:
                    spellspace = creations._conduit.get_active_spellspace()
                    if spellspace is None:
                        raise SpellSpaceScopeError(
                            "Existence.unique_per_spell_space requires an active SpellSpace. "
                            "Use 'with conduit.enter_spellspace()' when melding."
                        )
                    if spellspace.owner_conduit is not creations._conduit:
                        raise SpellSpaceScopeError(
                            "Active SpellSpace belongs to a different conduit."
                        )
                    creations.register_spellspace_creation(
                        spellspace.id,
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
            return

