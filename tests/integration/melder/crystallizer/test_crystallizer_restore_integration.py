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
    Nexus().enable(nexus_configuration)
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    rebooted = _fresh_boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["nexus"] == 1
    rebuilt = Nexus()
    assert rebuilt.is_enabled is True
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
        because the engine-restored registry is non-virgin.
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

    MutationResearch._reset_singleton_for_tests()
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
        walked_shas = [
            str(entry.get("spell_sha"))
            for entry in restored_set.walk("experiments")
        ]
        assert "f" * 64 in walked_shas

        # Continuable: new research lands on the restored organization.
        restored_set.register_spell(
            "b" * 64, lane="experiments", author="s3c", reason="post-restore"
        )
        assert restored_set.residence_of("b" * 64) is not None

        # Non-virgin registry: a later activation hydration NO-OPs (the
        # engine-restored organization survives untouched).
        restored_root.activate(hydrate_from_record=True)
        assert restored_set.residence_of("b" * 64) is not None
        assert set(restored_set.lane_names()) == {"default", "experiments"}
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
