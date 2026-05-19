from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_crafter.validation.spell_validation_context import SpellValidationContext
from melder.aether.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_validation_context() -> None:
    """
    Purpose:
        Ensure component validation context tests start with a clean Aether singleton.
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
        Provide a Spellbook configured for validation context component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> Optional[object]:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the spell mapped in the live _spell_id_pool for `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    return spellbook._spell_id_pool.get(spell_id)


def test_component_validation_context_cleanup_preserves_issues_and_cleans_artifacts() -> None:
    """
    Purpose:
        Validate SpellValidationContext cleanup preserves shared issues and cleans artifacts.
    Contract:
        - Cleanup leaves the shared issues list intact.
        - Cleanup calls cleanup on requirements, symbolic graph, and resolution frame.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clean artifacts or mutates issues.
    """
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        requirements = spell.requirements
        symbolic_graph = spell.symbolic_graph
        resolution_frame = spell.resolution_frame
        assert requirements is not None
        assert symbolic_graph is not None
        assert resolution_frame is not None

        issues = [SpellValidationIssue("warning", "TEST", "test")]
        context = SpellValidationContext(
            spell=spell,
            spellbook=spellbook,
            requirements=requirements,
            symbolic_graph=symbolic_graph,
            resolution_frame=resolution_frame,
            cancel_event=None,
            issues=issues,
        )
        context.cleanup()

        assert issues[0].code == "TEST"
        assert requirements.cleaned is True
        assert symbolic_graph.cleaned is True
        assert resolution_frame.cleaned is True
        assert context.cleaned is True
    finally:
        spellbook.cleanup()
