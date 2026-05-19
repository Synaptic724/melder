import pytest

from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.utilities.general_base.cleanable import Cleanable


class _FakeDiag(Cleanable):
    __slots__ = ("cleaned_count", "_raise_on_cleanup")

    def __init__(self, raise_on_cleanup: bool = False) -> None:
        super().__init__()
        self.cleaned_count = 0
        self._raise_on_cleanup = raise_on_cleanup

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self.cleaned_count += 1
        self._cleaned = True
        if self._raise_on_cleanup:
            raise RuntimeError("boom")


def _state(
    *,
    is_valid: bool = True,
    errors=None,
    warnings=None,
    nodes=None,
) -> SpellSystemValidationState:
    return SpellSystemValidationState(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        nodes=nodes,
    )


def test_properties_return_copies_and_are_isolated():
    err = _FakeDiag()
    warn = _FakeDiag()
    nodes = {"s": SpellSystemNode("sid", "lid")}
    state = _state(errors=[err], warnings=[warn], nodes=nodes, is_valid=False)

    assert state.is_valid is False

    errs_first = state.errors
    warns_first = state.warnings
    assert errs_first == [err]
    assert warns_first == [warn]

    # Mutating returned snapshots should not mutate internal storage.
    errs_first.append("mut")
    warns_first.clear()
    assert state.errors == [err]
    assert state.warnings == [warn]

    # Nodes are not copied (mapping is treated as opaque)
    assert state.nodes is nodes


def test_cleanup_disposes_children_and_nulls_collections():
    errors = [_FakeDiag(), _FakeDiag(raise_on_cleanup=True)]
    warnings = [_FakeDiag()]
    nodes = {"n": SpellSystemNode("sid", "lid")}
    state = _state(errors=errors, warnings=warnings, nodes=nodes)

    state.cleanup()
    # child cleanups executed and swallowed even if raising
    assert errors[0].cleaned_count == 1
    assert errors[1].cleaned_count == 1
    assert warnings[0].cleaned_count == 1

    assert state._errors == []
    assert state._warnings == []
    assert state._nodes is None
    assert state.cleaned is True

    # idempotent
    state.cleanup()
    assert errors[0].cleaned_count == 1


def test_properties_raise_after_cleanup():
    state = _state()
    state.cleanup()
    with pytest.raises(RuntimeError):
        _ = state.is_valid
    with pytest.raises(RuntimeError):
        _ = state.errors
    with pytest.raises(RuntimeError):
        _ = state.warnings
    with pytest.raises(RuntimeError):
        _ = state.nodes


def test_accessing_nodes_before_cleanup_allowed():
    node = SpellSystemNode("sid", "lid")
    state = _state(nodes={"sid": node})
    assert state.nodes["sid"] is node


def test_cleanup_is_noop_when_already_cleaned():
    diag = _FakeDiag()
    state = _state(errors=[diag])
    state.cleanup()
    state.cleanup()
    assert diag.cleaned_count == 1


def test_defaults_produce_empty_collections():
    state = _state()
    errs = state.errors
    warns = state.warnings
    assert errs == []
    assert warns == []
    assert errs is not state.errors  # copies each call
    assert warns is not state.warnings
    assert state.nodes is None


def test_is_valid_coerces_truthy_and_falsey():
    assert _state(is_valid=1).is_valid is True
    assert _state(is_valid="").is_valid is False


def test_error_warning_order_preserved_and_copied():
    e1, e2 = _FakeDiag(), _FakeDiag()
    w1, w2 = _FakeDiag(), _FakeDiag()
    state = _state(errors=[e1, e2], warnings=[w1, w2])
    assert state.errors == [e1, e2]
    assert state.warnings == [w1, w2]
    first = state.errors
    second = state.errors
    assert first == second
    assert first is not second


def test_mutating_input_lists_after_init_does_not_leak():
    e = _FakeDiag()
    w = _FakeDiag()
    errs = [e]
    warns = [w]
    state = _state(errors=errs, warnings=warns)
    errs.append("boom")
    warns.clear()
    assert state.errors == [e]
    assert state.warnings == [w]


def test_nodes_mapping_passthrough_and_not_cleaned():
    node = SpellSystemNode("sid", "lid")
    state = _state(nodes={"sid": node})
    # nodes reference is shared until cleanup
    assert state.nodes["sid"] is node
    state.cleanup()
    # cleanup should not attempt to clean nodes; they stay untouched
    assert node.cleaned is False
    assert state._nodes is None


def test_cleanup_swallows_warning_exceptions():
    warn = _FakeDiag(raise_on_cleanup=True)
    state = _state(warnings=[warn])
    state.cleanup()
    assert warn.cleaned_count == 1


def test_properties_after_partial_cleanup_raise():
    state = _state()
    state.cleanup()
    with pytest.raises(RuntimeError):
        _ = state.errors


def test_nodes_can_be_none_and_accessed_multiple_times():
    state = _state(nodes=None)
    assert state.nodes is None
    assert state.nodes is None


def test_cleaned_flag_set_after_cleanup():
    state = _state()
    assert state.cleaned is False
    state.cleanup()
    assert state.cleaned is True
