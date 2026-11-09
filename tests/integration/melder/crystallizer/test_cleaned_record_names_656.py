"""Major5 cached records retain terminal intent across CLEANED naming and both restore drivers."""

import json
from pathlib import Path
from typing import Dict, Iterator, List, Tuple, Union, cast

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_configuration import MutationResearchConfiguration
from melder.nexus.nexus import Nexus


def _reboot_world() -> None:
    """Run normal owned world teardown, boot hosted roots, and rebind standard test references."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Each cache round trip owns a complete world and leaves a live successor for later tests."""
    _reboot_world()
    try:
        yield
    finally:
        _reboot_world()


@pytest.fixture
def cache_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Route only filesystem custody to pytest's isolated directory."""
    root = tmp_path / "crystallizer-cache"
    monkeypatch.setattr(
        CrystallizerCache, "resolve_cache_root_path", staticmethod(lambda: root),
    )
    return root


def _activate_recorder(parallel: bool) -> Crystallizer:
    """Activate the real hosted recorder with an explicit sequential or parallel load policy."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_parallel_enabled", parallel)
    configuration.set_property("restore_scheduler_workers", 2)
    configuration.activate()
    recorder = Crystallizer()
    recorder.activate(configuration)
    return recorder


def _record_world(
    cache_root: Path, parallel: bool, final_state: str,
) -> Tuple[Crystallizer, str, Path]:
    """Record actual configured roots, their lifecycle acts, then seal and flush a real checkpoint."""
    recorder = _activate_recorder(parallel)
    nexus = Nexus()
    configuration = nexus.create_configuration()
    configuration.set_property("max_active_rift_count", 5)
    nexus.activate(configuration)
    research = Aether().mutation_research
    research.activate(MutationResearchConfiguration().with_defaults().activate())
    research.create_research_set("recorded-research")
    if final_state in ("disabled", "CLEANED"):
        nexus.deactivate()
        research.deactivate()
    if final_state == "CLEANED":
        nexus.cleanup()
        research.cleanup()
    checkpoint_id = recorder.create_checkpoint()
    assert recorder.flush_checkpoint(checkpoint_id) == [checkpoint_id]
    profile_name = str(recorder.describe_checkpoint(checkpoint_id)["profile_name"])
    return recorder, checkpoint_id, cache_root / profile_name / f"{checkpoint_id}.json"


def _terminal_name_fixture(cache_file: Path, state_name: str) -> Dict[str, object]:
    """Keep a real major5 cached item intact apart from its documented legacy terminal-name spelling."""
    item = cast(Dict[str, object], json.loads(cache_file.read_text(encoding="utf-8")))
    assert item["record_version"] == "5.0.0"
    payloads = cast(Dict[str, Dict[str, Dict[str, object]]], item["captured_payloads"])
    journal = cast(List[List[Union[int, str]]], item["journal_segment"])
    for kind in ("nexus_state", "mutation_research_state"):
        assert payloads[kind]["CLEANED"] == {"state": "CLEANED", "twin_present": True}
        states = [entry[2] for entry in journal if entry[1] == kind]
        assert states == ["enabled", "disabled", "CLEANED"]
        if state_name == "cleaned":
            payloads[kind]["cleaned"] = payloads[kind].pop("CLEANED")
            payloads[kind]["cleaned"]["state"] = "cleaned"
            for entry in journal:
                if entry[1] == kind and entry[2] == "CLEANED":
                    entry[2] = "cleaned"
    cache_file.write_text(json.dumps(item, sort_keys=True), encoding="utf-8")
    return item


@pytest.mark.parametrize("parallel", [False, True], ids=["sequential", "parallel"])
@pytest.mark.parametrize("state_name", ["cleaned", "CLEANED"], ids=["legacy", "canonical"])
def test_cached_terminal_state_never_reconstructs_cleaned_roots(
    cache_root: Path, parallel: bool, state_name: str,
) -> None:
    """Old and canonical final states suppress both roots through real public cached load and admission."""
    recorder, checkpoint_id, cache_file = _record_world(cache_root, parallel, "CLEANED")
    summary = recorder.describe_profile()
    assert summary["nexus_state"] == "CLEANED"
    assert summary["mutation_research_state"] == "CLEANED"
    _terminal_name_fixture(cache_file, state_name)
    _reboot_world()
    rebooted = _activate_recorder(parallel)
    assert rebooted.reload_cached_checkpoint(checkpoint_id)["checkpoint_id"] == checkpoint_id
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert bool(report["plan"]) is parallel
    counts = cast(Dict[str, int], report["built_counts"])
    assert (counts.get("nexus", 0), counts.get("mutation_research", 0)) == (0, 0)
    shortfalls = cast(List[Dict[str, str]], report["shortfalls"])
    for kind in ("nexus", "mutation_research"):
        assert {
            "kind": kind, "key": "root",
            "reason": f"{kind}_recorded_but_cleaned_before_seal_not_rebuilt",
        } in shortfalls
    assert Nexus().configured is False
    assert Aether().mutation_research.configured is False


@pytest.mark.parametrize("parallel", [False, True], ids=["sequential", "parallel"])
@pytest.mark.parametrize("final_state", ["enabled", "disabled"])
def test_cached_live_state_controls_rebuild_configuration_and_research(
    cache_root: Path, parallel: bool, final_state: str,
) -> None:
    """The terminal guard must preserve real enabled/disabled rebuilds and recorded organization."""
    _recorder, checkpoint_id, _cache_file = _record_world(cache_root, parallel, final_state)
    _reboot_world()
    rebooted = _activate_recorder(parallel)
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert bool(report["plan"]) is parallel
    counts = cast(Dict[str, int], report["built_counts"])
    assert counts["nexus"] == 1
    assert counts["mutation_research"] == 1
    nexus = Nexus()
    research = Aether().mutation_research
    assert nexus.configuration.get_property("max_active_rift_count") == 5
    assert research.list_research_set_names() == ["default", "recorded-research"]
    assert nexus.activated is (final_state == "enabled")
    assert research.activated is (final_state == "enabled")


@pytest.mark.parametrize(
    ("record_version", "reason"),
    [("4.3.0", "older than the oldest"), ("6.0.0", "newer than")],
)
def test_legacy_name_fixture_keeps_record_major_admission(
    cache_root: Path, record_version: str, reason: str,
) -> None:
    """Legacy-name compatibility never admits an older or newer unsupported record major."""
    _recorder, checkpoint_id, cache_file = _record_world(cache_root, False, "CLEANED")
    item = _terminal_name_fixture(cache_file, "cleaned")
    item["record_version"] = record_version
    cache_file.write_text(json.dumps(item, sort_keys=True), encoding="utf-8")
    _reboot_world()
    rebooted = _activate_recorder(False)
    with pytest.raises(ValueError, match=reason):
        rebooted.reload_cached_checkpoint(checkpoint_id)
