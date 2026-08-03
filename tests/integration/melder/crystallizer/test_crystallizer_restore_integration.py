"""
Integration tests for the restore engine against the REAL runtime: seal a
recorded world into checkpoints, simulate a fresh boot (singleton reset +
cache reload), and unfold it through Crystallizer.load_checkpoint - plus
the all-or-nothing rollback contract on injected failure.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystal_loader_system.restore_engine import RestoreEngine
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class RestoreAlpha:
    """
    Importable restore target (active bind lane).

    Contract:
        - Module-scoped so hydration can re-import it by qualname.
    """

    def __init__(self) -> None:
        """
        Initialize the marker service.
        """
        self.alive: bool = True


class RestoreBeta:
    """
    Importable restore target (staged member lane).
    """

    def __init__(self) -> None:
        """
        Initialize the marker service.
        """
        self.alive: bool = True


class RestoreGamma:
    """
    Importable restore target (peer conduit / contract lane).
    """

    def __init__(self) -> None:
        """
        Initialize the marker service.
        """
        self.alive: bool = True


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """
    Purpose:
        Isolate each test behind fresh Aether/Nexus/Crystallizer singletons.
    Contract:
        - Resets the world singletons and rebinds the Spellbook and Conduit
          static Aether references before and after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """
    Route the crystallizer cache into a per-test directory.

    Returns:
        Path: The isolated cache root.
    """
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def _activate_crystallizer():
    """
    Activate the Aether-hosted crystallizer with default knobs.

    Returns:
        Crystallizer: The live, activated singleton.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _dynamic_book():
    """
    Build one dynamic-posture Spellbook (configuration finalized first,
    per the recorded lane's configuration-discipline canon).

    Returns:
        Spellbook: The configured book on a dynamic frame posture.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(configuration=configuration)


def _fresh_boot():
    """
    Simulate a process restart: reset the world singletons mid-test and
    return the fresh activated crystallizer.

    Returns:
        Crystallizer: The post-"boot" activated singleton.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    return _activate_crystallizer()


def test_round_trip_restores_binds_and_conduit_from_cached_checkpoint(
        cache_root,
):
    """
    Purpose:
        Prove the full boot lane: record -> seal -> flush -> fresh boot ->
        reload -> load_checkpoint -> the world re-melds and re-records.
    Contract:
        The report completes; the rebuilt book re-emits custody for the
        SAME spell SHA (content-stable identity) under a fresh profile.
    Returns:
        None.
    Raises:
        AssertionError: If the unfolded world diverges from the record.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    spell_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="root")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spellbook"] == 1
    assert report["built_counts"]["conduit"] == 1
    assert report["built_counts"]["spell_active"] == 1
    # Re-emission: the rebuilt world re-recorded the same content-stable
    # spell SHA into the fresh active profile.
    assert rebooted.get_spell_crystal(spell_id).id == spell_id


def test_round_trip_restores_staged_member_and_selection(cache_root):
    """
    Purpose:
        Prove staged members re-park onto their rebuilt index anchor.
    Contract:
        The staged member binds inactive on the anchor; the recorded
        selection (the active member) is preserved without a notch.
    Returns:
        None.
    Raises:
        AssertionError: If staging or selection diverges.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    active_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="root")
    active_spell = book._spells_by_id[active_id]
    conduit.bind_inactive(
        spell=RestoreBeta,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 1
    assert report["built_counts"]["spell_staged"] == 1
    assert report["built_counts"].get("selection_notch") is None


def test_round_trip_restores_links_between_conduits(cache_root):
    """
    Purpose:
        Prove outbound link edges re-establish from the initiator side.
    Contract:
        Two rebuilt conduits re-link; the report counts one link and the
        identity map carries both recorded conduit ids.
    Returns:
        None.
    Raises:
        AssertionError: If the link lane diverges.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["link"] == 1
    assert conduit_a._id in report["identity_map"]
    assert conduit_b._id in report["identity_map"]


def test_round_trip_regrants_initiated_contract_details(cache_root):
    """
    Purpose:
        Prove contracts re-grant LAST from each side's initiated details.
    Contract:
        The re-granted detail count matches the recorded initiated
        entries; index subscriptions are reported (first cut).
    Returns:
        None.
    Raises:
        AssertionError: If the contract lane diverges.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    granted_id = book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    # Borrower-called verb: conduit_b borrows granted_id FROM its owner
    # conduit_a (the ward eligibility check demands the `conduit` argument
    # own the spell).
    with conduit_b.transaction("link", conduits=[conduit_a, conduit_b]):
        conduit_b.add_spell_to_contract(
            spell_id=granted_id,
            conduit=conduit_a,
            permissions="create",
        )
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["link"] == 1
    assert report["built_counts"]["contract_detail"] >= 1


def test_round_trip_restores_the_nexus_root(cache_root):
    """
    Purpose:
        Prove the Nexus root restores: recorded configuration reloads
        through the reload lane and the rebuilt root re-enables (and
        re-records) on the fresh boot.
    Contract:
        The report counts one nexus build; the rebooted world's Nexus is
        enabled with the recorded governance values.
    Returns:
        None.
    Raises:
        AssertionError: If the nexus lane diverges.
    """
    from melder.nexus.configuration.nexus_configuration import (
        NexusConfiguration,
    )

    crystallizer = _activate_crystallizer()
    nexus_configuration = NexusConfiguration()
    nexus_configuration.load_default_dictionary()
    nexus_configuration.set_property("max_active_rift_count", 5)
    Nexus().activate(nexus_configuration)
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["nexus"] == 1
    rebuilt = Nexus()
    assert rebuilt.is_activated is True
    assert rebuilt.configuration.get_property("max_active_rift_count") == 5


def test_removed_spell_stays_removed_after_restore(cache_root):
    """
    Purpose:
        Prove tombstones hold across the boot boundary.
    Contract:
        A spell removed before the seal is NOT rebuilt; only the survivor
        binds.
    Returns:
        None.
    Raises:
        AssertionError: If the tombstone leaks a rebuild.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    doomed_id = book.bind(
        spell=RestoreBeta,
        existence=Existence.unique,
        permissions="create",
        binding_name="doomed",
    )
    book.conjure(dynamic=True, name="root")
    book.cleanup_and_remove_spell(doomed_id)
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 1
    with pytest.raises(KeyError):
        rebooted.get_spell_crystal(doomed_id)


def test_failed_replay_tears_the_partial_world_down(cache_root):
    """
    Purpose:
        Prove the all-or-nothing contract on injected stage failure.
    Contract:
        A hand-built chain whose conduit twin carries an impossible policy
        fails the books_and_binds stage; the engine raises RuntimeError
        naming the stage and the frame holds no leftover conduits.
    Returns:
        None.
    Raises:
        AssertionError: If a partial world survives the failure.
    """
    _activate_crystallizer()
    window = {
        "journal": [
            [1, "spellbook", "book-x"],
            [2, "conduit", "cond-x"],
        ],
        "payloads": {
            "spellbook": {
                "book-x": {
                    "spellbook_id": "book-x",
                    "frame_name": "default",
                    "configuration_payload": {
                        "system_state": "dynamic",
                        "ai_native_enabled": True,
                        "rift_enabled": True,
                        "phase_scheduler_workers_per_spellbook": 1,
                    },
                    "hook_names": [],
                    "bind_order": [],
                }
            },
            "conduit": {
                "cond-x": {
                    "conduit_id": "cond-x",
                    "spellbook_id": "book-x",
                    "conduit_name": "broken",
                    "policy_name": "no_such_policy_anywhere",
                    "dynamic": True,
                    "link_targets": [],
                }
            },
        },
    }
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["01ROLLBACKTEST0000000000"],
        chain=[window],
    )
    with pytest.raises(RuntimeError) as raised:
        engine.restore()
    assert "books_and_binds" in str(raised.value)
    engine.cleanup()
    frame = Aether()._aetheric_frames["default"]
    assert frame._conduits == {}


def test_pre_patch_custody_without_gap_fields_still_restores(cache_root):
    """
    Purpose:
        Prove tolerance for cached checkpoints sealed BEFORE the capture-gap
        fields landed.
    Contract:
        Custody payloads missing disposal_method_names / profile_family
        bind with the defaults (empty disposal set, "general").
    Returns:
        None.
    Raises:
        AssertionError: If absence of the new keys breaks the bind lane.
    """
    _activate_crystallizer()
    window = {
        "journal": [
            [1, "spellbook", "book-y"],
            [2, "conduit", "cond-y"],
            [3, "spell_crystal", "sha-y"],
        ],
        "payloads": {
            "spellbook": {
                "book-y": {
                    "spellbook_id": "book-y",
                    "frame_name": "default",
                    "configuration_payload": {
                        "system_state": "dynamic",
                        "ai_native_enabled": True,
                        "rift_enabled": True,
                        "phase_scheduler_workers_per_spellbook": 1,
                    },
                    "hook_names": [],
                    "bind_order": ["sha-y"],
                }
            },
            "conduit": {
                "cond-y": {
                    "conduit_id": "cond-y",
                    "spellbook_id": "book-y",
                    "conduit_name": "root",
                    "policy_name": "default",
                    "dynamic": True,
                    "link_targets": [],
                }
            },
            "spell_crystal": {
                "sha-y": {
                    "id": "sha-y",
                    "spellbook_id": "book-y",
                    "spell_name": "RestoreAlpha",
                    "binding_name": None,
                    "spellframe_name": None,
                    "existence_name": "unique",
                    "permissions_name": "create",
                    "rebindability": "hydratable",
                    "root_module_kind": "user_source",
                    "root_module_name": (
                        "tests.integration.melder.crystallizer."
                        "test_crystallizer_restore_integration"
                    ),
                    "root_target_qualname": "RestoreAlpha",
                    "root_target_kind": "class",
                }
            },
        },
    }
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["01PREPATCHTEST0000000000"],
        chain=[window],
    )
    report = engine.restore()
    payload = report.describe()
    assert payload["status"] == "complete"
    assert payload["built_counts"]["spell_active"] == 1
    report.cleanup()
    engine.cleanup()


