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
    """
    Test helper that records validation inputs and optionally emits a diagnostic.
    """
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
        spell_system_states,
        spell_lookup,
        diagnostics,
        cancel_event,
    ) -> None:
        """
        Capture validation inputs and optionally append a diagnostic.
        """
        self.calls.append(
            (
                index,
                blueprints,
                phase4_results,
                broken_spell_ids,
                spell_system_states,
                spell_lookup,
                diagnostics,
                cancel_event,
            )
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
    """
    Test double for per-conduit resolution updates in SpellSystemValidationSystem.
    """

    def __init__(
        self,
        mapping=None,
        *,
        raise_on_spell_set=False,
        raise_on_root_set=False,
        raise_on_diagnostics=False,
        raise_on_clear=False,
    ):
        """
        Purpose:
            Initialize the stub with optional error-injection flags.
        Contract:
            - Captures per-conduit resolution update calls for assertions.
            - Can be configured to raise in specific update paths.
        Args:
            mapping: Optional spell-id mapping retained for compatibility.
            raise_on_spell_set: When True, bulk spell validity updates raise.
            raise_on_root_set: When True, bulk root validity updates raise.
            raise_on_diagnostics: When True, diagnostics recording raises.
            raise_on_clear: When True, clearing dirty state raises.
        Returns:
            None.
        """
        self.mapping = mapping or {}
        self.raise_on_spell_set = raise_on_spell_set
        self.raise_on_root_set = raise_on_root_set
        self.raise_on_diagnostics = raise_on_diagnostics
        self.raise_on_clear = raise_on_clear
        self.spell_validity_calls = []
        self.root_validity_calls = []
        self.diagnostics_calls = []
        self.clear_dirty_calls = []

    def get_by_spell_id(self, spell_id):
        """
        Purpose:
            Provide a compatibility lookup for spell ids.
        Contract:
            - Returns the stored mapping value for the spell id, if any.
        Args:
            spell_id: Spell id to lookup.
        Returns:
            The mapped value or None.
        """
        return self.mapping.get(spell_id)

    def bulk_set_conduit_spell_validity(self, conduit_id, validity_map, *, change_reason=None):
        """
        Purpose:
            Record per-conduit spell validity updates.
        Contract:
            - Appends call details to spell_validity_calls.
            - Raises if raise_on_spell_set is enabled.
        Args:
            conduit_id: Conduit identifier for the update.
            validity_map: Mapping of spell_id -> SpellValidity.
            change_reason: Optional SpellStateChangeReason for the update.
        Returns:
            None.
        Raises:
            RuntimeError: When configured to raise on spell updates.
        """
        self.spell_validity_calls.append(
            (conduit_id, dict(validity_map), change_reason)
        )
        if self.raise_on_spell_set:
            raise RuntimeError("boom")

    def bulk_set_conduit_root_validity(self, conduit_id, validity_map, *, change_reason=None):
        """
        Purpose:
            Record per-conduit root validity updates.
        Contract:
            - Appends call details to root_validity_calls.
            - Raises if raise_on_root_set is enabled.
        Args:
            conduit_id: Conduit identifier for the update.
            validity_map: Mapping of root_id -> SpellValidity.
            change_reason: Optional SpellStateChangeReason for the update.
        Returns:
            None.
        Raises:
            RuntimeError: When configured to raise on root updates.
        """
        self.root_validity_calls.append(
            (conduit_id, dict(validity_map), change_reason)
        )
        if self.raise_on_root_set:
            raise RuntimeError("boom")

    def record_conduit_diagnostics(self, conduit_id, diagnostics):
        """
        Purpose:
            Record diagnostics associated with a conduit validation run.
        Contract:
            - Appends call details to diagnostics_calls.
            - Raises if raise_on_diagnostics is enabled.
        Args:
            conduit_id: Conduit identifier for the diagnostics.
            diagnostics: Sequence of SystemDiagnostic entries.
        Returns:
            None.
        Raises:
            RuntimeError: When configured to raise on diagnostics recording.
        """
        self.diagnostics_calls.append((conduit_id, list(diagnostics)))
        if self.raise_on_diagnostics:
            raise RuntimeError("boom")

    def clear_conduit_dirty(self, conduit_id, validated_at):
        """
        Purpose:
            Record clearing of conduit dirty state.
        Contract:
            - Appends call details to clear_dirty_calls.
            - Raises if raise_on_clear is enabled.
        Args:
            conduit_id: Conduit identifier for the update.
            validated_at: Validation timestamp.
        Returns:
            None.
        Raises:
            RuntimeError: When configured to raise on dirty clearing.
        """
        self.clear_dirty_calls.append((conduit_id, validated_at))
        if self.raise_on_clear:
            raise RuntimeError("boom")


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
            spell_lookup={},
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
        spell_lookup={},
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
        spell_lookup={},
    )
    assert strategy.calls
    (_, bp, p4, broken, _, spell_lookup, diags, _) = strategy.calls[-1]
    assert bp is blueprints
    assert p4 == {"a": 1}
    assert broken == {"b"}
    assert spell_lookup == {}
    assert diags == []


