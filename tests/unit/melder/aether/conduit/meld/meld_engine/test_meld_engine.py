from threading import Barrier, Lock, RLock, Thread
from types import SimpleNamespace
from typing import Any, Iterable, Optional
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
)


class _ConduitStub:
    """
    Minimal conduit stub for creations and spellspace checks.

    This provides just enough surface area for Creations/LesserCreations
    and MeldEngine spellspace guards.
    """

    def __init__(
        self,
        conduit_id: str,
        state: ConduitState,
        active_spellspace: Optional[SpellSpace] = None,
    ) -> None:
        """
        Initialize the stub with an id, state, and optional spellspace.

        Args:
            conduit_id: Identifier returned to creations managers.
            state: ConduitState required by Creations/LesserCreations.
            active_spellspace: Optional SpellSpace to expose.
        """
        self._id = conduit_id
        self._logger = MagicMock()
        self._conduit_state = state
        self._spellspace = active_spellspace

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """
        Return the currently active SpellSpace for this stub.
        """
        return self._spellspace


class _SystemStatesStub:
    """
    Stubbed SpellSystemStates accessor for topology resolution.
    """

    def __init__(
        self,
        mapping: dict[str, Any],
        raise_on: Optional[set[str]] = None,
    ) -> None:
        """
        Initialize with a topology mapping and optional failure set.

        Args:
            mapping: Spell id to topology object mapping.
            raise_on: Optional set of ids that should raise on access.
        """
        self._mapping = dict(mapping)
        self._raise_on = set(raise_on or [])

    def get_local_topology_by_id(self, spell_id: str) -> Any:
        """
        Return the topology for a spell id or raise if configured.
        """
        if spell_id in self._raise_on:
            raise RuntimeError("topology lookup failed")
        return self._mapping.get(spell_id)


class _TrackingLock:
    """
    Simple re-entrant lock that exposes a locked flag for tests.
    """

    def __init__(self) -> None:
        """
        Initialize the tracking lock.
        """
        self._lock = RLock()
        self._count = 0

    def acquire(self) -> None:
        """
        Acquire the underlying lock and update the count.
        """
        self._lock.acquire()
        self._count += 1

    def release(self) -> None:
        """
        Release the underlying lock and update the count.
        """
        self._count -= 1
        self._lock.release()

    def __enter__(self) -> "_TrackingLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()

    @property
    def locked(self) -> bool:
        """
        Return True when the lock is currently held.
        """
        return self._count > 0


def _make_socket(param_name: str, target_ids: Iterable[str]) -> SimpleNamespace:
    """
    Build a socket-like object for topology stubs.

    Args:
        param_name: Constructor parameter name.
        target_ids: Spell ids that feed this parameter.

    Returns:
        SimpleNamespace: Socket stub with required attributes.
    """
    return SimpleNamespace(param_name=param_name, target_spell_ids=tuple(target_ids))


def _make_topology(sockets: Iterable[SimpleNamespace]) -> SimpleNamespace:
    """
    Build a topology stub with a sockets attribute.

    Args:
        sockets: Iterable of socket stubs.

    Returns:
        SimpleNamespace: Topology stub matching MeldEngine expectations.
    """
    return SimpleNamespace(sockets=list(sockets))


def _make_socket_ref(node_id: str, param_name: str) -> SocketRef:
    """
    Build a SocketRef for override targeting.

    Args:
        node_id: Spell id for the node.
        param_name: Parameter name to override.

    Returns:
        SocketRef: Targeting reference for overrides.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=(param_name,),
        socket_kind=SocketKind.NORMAL,
    )


def _make_socket_ref_with_path(
    *,
    node_id: str,
    param_name: str,
    param_path: Iterable[str],
    socket_kind: SocketKind,
) -> SocketRef:
    """
    Build a SocketRef with an explicit parameter path and socket kind.

    Args:
        node_id: Spell id that owns the socket.
        param_name: Parameter name for the socket.
        param_path: Full parameter path from the root.
        socket_kind: SocketKind classification for the socket.

    Returns:
        SocketRef: Socket reference with the requested metadata.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=tuple(param_path),
        socket_kind=socket_kind,
    )


def _make_mutation_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: Iterable[str],
) -> SocketRef:
    """
    Build a MutationContract SocketRef for mutation override tests.

    Args:
        node_id: Spell id that owns the socket.
        param_name: Parameter name for the socket.
        param_path: Full parameter path from the root.

    Returns:
        SocketRef: MutationContract socket reference.
    """
    return _make_socket_ref_with_path(
        node_id=node_id,
        param_name=param_name,
        param_path=param_path,
        socket_kind=SocketKind.MUTATION_CONTRACT,
    )


def _make_blueprint_with_sockets(
    *,
    root_id: str,
    dag: DirectedAcyclicWorkGraph,
    ordered_node_ids: Iterable[str],
    sockets: Iterable[SocketRef],
) -> RootResolutionBlueprint:
    """
    Build a RootResolutionBlueprint and attach socket refs for targeting.

    Args:
        root_id: Root spell id for the blueprint.
        dag: DAG used by the blueprint.
        ordered_node_ids: Topological node ordering.
        sockets: SocketRef entries to attach and index.

    Returns:
        RootResolutionBlueprint: Blueprint with sockets indexed.
    """
    blueprint = _make_blueprint(
        root_id=root_id,
        dag=dag,
        ordered_node_ids=ordered_node_ids,
    )
    for socket in sockets:
        blueprint.add_socket_ref(socket)
    return blueprint


def _make_engine_with_sockets(
    *,
    root_id: str,
    ordered_node_ids: Iterable[str],
    sockets: Iterable[SocketRef],
    spell_lookup: Optional[dict[str, Any]] = None,
) -> tuple[MeldEngine, RootResolutionBlueprint, SimpleNamespace]:
    """
    Build a MeldEngine wired to a blueprint with socket refs.

    Args:
        root_id: Root spell id for the blueprint and engine.
        ordered_node_ids: Execution order for the blueprint.
        sockets: Socket refs to attach to the blueprint index.
        spell_lookup: Optional extra spell lookup entries.

    Returns:
        tuple[MeldEngine, RootResolutionBlueprint, SimpleNamespace]:
            Engine, blueprint, and root spell stub.
    """
    node_ids = set(ordered_node_ids)
    node_ids.add(root_id)
    for socket in sockets:
        node_ids.add(socket.node_id)
    dag = _make_dag_with_nodes(node_ids)
    blueprint = _make_blueprint_with_sockets(
        root_id=root_id,
        dag=dag,
        ordered_node_ids=ordered_node_ids,
        sockets=sockets,
    )
    root_spell = _make_spell(spell_id=root_id, existence=Existence.many)
    lookup = {root_id: root_spell}
    if spell_lookup:
        lookup.update(spell_lookup)
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup=lookup,
    )
    return engine, blueprint, root_spell


def _make_dag_with_nodes(node_ids: Iterable[str]) -> DirectedAcyclicWorkGraph:
    """
    Create a DAG containing nodes for each id.

    Args:
        node_ids: Iterable of node identifiers.

    Returns:
        DirectedAcyclicWorkGraph: DAG populated with the nodes.
    """
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(node_id)
    return dag


def _make_blueprint(
    root_id: str,
    dag: DirectedAcyclicWorkGraph,
    ordered_node_ids: Iterable[str],
) -> RootResolutionBlueprint:
    """
    Build a RootResolutionBlueprint with a fixed order.

    Args:
        root_id: Root spell id for the blueprint.
        dag: DAG used by the blueprint.
        ordered_node_ids: Topological node ordering.

    Returns:
        RootResolutionBlueprint: Configured blueprint instance.
    """
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=None,
        dag=dag,
        ordered_node_ids=list(ordered_node_ids),
    )


def _make_context(
    creations: Any,
    cancel_event: Any | None = None,
    caller_creations: Any | None = None,
    owner_creations: Any | None = None,
    caller_creations_lock_held: bool = False,
) -> SimpleNamespace:
    """
    Build a minimal context stub used by MeldEngine.

    Args:
        creations: Creations or LesserCreations instance.
        cancel_event: Optional cancellation event stub.
        caller_creations: Optional caller creations override.
        owner_creations: Optional owner creations override.
        caller_creations_lock_held: Flag indicating the caller creations lock is held.

    Returns:
        SimpleNamespace: Context stub with expected attributes.
    """
    if caller_creations is None:
        caller_creations = creations
    if owner_creations is None:
        owner_creations = creations
    return SimpleNamespace(
        creations=owner_creations,
        owner_creations=owner_creations,
        caller_creations=caller_creations,
        caller_creations_lock_held=caller_creations_lock_held,
        cancel_event=cancel_event,
    )


def _make_spell(
    *,
    spell_id: str,
    spell_name: Optional[str] = None,
    spell: Any = None,
    existence: Existence = Existence.unique,
    is_class_spell: bool = True,
    is_method_spell: bool = False,
    is_lambda_spell: bool = False,
    is_existing_creation: bool = False,
    user_created_object: Any = None,
    owner_creations: Any | None = None,
) -> SimpleNamespace:
    """
    Build a minimal spell stub with attributes used by MeldEngine.

    Args:
        spell_id: Spell version identifier.
        spell_name: Optional human-readable name.
        spell: Callable or value backing the spell.
        existence: Existence scope for creation reuse/registration.
        is_class_spell: True when the spell is callable as a class factory.
        is_method_spell: True when the spell is callable as a method factory.
        is_lambda_spell: True when the spell is callable as a lambda factory.
        is_existing_creation: True when spell wraps a pre-created object.
        user_created_object: Optional object for existing-creation spells.
        owner_creations: Optional owner creations container for shared lifetimes.

    Returns:
        SimpleNamespace: Spell-like object with the required attributes.
    """
    if spell is None:
        def _default_callable(**_kwargs: Any) -> str:
            return f"value:{spell_id}"
        spell = _default_callable
    if spell_name is None:
        spell_name = spell_id
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_name,
        spell_index=SpellIndex(spell_id),
        spell=spell,
        existence=existence,
        is_class_spell=is_class_spell,
        is_method_spell=is_method_spell,
        is_lambda_spell=is_lambda_spell,
        is_existing_creation=is_existing_creation,
        user_created_object=user_created_object,
        _owner_creations=owner_creations,
        _lock=RLock(),
    )


def _make_engine(
    *,
    root_spell: Optional[SimpleNamespace] = None,
    creations: Any = None,
    caller_creations: Any | None = None,
    owner_creations: Any | None = None,
    caller_creations_lock_held: bool = False,
    frame: Optional[ResolutionFrame] = None,
    blueprint: Optional[RootResolutionBlueprint] = None,
    override_map: Optional[dict[SocketRef, Any]] = None,
    spell_lookup: Optional[dict[str, Any]] = None,
    system_states: Any = None,
    cancel_event: Any | None = None,
) -> tuple[MeldEngine, SimpleNamespace, ResolutionFrame]:
    """
    Build a MeldEngine with default stubs for testing.

    Defaults:
        - Uses a real Creations container so locking paths are exercised.

    Returns:
        Tuple of (engine, root_spell, frame) for assertions.
    """
    if root_spell is None:
        root_spell = _make_spell(spell_id="root", spell=lambda **_: "root")
    if creations is None:
        creations, _ = _make_creations()
    if frame is None:
        frame = ResolutionFrame()
    context = _make_context(
        creations=creations,
        cancel_event=cancel_event,
        caller_creations=caller_creations,
        owner_creations=owner_creations,
        caller_creations_lock_held=caller_creations_lock_held,
    )
    engine = MeldEngine(
        context=context,
        root_spell=root_spell,
        dag=None,
        resolution_frame=None,
        requirements=None,
        frame=frame,
        blueprint=blueprint,
        override_map=override_map or {},
        spell_lookup=spell_lookup or {},
        system_states=system_states,
        logger=None,
    )
    return engine, root_spell, frame


