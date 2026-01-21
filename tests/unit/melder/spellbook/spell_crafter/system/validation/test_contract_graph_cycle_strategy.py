from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.contract_graph_cycle_strategy import (
    ContractGraphCycleStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub for provider lookup.
    Contract:
        Exposes spellframe, spell_name, and binding_name attributes.
    """

    def __init__(
        self,
        *,
        spellframe: object,
        spell_name: str,
        binding_name: str | None,
    ) -> None:
        """
        Purpose:
            Initialize the spell stub with lookup metadata.
        Contract:
            Stores spellframe, spell_name, and binding_name.
        Args:
            spellframe: Frame/interface identifier.
            spell_name: Spell name string.
            binding_name: Optional binding name.
        Returns:
            None.
        """
        self.spellframe = spellframe
        self.spell_name = spell_name
        self.binding_name = binding_name


class _SocketStub:
    """
    Purpose:
        Provide a contract socket stub for cycle detection.
    Contract:
        Exposes socket_kind, contract_key, and param_name attributes.
    """

    def __init__(
        self,
        *,
        socket_kind: SocketKind,
        contract_key: tuple[str, str] | None,
        param_name: str,
    ) -> None:
        """
        Purpose:
            Initialize the socket stub.
        Contract:
            Stores provided socket metadata.
        Args:
            socket_kind: SocketKind value for the socket.
            contract_key: Canonical contract key tuple or None.
            param_name: Parameter name string.
        Returns:
            None.
        """
        self.socket_kind = socket_kind
        self.contract_key = contract_key
        self.param_name = param_name


class _TopologyStub:
    """
    Purpose:
        Provide a topology stub that yields sockets.
    Contract:
        iter_sockets returns the stored sockets in order.
    """

    def __init__(self, sockets: list[_SocketStub]) -> None:
        """
        Purpose:
            Initialize the topology stub with sockets.
        Contract:
            Stores sockets for iteration.
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


def test_contract_graph_cycle_emits_error() -> None:
    """
    Purpose:
        Verify contract graph cycles emit diagnostics.
    Contract:
        Emits contract_cycle_detected when contract edges form a loop.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing.
    """
    class FrameA:
        """
        Purpose:
            Dummy frame for spell A.
        Contract:
            Acts as a stable spellframe identifier.
        """

    class FrameB:
        """
        Purpose:
            Dummy frame for spell B.
        Contract:
            Acts as a stable spellframe identifier.
        """

    spell_lookup = {
        "A": _SpellStub(spellframe=FrameA, spell_name="spell-a", binding_name=None),
        "B": _SpellStub(spellframe=FrameB, spell_name="spell-b", binding_name=None),
    }

    key_a = SpellInputUtils.make_spell_key_from_parts(
        spellframe=spell_lookup["A"].spellframe,
        spell_name=spell_lookup["A"].spell_name,
        binding_name=spell_lookup["A"].binding_name,
    )
    key_b = SpellInputUtils.make_spell_key_from_parts(
        spellframe=spell_lookup["B"].spellframe,
        spell_name=spell_lookup["B"].spell_name,
        binding_name=spell_lookup["B"].binding_name,
    )

    topology_a = _TopologyStub(
        [
            _SocketStub(
                socket_kind=SocketKind.SPELL_CONTRACT,
                contract_key=key_b,
                param_name="dep_b",
            ),
        ]
    )
    topology_b = _TopologyStub(
        [
            _SocketStub(
                socket_kind=SocketKind.SPELL_CONTRACT,
                contract_key=key_a,
                param_name="dep_a",
            ),
        ]
    )
    states = _StatesStub({"A": topology_a, "B": topology_b})

    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="A",
            lineage_id="lineage-a",
            dependencies=set(),
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="B",
            lineage_id="lineage-b",
            dependencies=set(),
        )
    )

    diagnostics: list = []

    ContractGraphCycleStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup=spell_lookup,
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics
    assert diagnostics[0].code == "contract_cycle_detected"
    assert set(diagnostics[0].details["cycle_spell_ids"]) == {"A", "B"}


def test_contract_graph_cycle_skips_when_no_cycle() -> None:
    """
    Purpose:
        Verify contract graphs without cycles emit no diagnostics.
    Contract:
        Leaves diagnostics empty when edges are acyclic.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted unexpectedly.
    """
    class FrameA:
        """
        Purpose:
            Dummy frame for spell A.
        Contract:
            Acts as a stable spellframe identifier.
        """

    class FrameB:
        """
        Purpose:
            Dummy frame for spell B.
        Contract:
            Acts as a stable spellframe identifier.
        """

    spell_lookup = {
        "A": _SpellStub(spellframe=FrameA, spell_name="spell-a", binding_name=None),
        "B": _SpellStub(spellframe=FrameB, spell_name="spell-b", binding_name=None),
    }

    key_b = SpellInputUtils.make_spell_key_from_parts(
        spellframe=spell_lookup["B"].spellframe,
        spell_name=spell_lookup["B"].spell_name,
        binding_name=spell_lookup["B"].binding_name,
    )

    topology_a = _TopologyStub(
        [
            _SocketStub(
                socket_kind=SocketKind.SPELL_CONTRACT,
                contract_key=key_b,
                param_name="dep_b",
            ),
        ]
    )
    topology_b = _TopologyStub([])
    states = _StatesStub({"A": topology_a, "B": topology_b})

    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="A",
            lineage_id="lineage-a",
            dependencies=set(),
        )
    )
    index.upsert_node(
        SpellSystemNode(
            spell_id="B",
            lineage_id="lineage-b",
            dependencies=set(),
        )
    )

    diagnostics: list = []

    ContractGraphCycleStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup=spell_lookup,
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []
