"""Retain native integration behavior while eliminating full-catalog warm iteration.

The first adapter, probe and receipt remain unchanged. The existing integration
functions are reused through their constructor seam, then a 511-site deep plan
with both branches supplied runs with catalog iteration explicitly forbidden.
"""

import hashlib
import json
import sys
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    SliceProbe,
    World,
)
from context_compass.artifacts.override_structural_discovery_20260924 import (
    native_compact_probe,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_compact_direct_adapter import (
    DirectNativeCompactAdapter,
)
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from melder.aether.spellbook.spell import Spell


class CatalogWithoutIteration:
    """Borrow the catalog and allow O(1) lookup while rejecting a full warm traversal."""

    def __init__(self, catalog: tuple[Spell, ...]) -> None:
        """Retain the already-bound metadata only for this diagnostic guard."""
        self.catalog = catalog

    def __len__(self) -> int:
        """Allow the constant-time count; the regression concerns traversal and rebuilding."""
        return len(self.catalog)

    def __getitem__(self, index: int) -> Spell:
        """Allow direct indexed metadata access without changing its semantics."""
        return self.catalog[index]

    def __iter__(self) -> Iterator[Spell]:
        """Fail if execution tries to rebuild wrappers by visiting every base Spell."""
        raise AssertionError("A pruned warm call traversed the full constructor catalog.")


def deep_control() -> dict[str, object]:
    """Run one constructor from 511 base sites without iterating base metadata at runtime."""
    world = World()
    try:
        world.setup("deep", "automatic")
        ordinary = world.conduit.meld(spell_id=world.root_id)
        raw = {"left": ordinary.left, "right": ordinary.right}
        with native_compact_probe.prepared(world, raw) as adapter:
            assert isinstance(adapter, DirectNativeCompactAdapter)
            base_count = len(adapter.spells)
            assert base_count == 511
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(adapter, "spells", CatalogWithoutIteration(adapter.spells))
                (result, selected, attempts), calls = SliceProbe.observe(partial(adapter.execute, raw))
            assert result.left is raw["left"] and result.right is raw["right"]
            assert len(calls) == 1 and selected == () and attempts == 1
            return {"case": "deep_all_without_catalog_iteration", "base_sites": base_count,
                    "executed_constructors": len(calls), "shared_claims": 0,
                    "full_catalog_iteration": False, "source_bytes": len(adapter.source.encode())}
    finally:
        world.cleanup()


def main() -> None:
    """Persist variant evidence and prove the earlier native integration artifacts stayed intact."""
    directory = Path(__file__).resolve().parent
    frozen = ("native_compact_adapter.py", "native_compact_probe.py", "native_compact_results.json")
    frozen_hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in frozen}
    own_hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                  for name in ("native_compact_direct_adapter.py", "native_compact_direct_probe.py")}
    before = _source_fingerprints(directory.parents[2])
    original = native_compact_probe.NativeCompactAdapter
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(native_compact_probe, "NativeCompactAdapter", DirectNativeCompactAdapter)
        cases = [native_compact_probe.many_control(), native_compact_probe.reuse_and_purge_control(),
                 native_compact_probe.alias_control(), native_compact_probe.contention_control(),
                 native_compact_probe.failure_control(), native_compact_probe.dynamic_control(False),
                 native_compact_probe.dynamic_control(True), deep_control()]
    assert native_compact_probe.NativeCompactAdapter is original
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed
    assert all(hashlib.sha256((directory / name).read_bytes()).hexdigest() == value
               for name, value in frozen_hashes.items())
    assert all(hashlib.sha256((directory / name).read_bytes()).hexdigest() == value
               for name, value in own_hashes.items())
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "frozen_sha256": frozen_hashes,
              "scripts_sha256": own_hashes, "cases": cases,
              "limits": "Experimental native-store adapter; cold compilation duplicated; no throughput claim or full production compatibility."}
    (directory / "native_compact_direct_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
