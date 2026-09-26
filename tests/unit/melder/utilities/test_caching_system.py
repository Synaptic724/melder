import logging
import marshal
from pathlib import Path
import shutil
import sys
from types import MappingProxyType

import pytest

from melder.__version__ import __version__
from melder.utilities.caching_system.caching_system import CachingSystem


def _prepare_cache_root(path: Path) -> Path:
    """
    Reset one repo-local cache root for the test.

    Args:
        path:
            Target test directory.

    Returns:
        Path:
            Prepared directory path.
    """
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _make_cache_utility(
        *,
        frame_name: str = "frame-a",
        conduit_name: str = "root",
        cache_root_path: Path,
) -> CachingSystem:
    """
    Build one cache utility for the test.

    Args:
        frame_name:
            Frame name for the cache file.
        conduit_name:
            Conduit name for the cache file.
        cache_root_path:
            Absolute cache root path for the test.

    Returns:
        CachingSystem:
            Fresh cache utility.
    """
    return CachingSystem(
        frame_name=frame_name,
        conduit_name=conduit_name,
        cache_root_path=cache_root_path,
        logger=logging.getLogger("caching-system-test"),
    )


def _make_spell_payload(label: str) -> dict[str, object]:
    """
    Build one simple spell payload for the cache tests.

    Args:
        label:
            Stable label embedded into the payload.

    Returns:
        dict[str, object]:
            JSON-serializable spell payload.
    """
    return {
        "resolve_route_key": label,
        "no_overrides": {"source": f"no-{label}"},
        "overrides": {"source": f"over-{label}"},
    }


def _make_populated_cache_bundle() -> dict[str, object]:
    """
    Build a valid, populated envelope for admission tests.

    Contract:
        The frame and conduit match _make_cache_utility defaults. Tests change
        one field of this accepted control instead of writing an unused path.

    Returns:
        dict[str, object]: Current metadata and one nested-marshal payload.
    """
    return {
        "version": CachingSystem.CURRENT_VERSION,
        "melder_version": __version__,
        "python": sys.implementation.cache_tag,
        "frame_name": "frame-a",
        "conduit_name": "root",
        "spell_payloads": {"a" * 64: marshal.dumps(_make_spell_payload("cached"))},
    }


def _write_cache_bundle(cache_root: Path, contents: bytes) -> Path:
    """
    Write admission-test bytes to the actual conduit cache location.

    Args:
        cache_root: Test-owned cache directory.
        contents: Serialized bundle or deliberately corrupt bytes.

    Returns:
        Path: The frame-a/root.melc file read by _make_cache_utility.
    """
    bundle_path = cache_root / "frame-a" / "root.melc"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_bytes(contents)
    return bundle_path


def test_caching_system_upsert_remove_and_reload_round_trip() -> None:
    """
    Verify the cache utility can persist, remove, and reload one spell payload.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_round_trip")
    )
    spell_id = "a" * 64
    spell_payload = _make_spell_payload("many")

    caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    caching_system.upsert_spell_payload(spell_id, spell_payload)
    caching_system.emit()

    assert caching_system.has_spell_payload(spell_id) is True
    assert caching_system.get_spell_payload(spell_id) == spell_payload
    assert caching_system.bundle_path.exists() is True

    loaded_caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    assert loaded_caching_system.get_spell_payload(spell_id) == spell_payload

    assert loaded_caching_system.remove_spell_payload(spell_id) is True
    assert loaded_caching_system.has_spell_payload(spell_id) is False
    loaded_caching_system.emit()

    reloaded_caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    assert reloaded_caching_system.has_spell_payload(spell_id) is False


def test_caching_system_transfer_moves_payload_between_cache_files() -> None:
    """
    Verify one spell payload can move from one conduit cache to another.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_transfer")
    )
    spell_id = "b" * 64
    spell_payload = _make_spell_payload("shared")
    source_caching_system = _make_cache_utility(
        conduit_name="source",
        cache_root_path=cache_root_path,
    )
    target_caching_system = _make_cache_utility(
        conduit_name="target",
        cache_root_path=cache_root_path,
    )

    source_caching_system.upsert_spell_payload(spell_id, spell_payload)

    assert (
        source_caching_system.transfer_spell_payload_to(
            spell_id,
            target_caching_system,
        )
        is True
    )
    assert source_caching_system.has_spell_payload(spell_id) is False
    assert target_caching_system.get_spell_payload(spell_id) == spell_payload

