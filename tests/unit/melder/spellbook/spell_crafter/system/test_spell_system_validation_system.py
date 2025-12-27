import pytest

from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


class _RecordingStrategy(SpellSystemValidationStrategy):
    def __init__(self, *, severity=None, code="C", message="msg"):
        self.calls = []
        self.diag = (
            SystemDiagnostic(code, message, severity=severity)
            if severity is not None
            else None
        )

    def run(
        self,
        *,
        index,
        blueprints,
        phase4_results,
        broken_spell_ids,
        diagnostics,
        cancel_event,
    ) -> None:
        self.calls.append(
            (index, blueprints, phase4_results, broken_spell_ids, diagnostics, cancel_event)
        )
        if self.diag is not None:
            diagnostics.append(self.diag)


class _StateStub:
    def __init__(self):
        self.calls = []

    def set_validity(self, validity, *, change_reason):
        self.calls.append((validity, change_reason))


class _StateRaiser(_StateStub):
    def set_validity(self, validity, *, change_reason):
        super().set_validity(validity, change_reason=change_reason)
        raise RuntimeError("boom")


class _States:
    def __init__(self, mapping):
        self.mapping = mapping

    def get_by_spell_id(self, spell_id):
        return self.mapping.get(spell_id)


class _CancelStub:
    def __init__(self, is_set=True, exc=RuntimeError("cancel")):
        self.is_set = is_set
        self._exc = exc

    def throw_if_set(self):
        raise self._exc


def _index_with_nodes(*spell_ids):
    idx = SpellSystemIndex()
    for sid in spell_ids:
        idx.upsert_node(SpellSystemNode(spell_id=sid, lineage_id=f"lineage-{sid}"))
    return idx


def _blueprint(spell_id="root"):
    return {"root": RootResolutionBlueprint(spell_id, "lineage", DirectedAcyclicWorkGraph())}


def test_init_rejects_none_strategies():
    with pytest.raises(ValueError):
        SpellSystemValidationSystem(None)


def test_cleanup_is_idempotent_and_blocks_validate():
    sys_val = SpellSystemValidationSystem([])
    sys_val.cleanup()
    sys_val.cleanup()  # second call no-op
    with pytest.raises(RuntimeError):
        sys_val.validate(
            index=_index_with_nodes("s1"),
            blueprints=_blueprint(),
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=_States({}),
        )


@pytest.mark.parametrize(
    "param,kw",
    [
        ("index", {"index": None}),
        ("blueprints", {"blueprints": None}),
        ("spell_system_states", {"spell_system_states": None}),
    ],
)
def test_validate_requires_non_null_inputs(param, kw):
    sys_val = SpellSystemValidationSystem([])
    base_kwargs = dict(
        index=_index_with_nodes("s1"),
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({}),
    )
    base_kwargs.update(kw)
    with pytest.raises(ValueError):
        sys_val.validate(**base_kwargs)


def test_strategies_receive_inputs_and_diagnostics_shared():
    strategy = _RecordingStrategy()
    idx = _index_with_nodes("a")
    blueprints = _blueprint()
    sys_val = SpellSystemValidationSystem([strategy])
    sys_val.validate(
        index=idx,
        blueprints=blueprints,
        phase4_results={"a": 1},
        broken_spell_ids={"b"},
        spell_system_states=_States({}),
    )
    assert strategy.calls
    (_, bp, p4, broken, diags, _) = strategy.calls[-1]
    assert bp is blueprints
    assert p4 == {"a": 1}
    assert broken == {"b"}
    assert diags == []


def test_validity_set_to_valid_when_no_errors():
    strategy = _RecordingStrategy(severity=SystemDiagnosticSeverity.WARNING)
    idx = _index_with_nodes("a", "b")
    state_a, state_b = _StateStub(), _StateStub()
    states = _States({"a": state_a, "b": state_b})
    sys_val = SpellSystemValidationSystem([strategy])
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
    )
    for st in (state_a, state_b):
        assert st.calls == [(SpellValidity.valid, SpellStateChangeReason.validation_passed)]
    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings and result.warnings[0].severity is SystemDiagnosticSeverity.WARNING
    assert result.warnings[0].source == "_RecordingStrategy"
    assert result.nodes == idx.nodes


