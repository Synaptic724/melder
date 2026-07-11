"""
Record versioning + the classes-or-JSON interface contract
(external_mesh 2026-07-12, owner rulings: "an interface class that we
can emit or json" + "keep version control in the structures").

Everything that crosses the mesh boundary is a JSON-safe dict derived
from a twin's describe() - these suites prove the version stamps ride
every artifact, the read gates refuse newer-major shapes, the twin
family's describe() payloads survive JSON round trips losslessly, and
the generic manager verbs uphold their contracts over plain callables.
"""

import json

import pytest

from melder.crystallizer.asset_management.external_persistence_manager import (
    ExternalPersistenceManager,
)
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.crystals.aetheric_frame_crystal import (
    AethericFrameCrystal,
)
from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.crystallizer.crystals.spell_index_crystal import (
    SpellIndexCrystal,
)
from melder.crystallizer.persistence.persistence_crystal import (
    PersistenceCrystal,
)
from melder.crystallizer.persistence.record_version import RecordVersion


def _json_round_trip(payload):
    """One boundary crossing: what SQLite/any DB stores and returns."""
    return json.loads(json.dumps(payload))


# ----------------------------------------------------------------------
# RecordVersion semantics
# ----------------------------------------------------------------------

def test_record_version_parses_and_defaults():
    """
    Contract: MAJOR.MINOR.PATCH parses into comparable ints; missing
    parts read 0; absent stamps read "0.0.0" (pre-versioning artifacts).
    """
    assert RecordVersion.parse("1.0.0") == (1, 0, 0)
    assert RecordVersion.parse("2.13") == (2, 13, 0)
    assert RecordVersion.of({}) == "0.0.0"
    assert RecordVersion.of({"record_version": "1.4.2"}) == "1.4.2"
    with pytest.raises(ValueError):
        RecordVersion.parse("not.a.version")


def test_record_version_stamp_and_gate():
    """
    Contract: stamp writes CURRENT under the shared key; the read gate
    passes current/older/pre-versioning payloads and refuses a NEWER
    major with the upgrade instruction.
    """
    stamped = RecordVersion.stamp({"anything": 1})
    assert stamped[RecordVersion.KEY] == RecordVersion.CURRENT

    RecordVersion.check_readable(stamped, "self-stamped artifact")
    RecordVersion.check_readable({}, "pre-versioning artifact")
    RecordVersion.check_readable(
        {"record_version": "0.9.0"}, "older artifact"
    )

    current_major = RecordVersion.parse(RecordVersion.CURRENT)[0]
    future = {"record_version": "{0}.0.0".format(current_major + 1)}
    with pytest.raises(ValueError, match="upgrade melder"):
        RecordVersion.check_readable(future, "future artifact")


# ----------------------------------------------------------------------
# Stamped artifacts + JSON fidelity
# ----------------------------------------------------------------------

def _checkpoint_crystal():
    return PersistenceCrystal(
        checkpoint_id="01VERSIONSTAMPCHECKPOINT00",
        profile_name="default",
        checkpoint_number=1,
        description="version-stamp proof",
        journal_segment=[(1, "frame", "default")],
        captured_payloads={
            "frame": {"default": {"system_state": "dynamic"}},
        },
        sequence_range=(1, 1),
        created_at="2026-07-12T00:00:00Z",
    )


def test_cached_items_are_stamped_json_safe_and_rehydrate():
    """
    Contract: to_cached_item carries the version stamp, survives the
    JSON boundary LOSSLESSLY, and rehydrates through from_cached_item
    into an equivalent crystal (the full class -> json -> class loop).
    """
    crystal = _checkpoint_crystal()
    try:
        cached = crystal.to_cached_item()
        assert cached[RecordVersion.KEY] == RecordVersion.CURRENT

        crossed = _json_round_trip(cached)
        assert crossed == cached

        rebuilt = PersistenceCrystal.from_cached_item(crossed)
        try:
            assert rebuilt.to_cached_item() == cached
        finally:
            rebuilt.cleanup()
    finally:
        crystal.cleanup()


def test_newer_major_cached_items_refuse_rehydration():
    """
    Contract: a cached item stamped by a NEWER major refuses at
    from_cached_item - undefined shapes never half-load.
    """
    crystal = _checkpoint_crystal()
    try:
        cached = crystal.to_cached_item()
    finally:
        crystal.cleanup()
    current_major = RecordVersion.parse(RecordVersion.CURRENT)[0]
    cached[RecordVersion.KEY] = "{0}.0.0".format(current_major + 1)
    with pytest.raises(ValueError, match="upgrade melder"):
        PersistenceCrystal.from_cached_item(cached)


# ----------------------------------------------------------------------
# The interface contract: twin classes -> describe() -> JSON
# ----------------------------------------------------------------------

def test_twin_family_describes_survive_the_json_boundary():
    """
    Contract ("interface class that we can emit or json"): a twin IS the
    interface - emit consumes the object, the mesh ships its describe()
    dict, and that dict must cross JSON losslessly. Proven over three
    family members with distinct shapes (posture map, membership list,
    nested composition).
    """
    twins = [
        AethericFrameCrystal(
            frame_name="json-frame",
            system_state_name="dynamic",
            rift_enabled=False,
            ai_native_enabled=True,
            dev_ops_payload={"disable_bind": False,
                             "max_transaction_wait_time_in_seconds": 30.0},
        ),
        SpellIndexCrystal(
            index_id="01INDEXJSONCONTRACT0000000",
            spellbook_id="01BOOKJSONCONTRACT00000000",
            selected_spell_id="a" * 64,
            member_spell_ids=["a" * 64, "b" * 64],
        ),
        MutationResearchCrystal(
            activated=True,
            configuration_payload={"unrestricted_module_mutations": False},
            composition_payload={"default": {"organization": {
                "lanes": [], "residence": {"lane_id_by_spell_id": {}},
            }}},
        ),
    ]
    for twin in twins:
        try:
            payload = twin.describe()
            assert _json_round_trip(payload) == payload
        finally:
            twin.cleanup()