def test_caching_system_builds_expected_bundle_metadata() -> None:
    """
    Verify the default cache metadata for a new conduit cache.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_metadata")
    )
    caching_system = _make_cache_utility(
        frame_name="frame-b",
        conduit_name="alpha",
        cache_root_path=cache_root_path,
    )

    assert caching_system.conduit_name == "alpha"
    assert caching_system.bundle_path == (
        cache_root_path / "frame-b" / "alpha.melc"
    )


def test_caching_system_exposes_read_only_spell_payload_view() -> None:
    """
    Verify the spell payload surface is read-only.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_read_only")
    )
    spell_id = "c" * 64
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    caching_system.upsert_spell_payload(spell_id, _make_spell_payload("readonly"))

    spell_payloads = caching_system.spell_payloads

    assert isinstance(spell_payloads, MappingProxyType)
    with pytest.raises(TypeError):
        spell_payloads["x" * 64] = {}


def test_caching_system_returns_empty_keys_view_for_new_cache() -> None:
    """
    Verify a new cache starts with no cached spell ids.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_empty_keys")
    )
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)

    assert tuple(caching_system.cached_spell_ids) == ()
    assert caching_system.spell_payloads == {}


def test_caching_system_missing_payload_surfaces_are_safe() -> None:
    """
    Verify missing spell payload reads are safe.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_missing")
    )
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)

    assert caching_system.has_spell_payload("missing") is False
    assert caching_system.get_spell_payload("missing") is None
    assert caching_system.remove_spell_payload("missing") is False


def test_caching_system_upsert_replaces_existing_payload() -> None:
    """
    Verify upsert replaces an existing spell payload cleanly.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_replace")
    )
    spell_id = "d" * 64
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    caching_system.upsert_spell_payload(spell_id, _make_spell_payload("before"))
    caching_system.upsert_spell_payload(spell_id, _make_spell_payload("after"))

    assert caching_system.get_spell_payload(spell_id) == _make_spell_payload("after")

def test_caching_system_emit_writes_expected_file_shape() -> None:
    """
    Verify flush persists the top-level cache dict shape.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_flush")
    )
    spell_id = "e" * 64
    spell_payload = _make_spell_payload("flush")
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    caching_system.upsert_spell_payload(spell_id, spell_payload)
    caching_system.emit()

    loaded_payload = marshal.loads(caching_system.bundle_path.read_bytes())

    assert loaded_payload["version"] == CachingSystem.CURRENT_VERSION
    assert loaded_payload["melder_version"] == __version__
    assert loaded_payload["conduit_name"] == "root"
    assert loaded_payload["frame_name"] == "frame-a"
    # Version-3 bundle contract: payloads persist as nested-marshal bytes
    # (GC-untracked resident cache); one more decode yields the payload.
    persisted_bytes = loaded_payload["spell_payloads"][spell_id]
    assert isinstance(persisted_bytes, bytes)
    assert marshal.loads(persisted_bytes) == spell_payload
    assert loaded_payload["python"] == sys.implementation.cache_tag


