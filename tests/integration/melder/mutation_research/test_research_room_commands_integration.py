import pytest

from melder.nexus.rift.command_system.capability_command_system import (
    CapabilityCommandSystem,
)
from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)


@pytest.fixture(autouse=True)
def _isolated_runtime() -> None:
    reset_runtime_singletons()
    yield
    reset_runtime_singletons()


def _build_codegen_space():
    """
    Build one real codegen room over an enabled Nexus.

    Returns:
        tuple: (conduit, space) - the rooted conduit and the codegen room.
    """
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    rift.create_frame_link("ops")
    return conduit, rift.space


def _activate_research(conduit) -> object:
    """
    Activate the Aether-hosted MR root for the built world.

    Args:
        conduit: Rooted conduit carrying the hidden aether reference.

    Returns:
        object: The activated MutationResearch root.
    """
    root = conduit._aether.mutation_research
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)
    root.activate(hydrate_from_record=False)
    return root


def test_research_commands_refuse_before_activation() -> None:
    """
    Validate the teach-grade refusal: a user ASKING for research in a room
    gets a named error while the MR root is inactive, never a None.
    """
    _, space = _build_codegen_space()
    with pytest.raises(RuntimeError, match="not active"):
        space.command_system.research_heads()


def test_codegen_room_full_research_loop() -> None:
    """
    Validate the full room surface: campaign context, declaration truth,
    reads (walk/heads/history/residency/campaign), organization
    (create_lane/attach/join/archive), and campaign clear - all through the
    mediated command layer of a real codegen room.
    """
    conduit, space = _build_codegen_space()
    root = _activate_research(conduit)
    commands = space.command_system

    commands.research_set_campaign("apollo")
    assert root.active_campaign == "apollo"
    root.record_world_entry("sha-room-a")
    root.record_world_entry("sha-room-b")

    walk = commands.research_walk()
    assert [step["spell_id"] for step in walk] == [
        "sha-room-a", "sha-room-b",
    ]
    assert commands.research_heads()["default"] == "sha-room-b"

    lane_payload = commands.research_create_lane(
        "exp-room",
        attach_to="default",
        attach_at_spell_id="sha-room-b",
    )
    assert lane_payload["name"] == "exp-room"
    assert lane_payload["anchor_spell_id"] == "sha-room-b"

    history = commands.research_history("sha-room-a")
    assert history["lane_name"] == "default"

    residency = commands.research_residency("sha-room-a")
    assert residency["declared"] is True

    campaign = commands.research_campaign_view("apollo")
    assert {n["spell_id"] for n in campaign["nodes"]} == {
        "sha-room-a", "sha-room-b",
    }

    receiver = commands.research_join("exp-room", into="default")
    assert receiver["name"] == "default"

    commands.research_create_lane("dead-end-room")
    commands.research_archive("dead-end-room", reason="abandoned")
    assert "dead-end-room" not in commands.research_heads()

    commands.research_clear_campaign()
    assert root.active_campaign is None


def test_capability_room_surface_is_read_only() -> None:
    """
    Validate the room split: capability rooms carry exactly the six research
    reads and NONE of the organization or campaign mutation commands.
    """
    reads = (
        "research_walk",
        "research_history",
        "research_heads",
        "research_residency",
        "research_diff",
        "research_campaign_view",
    )
    mutations = (
        "research_create_lane",
        "research_attach",
        "research_detach",
        "research_join",
        "research_archive",
        "research_set_campaign",
        "research_clear_campaign",
    )
    for name in reads:
        assert hasattr(CapabilityCommandSystem, name), name
    for name in mutations:
        assert not hasattr(CapabilityCommandSystem, name), name
