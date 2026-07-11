import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
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
def test_integration_bound_spell_sha_registers_into_default_set(case_index: int) -> None:
    """
    Validate a live bind's SHA256 spell id registers as formal research in
    the root's default set (the spell id IS the custody-crystal id).
    """
    frame_name = f"integration-register-frame-{case_index:02d}"
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
        root = conduit._aether.mutation_research
        research_set = root.research_set()
        node = research_set.register_spell(
            spell_id,
            author=f"integration-{case_index:02d}",
            reason="declared research from a live bind",
        )
        assert node.spell_sha == spell_id
        assert research_set.residence_of(spell_id) == (
            research_set.default_lane.lane_id
        )
        history = research_set.history(spell_id)
        assert history["lane_name"] == "default"
        with pytest.raises(RuntimeError, match="Rediscovery"):
            research_set.register_spell(spell_id)
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    "case_index",
    list(range(1, 11)),
)
def test_integration_research_lines_survive_composition_roundtrip(case_index: int) -> None:
    """
    Validate the persistence composition payload round-trips a live-bound
    research line through the hydration seam.
    """
    frame_name = f"integration-composition-frame-{case_index:02d}"
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
        root = conduit._aether.mutation_research
        research_set = root.research_set()
        research_set.register_spell(spell_id)
        research_set.create_lane(
            f"exp-{case_index:02d}",
            attach_to="default",
            attach_at_sha=spell_id,
        )
        recorded = root.describe_research_composition()

        root.load_recorded_composition(recorded)

        rebuilt = root.research_set()
        assert rebuilt.residence_of(spell_id) == (
            rebuilt.default_lane.lane_id
        )
        assert f"exp-{case_index:02d}" in rebuilt.lane_names()
        assert rebuilt.get_lane(f"exp-{case_index:02d}").anchor_sha == spell_id
    finally:
        conduit.cleanup()
