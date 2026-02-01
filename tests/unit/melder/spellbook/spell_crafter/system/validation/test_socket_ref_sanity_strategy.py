from __future__ import annotations

from typing import Optional

import pytest

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)


class _CancelStub:
    """
    Purpose:
        Provide a minimal cancellation event stub for strategy tests.
    Contract:
        - If is_set is True, throw_if_set raises the configured exception.
        - If is_set is False, throw_if_set is a no-op.
    Args:
        is_set: Whether cancellation is considered active.
        exc: Exception instance to raise when cancelled.
    """

    def __init__(self, *, is_set: bool = True, exc: Exception | None = None) -> None:
        """
        Purpose:
            Initialize the stub with a fixed cancellation state.
        Contract:
            Stores the provided state and exception for later use.
        Args:
            is_set: Whether cancellation is active.
            exc: Optional exception to raise; defaults to RuntimeError.
        Returns:
            None.
        """
        self._is_set = is_set
        self._exc = exc or RuntimeError("cancelled")

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Report whether cancellation is currently active.
        Contract:
            Returns the value provided at initialization.
        Returns:
            bool: True when cancellation is active.
        """
        return self._is_set

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise the configured exception when cancellation is active.
        Contract:
            Raises only when is_set is True.
        Raises:
            Exception: The configured cancellation exception.
        """
        if self.is_set:
            raise self._exc


class _ToggleCancel:
    """
    Purpose:
        Toggle cancellation state on the second is_set check.
    Contract:
        Raises once the second check is performed.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the toggle state.
        Contract:
            Starts with cancellation disabled for the first check.
        Returns:
            None.
        """
        self._checks = 0

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Toggle to cancelled on the second check.
        Contract:
            Returns False on first check, True thereafter.
        Returns:
            bool: True once cancellation should be honored.
        """
        self._checks += 1
        return self._checks > 1

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise once cancellation has been toggled on.
        Contract:
            Raises RuntimeError when cancellation is active.
        Raises:
            RuntimeError: When cancellation has been toggled on.
        """
        if self._checks > 1:
            raise RuntimeError("cancelled")


def _node(spell_id: str) -> SpellSystemNode:
    """
    Purpose:
        Build a SpellSystemNode with a deterministic lineage id.
    Contract:
        Uses the provided spell_id for both identity and lineage naming.
    Args:
        spell_id: Spell identifier for the node.
    Returns:
        SpellSystemNode: The configured node instance.
    """
    return SpellSystemNode(
        spell_id=spell_id,
        lineage_id=f"lineage-{spell_id}",
    )


def _index(*spell_ids: str) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex populated with nodes for the provided ids.
    Contract:
        Inserts nodes in order without additional mutation.
    Args:
        spell_ids: Spell ids to insert into the index.
    Returns:
        SpellSystemIndex: The populated index.
    """
    idx = SpellSystemIndex()
    for spell_id in spell_ids:
        idx.upsert_node(_node(spell_id))
    return idx


def _socket_ref(
    *,
    node_id: str = "node",
    param_name: str = "param",
    param_path: tuple[str, ...] = ("param",),
    path_registry: PathRegistry,
    socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Purpose:
        Build a SocketRef with the provided socket metadata.
    Contract:
        Returns a frozen SocketRef instance for reuse in tests.
    Args:
        node_id: Spell id owning the socket.
        param_name: Parameter name for the socket.
        param_path: Param path tuple from the root.
        socket_kind: Socket kind classification.
    Returns:
        SocketRef: The configured socket reference.
    """
    path_id = path_registry.root_path_id
    for segment in param_path:
        path_id = path_registry.extend_path(path_id, segment)
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path_id=path_id,
        socket_kind=socket_kind,
    )


def _make_blueprint(
    *,
    root_id: str,
    socket_refs: tuple[SocketRef, ...] | None = None,
    dag_index: DagIndex | None = None,
    path_registry: Optional[PathRegistry] = None,
    sync_refs: bool = False,
) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a RootResolutionBlueprint for socket-ref sanity tests.
    Contract:
        - When sync_refs is True, socket_refs are added via add_socket_ref.
        - When sync_refs is False, socket_refs are stored without index updates.
    Args:
        root_id: Root id for the blueprint.
        socket_refs: Socket references to attach.
        dag_index: Optional DagIndex to attach to the blueprint.
        sync_refs: Whether to keep socket_refs and dag_index in sync.
    Returns:
        RootResolutionBlueprint: The configured blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_node(root_id)
    for ref in socket_refs or ():
        dag.add_node(ref.node_id)

    if dag_index is None:
        if path_registry is None:
            path_registry = PathRegistry()
        dag_index = DagIndex(path_registry=path_registry)

    if sync_refs:
        blueprint = RootResolutionBlueprint(
            root_spell_id=root_id,
            root_lineage_id=f"lineage-{root_id}",
            dag=dag,
            dag_index=dag_index,
        )
        for ref in socket_refs or ():
            blueprint.add_socket_ref(ref)
        return blueprint

    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=f"lineage-{root_id}",
        dag=dag,
        socket_refs=socket_refs,
        dag_index=dag_index,
    )


