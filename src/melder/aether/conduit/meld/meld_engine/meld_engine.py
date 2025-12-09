from __future__ import annotations

from threading import RLock
from typing import Any, Dict, MutableMapping, Optional, Sequence

# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.interfaces import ISpell, ICreations
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


class MeldEngine(Cleanable):
    """
    Per-meld-call execution engine.

    This class turns a validated spell + context into a concrete instance by
    walking the deep `RootResolutionBlueprint` DAG when available. It:

        * Walks the DirectedAcyclicWorkGraph from Phase 5 in topological order.
        * Builds constructor arguments from dependency results and socket-level overrides.
        * Applies reuse/registration according to Existence and Creations/LesserCreations.
        * Stores per-node results into a ResolutionFrame.

    If no blueprint is present, it falls back to single-node construction using
    the root spell and per-call overrides.
    """

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
            logger: Optional[Any] = None,
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
            logger: Optional logger; will be normalized to `SafeLogger`
                if provided.

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

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically clear references held by this engine.

        The runtime owns the lifetime of the engine; after `run()` has
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
            self._cleaned = True

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def context(self) -> "MeldContext":
        """
        Return the per-call `MeldContext` associated with this engine.

        The context is owned by the caller (typically `MeldRuntime`) and
        is expected to be cleaned up by the caller after `run()` has
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

    def run(self) -> Any:
        """
        Execute the meld call and return the constructed root instance.

        Executes the deep DAG in topological order using the RootResolutionBlueprint
        when available. Falls back to single-node construction if no blueprint is set.
        """
        self.check_cleaned()

        cancel_event: Optional[CancellationEvent] = self._context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        # If we have a deep blueprint, walk it; otherwise fall back to root-only.
        if self._blueprint is None:
            instance = self._construct_root_only()
            self._store_result(self._root_spell.spell_index.current, instance)
            return instance

        ordered_ids = self._blueprint.ordered_node_ids
        dag = self._blueprint.dag

        for node_id in ordered_ids:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            spell = self._spell_lookup.get(node_id)
            if spell is None:
                raise MeldExecutionError(
                    spell_id=node_id,
                    spell_name=node_id,
                    message=f"Spell with id '{node_id}' not found in spellbook for meld.",
                )

            existing = self._get_existing_creation(spell)
            if existing is not None:
                self._store_result(node_id, existing)
                continue

            kwargs = self._build_kwargs_for_node(
                node_id=node_id,
                dag=dag,
                override_map=self._override_map,
            )
            instance = self._construct_spell(spell, kwargs)
            self._register_spell(spell, instance)
            self._store_result(node_id, instance)

        root_id = self._root_spell.spell_index.current
        try:
            return self._frame.get_result(root_id)
        except KeyError:
            # If the blueprint didn't include the root (unlikely), build root directly.
            instance = self._construct_root_only()
            self._store_result(root_id, instance)
            return instance

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #

    def _construct_root_only(self) -> Any:
        """
        Construct the root spell instance using only override metadata.

        This path is used when we either have no DAG yet or the DAG is
        effectively a single node with no dependencies.

        Resolution logic (MVP)
        ----------------------

        * For existing-creation spells:
            - Return `spell.user_created_object` if available.
        * For class/method/lambda spells:
            - Use overrides from `ResolutionFrame.overrides`:
                - `__args__` (list/tuple) → positional args
                - other keys → keyword args
            - Invoke `spell.spell(*args, **kwargs)`.
        * For anything else:
            - Return `spell.spell` as-is (value spell).

        Any exception raised by the underlying callable is wrapped in a
        `MeldExecutionError` with the root spell's identity attached.

        Returns:
            The constructed instance for the root spell.

        Raises:
            MeldExecutionError:
                * If an existing-creation spell has no attached
                  `user_created_object`.
                * If invocation of the underlying callable fails.
        """
        spell = self._root_spell
        target = spell.spell

        # Only factory-like spells are expected here.
        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            # Treat everything else as a value spell.
            return target

        overrides = self._frame.overrides
        if overrides is None:
            overrides = {}

        # Positional overrides (if provided).
        raw_args = overrides.get("__args__")
        if isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes)):
            args = list(raw_args)
        else:
            args = []

        # Keyword overrides (all keys except "__args__").
        kwargs = {
            key: value
            for key, value in overrides.items()
            if key != "__args__"
        }

        try:
            instance = target(*args, **kwargs)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=f"Error invoking spell target {spell.spell_name!r}.",
                inner=exc,
            ) from exc

        return instance

    # ------------------------------------------------------------------ #
    # DAG helpers                                                        #
    # ------------------------------------------------------------------ #
    def _build_kwargs_for_node(
            self,
            *,
            node_id: str,
            dag,
            override_map: Dict[SocketRef, Any],
    ) -> Dict[str, Any]:
        """
        Build keyword args for a node by combining overrides and dependency instances.
        """
        kwargs: Dict[str, Any] = {}
        node = dag.get_node(node_id)
        if node is None:
            return kwargs

        # Map overrides targeting this node_id
        for socket_ref, value in (override_map or {}).items():
            if socket_ref.node_id == node_id:
                kwargs[socket_ref.param_name] = value

        # Resolve dependencies from DAG edges + topology
        if not node.dependencies:
            return kwargs

        topo = None
        if self._system_states is not None:
            try:
                topo = self._system_states.get_local_topology_by_id(node_id)
            except Exception:
                topo = None

        incoming_map: Dict[str, list[str]] = {}
        if topo is not None:
            for socket in topo.sockets:
                for target_id in socket.target_spell_ids:
                    incoming_map.setdefault(socket.param_name, []).append(target_id)

        # Merge incoming_params if topology is missing.
        for parent_node in node.dependencies:
            parent_id = parent_node.id
            param_name = node.incoming_params.get(parent_node)
            if param_name:
                incoming_map.setdefault(param_name, []).append(parent_id)

        for param_name, parent_ids in incoming_map.items():
            if param_name in kwargs:
                # Already overridden; skip DI value.
                continue
            values = []
            for parent_id in sorted(set(parent_ids)):
                if not self._frame.has_result(parent_id):
                    raise MeldExecutionError(
                        spell_id=node_id,
                        spell_name=node_id,
                        message=(
                            f"Dependency '{parent_id}' missing while building args for '{node_id}'."
                        ),
                    )
                values.append(self._frame.get_result(parent_id))
            if not values:
                continue
            if len(values) == 1:
                kwargs[param_name] = values[0]
            else:
                # Multiple providers -> inject list. Downstream type checks can enforce collections.
                kwargs[param_name] = values

        return kwargs

    def _construct_spell(self, spell: ISpell, kwargs: Dict[str, Any]) -> Any:
        """
        Construct a spell instance with provided kwargs (no positional in DAG mode).
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
            return spell.spell(**kwargs)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=f"Error invoking spell '{spell.spell_name}'.",
                inner=exc,
            ) from exc

    def _store_result(self, node_id: str, value: Any) -> None:
        self._frame.set_result(node_id, value)

    def _get_existing_creation(self, spell: ISpell) -> Optional[Any]:
        """
        Attempt reuse from creations manager based on Existence.
        """
        creations = self._context.creations
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        # many never reuses
        if existence is Existence.many:
            return None

        if isinstance(creations, Creations):
            if existence is Existence.unique_per_aetheric_frame:
                found = creations._unique.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_aetheric_frame_per_conduit:
                found = creations._unique_per_scope.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_aetheric_frame_per_conduit_cluster:
                found = creations._unique_per_cluster.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_aetheric_frame_per_conduit_lineage:
                found = creations._unique_per_lineage.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_aetheric_frame_per_spell_space:
                spellspace = creations._conduit.get_active_spellspace()
                if spellspace is None:
                    raise SpellSpaceScopeError(
                        "Existence.unique_per_aetheric_frame_per_spell_space requires an active SpellSpace. "
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
            if existence is Existence.unique_per_aetheric_frame_per_conduit:
                found = creations._unique_per_scope.get(spell_id)
                return found.value if found is not None else None
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique_per_aetheric_frame:
                    found = parent_creations._unique.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_aetheric_frame_per_conduit_cluster:
                    found = parent_creations._unique_per_cluster.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_aetheric_frame_per_conduit_lineage:
                    found = parent_creations._unique_per_lineage.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_aetheric_frame_per_spell_space:
                    spellspace = creations._conduit.get_active_spellspace()
                    if spellspace is None:
                        raise SpellSpaceScopeError(
                            "Existence.unique_per_aetheric_frame_per_spell_space requires an active SpellSpace. "
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

    def _register_spell(self, spell: ISpell, instance: Any) -> None:
        creations = self._context.creations
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        if isinstance(creations, Creations):
            if existence is Existence.unique_per_aetheric_frame:
                creations.add_unique(spell_id, instance)
                return
            if existence is Existence.unique_per_aetheric_frame_per_conduit:
                creations.add_unique_per_scope(spell_id, instance)
                return
            if existence is Existence.many:
                creations.add_many(spell_id, instance)
                return
            if existence is Existence.unique_per_aetheric_frame_per_conduit_cluster:
                creations.add_unique_per_cluster(spell_id, instance)
                return
            if existence is Existence.unique_per_aetheric_frame_per_conduit_lineage:
                creations.add_unique_per_lineage(spell_id, instance)
                return
            if existence is Existence.unique_per_aetheric_frame_per_spell_space:
                spellspace = creations._conduit.get_active_spellspace()
                if spellspace is None:
                    raise SpellSpaceScopeError(
                        "Existence.unique_per_aetheric_frame_per_spell_space requires an active SpellSpace. "
                        "Use 'with conduit.enter_spellspace()' when melding."
                    )
                if spellspace.owner_conduit is not creations._conduit:
                    raise SpellSpaceScopeError(
                        "Active SpellSpace belongs to a different conduit."
                    )
                creations.register_spellspace_creation(spellspace.id, spell_id, instance)
                return
            return

        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_aetheric_frame_per_conduit:
                creations.add_unique_per_scope(spell_id, instance)
                return
            if existence is Existence.many:
                creations.add_many(spell_id, instance)
                return
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique_per_aetheric_frame:
                    parent_creations.add_unique(spell_id, instance)
                    return
                if existence is Existence.unique_per_aetheric_frame_per_conduit_cluster:
                    parent_creations.add_unique_per_cluster(spell_id, instance)
                    return
                if existence is Existence.unique_per_aetheric_frame_per_conduit_lineage:
                    parent_creations.add_unique_per_lineage(spell_id, instance)
                    return
                if existence is Existence.unique_per_aetheric_frame_per_spell_space:
                    spellspace = creations._conduit.get_active_spellspace()
                    if spellspace is None:
                        raise SpellSpaceScopeError(
                            "Existence.unique_per_aetheric_frame_per_spell_space requires an active SpellSpace. "
                            "Use 'with conduit.enter_spellspace()' when melding."
                        )
                    if spellspace.owner_conduit is not creations._conduit:
                        raise SpellSpaceScopeError(
                            "Active SpellSpace belongs to a different conduit."
                        )
                    creations.register_spellspace_creation(spellspace.id, spell_id, instance)
                    return
            return