def test_post_notch_selection_restores_without_an_extra_notch(cache_root):
    """
    Purpose:
        Prove a world sealed AFTER a notch restores its final selection
        directly.
    Contract:
        The fold captures the final truth: the promoted member holds
        active custody and the recorded selection, so replay binds it
        active, stages the parked original, and needs NO selection notch
        (the recorded and rebuilt selections already agree).
    Returns:
        None.
    Raises:
        AssertionError: If the folded selection diverges from the rebuilt
            world or a redundant notch fires.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    active_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="root")
    active_spell = book._spells_by_id[active_id]
    staged_id = conduit.bind_inactive(
        spell=RestoreBeta,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    staged_spell = book._inactive_spells[staged_id]
    conduit.notch_spell(
        spell_index=active_spell.spell_index,
        spell=staged_spell,
    )
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 1
    assert report["built_counts"]["spell_staged"] == 1
    assert report["built_counts"].get("selection_notch") is None

def test_profile_cache_round_trip_reloads_and_unfolds(cache_root):
    """
    Purpose:
        Prove the profile-cache transport (owner ruling: the cache IS the
        transport): record a world, flush the profile's checkpoints,
        reboot fresh, reload the whole profile from cache, unfold.
    Contract:
        reload_profile_from_cache inserts every cached checkpoint;
        load_checkpoint on the newest restores the world; the rebuilt
        book re-emits the same content-stable spell SHA.
    Returns:
        None.
    Raises:
        AssertionError: If any leg of the profile-cache lane diverges.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    spell_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="root")
    crystallizer.create_checkpoint()
    flushed = crystallizer.flush_checkpoint()

    rebooted = _fresh_boot()
    summary = rebooted.reload_profile_from_cache("default")
    assert len(summary["inserted"]) == len(flushed)
    report = rebooted.load_checkpoint(summary["inserted"][-1])

    assert report["status"] == "complete"
    assert report["built_counts"]["spellbook"] == 1
    assert report["built_counts"]["spell_active"] == 1
    # Spell SHAs are content-STABLE and never enter the identity map
    # (only conduit/index/book ULIDs translate); the proof of the rebuilt
    # bind is the re-emission of the SAME SHA into the fresh profile.
    assert rebooted.get_spell_crystal(spell_id).id == spell_id


def test_pod_bootstrap_rebuilds_the_world_from_the_remote(
        cache_root, tmp_path,
):
    """
    Purpose:
        Prove the kube pod-restart story end to end: a recorded world
        uploads through user callables; a BRAND-NEW pod (fresh
        singletons, EMPTY local cache) runs the fluent
        CrystallizerBootstrap and comes back with the world rebuilt.
    Contract:
        Bootstrap activates, attaches the manager, finds no local cache,
        pulls the profile from the remote, stores it locally, picks the
        newest checkpoint, and load_checkpoint completes - the same
        content-stable spell SHA re-emits in the rebuilt pod.
    Returns:
        None.
    Raises:
        AssertionError: If any leg of the pod boot diverges.
    """
    import shutil

    from melder.crystallizer.crystal_loader_system.bootstrap_loader import (
        CrystallizerBootstrap,
    )
    from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
        ExternalPersistenceManagerConfiguration,
    )

    remote_store = {}

    def upload(profile_name, checkpoint_id, cached_item):
        remote_store[checkpoint_id] = (profile_name, cached_item)

    def download(checkpoint_id):
        entry = remote_store.get(checkpoint_id)
        return entry[1] if entry is not None else None

    def list_ids(profile_name):
        return [
            checkpoint_id
            for checkpoint_id, entry in remote_store.items()
            if entry[0] == profile_name
        ]

    # ---- Pod 1: record, seal, flush (cache + remote upload). ----------
    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        ExternalPersistenceManagerConfiguration()
        .with_upload_handler(upload)
        .with_download_handler(download)
        .with_list_handler(list_ids)
    )
    book = _dynamic_book()
    spell_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="root")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    assert checkpoint_id in remote_store

    # ---- Pod death: fresh singletons AND an empty local cache. --------
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    shutil.rmtree(cache_root, ignore_errors=True)

    # ---- Pod 2: one fluent chain boots the whole world back. ----------
    report = (
        CrystallizerBootstrap()
        .with_external_persistence_manager(
            ExternalPersistenceManagerConfiguration()
            .with_upload_handler(upload)
            .with_download_handler(download)
            .with_list_handler(list_ids)
        )
        .with_profile("default")
        .bootstrap()
    )

    assert report["activated"] is True
    assert report["cache_reload"] is None
    assert checkpoint_id in report["remote_reload"]["inserted"]
    assert report["restored_checkpoint_id"] == checkpoint_id
    assert report["restore_report"]["status"] == "complete"
    assert report["restore_report"]["built_counts"]["spellbook"] == 1
    # The rebuilt pod re-recorded the same content-stable spell SHA, and
    # the remote pull re-flushed the item into the fresh local cache.
    assert Crystallizer().get_spell_crystal(spell_id).id == spell_id
    assert (cache_root / "default" / (checkpoint_id + ".json")).is_file()


def test_saved_conduit_formation_restores_directly_after_reboot(
        cache_root,
):
    """
    Purpose:
        Prove the owner's formation story: a user likes a conduit
        formation, saves it under THEIR name, the process dies, and a
        fresh boot restores JUST that formation (book + conduit +
        custody) - not the world.
    Contract:
        save_formation captures the conduit scope (spellbook included);
        the analyzer pre-flights it clean; restore_formation on the
        fresh boot rebuilds it with the engine's normal report; the
        same content-stable spell SHA re-records.
    Returns:
        None.
    Raises:
        AssertionError: If any leg of the formation lane diverges.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    spell_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="keeper")
    crystallizer.save_formation(
        "my-keeper-formation",
        conduit_id=conduit._id,
        description="the formation I like",
    )
    assert crystallizer.list_formations() == ["my-keeper-formation"]
    preflight = crystallizer.analyze_formation("my-keeper-formation")
    # Conduit-scoped formations DELIBERATELY exclude the frame twin
    # (frame posture is frame-scope material; restore fallback-postures
    # from book hints), so the scope-blind frame_posture strategy warns.
    # This is the documented current truth until the admission plane makes
    # admission scope-aware (decomposition epic S4; the plane is
    # LoadAdmission since the 2026-07-11 rename) - then a conduit
    # scope interprets frame-absence as expected and this flips back to
    # a clean verdict for the scope.
    assert preflight["verdict"] == "warnings"
    warning_strategies = {
        finding["strategy"]
        for finding in preflight["findings"]
        if finding["severity"] == "warning"
    }
    assert warning_strategies == {"frame_posture"}

    rebooted = _fresh_boot()
    assert rebooted.list_formations() == ["my-keeper-formation"]
    report = rebooted.restore_formation("my-keeper-formation")

    assert report["status"] == "complete"
    assert report["built_counts"]["spellbook"] == 1
    assert report["built_counts"]["conduit"] == 1
    assert report["built_counts"]["spell_active"] == 1
    # S4 flip-back (the S1 acceptance criterion landed): admission is
    # scope-aware - the conduit-scoped load adjudicates the expected
    # frame_posture warning away, so the ADMISSION verdict is clean
    # while the raw preflight above stays honest "warnings".
    admission = dict(report["admission"])
    assert admission["scope"] == "conduit"
    assert admission["verdict"] == "clean"
    assert len(list(admission["reclassified"])) >= 1
    assert rebooted.get_spell_crystal(spell_id).id == spell_id


def test_auto_flush_cadence_ships_the_automatic_seal(cache_root):
    """
    Purpose:
        Regression (S-test; symptom: the S3 decomposition left the
        automatic-cadence auto-flush lane calling a removed ledger verb -
        caught by gate grep, never by a test, and it would have
        AttributeError'd in production on the first interval).
    Contract:
        With auto-flush armed and the cadence interval elapsed, one
        cadence tick seals an automatic checkpoint AND ships it to the
        local cache through the asset system (seal-then-ship, both legs).
    Returns:
        None.
    Raises:
        AssertionError: If the cadence seal never reaches the cache.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="cadence")
    # Arm the cadence directly (the regression harness forces the exact
    # private posture the production ticker reaches: auto-flush on,
    # interval elapsed) - the SEAM under test is the flush routing.
    crystallizer._auto_flush_checkpoints = True
    crystallizer._checkpoint_interval_seconds = 0.0
    crystallizer._last_automatic_checkpoint_monotonic = 0.0
    crystallizer._maybe_create_automatic_checkpoint()
    cached_ids = crystallizer.list_cached_checkpoint_ids()
    assert cached_ids != []


def test_synthetic_rooted_spell_restores_across_the_boot_boundary(
        cache_root,
):
    """
    Purpose:
        Prove loader chain M3 end to end: a spell whose bind target lives
        in a SYNTHETIC module (no file anywhere) records its module
        source, survives a simulated process death INCLUDING the module's
        eviction from sys.modules, and restores - module world rebuilt
        from the record, target re-bound with the same content-stable
        SHA.
    Contract:
        The custody crystal carries synthetic_module_sources; the fresh
        boot rebuilds the module (built_counts synthetic_module >= 1),
        the bind hydrates, and the restored world re-records the SHA.
    Returns:
        None.
    Raises:
        AssertionError: If any leg of the synthetic restore diverges.
    """
    import sys

    import hashlib

    from melder.crystallizer.synthetic_module import SyntheticModule

    module_name = "m3_live_world"
    module_source_text = (
        "class M3LiveService:\n"
        "    def __init__(self) -> None:\n"
        "        self.alive = True\n"
    )
    synthetic_module = SyntheticModule(
        module_name=module_name,
        spell_crystal_id="m3-live-crystal",
        source_text=module_source_text,
        # The REAL fingerprint: S4 admission refuses tampered-looking
        # synthetic sources (synthetic_source_integrity blocker), so the
        # fixture must carry true integrity - the old "m3-live-sha"
        # placeholder read as tampering and correctly refused the boot.
        source_sha256=hashlib.sha256(
            module_source_text.encode("utf-8")
        ).hexdigest(),
        binding_signature="m3-live-binding",
    )
    try:
        synthetic_module.register_in_import_registry()
        synthetic_module.publish_to_sys_modules()
        synthetic_module.execute_source()
        target = synthetic_module.__dict__["M3LiveService"]

        crystallizer = _activate_crystallizer()
        book = _dynamic_book()
        spell_id = book.bind(
            spell=target,
            existence=Existence.unique,
            permissions="create",
        )
        book.conjure(dynamic=True, name="root")
        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)

        # Process death: fresh singletons AND the synthetic module gone
        # from sys.modules (a real new process has neither).
        rebooted = _fresh_boot()
        if not synthetic_module.cleaned:
            synthetic_module.cleanup()
        sys.modules.pop(module_name, None)

        rebooted.reload_cached_checkpoint(checkpoint_id)
        report = rebooted.load_checkpoint(checkpoint_id)

        assert report["status"] == "complete"
        assert report["built_counts"]["synthetic_module"] >= 1
        assert report["built_counts"]["spell_active"] == 1
        assert module_name in sys.modules
        # Same content-derived SHA re-recorded by the rebuilt world.
        assert rebooted.get_spell_crystal(spell_id).id == spell_id
    finally:
        if not synthetic_module.cleaned:
            synthetic_module.cleanup()
        sys.modules.pop(module_name, None)


