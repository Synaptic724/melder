from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.mutation_research.mutation_conduit import MutationConduit
from melder.mutation_research.mutation_frame import MutationFrame
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


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


def _make_dynamic_configuration(frame_name: str) -> Configuration:
    """
    Create one dynamic configuration for integration tests.

    Args:
        frame_name:
            Target Aether frame name.

    Returns:
        Configuration: Dynamic configuration instance.
    """
    configuration = Configuration(aether_frame=frame_name)
    configuration.dynamic_defaults()
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
    conduit = spellbook.conjure(automatic=False, name=f"root-{case_index:02d}")
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
    conduit = spellbook.conjure(automatic=False, name=f"root-{case_index:02d}")
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
    conduit = spellbook.conjure(automatic=False, name=f"root-{case_index:02d}")
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