def test_caching_system_resident_store_holds_untracked_bytes() -> None:
    """
    Pin the GC-motivated resident-store contract (regression, 2026-07-02).

    Contract:
        - The in-memory store keeps nested-marshal BYTES per spell, never
          decoded containers: the free-threaded GC scans the full tracked
          heap per collection, and a decoded resident bundle measurably
          fattened every pass (~13% warm wall regression on the gauntlet).
        - Reads return fresh decodes: caller mutations are never persisted.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_untracked")
    )
    spell_id = "f" * 64
    spell_payload = _make_spell_payload("untracked")
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)
    caching_system.upsert_spell_payload(spell_id, spell_payload)

    stored_value = caching_system._cache_data["spell_payloads"][spell_id]
    assert isinstance(stored_value, bytes)

    first_read = caching_system.get_spell_payload(spell_id)
    assert first_read == spell_payload
    first_read["mutated"] = True
    second_read = caching_system.get_spell_payload(spell_id)
    assert "mutated" not in second_read


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        pytest.param("version", -1, id="wrong-schema"),
        pytest.param("python", "foreign-interpreter", id="wrong-python"),
        pytest.param("conduit_name", "other", id="wrong-conduit"),
        pytest.param("spell_payloads", [], id="wrong-payload-map"),
        pytest.param("spell_payloads", {"a" * 64: {}}, id="decoded-payload"),
        pytest.param("structural_payloads", {"a" * 64: {}}, id="decoded-structural-payload"),
        pytest.param("melder_version", __version__ + ".other", id="different-release"),
        pytest.param("melder_version", "", id="empty-release"),
        pytest.param("melder_version", None, id="null-release"),
        pytest.param("melder_version", 7, id="numeric-release"),
        pytest.param("melder_version", __version__.encode(), id="bytes-release"),
    ],
)
def test_caching_system_rejects_invalid_real_bundle_metadata(
        tmp_path: Path,
        field: str,
        replacement: object,
) -> None:
    """
    Reject invalid metadata from the actual populated marshal bundle.

    Contract:
        Only the selected field differs from the accepted control. Rejection
        exposes no old payload and does not delete or rewrite the disk file.

    Args:
        tmp_path: Isolated test-owned cache root.
        field: Header field to invalidate.
        replacement: Deliberately incompatible value.

    Returns:
        None.
    """
    bundle = _make_populated_cache_bundle()
    bundle[field] = replacement
    raw = marshal.dumps(bundle)
    bundle_path = _write_cache_bundle(tmp_path, raw)
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.bundle_path == bundle_path
        assert tuple(caching_system.cached_spell_ids) == ()
        assert caching_system.get_spell_payload("a" * 64) is None
        assert bundle_path.read_bytes() == raw
    finally:
        caching_system.cleanup()


def test_caching_system_accepts_current_release_populated_bundle(tmp_path: Path) -> None:
    """
    Prove the populated admission fixture exposes its matching-release payload.

    Contract:
        This accepted control proves negative cases are testing field rejection
        rather than silently reading a missing or invalid fixture file.

    Args:
        tmp_path: Isolated test-owned cache root.

    Returns:
        None.
    """
    _write_cache_bundle(tmp_path, marshal.dumps(_make_populated_cache_bundle()))
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.get_spell_payload("a" * 64) == _make_spell_payload("cached")
    finally:
        caching_system.cleanup()


def test_caching_system_rejects_missing_release_then_emits_current_bundle(tmp_path: Path) -> None:
    """
    Cold-reset an unstamped bundle and preserve the new stamp through later writes.

    Contract:
        Freshly compiled payloads replace the old data. Loading, adding another
        payload and emitting again must retain the accepted release stamp.

    Args:
        tmp_path: Isolated test-owned cache root.

    Returns:
        None.
    """
    bundle = _make_populated_cache_bundle()
    del bundle["melder_version"]
    bundle_path = _write_cache_bundle(tmp_path, marshal.dumps(bundle))
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.get_spell_payload("a" * 64) is None
        caching_system.upsert_spell_payload("b" * 64, _make_spell_payload("fresh"))
        caching_system.emit()
    finally:
        caching_system.cleanup()

    reloaded = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert reloaded.get_spell_payload("a" * 64) is None
        assert reloaded.get_spell_payload("b" * 64) == _make_spell_payload("fresh")
        reloaded.upsert_spell_payload("c" * 64, _make_spell_payload("later"))
        reloaded.emit()
        assert marshal.loads(bundle_path.read_bytes())["melder_version"] == __version__
    finally:
        reloaded.cleanup()


@pytest.mark.parametrize("contents", [b"not-marshal", marshal.dumps([])])
def test_caching_system_rejects_corrupt_real_bundle(tmp_path: Path, contents: bytes) -> None:
    """
    Treat unreadable or non-dictionary .melc contents as a cold cache.

    Args:
        tmp_path: Isolated test-owned cache root.
        contents: Invalid marshal bytes or a serialized non-dictionary value.

    Returns:
        None. No cached spell is exposed by the rejected input.
    """
    _write_cache_bundle(tmp_path, contents)
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert tuple(caching_system.cached_spell_ids) == ()
    finally:
        caching_system.cleanup()


def test_caching_system_transfer_to_self_returns_false() -> None:
    """
    Verify self-transfer is ignored.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_transfer_self")
    )
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)

    assert caching_system.transfer_spell_payload_to("j" * 64, caching_system) is False