def test_validity_set_to_valid_when_no_errors():
    """
    Purpose:
        Verify conduit resolution validity is marked valid on warning-only output.
    Contract:
        - Spell and root validity are set to VALID with validation_passed.
        - Diagnostics are recorded and dirty state is cleared.
    Returns:
        None.
    Raises:
        AssertionError: If per-conduit validity or diagnostics are incorrect.
    """
    strategy = _RecordingStrategy(severity=SystemDiagnosticSeverity.WARNING)
    idx = _index_with_nodes("a", "b")
    states = _States({"a": _StateStub(), "b": _StateStub()})
    sys_val = SpellSystemValidationSystem([strategy])
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        conduit_id="cid",
    )
    assert states.spell_validity_calls == [
        ("cid", {"a": SpellValidity.valid, "b": SpellValidity.valid}, SpellStateChangeReason.validation_passed)
    ]
    assert states.root_validity_calls == [
        ("cid", {"root": SpellValidity.valid}, SpellStateChangeReason.validation_passed)
    ]
    assert states.diagnostics_calls
    assert states.diagnostics_calls[-1][0] == "cid"
    assert states.diagnostics_calls[-1][1][0].severity is SystemDiagnosticSeverity.WARNING
    assert len(states.clear_dirty_calls) == 1
    assert states.clear_dirty_calls[0][0] == "cid"
    assert isinstance(states.clear_dirty_calls[0][1], float)
    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings and result.warnings[0].severity is SystemDiagnosticSeverity.WARNING
    assert result.warnings[0].source == "_RecordingStrategy"
    assert result.nodes == idx.nodes


def test_validity_set_to_gated_on_error_diagnostic():
    """
    Purpose:
        Verify conduit resolution validity is marked invalid on error output.
    Contract:
        - Spell and root validity are set to INVALID with validation_failed.
        - Diagnostics are recorded and dirty state is not cleared.
    Returns:
        None.
    Raises:
        AssertionError: If per-conduit validity is not invalid on errors.
    """
    strategy = _RecordingStrategy(severity=SystemDiagnosticSeverity.ERROR)
    idx = _index_with_nodes("a")
    sys_val = SpellSystemValidationSystem([strategy])
    states = _States({"a": _StateStub()})
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        conduit_id="cid",
    )
    assert states.spell_validity_calls == [
        ("cid", {"a": SpellValidity.invalid}, SpellStateChangeReason.validation_failed)
    ]
    assert states.root_validity_calls == [
        ("cid", {"root": SpellValidity.invalid}, SpellStateChangeReason.validation_failed)
    ]
    assert states.diagnostics_calls
    assert states.clear_dirty_calls == []
    assert result.is_valid is False
    assert result.errors and result.errors[0].severity is SystemDiagnosticSeverity.ERROR
    assert result.errors[0].source == "_RecordingStrategy"
    assert result.warnings == []


