"""
Unit tests for the ExternalPersistenceManager lane (the DB opt-in):
handler configuration contract, upload gating and failure postures,
profile downloads through user callables, and the ledger insert lane.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.persistence.external_persistence_manager import (
    ExternalPersistenceManager,
)
from melder.crystallizer.persistence.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.persistence.persistence_system import (
    PersistenceSystem,
)
from melder.crystallizer.persistence.recorded_unit_state import (
    RecordedUnitState,
)


def _recording_store():
    """
    Build a dict-backed remote plus its three handler callables.

    Returns:
        tuple: (store dict, upload, download, list_ids) where the
        handlers close over the store the way a user's DB calls would
        close over their session.
    """
    store = {}

    def upload(profile_name, checkpoint_id, cached_item):
        store[checkpoint_id] = (profile_name, cached_item)

    def download(checkpoint_id):
        entry = store.get(checkpoint_id)
        return entry[1] if entry is not None else None

    def list_ids(profile_name):
        return [
            checkpoint_id
            for checkpoint_id, entry in store.items()
            if entry[0] == profile_name
        ]

    return store, upload, download, list_ids


def test_configuration_validates_freezes_and_reports_presence_only():
    """
    Contract: the separate configuration seals with attached callables,
    refuses mutation after freeze, refuses upload_on_flush with no
    handler, and its record surface carries PRESENCE FLAGS only.
    """
    with pytest.raises(ValueError, match="upload_on_flush"):
        ExternalPersistenceManagerConfiguration().freeze()
    _store, upload, _download, _list_ids = _recording_store()
    configuration = (
        ExternalPersistenceManagerConfiguration()
        .with_upload_handler(upload)
        .with_strict_uploads(True)
    )
    configuration.freeze()
    with pytest.raises(RuntimeError):
        configuration.with_upload_on_flush(False)
    presence = configuration.describe_presence()
    assert presence["upload_handler_present"] is True
    assert presence["download_handler_present"] is False
    assert presence["strict_uploads"] is True
    assert not any(callable(value) for value in presence.values())
    configuration.cleanup()


def test_upload_gates_and_failure_postures():
    """
    Contract: no handler -> False no-op; lenient failures count and
    return False without breaking the caller; strict failures re-raise.
    """
    lenient_configuration = ExternalPersistenceManagerConfiguration()
    lenient_configuration.with_upload_on_flush(False)
    lenient_configuration.freeze()
    bare_manager = ExternalPersistenceManager(lenient_configuration)
    assert bare_manager.upload_checkpoint("default", "01X", {}) is False
    assert bare_manager.upload_enabled is False
    bare_manager.cleanup()

    def exploding(profile_name, checkpoint_id, cached_item):
        raise ConnectionError("db down")

    lenient = ExternalPersistenceManagerConfiguration().with_upload_handler(
        exploding
    )
    lenient.freeze()
    manager = ExternalPersistenceManager(lenient)
    assert manager.upload_checkpoint("default", "01X", {}) is False
    assert manager.upload_failure_count == 1
    manager.cleanup()

    strict = (
        ExternalPersistenceManagerConfiguration()
        .with_upload_handler(exploding)
        .with_strict_uploads(True)
    )
    strict.freeze()
    strict_manager = ExternalPersistenceManager(strict)
    with pytest.raises(ConnectionError):
        strict_manager.upload_checkpoint("default", "01X", {})
    strict_manager.cleanup()


def test_download_profile_requires_handlers_and_refuses_inconsistency():
    """
    Contract: missing handlers refuse loudly; a remote that lists an id
    it cannot return raises the inconsistency ValueError.
    """
    bare = ExternalPersistenceManagerConfiguration()
    bare.with_upload_on_flush(False)
    bare.freeze()
    manager = ExternalPersistenceManager(bare)
    with pytest.raises(RuntimeError, match="list handler"):
        manager.download_profile("default")
    manager.cleanup()

    def liar_list(profile_name):
        return ["01GHOST"]

    def empty_download(checkpoint_id):
        return None

    lying = (
        ExternalPersistenceManagerConfiguration()
        .with_list_handler(liar_list)
        .with_download_handler(empty_download)
        .with_upload_on_flush(False)
    )
    lying.freeze()
    liar = ExternalPersistenceManager(lying)
    with pytest.raises(ValueError, match="inconsistent"):
        liar.download_profile("default")
    liar.cleanup()


def test_remote_round_trip_rebuilds_the_ledger():
    """
    Contract: upload every flushed-form item into the dict-backed
    remote, then a FRESH system rebuilds the profile purely from
    manager downloads (insert_cached_items) and verifies intact.
    """
    store, upload, download, list_ids = _recording_store()
    source = PersistenceSystem()
    for _round in range(2):
        source.record_nexus_state(RecordedUnitState.enabled)
        checkpoint_id = source.create_checkpoint()
        upload("default", checkpoint_id, source.cached_item_form(checkpoint_id))
    source.cleanup()
    assert len(store) == 2

    configuration = (
        ExternalPersistenceManagerConfiguration()
        .with_download_handler(download)
        .with_list_handler(list_ids)
        .with_upload_on_flush(False)
    )
    configuration.freeze()
    manager = ExternalPersistenceManager(configuration)
    target = PersistenceSystem()
    summary = target.insert_cached_items(
        manager.download_profile("default")
    )
    assert len(summary["inserted"]) == 2
    assert target.verify_checkpoint_chain()["verdict"] == "intact"
    manager.cleanup()
    target.cleanup()
