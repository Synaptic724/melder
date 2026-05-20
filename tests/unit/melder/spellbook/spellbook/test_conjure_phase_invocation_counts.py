from typing import Any, Dict

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from tests.mocks.spellbook.core_classes import BasicConfig
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
        Wrap a SpellCompilerSystem phase method to count invocations.
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
    original = getattr(SpellCompilerSystem, method_name)

    def _wrapped(self: SpellCompilerSystem, *args: Any, **kwargs: Any) -> None:
        """
        Purpose:
            Count a SpellCompilerSystem phase invocation before delegating to the original method.
        Contract:
            - Increments the supplied counter exactly once per call.
            - Preserves the original method behavior and return value.
        Args:
            self: SpellCompilerSystem instance.
            *args: Positional arguments passed to the original method.
            **kwargs: Keyword arguments passed to the original method.
        Returns:
            None.
        """
        counters[counter_key] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SpellCompilerSystem, method_name, _wrapped)


def _wrap_phase_method_record_spell_ids(
    monkeypatch: pytest.MonkeyPatch,
    records: Dict[str, list[str]],
    method_name: str,
    record_key: str,
) -> None:
    """
    Purpose:
        Wrap a SpellCompilerSystem phase method and record spell ids per invocation.
    Contract:
        - Appends self._spell.spell_id to records[record_key] once per call.
        - Delegates to the original method to preserve behavior.
    Args:
        monkeypatch: Pytest monkeypatch fixture.
        records: Mutable mapping of record lists.
        method_name: SpellCrafter method name to wrap.
        record_key: Key in records to append spell ids into.
    Returns:
        None.
    """
    original = getattr(SpellCompilerSystem, method_name)

    def _wrapped(self: SpellCompilerSystem, *args: Any, **kwargs: Any) -> None:
        """
        Purpose:
            Record compiler-phase invocation spell identity before delegation.
        Contract:
            - Appends exactly one spell id per invocation.
            - Preserves the original method behavior and return value.
        Args:
            self: SpellCompilerSystem instance.
            *args: Positional arguments passed to the original method.
            **kwargs: Keyword arguments passed to the original method.
        Returns:
            None.
        """
        if method_name in ("run_phase_injection_plan", "run_phase_patch_maps"):
            spell = args[0]
        else:
            spell = args[1]
        records[record_key].append(spell.spell_id)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SpellCompilerSystem, method_name, _wrapped)


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

        spellbook.conjure(name="root")

        assert counters["root_blueprints"] == 1
        assert counters["system_validation"] == 1
        assert counters["change_control"] == 1
    finally:
        spellbook.cleanup()


def test_component_meld_revalidation_uses_local_phase_5_6_7(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify meld-triggered revalidation executes local phases 5/6/7.
    Contract:
        - Post-conjure bind + meld triggers local phase methods once.
        - Frame-wide phase methods are not invoked during the meld revalidation pass.
        - Conjure still uses frame-wide phases once.
    Returns:
        None.
    Raises:
        AssertionError: If routing does not use local phase methods.
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
            "root_blueprints_local": 0,
            "system_validation_local": 0,
            "change_control_local": 0,
        }

        _wrap_phase_method(monkeypatch, counters, "run_phase_root_blueprints", "root_blueprints")
        _wrap_phase_method(monkeypatch, counters, "run_phase_system_validation", "system_validation")
        _wrap_phase_method(monkeypatch, counters, "run_phase_change_control", "change_control")
        _wrap_phase_method(
            monkeypatch,
            counters,
            "run_phase_root_blueprints_local",
            "root_blueprints_local",
        )
        _wrap_phase_method(
            monkeypatch,
            counters,
            "run_phase_system_validation_local",
            "system_validation_local",
        )
        _wrap_phase_method(
            monkeypatch,
            counters,
            "run_phase_change_control_local",
            "change_control_local",
        )

        conduit = spellbook.conjure(name="root")
        assert counters["root_blueprints"] == 1
        assert counters["system_validation"] == 1
        assert counters["change_control"] == 1

        counters["root_blueprints"] = 0
        counters["system_validation"] = 0
        counters["change_control"] = 0
        counters["root_blueprints_local"] = 0
        counters["system_validation_local"] = 0
        counters["change_control_local"] = 0

        spellbook.begin_transaction("bind")
        local_spell_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.end_transaction("bind")
        resolved = conduit.meld(spell=local_spell_id)

        assert resolved is not None
        assert counters["root_blueprints"] == 0
        assert counters["system_validation"] == 0
        assert counters["change_control"] == 0
        assert counters["root_blueprints_local"] == 1
        assert counters["system_validation_local"] == 1
        assert counters["change_control_local"] == 1
    finally:
        spellbook.cleanup()


def test_component_meld_revalidation_phase_8_to_11_runs_for_target_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify local meld revalidation compiles phase 8-11 only for target spell.
    Contract:
        - Post-conjure bind + meld executes phase 8/9/10/11 for the new target spell.
        - No unrelated spell ids are recorded for these phases during the meld pass.
    Returns:
        None.
    Raises:
        AssertionError: If phase 8-11 compile unrelated spells during local revalidation.
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

        records: Dict[str, list[str]] = {
            "occurrence": [],
            "injection": [],
            "patch": [],
            "execution": [],
        }
        _wrap_phase_method_record_spell_ids(
            monkeypatch,
            records,
            "run_phase_occurrence_plan",
            "occurrence",
        )
        _wrap_phase_method_record_spell_ids(
            monkeypatch,
            records,
            "run_phase_injection_plan",
            "injection",
        )
        _wrap_phase_method_record_spell_ids(
            monkeypatch,
            records,
            "run_phase_patch_maps",
            "patch",
        )
        _wrap_phase_method_record_spell_ids(
            monkeypatch,
            records,
            "run_phase_execution_plan",
            "execution",
        )

        conduit = spellbook.conjure(name="root")

        records["occurrence"].clear()
        records["injection"].clear()
        records["patch"].clear()
        records["execution"].clear()

        spellbook.begin_transaction("bind")
        local_spell_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.end_transaction("bind")
        resolved = conduit.meld(spell=local_spell_id)

        assert resolved is not None
        assert records["occurrence"] == [local_spell_id]
        assert records["injection"] == [local_spell_id]
        assert records["patch"] == [local_spell_id]
        assert records["execution"] == [local_spell_id]
    finally:
        spellbook.cleanup()

