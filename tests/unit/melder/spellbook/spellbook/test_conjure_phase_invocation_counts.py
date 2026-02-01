from typing import Any, Dict

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_crafter import SpellCrafter
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import RepositoryWithLogger
from tests.mocks.spellbook.core_classes import ServiceWithRepository
from tests.mocks.spellbook.protocols import ILogger
from tests.mocks.spellbook.protocols import IRepository


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_phase_invocation_counts() -> None:
    """
    Purpose:
        Reset the Aether singleton for phase invocation count tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for phase invocation count tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1 for deterministic order.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _wrap_phase_method(
    monkeypatch: pytest.MonkeyPatch,
    counters: Dict[str, int],
    method_name: str,
    counter_key: str,
) -> None:
    """
    Purpose:
        Wrap a SpellCrafter phase method to count invocations.
    Contract:
        - Increments counters[counter_key] once per method call.
        - Delegates to the original method to preserve behavior.
    Args:
        monkeypatch: Pytest monkeypatch fixture.
        counters: Mutable counter map keyed by phase label.
        method_name: SpellCrafter method name to wrap.
        counter_key: Key to increment in the counter map.
    Returns:
        None.
    """
    original = getattr(SpellCrafter, method_name)

    def _wrapped(self: SpellCrafter, *args: Any, **kwargs: Any) -> None:
        """
        Purpose:
            Count a SpellCrafter phase invocation before delegating to the original method.
        Contract:
            - Increments the supplied counter exactly once per call.
            - Preserves the original method behavior and return value.
        Args:
            self: SpellCrafter instance.
            *args: Positional arguments passed to the original method.
            **kwargs: Keyword arguments passed to the original method.
        Returns:
            None.
        """
        counters[counter_key] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SpellCrafter, method_name, _wrapped)


def test_component_frame_level_phase_invocations_are_per_spell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Capture current phase scheduling behavior for frame-level phases.
    Contract:
        - Phase 5/6/7 are frame-level and invoked once per conjure.
        - Conjure completes successfully for a small, valid spell graph.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    try:
        spellbook.bind(
            spell=BasicLogger,
            existence=Existence.unique,
            permissions="create",
            spellframe=ILogger,
        )
        spellbook.bind(
            spell=RepositoryWithLogger,
            existence=Existence.unique,
            permissions="create",
            spellframe=IRepository,
        )
        spellbook.bind(
            spell=ServiceWithRepository,
            existence=Existence.unique,
            permissions="create",
        )

        counters = {
            "root_blueprints": 0,
            "system_validation": 0,
            "change_control": 0,
        }

        _wrap_phase_method(
            monkeypatch,
            counters,
            "run_phase_root_blueprints",
            "root_blueprints",
        )
        _wrap_phase_method(
            monkeypatch,
            counters,
            "run_phase_system_validation",
            "system_validation",
        )
        _wrap_phase_method(
            monkeypatch,
            counters,
            "run_phase_change_control",
            "change_control",
        )

        spellbook.conjure()

        assert counters["root_blueprints"] == 1
        assert counters["system_validation"] == 1
        assert counters["change_control"] == 1
    finally:
        spellbook.cleanup()
