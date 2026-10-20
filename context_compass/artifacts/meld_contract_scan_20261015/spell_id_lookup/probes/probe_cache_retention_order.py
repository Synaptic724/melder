"""Probe (melder_1, 2026-10-18): which cached checkpoint file the crystallizer cache's retention removes.

`CrystallizerCache.enforce_cache_retention` keeps the newest `max_persistence_crystals` files of a profile and
orders them by the `checkpoint_number` each payload records. That number is minted per process
(`PersistenceSystem._next_checkpoint_number`: 1 + the highest number in THIS process's record), while the cache
folder outlives the process. This probe, run in a fresh process against a copy of src whose `default` cache folder
already holds files from earlier processes, seals and flushes one checkpoint and reports its number, the numbers
already in the folder, and whether the flushed file survives retention.

Read-only on src/: run against a COPY of src (the cache folder lives under the package root), e.g.
    PYTHONPATH=<copy>/src python probe_cache_retention_order.py
"""
import collections
import json
import pathlib

import melder as md
from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache


class Ledger:
    """A spell so the world has something to record."""


def numbers_in(folder: pathlib.Path) -> "collections.Counter[int]":
    """Count the recorded checkpoint numbers of the cached files in one profile folder."""
    counts: "collections.Counter[int]" = collections.Counter()
    for path in folder.glob("*.json"):
        counts[json.loads(path.read_text(encoding="utf-8")).get("checkpoint_number")] += 1
    return counts


def main() -> None:
    """Seal and flush one checkpoint and report what retention kept."""
    folder = CrystallizerCache.resolve_cache_root_path() / "default"
    before = numbers_in(folder)
    print(f"files in the folder before: {sum(before.values())}, checkpoint numbers: {sorted(before.items())}")
    crystallizer = md.Crystallizer()
    crystallizer.activate(md.CrystallizerConfigurationBuilder().with_defaults().activate())
    book = md.Spellbook()
    book.bind(spell=Ledger, existence="unique", permissions="create", binding_name="retention-ledger")
    book.conjure(name="retention-root")
    checkpoint_id = crystallizer.create_checkpoint()
    path = folder / f"{checkpoint_id}.json"
    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    print(f"flush_checkpoint returned the id: {checkpoint_id in flushed}")
    print(f"file written then kept: {path.exists()}")
    print(f"in list_cached_checkpoint_ids(): {checkpoint_id in crystallizer.list_cached_checkpoint_ids()}")
    after = numbers_in(folder)
    print(f"files in the folder after: {sum(after.values())}, checkpoint numbers: {sorted(after.items())}")
    print(f"this process's checkpoint number: {sorted((after - before).elements()) or '(its file was removed)'}"
          f" / removed numbers: {sorted((before - after).elements())}")


if __name__ == "__main__":
    main()
