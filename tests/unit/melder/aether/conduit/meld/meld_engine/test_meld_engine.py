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
        - missing spell_lookup entries raise MeldExecutionError.
    """
    dag = _make_dag_with_nodes(["node-1"])
    blueprint = _make_blueprint("node-1", dag, ["node-1"])
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