def test_mutation_research_round_trips_through_checkpoints(cache_root):
    """
    Purpose:
        S3c of mr_restore_build_stage_2026_07_11: prove a checkpointed
        world unfolds WITH its research - declare -> seal -> flush ->
        fresh boot -> load_checkpoint -> lanes, membership, and residence
        present; research CONTINUABLE; a later activation hydration NO-OPs
        because the engine-restored registry is already touched.
    Contract:
        The report shows mutation_research under built stages and carries
        ZERO first_cut shortfalls; the rebuilt set walks the recorded
        lanes and accepts new research afterwards.
    Returns:
        None.
    Raises:
        AssertionError: If the unfolded research diverges from the record.
    """
    from melder.mutation_research.mutation_configuration import (
        MutationResearchConfiguration,
    )
    from melder.mutation_research.mutation_research import MutationResearch

    # Aether owns the research root, so resetting the root's singleton alone
    # leaves Aether's slot pointing at the corpse. Reset both, then REBUILD -
    # a reset only tears down; `Aether()` is what constructs the hosted set
    # again, and without it the next bare `Crystallizer()` is a first
    # construction with no host and refuses.
    MutationResearch._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Aether()
    try:
        crystallizer = _activate_crystallizer()
        root = Aether()._get_mutation_research()
        root.activate(MutationResearchConfiguration().with_defaults().activate())
        research = root.research_set()
        research.create_lane("experiments", actor="s3c")
        research.register_spell(
            "f" * 64, lane="experiments", author="s3c", reason="round-trip"
        )
        research.register_spell("a" * 64, author="s3c")

        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)

        MutationResearch._reset_singleton_for_tests()
        rebooted = _fresh_boot()
        rebooted.reload_cached_checkpoint(checkpoint_id)
        report = rebooted.load_checkpoint(checkpoint_id)

        assert report["status"] == "complete"
        assert report["built_counts"]["mutation_research"] == 1
        assert all(
            "first_cut" not in str(shortfall)
            for shortfall in report.get("shortfalls", [])
        )

        restored_root = Aether()._get_mutation_research()
        restored_set = restored_root.research_set()
        assert set(restored_set.lane_names()) == {"default", "experiments"}
        assert restored_set.residence_of("f" * 64) is not None
        # Vocabulary sync 2026-07-11: node payloads speak spell_id.
        walked_ids = [
            str(entry.get("spell_id"))
            for entry in restored_set.walk("experiments")
        ]
        assert "f" * 64 in walked_ids

        # Continuable: new research lands on the restored organization.
        restored_set.register_spell(
            "b" * 64, lane="experiments", author="s3c", reason="post-restore"
        )
        assert restored_set.residence_of("b" * 64) is not None

        # Already-touched registry: a later activation hydration NO-OPs (the
        # engine-restored organization survives untouched).
        restored_root.activate(hydrate_from_record=True)
        assert restored_set.residence_of("b" * 64) is not None
        assert set(restored_set.lane_names()) == {"default", "experiments"}
    finally:
        MutationResearch._reset_singleton_for_tests()


def test_mutation_research_disabled_worlds_restore_deactivated(cache_root):
    """
    Purpose:
        The disabled later-wins lane (owner + mutation_0 ruling 15:22Z:
        KEEP deactivate/disabled): a world sealed with a deactivated MR
        restores with its research PRESENT but the root SWITCHED OFF -
        activate-then-deactivate replays both truthful acts.
    Contract:
        Research organization survives (research_set() reads while
        inactive); root.activated is False post-restore. DOCUMENTED
        NUANCE (mutation_0, accepted behavior): because MR builds before
        books, a spell bound during a pre-seal DEACTIVATED window seals
        undeclared but would restore DECLARED in worlds sealed ACTIVE;
        in THIS lane the root restores deactivated before the books
        stage, so replayed binds do not auto-record - the sealed truth
        (undeclared) holds.
    Returns:
        None.
    Raises:
        AssertionError: If the deactivated world restores switched on or
            loses its research.
    """
    from melder.mutation_research.mutation_configuration import (
        MutationResearchConfiguration,
    )
    from melder.mutation_research.mutation_research import MutationResearch

    # Aether owns the research root, so resetting the root's singleton alone
    # leaves Aether's slot pointing at the corpse. Reset both, then REBUILD -
    # a reset only tears down; `Aether()` is what constructs the hosted set
    # again, and without it the next bare `Crystallizer()` is a first
    # construction with no host and refuses.
    MutationResearch._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Aether()
    try:
        crystallizer = _activate_crystallizer()
        root = Aether()._get_mutation_research()
        root.activate(MutationResearchConfiguration().with_defaults().activate())
        research = root.research_set()
        research.register_spell("c" * 64, author="s3c", reason="pre-off")

        # The kill switch: run-without-declaring from here on; the world
        # seals with MR truthfully OFF.
        root.deactivate()

        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)

        MutationResearch._reset_singleton_for_tests()
        rebooted = _fresh_boot()
        rebooted.reload_cached_checkpoint(checkpoint_id)
        report = rebooted.load_checkpoint(checkpoint_id)

        assert report["status"] == "complete"
        assert report["built_counts"]["mutation_research"] == 1

        restored_root = Aether()._get_mutation_research()
        # Both truthful acts replayed: built, then switched back off.
        assert restored_root.activated is False
        # The organization survives the off switch (reads need no
        # activation).
        assert restored_root.research_set().residence_of(
            "c" * 64
        ) is not None
    finally:
        MutationResearch._reset_singleton_for_tests()


def test_user_source_retention_rebuilds_deleted_files(
        cache_root, tmp_path, monkeypatch,
):
    """
    Purpose:
        S2 physical custody end to end: seal a world with retention ON
        whose spell target lives in a USER FILE, delete the file, fresh
        boot, load_checkpoint - the spell rebuilds from retained text
        through the synthetic module lane with the honest shortfall.
    Contract:
        The report completes; the rebuild names itself
        ("user_module_rebuilt_synthetic_from_retained_source"); the
        module is import-resolvable again for the rebuilt bind.
    Returns:
        None.
    Raises:
        AssertionError: If the deleted user world does not rebuild.
    """
    import importlib as _importlib
    import sys

    module_root = tmp_path / "userland_s2"
    module_root.mkdir()
    module_file = module_root / "s2_retained_widget.py"
    module_file.write_text(
        "class S2RetainedWidget:\n"
        "    def run(self):\n"
        "        return 42\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(module_root))
    module = _importlib.import_module("s2_retained_widget")
    try:
        # Retention ON + the temp root as user-source authority.
        configuration = CrystallizerConfiguration().with_defaults()
        configuration.with_user_source_root_paths((module_root,))
        configuration.with_retain_user_sources(True)
        configuration.activate()
        crystallizer = Crystallizer()
        crystallizer.activate(configuration)

        book = _dynamic_book()
        spell_id = book.bind(
            spell=module.S2RetainedWidget,
            existence=Existence.unique,
            permissions="create",
        )
        book.conjure(dynamic=True, name="root")

        # Retention proof at the record: the crystal carries the text.
        sealed = crystallizer.get_spell_crystal(spell_id).describe()
        assert "s2_retained_widget" in sealed["user_module_sources"]

        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)

        # The fresh pod: no user file, no cached import.
        module_file.unlink()
        sys.modules.pop("s2_retained_widget", None)

        rebooted = _fresh_boot()
        rebooted.reload_cached_checkpoint(checkpoint_id)
        report = rebooted.load_checkpoint(checkpoint_id)

        assert report["status"] == "complete"
        assert report["built_counts"]["spell_active"] == 1
        assert (
            "user_module_rebuilt_synthetic_from_retained_source"
            in str(report.get("shortfalls", []))
        )
        assert "s2_retained_widget" in sys.modules
    finally:
        sys.modules.pop("s2_retained_widget", None)


def _sqlite_handler_trio(db_path):
    """
    Build the upload/download/list handler callables over one SQLite file.

    The user-side pattern the external persistence lane was ruled around
    (callables-first, no ORM): the handlers own their connection, their
    schema, and their serialization - melder only calls them.
    """
    import json
    import sqlite3

    def _connect():
        connection = sqlite3.connect(str(db_path))
        connection.execute(
            "CREATE TABLE IF NOT EXISTS checkpoints ("
            "checkpoint_id TEXT PRIMARY KEY, "
            "profile_name TEXT NOT NULL, "
            "payload TEXT NOT NULL)"
        )
        return connection

    def upload(profile_name, checkpoint_id, cached_item):
        connection = _connect()
        try:
            with connection:
                # INSERT OR REPLACE = the remote Update lane: re-flushed
                # ids overwrite their row (replace-on-emit parity).
                connection.execute(
                    "INSERT OR REPLACE INTO checkpoints VALUES (?, ?, ?)",
                    (checkpoint_id, profile_name, json.dumps(cached_item)),
                )
        finally:
            connection.close()

    def download(checkpoint_id):
        connection = _connect()
        try:
            row = connection.execute(
                "SELECT payload FROM checkpoints WHERE checkpoint_id = ?",
                (checkpoint_id,),
            ).fetchone()
            return json.loads(row[0]) if row is not None else None
        finally:
            connection.close()

    def list_ids(profile_name):
        connection = _connect()
        try:
            return [
                row[0]
                for row in connection.execute(
                    "SELECT checkpoint_id FROM checkpoints "
                    "WHERE profile_name = ?",
                    (profile_name,),
                )
            ]
        finally:
            connection.close()

    return upload, download, list_ids


def _external_configuration(upload=None, download=None, list_ids=None):
    """Build one handler configuration (frozen by the facade attach)."""
    from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
        ExternalPersistenceManagerConfiguration,
    )

    configuration = ExternalPersistenceManagerConfiguration()
    if upload is not None:
        configuration.with_upload_handler(upload)
    if download is not None:
        configuration.with_download_handler(download)
    if list_ids is not None:
        configuration.with_list_handler(list_ids)
    return configuration


def test_flush_pushes_checkpoints_into_sqlite(cache_root, tmp_path):
    """
    Purpose:
        The C/U half of the DB lane over a REAL stdlib sqlite3 store:
        flush ships local-then-remote through the user's upload handler,
        and re-flushing the same id upserts (INSERT OR REPLACE) instead
        of duplicating.
    Contract:
        The row exists, its JSON payload parses, and the id round-trips
        through the download handler.
    """
    import json
    import sqlite3

    db_path = tmp_path / "melder_checkpoints.sqlite3"
    upload, download, list_ids = _sqlite_handler_trio(db_path)

    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _external_configuration(upload, download, list_ids)
    )
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    book.conjure(dynamic=True, name="root")

    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    # Upsert lane: a second flush of the same id must not duplicate.
    crystallizer.flush_checkpoint(checkpoint_id)

    connection = sqlite3.connect(str(db_path))
    try:
        rows = connection.execute(
            "SELECT checkpoint_id, payload FROM checkpoints"
        ).fetchall()
    finally:
        connection.close()
    stored_ids = [row[0] for row in rows]
    assert checkpoint_id in stored_ids
    assert len(stored_ids) == len(set(stored_ids))
    assert json.loads(rows[0][1])
    assert download(checkpoint_id) is not None
    assert checkpoint_id in list_ids("default")


