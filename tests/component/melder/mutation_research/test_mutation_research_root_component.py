import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.mutation_research.research_set.research_lane import LaneState
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
    spellbook._aetheric_frame_configuration.with_disable_mutations(False)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name=f"root-{case_index:02d}")
    try:
        manager = conduit.get_mutation_research()
        assert manager is conduit._aether.mutation_research
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_component_root_default_set_ready_on_real_aether(case_index: int) -> None:
    """
    Validate the Aether-owned root births the guaranteed default set with
    its guaranteed default lane.
    """
    aether = Aether()
    root = aether.mutation_research

    assert root.list_research_set_names() == ["default"]
    research_set = root.research_set()
    assert research_set.lane_names() == ["default"]
    assert research_set.default_lane.state is LaneState.open


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_component_research_flow_on_real_aether(case_index: int) -> None:
    """
    Validate a register -> branch -> join research flow against the real
    Aether-owned root.
    """
    aether = Aether()
    research_set = aether.mutation_research.research_set()
    base_sha = f"component-sha-{case_index:02d}-base"
    next_sha = f"component-sha-{case_index:02d}-next"
    lane_name = f"component-lane-{case_index:02d}"

    research_set.register_spell(base_sha)
    research_set.create_lane(
        lane_name, attach_to="default", attach_at_spell_id=base_sha,
    )
    research_set.register_spell(
        next_sha, lane=lane_name, parent_spell_ids=[base_sha],
    )
    research_set.join(lane_name, into="default")

    assert research_set.default_lane.tip_spell_id == next_sha
    assert research_set.get_lane(lane_name).state is LaneState.joined
    assert research_set.heads() == {"default": next_sha}


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