def _make_creations(conduit_id: str = "conduit-1") -> tuple[Creations, _ConduitStub]:
    """
    Build a Creations manager with a stub conduit.

    Args:
        conduit_id: Identifier for the stub conduit.

    Returns:
        Tuple of (Creations, conduit stub).
    """
    conduit = _ConduitStub(conduit_id, ConduitState.normal)
    creations = Creations(False, [], conduit)
    return creations, conduit


def _make_lesser_creations(
    conduit_id: str = "conduit-1",
    parent_creations: Optional[Creations] = None,
) -> tuple[LesserCreations, _ConduitStub, Optional[Creations]]:
    """
    Build a LesserCreations manager with a stub conduit.

    Args:
        conduit_id: Identifier for the lesser conduit.
        parent_creations: Optional parent creations manager.

    Returns:
        Tuple of (LesserCreations, conduit stub, parent creations).
    """
    conduit = _ConduitStub(conduit_id, ConduitState.lesser)
    lesser = LesserCreations(False, [], conduit, parent_creations)
    return lesser, conduit, parent_creations


def test_init_requires_context_raises_valueerror() -> None:
    """
    Verify MeldEngine rejects a None context.

    Contract:
        - context must not be None.
    """
    root_spell = _make_spell(spell_id="root")
    frame = ResolutionFrame()
    with pytest.raises(ValueError, match="context cannot be None"):
        MeldEngine(
            context=None,
            root_spell=root_spell,
            dag=None,
            resolution_frame=None,
            requirements=None,
            frame=frame,
            blueprint=None,
            override_map={},
            spell_lookup={},
            system_states=None,
        )


def test_init_requires_root_spell_raises_valueerror() -> None:
    """
    Verify MeldEngine rejects a None root spell.

    Contract:
        - root_spell must not be None.
    """
    frame = ResolutionFrame()
    with pytest.raises(ValueError, match="root_spell cannot be None"):
        MeldEngine(
            context=_make_context(SimpleNamespace()),
            root_spell=None,
            dag=None,
            resolution_frame=None,
            requirements=None,
            frame=frame,
            blueprint=None,
            override_map={},
            spell_lookup={},
            system_states=None,
        )


def test_init_requires_frame_raises_valueerror() -> None:
    """
    Verify MeldEngine rejects a None ResolutionFrame.

    Contract:
        - frame must not be None.
    """
    root_spell = _make_spell(spell_id="root")
    with pytest.raises(ValueError, match="frame cannot be None"):
        MeldEngine(
            context=_make_context(SimpleNamespace()),
            root_spell=root_spell,
            dag=None,
            resolution_frame=None,
            requirements=None,
            frame=None,
            blueprint=None,
            override_map={},
            spell_lookup={},
            system_states=None,
        )


def test_properties_expose_context_root_spell_and_frame() -> None:
    """
    Verify MeldEngine exposes core constructor inputs.

    Contract:
        - context, root_spell, and frame properties match inputs.
    """
    root_spell = _make_spell(spell_id="root")
    frame = ResolutionFrame()
    context = _make_context(SimpleNamespace())
    engine = MeldEngine(
        context=context,
        root_spell=root_spell,
        dag=None,
        resolution_frame=None,
        requirements=None,
        frame=frame,
        blueprint=None,
        override_map={},
        spell_lookup={},
        system_states=None,
    )
    assert engine.context is context
    assert engine.root_spell is root_spell
    assert engine.frame is frame


def test_cleanup_clears_references_and_is_idempotent() -> None:
    """
    Verify cleanup clears references and can be called repeatedly.

    Contract:
        - cleanup drops stored references and marks the engine cleaned.
        - repeated cleanup calls are safe.
    """
    engine, _, _ = _make_engine()
    engine.cleanup()
    assert engine.cleaned is True
    assert engine.context is None
    assert engine.root_spell is None
    assert engine.frame is None
    engine.cleanup()
    assert engine.cleaned is True


def test_run_after_cleanup_raises_runtimeerror() -> None:
    """
    Verify run() refuses execution after cleanup.

    Contract:
        - run raises RuntimeError once cleaned.
    """
    engine, _, _ = _make_engine()
    engine.cleanup()
    with pytest.raises(RuntimeError, match="already been cleaned"):
        engine.run()


def test_run_root_only_returns_value_and_stores_result() -> None:
    """
    Verify root-only execution returns a value spell and stores the result.

    Contract:
        - non-callable spells are returned as-is and stored in the frame.
    """
    root_spell = _make_spell(
        spell_id="root",
        spell="root-value",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    frame = ResolutionFrame()
    engine, _, _ = _make_engine(root_spell=root_spell, frame=frame)
    result = engine.run()
    assert result == "root-value"
    assert frame.get_result(root_spell.spell_index.current) == "root-value"


def test_run_root_only_unique_per_conduit_holds_creations_lock() -> None:
    """
    Verify unique_per_conduit holds the caller creations lock during construction.

    Contract:
        - creations lock is held while the root spell callable runs.
    """
    creations, _ = _make_creations()
    creations_lock = _TrackingLock()
    creations._lock = creations_lock

    def build() -> str:
        assert creations_lock.locked is True
        return "root-value"

    root_spell = _make_spell(
        spell_id="root",
        spell=build,
        existence=Existence.unique_per_conduit,
    )
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        creations=creations,
        caller_creations=creations,
    )
    assert engine.run() == "root-value"


def test_run_root_only_shared_unique_holds_spell_lock() -> None:
    """
    Verify shared unique existence holds the spell lock during construction.

    Contract:
        - spell lock is held while the root spell callable runs.
        - creations lock is not held during construction.
    """
    creations, _ = _make_creations()
    creations_lock = _TrackingLock()
    creations._lock = creations_lock
    spell_lock = _TrackingLock()

    def build() -> str:
        assert spell_lock.locked is True
        assert creations_lock.locked is False
        return "root-value"

    root_spell = _make_spell(
        spell_id="root",
        spell=build,
        existence=Existence.unique,
        owner_creations=creations,
    )
    root_spell._lock = spell_lock
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        creations=creations,
        caller_creations=creations,
        owner_creations=creations,
    )
    assert engine.run() == "root-value"


def test_run_root_only_skips_spell_lock_when_caller_creations_lock_held() -> None:
    """
    Verify shared unique skips the spell lock when caller creations are held.

    Contract:
        - spell lock is not acquired when caller_creations_lock_held is True
          and the spell resolves against the same creations container.
        - creations lock remains held during construction.
    """
    creations, _ = _make_creations()
    creations_lock = _TrackingLock()
    creations._lock = creations_lock
    spell_lock = _TrackingLock()

    def build() -> str:
        assert spell_lock.locked is False
        assert creations_lock.locked is True
        return "root-value"

    root_spell = _make_spell(
        spell_id="root",
        spell=build,
        existence=Existence.unique,
        owner_creations=creations,
    )
    root_spell._lock = spell_lock
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        creations=creations,
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=True,
    )
    with creations._lock:
        assert engine.run() == "root-value"


def test_run_root_only_uses_args_and_kwargs_overrides() -> None:
    """
    Verify root-only execution applies __args__ and keyword overrides.

    Contract:
        - positional and keyword overrides are passed to the callable.
    """
    def build(a: int, b: int, *, c: int) -> tuple[int, int, int]:
        return a, b, c

    root_spell = _make_spell(spell_id="root", spell=build)
    frame = ResolutionFrame(overrides={"__args__": [1, 2], "c": 3})
    engine, _, _ = _make_engine(root_spell=root_spell, frame=frame)
    assert engine.run() == (1, 2, 3)


def test_run_root_only_ignores_string_args_override() -> None:
    """
    Verify string __args__ overrides are ignored.

    Contract:
        - __args__ string values are not treated as positional args.
    """
    def build(*, c: int) -> int:
        return c

    root_spell = _make_spell(spell_id="root", spell=build)
    frame = ResolutionFrame(overrides={"__args__": "abc", "c": 7})
    engine, _, _ = _make_engine(root_spell=root_spell, frame=frame)
    assert engine.run() == 7


def test_run_root_only_wraps_callable_error() -> None:
    """
    Verify root-only errors are wrapped in MeldExecutionError.

    Contract:
        - callable exceptions are wrapped with spell identity metadata.
    """
    def boom() -> None:
        raise ValueError("broken")

    root_spell = _make_spell(spell_id="root", spell=boom)
    engine, _, _ = _make_engine(root_spell=root_spell)
    with pytest.raises(MeldExecutionError) as exc_info:
        engine.run()
    assert exc_info.value.spell_id == root_spell.spell_index.current
    assert isinstance(exc_info.value.inner, ValueError)


def test_run_root_only_respects_cancellation_event() -> None:
    """
    Verify root-only execution honors cancellation signals.

    Contract:
        - when cancellation is set, run raises OperationCancelledError.
    """
    signal = CancellationEventSignal()
    signal.cancel()
    root_spell = _make_spell(spell_id="root", spell=lambda: "never")
    engine, _, _ = _make_engine(root_spell=root_spell, cancel_event=signal.event)
    with pytest.raises(OperationCancelledError):
        engine.run()
    signal.cleanup()


def test_construct_spell_existing_creation_requires_user_object() -> None:
    """
    Verify existing-creation spells require a user_created_object.

    Contract:
        - missing user_created_object raises MeldExecutionError.
    """
    engine, _, _ = _make_engine()
    spell = _make_spell(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=None,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    with pytest.raises(MeldExecutionError, match="EXISTING_CREATION"):
        engine._construct_spell(spell, {})


def test_construct_spell_existing_creation_returns_object() -> None:
    """
    Verify existing-creation spells return their backing object.

    Contract:
        - user_created_object is returned for existing-creation spells.
    """
    engine, _, _ = _make_engine()
    instance = object()
    spell = _make_spell(
        spell_id="spell-1",
        is_existing_creation=True,
        user_created_object=instance,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    assert engine._construct_spell(spell, {}) is instance


def test_construct_spell_value_spell_returns_value() -> None:
    """
    Verify value spells return their spell attribute unchanged.

    Contract:
        - non-callable spells yield the raw value.
    """
    engine, _, _ = _make_engine()
    spell = _make_spell(
        spell_id="spell-1",
        spell="value",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    assert engine._construct_spell(spell, {}) == "value"


def test_construct_spell_callable_invoked() -> None:
    """
    Verify callable spells receive keyword arguments.

    Contract:
        - kwargs are passed to the callable spell.
    """
    def build(*, dep: str) -> str:
        return dep

    engine, _, _ = _make_engine()
    spell = _make_spell(spell_id="spell-1", spell=build)
    assert engine._construct_spell(spell, {"dep": "value"}) == "value"


def test_construct_spell_wraps_callable_error() -> None:
    """
    Verify callable spell failures are wrapped.

    Contract:
        - callable exceptions are wrapped in MeldExecutionError.
    """
    def boom() -> None:
        raise RuntimeError("fail")

    engine, _, _ = _make_engine()
    spell = _make_spell(spell_id="spell-1", spell=boom)
    with pytest.raises(MeldExecutionError) as exc_info:
        engine._construct_spell(spell, {})
    assert isinstance(exc_info.value.inner, RuntimeError)


def test_build_kwargs_returns_empty_when_node_missing() -> None:
    """
    Verify build_kwargs returns empty when the node is absent.

    Contract:
        - missing nodes produce empty kwargs.
    """
    engine, _, _ = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    assert engine._build_kwargs_for_node(
        node_id="missing",
        dag=dag,
        override_map={},
    ) == {}


def test_build_kwargs_applies_override_map_for_node() -> None:
    """
    Verify build_kwargs applies override_map values for a node.

    Contract:
        - override_map entries become kwargs for matching node_id.
    """
    engine, _, _ = _make_engine()
    dag = _make_dag_with_nodes(["node-1"])
    override_map = {_make_socket_ref("node-1", "dep"): "override"}
    kwargs = engine._build_kwargs_for_node(
        node_id="node-1",
        dag=dag,
        override_map=override_map,
    )
    assert kwargs == {"dep": "override"}


def test_build_kwargs_uses_topology_sockets() -> None:
    """
    Verify topology sockets drive dependency injection.

    Contract:
        - target_spell_ids are resolved into kwargs values.
    """
    engine, _, frame = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name=None)
    frame.set_result("parent", "parent-value")
    topology = _make_topology([_make_socket("dep", ["parent"])])
    system_states = _SystemStatesStub({"child": topology})
    engine._system_states = system_states
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map={},
    )
    assert kwargs == {"dep": "parent-value"}


def test_build_kwargs_uses_incoming_params_when_topology_missing() -> None:
    """
    Verify incoming_params resolve dependencies when no topology exists.

    Contract:
        - incoming_params mappings are used in absence of topology.
    """
    engine, _, frame = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")
    frame.set_result("parent", "parent-value")
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map={},
    )
    assert kwargs == {"dep": "parent-value"}