def test_pod_death_rebuilds_the_world_from_sqlite(cache_root, tmp_path):
    """
    Purpose:
        The R half end to end: seal + flush to SQLite, then POD DEATH
        (local cache erased, fresh boot) - the world rebuilds purely
        from the user's DB: reload_profile_from_external inserts the
        remote history, load_checkpoint unfolds it.
    Contract:
        Inserted count >= 1; the restored world re-records the SAME
        content-derived spell SHA.
    """
    import shutil

    db_path = tmp_path / "melder_checkpoints.sqlite3"
    upload, download, list_ids = _sqlite_handler_trio(db_path)

    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _external_configuration(upload, download, list_ids)
    )
    book = _dynamic_book()
    spell_id = book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    book.conjure(dynamic=True, name="root")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    # Pod death: the entire local cache is gone; only the DB survives.
    shutil.rmtree(cache_root, ignore_errors=True)

    rebooted = _fresh_boot()
    rebooted.configure_external_persistence_manager(
        _external_configuration(upload, download, list_ids)
    )
    outcome = rebooted.reload_profile_from_external("default")
    # "inserted" is the id LIST (insert-if-absent summary), not a count.
    assert len(outcome["inserted"]) >= 1

    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert rebooted.get_spell_crystal(spell_id).id == spell_id


def test_broken_upload_handler_is_lenient_and_counted(cache_root, tmp_path):
    """
    Purpose:
        The lenient-upload law: a dying DB handler never kills the local
        seal/flush lane - the failure counts on the manager's diagnostic
        surface instead.
    Contract:
        flush completes; describe_external_persistence_manager reports
        the failure count.
    """
    def broken_upload(profile_name, checkpoint_id, cached_item):
        raise RuntimeError("db is down")

    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _external_configuration(upload=broken_upload)
    )
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    book.conjure(dynamic=True, name="root")

    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)  # must not raise

    described = crystallizer.describe_external_persistence_manager()
    assert described["upload_failure_count"] == 1


def test_inconsistent_remote_refuses_loudly(cache_root, tmp_path):
    """
    Purpose:
        The remote-contradiction law: a DB that LISTS an id but returns
        nothing for it is inconsistent - the reload refuses with a
        teach-grade error instead of silently rebuilding a partial world.
    """
    def lying_list(profile_name):
        return ["01LIEDABOUTTHISCHECKPOINT0"]

    def empty_download(checkpoint_id):
        return None

    crystallizer = _activate_crystallizer()
    # Read-only configuration: no write lane attached, so the flush knob
    # must be disabled explicitly (validate refuses a knob pointing at
    # nothing).
    crystallizer.configure_external_persistence_manager(
        _external_configuration(
            download=empty_download, list_ids=lying_list
        ).with_upload_on_flush(False)
    )
    with pytest.raises(ValueError, match="inconsistent"):
        crystallizer.reload_profile_from_external("default")


def _sqlite_mesh_handlers(db_path):
    """
    Build the GENERIC kind-partitioned handler quartet over one SQLite
    file (external_mesh 2026-07-12): one table, a kind column, four plain
    callables - store/fetch/list/delete for ANY mesh unit.
    """
    import json
    import sqlite3

    def _connect():
        connection = sqlite3.connect(str(db_path))
        connection.execute(
            "CREATE TABLE IF NOT EXISTS mesh_units ("
            "kind TEXT NOT NULL, "
            "unit_id TEXT NOT NULL, "
            "profile_name TEXT NOT NULL, "
            "payload TEXT NOT NULL, "
            "PRIMARY KEY (kind, unit_id))"
        )
        return connection

    def store(kind, profile_name, unit_id, payload):
        connection = _connect()
        try:
            with connection:
                connection.execute(
                    "INSERT OR REPLACE INTO mesh_units VALUES (?, ?, ?, ?)",
                    (kind, unit_id, profile_name, json.dumps(payload)),
                )
        finally:
            connection.close()

    def fetch(kind, unit_id):
        connection = _connect()
        try:
            row = connection.execute(
                "SELECT payload FROM mesh_units "
                "WHERE kind = ? AND unit_id = ?",
                (kind, unit_id),
            ).fetchone()
            return json.loads(row[0]) if row is not None else None
        finally:
            connection.close()

    def list_units(kind, profile_name):
        connection = _connect()
        try:
            return [
                row[0]
                for row in connection.execute(
                    "SELECT unit_id FROM mesh_units "
                    "WHERE kind = ? AND profile_name = ?",
                    (kind, profile_name),
                )
            ]
        finally:
            connection.close()

    def delete(kind, unit_id):
        connection = _connect()
        try:
            with connection:
                connection.execute(
                    "DELETE FROM mesh_units "
                    "WHERE kind = ? AND unit_id = ?",
                    (kind, unit_id),
                )
        finally:
            connection.close()

    return store, fetch, list_units, delete


def _mesh_configuration(db_path, *, stream_emissions=False, delete=False):
    """One generic-lane configuration over the SQLite mesh handlers."""
    store, fetch, list_units, delete_fn = _sqlite_mesh_handlers(db_path)
    configuration = _external_configuration()
    configuration.with_store_handler(store)
    configuration.with_fetch_handler(fetch)
    configuration.with_list_units_handler(list_units)
    if delete:
        configuration.with_delete_handler(delete_fn)
    if stream_emissions:
        configuration.with_stream_emissions(True)
    return configuration


def test_generic_mesh_handlers_carry_checkpoints_via_the_bridge(
        cache_root, tmp_path,
):
    """
    Purpose:
        The legacy bridge: with ONLY the generic quartet attached
        (no legacy checkpoint handlers), flush ships kind="checkpoint"
        rows and the pod-death reload reads them back through the same
        callables - one handler set serves the whole mesh.
    """
    import shutil
    import sqlite3

    db_path = tmp_path / "mesh.sqlite3"
    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _mesh_configuration(db_path)
    )
    book = _dynamic_book()
    spell_id = book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    book.conjure(dynamic=True, name="root")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    connection = sqlite3.connect(str(db_path))
    try:
        kinds = [
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT kind FROM mesh_units"
            )
        ]
    finally:
        connection.close()
    assert "checkpoint" in kinds

    shutil.rmtree(cache_root, ignore_errors=True)
    rebooted = _fresh_boot()
    rebooted.configure_external_persistence_manager(
        _mesh_configuration(db_path)
    )
    outcome = rebooted.reload_profile_from_external("default")
    # "inserted" is the id LIST (insert-if-absent summary), not a count.
    assert len(outcome["inserted"]) >= 1
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert rebooted.get_spell_crystal(spell_id).id == spell_id


def test_formations_ship_remote_and_reload(cache_root, tmp_path):
    """
    Purpose:
        The formation mesh lane: store_formation ships local-then-remote
        (kind="formation", unit_id=name); after pod death the formations
        reload from the DB and restore_formation unfolds one as usual.
    """
    import shutil

    db_path = tmp_path / "mesh.sqlite3"
    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _mesh_configuration(db_path)
    )
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    conduit = book.conjure(dynamic=True, name="root")
    crystallizer.save_formation("mesh_slice", conduit_id=conduit._id)

    store, fetch, list_units, _delete = _sqlite_mesh_handlers(db_path)
    assert "mesh_slice" in list_units("formation", "default")

    shutil.rmtree(cache_root, ignore_errors=True)
    rebooted = _fresh_boot()
    rebooted.configure_external_persistence_manager(
        _mesh_configuration(db_path)
    )
    outcome = rebooted.reload_formations_from_external()
    assert "mesh_slice" in outcome["inserted"]
    report = rebooted.restore_formation("mesh_slice")
    assert report["status"] == "complete"


def test_emission_tap_streams_delta_rows(cache_root, tmp_path):
    """
    Purpose:
        The opt-in tap: with stream_emissions on, every recorded twin
        ships a kind="emission" row carrying {crystal_kind, payload} -
        a live DB mirror of the mesh, fed by the same store callable.
    """
    import json
    import sqlite3

    db_path = tmp_path / "mesh.sqlite3"
    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _mesh_configuration(db_path, stream_emissions=True)
    )
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    book.conjure(dynamic=True, name="root")

    connection = sqlite3.connect(str(db_path))
    try:
        rows = connection.execute(
            "SELECT payload FROM mesh_units WHERE kind = 'emission'"
        ).fetchall()
    finally:
        connection.close()
    assert len(rows) >= 1
    envelopes = [json.loads(row[0]) for row in rows]
    crystal_kinds = {envelope["crystal_kind"] for envelope in envelopes}
    assert any("Crystal" in kind for kind in crystal_kinds)
    # Record versioning: every emission envelope carries the stamp.
    assert all(
        envelope.get("record_version") == "1.0.0"
        for envelope in envelopes
    )


def test_external_retention_trims_oldest_checkpoints(cache_root, tmp_path):
    """
    Purpose:
        Melder-driven remote retention (opt-in delete lane): with more
        remote checkpoints than the cap, apply_external_retention deletes
        the oldest (ULID order) and the survivors are the newest ids.
    """
    db_path = tmp_path / "mesh.sqlite3"
    crystallizer = _activate_crystallizer()
    crystallizer.configure_external_persistence_manager(
        _mesh_configuration(db_path, delete=True)
    )
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    book.conjure(dynamic=True, name="root")

    checkpoint_ids = []
    for _ in range(3):
        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)
        checkpoint_ids.append(checkpoint_id)

    deleted = crystallizer.apply_external_retention(max_checkpoints=2)
    assert deleted == sorted(checkpoint_ids)[:1]

    _store, _fetch, list_units, _delete = _sqlite_mesh_handlers(db_path)
    survivors = list_units("checkpoint", "default")
    assert sorted(survivors) == sorted(checkpoint_ids)[1:]


