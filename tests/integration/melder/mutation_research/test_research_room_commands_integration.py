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
    Validate the room split: capability rooms carry exactly the ten research
    reads and NONE of the organization, campaign-mutation, or code-taking
    commands (the candidate preview takes code and stays codegen-only).
    """
    reads = (
        "research_walk",
        "research_history",
        "research_heads",
        "research_residency",
        "research_diff",
        "research_campaign_view",
        "research_source",
        "research_impact",
        "research_module_graph",
        "research_source_drift",
    )
    mutations = (
        "research_create_lane",
        "research_attach",
        "research_detach",
        "research_join",
        "research_archive",
        "research_set_campaign",
        "research_clear_campaign",
        "research_preview",
    )
    for name in reads:
        assert hasattr(CapabilityCommandSystem, name), name
    for name in mutations:
        assert not hasattr(CapabilityCommandSystem, name), name


class _FakeCrystal:
    """
    Minimal custody-crystal double answering describe() verbatim.
    """

    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def describe(self) -> dict:
        return self._payload


class _FakeCrystallizer:
    """
    Minimal live-custody double for the foresight room loop: one recorded
    two-module world plus a fixed blast radius.
    """

    cleaned = False
    activated = True

    def __init__(self) -> None:
        self.payload = {
            "root_module_name": "pkg.root",
            "module_targets": ["pkg.root", "pkg.helper"],
            "synthetic_module_sources": {
                "pkg.root": {"source_text": "def cast():\n    return 1\n"},
            },
            "user_module_sources": {},
            "module_to_path": {},
            "physical_module_fingerprints": {"pkg.root": "sealed-print"},
            "module_to_direct_dependencies": {
                "pkg.root": ["pkg.helper"],
                "pkg.helper": [],
            },
            "export_surfaces": {"pkg.root": ["cast"]},
            "module_load_order": ["pkg.helper", "pkg.root"],
        }

    def get_spell_crystal(self, spell_id: str) -> _FakeCrystal:
        return _FakeCrystal(self.payload)

    def analyze_impact(self, module_name=None, spell_id=None) -> dict:
        return {
            "root_module": "pkg.root",
            "affected_spells": ["sha-room-a"],
            "affected_modules": ["pkg.root"],
        }

    def emit(self, crystal) -> None:
        return None

    def emit_mutation_research_state(self, state) -> None:
        return None


def test_codegen_room_foresight_loop() -> None:
    """
    Validate the foresight surface end to end through a real codegen room:
    refusal while MR is inactive, then source return, residency-joined
    impact, module graph walk, drift report, and the candidate preview -
    all mediated, all read-only.

    Note:
        The fake crystallizer is swapped in ONLY for the command window and
        the real one is restored before teardown, so the singleton-reset
        lane (MR cleanup emits its recorded-unit state into live custody)
        always talks to the real record.
    """
    conduit, space = _build_codegen_space()
    commands = space.command_system

    with pytest.raises(RuntimeError, match="not active"):
        commands.research_source("sha-room-a")

    root = _activate_research(conduit)
    real_crystallizer = root._crystallizer
    root._crystallizer = _FakeCrystallizer()
    try:
        root.record_world_entry("sha-room-a")

        source = commands.research_source(
            "sha-room-a", module_name="pkg.root",
        )
        assert source["modules"]["pkg.root"]["origin"] == "recorded"

        impact = commands.research_impact(spell_id="sha-room-a")
        assert impact["research"]["sha-room-a"]["declared"] is True
        assert impact["research"]["sha-room-a"]["lane_name"] == "default"

        graph = commands.research_module_graph("sha-room-a")
        assert graph["local_importers"]["pkg.helper"] == ["pkg.root"]

        drift = commands.research_source_drift()
        assert drift["affected_modules"] == ["pkg.root"]

        preview = commands.research_preview(
            "def cast():\n    return 2\n",
            against_spell_id="sha-room-a",
        )
        assert preview["module_name"] == "pkg.root"
        assert (
            "pkg.root"
            in preview["diff"]["source"]["result"]["changed_modules"]
        )
        assert preview["impact"]["research"]["sha-room-a"]["declared"] is True
        assert preview["validation"] is None
    finally:
        root._crystallizer = real_crystallizer