def test_no_blueprints_produces_no_diagnostics() -> None:
    """
    Purpose:
        Ensure empty blueprints yield no diagnostics.
    Contract:
        Leaves diagnostics empty when no roots are provided.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index(),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_synced_socket_refs_and_index_produce_no_diagnostics() -> None:
    """
    Purpose:
        Verify synced socket_refs and DagIndex produce no diagnostics.
    Contract:
        Leaves diagnostics empty when refs are consistent.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    path_registry = PathRegistry()
    ref_a = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    ref_b = _socket_ref(
        node_id="b",
        param_name="q",
        param_path=("p", "q"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref_a, ref_b),
        path_registry=path_registry,
        sync_refs=True,
    )
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a", "b"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_duplicate_socket_ref_emits_duplicate_diagnostic() -> None:
    """
    Purpose:
        Ensure duplicate socket_refs are detected.
    Contract:
        Emits one socket_ref_duplicate diagnostic for the extra reference.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate diagnostics are missing or incorrect.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
        sync_refs=True,
    )
    blueprint.add_socket_ref(ref)
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "socket_ref_duplicate"
    assert diags[0].root_id == "root"


def test_duplicate_socket_ref_multiple_times_emits_multiple_duplicates() -> None:
    """
    Purpose:
        Validate repeated duplicates emit a diagnostic for each extra ref.
    Contract:
        Emits two socket_ref_duplicate diagnostics for three identical refs.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate count is incorrect.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
        sync_refs=True,
    )
    blueprint.add_socket_ref(ref)
    blueprint.add_socket_ref(ref)
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    dupes = [d for d in diags if d.code == "socket_ref_duplicate"]
    assert len(dupes) == 2


def test_missing_in_index_emits_path_and_name_diagnostics() -> None:
    """
    Purpose:
        Ensure a socket_ref absent from the index emits both missing diagnostics.
    Contract:
        Emits socket_ref_missing_in_index and socket_ref_missing_in_index_name.
    Returns:
        None.
    Raises:
        AssertionError: If expected diagnostics are missing.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
    )
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    codes = {d.code for d in diags}
    assert codes == {"socket_ref_missing_in_index", "socket_ref_missing_in_index_name"}


def test_missing_in_index_by_name_only_emits_name_diagnostic() -> None:
    """
    Purpose:
        Confirm missing name bucket detection when path lookup succeeds.
    Contract:
        Emits socket_ref_missing_in_index_name only.
    Returns:
        None.
    Raises:
        AssertionError: If the wrong diagnostics are emitted.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    index = DagIndex(path_registry=path_registry)
    index.add_socket(ref)
    index._by_name[ref.param_name] = []
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        dag_index=index,
        path_registry=path_registry,
    )
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "socket_ref_missing_in_index_name"


def test_missing_in_index_by_path_only_emits_path_diagnostic() -> None:
    """
    Purpose:
        Confirm missing path lookup detection when name lookup succeeds.
    Contract:
        Emits socket_ref_missing_in_index only.
    Returns:
        None.
    Raises:
        AssertionError: If the wrong diagnostics are emitted.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    index = DagIndex(path_registry=path_registry)
    index.add_socket(ref)
    index._by_exact_path_id = {}
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        dag_index=index,
        path_registry=path_registry,
    )
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "socket_ref_missing_in_index"


def test_orphan_socket_in_index_emits_orphan_diagnostic() -> None:
    """
    Purpose:
        Ensure sockets in DagIndex but not in socket_refs are reported.
    Contract:
        Emits dag_index_orphan_socket for the orphan socket.
    Returns:
        None.
    Raises:
        AssertionError: If orphan diagnostics are missing.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    index = DagIndex(path_registry=path_registry)
    index.add_socket(ref)
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(),
        dag_index=index,
        path_registry=path_registry,
    )
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "dag_index_orphan_socket"
    assert diags[0].root_id == "root"