@pytest.mark.xfail(
    strict=True,
    reason=(
        "OPEN FEATURE CONFLICT - EPIC-2026-08-02-process-wide-spell-id-uniqueness. "
        "graft_runner._bind_selected (graft_runner.py:404) rebinds a LIVE "
        "Existence.unique spell into a host book on ANOTHER frame while the SOURCE "
        "book still holds it. Under process-wide uniqueness that is two spells "
        "wearing one spell_id, which is exactly what the regime forbids. "
        "THE TEST IS NOT WRONG - the graft lane is, and the fix is a design call: "
        "either the graft RELEASES the source claim first (a move, not a copy), or "
        "custody transfer is carved out of the regime explicitly. Marked rather "
        "than deleted because this is real shipped behaviour with real coverage. "
        "STRICT: whichever way it is ruled, this starts passing and the marker "
        "must come off."
    ),
)
def test_index_graft_round_trips_into_a_live_host_book(cache_root):
    """
    Purpose:
        The spell-index graft lane end to end: capture one index's graft
        record from book A, graft it into a LIVE conjured book B on
        ANOTHER frame - the selected member binds ACTIVE into a FRESH
        index (bind creates it; no existing index touched), and the
        overlap rule refuses a graft back into the source frame unless
        skip_resident is passed.
    Contract:
        Report complete with a live index id; the host frame resolves
        the member; the source-frame re-graft refuses by default and
        skips-with-shortfall under skip_resident.
    """
    from melder.aether.spellbook.configuration.spellbook_configuration import (
        SpellbookConfiguration,
    )

    crystallizer = _activate_crystallizer()
    source_book = _dynamic_book()
    spell_id = source_book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    source_book.conjure(dynamic=True, name="graft-source")

    live_spell = source_book.find_spell_by_id(spell_id)
    recorded_index_id = live_spell.spell_index.id
    record = crystallizer.capture_index_graft(recorded_index_id)
    assert record["graft_kind"] == "spell_index"
    assert record["record_version"] == "1.0.0"
    assert spell_id in record["members"]

    # A live host on ANOTHER frame (lazy frames: the book births it).
    host_configuration = SpellbookConfiguration(
        aether_frame="graft-host-frame"
    )
    apply_dynamic_defaults_for_spellbook_configuration(host_configuration)
    host_configuration.set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    host_configuration.finalize()
    host_book = Spellbook(
        aetheric_frame="graft-host-frame",
        configuration=host_configuration,
    )
    host_book.conjure(dynamic=True, name="graft-host")

    report = crystallizer.graft_index(record, host_book)
    assert report["status"] == "complete"
    assert report["members_bound"] == 1
    assert report["live_index_id"] is not None
    assert report["live_index_id"] != recorded_index_id
    grafted = host_book.find_spell_by_id(spell_id)
    assert grafted is not None

    # Overlap rule: the SOURCE frame already holds the member - refuse
    # by default, skip-with-shortfall when asked.
    second_record = crystallizer.capture_index_graft(recorded_index_id)
    with pytest.raises(RuntimeError, match="already resident"):
        crystallizer.graft_index(second_record, source_book)
    third_record = crystallizer.capture_index_graft(recorded_index_id)
    try:
        skipped = crystallizer.graft_index(
            third_record, source_book, skip_resident=True
        )
        raised = None
    except ValueError as exc:
        # Skipping the only (selected) member leaves no anchor - the
        # structural refusal is the honest outcome for a single-member
        # graft; either surface is acceptable evidence of the skip lane.
        raised = str(exc)
    if raised is None:
        assert skipped["skipped_resident"] == [spell_id]
    else:
        assert "no graftable SELECTED member" in raised


