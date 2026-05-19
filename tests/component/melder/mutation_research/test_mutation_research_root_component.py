from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.mutation_research.mutation_conduit import MutationConduit
from melder.mutation_research.mutation_frame import MutationFrame
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_runtime_singletons() -> None:
    """
    Reset the runtime singletons around each mutation-research component test.

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
    Create one dynamic configuration for component tests.

    Args:
        frame_name:
            Target Aether frame name.

    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_component_conduit_returns_aether_owned_mutation_research(case_index: int) -> None:
    """
    Validate dynamic conduits expose the same Aether-owned MutationResearch root.
    """
    frame_name = f"component-frame-{case_index:02d}"
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
        manager = conduit.get_mutation_research()
        assert manager is conduit._aether.mutation_research
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_component_root_create_mutation_conduit_returns_placeholder(case_index: int) -> None:
    """
    Validate the Aether-owned root can build MutationConduit placeholders from live conduits.
    """
    frame_name = f"component-conduit-frame-{case_index:02d}"
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
        placeholder = conduit._aether.mutation_research.create_mutation_conduit(conduit)
        assert isinstance(placeholder, MutationConduit)
        assert placeholder.conduit is conduit
        assert placeholder.mutation_research is conduit._aether.mutation_research
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_component_root_create_mutation_frame_returns_placeholder(case_index: int) -> None:
    """
    Validate the Aether-owned root can build MutationFrame placeholders from live frames.
    """
    frame_name = f"component-frame-surface-{case_index:02d}"
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
        assert placeholder.aetheric_frame_name == frame_name
        assert placeholder.mutation_research is conduit._aether.mutation_research
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index,unrestricted",
    [(i, i % 2 != 0) for i in range(1, 11)],
)
def test_component_root_configuration_activation_matrix(
    case_index: int,
    unrestricted: bool,
) -> None:
    """
    Validate the Aether-owned root accepts activated configuration across both postures.
    """
    aether = Aether()
    root = aether.mutation_research
    configuration = root.create_configuration()
    configuration.with_unrestricted_module_mutations(unrestricted)
    configuration.activate()

    root.configure(configuration)
    root.activate()

    assert root.is_configured is True
    assert root.is_activated is True
    assert root.configuration is configuration
    assert root.configuration.get_property("unrestricted_module_mutations") is unrestricted
    root.deactivate()
    assert root.is_activated is False