def test_orphan_socket_with_valid_ref_only_reports_orphan() -> None:
    """
    Purpose:
        Verify orphan detection does not flag valid socket_refs.
    Contract:
        Emits only dag_index_orphan_socket for the extra entry.
    Returns:
        None.
    Raises:
        AssertionError: If unexpected diagnostics appear.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    orphan = _socket_ref(
        node_id="b",
        param_name="q",
        param_path=("q",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
        sync_refs=True,
    )
    blueprint.dag_index.add_socket(orphan)
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a", "b"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert {d.code for d in diags} == {"dag_index_orphan_socket"}


def test_multiple_orphan_sockets_emit_multiple_diagnostics() -> None:
    """
    Purpose:
        Ensure each orphan socket yields a diagnostic.
    Contract:
        Emits one dag_index_orphan_socket per orphan.
    Returns:
        None.
    Raises:
        AssertionError: If orphan count is incorrect.
    """
    path_registry = PathRegistry()
    ref_a = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    ref_b = _socket_ref(
        node_id="b",
        param_name="q",
        param_path=("q",),
        path_registry=path_registry,
    )
    index = DagIndex(path_registry=path_registry)
    index.add_socket(ref_a)
    index.add_socket(ref_b)
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(),
        dag_index=index,
        path_registry=path_registry,
    )
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a", "b"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 2
    assert {d.spell_id for d in diags} == {"a", "b"}


def test_diagnostics_list_reused_appends_entries() -> None:
    """
    Purpose:
        Confirm diagnostics are appended rather than replaced.
    Contract:
        Preserves existing diagnostics and adds new ones.
    Returns:
        None.
    Raises:
        AssertionError: If existing diagnostics are lost.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
    )
    existing = [SystemDiagnostic("pre", "keep")]
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=existing,
        cancel_event=None,
    )
    assert existing[0].code == "pre"
    assert any(d.code == "socket_ref_missing_in_index" for d in existing)


def test_cancel_event_halts_before_processing() -> None:
    """
    Purpose:
        Ensure cancellation is honored before any root processing begins.
    Contract:
        Raises the cancellation exception without appending diagnostics.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
    )
    diags: list[SystemDiagnostic] = []
    with pytest.raises(RuntimeError, match="cancelled"):
        SocketRefSanityStrategy().run(
            index=_index("a"),
            blueprints={"root": blueprint},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_CancelStub(is_set=True),
        )
    assert diags == []


def test_cancel_event_checked_between_roots() -> None:
    """
    Purpose:
        Verify cancellation can stop processing between roots.
    Contract:
        Processes the first root, then raises before the second.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is toggled on.
    """
    path_registry_a = PathRegistry()
    path_registry_b = PathRegistry()
    ref_a = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry_a,
    )
    ref_b = _socket_ref(
        node_id="b",
        param_name="q",
        param_path=("q",),
        path_registry=path_registry_b,
    )
    blueprints = {
        "r1": _make_blueprint(root_id="r1", socket_refs=(ref_a,), path_registry=path_registry_a),
        "r2": _make_blueprint(root_id="r2", socket_refs=(ref_b,), path_registry=path_registry_b),
    }
    diags: list[SystemDiagnostic] = []
    with pytest.raises(RuntimeError, match="cancelled"):
        SocketRefSanityStrategy().run(
            index=_index("a", "b"),
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_ToggleCancel(),
        )
    assert {d.root_id for d in diags} == {"r1"}


def test_missing_refs_across_multiple_roots_include_root_id() -> None:
    """
    Purpose:
        Ensure missing socket_refs are reported per root.
    Contract:
        Emits missing diagnostics tagged with the root id.
    Returns:
        None.
    Raises:
        AssertionError: If root ids are not included.
    """
    path_registry_a = PathRegistry()
    path_registry_b = PathRegistry()
    ref_a = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("p",),
        path_registry=path_registry_a,
    )
    ref_b = _socket_ref(
        node_id="b",
        param_name="q",
        param_path=("q",),
        path_registry=path_registry_b,
    )
    blueprints = {
        "r1": _make_blueprint(root_id="r1", socket_refs=(ref_a,), path_registry=path_registry_a),
        "r2": _make_blueprint(root_id="r2", socket_refs=(ref_b,), path_registry=path_registry_b),
    }
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert {d.root_id for d in diags} == {"r1", "r2"}


def test_duplicate_message_includes_param_path() -> None:
    """
    Purpose:
        Validate duplicate diagnostics include the param path in the message.
    Contract:
        socket_ref_duplicate message contains the joined param path.
    Returns:
        None.
    Raises:
        AssertionError: If the path is not present in the message.
    """
    path_registry = PathRegistry()
    ref = _socket_ref(
        node_id="a",
        param_name="p",
        param_path=("a", "b"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        socket_refs=(ref,),
        path_registry=path_registry,
        sync_refs=True,
    )
    blueprint.add_socket_ref(ref)
    diags: list[SystemDiagnostic] = []
    SocketRefSanityStrategy().run(
        index=_index("a"),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    message = diags[0].message
    assert "a>b" in message