def test_caching_system_transfer_missing_spell_returns_false() -> None:
    """
    Verify transfer returns false when the source spell is missing.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_transfer_missing")
    )
    source_caching_system = _make_cache_utility(
        conduit_name="source",
        cache_root_path=cache_root_path,
    )
    target_caching_system = _make_cache_utility(
        conduit_name="target",
        cache_root_path=cache_root_path,
    )

    assert (
        source_caching_system.transfer_spell_payload_to(
            "k" * 64,
            target_caching_system,
        )
        is False
    )


def test_caching_system_cleanup_is_idempotent() -> None:
    """
    Verify cleanup is safe to call more than once.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path("tests/unit/melder/utilities/_caching_system_tmp_cleanup")
    )
    caching_system = _make_cache_utility(cache_root_path=cache_root_path)

    caching_system.cleanup()
    caching_system.cleanup()

    assert caching_system.cleaned is True


def _make_structural_payload(label: str) -> dict[str, object]:
    """
    Build one marshal-safe structural payload shaped like the capture seam's rows.

    Args:
        label:
            Stable label embedded into the payload.

    Returns:
        dict[str, object]:
            Value-only structural payload.
    """
    return {
        "key": {"format": 1, "spell_id": label, "annotation_refs": [("mod", "Type")]},
        "world_stamp": "stamp-" + label,
        "replayable": True,
        "phase3": {"dependency_ids": ["d" * 64], "sockets": [("dep", 0, "NORMAL", False, False, ("d" * 64,), None, None, (), "POSITIONAL_OR_KEYWORD")]},
        "phase4": {"validity": "valid", "contract_unvalidated": False},
    }


def test_caching_system_structural_tier_round_trips_through_emit_and_reload(tmp_path: Path) -> None:
    """
    Verify structural payloads persist beside executor payloads and reload independently.

    Contract:
        - upsert returns True on add, False on an identical re-upsert, True on a change.
        - The structural tier survives emit/reload and does not touch the executor tier.
        - remove reports presence; a missing id is a False no-op.
    """
    spell_id = "c" * 64
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.has_structural_payload(spell_id) is False
        assert caching_system.get_structural_payload(spell_id) is None
        payload = _make_structural_payload("one")
        assert caching_system.upsert_structural_payload(spell_id, payload) is True
        assert caching_system.upsert_structural_payload(spell_id, payload) is False
        assert caching_system.upsert_structural_payload(spell_id, _make_structural_payload("two")) is True
        assert tuple(caching_system.cached_structural_spell_ids) == (spell_id,)
        assert tuple(caching_system.cached_spell_ids) == ()
        caching_system.emit()
    finally:
        caching_system.cleanup()
    reloaded = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert reloaded.get_structural_payload(spell_id) == _make_structural_payload("two")
        assert reloaded.structural_payloads == {spell_id: _make_structural_payload("two")}
        assert isinstance(reloaded.structural_payloads, MappingProxyType)
        assert reloaded.has_spell_payload(spell_id) is False
        assert reloaded.remove_structural_payload(spell_id) is True
        assert reloaded.remove_structural_payload(spell_id) is False
        assert reloaded.has_structural_payload(spell_id) is False
    finally:
        reloaded.cleanup()


