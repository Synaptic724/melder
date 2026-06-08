from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.mutation_research.mutation_frame import MutationFrame
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    get_frame_posture_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_runtime_singletons() -> None:
    """
    Reset runtime singletons around each mutation-research integration test.

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


def _make_dynamic_configuration(frame_name: str) -> SpellbookConfiguration:
    """
    Create one dynamic configuration for integration tests.

    Args:
        frame_name:
            Target Aether frame name.

    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    get_frame_posture_for_spellbook_configuration(
        configuration
    ).with_disable_mutations(False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_integration_aether_owned_root_is_shared_across_frames(case_index: int) -> None:
    """
    Validate one Aether-owned MutationResearch root is shared across frames.
    """
    aether = Aether()
    frame_name = f"integration-shared-frame-{case_index:02d}"
    aether._ensure_frame(frame_name)

    assert aether._get_mutation_research() is aether.mutation_research


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_integration_dynamic_conduit_returns_shared_root(case_index: int) -> None:
    """
    Validate dynamic conduits across many frames all return the Aether-owned root.
    """
    frame_name = f"integration-conduit-frame-{case_index:02d}"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_dynamic_configuration(frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name=f"root-{case_index:02d}")
    try:
        assert conduit.get_mutation_research() is conduit._aether.mutation_research
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_integration_create_mutation_frame_is_wired_to_live_frame_services(case_index: int) -> None:
    """
    Validate MutationFrame placeholders read the correct live frame services.
    """
    frame_name = f"integration-frame-surface-{case_index:02d}"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_dynamic_configuration(frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name=f"root-{case_index:02d}")
    try:
        placeholder = conduit._aether.mutation_research.create_mutation_frame(frame_name)
        assert isinstance(placeholder, MutationFrame)
        assert placeholder.spell_system_states is conduit._aether._get_spell_system_states(frame_name)
        assert placeholder.change_control_manager is conduit._aether._get_change_control_manager(frame_name)
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_integration_root_session_management_works_across_frames(case_index: int) -> None:
    """
    Validate the Aether-owned root can manage sessions for spell indexes from many frames.
    """
    frame_name = f"integration-session-frame-{case_index:02d}"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_dynamic_configuration(frame_name),
    )
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name=f"root-{case_index:02d}")
    try:
        spell = spellbook.find_spell_by_id(spell_id)
        assert spell is not None
        index = spell.spell_index
        root = conduit._aether.mutation_research
        session = root.create_session(index, name=f"session-{case_index:02d}")
        assert root.get_session_for_index(index) is session
        assert root.get_session_by_index_id(index.id) is session
    finally:
        conduit.cleanup()