def test_build_kwargs_uses_incoming_params_when_topology_errors() -> None:
    """
    Verify incoming_params are used if topology lookup fails.

    Contract:
        - topology lookup failures do not prevent dependency injection.
    """
    engine, _, frame = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")
    frame.set_result("parent", "parent-value")
    engine._system_states = _SystemStatesStub({}, raise_on={"child"})
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map={},
    )
    assert kwargs == {"dep": "parent-value"}


def test_build_kwargs_injects_list_for_multiple_dependencies() -> None:
    """
    Verify multiple dependencies inject as a list.

    Contract:
        - multiple parents map to a list of resolved values.
    """
    engine, _, frame = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "child", param_name="deps")
    dag.add_dependency("b", "child", param_name="deps")
    frame.set_result("a", "value-a")
    frame.set_result("b", "value-b")
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map={},
    )
    assert kwargs == {"deps": ["value-a", "value-b"]}


def test_build_kwargs_skips_injection_when_override_present() -> None:
    """
    Verify overrides prevent dependency injection for the same param.

    Contract:
        - overridden parameters do not require dependency results.
    """
    engine, _, _ = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")
    override_map = {_make_socket_ref("child", "dep"): "override"}
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map=override_map,
    )
    assert kwargs == {"dep": "override"}


def test_build_kwargs_raises_when_dependency_missing() -> None:
    """
    Verify build_kwargs raises when a dependency result is missing.

    Contract:
        - missing parent results raise MeldExecutionError.
    """
    engine, _, _ = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")
    with pytest.raises(MeldExecutionError, match="Dependency"):
        engine._build_kwargs_for_node(
            node_id="child",
            dag=dag,
            override_map={},
        )


def test_get_existing_creation_returns_none_for_many() -> None:
    """
    Verify Existence.many never reuses an instance.

    Contract:
        - many existence always returns None.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(spell_id="spell-1", existence=Existence.many)
    assert engine._get_existing_creation(spell) is None


def test_get_existing_creation_returns_unique_from_creations() -> None:
    """
    Verify unique creations are reused from Creations.

    Contract:
        - Existence.unique returns the stored instance.
    """
    creations, _ = _make_creations()
    instance = object()
    creations.add_unique("spell-1", instance)
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique)
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_prefers_caller_for_unique_per_conduit() -> None:
    """
    Verify per-conduit reuse prefers caller creations over owner creations.

    Contract:
        - unique_per_conduit reuse checks caller creations first.
    """
    caller_creations, _ = _make_creations(conduit_id="caller")
    owner_creations, _ = _make_creations(conduit_id="owner")
    caller_instance = object()
    owner_instance = object()
    caller_creations.add_unique_per_scope("spell-1", caller_instance)
    owner_creations.add_unique_per_scope("spell-1", owner_instance)
    engine, _, _ = _make_engine(
        creations=caller_creations,
        caller_creations=caller_creations,
        owner_creations=owner_creations,
    )
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique_per_conduit)
    assert engine._get_existing_creation(spell) is caller_instance


def test_get_existing_creation_returns_unique_per_conduit_from_creations() -> None:
    """
    Verify unique-per-conduit creations are reused.

    Contract:
        - Existence.unique_per_conduit returns the stored instance.
    """
    creations, _ = _make_creations()
    instance = object()
    creations.add_unique_per_scope("spell-1", instance)
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique_per_conduit)
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_prefers_owner_for_unique() -> None:
    """
    Verify shared reuse prefers owner creations over caller creations.

    Contract:
        - unique reuse checks owner creations first.
    """
    caller_creations, _ = _make_creations(conduit_id="caller")
    owner_creations, _ = _make_creations(conduit_id="owner")
    caller_instance = object()
    owner_instance = object()
    caller_creations.add_unique("spell-1", caller_instance)
    owner_creations.add_unique("spell-1", owner_instance)
    engine, _, _ = _make_engine(
        creations=caller_creations,
        caller_creations=caller_creations,
        owner_creations=owner_creations,
    )
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique)
    assert engine._get_existing_creation(spell) is owner_instance


def test_get_existing_creation_returns_unique_per_cluster_from_creations() -> None:
    """
    Verify unique-per-cluster creations are reused.

    Contract:
        - Existence.unique_per_conduit_cluster returns the stored instance.
    """
    creations, _ = _make_creations()
    instance = object()
    creations.add_unique_per_cluster("spell-1", instance)
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit_cluster,
    )
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_returns_unique_per_lineage_from_creations() -> None:
    """
    Verify unique-per-lineage creations are reused.

    Contract:
        - Existence.unique_per_conduit_lineage returns the stored instance.
    """
    creations, _ = _make_creations()
    instance = object()
    creations.add_unique_per_lineage("spell-1", instance)
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit_lineage,
    )
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_raises_when_spellspace_missing() -> None:
    """
    Verify spellspace reuse requires an active SpellSpace.

    Contract:
        - Existence.unique_per_spell_space raises when no spellspace is active.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    with pytest.raises(SpellSpaceScopeError, match="SpellSpace"):
        engine._get_existing_creation(spell)


def test_get_existing_creation_raises_when_spellspace_owner_mismatch() -> None:
    """
    Verify spellspace reuse enforces owner identity.

    Contract:
        - active spellspace owned by another conduit raises SpellSpaceScopeError.
    """
    creations, conduit = _make_creations()
    other_conduit = _ConduitStub("other", ConduitState.normal)
    conduit._spellspace = SpellSpace(other_conduit)
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    with pytest.raises(SpellSpaceScopeError, match="different conduit"):
        engine._get_existing_creation(spell)


def test_get_existing_creation_returns_spellspace_creation() -> None:
    """
    Verify spellspace reuse returns registered instances.

    Contract:
        - spellspace creations return their stored instance.
    """
    creations, conduit = _make_creations()
    conduit._spellspace = SpellSpace(conduit)
    instance = object()
    creations.register_spellspace_creation(conduit._spellspace.id, "spell-1", instance)
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_lesser_unique_per_scope() -> None:
    """
    Verify lesser creations reuse unique-per-conduit instances.

    Contract:
        - LesserCreations unique_per_scope is reused.
    """
    lesser, _, _ = _make_lesser_creations()
    instance = object()
    lesser.add_unique_per_scope("spell-1", instance)
    engine, _, _ = _make_engine(creations=lesser)
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique_per_conduit)
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_lesser_parent_unique() -> None:
    """
    Verify lesser creations reuse parent unique instances.

    Contract:
        - parent Creations unique instances are reused by lesser scope.
    """
    parent, _ = _make_creations()
    instance = object()
    parent.add_unique("spell-1", instance)
    lesser, _, _ = _make_lesser_creations(parent_creations=parent)
    engine, _, _ = _make_engine(creations=lesser)
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique)
    assert engine._get_existing_creation(spell) is instance


def test_get_existing_creation_lesser_spellspace_missing_raises() -> None:
    """
    Verify lesser spellspace reuse requires an active SpellSpace.

    Contract:
        - missing spellspace raises SpellSpaceScopeError for lesser scope.
    """
    parent, _ = _make_creations()
    lesser, _, _ = _make_lesser_creations(parent_creations=parent)
    engine, _, _ = _make_engine(creations=lesser)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    with pytest.raises(SpellSpaceScopeError, match="SpellSpace"):
        engine._get_existing_creation(spell)


def test_get_existing_creation_unknown_creations_returns_none() -> None:
    """
    Verify unknown creations types return None.

    Contract:
        - unsupported creations containers yield no reuse.
    """
    engine, _, _ = _make_engine(creations=SimpleNamespace())
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique)
    assert engine._get_existing_creation(spell) is None


@pytest.mark.parametrize(
    ("existence", "expected_scope"),
    [
        (Existence.unique, "unique"),
        (Existence.unique_per_conduit, "unique_per_scope"),
        (Existence.many, "many"),
        (Existence.unique_per_conduit_cluster, "unique_per_cluster"),
        (Existence.unique_per_conduit_lineage, "unique_per_lineage"),
    ],
)
def test_register_spell_creations_scopes(
    existence: Existence,
    expected_scope: str,
) -> None:
    """
    Verify register_spell routes to the correct Creations scope.

    Contract:
        - each existence maps to its corresponding creations bucket.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(creations=creations)
    instance = object()
    spell = _make_spell(spell_id="spell-1", existence=existence)
    engine._register_spell(spell, instance)
    extracted = creations.extract_spell_creations("spell-1")
    assert len(extracted) == 1
    assert extracted[0]["scope"] == expected_scope
    assert extracted[0]["creation"].value is instance


def test_register_spell_spellspace_in_creations() -> None:
    """
    Verify spellspace registration stores in the spellspace bucket.

    Contract:
        - Existence.unique_per_spell_space registers under the active spellspace.
    """
    creations, conduit = _make_creations()
    conduit._spellspace = SpellSpace(conduit)
    engine, _, _ = _make_engine(creations=creations)
    instance = object()
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    engine._register_spell(spell, instance)
    extracted = creations.extract_spell_creations("spell-1")
    assert extracted[0]["scope"] == "spellspace"
    assert extracted[0]["spellspace_id"] == conduit._spellspace.id
    assert extracted[0]["creation"].value is instance


def test_register_spell_spellspace_missing_raises() -> None:
    """
    Verify spellspace registration requires an active SpellSpace.

    Contract:
        - missing spellspace raises SpellSpaceScopeError.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    with pytest.raises(SpellSpaceScopeError, match="SpellSpace"):
        engine._register_spell(spell, object())


def test_register_spell_spellspace_owner_mismatch_raises() -> None:
    """
    Verify spellspace registration enforces owner identity.

    Contract:
        - active spellspace owned by another conduit raises SpellSpaceScopeError.
    """
    creations, conduit = _make_creations()
    conduit._spellspace = SpellSpace(_ConduitStub("other", ConduitState.normal))
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    with pytest.raises(SpellSpaceScopeError, match="different conduit"):
        engine._register_spell(spell, object())


