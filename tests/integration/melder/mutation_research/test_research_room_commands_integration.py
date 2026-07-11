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
        "research_module",
        "research_part",
        "research_parts",
        "research_part_diff",
        "research_group_view",
        "research_group_diff",
        "research_group_impact",
        "research_group_footprint",
        "research_group_drift",
        "research_group_history",
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
        "research_synthesize",
        "research_stage_ancestry",
        "research_clear_staged_ancestry",
        "research_group_register",
        "research_group_recompose",
    )
    for name in reads:
        assert hasattr(CapabilityCommandSystem, name), name
    for name in mutations:
        assert not hasattr(CapabilityCommandSystem, name), name
    # Discoverability law: both rooms ADVERTISE their research surface.
    for name in reads:
        assert name in CapabilityCommandSystem._CAPABILITY_COMMAND_METHOD_NAMES


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
    Minimal live-custody double for the foresight/synthesis room loops:
    recorded two-module worlds (per-identity source overrides) plus a
    fixed blast radius.
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
        self.source_overrides = {}

    def get_spell_crystal(self, spell_id: str) -> _FakeCrystal:
        override = self.source_overrides.get(spell_id)
        if override is None:
            return _FakeCrystal(self.payload)
        payload = dict(self.payload)
        payload["synthetic_module_sources"] = {
            "pkg.root": {"source_text": override},
        }
        return _FakeCrystal(payload)

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
        assert impact["research"]["sha-room-a"]["lane_type"] == "development"

        graph = commands.research_module_graph("sha-room-a")
        assert graph["local_importers"]["pkg.helper"] == ["pkg.root"]

        dossier = commands.research_module("sha-room-a", "pkg.root")
        assert dossier["source_kind"] == "synthetic"
        assert dossier["local_importers"] == []
        assert dossier["fingerprint"] == "sealed-print"

        part = commands.research_part("sha-room-a", "cast")
        assert part["found"] is True
        assert part["kind"] == "function"
        assert part["module_name"] == "pkg.root"

        inventory = commands.research_parts("sha-room-a")
        root_parts = inventory["modules"]["pkg.root"]["parts"]
        assert [row["name"] for row in root_parts] == ["cast"]
        assert "def cast():" in root_parts[0]["text"]

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

        # Composed lane (the test-debt slice): frame_name routes the
        # candidate through the room's REAL codegen validation pass.
        validated = commands.research_preview(
            "result = 1\n",
            module_name="pkg.root",
            frame_name="ops",
        )
        assert validated["validation"] == {
            "accepted": True,
            "reason": "codegen_validation_accepted",
            "frame_name": "ops",
        }
        assert validated["impact"]["affected_modules"] == ["pkg.root"]
    finally:
        root._crystallizer = real_crystallizer


