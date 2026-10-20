"""
Characterization test: a research lane is not a runtime fork (core-protection review, 2026-10-10).

Purpose:
    The review asks whether a deliberate core "fork" or "research branch" could be Melder's native
    research lane. This pins what a lane does today in a live, bound world: anchoring a lane onto a
    running spell's node records ancestry only, a version registered into that lane is research
    material only, and neither changes which version is selected, where the running version
    resides, or what a meld returns. Lanes have zero runtime footprint; selection is moved only by
    the Spellbook and Conduit verbs. It describes today's behaviour; it does not decide the review's
    fork mapping.

Runs only on 3.14t (melder package root import chain).
"""
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def fresh_runtime() -> Iterator[None]:
    """
    Reset the runtime singletons around the test and rebind the static Aether references.

    Yields:
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


def _dynamic_spellbook(frame_name: str) -> Spellbook:
    """
    Build one dynamic-posture Spellbook on its own frame.

    Args:
        frame_name: Aether frame the book binds into.

    Returns:
        Spellbook: The configured book.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame_name, configuration=configuration)


def test_an_anchored_lane_and_its_versions_leave_the_running_world_unchanged() -> None:
    """
    Contract: with MutationResearch active, a bind declares the spell into the default lane. A lane
    anchored at that spell starts empty and names its anchor; registering a candidate version into
    it adds research material only. Throughout, the bound spell stays in the default lane, reads
    `active` at runtime, and its unique instance is the one a meld returns; the candidate is never
    active.
    """
    root = Aether().mutation_research
    root.configure(root.create_configuration().with_defaults().activate())
    root.activate(hydrate_from_record=False)
    spellbook = _dynamic_spellbook("lane-isolation")
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(dynamic=True, name="lane-isolation-root")
    try:
        running = conduit.meld(spell_id=spell_id)
        research_set = root.research_set()
        default_lane_id = research_set.default_lane.lane_id
        assert research_set.residence_of(spell_id) == default_lane_id
        assert root.residency_view(spell_id)["runtime"] == "active"

        lane = research_set.create_lane(
            "fork-candidate",
            attach_to="default",
            attach_at_spell_id=spell_id,
        )
        assert lane.node_count == 0
        assert lane.anchor_lane_id == default_lane_id
        assert lane.anchor_spell_id == spell_id

        research_set.register_spell(
            "sha-fork-candidate",
            lane="fork-candidate",
            parent_spell_ids=[spell_id],
        )
        assert lane.node_count == 1
        assert root.residency_view("sha-fork-candidate")["runtime"] != "active"

        assert research_set.residence_of(spell_id) == default_lane_id
        assert research_set.default_lane.has_node(spell_id)
        residency = root.residency_view(spell_id)
        assert residency["runtime"] == "active"
        assert residency["lane_name"] == "default"
        assert conduit.meld(spell_id=spell_id) is running
    finally:
        conduit.cleanup()
        root.deactivate()