@pytest.mark.parametrize(
    "existence",
    [
        Existence.unique_per_conduit,
        Existence.many,
    ],
)
def test_register_spell_lesser_local_scopes(existence: Existence) -> None:
    """
    Verify lesser creations register local-scope existences.

    Contract:
        - unique_per_conduit and many are stored in LesserCreations.
    """
    lesser, _, _ = _make_lesser_creations()
    engine, _, _ = _make_engine(creations=lesser)
    instance = object()
    spell = _make_spell(spell_id="spell-1", existence=existence)
    engine._register_spell(spell, instance)
    if existence is Existence.unique_per_conduit:
        assert lesser._unique_per_scope["spell-1"].value is instance
    else:
        assert lesser._many["spell-1"][0].value is instance


@pytest.mark.parametrize(
    ("existence", "expected_scope"),
    [
        (Existence.unique, "unique"),
        (Existence.unique_per_conduit_cluster, "unique_per_cluster"),
        (Existence.unique_per_conduit_lineage, "unique_per_lineage"),
    ],
)
def test_register_spell_lesser_parent_scopes(
    existence: Existence,
    expected_scope: str,
) -> None:
    """
    Verify lesser creations forward parent-scoped existences.

    Contract:
        - parent Creations receives unique/cluster/lineage registrations.
    """
    parent, _ = _make_creations()
    lesser, _, _ = _make_lesser_creations(parent_creations=parent)
    engine, _, _ = _make_engine(creations=lesser)
    instance = object()
    spell = _make_spell(spell_id="spell-1", existence=existence)
    engine._register_spell(spell, instance)
    extracted = parent.extract_spell_creations("spell-1")
    assert extracted[0]["scope"] == expected_scope
    assert extracted[0]["creation"].value is instance


def test_register_spell_lesser_spellspace_success() -> None:
    """
    Verify lesser spellspace registration stores in the lesser bucket.

    Contract:
        - lesser spellspace registrations use LesserCreations buckets.
    """
    parent, _ = _make_creations()
    lesser, conduit, _ = _make_lesser_creations(parent_creations=parent)
    conduit._spellspace = SpellSpace(conduit)
    engine, _, _ = _make_engine(creations=lesser)
    instance = object()
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    engine._register_spell(spell, instance)
    creation = lesser.get_spellspace_creation(conduit._spellspace.id, "spell-1")
    assert creation.value is instance


def test_register_spell_lesser_spellspace_missing_raises() -> None:
    """
    Verify lesser spellspace registration requires an active SpellSpace.

    Contract:
        - missing spellspace raises SpellSpaceScopeError.
    """
    parent, _ = _make_creations()
    lesser, _, _ = _make_lesser_creations(parent_creations=parent)
    engine, _, _ = _make_engine(creations=lesser)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_spell_space,
    )
    with pytest.raises(SpellSpaceScopeError, match="SpellSpace"):
        engine._register_spell(spell, object())


def test_run_blueprint_missing_spell_lookup_raises() -> None:
    """
    Verify blueprint execution rejects missing spell lookups.

    Contract:
        - missing non-root spell_lookup entries raise MeldExecutionError.
        - the root spell can be used even when not present in spell_lookup.
    """
    dag = _make_dag_with_nodes(["node-1", "missing-node"])
    blueprint = _make_blueprint("node-1", dag, ["node-1", "missing-node"])
    root_spell = _make_spell(spell_id="node-1")
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={},
    )
    with pytest.raises(MeldExecutionError, match="not found"):
        engine.run()


def test_run_blueprint_reuses_existing_creation() -> None:
    """
    Verify blueprint execution reuses existing creations.

    Contract:
        - existing instances bypass construction and are returned.
    """
    creations, _ = _make_creations()
    instance = object()
    creations.add_unique("root", instance)
    dag = _make_dag_with_nodes(["root"])
    blueprint = _make_blueprint("root", dag, ["root"])

    def boom() -> None:
        raise RuntimeError("should not be called")

    root_spell = _make_spell(spell_id="root", spell=boom)
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        creations=creations,
        blueprint=blueprint,
        spell_lookup={"root": root_spell},
    )
    assert engine.run() is instance


def test_run_blueprint_injects_dependency_from_topology() -> None:
    """
    Verify blueprint execution injects topology-based dependencies.

    Contract:
        - topology sockets provide dependency values for constructors.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name=None)
    topology = _make_topology([_make_socket("dep", ["parent"])])
    system_states = _SystemStatesStub({"child": topology})

    parent_spell = _make_spell(
        spell_id="parent",
        spell="parent-value",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        existence=Existence.many,
    )

    def build(*, dep: str) -> str:
        return dep

    child_spell = _make_spell(spell_id="child", spell=build, existence=Existence.many)
    blueprint = _make_blueprint("child", dag, ["parent", "child"])
    engine, _, _ = _make_engine(
        root_spell=child_spell,
        blueprint=blueprint,
        spell_lookup={"parent": parent_spell, "child": child_spell},
        system_states=system_states,
    )
    assert engine.run() == "parent-value"


def test_run_blueprint_injects_dependency_from_incoming_params() -> None:
    """
    Verify blueprint execution uses incoming_params without topology.

    Contract:
        - incoming_params wiring injects dependency values.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")

    parent_spell = _make_spell(
        spell_id="parent",
        spell="parent-value",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        existence=Existence.many,
    )

    def build(*, dep: str) -> str:
        return dep

    child_spell = _make_spell(spell_id="child", spell=build, existence=Existence.many)
    blueprint = _make_blueprint("child", dag, ["parent", "child"])
    engine, _, _ = _make_engine(
        root_spell=child_spell,
        blueprint=blueprint,
        spell_lookup={"parent": parent_spell, "child": child_spell},
    )
    assert engine.run() == "parent-value"


def test_run_blueprint_injects_list_for_multiple_parents() -> None:
    """
    Verify blueprint execution injects lists for multi-parent params.

    Contract:
        - multiple parents result in list injection.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "child", param_name="deps")
    dag.add_dependency("b", "child", param_name="deps")

    parent_a = _make_spell(
        spell_id="a",
        spell="value-a",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        existence=Existence.many,
    )
    parent_b = _make_spell(
        spell_id="b",
        spell="value-b",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        existence=Existence.many,
    )

    def build(*, deps: list[str]) -> list[str]:
        return deps

    child_spell = _make_spell(spell_id="child", spell=build, existence=Existence.many)
    blueprint = _make_blueprint("child", dag, ["a", "b", "child"])
    engine, _, _ = _make_engine(
        root_spell=child_spell,
        blueprint=blueprint,
        spell_lookup={"a": parent_a, "b": parent_b, "child": child_spell},
    )
    assert engine.run() == ["value-a", "value-b"]


def test_run_blueprint_override_map_takes_precedence() -> None:
    """
    Verify override_map values override dependency injection.

    Contract:
        - explicit overrides win over DAG-derived values.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")

    parent_spell = _make_spell(
        spell_id="parent",
        spell="parent-value",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        existence=Existence.many,
    )

    def build(*, dep: str) -> str:
        return dep

    child_spell = _make_spell(spell_id="child", spell=build, existence=Existence.many)
    blueprint = _make_blueprint("child", dag, ["parent", "child"])
    override_map = {_make_socket_ref("child", "dep"): "override"}
    engine, _, _ = _make_engine(
        root_spell=child_spell,
        blueprint=blueprint,
        spell_lookup={"parent": parent_spell, "child": child_spell},
        override_map=override_map,
    )
    assert engine.run() == "override"


