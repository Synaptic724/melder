from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig


class RootWithConfig:
    """
    Purpose:
        Provide a root spell that depends on BasicConfig.
    Contract:
        - Stores the injected BasicConfig for assertions.
    """

    def __init__(self, config: BasicConfig) -> None:
        """
        Purpose:
            Capture the injected configuration instance.
        Contract:
            - Stores the config instance.
        Args:
            config: Injected BasicConfig instance.
        Returns:
            None.
        """
        self.config = config


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
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
        Provide a Spellbook configured for Phase 11 integration tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_phase11_execution_plan_compiled_for_root() -> None:
    """
    Purpose:
        Validate Phase 11 execution plans compile for root spells.
    Contract:
        - execution_plan_phase11 is populated after run_all_phases.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        assert root_spell._crafter is not None
        assert root_spell._crafter.execution_plan_phase11 is not None
        assert root_spell._crafter.execution_plan_phase11.steps
    finally:
        spellbook.cleanup()


def test_phase11_execution_plan_preserved_after_phase_cleanup() -> None:
    """
    Purpose:
        Ensure Phase 11 plans persist after run_all_phases cleanup.
    Contract:
        - execution_plan_phase11 remains available after run_all_phases.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        plan = root_spell._crafter.execution_plan_phase11
        assert plan is not None
        assert plan.root_spell_id == root_id
    finally:
        spellbook.cleanup()


def test_phase11_execution_plan_occurrence_path_recorded() -> None:
    """
    Purpose:
        Verify Phase 11 steps include canonical occurrence paths.
    Contract:
        - Each step includes an occurrence tuple with a spell id.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        plan = root_spell._crafter.execution_plan_phase11
        assert plan is not None
        assert all(step.occurrence[0] for step in plan.steps)
    finally:
        spellbook.cleanup()


def test_phase11_meld_returns_expected_instance() -> None:
    """
    Purpose:
        Validate meld returns expected instances after Phase 11 compilation.
    Contract:
        - Meld returns a ServiceWithConfig instance with config injected.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")
    conduit = spellbook.conjure(name="root")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        instance = conduit.meld(spell=root_id)
        assert isinstance(instance, RootWithConfig)
        assert isinstance(instance.config, BasicConfig)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_phase11_plan_survives_multiple_runs() -> None:
    """
    Purpose:
        Ensure Phase 11 plan remains available across multiple run_all_phases calls.
    Contract:
        - execution_plan_phase11 exists after each run_all_phases invocation.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        assert root_spell._crafter.execution_plan_phase11 is not None
        root_spell.run_all_phases("cid")
        assert root_spell._crafter.execution_plan_phase11 is not None
    finally:
        spellbook.cleanup()


def test_phase11_execution_plan_step_count_matches_occurrence_plan() -> None:
    """
    Purpose:
        Validate Phase 11 steps align with Phase 8 instance planning counts.
    Contract:
        - Step count equals the sum of instance keys across spell ids.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        plan = root_spell._crafter.execution_plan_phase11
        occurrence_plan = root_spell._crafter.occurrence_plan_phase8
        assert plan is not None
        assert occurrence_plan is not None
        expected_steps = sum(
            len(keys) for keys in occurrence_plan.instance_keys_by_spell_id.values()
        )
        assert len(plan.steps) == expected_steps
    finally:
        spellbook.cleanup()


def test_phase11_execution_plan_root_key_matches_occurrence_plan() -> None:
    """
    Purpose:
        Ensure Phase 11 root instance key matches Phase 8 planning.
    Contract:
        - ExecutionPlan.root_instance_key equals OccurrencePlan.root_instance_key.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    root_id = spellbook.bind(spell=RootWithConfig, existence=Existence.unique, permissions="create")

    try:
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")
        plan = root_spell._crafter.execution_plan_phase11
        occurrence_plan = root_spell._crafter.occurrence_plan_phase8
        assert plan is not None
        assert occurrence_plan is not None
        assert plan.root_instance_key == occurrence_plan.root_instance_key
    finally:
        spellbook.cleanup()