def test_set_validity_skips_missing_state_and_swallows_errors():
    """
    Purpose:
        Ensure per-conduit state update failures do not crash validation.
    Contract:
        - Exceptions raised by resolution-state updates are swallowed.
        - Validation still returns a successful result when no diagnostics exist.
    Returns:
        None.
    Raises:
        AssertionError: If errors propagate or result validity is incorrect.
    """
    strategy = _RecordingStrategy()  # no diagnostics -> valid path
    idx = _index_with_nodes("a", "b")
    states = _States({"a": _StateStub(), "b": _StateStub()}, raise_on_spell_set=True)
    sys_val = SpellSystemValidationSystem([strategy])
    result = sys_val.validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        conduit_id="cid",
    )
    assert states.spell_validity_calls
    assert states.diagnostics_calls == []
    assert states.clear_dirty_calls == []
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
            spell_lookup={},
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
            spell_lookup={},
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
            spell_lookup={},
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
        spell_lookup={},
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
        spell_lookup={},
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
        spell_lookup={},
    )
    assert {d.code for d in result.warnings} == {"W1", "W2"}
    assert result.errors == []
    assert result.is_valid is True


def test_error_overrides_warnings_for_validity():
    """
    Purpose:
        Verify error diagnostics override warnings for conduit validity.
    Contract:
        - Conduit spell validity is INVALID when errors are present.
    Returns:
        None.
    Raises:
        AssertionError: If error diagnostics do not drive invalid validity.
    """
    warn = _RecordingStrategy(severity=SystemDiagnosticSeverity.WARNING)
    err = _RecordingStrategy(severity=SystemDiagnosticSeverity.ERROR)
    idx = _index_with_nodes("a")
    states = _States({"a": _StateStub()})
    result = SpellSystemValidationSystem([warn, err]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        conduit_id="cid",
    )
    assert result.is_valid is False
    assert result.errors
    assert states.spell_validity_calls[-1] == (
        "cid",
        {"a": SpellValidity.invalid},
        SpellStateChangeReason.validation_failed,
    )


def test_validate_returns_nodes_reference():
    idx = _index_with_nodes("a", "b")
    result = SpellSystemValidationSystem([]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": _StateStub(), "b": _StateStub()}),
        spell_lookup={},
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
        spell_lookup={},
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
            spell_lookup={},
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
        spell_lookup={},
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
        spell_lookup={},
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
        spell_lookup={},
    )
    assert strat.calls
    assert strat.calls[0][3] == broken


def test_state_set_validity_called_for_each_node():
    """
    Purpose:
        Ensure all index nodes are included in per-conduit validity updates.
    Contract:
        - bulk_set_conduit_spell_validity receives all node ids.
    Returns:
        None.
    Raises:
        AssertionError: If any index node is missing from the validity map.
    """
    strat = _RecordingStrategy()
    idx = _index_with_nodes("a", "b", "c")
    states = _States({sid: _StateStub() for sid in idx.nodes})
    SpellSystemValidationSystem([strat]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=states,
        spell_lookup={},
        conduit_id="cid",
    )
    assert states.spell_validity_calls
    validity_map = states.spell_validity_calls[-1][1]
    assert set(validity_map.keys()) == set(idx.nodes.keys())
    assert all(validity is SpellValidity.valid for validity in validity_map.values())


def test_validate_returns_diagnostics_when_error_present():
    strat = _RecordingStrategy(severity=SystemDiagnosticSeverity.ERROR)
    idx = _index_with_nodes("a")
    result = SpellSystemValidationSystem([strat]).validate(
        index=idx,
        blueprints=_blueprint(),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=_States({"a": _StateStub()}),
        spell_lookup={},
    )
    assert result.errors
    assert result.errors[0].severity is SystemDiagnosticSeverity.ERROR
    assert result.is_valid is False