def test_run_blueprint_missing_dependency_raises() -> None:
    """
    Verify blueprint execution fails when dependencies are missing.

    Contract:
        - missing parent results raise MeldExecutionError.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")

    def build(*, dep: str) -> str:
        return dep

    child_spell = _make_spell(spell_id="child", spell=build, existence=Existence.many)
    blueprint = _make_blueprint("child", dag, ["child"])
    engine, _, _ = _make_engine(
        root_spell=child_spell,
        blueprint=blueprint,
        spell_lookup={"child": child_spell},
    )
    with pytest.raises(MeldExecutionError, match="Dependency"):
        engine.run()


def test_run_blueprint_root_missing_fallback_constructs_root() -> None:
    """
    Verify blueprint execution falls back to root-only when root missing.

    Contract:
        - missing root result triggers root-only construction.
    """
    dag = _make_dag_with_nodes(["node-1"])
    blueprint = _make_blueprint("root", dag, ["node-1"])
    node_spell = _make_spell(
        spell_id="node-1",
        spell="node-value",
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        existence=Existence.many,
    )
    root_spell = _make_spell(spell_id="root", spell=lambda: "root-value")
    engine, _, frame = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={"node-1": node_spell},
    )
    assert engine.run() == "root-value"
    assert frame.get_result("root") == "root-value"


def test_run_blueprint_registers_constructed_spell() -> None:
    """
    Verify blueprint execution registers constructed spells.

    Contract:
        - constructed instances are registered with Creations.
    """
    creations, _ = _make_creations()
    dag = _make_dag_with_nodes(["root"])
    blueprint = _make_blueprint("root", dag, ["root"])

    def build() -> str:
        return "root-value"

    root_spell = _make_spell(
        spell_id="root",
        spell=build,
        existence=Existence.unique,
    )
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        creations=creations,
        blueprint=blueprint,
        spell_lookup={"root": root_spell},
    )
    assert engine.run() == "root-value"
    extracted = creations.extract_spell_creations("root")
    assert extracted[0]["scope"] == "unique"


def test_run_blueprint_respects_cancellation_event() -> None:
    """
    Verify blueprint execution honors cancellation signals.

    Contract:
        - when cancellation is set, run raises OperationCancelledError.
    """
    signal = CancellationEventSignal()
    signal.cancel()
    dag = _make_dag_with_nodes(["root"])
    blueprint = _make_blueprint("root", dag, ["root"])
    root_spell = _make_spell(spell_id="root", spell=lambda: "never")
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={"root": root_spell},
        cancel_event=signal.event,
    )
    with pytest.raises(OperationCancelledError):
        engine.run()
    signal.cleanup()


def test_run_blueprint_cancels_between_nodes() -> None:
    """
    Verify blueprint execution stops between nodes when cancellation is triggered.

    Contract:
        - cancellation set during the first node prevents the next node from running.
        - completed node results remain stored in the ResolutionFrame.
    """
    signal = CancellationEventSignal()
    dag = _make_dag_with_nodes(["first", "second"])
    blueprint = _make_blueprint("second", dag, ["first", "second"])

    def build_first() -> str:
        signal.cancel()
        return "first-value"

    first_spell = _make_spell(spell_id="first", spell=build_first, existence=Existence.many)
    second_spell = _make_spell(spell_id="second", spell=lambda: "second-value", existence=Existence.many)
    engine, _, frame = _make_engine(
        root_spell=second_spell,
        blueprint=blueprint,
        spell_lookup={"first": first_spell, "second": second_spell},
        cancel_event=signal.event,
    )
    with pytest.raises(OperationCancelledError):
        engine.run()
    assert frame.has_result("first") is True
    assert frame.has_result("second") is False
    signal.cleanup()


def test_run_blueprint_executes_orphan_ordered_node() -> None:
    """
    Verify ordered nodes outside the root path still execute.

    Contract:
        - orphan nodes in the ordered list are constructed and stored in the frame.
        - the root spell result is still returned.
    """
    dag = _make_dag_with_nodes(["first", "second"])
    blueprint = _make_blueprint("second", dag, ["first", "second"])

    first_spell = _make_spell(spell_id="first", spell=lambda: "first-value", existence=Existence.many)
    second_spell = _make_spell(spell_id="second", spell=lambda: "second-value", existence=Existence.many)

    engine, _, frame = _make_engine(
        root_spell=second_spell,
        blueprint=blueprint,
        spell_lookup={"first": first_spell, "second": second_spell},
    )
    assert engine.run() == "second-value"
    assert frame.get_result("first") == "first-value"


def test_build_kwargs_merges_topology_and_incoming_params() -> None:
    """
    Verify build_kwargs merges partial topology with incoming_params.

    Contract:
        - topology sockets contribute known parents.
        - incoming_params adds missing parents to the same parameter list.
    """
    engine, _, frame = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "child", param_name="dep")
    dag.add_dependency("b", "child", param_name="dep")
    frame.set_result("a", "value-a")
    frame.set_result("b", "value-b")
    topology = _make_topology([_make_socket("dep", ["a"])])
    engine._system_states = _SystemStatesStub({"child": topology})
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map={},
    )
    assert kwargs == {"dep": ["value-a", "value-b"]}


def test_register_spell_unknown_creations_is_noop() -> None:
    """
    Verify register_spell ignores unsupported creations containers.

    Contract:
        - unsupported creations types are ignored without raising.
    """
    engine, _, _ = _make_engine(creations=SimpleNamespace())
    spell = _make_spell(spell_id="spell-1", existence=Existence.unique)
    assert engine._register_spell(spell, object()) is None


def test_build_kwargs_merges_override_and_dependency_params() -> None:
    """
    Verify build_kwargs merges overrides with dependency injection across params.

    Contract:
        - overridden params stay fixed.
        - other params still receive dependency values.
    """
    engine, _, frame = _make_engine()
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")
    frame.set_result("parent", "parent-value")
    override_map = {_make_socket_ref("child", "override_param"): "override"}
    kwargs = engine._build_kwargs_for_node(
        node_id="child",
        dag=dag,
        override_map=override_map,
    )
    assert kwargs == {"override_param": "override", "dep": "parent-value"}


def test_run_blueprint_reuse_stores_existing_result() -> None:
    """
    Verify reused instances are stored in the ResolutionFrame.

    Contract:
        - when reuse happens, the existing instance is stored for the node id.
    """
    creations, _ = _make_creations()
    instance = object()
    creations.add_unique("root", instance)
    dag = _make_dag_with_nodes(["root"])
    blueprint = _make_blueprint("root", dag, ["root"])
    root_spell = _make_spell(spell_id="root", spell=lambda: "unused")
    engine, _, frame = _make_engine(
        root_spell=root_spell,
        creations=creations,
        blueprint=blueprint,
        spell_lookup={"root": root_spell},
    )
    assert engine.run() is instance
    assert frame.get_result("root") is instance


def test_construct_root_only_accepts_tuple_args() -> None:
    """
    Verify root-only construction accepts tuple positional overrides.

    Contract:
        - tuple __args__ values are treated as positional arguments.
    """
    def build(a: int, b: int) -> tuple[int, int]:
        return a, b

    root_spell = _make_spell(spell_id="root", spell=build)
    frame = ResolutionFrame(overrides={"__args__": (1, 2)})
    engine, _, _ = _make_engine(root_spell=root_spell, frame=frame)
    assert engine._construct_root_only() == (1, 2)


def test_resolve_spell_instance_shared_unique_concurrent_reuses_single_creation() -> None:
    """
    Verify shared unique existence constructs once under concurrent callers.

    Contract:
        - only one instance is constructed.
        - both callers receive the same instance.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(
        creations=creations,
        caller_creations=creations,
        owner_creations=creations,
    )
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=creations,
    )
    barrier = Barrier(2)
    lock = Lock()
    results: list[tuple[Any, bool]] = []
    errors: list[Exception] = []
    construct_calls = 0

    def construct() -> object:
        nonlocal construct_calls
        with lock:
            construct_calls += 1
        return object()

    def worker() -> None:
        try:
            barrier.wait(timeout=5)
            instance, created = engine._resolve_spell_instance(
                spell,
                construct_fn=construct,
            )
            with lock:
                results.append((instance, created))
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert construct_calls == 1
    assert len(results) == 2
    instances = {id(instance) for instance, _ in results}
    assert len(instances) == 1
    assert sum(1 for _, created in results if created) == 1


def test_resolve_spell_instance_unique_per_conduit_concurrent_reuses_single_creation() -> None:
    """
    Verify unique_per_conduit constructs once per conduit under concurrency.

    Contract:
        - only one instance is constructed for the caller creations.
        - both callers receive the same instance.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique_per_conduit,
        owner_creations=creations,
    )
    barrier = Barrier(2)
    lock = Lock()
    results: list[tuple[Any, bool]] = []
    errors: list[Exception] = []
    construct_calls = 0

    def construct() -> object:
        nonlocal construct_calls
        with lock:
            construct_calls += 1
        return object()

    def worker() -> None:
        try:
            barrier.wait(timeout=5)
            instance, created = engine._resolve_spell_instance(
                spell,
                construct_fn=construct,
            )
            with lock:
                results.append((instance, created))
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert construct_calls == 1
    assert len(results) == 2
    instances = {id(instance) for instance, _ in results}
    assert len(instances) == 1
    assert sum(1 for _, created in results if created) == 1


def test_resolve_spell_instance_many_concurrent_creates_distinct_instances() -> None:
    """
    Verify Existence.many constructs distinct instances under concurrency.

    Contract:
        - each caller receives a new instance.
        - all calls report created=True.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(creations=creations)
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.many,
        owner_creations=creations,
    )
    barrier = Barrier(2)
    lock = Lock()
    results: list[tuple[Any, bool]] = []
    errors: list[Exception] = []

    def construct() -> object:
        return object()

    def worker() -> None:
        try:
            barrier.wait(timeout=5)
            instance, created = engine._resolve_spell_instance(
                spell,
                construct_fn=construct,
            )
            with lock:
                results.append((instance, created))
        except Exception as exc:
            with lock:
                errors.append(exc)

    threads = [Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(results) == 2
    instances = {id(instance) for instance, _ in results}
    assert len(instances) == 2
    assert all(created for _, created in results)
    creations_snapshot = creations.extract_spell_creations("spell-1")
    assert len(creations_snapshot) == 2


def test_resolve_spell_instance_shared_unique_prefers_owner_creations() -> None:
    """
    Verify shared unique uses owner creations when caller differs.

    Contract:
        - instance registers in owner creations for shared lifetimes.
        - caller creations remain unchanged.
    """
    caller_creations, _ = _make_creations(conduit_id="caller")
    owner_creations, _ = _make_creations(conduit_id="owner")
    engine, _, _ = _make_engine(
        creations=caller_creations,
        caller_creations=caller_creations,
        owner_creations=owner_creations,
    )
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=owner_creations,
    )
    instance, created = engine._resolve_spell_instance(
        spell,
        construct_fn=lambda: object(),
    )
    assert created is True
    owner_snapshot = owner_creations.extract_spell_creations("spell-1")
    caller_snapshot = caller_creations.extract_spell_creations("spell-1")
    assert len(owner_snapshot) == 1
    assert owner_snapshot[0]["creation"].value is instance
    assert caller_snapshot == []


def test_resolve_spell_instance_shared_unique_skips_spell_lock_when_caller_lock_held() -> None:
    """
    Verify shared unique skips the spell lock when caller lock is already held.

    Contract:
        - spell lock is not acquired when caller_creations_lock_held is True.
    """
    creations, _ = _make_creations()
    engine, _, _ = _make_engine(
        creations=creations,
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=True,
    )
    spell = _make_spell(
        spell_id="spell-1",
        existence=Existence.unique,
        owner_creations=creations,
    )
    spell._lock = MagicMock()

    instance, created = engine._resolve_spell_instance(
        spell,
        construct_fn=lambda: object(),
    )

    assert created is True
    assert spell._lock.__enter__.called is False
    creations_snapshot = creations.extract_spell_creations("spell-1")
    assert creations_snapshot[0]["creation"].value is instance


def test_extend_occurrence_graph_with_ordered_nodes_noop_on_empty_order() -> None:
    """
    Verify ordered-node expansion is skipped when no ordered ids are provided.

    Contract:
        - Occurrence graph remains unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If ordered-node expansion mutates the graph.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id])
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(),
        dag=dag,
    )

    assert set(occurrence_graph.keys()) == {(root_id, ())}
    assert occurrence_graph[(root_id, ())] == {}


def test_extend_occurrence_graph_with_ordered_nodes_noop_on_none_dag() -> None:
    """
    Verify ordered-node expansion is skipped when the DAG is missing.

    Contract:
        - Occurrence graph is left unchanged when dag is None.
    Returns:
        None.
    Raises:
        AssertionError: If entries are added without a DAG.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    occurrence_graph = engine._build_occurrence_graph(
        dag=_make_dag_with_nodes([root_id]),
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan"),
        dag=None,
    )

    assert set(occurrence_graph.keys()) == {(root_id, ())}


@pytest.mark.parametrize("orphan_id", ("orphan-a", "orphan-b", "orphan-c"))
def test_extend_occurrence_graph_with_ordered_nodes_adds_orphan_nodes(
    orphan_id: str,
) -> None:
    """
    Verify ordered-node expansion adds missing orphan nodes as entrypoints.

    Contract:
        - Orphan nodes appear in the occurrence graph with empty paths.
    Returns:
        None.
    Raises:
        AssertionError: If orphan nodes are not added.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id, orphan_id])
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, orphan_id),
        dag=dag,
    )

    assert (orphan_id, ()) in occurrence_graph
    assert occurrence_graph[(orphan_id, ())] == {}


@pytest.mark.parametrize(
    ("param_name", "parent_ids"),
    (
        ("dep", ("b", "a")),
        ("socket", ("c", "a")),
    ),
)
def test_extend_occurrence_graph_with_ordered_nodes_adds_orphan_dependencies(
    param_name: str,
    parent_ids: tuple[str, ...],
) -> None:
    """
    Verify ordered-node expansion walks orphan dependencies in DAG order.

    Contract:
        - Orphan dependencies are added with the correct param path.
        - Parent ordering is sorted by parent id.
    Returns:
        None.
    Raises:
        AssertionError: If orphan dependencies are not expanded correctly.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    node_ids = [root_id, "orphan", *parent_ids]
    dag = _make_dag_with_nodes(node_ids)
    for parent_id in parent_ids:
        dag.add_dependency(parent_id, "orphan", param_name=param_name)
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan"),
        dag=dag,
    )

    deps = occurrence_graph[("orphan", ())][param_name]
    expected_parent_ids = sorted(parent_ids)
    assert [occurrence[0] for occurrence in deps] == expected_parent_ids
    assert all(occurrence[1] == (param_name,) for occurrence in deps)


