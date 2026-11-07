"""SocketKind exact-name values and stable numeric compiler row contracts."""

import base64
import pickle
from enum import Enum, StrEnum
from types import SimpleNamespace

import pytest

from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_site_graph_processor_strategy import (
    SpellSiteGraphProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import SharedCompilerExecutions
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellSocketDescriptor


class ForeignKind(Enum):
    """A non-SocketKind value carrier accepted by the existing row exporters."""

    OTHER = 77


class Node:
    """Minimal hashable DAG node used by the real edge-row exporter."""

    def __init__(self, node_id: str) -> None:
        self.id = node_id
        self.dependents = []
        self.incoming_params = {}


def _edge_rows(kind: object) -> tuple:
    """Export one parent-child row with the given socket-kind carrier."""
    parent = Node("parent")
    child = Node("child")
    parent.dependents.append(child)
    child.incoming_params[parent] = "argument"
    dag = SimpleNamespace(nodes={"parent": parent, "child": child}, _socket_kinds={(parent, child): kind})
    artifact = SimpleNamespace(_root_blueprint_phase5=SimpleNamespace(dag=dag))
    return SharedCompilerExecutions.build_phase5_dag_edge_rows(artifact)


def test_socket_values_match_names_and_legacy_ordinals() -> None:
    """Every historical ordinal resolves to its original named socket."""
    names = ("NORMAL", "SPELL_CONTRACT", "OVERRIDE_REQUIRED", "UNRESOLVED_INPUT", "AMBIGUOUS_INPUT")
    assert issubclass(SocketKind, StrEnum)
    assert tuple(member.name for member in SocketKind) == names
    for ordinal, name in enumerate(names, 1):
        member = SocketKind[name]
        assert member.value == name
        assert SocketKind(name) is member
        assert SocketKind(ordinal) is member
        assert SocketKind(float(ordinal)) is member


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        ("gASVTwAAAAAAAACMNm1lbGRlci5hZXRoZXIuc3BlbGxib29rLnNwZWxsX2NvbXBpbGVyLmRhZy5zb2NrZXRfa2luZJSMClNvY2tldEtpbmSUk5RLAYWUUpQu", SocketKind.NORMAL),
        ("gASVTwAAAAAAAACMNm1lbGRlci5hZXRoZXIuc3BlbGxib29rLnNwZWxsX2NvbXBpbGVyLmRhZy5zb2NrZXRfa2luZJSMClNvY2tldEtpbmSUk5RLBIWUUpQu", SocketKind.UNRESOLVED_INPUT),
        ("gASVTwAAAAAAAACMNm1lbGRlci5hZXRoZXIuc3BlbGxib29rLnNwZWxsX2NvbXBpbGVyLmRhZy5zb2NrZXRfa2luZJSMClNvY2tldEtpbmSUk5RLBYWUUpQu", SocketKind.AMBIGUOUS_INPUT),
    ),
)
def test_pre_migration_numeric_pickles_remain_readable(payload: str, expected: SocketKind) -> None:
    """Previously serialized numeric values still recover the same member."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize(
    ("kind", "code"),
    (
        (SocketKind.NORMAL, 1), (SocketKind.SPELL_CONTRACT, 2),
        (SocketKind.OVERRIDE_REQUIRED, 3), (SocketKind.UNRESOLVED_INPUT, 4),
        (SocketKind.AMBIGUOUS_INPUT, 5),
    ),
)
def test_actual_compiler_rows_keep_historical_integer_codes(kind: SocketKind, code: int) -> None:
    """Real edge, override, site and topology exporters keep their integer rows."""
    assert _edge_rows(kind) == (("parent", "child", "argument", code),)
    reference = SimpleNamespace(node_id="node", param_name="argument", param_path_id=0, socket_kind=kind)
    patch_map = SimpleNamespace(targets_by_spec={"key": [reference]}, specificity_by_spec={})
    assert SharedCompilerExecutions.build_override_target_rows(patch_map) == (
        ("key", None, (("node", "argument", 0, code),)),
    )
    socket = SpellSocketDescriptor(
        spell_id="root", param_name="argument", position=0, socket_kind=kind,
        is_collection=False, is_optional=False, target_spell_ids=(),
        parameter_kind="POSITIONAL_OR_KEYWORD",
    )
    row = SpellSiteGraphProcessorStrategy._param_from_socket(socket, None, {})
    assert type(row.socket_kind_value) is int
    assert row.socket_kind_value == code
    book = SimpleNamespace(
        _lookup_contracted_spells={}, _contracted_spells={},
        _aetheric_frame_configuration=SimpleNamespace(system_state=SystemState.automatic),
    )
    states = SimpleNamespace(_local_topologies={"root": SimpleNamespace(sockets=[socket])})
    shape = SpellOccurrenceGraphAnalyzerStrategy()._build_graph_shape_rows(
        spellbook=book, spell_system_states=states,
    )
    assert shape[0][0][1][0][2] == code
    assert type(shape[0][0][1][0][2]) is int


@pytest.mark.parametrize(
    ("source_kind", "code"),
    (("plain", 1), ("contract", 2), ("override_required", 3), ("unresolved_input", 4)),
)
def test_site_fallback_sources_keep_historical_integer_codes(source_kind: str, code: int) -> None:
    """A source without a topology socket receives the same numeric code."""
    source = SimpleNamespace(
        kind=source_kind, position=0, parameter_kind="POSITIONAL_OR_KEYWORD",
        is_collection=False, contract_key=None, dependency_keys=(),
    )
    row = SpellSiteGraphProcessorStrategy._param_from_source("argument", source, {})
    assert type(row.socket_kind_value) is int
    assert row.socket_kind_value == code


def test_phase5_foreign_value_and_missing_value_fallbacks_remain() -> None:
    """The permissive edge exporter keeps foreign .value and repr fallbacks."""
    assert _edge_rows(ForeignKind.OTHER) == (("parent", "child", "argument", 77),)
    missing = object()
    assert _edge_rows(missing) == (("parent", "child", "argument", repr(missing)),)
