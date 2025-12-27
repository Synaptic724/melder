from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.topology_dependency_mismatch_strategy import (
    TopologyDependencyMismatchStrategy,
)


class _SocketStub:
    """
    Purpose:
        Provide a minimal socket stub for topology mismatch tests.
    Contract:
        Exposes socket_kind and target_spell_ids attributes.
    """

    def __init__(self, *, socket_kind: SocketKind, target_spell_ids: set[str]) -> None:
        """
        Purpose:
            Initialize the socket stub.
        Contract:
            Stores socket metadata without mutation.
        Args:
            socket_kind: SocketKind enum value.
            target_spell_ids: Set of target spell ids.
        Returns:
            None.
        """
        self.socket_kind = socket_kind
        self.target_spell_ids = target_spell_ids


class _TopologyStub:
    """
    Purpose:
        Provide a topology stub exposing sockets.
    Contract:
        iter_sockets yields sockets in insertion order.
    """

    def __init__(self, sockets: list[_SocketStub]) -> None:
        """
        Purpose:
            Initialize the topology stub with sockets.
        Contract:
            Stores socket list for iteration.
        Args:
            sockets: List of socket stubs.
        Returns:
            None.
        """
        self._sockets = list(sockets)

    def iter_sockets(self):
        """
        Purpose:
            Yield stored socket stubs.
        Contract:
            Returns sockets in insertion order.
        Returns:
            Iterable[_SocketStub]: Socket stubs.
        """
        return iter(self._sockets)


class _StatesStub:
    """
    Purpose:
        Provide a spell system states stub for topology lookup.
    Contract:
        Returns stored topologies by spell id.
    """

    def __init__(self, mapping: dict[str, _TopologyStub]) -> None:
        """
        Purpose:
            Initialize the topology mapping.
        Contract:
            Stores the provided mapping.
        Args:
            mapping: Spell id to topology mapping.
        Returns:
            None.
        """
        self._mapping = dict(mapping)

    def get_local_topology_by_id(self, spell_id: str) -> _TopologyStub | None:
        """
        Purpose:
            Return the topology for the requested spell id.
        Contract:
            Returns None when missing.
        Args:
            spell_id: Spell id lookup key.
        Returns:
            _TopologyStub | None: Stored topology or None.
        """
        return self._mapping.get(spell_id)


def test_topology_dependency_mismatch_emits_error() -> None:
    """
    Purpose:
        Verify mismatched topology and index dependencies emit errors.
    Contract:
        Emits topology_dependency_mismatch when deps diverge.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing.
    """
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies={"a"},
        )
    )
    topology = _TopologyStub(
        [
            _SocketStub(socket_kind=SocketKind.NORMAL, target_spell_ids={"a", "b"}),
        ]
    )
    states = _StatesStub({"root": topology})
    diagnostics: list = []

    TopologyDependencyMismatchStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "topology_dependency_mismatch"
    assert diagnostics[0].details["missing_in_index"] == ["b"]


def test_topology_dependency_mismatch_skips_when_aligned() -> None:
    """
    Purpose:
        Verify aligned topology and index dependencies emit no diagnostics.
    Contract:
        Leaves diagnostics empty when deps match.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted unexpectedly.
    """
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies={"a"},
        )
    )
    topology = _TopologyStub(
        [
            _SocketStub(socket_kind=SocketKind.NORMAL, target_spell_ids={"a"}),
        ]
    )
    states = _StatesStub({"root": topology})
    diagnostics: list = []

    TopologyDependencyMismatchStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []
