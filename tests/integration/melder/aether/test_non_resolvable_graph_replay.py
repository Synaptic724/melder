"""Non-resolvable definitions remain connected, inspectable and non-resolvable after replay."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import nullcontext
from pathlib import Path

import pytest

from melder.aether.aether import Aether
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.persistence.record_version import RecordVersion
from melder.nexus.rift.frame_viewer.view_spell import ViewSpell
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class GraphDefinition(ABC):
    """Abstract application architecture node, registered for inspection and supplied externally."""

    @abstractmethod
    def value(self) -> str:
        """Describe the application contract without providing construction behavior."""
        raise NotImplementedError


class GraphImplementation(GraphDefinition):
    """Concrete child whose real base relationship should remain visible in Nexus."""

    def value(self) -> str:
        """Return a stable value for restored consumer assertions."""
        return "supplied"


class GraphConsumer:
    """Require a supplied definition while keeping an ordinary required constructor argument."""

    def __init__(self, definition: GraphDefinition) -> None:
        """Retain the exact supplied object."""
        self.definition = definition


@pytest.fixture(autouse=True)
def clean_graph_world() -> Iterator[None]:
    """Reset runtime ownership before and after every complete graph scenario."""
    reset_runtime_singletons()
    try:
        yield
    finally:
        reset_runtime_singletons()


def _recording() -> Crystallizer:
    """Activate existing crystal recording with its standard policy."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    root = Crystallizer()
    root.activate(configuration)
    return root


def _book(frame: str) -> Spellbook:
    """Finalize a recorded dynamic book before binding, as the replay contract requires."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    posture = configure_frame_posture_for_spellbook_configuration(
        configuration, dynamic=True, rift_enabled=True, ai_native_enabled=True,
    )
    posture.with_system_caching_enabled(False)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def test_nexus_exposes_definition_reference_and_base_relationships() -> None:
    """Agents can navigate actual registered references and bases without melding the definition."""
    _recording()
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    research = Aether().mutation_research
    research.configure(research.create_configuration().with_defaults().activate())
    research.activate(hydrate_from_record=False)
    rift.create_frame_link("ops")
    definition_id = conduit.bind(spell=GraphDefinition, existence="unique", resolvable=False)
    child_id = conduit.bind(spell=GraphImplementation, existence="unique", resolvable=False)
    consumer_id = conduit.bind(spell=GraphConsumer, existence="many")
    rift.refresh_runtime_projections(frame_names=("ops",))
    book = conduit._spellbook
    source = f"{book.id}:{definition_id}"
    viewer = rift.space.frame_viewer
    description = viewer.describe_spell(source, frame_name="ops")
    assert description["payload"]["binding_payload"]["resolvable"] is False
    relations = viewer.describe_spell_relationships(source, frame_name="ops")
    assert {(row["source_id"], row["kind"]) for row in relations["incoming"]} == {
        (f"{book.id}:{consumer_id}", "override_required"),
        (f"{book.id}:{child_id}", "base"),
    }
    history = rift.space.command_system.research_history(definition_id)
    assert history["lane_name"] == "default"
    source_view = rift.space.command_system.research_source(definition_id)
    assert "class GraphDefinition" in repr(source_view)
    index = book._spells_by_id[child_id].spell_index
    revision_id = conduit.bind_inactive(spell=GraphImplementation, spell_index=index, existence="unique")
    assert revision_id != child_id
    assert rift.space.command_system.research_history(revision_id)["lane_name"] == "default"
    conduit.notch_spell(spell_index=index, spell=book._inactive_spells[revision_id])
    rift.refresh_runtime_projections(frame_names=("ops",))
    revised = viewer.describe_spell_relationships(source, frame_name="ops")
    assert (f"{book.id}:{revision_id}", "base") in {
        (row["source_id"], row["kind"]) for row in revised["incoming"]
    }
    assert f"{book.id}:{child_id}" not in {row["source_id"] for row in revised["incoming"]}
    assert rift.space.command_system.research_history(child_id)["lane_name"] == "default"
    with pytest.raises(MeldExecutionError, match="resolvable=False"):
        conduit.meld(spell_id=definition_id)


def test_checkpoint_replay_preserves_false_and_reemits_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An isolated-world disk round trip must never silently turn a definition into a factory."""
    monkeypatch.setattr(CrystallizerCache, "resolve_cache_root_path", staticmethod(lambda: tmp_path))
    root = _recording()
    book = _book("recorded")
    definition_id = book.bind(spell=GraphDefinition, existence="unique", resolvable=False)
    consumer_id = book.bind(spell=GraphConsumer, existence="many")
    original_conduit = book.conjure(dynamic=True, name="root")
    consumer_index = book._spells_by_id[consumer_id].spell_index
    parked_id = original_conduit.bind_inactive(
        spell=GraphConsumer, spell_index=consumer_index, existence="many", resolvable=False,
    )
    assert root.get_spell_crystal(definition_id).describe()["resolvable"] is False
    checkpoint_id = root.create_checkpoint()
    root.flush_checkpoint(checkpoint_id)
    reset_runtime_singletons()
    rebooted = _recording()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert rebooted.get_spell_crystal(definition_id).describe()["resolvable"] is False
    conduit = Aether().get_conduit_by_name("root", "recorded")
    assert conduit._spellbook._inactive_spells[parked_id].resolvable is False
    supplied = GraphImplementation()
    assert conduit.meld(spell_id=consumer_id, override={"definition": supplied}).definition is supplied
    with pytest.raises(MeldExecutionError, match="resolvable=False"):
        conduit.meld(spell_id=definition_id)


def test_graft_preserves_active_and_parked_capability() -> None:
    """Fresh graft retains each version's own bool rather than applying one index-wide policy."""
    root = _recording()
    source = _book("source")
    false_id = source.bind(spell=GraphImplementation, existence="unique", resolvable=False)
    conduit = source.conjure(dynamic=True, name="source-root")
    index = source._spells_by_id[false_id].spell_index
    true_id = conduit.bind_inactive(spell=GraphImplementation, spell_index=index, existence="unique")
    record = root.capture_index_graft(index.id)
    # Graft from detached custody after releasing live claims; process-wide uniqueness stays enforced.
    conduit.permanent_cleanup()
    host = _book("host")
    host_conduit = host.conjure(dynamic=True, name="host-root")
    report = root.graft_index(record, host)
    assert report["status"] == "complete"
    assert host._spells_by_id[false_id].resolvable is False
    assert host._inactive_spells[true_id].resolvable is True
    with pytest.raises(MeldExecutionError, match="resolvable=False"):
        host_conduit.meld(spell_id=false_id)


def test_old_record_reader_refuses_new_capability_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use the established major gate to prevent older code from ignoring a False capability."""
    payload = RecordVersion.stamp({})
    assert RecordVersion.parse(str(payload["record_version"]))[0] >= 2
    monkeypatch.setattr(RecordVersion, "CURRENT", "1.0.0")
    with pytest.raises(ValueError, match="upgrade"):
        RecordVersion.check_readable(payload, "definition graph")


def test_legacy_graft_without_capability_remains_resolvable() -> None:
    """An actual old-shaped member uses True when its recorded bool is absent."""
    root = _recording()
    source = _book("legacy-source")
    spell_id = source.bind(spell=GraphImplementation, existence="unique")
    conduit = source.conjure(dynamic=True, name="legacy-source-root")
    record = root.capture_index_graft(source._spells_by_id[spell_id].spell_index.id)
    record["record_version"] = "1.0.0"
    record["members"][spell_id]["payload"].pop("resolvable")
    conduit.permanent_cleanup()
    host = _book("legacy-host")
    host_conduit = host.conjure(dynamic=True, name="legacy-host-root")
    assert root.graft_index(record, host)["status"] == "complete"
    assert host._spells_by_id[spell_id].resolvable is True
    assert host_conduit.meld(spell_id=spell_id).value() == "supplied"


@pytest.mark.parametrize("binding_visible", [False, True])
def test_relationship_navigation_respects_visible_endpoints_and_sections(
    monkeypatch: pytest.MonkeyPatch, binding_visible: bool,
) -> None:
    """The graph join cannot reveal a hidden endpoint or a hidden binding section."""
    source_id = "book:consumer"
    visible_target = "book:definition"
    relationships = tuple(
        {"kind": "override_required", "parameter": "value", "target_source_id": target}
        for target in (visible_target, "book:hidden")
    )
    payload = {"binding_payload": {"resolvable": True, "relationships": relationships}}
    descriptions = [
        {"source_id": source_id, "payload": payload if binding_visible else {}},
        {"source_id": visible_target, "payload": {"binding_payload": {"resolvable": False}}},
    ]
    by_id = {description["source_id"]: description for description in descriptions}
    # The compiled ACL/view descriptions are the input boundary; no runtime lookup is mocked.
    monkeypatch.setattr(ViewSpell, "_entered_view_action", lambda *_args, **_kwargs: nullcontext())
    monkeypatch.setattr(ViewSpell, "describe_spells", lambda *_args, **_kwargs: descriptions)
    monkeypatch.setattr(ViewSpell, "describe_spell", lambda _self, key, **_kwargs: by_id[key])
    view = ViewSpell(frame_view=None)
    try:
        result = view.describe_spell_relationships(source_id)
        assert result["outgoing"] == ([{"source_id": source_id, **relationships[0]}] if binding_visible else [])
        assert result["resolvable"] is (True if binding_visible else None)
        assert "book:hidden" not in repr(result)
    finally:
        view.cleanup()