def test_codegen_room_synthesis_loop() -> None:
    """
    Validate the surgical-synthesis surface through a real codegen room:
    lane typed at creation, donor parts composed into the base with a full
    preview, ancestry staged by the command, and the next world entry
    minting the multi-parent node - all mediated, nothing executed.
    """
    conduit, space = _build_codegen_space()
    commands = space.command_system
    root = _activate_research(conduit)
    real_crystallizer = root._crystallizer
    fake = _FakeCrystallizer()
    fake.source_overrides["sha-donor"] = (
        "def cast():\n"
        "    return 99\n"
        "\n"
        "def fresh():\n"
        "    return 'donor'\n"
    )
    root._crystallizer = fake
    try:
        lane_payload = commands.research_create_lane(
            "surgical", lane_type="experiment",
        )
        assert lane_payload["lane_type"] == "experiment"

        root.record_world_entry("sha-base")
        root.record_world_entry("sha-donor")

        verdict = commands.research_synthesize(
            "sha-base",
            "sha-donor",
            take_functions=["cast", "fresh"],
            stage_ancestry=True,
        )
        assert verdict["parents"] == ["sha-base", "sha-donor"]
        assert "return 99" in verdict["composed_source"]
        assert verdict["preview"]["module_name"] == "pkg.root"
        assert verdict["ancestry_staged"] is True

        # The composed candidate "binds": the auto-record seam mints the
        # multi-parent node from the staged ancestry, one-shot.
        assert root.record_world_entry("sha-composed") is True
        residency = commands.research_residency("sha-composed")
        assert residency["declared"] is True
        history = commands.research_history("sha-composed")
        assert history["node"]["parent_spell_ids"] == [
            "sha-base", "sha-donor",
        ]
        assert root.staged_ancestry is None

        # Restage/clear loop through the room commands.
        commands.research_stage_ancestry(["sha-base"])
        assert root.staged_ancestry == ["sha-base"]
        commands.research_clear_staged_ancestry()
        assert root.staged_ancestry is None

        # Part-grain comparison (owner ruling: class diffs + their radius):
        # base cast() vs donor cast() through recorded material only.
        part_verdict = commands.research_part_diff(
            "sha-base", "sha-donor", "cast",
        )
        assert part_verdict["left_found"] is True
        assert part_verdict["right_found"] is True
        assert part_verdict["identical"] is False
        assert any(
            "return 99" in line for line in part_verdict["unified_diff"]
        )
        assert part_verdict["impact"]["affected_modules"] == ["pkg.root"]

        # Grain choice on the whole-version diff (owner ruling): the agent
        # picks class grain via strategy="parts" and sees every part's code.
        parts_verdict = commands.research_diff(
            "sha-base", "sha-donor", strategy="parts",
        )
        donor_report = parts_verdict["result"]["module_reports"]["pkg.root"]
        assert {row["name"] for row in donor_report["added_parts"]} == {
            "fresh",
        }
        changed_names = {
            row["name"] for row in donor_report["changed_parts"]
        }
        assert "cast" in changed_names
    finally:
        root._crystallizer = real_crystallizer


def test_codegen_room_composition_loop() -> None:
    """
    Validate the GroupedResearchNode surface through a real codegen room:
    register a composition over declared versions, iterate it forward,
    read the roster with drift truth, diff the two compositions at member
    grain, and take the union radius with closure - all mediated, the
    composition purely informational.
    """
    conduit, space = _build_codegen_space()
    commands = space.command_system
    root = _activate_research(conduit)
    real_crystallizer = root._crystallizer
    root._crystallizer = _FakeCrystallizer()
    try:
        root.record_world_entry("sha-room-a")
        root.record_world_entry("sha-room-b")
        commands.research_create_lane("subsystem", lane_type="production")

        first = commands.research_group_register(
            ["sha-room-a"], lane="subsystem",
        )
        assert first["node_type"] == "group"

        second = commands.research_group_recompose(
            first["group_id"], add=["sha-room-b"],
        )
        assert second["member_spell_ids"] == ["sha-room-a", "sha-room-b"]
        assert second["parent_group_ids"] == [first["group_id"]]

        view = commands.research_group_view(second["group_id"])
        assert view["member_count"] == 2
        # Both members share the default lane whose tip is sha-room-b, so
        # the pinned sha-room-a honestly reports behind.
        assert view["behind_count"] == 1
        assert view["members"]["sha-room-a"]["behind"] is True
        assert view["members"]["sha-room-b"]["behind"] is False

        verdict = commands.research_group_diff(
            first["group_id"], second["group_id"],
        )
        assert verdict["result"]["added_members"] == ["sha-room-b"]
        assert verdict["result"]["ancestry_related"] is True

        impact = commands.research_group_impact(second["group_id"])
        assert impact["member_count"] == 2
        assert "pkg.root" in impact["affected_modules"]
        assert impact["closure"] is not None

        residency = commands.research_residency(second["group_id"])
        assert residency["node_type"] == "group"
        assert residency["runtime"] == "informational"

        footprint = commands.research_group_footprint(second["group_id"])
        assert footprint["modules"] == ["pkg.helper", "pkg.root"]
        assert footprint["shared_modules"] == ["pkg.helper", "pkg.root"]

        drift = commands.research_group_drift(second["group_id"])
        assert drift["footprint_size"] == 2

        story = commands.research_group_history(second["group_id"])
        acts = [entry["act"] for entry in story["entries"]]
        assert "group_registered" in acts
        assert "group_recomposed" in acts

        member_row = commands.research_residency("sha-room-a")
        assert [
            entry["group_id"]
            for entry in member_row["pinned_by_compositions"]
        ] == [second["group_id"]]
    finally:
        root._crystallizer = real_crystallizer