def test_validity_set_to_gated_on_error_diagnostic():
    strategy = _RecordingStrategy(severity=SystemDiagnosticSeverity.ERROR)
    idx = _index_with_nodes("a")
    state = _StateStub()
    sys_val = SpellSystemValidationSystem([strategy])
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": state}),
    )
    assert state.calls == [(SpellValidity.gated, SpellStateChangeReason.validation_failed)]
    assert result.is_valid is False
    assert result.errors and result.errors[0].severity is SystemDiagnosticSeverity.ERROR
    assert result.errors[0].source == "_RecordingStrategy"
    assert result.warnings == []


def test_set_validity_skips_missing_state_and_swallows_errors():
    strategy = _RecordingStrategy()  # no diagnostics -> valid path
    idx = _index_with_nodes("a", "b")
    good = _StateStub()
    bad = _StateRaiser()
    sys_val = SpellSystemValidationSystem([strategy])
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": good, "b": bad, "missing": None}),
    )
    # good state updated, bad state exception swallowed, validity still reflected as valid
    assert good.calls == [(SpellValidity.valid, SpellStateChangeReason.validation_passed)]
    assert result.is_valid is True


def test_cancel_event_short_circuits_before_strategy():
    strategy = _RecordingStrategy()
    sys_val = SpellSystemValidationSystem([strategy])
    with pytest.raises(RuntimeError, match="cancel"):
        sys_val.validate(
            index=_index_with_nodes("a"),
            blueprints=_blueprint(),
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=_States({}),
            cancel_event=_CancelStub(),
        )
    assert strategy.calls == []


def test_validate_raises_after_cleanup_of_strategies():
    strategy = _RecordingStrategy()
    sys_val = SpellSystemValidationSystem([strategy])
    sys_val.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sys_val.validate(
            index=_index_with_nodes("a"),
            blueprints=_blueprint(),
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=_States({}),
        )


def test_validate_can_run_multiple_times():
    strategy = _RecordingStrategy()
    sys_val = SpellSystemValidationSystem([strategy])
    idx = _index_with_nodes("a")
    states = _States({"a": _StateStub()})
    for _ in range(2):
        sys_val.validate(
            index=idx,
            blueprints=_blueprint(),
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=states,
        )
    assert len(strategy.calls) == 2


def test_validate_with_no_strategies_succeeds():
    idx = _index_with_nodes("solo")
    states = _States({"solo": _StateStub()})
    sys_val = SpellSystemValidationSystem([])
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
    )
    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []


def test_validate_ignores_none_severity_diagnostics():
    strat = _RecordingStrategy(severity=None)
    idx = _index_with_nodes("a")
    states = _States({"a": _StateStub()})
    result = SpellSystemValidationSystem([strat]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
    )
    assert result.errors == []
    assert result.warnings == []


def test_validate_collects_multiple_warnings():
    s1 = _RecordingStrategy(severity=SystemDiagnosticSeverity.WARNING, code="W1")
    s2 = _RecordingStrategy(severity=SystemDiagnosticSeverity.WARNING, code="W2")
    idx = _index_with_nodes("a")
    result = SpellSystemValidationSystem([s1, s2]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": _StateStub()}),
    )
    assert {d.code for d in result.warnings} == {"W1", "W2"}
    assert result.errors == []
    assert result.is_valid is True


def test_error_overrides_warnings_for_validity():
    warn = _RecordingStrategy(severity=SystemDiagnosticSeverity.WARNING)
    err = _RecordingStrategy(severity=SystemDiagnosticSeverity.ERROR)
    idx = _index_with_nodes("a")
    state = _StateStub()
    result = SpellSystemValidationSystem([warn, err]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": state}),
    )
    assert result.is_valid is False
    assert result.errors
    assert state.calls[-1] == (SpellValidity.gated, SpellStateChangeReason.validation_failed)


