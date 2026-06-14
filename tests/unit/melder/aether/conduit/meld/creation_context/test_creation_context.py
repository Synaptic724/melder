"""Focused runtime contract tests for the direct CreationContext doors."""

from types import SimpleNamespace
from typing import Any, Optional

import pytest

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)


class _Gate:
    """Minimal CreationGate stub for execute-path tests."""

    def __init__(self, *, enabled: bool = True, closed: bool = False) -> None:
        self.enabled = enabled
        self._closed = closed
        self.wait_calls = 0
        self.register_calls = 0
        self.unregister_calls = 0

    def is_closed(self) -> bool:
        return self._closed

    def wait(self) -> None:
        self.wait_calls += 1

    def register_ticket(self) -> None:
        self.register_calls += 1

    def unregister_ticket(self) -> None:
        self.unregister_calls += 1


def _make_spell(spell_id: str = "spell-1") -> Any:
    """Build a minimal spell stub for CreationContext tests."""
    owner_creations = SimpleNamespace(get_creation=lambda target_spell_id: None)
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
        _owner_creations=owner_creations,
    )


def test_init_requires_creation_gate_in_dynamic_mode() -> None:
    """Dynamic contexts should require a CreationGate."""
    with pytest.raises(ValueError, match="creation_gate cannot be None"):
        CreationContext(
            spell=_make_spell(),
            dynamic_environment=True,
            creation_gate=None,
            creation_gate_index_id="index-1",
            no_overrides_executor=lambda caller_creations, root_creations=None: ("plain", True),
            overrides_executor=lambda caller_creations, overrides, root_creations=None: ("override", True),
        )


def test_execute_automatic_mode_uses_no_overrides_executor() -> None:
    """Automatic execution should route to the no-overrides door when overrides are absent."""
    calls = []

    def _no_overrides_executor(caller_creations: Any, root_creations: Any = None) -> tuple[str, bool]:
        calls.append((caller_creations,))
        return "plain", True

    context = CreationContext(
        spell=_make_spell(),
        no_overrides_executor=_no_overrides_executor,
        overrides_executor=lambda caller_creations, overrides, root_creations=None: ("override", True),
    )
    caller_creations = object()

    assert context.execute(caller_creations) == ("plain", True)
    assert calls == [(caller_creations,)]


def test_execute_automatic_mode_uses_overrides_executor() -> None:
    """Automatic execution should route to the overrides door when payload exists."""
    calls = []

    def _overrides_executor(
            caller_creations: Any,
            overrides: dict[str, Any],
            root_creations: Any = None,
    ) -> tuple[str, bool]:
        calls.append((caller_creations, overrides))
        return "override", True

    context = CreationContext(
        spell=_make_spell(),
        no_overrides_executor=lambda caller_creations, root_creations=None: ("plain", True),
        overrides_executor=_overrides_executor,
    )
    caller_creations = object()

    assert context.execute(caller_creations, {"dep": "value"}) == ("override", True)
    assert calls == [(caller_creations, {"dep": "value"})]


def test_execute_no_hooks_discards_created_flag() -> None:
    """No-hooks execution should return only the instance value."""
    context = CreationContext(
        spell=_make_spell(),
        no_overrides_executor=lambda caller_creations, root_creations=None: ("plain", True),
        overrides_executor=lambda caller_creations, overrides, root_creations=None: ("override", False),
    )

    assert context.execute_no_hooks(object()) == "plain"
    assert context.execute_no_hooks(object(), {"dep": "value"}) == "override"


def test_dynamic_execute_waits_registers_and_unregisters_gate() -> None:
    """Dynamic execution should wait on disabled gates and balance ticket registration."""
    gate = _Gate(enabled=False, closed=False)
    context = CreationContext(
        spell=_make_spell(),
        dynamic_environment=True,
        creation_gate=gate,
        creation_gate_index_id="index-1",
        no_overrides_executor=lambda caller_creations, root_creations=None: ("plain", True),
        overrides_executor=lambda caller_creations, overrides, root_creations=None: ("override", True),
    )

    assert context.execute(object()) == ("plain", True)
    assert gate.wait_calls == 1
    assert gate.register_calls == 1
    assert gate.unregister_calls == 1


def test_dynamic_execute_raises_when_gate_is_closed() -> None:
    """Dynamic execution should fail fast when the CreationGate is closed."""
    gate = _Gate(enabled=True, closed=True)
    context = CreationContext(
        spell=_make_spell(),
        dynamic_environment=True,
        creation_gate=gate,
        creation_gate_index_id="index-closed",
        no_overrides_executor=lambda caller_creations, root_creations=None: ("plain", True),
        overrides_executor=lambda caller_creations, overrides, root_creations=None: ("override", True),
    )

    with pytest.raises(RuntimeError, match="CreationGate is closed"):
        context.execute(object())

    assert gate.register_calls == 0
    assert gate.unregister_calls == 0


def test_execute_fails_when_base_executor_inputs_are_missing() -> None:
    """Direct contexts without required base executors should fail when invoked."""
    context = CreationContext(
        spell=_make_spell(),
        no_overrides_executor=None,
        overrides_executor=None,
    )

    with pytest.raises(TypeError, match="callable"):
        context.execute(object())
    with pytest.raises(TypeError, match="callable"):
        context.execute(object(), {"dep": "value"})
