from unittest.mock import MagicMock

import pytest

from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.mutation_research import MutationResearch
from melder.mutation_research.research_set.research_set import ResearchSet


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each root/config test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


def _mock_aether(*, recording: bool = False) -> MagicMock:
    """
    Build one MagicMock Aether host for root unit tests.

    Args:
        recording:
            When True, the mocked crystallizer poses as live-and-recording so
            the emission seam proceeds; otherwise emission short-circuits on
            the cleaned guard.

    Returns:
        MagicMock: Aether double carrying a crystallizer double.
    """
    aether = MagicMock()
    if recording:
        aether._crystallizer.cleaned = False
        aether._crystallizer.activated = True
    return aether


def test_mutation_research_configuration_defaults_validate() -> None:
    """
    Verify the default mutation-research configuration disables unrestricted mode.
    """
    configuration = MutationResearchConfiguration().with_defaults()

    assert configuration.get_property("unrestricted_module_mutations") is False
    assert configuration.validate() is True


def test_mutation_research_configuration_payload_is_value_typed() -> None:
    """
    Verify the shared twin-payload builder coerces non-plain values.
    """
    configuration = MutationResearchConfiguration().with_defaults()
    payload = configuration.describe_configuration_payload()

    assert payload["unrestricted_module_mutations"] is False
    for value in payload.values():
        assert value is None or isinstance(value, (str, int, float, bool))


def test_mutation_research_configuration_builder_activate_hands_off_configuration() -> None:
    """
    Verify the builder activates and hands off a configured object.
    """
    builder = MutationResearchConfigurationBuilder()
    configuration = builder.with_defaults().activate()

    assert configuration.activated is True
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        builder.build()


def test_mutation_research_root_configure_and_activate() -> None:
    """
    Verify the Aether-owned root follows the config/activate pattern.
    """
    root = MutationResearch(aether=_mock_aether())
    configuration = root.create_configuration().with_defaults().activate()

    root.configure(configuration)
    root.activate()

    assert root.is_configured is True
    assert root.is_activated is True
    assert root.configuration is configuration


def test_root_guarantees_default_research_set() -> None:
    """
    Verify the sets registry births with the guaranteed default set.
    """
    root = MutationResearch(aether=_mock_aether())

    assert root.list_research_set_names() == ["default"]
    default_set = root.research_set()
    assert isinstance(default_set, ResearchSet)
    assert default_set.lane_names() == ["default"]


def test_root_create_research_set_registers_unique_names() -> None:
    """
    Verify additional sets register by unique name and resolve back.
    """
    root = MutationResearch(aether=_mock_aether())
    created = root.create_research_set("side-campaign")

    assert root.research_set("side-campaign") is created
    assert root.list_research_set_names() == ["default", "side-campaign"]
    with pytest.raises(ValueError, match="already owns"):
        root.create_research_set("side-campaign")
    with pytest.raises(KeyError, match="Known sets"):
        root.research_set("missing")


def test_root_emits_composition_twin_when_recording() -> None:
    """
    Verify a set mutation re-emits the MutationResearchCrystal composition
    through the crystallizer sink while the root is active and recording.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)
    root.activate()
    aether._crystallizer.emit.reset_mock()

    root.research_set().register_spell("sha-a", author="mutation_0")

    assert aether._crystallizer.emit.call_count == 1
    twin = aether._crystallizer.emit.call_args.args[0]
    assert isinstance(twin, MutationResearchCrystal)
    composition = twin.composition_payload
    organization = composition["default"]["organization"]
    assert organization["residence"]["lane_id_by_sha"].keys() == {"sha-a"}


def test_root_emission_skips_while_inactive() -> None:
    """
    Verify set mutations emit nothing before root activation.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    aether._crystallizer.emit.reset_mock()

    root.research_set().register_spell("sha-a")

    assert aether._crystallizer.emit.call_count == 0


def test_root_load_recorded_composition_rebuilds_registry() -> None:
    """
    Verify the hydration seam replaces the registry from a recorded payload
    and keeps the default-set guarantee.
    """
    root = MutationResearch(aether=_mock_aether())
    root.research_set().register_spell("sha-a")
    root.create_research_set("side")
    recorded = root.describe_research_composition()

    root.load_recorded_composition({"side": recorded["side"]})

    assert root.list_research_set_names() == ["default", "side"]
    assert root.research_set().residence_of("sha-a") is None
    with pytest.raises(ValueError, match="dict"):
        root.load_recorded_composition("not-a-dict")