def test_extend_occurrence_graph_with_ordered_nodes_adds_nested_orphan_dependencies() -> None:
    """
    Verify ordered-node expansion follows nested orphan dependency chains.

    Contract:
        - Dependencies discovered from orphan nodes are expanded recursively.
    Returns:
        None.
    Raises:
        AssertionError: If nested dependencies are missing.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id, "orphan", "mid", "leaf"])
    dag.add_dependency("mid", "orphan", param_name="mid")
    dag.add_dependency("leaf", "mid", param_name="leaf")
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan"),
        dag=dag,
    )

    assert ("mid", ("mid",)) in occurrence_graph
    assert ("leaf", ("mid", "leaf")) in occurrence_graph
    assert occurrence_graph[("orphan", ())]["mid"] == [("mid", ("mid",))]
    assert occurrence_graph[("mid", ("mid",))]["leaf"] == [("leaf", ("mid", "leaf"))]


def test_extend_occurrence_graph_with_ordered_nodes_uses_topology_for_orphan_dependencies() -> None:
    """
    Verify ordered-node expansion uses topology when available.

    Contract:
        - Topology sockets provide dependency occurrences for orphan nodes.
    Returns:
        None.
    Raises:
        AssertionError: If topology dependencies are not applied.
    """
    topology = _make_topology([_make_socket("dep", ["parent"])])
    system_states = _SystemStatesStub({"orphan": topology})
    engine, root_spell, _ = _make_engine(system_states=system_states)
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id, "orphan", "parent"])
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan"),
        dag=dag,
    )

    assert occurrence_graph[("orphan", ())]["dep"] == [("parent", ("dep",))]
    assert ("parent", ("dep",)) in occurrence_graph


def test_extend_occurrence_graph_with_ordered_nodes_skips_existing_occurrence() -> None:
    """
    Verify ordered-node expansion does not add duplicate occurrences.

    Contract:
        - Nodes already reachable from the root are not re-added as entrypoints.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate occurrences are added.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("child", root_id, param_name="dep")
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "child"),
        dag=dag,
    )

    occurrences = {occurrence for occurrence in occurrence_graph if occurrence[0] == "child"}
    assert occurrences == {("child", ("dep",))}


def test_extend_occurrence_graph_with_ordered_nodes_preserves_existing_dependencies() -> None:
    """
    Verify ordered-node expansion preserves existing dependency mappings.

    Contract:
        - Existing dependency lists remain unchanged after expansion.
    Returns:
        None.
    Raises:
        AssertionError: If existing dependencies are overwritten.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("child", root_id, param_name="dep")
    dag.add_node("orphan")
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "child", "orphan"),
        dag=dag,
    )

    assert occurrence_graph[(root_id, ())] == {"dep": [("child", ("dep",))]}


def test_run_blueprint_executes_ordered_nodes_in_order() -> None:
    """
    Verify blueprint execution respects the ordered node list.

    Contract:
        - Ordered nodes execute in the supplied order.
        - Root result is still returned.
    Returns:
        None.
    Raises:
        AssertionError: If execution order is not preserved.
    """
    order: list[str] = []
    root_spell = _make_spell(
        spell_id="root",
        spell=lambda **_: order.append("root") or "root-value",
        existence=Existence.many,
    )
    first_spell = _make_spell(
        spell_id="first",
        spell=lambda **_: order.append("first") or "first-value",
        existence=Existence.many,
    )
    second_spell = _make_spell(
        spell_id="second",
        spell=lambda **_: order.append("second") or "second-value",
        existence=Existence.many,
    )
    dag = _make_dag_with_nodes(["root", "first", "second"])
    blueprint = _make_blueprint("root", dag, ["first", "root", "second"])
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            "root": root_spell,
            "first": first_spell,
            "second": second_spell,
        },
    )

    assert engine.run() == "root-value"
    assert order == ["first", "root", "second"]


def test_run_blueprint_cancellation_after_orphan_stores_results() -> None:
    """
    Verify cancellation after an orphan node preserves completed results.

    Contract:
        - Nodes executed before cancellation remain stored in the frame.
    Returns:
        None.
    Raises:
        AssertionError: If completed results are missing after cancellation.
    """
    signal = CancellationEventSignal()
    root_spell = _make_spell(
        spell_id="root",
        spell=lambda **_: "root-value",
        existence=Existence.many,
    )
    orphan_spell = _make_spell(
        spell_id="orphan",
        spell=lambda **_: signal.cancel() or "orphan-value",
        existence=Existence.many,
    )
    dag = _make_dag_with_nodes(["root", "orphan"])
    blueprint = _make_blueprint("root", dag, ["root", "orphan"])
    engine, _, frame = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={"root": root_spell, "orphan": orphan_spell},
        cancel_event=signal.event,
    )

    with pytest.raises(OperationCancelledError):
        engine.run()

    assert frame.get_result("root") == "root-value"
    assert frame.get_result("orphan") == "orphan-value"
    signal.cleanup()


def test_run_blueprint_orphan_dependency_injected_from_dag() -> None:
    """
    Verify orphan nodes still receive DAG-based dependencies.

    Contract:
        - Dependencies for orphan nodes are injected when ordered ids include them.
    Returns:
        None.
    Raises:
        AssertionError: If orphan dependency wiring is missing.
    """
    root_spell = _make_spell(
        spell_id="root",
        spell=lambda **_: "root-value",
        existence=Existence.many,
    )
    parent_spell = _make_spell(
        spell_id="parent",
        spell=lambda **_: "parent-value",
        existence=Existence.many,
    )
    orphan_spell = _make_spell(
        spell_id="orphan",
        spell=lambda *, dep: f"orphan-{dep}",
        existence=Existence.many,
    )
    dag = _make_dag_with_nodes(["root", "parent", "orphan"])
    dag.add_dependency("parent", "orphan", param_name="dep")
    blueprint = _make_blueprint("root", dag, ["parent", "orphan", "root"])
    engine, _, frame = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            "root": root_spell,
            "parent": parent_spell,
            "orphan": orphan_spell,
        },
    )

    assert engine.run() == "root-value"
    assert frame.get_result("orphan") == "orphan-parent-value"


def test_resolve_mutation_override_targets_requires_dict() -> None:
    """
    Verify mutation override resolution rejects non-dict payloads.

    Contract:
        - mutation_override must be a dict.
    Returns:
        None.
    Raises:
        MeldExecutionError: If a non-dict payload is provided.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name="mutant",
        param_path=("mutant",),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    with pytest.raises(MeldExecutionError, match="mutation_override must be a dict"):
        engine._resolve_mutation_override_targets(
            mutation_override=["mutant"],
            dag_index=blueprint.dag_index,
        )


def test_resolve_mutation_override_targets_requires_dag_index() -> None:
    """
    Verify mutation override resolution requires a DagIndex.

    Contract:
        - Missing DagIndex raises MeldExecutionError.
    Returns:
        None.
    Raises:
        MeldExecutionError: If DagIndex is None.
    """
    engine, _, _ = _make_engine()
    with pytest.raises(MeldExecutionError, match="requires an active DagIndex"):
        engine._resolve_mutation_override_targets(
            mutation_override={"mutant": "target"},
            dag_index=None,
        )


@pytest.mark.parametrize(
    ("path_key", "param_path"),
    (
        ("mutant", ("mutant",)),
        ("left>mutant", ("left", "mutant")),
        ("left>right>mutant", ("left", "right", "mutant")),
    ),
)
def test_resolve_mutation_override_targets_path_matches_mutation_socket(
    path_key: str,
    param_path: tuple[str, ...],
) -> None:
    """
    Verify PATH mutation overrides resolve matching mutation sockets.

    Contract:
        - PATH keys resolve to mutation sockets at the exact path.
    Returns:
        None.
    Raises:
        AssertionError: If PATH resolution misses the socket.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name=param_path[-1],
        param_path=param_path,
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    resolved = engine._resolve_mutation_override_targets(
        mutation_override={path_key: "override-id"},
        dag_index=blueprint.dag_index,
    )

    assert len(resolved) == 1
    resolved_socket, target_id = resolved[0]
    assert resolved_socket.param_path == param_path
    assert target_id == "override-id"


@pytest.mark.parametrize(
    ("path_key", "param_path"),
    (
        ("mutant", ("mutant",)),
        ("left>mutant", ("left", "mutant")),
    ),
)
def test_resolve_mutation_override_targets_path_ignores_non_mutation_socket(
    path_key: str,
    param_path: tuple[str, ...],
) -> None:
    """
    Verify PATH mutation overrides reject non-mutation sockets.

    Contract:
        - Non-mutation sockets are not eligible for mutation overrides.
    Returns:
        None.
    Raises:
        MeldExecutionError: If no mutation sockets match the path.
    """
    socket = _make_socket_ref_with_path(
        node_id="node",
        param_name=param_path[-1],
        param_path=param_path,
        socket_kind=SocketKind.NORMAL,
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    with pytest.raises(MeldExecutionError, match="No mutation sockets found"):
        engine._resolve_mutation_override_targets(
            mutation_override={path_key: "override-id"},
            dag_index=blueprint.dag_index,
        )


def test_resolve_mutation_override_targets_path_missing_raises() -> None:
    """
    Verify PATH mutation overrides raise when no sockets exist at the path.

    Contract:
        - Missing mutation socket paths raise MeldExecutionError.
    Returns:
        None.
    Raises:
        MeldExecutionError: If the path does not resolve.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name="other",
        param_path=("other",),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    with pytest.raises(MeldExecutionError, match="override path"):
        engine._resolve_mutation_override_targets(
            mutation_override={"mutant": "override-id"},
            dag_index=blueprint.dag_index,
        )


@pytest.mark.parametrize("param_name", ("mutant", "config"))
def test_resolve_mutation_override_targets_unique_matches_single(
    param_name: str,
) -> None:
    """
    Verify UNIQUE mutation overrides resolve a single mutation socket.

    Contract:
        - Unique overrides resolve to exactly one mutation socket.
    Returns:
        None.
    Raises:
        AssertionError: If resolution does not return one socket.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name=param_name,
        param_path=(param_name,),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    resolved = engine._resolve_mutation_override_targets(
        mutation_override={f"*{param_name}": "override-id"},
        dag_index=blueprint.dag_index,
    )

    assert len(resolved) == 1
    resolved_socket, target_id = resolved[0]
    assert resolved_socket.param_name == param_name
    assert target_id == "override-id"


@pytest.mark.parametrize("param_name", ("missing", "absent"))
def test_resolve_mutation_override_targets_unique_missing_raises(
    param_name: str,
) -> None:
    """
    Verify UNIQUE mutation overrides raise when no mutation sockets match.

    Contract:
        - Unique overrides require exactly one mutation socket.
    Returns:
        None.
    Raises:
        MeldExecutionError: If no mutation socket matches the name.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name="mutant",
        param_path=("mutant",),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    with pytest.raises(MeldExecutionError, match="unique override"):
        engine._resolve_mutation_override_targets(
            mutation_override={f"*{param_name}": "override-id"},
            dag_index=blueprint.dag_index,
        )


@pytest.mark.parametrize(
    "param_paths",
    (
        (("left", "mutant"), ("right", "mutant")),
        (("mutant",), ("other", "mutant")),
    ),
)
def test_resolve_mutation_override_targets_unique_multiple_matches_raises(
    param_paths: tuple[tuple[str, ...], ...],
) -> None:
    """
    Verify UNIQUE mutation overrides raise when multiple mutation sockets match.

    Contract:
        - Unique overrides reject multiple mutation socket matches.
    Returns:
        None.
    Raises:
        MeldExecutionError: If multiple mutation sockets match the name.
    """
    sockets = tuple(
        _make_mutation_socket_ref(
            node_id="node",
            param_name=param_path[-1],
            param_path=param_path,
        )
        for param_path in param_paths
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=sockets,
    )

    with pytest.raises(MeldExecutionError, match="multiple mutation sockets"):
        engine._resolve_mutation_override_targets(
            mutation_override={"*mutant": "override-id"},
            dag_index=blueprint.dag_index,
        )


