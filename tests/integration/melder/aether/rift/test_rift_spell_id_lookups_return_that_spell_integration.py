"""
Integration tests - a capability room's lookups by spell_id answer that spell or refuse (0.2.8253).

A Rift room's command projection reads the frame's published records, and Nexus publishes the version each index has
active: a notch swaps the record at once. So the room answers the active version by its spell_id
(`get_spell_by_spell_id`), by its source id (`get_spell_by_source_id`, `spellbook_id:spell_id`) and by its index
(`get_spell_by_index_id`), and refuses a parked version's spell_id and source id - it never answers them with the
version the index has active. Until 0.2.8253 the spell_id lookup was named `get_spell_by_id`, and the room's
spell_id and source-id lookups went through paths that turn a spell_id into its index.

Each test builds a dynamic `default` frame open to Rift rooms: one Book binds PricingV1 active, conjures and stages
PricingV2 on its index with `bind_inactive`; an enabled Nexus creates a capability Rift linked to the frame.
"""

from collections.abc import Iterator
from typing import Dict

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.rift_space.capability_rift_space import CapabilityRiftSpace
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


class PricingV1:
    """Version 1 of the pricing spell: bound active."""

    def __init__(self) -> None:
        """Set the version's rate."""
        self.rate = 100


class PricingV2:
    """Version 2 of the pricing spell: staged parked, notched in by the tests that need it."""

    def __init__(self) -> None:
        """Set the version's rate."""
        self.rate = 250


def _reset_runtime_singletons() -> None:
    """Reset the singletons the room touches and rebind the class-level Aether handles."""
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    CommandSystem._aether = aether


@pytest.fixture(autouse=True)
def _isolated_runtime() -> Iterator[None]:
    """Give every test fresh runtime singletons, and reset them after."""
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _build_world() -> Dict[str, object]:
    """Build the frame, its Book with PricingV1 active and PricingV2 parked, and a capability room linked to it."""
    configuration = SpellbookConfiguration(aether_frame="default")
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=True, rift_enabled=True)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(aetheric_frame="default", configuration=configuration)
    v1_id = spellbook.bind(spell=PricingV1, existence=Existence.unique, permissions="create")
    root = spellbook.conjure(name="pricing_root", dynamic=True)
    index = spellbook._spells_by_id[v1_id].spell_index
    v2_id = root.bind_inactive(spell=PricingV2, spell_index=index, existence=Existence.unique, permissions="create")
    nexus = Nexus()
    nexus_configuration = nexus.create_configuration()
    nexus_configuration.with_rift_creation_enabled(True)
    nexus_configuration.with_direct_rift_access(True)
    nexus_configuration.with_target_frame_override(True)
    nexus_configuration.with_multiple_target_frames(True)
    nexus_configuration.with_max_target_frame_count(8)
    nexus_configuration.with_allowed_target_frame_names(("default",))
    nexus_configuration.with_nexus_frame_mode("indexed")
    nexus_configuration.with_max_nexus_frame_count(8)
    nexus.activate(nexus_configuration)
    rift = nexus.create_rift(
        configuration=nexus.create_rift_configuration().with_space_type(RiftSpaceType.capability),
        rift_name="pricing_rift",
    )
    rift.create_frame_link("default")
    space = rift.space
    assert isinstance(space, CapabilityRiftSpace)
    return {
        "command": space.command_system,
        "spellbook": spellbook,
        "root": root,
        "index": index,
        "v1_id": v1_id,
        "v2_id": v2_id,
    }


def _source_id(world: Dict[str, object], spell_id: object) -> str:
    """Return the source id `<spellbook id>:<spell_id>` the room addresses a published spell by."""
    return "{0}:{1}".format(world["spellbook"].id, spell_id)


def test_the_room_answers_the_active_version_by_spell_id_source_id_and_index() -> None:
    """Before the notch PricingV1 is active: its spell_id, its source id and its index all answer PricingV1."""
    world = _build_world()
    command = world["command"]
    by_spell_id = command.get_spell_by_spell_id(world["v1_id"], frame_name="default")
    by_source_id = command.get_spell_by_source_id(_source_id(world, world["v1_id"]), frame_name="default")
    by_index = command.get_spell_by_index_id(world["index"].id, frame_name="default")
    assert by_spell_id.spell is PricingV1 and by_spell_id.spell_id == world["v1_id"]
    assert by_source_id is by_spell_id
    assert by_index is by_spell_id


def test_after_a_notch_the_room_answers_the_version_now_active() -> None:
    """The notch swaps the published record: PricingV2's spell_id and source id answer PricingV2, as does the index."""
    world = _build_world()
    command = world["command"]
    world["root"].notch_spell(spell_index=world["index"], spell_id=world["v2_id"])
    by_spell_id = command.get_spell_by_spell_id(world["v2_id"], frame_name="default")
    by_source_id = command.get_spell_by_source_id(_source_id(world, world["v2_id"]), frame_name="default")
    by_index = command.get_spell_by_index_id(world["index"].id, frame_name="default")
    assert by_spell_id.spell is PricingV2 and by_spell_id.spell_id == world["v2_id"]
    assert by_source_id is by_spell_id
    assert by_index is by_spell_id
    assert world["root"].meld(spell_id=world["v2_id"]).rate == 250


@pytest.mark.parametrize("notched", (False, True))
def test_a_parked_version_is_refused_never_answered_with_the_active_one(notched: bool) -> None:
    """
    The parked version - PricingV2 before the notch, PricingV1 after it - is not published, so the room refuses its
    spell_id and its source id instead of answering the version its index has active.
    """
    world = _build_world()
    command = world["command"]
    parked_id = world["v1_id"] if notched else world["v2_id"]
    if notched:
        world["root"].notch_spell(spell_index=world["index"], spell_id=world["v2_id"])
    with pytest.raises(ValueError, match="was not found in frame 'default'"):
        command.get_spell_by_spell_id(parked_id, frame_name="default")
    with pytest.raises(ValueError, match="was not found in frame 'default'"):
        command.get_spell_by_source_id(_source_id(world, parked_id), frame_name="default")
