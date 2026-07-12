import logging
import marshal
import sys
from pathlib import Path

import pytest

from melder.utilities.caching_system.caching_system import CachingSystem


EXPECTED_CACHE_VERSION_HISTORY = {
    1: "legacy_executor_payloads",
    2: "decoded_manifest_package_payloads",
    3: "nested_marshal_spell_payload_bytes",
    4: "generalized_collection_param_names",
    5: "many_only_collection_param_names",
    6: "zero_provider_required_collections",
}


@pytest.mark.parametrize("bundle_version", tuple(EXPECTED_CACHE_VERSION_HISTORY))
def test_cache_schema_version_history_accepts_only_current_bundle(
        tmp_path: Path,
        bundle_version: int,
) -> None:
    """
    Pin every persisted cache schema generation and its invalidation boundary.

    A newly documented schema generation must be added to
    ``CachingSystem.CACHE_VERSION_HISTORY``. ``CURRENT_VERSION`` is derived
    from that mapping, so advancing the history automatically advances the
    persisted bundle version. This integration test writes every known bundle
    generation through the real marshal format and proves that only the newest
    generation survives loading; every predecessor cold-resets.
    """
    assert dict(CachingSystem.CACHE_VERSION_HISTORY) == (
        EXPECTED_CACHE_VERSION_HISTORY
    )
    assert CachingSystem.CURRENT_VERSION == max(
        EXPECTED_CACHE_VERSION_HISTORY
    )

    frame_name = "cache-version-history"
    conduit_name = "root"
    spell_id = "a" * 64
    cache_root = tmp_path / "cache"
    bundle_path = cache_root / frame_name / f"{conduit_name}.melc"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_bytes(marshal.dumps({
        "version": bundle_version,
        "python": sys.implementation.cache_tag,
        "frame_name": frame_name,
        "conduit_name": conduit_name,
        "spell_payloads": {
            spell_id: marshal.dumps({"bundle_version": bundle_version}),
        },
    }))

    caching_system = CachingSystem(
        frame_name=frame_name,
        conduit_name=conduit_name,
        cache_root_path=cache_root,
        logger=logging.getLogger("cache-schema-version-integration"),
    )
    try:
        if bundle_version == CachingSystem.CURRENT_VERSION:
            assert caching_system.get_spell_payload(spell_id) == {
                "bundle_version": bundle_version,
            }
        else:
            assert caching_system.get_spell_payload(spell_id) is None
    finally:
        caching_system.cleanup()