@pytest.mark.xfail(
    strict=True,
    reason=(
        "OPEN FEATURE CONFLICT - EPIC-2026-08-02-process-wide-spell-id-uniqueness. "
        "graft_runner._bind_selected (graft_runner.py:404) rebinds a LIVE "
        "Existence.unique spell into a host book on ANOTHER frame while the SOURCE "
        "book still holds it. Under process-wide uniqueness that is two spells "
        "wearing one spell_id, which is exactly what the regime forbids. "
        "THE TEST IS NOT WRONG - the graft lane is, and the fix is a design call: "
        "either the graft RELEASES the source claim first (a move, not a copy), or "
        "custody transfer is carved out of the regime explicitly. Marked rather "
        "than deleted because this is real shipped behaviour with real coverage. "
        "STRICT: whichever way it is ruled, this starts passing and the marker "
        "must come off."
    ),
)
def test_multi_member_index_graft_parks_the_staged_members(cache_root):
    """
    Purpose:
        The graft lane's full membership arc: an index carrying an ACTIVE
        selected member AND a PARKED member (bind_inactive) grafts into a
        live host book - the selected member binds active into the fresh
        index and the parked member parks onto it, custody states intact.
    Contract:
        Capture carries both members (parked one custody_state
        "inactive"); the report shows members_bound==1 AND
        members_parked==1; the host's fresh index holds BOTH spell ids
        with the recorded selection.
    """
    from melder.aether.spellbook.configuration.spellbook_configuration import (
        SpellbookConfiguration,
    )

    crystallizer = _activate_crystallizer()
    source_book = _dynamic_book()
    active_id = source_book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    source_conduit = source_book.conjure(dynamic=True, name="graft-multi")
    active_spell = source_book._spells_by_id[active_id]
    staged_id = source_conduit.bind_inactive(
        spell=RestoreBeta,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )

    record = crystallizer.capture_index_graft(active_spell.spell_index.id)
    assert set(record["members"]) == {active_id, staged_id}
    assert record["members"][staged_id]["custody_state"] == "inactive"
    assert record["index_payload"]["selected_spell_id"] == active_id

    host_configuration = SpellbookConfiguration(
        aether_frame="graft-multi-host-frame"
    )
    apply_dynamic_defaults_for_spellbook_configuration(host_configuration)
    host_configuration.set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    host_configuration.finalize()
    host_book = Spellbook(
        aetheric_frame="graft-multi-host-frame",
        configuration=host_configuration,
    )
    host_book.conjure(dynamic=True, name="graft-multi-host")

    report = crystallizer.graft_index(record, host_book)
    assert report["status"] == "complete"
    assert report["members_bound"] == 1
    assert report["members_parked"] == 1
    assert report["shortfalls"] == []

    grafted_anchor = host_book.find_spell_by_id(active_id)
    assert grafted_anchor is not None
    live_index = grafted_anchor.spell_index
    assert live_index.selected_spell_id == active_id
    assert live_index.has_spell(active_id)
    assert live_index.has_spell(staged_id)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "OPEN FEATURE CONFLICT - EPIC-2026-08-02-process-wide-spell-id-uniqueness. "
        "graft_runner._bind_selected (graft_runner.py:404) rebinds a LIVE "
        "Existence.unique spell into a host book on ANOTHER frame while the SOURCE "
        "book still holds it. Under process-wide uniqueness that is two spells "
        "wearing one spell_id, which is exactly what the regime forbids. "
        "THE TEST IS NOT WRONG - the graft lane is, and the fix is a design call: "
        "either the graft RELEASES the source claim first (a move, not a copy), or "
        "custody transfer is carved out of the regime explicitly. Marked rather "
        "than deleted because this is real shipped behaviour with real coverage. "
        "STRICT: whichever way it is ruled, this starts passing and the marker "
        "must come off."
    ),
)
def test_merge_graft_grows_an_existing_index_and_adopts_selection(
        cache_root,
):
    """
    Purpose:
        The merge lane end to end (finishing slice 3): a captured index
        (active + parked member) merges into a host book's EXISTING
        live index through public verbs only - no fresh index minted,
        the target grows by both members, and the recorded selection is
        adopted via the public notch.
    Contract:
        Report shows merged_into_existing True, members_parked==2,
        members_bound==0, selection_adopted True, live_index_id == the
        TARGET's id; the target index holds its own original member
        PLUS both grafted ids with the recorded selection active; the
        grafted members' live index IS the target (no fresh index);
        adopt_recorded_selection without a merge target refuses
        (ValueError) - fresh-lane semantics stay untouched.
    """
    from melder.aether.spellbook.configuration.spellbook_configuration import (
        SpellbookConfiguration,
    )

    crystallizer = _activate_crystallizer()
    source_book = _dynamic_book()
    active_id = source_book.bind(
        spell=RestoreAlpha, existence=Existence.unique, permissions="create"
    )
    source_conduit = source_book.conjure(dynamic=True, name="graft-merge-src")
    active_spell = source_book._spells_by_id[active_id]
    staged_id = source_conduit.bind_inactive(
        spell=RestoreBeta,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    record = crystallizer.capture_index_graft(active_spell.spell_index.id)

    host_configuration = SpellbookConfiguration(
        aether_frame="graft-merge-host-frame"
    )
    apply_dynamic_defaults_for_spellbook_configuration(host_configuration)
    host_configuration.set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    host_configuration.finalize()
    host_book = Spellbook(
        aetheric_frame="graft-merge-host-frame",
        configuration=host_configuration,
    )
    resident_id = host_book.bind(
        spell=RestoreGamma, existence=Existence.unique, permissions="create"
    )
    host_book.conjure(dynamic=True, name="graft-merge-host")
    target_index = host_book.find_spell_by_id(resident_id).spell_index

    report = crystallizer.graft_index(
        record,
        host_book,
        merge_into_index=target_index,
        adopt_recorded_selection=True,
    )
    assert report["status"] == "complete"
    assert report["merged_into_existing"] is True
    assert report["members_bound"] == 0
    assert report["members_parked"] == 2
    assert report["selection_adopted"] is True
    assert report["live_index_id"] == target_index.id
    assert report["shortfalls"] == []

    # The target GREW (public-verb growth, no fresh index anywhere):
    assert target_index.has_spell(resident_id)
    assert target_index.has_spell(active_id)
    assert target_index.has_spell(staged_id)
    assert target_index.selected_spell_id == active_id
    merged_member = host_book.find_spell_by_id(active_id)
    assert merged_member is not None
    assert merged_member.spell_index.id == target_index.id

    # Fresh-lane semantics untouched: adoption without a merge target
    # is a contract refusal, not a silent fresh-index graft.
    with pytest.raises(ValueError, match="merge_into_index"):
        crystallizer.graft_index(
            record, host_book, adopt_recorded_selection=True
        )


def test_restored_link_maps_recorded_contract_ulid_to_fresh_contract(
        cache_root,
):
    """
    Purpose:
        Prove the S1 link-identity law: every rebuilt link edge maps its
        RECORDED contract ULID (the identity the ward minted when the
        original link was established) onto the FRESH contract ULID the
        rebuilt ward mints during replay.
    Contract:
        - The recorded contract id appears as an identity-map key.
        - The mapped value is a fresh 26-character ULID that differs from
          the recorded id (never-rehydrate-ULIDs).
        - Existing link-lane behavior is untouched: one link built, both
          conduit endpoints identity-mapped.
    Returns:
        None.
    Raises:
        AssertionError: If the link identity mapping diverges.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    # The recorded link identity IS the contract the initiating ward
    # minted at link time (ward truth: target conduit id -> contract id).
    recorded_contract_id = (
        conduit_a._conduit_ward._initiated_index[conduit_b._id]
    )
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["link"] == 1
    assert conduit_a._id in report["identity_map"]
    assert conduit_b._id in report["identity_map"]
    # S1 law: recorded contract ULID -> fresh contract ULID.
    assert recorded_contract_id in report["identity_map"]
    fresh_contract_id = report["identity_map"][recorded_contract_id]
    assert fresh_contract_id != recorded_contract_id
    assert isinstance(fresh_contract_id, str)
    assert len(fresh_contract_id) == 26


def test_legacy_chain_link_without_contract_twin_restores_without_mapping(
        cache_root,
):
    """
    Purpose:
        Prove the S1 legacy tolerance: a chain whose conduit twin carries a
        link edge but whose contract twin is ABSENT (pre-contract-crystal
        chains / evicted twins) still rebuilds the link cleanly - it simply
        gains no contract identity mapping and files no shortfall for it.
    Contract:
        - One link built; status complete; link lane shortfall-free.
        - The identity map holds exactly the recorded book/conduit ids
          (books map first, conduits second); no contract key appears.
    Returns:
        None.
    Raises:
        AssertionError: If the legacy lane maps, fails, or under-builds.
    """
    _activate_crystallizer()
    window = {
        "journal": [
            [1, "spellbook", "book-x"],
            [2, "spellbook", "book-z"],
            [3, "spell_crystal", "sha-x"],
            [4, "spell_crystal", "sha-z"],
            [5, "conduit", "cond-x"],
            [6, "conduit", "cond-z"],
        ],
        "payloads": {
            "spellbook": {
                "book-x": {
                    "spellbook_id": "book-x",
                    "frame_name": "default",
                    "configuration_payload": {
                        "system_state": "dynamic",
                        "ai_native_enabled": True,
                        "rift_enabled": True,
                        "phase_scheduler_workers_per_spellbook": 1,
                    },
                    "hook_names": [],
                    "bind_order": ["sha-x"],
                },
                "book-z": {
                    "spellbook_id": "book-z",
                    "frame_name": "default",
                    "configuration_payload": {
                        "system_state": "dynamic",
                        "ai_native_enabled": True,
                        "rift_enabled": True,
                        "phase_scheduler_workers_per_spellbook": 1,
                    },
                    "hook_names": [],
                    "bind_order": ["sha-z"],
                },
            },
            "conduit": {
                "cond-x": {
                    "conduit_id": "cond-x",
                    "spellbook_id": "book-x",
                    "conduit_name": "legacy-alpha",
                    "policy_name": "default",
                    "dynamic": True,
                    # Legacy edge WITHOUT a matching contract twin below.
                    "link_targets": ["cond-z"],
                },
                "cond-z": {
                    "conduit_id": "cond-z",
                    "spellbook_id": "book-z",
                    "conduit_name": "legacy-beta",
                    "policy_name": "default",
                    "dynamic": True,
                    "link_targets": [],
                },
            },
            "spell_crystal": {
                "sha-x": {
                    "id": "sha-x",
                    "spellbook_id": "book-x",
                    "spell_name": "RestoreAlpha",
                    "binding_name": None,
                    "spellframe_name": None,
                    "existence_name": "unique",
                    "permissions_name": "create",
                    "rebindability": "hydratable",
                    "root_module_kind": "user_source",
                    "root_module_name": (
                        "tests.integration.melder.crystallizer."
                        "test_crystallizer_restore_integration"
                    ),
                    "root_target_qualname": "RestoreAlpha",
                    "root_target_kind": "class",
                },
                "sha-z": {
                    "id": "sha-z",
                    "spellbook_id": "book-z",
                    "spell_name": "RestoreGamma",
                    "binding_name": None,
                    "spellframe_name": None,
                    "existence_name": "unique",
                    "permissions_name": "create",
                    "rebindability": "hydratable",
                    "root_module_kind": "user_source",
                    "root_module_name": (
                        "tests.integration.melder.crystallizer."
                        "test_crystallizer_restore_integration"
                    ),
                    "root_target_qualname": "RestoreGamma",
                    "root_target_kind": "class",
                },
            },
        },
    }
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["01LEGACYLINKTEST00000000"],
        chain=[window],
    )
    report = engine.restore()
    payload = report.describe()
    engine.cleanup()

    assert payload["status"] == "complete"
    assert payload["built_counts"]["link"] == 1
    # Link-lane honesty unchanged: no shortfall rows for the legacy edge.
    assert not [
        row for row in payload["shortfalls"]
        if "link" in str(row.get("reason", ""))
    ]
    # No contract twin -> no contract mapping; the map holds exactly the
    # recorded book and conduit identities.
    assert set(payload["identity_map"].keys()) == {
        "book-x", "book-z", "cond-x", "cond-z"
    }


def test_parallel_and_sequential_drivers_restore_identical_outcomes(
        cache_root,
):
    """
    Purpose:
        The S4 parity law: the graph-planned parallel driver restores the
        SAME sealed world to the same outcomes as the sequential baseline.
    Contract:
        - Identical built_counts, identical sorted shortfalls, identical
          identity-map KEY set (values are fresh ULIDs by law).
        - The parallel report carries the plan summary; sequential's is
          empty. Load authority is fully released after both loads.
    Returns:
        None.
    Raises:
        AssertionError: If the drivers diverge on any outcome surface.
    """
    def build_world_and_seal():
        crystallizer = _activate_crystallizer()
        book_a = _dynamic_book()
        granted_id = book_a.bind(
            spell=RestoreAlpha,
            existence=Existence.unique,
            permissions="create",
        )
        conduit_a = book_a.conjure(dynamic=True, name="alpha")
        book_b = _dynamic_book()
        book_b.bind(
            spell=RestoreGamma,
            existence=Existence.unique,
            permissions="create",
        )
        conduit_b = book_b.conjure(dynamic=True, name="beta")
        assert conduit_a.link(conduit_b) is True
        with conduit_b.transaction("link", conduits=[conduit_a, conduit_b]):
            conduit_b.add_spell_to_contract(
                spell_id=granted_id,
                conduit=conduit_a,
                permissions="create",
            )
        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)
        return checkpoint_id

    def fresh_boot_with_driver(parallel_enabled):
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        configuration = CrystallizerConfiguration().with_defaults()
        configuration.set_property(
            "restore_parallel_enabled", parallel_enabled
        )
        configuration.activate()
        crystallizer = Crystallizer()
        crystallizer.activate(configuration)
        return crystallizer

    checkpoint_id = build_world_and_seal()

    sequential_boot = fresh_boot_with_driver(False)
    sequential_boot.reload_cached_checkpoint(checkpoint_id)
    sequential_report = sequential_boot.load_checkpoint(checkpoint_id)

    parallel_boot = fresh_boot_with_driver(True)
    parallel_boot.reload_cached_checkpoint(checkpoint_id)
    parallel_report = parallel_boot.load_checkpoint(checkpoint_id)

    assert sequential_report["status"] == "complete"
    assert parallel_report["status"] == "complete"
    assert (
        parallel_report["built_counts"]
        == sequential_report["built_counts"]
    )
    def shortfall_key(row):
        return (row["kind"], row["key"], row["reason"])
    assert (
        sorted(parallel_report["shortfalls"], key=shortfall_key)
        == sorted(sequential_report["shortfalls"], key=shortfall_key)
    )
    assert (
        set(parallel_report["identity_map"])
        == set(sequential_report["identity_map"])
    )
    assert sequential_report["plan"] == {}
    assert parallel_report["plan"]["level_count"] >= 2
    assert sum(parallel_report["plan"]["nodes_per_level"]) >= 4
    # The load span released: no residual authority bars root transactions.
    assert Aether()._load_gate.is_held() is False


def test_parallel_driver_failure_tears_the_partial_world_down(cache_root):
    """
    Purpose:
        The S4 chaos law: a poisoned unit inside a level fails the run,
        the failed LEVEL is named, and the all-or-nothing teardown leaves
        zero leaked units - identical law to the sequential driver.
    Contract:
        - RuntimeError names a level_N stage; the frame holds no leftover
          conduits after teardown; the poisoned world never half-exists.
    Returns:
        None.
    Raises:
        AssertionError: If a partial world survives the failure.
    """
    from melder.utilities.synchronization.phase_scheduler import (
        PhaseScheduler,
    )

    _activate_crystallizer()
    window = {
        "journal": [
            [1, "spellbook", "book-p"],
            [2, "spellbook", "book-q"],
            [3, "spell_crystal", "sha-p"],
            [4, "conduit", "cond-p"],
            [5, "conduit", "cond-q"],
        ],
        "payloads": {
            "spellbook": {
                "book-p": {
                    "spellbook_id": "book-p",
                    "frame_name": "default",
                    "configuration_payload": {
                        "system_state": "dynamic",
                        "ai_native_enabled": True,
                        "rift_enabled": True,
                        "phase_scheduler_workers_per_spellbook": 1,
                    },
                    "hook_names": [],
                    "bind_order": ["sha-p"],
                },
                "book-q": {
                    "spellbook_id": "book-q",
                    "frame_name": "default",
                    "configuration_payload": {
                        "system_state": "dynamic",
                        "ai_native_enabled": True,
                        "rift_enabled": True,
                        "phase_scheduler_workers_per_spellbook": 1,
                    },
                    "hook_names": [],
                    "bind_order": [],
                },
            },
            "conduit": {
                "cond-p": {
                    "conduit_id": "cond-p",
                    "spellbook_id": "book-p",
                    "conduit_name": "healthy",
                    "policy_name": "default",
                    "dynamic": True,
                    "link_targets": [],
                },
                "cond-q": {
                    "conduit_id": "cond-q",
                    "spellbook_id": "book-q",
                    "conduit_name": "poisoned",
                    "policy_name": "no_such_policy_anywhere",
                    "dynamic": True,
                    "link_targets": [],
                },
            },
            "spell_crystal": {
                "sha-p": {
                    "id": "sha-p",
                    "spellbook_id": "book-p",
                    "spell_name": "RestoreAlpha",
                    "binding_name": None,
                    "spellframe_name": None,
                    "existence_name": "unique",
                    "permissions_name": "create",
                    "rebindability": "hydratable",
                    "root_module_kind": "user_source",
                    "root_module_name": (
                        "tests.integration.melder.crystallizer."
                        "test_crystallizer_restore_integration"
                    ),
                    "root_target_qualname": "RestoreAlpha",
                    "root_target_kind": "class",
                },
            },
        },
    }
    scheduler = PhaseScheduler(
        spellbook=None,
        configuration=None,
        worker_count=2,
        barrier_timeout_ms=60000,
    )
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["01CHAOSLEVELTEST00000000"],
        chain=[window],
        scheduler=scheduler,
    )
    try:
        with pytest.raises(RuntimeError) as raised:
            engine.restore()
    finally:
        engine.cleanup()
        scheduler.cleanup()
    assert "level_" in str(raised.value)
    frame = Aether()._aetheric_frames["default"]
    assert frame._conduits == {}


def test_roots_only_configuration_parallel_restores_a_sealed_world(
        cache_root,
):
    """
    Purpose:
        End-to-end REOPEN regression (2026-07-19): the red run's fixture
        shape - a configuration that never set the restore knobs - must
        boot, activate, and PARALLEL-restore a sealed multi-entity world
        purely on the schema defaults (True/4/60000). The old activate()
        KeyError'd before any load could start.
    Contract:
        - Roots-only configuration activates the crystallizer.
        - load_checkpoint completes under the default parallel driver:
          status complete, plan summary present (level_count >= 2), books
          and the link edge rebuilt, load authority fully released.
    Returns:
        None.
    Raises:
        AssertionError: If the defaults-only lane fails anywhere between
            activation and the restored world.
    """
    def build_world_and_seal():
        crystallizer = _activate_crystallizer()
        book_a = _dynamic_book()
        book_a.bind(
            spell=RestoreAlpha,
            existence=Existence.unique,
            permissions="create",
        )
        conduit_a = book_a.conjure(dynamic=True, name="alpha")
        book_b = _dynamic_book()
        book_b.bind(
            spell=RestoreGamma,
            existence=Existence.unique,
            permissions="create",
        )
        conduit_b = book_b.conjure(dynamic=True, name="beta")
        assert conduit_a.link(conduit_b) is True
        checkpoint_id = crystallizer.create_checkpoint()
        crystallizer.flush_checkpoint(checkpoint_id)
        return checkpoint_id

    checkpoint_id = build_world_and_seal()

    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    # The red-run shape: roots only, no with_defaults(), no restore knobs.
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    ).activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)

    crystallizer.reload_cached_checkpoint(checkpoint_id)
    report = crystallizer.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    # Schema-default driver selection: parallel ran, so the plan summary
    # is populated (sequential runs carry an empty plan by contract).
    assert report["plan"]["level_count"] >= 2
    assert sum(report["plan"]["nodes_per_level"]) >= 4
    assert report["built_counts"].get("spellbook", 0) == 2
    assert report["built_counts"].get("link", 0) == 1
    # The load span released: no residual authority bars root work.
    assert Aether()._load_gate.is_held() is False


def test_unknown_checkpoint_refusal_releases_load_authority(cache_root):
    """
    Purpose:
        Safety wave 2 (2026-07-19): the authority finally-law on the
        refusal path - an unknown checkpoint id raises INSIDE the load
        span (plan minting), and the LoadGate must still release so the
        world is not bricked by a typo'd id.
    Contract:
        - load_checkpoint(unknown) raises KeyError (teach-grade).
        - The gate is released afterwards and a normal root transaction
          (bind + conjure) proceeds unbarred.
    Returns:
        None.
    Raises:
        AssertionError: If refusal leaks held authority.
    """
    crystallizer = _activate_crystallizer()
    with pytest.raises(KeyError):
        crystallizer.load_checkpoint("01UNKNOWNCHECKPOINT0000000")
    assert Aether()._load_gate.is_held() is False
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="post-refusal")
    assert conduit is not None


def test_reload_over_live_world_fails_atomically_and_releases_authority(
        cache_root,
):
    """
    Purpose:
        Safety wave 2: the all-or-nothing law when a PARALLEL load fails
        over a LIVE world. World-scope loads skip host preflight by
        contract (load_admission._preflight_host), so replaying a
        checkpoint onto its own restored world fails mid-replay on the
        named-conduit collision - the failing run must tear down ONLY its
        own partial units, release authority, and leave the first restored
        world standing.
    Contract:
        - First load completes (parallel driver, plan present).
        - Second load of the SAME checkpoint raises RuntimeError (stage
          failure, cause chained).
        - Gate released; the restored world's named conduits are still
          registered afterwards (public cloud probe).
    Returns:
        None.
    Raises:
        AssertionError: If the failed reload bricks authority or damages
            the standing world.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    crystallizer = _fresh_boot()
    crystallizer.reload_cached_checkpoint(checkpoint_id)
    first = crystallizer.load_checkpoint(checkpoint_id)
    assert first["status"] == "complete"
    assert first["plan"]["level_count"] >= 2

    with pytest.raises(RuntimeError):
        crystallizer.load_checkpoint(checkpoint_id)

    assert Aether()._load_gate.is_held() is False
    cloud = Aether()._aetheric_frames["default"].conduit_cloud
    assert cloud.has_conduit_name("alpha") is True
    assert cloud.has_conduit_name("beta") is True


def test_single_worker_parallel_restore_completes_without_deadlock(
        cache_root,
):
    """
    Purpose:
        Safety wave 2: the degenerate-pool law - restore_scheduler_workers
        = 1 must still complete a multi-level parallel restore (one worker
        drains every level behind its barrier; the cohort of one enrolled
        worker passes the gate).
    Contract:
        Restore completes with the plan summary populated and both books
        rebuilt; authority fully released.
    Returns:
        None.
    Raises:
        AssertionError: If the width-1 pool deadlocks or diverges.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_scheduler_workers", 1)
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)

    crystallizer.reload_cached_checkpoint(checkpoint_id)
    report = crystallizer.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert report["plan"]["level_count"] >= 2
    assert report["built_counts"].get("spellbook", 0) == 2
    assert report["built_counts"].get("link", 0) == 1
    assert Aether()._load_gate.is_held() is False


def _seal_linked_world():
    """
    Build the house two-book linked world and seal it.

    Returns:
        str: The flushed checkpoint id.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    return checkpoint_id


def test_restored_world_recheckpoints_and_restores_again(cache_root):
    """
    Purpose:
        Wave 3: the re-emission covenant across GENERATIONS - a restored
        world re-records itself, so its own checkpoint must restore on a
        third boot with the same structure (record -> world -> record
        lineage is closed).
    Contract:
        Generation-2 checkpoint (sealed from the restored world) rebuilds
        2 spellbooks and 1 link on boot 3, matching generation 1.
    Returns:
        None.
    Raises:
        AssertionError: If the second generation loses structure.
    """
    checkpoint_one = _seal_linked_world()

    generation_two = _fresh_boot()
    generation_two.reload_cached_checkpoint(checkpoint_one)
    first_report = generation_two.load_checkpoint(checkpoint_one)
    assert first_report["status"] == "complete"
    checkpoint_two = generation_two.create_checkpoint()
    generation_two.flush_checkpoint(checkpoint_two)

    generation_three = _fresh_boot()
    generation_three.reload_cached_checkpoint(checkpoint_two)
    second_report = generation_three.load_checkpoint(checkpoint_two)
    assert second_report["status"] == "complete"
    assert second_report["built_counts"].get("spellbook", 0) == 2
    assert second_report["built_counts"].get("link", 0) == 1
    assert (
        second_report["built_counts"].get("spellbook", 0)
        == first_report["built_counts"].get("spellbook", 0)
    )


def test_cluster_world_parallel_restore_rebuilds_membership(cache_root):
    """
    Purpose:
        Wave 3: the cluster vocabulary under the parallel driver - a
        recorded cluster with two member conduits rebuilds as one cluster
        unit plus per-member joins in a plan level behind the books.
    Contract:
        built_counts cluster == 1 and cluster_member == 2; plan present.
    Returns:
        None.
    Raises:
        AssertionError: If cluster topology loses members on restore.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    cloud = Aether()._aetheric_frames["default"].conduit_cloud
    cloud.create_cluster("workers")
    cloud.add_conduit_to_cluster(conduit_a, "workers")
    cloud.add_conduit_to_cluster(conduit_b, "workers")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert report["plan"]["level_count"] >= 3
    assert report["built_counts"].get("cluster", 0) == 1
    assert report["built_counts"].get("cluster_member", 0) == 2


def test_staged_member_world_restores_identically_on_both_drivers(
        cache_root,
):
    """
    Purpose:
        Wave 3: staged-member parity - a world with a parked member on
        the active index restores to the same staged/active shape under
        the sequential AND parallel drivers (no notch fabricated by
        either).
    Contract:
        Both drivers: spell_active == 1, spell_staged == 1, no
        selection_notch; the parallel report additionally carries a plan.
    Returns:
        None.
    Raises:
        AssertionError: If the drivers diverge on staged custody.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    active_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="root")
    active_spell = book._spells_by_id[active_id]
    conduit.bind_inactive(
        spell=RestoreBeta,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    reports = {}
    for parallel_enabled in (False, True):
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        configuration = CrystallizerConfiguration().with_defaults()
        configuration.set_property(
            "restore_parallel_enabled", parallel_enabled
        )
        configuration.activate()
        crystallizer = Crystallizer()
        crystallizer.activate(configuration)
        crystallizer.reload_cached_checkpoint(checkpoint_id)
        reports[parallel_enabled] = crystallizer.load_checkpoint(
            checkpoint_id
        )

    for parallel_enabled, report in reports.items():
        assert report["status"] == "complete"
        assert report["built_counts"].get("spell_active", 0) == 1
        assert report["built_counts"].get("spell_staged", 0) == 1
        assert report["built_counts"].get("selection_notch") is None
    assert reports[False]["plan"] == {}
    assert reports[True]["plan"]["level_count"] >= 2


def test_recorded_policy_twin_drives_driver_selection_on_reload(
        cache_root,
):
    """
    Purpose:
        Wave 3: the record -> policy -> driver chain end to end - a world
        sealed under a sequential-polarity policy carries that truth in
        its own crystallizer twin; a boot that reloads policy FROM THE
        RECORD (the documented cache-boot lane) must select the
        sequential driver.
    Contract:
        The sealed window's crystallizer payload reloads via
        load_recorded_dictionary; activation wires no pool; the load runs
        sequential (empty plan) and completes.
    Returns:
        None.
    Raises:
        AssertionError: If recorded polarity is lost anywhere in the
            chain.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_parallel_enabled", False)
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="solo")
    checkpoint_id = crystallizer.create_checkpoint()
    window = crystallizer.checkpoint_replay_data(checkpoint_id)
    recorded_policy = dict(
        next(iter(window["payloads"]["crystallizer"].values()))
    )["configuration_payload"]
    assert recorded_policy["restore_parallel_enabled"] is False
    crystallizer.flush_checkpoint(checkpoint_id)

    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    rebooted_configuration = CrystallizerConfiguration()
    outcome = rebooted_configuration.load_recorded_dictionary(
        dict(recorded_policy)
    )
    assert outcome["rejected"] == []
    rebooted_configuration.activate()
    rebooted = Crystallizer()
    rebooted.activate(rebooted_configuration)
    assert (
        rebooted._crystal_loader_system._restore_scheduler is None
    )
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    assert report["plan"] == {}


def test_formation_restore_under_the_pool_carries_a_plan(cache_root):
    """
    Purpose:
        Wave 3: the scoped-restore lane under the parallel driver - a
        conduit-scope formation composes through the SAME plan/level
        machinery, so its report carries a plan summary beside the
        scope-aware clean admission.
    Contract:
        restore_formation on a defaults boot (parallel driver) completes
        with plan level_count >= 1 and admission scope "conduit".
    Returns:
        None.
    Raises:
        AssertionError: If the scoped lane bypasses the plan machinery.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="keeper")
    crystallizer.save_formation(
        "pooled-formation", conduit_id=conduit._id
    )

    rebooted = _fresh_boot()
    report = rebooted.restore_formation("pooled-formation")
    assert report["status"] == "complete"
    assert report["plan"]["level_count"] >= 1
    admission = dict(report["admission"])
    assert admission["scope"] == "conduit"
    assert admission["verdict"] == "clean"