@pytest.mark.parametrize(
    ("socket_specs", "expected_paths"),
    (
        (
            (
                (("left", "mutant"), SocketKind.MUTATION_CONTRACT),
                (("right", "mutant"), SocketKind.MUTATION_CONTRACT),
            ),
            (("left", "mutant"), ("right", "mutant")),
        ),
        (
            (
                (("left", "mutant"), SocketKind.MUTATION_CONTRACT),
                (("right", "mutant"), SocketKind.NORMAL),
            ),
            (("left", "mutant"),),
        ),
        (
            (
                (("mutant",), SocketKind.MUTATION_CONTRACT),
            ),
            (("mutant",),),
        ),
    ),
)
def test_resolve_mutation_override_targets_broadcast_matches(
    socket_specs: tuple[tuple[tuple[str, ...], SocketKind], ...],
    expected_paths: tuple[tuple[str, ...], ...],
) -> None:
    """
    Verify BROADCAST mutation overrides resolve all mutation sockets by name.

    Contract:
        - Broadcast overrides return every matching mutation socket.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast resolution does not return all matches.
    """
    sockets = tuple(
        _make_socket_ref_with_path(
            node_id="node",
            param_name=param_path[-1],
            param_path=param_path,
            socket_kind=socket_kind,
        )
        for param_path, socket_kind in socket_specs
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=sockets,
    )

    resolved = engine._resolve_mutation_override_targets(
        mutation_override={"**mutant": "override-id"},
        dag_index=blueprint.dag_index,
    )

    resolved_paths = sorted(socket.param_path for socket, _ in resolved)
    assert resolved_paths == sorted(expected_paths)


@pytest.mark.parametrize(
    "socket_specs",
    (
        (
            (("other",), SocketKind.MUTATION_CONTRACT),
        ),
        (
            (("mutant",), SocketKind.NORMAL),
        ),
    ),
)
def test_resolve_mutation_override_targets_broadcast_missing_raises(
    socket_specs: tuple[tuple[tuple[str, ...], SocketKind], ...],
) -> None:
    """
    Verify BROADCAST mutation overrides raise when no mutation sockets match.

    Contract:
        - Broadcast overrides require at least one mutation socket match.
    Returns:
        None.
    Raises:
        MeldExecutionError: If no mutation sockets match the name.
    """
    sockets = tuple(
        _make_socket_ref_with_path(
            node_id="node",
            param_name=param_path[-1],
            param_path=param_path,
            socket_kind=socket_kind,
        )
        for param_path, socket_kind in socket_specs
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=sockets,
    )

    with pytest.raises(MeldExecutionError, match="broadcast override"):
        engine._resolve_mutation_override_targets(
            mutation_override={"**mutant": "override-id"},
            dag_index=blueprint.dag_index,
        )


@pytest.mark.parametrize("raw_key", (None, "", "   ", "*", "**", ">"))
def test_resolve_mutation_override_targets_invalid_key_raises(
    raw_key: object,
) -> None:
    """
    Verify mutation override resolution rejects invalid keys.

    Contract:
        - Invalid keys raise MeldExecutionError.
    Returns:
        None.
    Raises:
        MeldExecutionError: If the override key is invalid.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name="mutant",
        param_path=("mutant",),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    with pytest.raises(MeldExecutionError, match="Invalid mutation_override key"):
        engine._resolve_mutation_override_targets(
            mutation_override={raw_key: "override-id"},
            dag_index=blueprint.dag_index,
        )


@pytest.mark.parametrize("target_id", (None, "", 123))
def test_resolve_mutation_override_targets_invalid_target_raises(
    target_id: object,
) -> None:
    """
    Verify mutation override resolution rejects invalid target ids.

    Contract:
        - Targets must be non-empty spell id strings.
    Returns:
        None.
    Raises:
        MeldExecutionError: If the target id is invalid.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name="mutant",
        param_path=("mutant",),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    with pytest.raises(MeldExecutionError, match="Invalid mutation_override target"):
        engine._resolve_mutation_override_targets(
            mutation_override={"mutant": target_id},
            dag_index=blueprint.dag_index,
        )


@pytest.mark.parametrize(
    "param_path",
    (
        ("mutant",),
        ("left", "mutant"),
        ("left", "right", "mutant"),
    ),
)
def test_apply_mutation_overrides_replaces_dependency_for_matching_path(
    param_path: tuple[str, ...],
) -> None:
    """
    Verify mutation overrides replace dependencies for the matching path.

    Contract:
        - Matching paths are rewired to the override target id.
        - Other parameters remain unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If rewiring does not occur.
    """
    node_id = "node-1"
    param_name = param_path[-1]
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name=param_name,
        param_path=param_path,
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    override_key = ">".join(param_path)
    spell.mutation_override = {override_key: "override-id"}
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    occurrence = (node_id, param_path[:-1])
    other_path = param_path[:-1] + ("other",)
    dependencies = {
        param_name: [("orig-id", param_path)],
        "other": [("other-id", other_path)],
    }

    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=occurrence,
    )

    assert dependencies[param_name] == [("override-id", param_path)]
    assert dependencies["other"] == [("other-id", other_path)]


@pytest.mark.parametrize(
    ("param_path", "occurrence_path"),
    (
        (("left", "mutant"), ()),
        (("left", "mutant"), ("right",)),
    ),
)
def test_apply_mutation_overrides_ignores_nonmatching_path(
    param_path: tuple[str, ...],
    occurrence_path: tuple[str, ...],
) -> None:
    """
    Verify mutation overrides ignore occurrences that do not match the path.

    Contract:
        - Non-matching paths do not rewrite dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If non-matching paths are rewritten.
    """
    node_id = "node-1"
    param_name = param_path[-1]
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name=param_name,
        param_path=param_path,
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    spell.mutation_override = {">".join(param_path): "override-id"}
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    dependencies = {
        param_name: [("orig-id", occurrence_path + (param_name,))],
    }
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(node_id, occurrence_path),
    )

    assert dependencies[param_name] == [("orig-id", occurrence_path + (param_name,))]


def test_apply_mutation_overrides_ignores_other_node_id() -> None:
    """
    Verify mutation overrides do not apply to different node ids.

    Contract:
        - Overrides only apply when socket_ref.node_id matches the occurrence spell id.
    Returns:
        None.
    Raises:
        AssertionError: If overrides apply to other nodes.
    """
    socket = _make_mutation_socket_ref(
        node_id="other-node",
        param_name="mutant",
        param_path=("mutant",),
    )
    spell = _make_spell(spell_id="node-1", existence=Existence.many)
    spell.mutation_override = {"mutant": "override-id"}
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node-1"),
        sockets=(socket,),
        spell_lookup={"node-1": spell},
    )

    dependencies = {"mutant": [("orig-id", ("mutant",))]}
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=("node-1", ()),
    )

    assert dependencies["mutant"] == [("orig-id", ("mutant",))]


def test_apply_mutation_overrides_updates_multiple_params() -> None:
    """
    Verify mutation overrides can update multiple parameters in one pass.

    Contract:
        - Each targeted param receives its override target id.
    Returns:
        None.
    Raises:
        AssertionError: If not all params are updated.
    """
    node_id = "node-1"
    sockets = (
        _make_mutation_socket_ref(
            node_id=node_id,
            param_name="left",
            param_path=("left",),
        ),
        _make_mutation_socket_ref(
            node_id=node_id,
            param_name="right",
            param_path=("right",),
        ),
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    spell.mutation_override = {
        "left": "left-id",
        "right": "right-id",
    }
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=sockets,
        spell_lookup={node_id: spell},
    )

    dependencies = {
        "left": [("orig-left", ("left",))],
        "right": [("orig-right", ("right",))],
    }
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(node_id, ()),
    )

    assert dependencies["left"] == [("left-id", ("left",))]
    assert dependencies["right"] == [("right-id", ("right",))]


def test_apply_mutation_overrides_replaces_multiple_existing_occurrences() -> None:
    """
    Verify mutation overrides replace multi-occurrence dependency lists.

    Contract:
        - Existing lists are replaced by a single override occurrence.
    Returns:
        None.
    Raises:
        AssertionError: If extra occurrences remain.
    """
    node_id = "node-1"
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name="mutant",
        param_path=("mutant",),
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    spell.mutation_override = {"mutant": "override-id"}
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    dependencies = {
        "mutant": [
            ("orig-a", ("mutant",)),
            ("orig-b", ("mutant",)),
        ],
    }
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(node_id, ()),
    )

    assert dependencies["mutant"] == [("override-id", ("mutant",))]


def test_apply_mutation_overrides_skips_when_blueprint_missing() -> None:
    """
    Verify mutation overrides are skipped without a blueprint.

    Contract:
        - Missing blueprint results in no dependency changes.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies change without a blueprint.
    """
    engine, root_spell, _ = _make_engine()
    root_spell.mutation_override = {"mutant": "override-id"}
    dependencies = {"mutant": [("orig-id", ("mutant",))]}

    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(root_spell.spell_index.current, ()),
    )

    assert dependencies["mutant"] == [("orig-id", ("mutant",))]


def test_apply_mutation_overrides_skips_when_mutation_override_missing() -> None:
    """
    Verify missing mutation_override attributes are treated as no-ops.

    Contract:
        - Missing mutation_override does not alter dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies change without overrides.
    """
    node_id = "node-1"
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name="mutant",
        param_path=("mutant",),
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    dependencies = {"mutant": [("orig-id", ("mutant",))]}
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(node_id, ()),
    )

    assert dependencies["mutant"] == [("orig-id", ("mutant",))]


def test_apply_mutation_overrides_uses_root_spell_when_lookup_missing() -> None:
    """
    Verify root spell overrides apply even when root is not in spell_lookup.

    Contract:
        - Root spell fallback provides mutation_override resolution.
    Returns:
        None.
    Raises:
        AssertionError: If root overrides are not applied.
    """
    root_id = "root"
    socket = _make_mutation_socket_ref(
        node_id=root_id,
        param_name="mutant",
        param_path=("mutant",),
    )
    blueprint = _make_blueprint_with_sockets(
        root_id=root_id,
        dag=_make_dag_with_nodes([root_id]),
        ordered_node_ids=(root_id,),
        sockets=(socket,),
    )
    root_spell = _make_spell(spell_id=root_id, existence=Existence.many)
    root_spell.mutation_override = {"mutant": "override-id"}
    engine, _, _ = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={},
    )

    dependencies = {"mutant": [("orig-id", ("mutant",))]}
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(root_id, ()),
    )

    assert dependencies["mutant"] == [("override-id", ("mutant",))]


def test_apply_mutation_overrides_rejects_non_dict_override() -> None:
    """
    Verify mutation override application rejects non-dict payloads.

    Contract:
        - Non-dict mutation_override raises MeldExecutionError.
    Returns:
        None.
    Raises:
        MeldExecutionError: If mutation_override is not a dict.
    """
    node_id = "node-1"
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name="mutant",
        param_path=("mutant",),
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    spell.mutation_override = ["mutant"]
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    dependencies = {"mutant": [("orig-id", ("mutant",))]}
    with pytest.raises(MeldExecutionError, match="mutation_override must be a dict"):
        engine._apply_mutation_overrides_to_dependencies(
            dependencies=dependencies,
            occurrence=(node_id, ()),
        )


def test_extend_occurrence_graph_with_ordered_nodes_merges_topology_and_dag_dependencies() -> None:
    """
    Verify ordered-node expansion merges topology and DAG dependencies.

    Contract:
        - Topology sockets are merged with DAG-discovered dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If dependency sources are not combined.
    """
    topology = _make_topology([_make_socket("dep", ["parent-a"])])
    system_states = _SystemStatesStub({"orphan": topology})
    engine, root_spell, _ = _make_engine(system_states=system_states)
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id, "orphan", "parent-a", "parent-b"])
    dag.add_dependency("parent-b", "orphan", param_name="dep")
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan"),
        dag=dag,
    )

    deps = occurrence_graph[("orphan", ())]["dep"]
    assert deps == [("parent-a", ("dep",)), ("parent-b", ("dep",))]