def test_validate_returns_nodes_reference():
    idx = _index_with_nodes("a", "b")
    result = SpellSystemValidationSystem([]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": _StateStub(), "b": _StateStub()}),
    )
    assert result.nodes is idx.nodes


def test_validate_runs_all_strategies_when_not_cancelled():
    s1 = _RecordingStrategy()
    s2 = _RecordingStrategy()
    cancel = _CancelStub(is_set=False)
    SpellSystemValidationSystem([s1, s2]).validate(
        index=_index_with_nodes("a"),
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids={"x"},
        spell_system_states=_States({"a": _StateStub()}),
        cancel_event=cancel,
    )
    assert len(s1.calls) == 1
    assert len(s2.calls) == 1


def test_cancel_event_blocks_subsequent_strategies():
    class ToggleCancel(_CancelStub):
        def __init__(self):
            super().__init__(is_set=False)
            self.flip = False

        @property
        def is_set(self):
            flag = self.flip
            self.flip = True
            return flag
        @is_set.setter
        def is_set(self, value):
            self.flip = value

    s1 = _RecordingStrategy()
    s2 = _RecordingStrategy()
    cancel = ToggleCancel()
    with pytest.raises(RuntimeError, match="cancel"):
        SpellSystemValidationSystem([s1, s2]).validate(
            index=_index_with_nodes("a"),
            blueprints=_blueprint(),
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=_States({"a": _StateStub()}),
            cancel_event=cancel,
        )
    # first strategy runs, second blocked
    assert len(s1.calls) == 1
    assert len(s2.calls) == 0


def test_validate_supports_empty_index():
    idx = _index_with_nodes()  # no nodes
    result = SpellSystemValidationSystem([]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({}),
    )
    assert result.is_valid is True
    assert result.nodes == {}


def test_errors_and_warnings_filtered_by_severity():
    warn = SystemDiagnostic("W", "warn", severity=SystemDiagnosticSeverity.WARNING)
    err = SystemDiagnostic("E", "err", severity=SystemDiagnosticSeverity.ERROR)

    class Injector(SpellSystemValidationStrategy):
        def run(self, *, diagnostics, **_):
            diagnostics.extend([warn, err])

    result = SpellSystemValidationSystem([Injector()]).validate(
        index=_index_with_nodes("a"),
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": _StateStub()}),
    )
    assert result.errors == [err]
    assert result.warnings == [warn]


def test_cleanup_clears_strategies_list():
    strat = _RecordingStrategy()
    sys_val = SpellSystemValidationSystem([strat])
    sys_val.cleanup()
    assert sys_val._strategies is None  # noqa: SLF001


def test_validate_propagates_broken_spell_ids_to_strategies():
    strat = _RecordingStrategy()
    broken = {"b1", "b2"}
    SpellSystemValidationSystem([strat]).validate(
        index=_index_with_nodes("x"),
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=broken,
        spell_system_states=_States({"x": _StateStub()}),
    )
    assert strat.calls
    assert strat.calls[0][3] == broken


def test_state_set_validity_called_for_each_node():
    strat = _RecordingStrategy()
    idx = _index_with_nodes("a", "b", "c")
    states = _States({sid: _StateStub() for sid in idx.nodes})
    SpellSystemValidationSystem([strat]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
    )
    for sid in idx.nodes:
        assert states.mapping[sid].calls


def test_validate_returns_diagnostics_when_error_present():
    strat = _RecordingStrategy(severity=SystemDiagnosticSeverity.ERROR)
    idx = _index_with_nodes("a")
    result = SpellSystemValidationSystem([strat]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": _StateStub()}),
    )
    assert result.errors
    assert result.errors[0].severity is SystemDiagnosticSeverity.ERROR
    assert result.is_valid is False