def test_skip_existing_formation_composes_over_a_live_world(cache_root):
    """
    Purpose:
        Wave 3: the S1 skip lanes under the parallel driver - composing a
        formation whose conduit NAME is already live must downgrade the
        host collision and build UNNAMED with the honesty shortfall,
        never refuse or damage the resident conduit.
    Contract:
        - The live world owns a DIFFERENT spell under the colliding name
          ("keeper" carries RestoreGamma), so ONLY the conduit name
          collides: content-stable spell SHAs never join the skip
          vocabulary, and re-composing a formation whose spells are
          already resident refuses by design (Aether spell-id collision).
        - Compose with skip_existing=True completes; shortfall
          "conduit_name_taken_built_unnamed" reported; the resident named
          conduit survives untouched as the SAME live object.
    Returns:
        None.
    Raises:
        AssertionError: If the skip lane refuses or drops honesty.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="keeper")
    crystallizer.save_formation(
        "skip-formation", conduit_id=conduit._id
    )

    rebooted = _fresh_boot()
    resident_book = _dynamic_book()
    resident_book.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    resident = resident_book.conjure(dynamic=True, name="keeper")
    resident_id = resident._id

    composed = rebooted.restore_formation(
        "skip-formation", skip_existing=True
    )
    assert composed["status"] == "complete"
    reasons = {row["reason"] for row in composed["shortfalls"]}
    assert "conduit_name_taken_built_unnamed" in reasons
    assert composed["built_counts"]["spellbook"] == 1
    assert composed["built_counts"]["conduit"] == 1
    cloud = Aether()._aetheric_frames["default"].conduit_cloud
    assert cloud.has_conduit_name("keeper") is True
    survivor = cloud.get_conduit("keeper")
    assert survivor._id == resident_id
    assert survivor.cleaned is False


def test_wide_pool_chaos_tears_down_three_book_world(cache_root):
    """
    Purpose:
        Wave 3: the chaos law at width 4 over three books - one poisoned
        conduit policy fails its level while healthy siblings build
        concurrently, and the all-or-nothing teardown still leaves zero
        survivors.
    Contract:
        RuntimeError names a level_N stage; the frame holds no conduits;
        the report reads failed with the level stage.
    Returns:
        None.
    Raises:
        AssertionError: If a sibling unit survives the poisoned level.
    """
    from melder.utilities.synchronization.phase_scheduler import (
        PhaseScheduler,
    )

    _activate_crystallizer()

    def book_payload(book_id):
        return {
            "spellbook_id": book_id,
            "frame_name": "default",
            "configuration_payload": {
                "system_state": "dynamic",
                "ai_native_enabled": True,
                "rift_enabled": True,
                "phase_scheduler_workers_per_spellbook": 1,
            },
            "hook_names": [],
            "bind_order": [],
        }

    window = {
        "journal": [
            [1, "spellbook", "book-1"],
            [2, "spellbook", "book-2"],
            [3, "spellbook", "book-3"],
            [4, "conduit", "cond-1"],
            [5, "conduit", "cond-2"],
            [6, "conduit", "cond-3"],
        ],
        "payloads": {
            "spellbook": {
                "book-1": book_payload("book-1"),
                "book-2": book_payload("book-2"),
                "book-3": book_payload("book-3"),
            },
            "conduit": {
                "cond-1": {
                    "conduit_id": "cond-1",
                    "spellbook_id": "book-1",
                    "conduit_name": "healthy-one",
                    "policy_name": "default",
                    "dynamic": True,
                    "link_targets": [],
                },
                "cond-2": {
                    "conduit_id": "cond-2",
                    "spellbook_id": "book-2",
                    "conduit_name": "healthy-two",
                    "policy_name": "default",
                    "dynamic": True,
                    "link_targets": [],
                },
                "cond-3": {
                    "conduit_id": "cond-3",
                    "spellbook_id": "book-3",
                    "conduit_name": "poisoned",
                    "policy_name": "no_such_policy_anywhere",
                    "dynamic": True,
                    "link_targets": [],
                },
            },
        },
    }
    scheduler = PhaseScheduler(
        spellbook=None,
        configuration=None,
        worker_count=4,
        barrier_timeout_ms=60000,
    )
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["01CHAOSWIDEPOOL000000000"],
        chain=[window],
        scheduler=scheduler,
    )
    try:
        with pytest.raises(RuntimeError) as raised:
            engine.restore()
        report_payload = engine._report.describe()
    finally:
        engine.cleanup()
        scheduler.cleanup()
    assert "level_" in str(raised.value)
    assert report_payload["status"] == "failed"
    assert str(report_payload["failed_stage"]).startswith("level_")
    frame = Aether()._aetheric_frames["default"]
    assert frame._conduits == {}


def test_restored_borrower_melds_the_granted_spell(cache_root):
    """
    Purpose:
        Wave 3: the restored world must WORK, not just count - after a
        parallel restore of a linked world with a contract grant, the
        borrower conduit (found through the identity map) melds the
        granted spell into a live instance.
    Contract:
        The recorded borrower id translates to a fresh conduit whose
        meld(spell=RestoreAlpha) returns a RestoreAlpha instance.
    Returns:
        None.
    Raises:
        AssertionError: If the rebuilt grant cannot resolve.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    granted_id = book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    with conduit_b.transaction("link", conduits=[conduit_a, conduit_b]):
        conduit_b.add_spell_to_contract(
            spell_id=granted_id,
            conduit=conduit_a,
            permissions="create",
        )
    recorded_borrower_id = conduit_a._id
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    fresh_borrower_id = report["identity_map"][recorded_borrower_id]
    cloud = Aether()._aetheric_frames["default"].conduit_cloud
    borrower = cloud.get_conduit_by_id(fresh_borrower_id)
    instance = borrower.meld(spell=RestoreAlpha)
    assert isinstance(instance, RestoreAlpha)


