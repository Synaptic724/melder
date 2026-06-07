import json
import logging
from pathlib import Path
import shutil
from types import MappingProxyType

import pytest

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
        cache_root_path / "frame-b" / "alpha" / "bundle.json"
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

    loaded_json = json.loads(caching_system.bundle_path.read_text(encoding="utf-8"))

    assert loaded_json["version"] == CachingSystem.CURRENT_VERSION
    assert loaded_json["conduit_name"] == "root"
    assert loaded_json["spell_payloads"][spell_id] == spell_payload
    assert isinstance(loaded_json["sha256"], str)


@pytest.mark.parametrize(
    ("file_contents", "label"),
    [
        ("not-json", "invalid_json"),
        (
            json.dumps(
                {
                    "version": 999,
                    "conduit_name": "root",
                    "spell_payloads": {},
                    "sha256": "x",
                }
            ),
            "wrong_version",
        ),
        (
            json.dumps(
                {
                    "version": CachingSystem.CURRENT_VERSION,
                    "conduit_name": "other",
                    "spell_payloads": {},
                    "sha256": "x",
                }
            ),
            "wrong_conduit_name",
        ),
        (
            json.dumps(
                {
                    "version": CachingSystem.CURRENT_VERSION,
                    "conduit_name": "root",
                    "spell_payloads": [],
                    "sha256": "x",
                }
            ),
            "non_dict_spell_payloads",
        ),
        (
            json.dumps(
                {
                    "version": CachingSystem.CURRENT_VERSION,
                    "conduit_name": "root",
                    "spell_payloads": {7: {}},
                    "sha256": "x",
                }
            ),
            "non_string_spell_id",
        ),
        (
            json.dumps(
                {
                    "version": CachingSystem.CURRENT_VERSION,
                    "conduit_name": "root",
                    "spell_payloads": {"f" * 64: _make_spell_payload("sha-mismatch")},
                    "sha256": "wrong",
                }
            ),
            "sha_mismatch",
        ),
    ],
)
def test_caching_system_resets_to_empty_cache_on_invalid_bundle_file(
        file_contents: str,
        label: str,
) -> None:
    """
    Verify invalid bundle files reset to an empty cache dict.

    Args:
        file_contents:
            Raw file payload to persist before construction.
        label:
            Unique suffix for the repo-local scratch path.

    Returns:
        None.
    """
    cache_root_path = _prepare_cache_root(
        Path(f"tests/unit/melder/utilities/_caching_system_tmp_load_{label}")
    )
    bundle_path = cache_root_path / "frame-a" / "root" / "bundle.json"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(file_contents, encoding="utf-8")

    caching_system = _make_cache_utility(cache_root_path=cache_root_path)

    assert tuple(caching_system.cached_spell_ids) == ()
    assert caching_system.spell_payloads == {}


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
