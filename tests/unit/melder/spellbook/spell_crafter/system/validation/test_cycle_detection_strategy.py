import pytest

from melder.spellbook.spell_crafter.system.spell_system_index import (
    SpellSystemIndex,
)
from melder.spellbook.spell_crafter.system.spell_system_node import (
    SpellSystemNode,
)
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.cycle_detection_strategy import (
    CycleDetectionStrategy,
)


def _node(spell_id: str, deps=()):
    return SpellSystemNode(spell_id=spell_id, lineage_id="ln", dependencies=deps)


def _index(*nodes: SpellSystemNode) -> SpellSystemIndex:
    idx = SpellSystemIndex()
    for n in nodes:
        idx.upsert_node(n)
    return idx


class _CancelStub:
    def __init__(self, is_set=True, exc=RuntimeError("cancel")):
        self._is_set = is_set
        self._exc = exc

    @property
    def is_set(self):
        return self._is_set

    def throw_if_set(self):
        if self.is_set:
            raise self._exc


def test_run_requires_index():
    strategy = CycleDetectionStrategy()
    with pytest.raises(ValueError):
        strategy.run(
            index=None,
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_CancelStub(is_set=False),
        )


def test_empty_index_produces_no_diagnostics():
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=SpellSystemIndex(),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert diags == []


def test_single_node_no_deps_has_no_cycle():
    idx = _index(_node("a"))
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert diags == []


def test_linear_chain_is_acyclic():
    idx = _index(_node("a", deps={"b"}), _node("b", deps={"c"}), _node("c"))
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert diags == []


def test_simple_cycle_emits_diagnostic():
    idx = _index(_node("a", deps={"b"}), _node("b", deps={"a"}))
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert len(diags) == 1
    diag = diags[0]
    assert diag.code == "cycle_detected"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert "Cycle detected" in diag.message


def test_self_cycle_detected():
    idx = _index(_node("solo", deps={"solo"}))
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert diags and diags[0].code == "cycle_detected"


def test_cycle_in_one_component_still_reports_once():
    idx = _index(
        _node("c1", deps={"c2"}),
        _node("c2", deps={"c1"}),  # cyclic component
        _node("d1"),
        _node("d2", deps={"d1"}),
    )
    diags: list[SystemDiagnostic] = [SystemDiagnostic("pre", "existing")]
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    # one new diagnostic appended in addition to the existing one
    assert len(diags) == 2
    assert any(d.code == "cycle_detected" for d in diags)


def test_missing_dependency_node_does_not_crash():
    # dependency references a node not present; algorithm should still finish without cycle
    idx = _index(_node("a", deps={"ghost"}))
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert diags == []


def test_cancel_event_halts_processing():
    idx = _index(_node("a"))
    cancel = _CancelStub(is_set=True)
    with pytest.raises(RuntimeError, match="cancel"):
        CycleDetectionStrategy().run(
            index=idx,
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=cancel,
        )


def test_cancel_event_checked_during_traversal():
    idx = _index(_node("a", deps={"b"}), _node("b"))
    class ToggleCancel(_CancelStub):
        def __init__(self):
            super().__init__(is_set=False)
            self.flip = False

        @property
        def is_set(self):
            self.flip = not self.flip
            return self.flip

    cancel = ToggleCancel()

    with pytest.raises(RuntimeError, match="cancel"):
        CycleDetectionStrategy().run(
            index=idx,
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=cancel,
        )


def test_three_node_cycle_emits_diagnostic() -> None:
    """
    Purpose:
        Ensure a three-node cycle triggers a cycle_detected diagnostic.
    Contract:
        Appends one diagnostic and does not raise when not cancelled.
    Args:
        None.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing or incorrect.
    """
    idx = _index(
        _node("a", deps={"b"}),
        _node("b", deps={"c"}),
        _node("c", deps={"a"}),
    )
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert len(diags) == 1
    assert diags[0].code == "cycle_detected"


def test_diamond_graph_is_acyclic() -> None:
    """
    Purpose:
        Validate that a diamond-shaped DAG is treated as acyclic.
    Contract:
        Leaves diagnostics empty for a valid DAG.
    Args:
        None.
    Returns:
        None.
    Raises:
        AssertionError: If a diagnostic is emitted for an acyclic graph.
    """
    idx = _index(
        _node("a", deps={"b", "c"}),
        _node("b", deps={"d"}),
        _node("c", deps={"d"}),
        _node("d"),
    )
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert diags == []


def test_multiple_cycles_report_once() -> None:
    """
    Purpose:
        Confirm multiple disjoint cycles still produce a single diagnostic.
    Contract:
        Appends one cycle_detected diagnostic for any cycle presence.
    Args:
        None.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostic count or code is unexpected.
    """
    idx = _index(
        _node("a", deps={"b"}),
        _node("b", deps={"a"}),
        _node("c", deps={"d"}),
        _node("d", deps={"c"}),
    )
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert len(diags) == 1
    assert diags[0].code == "cycle_detected"


def test_cycle_with_missing_dependency_still_detected() -> None:
    """
    Purpose:
        Ensure a missing dependency does not mask a real cycle.
    Contract:
        Appends a cycle_detected diagnostic when a cycle exists.
    Args:
        None.
    Returns:
        None.
    Raises:
        AssertionError: If the cycle diagnostic is not emitted.
    """
    idx = _index(
        _node("a", deps={"b", "ghost"}),
        _node("b", deps={"a"}),
    )
    diags: list[SystemDiagnostic] = []
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=_CancelStub(is_set=False),
    )
    assert len(diags) == 1
    assert diags[0].code == "cycle_detected"


def test_diagnostics_list_reused():
    idx = _index(_node("a", deps={"a"}))
    existing = [SystemDiagnostic("X", "keep")]
    CycleDetectionStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=existing,
        cancel_event=_CancelStub(is_set=False),
    )
    assert existing[0].code == "X"
    assert any(d.code == "cycle_detected" for d in existing)
