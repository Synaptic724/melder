"""Regression: BUG-072 (2026-07-17 audit) - None singletons are present, not absent.

Symptom:
    The emitted CreationContext door lanes used `None` both as a valid stored
    creation and as the absent sentinel. A legally `None`-returning
    `Existence.unique` provider was stored on first resolution, but the next
    resolution treated the stored `None` as absent and invoked the provider
    again - the duplicate store then raised ValueError, and provider side
    effects repeated.

Contract under test:
    Emitted singleton lanes test presence with a private missing-value
    sentinel: repeated resolution returns the first stored result even when
    that result is None, the provider runs exactly once, and the overrides
    lane refuses to override an existing stored-None singleton.
"""

import threading
from types import SimpleNamespace
from typing import Any, List

import pytest

from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_instance_no_overrides_executor,
    compile_creation_context_instance_overrides_only_executor,
    compile_creation_context_hooks_no_overrides_executor,
)


class DummyMeldExecutionError(Exception):
    """Meld-error double matching the emitted constructor signature."""

    def __init__(self, *, spell_id: str, spell_name: str, message: str) -> None:
        """Record the emitted error payload."""
        super().__init__(message)
        self.spell_id = spell_id
        self.spell_name = spell_name


def _build_spell(store: Creations) -> SimpleNamespace:
    """Build the minimal spell double the `unique` door lanes read.

    Contract:
        - Carries `_lock` (the unique route's creation lock),
          `_owner_creations` (the real store), and the identity fields the
          emitted error paths format.
    """
    return SimpleNamespace(
        _lock=threading.RLock(),
        _owner_creations=store,
        spell_name="none-spell",
        spell_index=SimpleNamespace(selected_spell_id="spell-none"),
    )


def _build_none_executor(store: Creations, calls: List[int]) -> Any:
    """Build a provider double mirroring the solo `unique` executor lane.

    Contract:
        - Increments the shared call counter, stores its (None) result in the
          spell-owned store exactly like the emitted solo executor, and
          returns the result.
    """

    def executor(meld: Any) -> None:
        """Run the None-returning unique provider once."""
        calls.append(1)
        store.add_creation("spell-none", None)
        return None

    return executor


def test_repeated_resolution_returns_stored_none_without_rerunning_provider() -> None:
    """The audited repro on the instance no-overrides `unique` door.

    Contract assertions:
        - First resolution stores and returns None; provider ran once.
        - Second resolution returns the stored None WITHOUT re-invoking the
          provider (broken code re-ran it and died on the duplicate store's
          ValueError).
    """
    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")
    calls: List[int] = []
    spell = _build_spell(store)
    door = compile_creation_context_instance_no_overrides_executor(
        resolve_route_key="unique",
        fast_transient_no_overrides_enabled=False,
        spell=spell,
        spell_id="spell-none",
        no_overrides_executor=_build_none_executor(store, calls),
        spell_space_scope_error_type=RuntimeError,
    )

    first = door(None)
    assert first is None
    assert len(calls) == 1
    assert "spell-none" in store._creations

    second = door(None)

    assert second is None
    assert len(calls) == 1, (
        "a stored-None singleton was mistaken for absent and the provider "
        "re-ran (the audited BUG-072 symptom)"
    )
    store.cleanup()


def test_hooks_lane_reports_stored_none_as_not_created() -> None:
    """The hooks door returns `(None, False)` for the stored-None singleton.

    Contract assertions:
        - First resolution reports `(None, True)` (created).
        - Second resolution reports `(None, False)` with no provider re-run.
    """
    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")
    calls: List[int] = []
    spell = _build_spell(store)
    door = compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key="unique",
        fast_transient_no_overrides_enabled=False,
        spell=spell,
        spell_id="spell-none",
        no_overrides_executor=_build_none_executor(store, calls),
        spell_space_scope_error_type=RuntimeError,
    )

    first_instance, first_created = door(None)
    second_instance, second_created = door(None)

    assert first_instance is None and first_created is True
    assert second_instance is None and second_created is False
    assert len(calls) == 1
    store.cleanup()


def test_overrides_lane_refuses_to_override_a_stored_none_singleton() -> None:
    """Overriding an existing (None) singleton must raise, not re-create.

    Contract assertions:
        - With `None` stored, the overrides-only door raises the meld error
          on its presence check (broken code saw "absent" and created a
          second instance over the stored singleton).
        - The override executor never runs.
    """
    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")
    store.add_creation("spell-none", None)
    spell = _build_spell(store)
    override_calls: List[int] = []

    def execute_with_overrides(meld: Any, overrides: Any) -> object:
        """Override-executor double that must stay uncalled."""
        override_calls.append(1)
        return object()

    door = compile_creation_context_instance_overrides_only_executor(
        resolve_route_key="unique",
        spell=spell,
        spell_id="spell-none",
        no_overrides_executor=None,
        execute_with_overrides=execute_with_overrides,
        meld_execution_error_type=DummyMeldExecutionError,
        spell_space_scope_error_type=RuntimeError,
    )

    with pytest.raises(DummyMeldExecutionError, match="already exists"):
        door(None, {"value": 1})

    assert override_calls == [], (
        "the overrides lane created over an existing stored-None singleton"
    )
    store.cleanup()


def test_non_none_singleton_behavior_is_unchanged() -> None:
    """Behavior guard: ordinary singleton reuse is untouched by the sentinel.

    Contract assertions:
        - A concrete stored instance is returned on both resolutions with a
          single provider run.
    """
    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")
    calls: List[int] = []
    payload = object()
    spell = _build_spell(store)

    def executor(meld: Any) -> object:
        """Concrete-instance provider double."""
        calls.append(1)
        store.add_creation("spell-none", payload)
        return payload

    door = compile_creation_context_instance_no_overrides_executor(
        resolve_route_key="unique",
        fast_transient_no_overrides_enabled=False,
        spell=spell,
        spell_id="spell-none",
        no_overrides_executor=executor,
        spell_space_scope_error_type=RuntimeError,
    )

    assert door(None) is payload
    assert door(None) is payload
    assert len(calls) == 1
    store.cleanup()