# ----------------------------------------------------------------------
# Generic manager verbs over plain callables (dict-backed "DB")
# ----------------------------------------------------------------------

def _dict_backed_manager(*, strict=False, with_delete=True):
    """A pure in-memory mesh 'DB' - the callables-first contract naked."""
    rows = {}

    def store(kind, profile_name, unit_id, payload):
        rows[(kind, unit_id)] = (profile_name, json.dumps(payload))

    def fetch(kind, unit_id):
        row = rows.get((kind, unit_id))
        return json.loads(row[1]) if row is not None else None

    def list_units(kind, profile_name):
        return [
            unit_id
            for (row_kind, unit_id), (row_profile, _payload) in rows.items()
            if row_kind == kind and row_profile == profile_name
        ]

    def delete(kind, unit_id):
        del rows[(kind, unit_id)]

    configuration = ExternalPersistenceManagerConfiguration()
    configuration.with_store_handler(store)
    configuration.with_fetch_handler(fetch)
    configuration.with_list_units_handler(list_units)
    if with_delete:
        configuration.with_delete_handler(delete)
    if strict:
        configuration.with_strict_uploads(True)
    configuration.freeze()
    return ExternalPersistenceManager(configuration), rows


def test_generic_verbs_round_trip_any_kind():
    """
    Contract: store/fetch/list/delete carry arbitrary kinds untouched;
    payloads cross the JSON boundary losslessly; delete removes exactly
    the named unit.
    """
    manager, rows = _dict_backed_manager()
    try:
        payload = RecordVersion.stamp({"nested": {"deep": [1, 2, 3]}})
        assert manager.store_unit(
            "anything", "default", "unit-1", payload
        ) is True
        assert manager.fetch_unit("anything", "unit-1") == payload
        assert manager.list_units("anything", "default") == ["unit-1"]
        assert manager.fetch_unit("anything", "missing") is None

        manager.delete_unit("anything", "unit-1")
        assert manager.list_units("anything", "default") == []
        assert rows == {}
    finally:
        manager.cleanup()


def test_generic_store_is_lenient_and_counted_deletes_are_strict():
    """
    Contract: a raising store handler counts on store_failure_count and
    returns False (lenient law); a raising/missing delete propagates or
    refuses loudly (retention must never lie).
    """
    def broken_store(kind, profile_name, unit_id, payload):
        raise RuntimeError("db down")

    configuration = ExternalPersistenceManagerConfiguration()
    configuration.with_store_handler(broken_store)
    configuration.freeze()
    manager = ExternalPersistenceManager(configuration)
    try:
        assert manager.store_unit("k", "p", "u", {}) is False
        assert manager.store_failure_count == 1
        with pytest.raises(RuntimeError, match="delete handler"):
            manager.delete_unit("k", "u")
        with pytest.raises(RuntimeError, match="fetch handler"):
            manager.fetch_unit("k", "u")
        with pytest.raises(RuntimeError, match="list-units handler"):
            manager.list_units("k", "p")
    finally:
        manager.cleanup()


def test_strict_uploads_propagate_generic_store_errors():
    """
    Contract: strict_uploads governs the generic lane exactly like the
    legacy upload lane - handler errors re-raise instead of counting.
    """
    def broken_store(kind, profile_name, unit_id, payload):
        raise RuntimeError("db down hard")

    configuration = ExternalPersistenceManagerConfiguration()
    configuration.with_store_handler(broken_store)
    configuration.with_strict_uploads(True)
    configuration.freeze()
    manager = ExternalPersistenceManager(configuration)
    try:
        with pytest.raises(RuntimeError, match="db down hard"):
            manager.store_unit("k", "p", "u", {})
        assert manager.store_failure_count == 0
    finally:
        manager.cleanup()


def test_legacy_bridge_serves_checkpoints_from_the_generic_lanes():
    """
    Contract: with ONLY generic handlers attached, the legacy checkpoint
    verbs bridge - upload_checkpoint stores kind="checkpoint",
    download_checkpoint fetches it, download_profile lists+fetches in
    ULID order.
    """
    manager, _rows = _dict_backed_manager()
    try:
        item = RecordVersion.stamp({"checkpoint_id": "01A", "n": 1})
        assert manager.upload_checkpoint("default", "01A", item) is True
        assert manager.download_checkpoint("01A") == item

        second = RecordVersion.stamp({"checkpoint_id": "01B", "n": 2})
        manager.upload_checkpoint("default", "01B", second)
        history = manager.download_profile("default")
        assert [entry["checkpoint_id"] for entry in history] == [
            "01A", "01B",
        ]
    finally:
        manager.cleanup()


def test_presence_flags_describe_the_generic_lanes():
    """
    Contract (record law): callables never escape - describe reports
    presence flags + both failure counters, all JSON-safe.
    """
    manager, _rows = _dict_backed_manager()
    try:
        described = manager.describe()
        assert described["store_handler_present"] is True
        assert described["fetch_handler_present"] is True
        assert described["list_units_handler_present"] is True
        assert described["delete_handler_present"] is True
        assert described["stream_emissions"] is False
        assert described["store_failure_count"] == 0
        assert _json_round_trip(described) == described
    finally:
        manager.cleanup()