def test_root_record_world_entry_is_idempotent() -> None:
    """
    Verify the seam facade declares once and no-ops on rediscovery.
    """
    root = MutationResearch(aether=_mock_aether())

    assert root.record_world_entry("sha-a") is True
    assert root.record_world_entry("sha-a") is False
    assert root.record_world_entry("sha-b", staged=True) is True
    acts = [
        entry.act.value
        for entry in root.research_set().journal.entries()
    ]
    assert acts.count("registered") == 1
    assert acts.count("staged") == 1


def test_root_record_promotion_catches_up_unknown_targets() -> None:
    """
    Verify promotion of an undeclared identity declares it first (staged
    catch-up), then journals the promoted event.
    """
    root = MutationResearch(aether=_mock_aether())
    root.record_world_entry("sha-old")

    root.record_promotion("sha-old", "sha-new", actor="mutation_0")

    research_set = root.research_set()
    assert research_set.residence_of("sha-new") is not None
    acts = [entry.act.value for entry in research_set.journal.entries()]
    assert acts[-2:] == ["staged", "promoted"]
    last = research_set.journal.entries()[-1]
    assert last.from_sha == "sha-old" and last.to_sha == "sha-new"


def test_root_activation_hydrates_virgin_registry_from_record() -> None:
    """
    Verify the twin docking loop: a virgin root rebuilds its registry from
    the active profile's recorded composition at activation.
    """
    donor = ResearchSet("default")
    donor.register_spell("sha-recorded", author="past-life")
    recorded_composition = {"default": donor.describe_composition()}
    donor.cleanup()

    aether = _mock_aether(recording=True)
    aether._crystallizer.describe_mutation_research_record.return_value = {
        "twin_kind": "mutation_research",
        "activated": True,
        "configuration_payload": {},
        "composition_payload": recorded_composition,
    }
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)

    root.activate()

    hydrated = root.research_set()
    assert hydrated.residence_of("sha-recorded") == (
        hydrated.default_lane.lane_id
    )


def test_root_activation_never_clobbers_live_research() -> None:
    """
    Verify a non-virgin registry skips hydration: live research wins and
    re-records itself instead.
    """
    donor = ResearchSet("default")
    donor.register_spell("sha-recorded")
    recorded_composition = {"default": donor.describe_composition()}
    donor.cleanup()

    aether = _mock_aether(recording=True)
    aether._crystallizer.describe_mutation_research_record.return_value = {
        "composition_payload": recorded_composition,
    }
    root = MutationResearch(aether=aether)
    root.research_set().register_spell("sha-live")
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)

    root.activate()

    live = root.research_set()
    assert live.residence_of("sha-live") is not None
    assert live.residence_of("sha-recorded") is None


def test_root_activation_hydration_opt_out() -> None:
    """
    Verify hydrate_from_record=False leaves even a virgin registry alone.
    """
    aether = _mock_aether(recording=True)
    aether._crystallizer.describe_mutation_research_record.return_value = {
        "composition_payload": {"default": {}},
    }
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)

    root.activate(hydrate_from_record=False)

    aether._crystallizer.describe_mutation_research_record.assert_not_called()


def test_root_diff_research_resolves_material_from_custody() -> None:
    """
    Verify diff_research pulls custody material through the crystallizer
    (crystal id == spell SHA) and dispatches the source strategy.
    """
    aether = _mock_aether(recording=True)
    aether._crystallizer.get_spell_crystal.return_value.describe.side_effect = [
        {
            "synthetic_module_sources": {"mod.a": {"source_text": "x = 1\n"}},
            "physical_module_fingerprints": {},
        },
        {
            "synthetic_module_sources": {"mod.a": {"source_text": "x = 2\n"}},
            "physical_module_fingerprints": {},
        },
    ]
    root = MutationResearch(aether=aether)

    verdict = root.diff_research("sha-left", "sha-right")

    assert verdict["strategy"] == "source"
    assert verdict["result"]["changed_modules"] == ["mod.a"]
    assert verdict["result"]["identical"] is False


def test_root_diff_research_refuses_dead_custody() -> None:
    """
    Verify diff material resolution stays loud when the crystallizer is not
    live (no fabricated empty material).
    """
    aether = _mock_aether()
    aether._crystallizer.cleaned = True
    root = MutationResearch(aether=aether)

    with pytest.raises(RuntimeError, match="custody is unavailable"):
        root.diff_research("sha-left", "sha-right")


def test_root_cleanup_cascades_into_sets() -> None:
    """
    Verify root cleanup cascades into every owned research set.
    """
    root = MutationResearch(aether=_mock_aether())
    default_set = root.research_set()
    root.cleanup()

    assert root.cleaned is True
    assert default_set.cleaned is True
    with pytest.raises(RuntimeError):
        root.research_set()