def test_identity_map_covers_every_recorded_structural_id(cache_root):
    """
    Purpose:
        Wave 3: identity-translation completeness - every structural
        identity captured pre-seal (books, conduits, the link's contract
        ULID) must appear as an identity-map KEY after a parallel
        restore, and every mapped value must be a fresh identity.
    Contract:
        Recorded ids are all keys; no recorded id maps to itself
        (never-rehydrate-ULIDs).
    Returns:
        None.
    Raises:
        AssertionError: If any structural identity is left untranslated.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    recorded_ids = {
        book_a._id, book_b._id, conduit_a._id, conduit_b._id,
        str(conduit_a._conduit_ward._initiated_index[conduit_b._id]),
    }
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    identity_map = dict(report["identity_map"])
    missing = recorded_ids - set(identity_map)
    assert missing == set()
    for recorded_id in recorded_ids:
        assert identity_map[recorded_id] != recorded_id


def test_full_vocabulary_world_restores_identically_on_both_drivers(
        cache_root,
):
    """
    Purpose:
        Wave 3: the superset parity arc - link + cluster + contract grant
        + staged member in ONE world; the sequential and parallel drivers
        must agree on every outcome surface at full vocabulary width.
    Contract:
        Identical built_counts, identical sorted shortfalls, identical
        identity-map key sets; plan populated only on parallel.
    Returns:
        None.
    Raises:
        AssertionError: If any entity family diverges between drivers.
    """
    crystallizer = _activate_crystallizer()
    book_a = _dynamic_book()
    granted_id = book_a.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(dynamic=True, name="alpha")
    active_spell = book_a._spells_by_id[granted_id]
    conduit_a.bind_inactive(
        spell=RestoreBeta,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    book_b = _dynamic_book()
    book_b.bind(
        spell=RestoreGamma,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_b = book_b.conjure(dynamic=True, name="beta")
    assert conduit_a.link(conduit_b) is True
    with conduit_b.transaction("link", conduits=[conduit_a, conduit_b]):
        conduit_b.add_spell_to_contract(
            spell_id=granted_id,
            conduit=conduit_a,
            permissions="create",
        )
    cloud = Aether()._aetheric_frames["default"].conduit_cloud
    cloud.create_cluster("everything")
    cloud.add_conduit_to_cluster(conduit_a, "everything")
    cloud.add_conduit_to_cluster(conduit_b, "everything")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    reports = {}
    for parallel_enabled in (False, True):
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        configuration = CrystallizerConfiguration().with_defaults()
        configuration.set_property(
            "restore_parallel_enabled", parallel_enabled
        )
        configuration.activate()
        booted = Crystallizer()
        booted.activate(configuration)
        booted.reload_cached_checkpoint(checkpoint_id)
        reports[parallel_enabled] = booted.load_checkpoint(checkpoint_id)

    sequential, parallel = reports[False], reports[True]
    assert sequential["status"] == parallel["status"] == "complete"
    assert sequential["built_counts"] == parallel["built_counts"]

    def shortfall_key(row):
        return (row["kind"], row["key"], row["reason"])

    assert (
        sorted(sequential["shortfalls"], key=shortfall_key)
        == sorted(parallel["shortfalls"], key=shortfall_key)
    )
    assert set(sequential["identity_map"]) == set(parallel["identity_map"])
    assert sequential["plan"] == {}
    assert parallel["plan"]["level_count"] >= 3
    assert parallel["built_counts"].get("cluster", 0) == 1
    assert parallel["built_counts"].get("spell_staged", 0) == 1
    assert parallel["built_counts"].get("link", 0) == 1