def test_caching_system_structural_store_holds_untracked_bytes(tmp_path: Path) -> None:
    """The structural tier keeps nested-marshal bytes resident, like the executor tier."""
    spell_id = "e" * 64
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        caching_system.upsert_structural_payload(spell_id, _make_structural_payload("bytes"))
        stored = caching_system._cache_data["structural_payloads"][spell_id]
        assert isinstance(stored, bytes)
        assert marshal.loads(stored) == _make_structural_payload("bytes")
    finally:
        caching_system.cleanup()


def test_caching_system_transfer_drops_source_structural_payload(tmp_path: Path) -> None:
    """
    Verify a transfer moves the executor bytes and drops the source's structural payload without copying it.

    Contract:
        - With both tiers present: executor moves, structural is removed at the source and absent at the target.
        - With only a structural payload: transfer returns False (no executor payload) but still drops it.
    """
    spell_id = "f" * 64
    source = _make_cache_utility(conduit_name="source", cache_root_path=tmp_path)
    target = _make_cache_utility(conduit_name="target", cache_root_path=tmp_path)
    try:
        source.upsert_spell_payload(spell_id, _make_spell_payload("moving"))
        source.upsert_structural_payload(spell_id, _make_structural_payload("moving"))
        assert source.transfer_spell_payload_to(spell_id, target) is True
        assert source.has_spell_payload(spell_id) is False
        assert source.has_structural_payload(spell_id) is False
        assert target.get_spell_payload(spell_id) == _make_spell_payload("moving")
        assert target.has_structural_payload(spell_id) is False

        only_structural = "g" * 64
        source.upsert_structural_payload(only_structural, _make_structural_payload("lonely"))
        assert source.transfer_spell_payload_to(only_structural, target) is False
        assert source.has_structural_payload(only_structural) is False
        assert target.has_structural_payload(only_structural) is False
    finally:
        source.cleanup()
        target.cleanup()


def test_caching_system_accepts_current_bundle_without_structural_tier(tmp_path: Path) -> None:
    """A current-generation bundle written without the structural map is a valid executor bundle."""
    bundle = _make_populated_cache_bundle()
    assert "structural_payloads" not in bundle
    bundle_path = _write_cache_bundle(tmp_path, marshal.dumps(bundle))
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        assert caching_system.get_spell_payload("a" * 64) == _make_spell_payload("cached")
        assert tuple(caching_system.cached_structural_spell_ids) == ()
        caching_system.upsert_structural_payload("a" * 64, _make_structural_payload("late"))
        caching_system.emit()
        persisted = marshal.loads(bundle_path.read_bytes())
        assert set(persisted["structural_payloads"]) == {"a" * 64}
        assert set(persisted["spell_payloads"]) == {"a" * 64}
    finally:
        caching_system.cleanup()


def test_caching_system_emit_writes_structural_tier_in_envelope(tmp_path: Path) -> None:
    """The persisted envelope carries both maps and the current generation."""
    caching_system = _make_cache_utility(cache_root_path=tmp_path)
    try:
        caching_system.upsert_spell_payload("h" * 64, _make_spell_payload("exec"))
        caching_system.upsert_structural_payload("i" * 64, _make_structural_payload("rows"))
        caching_system.emit()
        persisted = marshal.loads(caching_system.bundle_path.read_bytes())
        assert persisted["version"] == CachingSystem.CURRENT_VERSION
        assert set(persisted) == {
            "version", "melder_version", "python", "frame_name", "conduit_name",
            "spell_payloads", "structural_payloads",
        }
        assert isinstance(persisted["structural_payloads"]["i" * 64], bytes)
        assert marshal.loads(persisted["structural_payloads"]["i" * 64]) == _make_structural_payload("rows")
    finally:
        caching_system.cleanup()