def test_extend_occurrence_graph_with_ordered_nodes_dedupes_topology_and_dag_duplicates() -> None:
    """
    Verify ordered-node expansion does not duplicate shared dependencies.

    Contract:
        - DAG dependencies that duplicate topology sockets are not repeated.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate dependencies are added.
    """
    topology = _make_topology([_make_socket("dep", ["parent-a"])])
    system_states = _SystemStatesStub({"orphan": topology})
    engine, root_spell, _ = _make_engine(system_states=system_states)
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id, "orphan", "parent-a"])
    dag.add_dependency("parent-a", "orphan", param_name="dep")
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan"),
        dag=dag,
    )

    deps = occurrence_graph[("orphan", ())]["dep"]
    assert deps == [("parent-a", ("dep",))]


def test_extend_occurrence_graph_with_ordered_nodes_adds_multiple_orphans() -> None:
    """
    Verify ordered-node expansion adds multiple orphan nodes.

    Contract:
        - Each orphan in the ordered list is added as an entrypoint.
    Returns:
        None.
    Raises:
        AssertionError: If orphan entrypoints are missing.
    """
    engine, root_spell, _ = _make_engine()
    root_id = root_spell.spell_index.current
    dag = _make_dag_with_nodes([root_id, "orphan-a", "orphan-b"])
    occurrence_graph = engine._build_occurrence_graph(
        dag=dag,
        root_spell_id=root_id,
    )

    engine._extend_occurrence_graph_with_ordered_nodes(
        occurrence_graph=occurrence_graph,
        ordered_node_ids=(root_id, "orphan-a", "orphan-b"),
        dag=dag,
    )

    assert ("orphan-a", ()) in occurrence_graph
    assert ("orphan-b", ()) in occurrence_graph


def test_run_blueprint_orphan_dependency_injected_from_topology() -> None:
    """
    Verify orphan nodes can inject topology-based dependencies.

    Contract:
        - Orphan nodes execute with topology-provided dependency values.
    Returns:
        None.
    Raises:
        AssertionError: If orphan dependency injection fails.
    """
    topology = _make_topology([_make_socket("dep", ["parent"])])
    system_states = _SystemStatesStub({"orphan": topology})
    root_spell = _make_spell(
        spell_id="root",
        spell=lambda **_: "root-value",
        existence=Existence.many,
    )
    parent_spell = _make_spell(
        spell_id="parent",
        spell=lambda **_: "parent-value",
        existence=Existence.many,
    )
    orphan_spell = _make_spell(
        spell_id="orphan",
        spell=lambda *, dep: f"orphan-{dep}",
        existence=Existence.many,
    )
    dag = _make_dag_with_nodes(["root", "parent", "orphan"])
    blueprint = _make_blueprint("root", dag, ["parent", "orphan", "root"])
    engine, _, frame = _make_engine(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            "root": root_spell,
            "parent": parent_spell,
            "orphan": orphan_spell,
        },
        system_states=system_states,
    )

    assert engine.run() == "root-value"
    assert frame.get_result("orphan") == "orphan-parent-value"


def test_resolve_mutation_override_targets_unique_ignores_non_mutation_socket() -> None:
    """
    Verify UNIQUE mutation overrides ignore non-mutation sockets.

    Contract:
        - Only mutation sockets are eligible for unique override matches.
    Returns:
        None.
    Raises:
        AssertionError: If non-mutation sockets influence the match count.
    """
    sockets = (
        _make_mutation_socket_ref(
            node_id="node",
            param_name="mutant",
            param_path=("mutant",),
        ),
        _make_socket_ref_with_path(
            node_id="node",
            param_name="mutant",
            param_path=("other", "mutant"),
            socket_kind=SocketKind.NORMAL,
        ),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=sockets,
    )

    resolved = engine._resolve_mutation_override_targets(
        mutation_override={"*mutant": "override-id"},
        dag_index=blueprint.dag_index,
    )

    assert len(resolved) == 1
    resolved_socket, target_id = resolved[0]
    assert resolved_socket.socket_kind is SocketKind.MUTATION_CONTRACT
    assert target_id == "override-id"


def test_resolve_mutation_override_targets_path_allows_multiple_matches() -> None:
    """
    Verify PATH mutation overrides allow multiple mutation socket matches.

    Contract:
        - PATH overrides resolve all mutation sockets sharing the exact path.
    Returns:
        None.
    Raises:
        AssertionError: If multiple matches are not returned.
    """
    sockets = (
        _make_mutation_socket_ref(
            node_id="node-a",
            param_name="mutant",
            param_path=("left", "mutant"),
        ),
        _make_mutation_socket_ref(
            node_id="node-b",
            param_name="mutant",
            param_path=("left", "mutant"),
        ),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node-a", "node-b"),
        sockets=sockets,
    )

    resolved = engine._resolve_mutation_override_targets(
        mutation_override={"left>mutant": "override-id"},
        dag_index=blueprint.dag_index,
    )

    node_ids = {socket.node_id for socket, _ in resolved}
    assert node_ids == {"node-a", "node-b"}


def test_resolve_mutation_override_targets_path_trims_whitespace() -> None:
    """
    Verify PATH mutation overrides ignore surrounding whitespace.

    Contract:
        - Whitespace around path segments is ignored for matching.
    Returns:
        None.
    Raises:
        AssertionError: If whitespace prevents path matching.
    """
    socket = _make_mutation_socket_ref(
        node_id="node",
        param_name="mutant",
        param_path=("left", "mutant"),
    )
    engine, blueprint, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "node"),
        sockets=(socket,),
    )

    resolved = engine._resolve_mutation_override_targets(
        mutation_override={" left > mutant ": "override-id"},
        dag_index=blueprint.dag_index,
    )

    assert len(resolved) == 1
    assert resolved[0][0].param_path == ("left", "mutant")


def test_apply_mutation_overrides_adds_dependency_when_missing() -> None:
    """
    Verify mutation overrides create dependency entries when missing.

    Contract:
        - Missing parameter entries are created during override application.
    Returns:
        None.
    Raises:
        AssertionError: If missing dependencies are not created.
    """
    node_id = "node-1"
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name="mutant",
        param_path=("mutant",),
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    spell.mutation_override = {"mutant": "override-id"}
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    dependencies = {"other": [("other-id", ("other",))]}
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(node_id, ()),
    )

    assert dependencies["mutant"] == [("override-id", ("mutant",))]
    assert dependencies["other"] == [("other-id", ("other",))]


def test_apply_mutation_overrides_skips_when_spell_missing_in_lookup() -> None:
    """
    Verify mutation override application is skipped for missing spells.

    Contract:
        - Unknown spell ids do not mutate dependency mappings.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies are mutated for missing spells.
    """
    socket = _make_mutation_socket_ref(
        node_id="missing",
        param_name="mutant",
        param_path=("mutant",),
    )
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", "missing"),
        sockets=(socket,),
    )

    dependencies = {"mutant": [("orig-id", ("mutant",))]}
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=("missing", ()),
    )

    assert dependencies["mutant"] == [("orig-id", ("mutant",))]


def test_apply_mutation_overrides_skips_when_override_dict_empty() -> None:
    """
    Verify empty mutation_override dictionaries are treated as no-ops.

    Contract:
        - Empty mutation_override values do not change dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If empty overrides change dependencies.
    """
    node_id = "node-1"
    socket = _make_mutation_socket_ref(
        node_id=node_id,
        param_name="mutant",
        param_path=("mutant",),
    )
    spell = _make_spell(spell_id=node_id, existence=Existence.many)
    spell.mutation_override = {}
    engine, _, _ = _make_engine_with_sockets(
        root_id="root",
        ordered_node_ids=("root", node_id),
        sockets=(socket,),
        spell_lookup={node_id: spell},
    )

    dependencies = {"mutant": [("orig-id", ("mutant",))]}
    engine._apply_mutation_overrides_to_dependencies(
        dependencies=dependencies,
        occurrence=(node_id, ()),
    )

    assert dependencies["mutant"] == [("orig-id", ("mutant",))]


def test_build_execution_order_returns_fallback_for_empty_graph() -> None:
    """
    Verify execution ordering falls back to blueprint order for empty graphs.

    Contract:
        - Empty occurrence graphs return the fallback order as-is.
    Returns:
        None.
    Raises:
        AssertionError: If fallback ordering is not preserved.
    """
    engine, _, _ = _make_engine()
    order = engine._build_execution_order(
        occurrence_graph={},
        fallback_order=["a", "b"],
    )
    assert order == ["a", "b"]


def test_build_execution_order_uses_fallback_on_cycle() -> None:
    """
    Verify execution ordering falls back when cycles prevent full ordering.

    Contract:
        - Cyclic dependency graphs fall back to the provided order.
    Returns:
        None.
    Raises:
        AssertionError: If fallback ordering is not used on cycles.
    """
    engine, _, _ = _make_engine()
    occurrence_graph = {
        ("a", ()): {"dep": [("b", ("dep",))]},
        ("b", ()): {"dep": [("a", ("dep",))]},
    }
    order = engine._build_execution_order(
        occurrence_graph=occurrence_graph,
        fallback_order=["a", "b"],
    )
    assert order == ["a", "b"]


def test_construct_root_only_wraps_callable_errors() -> None:
    """
    Verify root-only construction wraps callable failures in MeldExecutionError.

    Contract:
        - Errors from the root callable raise MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If callable errors are not wrapped.
    """
    def _boom(**_kwargs: Any) -> None:
        raise RuntimeError("boom")

    root_spell = _make_spell(spell_id="root", spell=_boom)
    engine, _, _ = _make_engine(root_spell=root_spell)
    with pytest.raises(MeldExecutionError, match="Error invoking spell target"):
        engine._construct_root_only()


def test_construct_root_only_ignores_invalid_args_override() -> None:
    """
    Verify invalid __args__ overrides are ignored for root-only construction.

    Contract:
        - Non-sequence __args__ overrides are ignored.
        - Keyword overrides still apply.
    Returns:
        None.
    Raises:
        AssertionError: If invalid __args__ overrides are not ignored.
    """
    captured: dict[str, Any] = {}

    def _callable(*args: Any, **kwargs: Any) -> str:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return "ok"

    root_spell = _make_spell(spell_id="root", spell=_callable)
    frame = ResolutionFrame(overrides={"__args__": "bad", "x": 1})
    engine, _, _ = _make_engine(root_spell=root_spell, frame=frame)

    assert engine._construct_root_only() == "ok"
    assert captured["args"] == ()
    assert captured["kwargs"] == {"x": 1}


def test_collect_occurrence_dependencies_ignores_topology_errors_without_dag() -> None:
    """
    Verify topology lookup errors do not block occurrence expansion without a DAG.

    Contract:
        - Topology errors fall back to empty dependency sets when no DAG exists.
    Returns:
        None.
    Raises:
        AssertionError: If topology errors prevent dependency collection.
    """
    engine, root_spell, _ = _make_engine()
    engine._system_states = _SystemStatesStub({}, raise_on={root_spell.spell_index.current})

    dependencies = engine._collect_occurrence_dependencies(
        occurrence=(root_spell.spell_index.current, ()),
        dag=None,
    )

    assert dependencies == {}
