"""
TIER: intermediate (48)
GOAL: Change a pool's settings and hand a pool to another root (dynamic mode).
      A managed spell's mode, limit, queue timeout and reset methods are SETTINGS of
      the spell, not part of its spell_id. To change them, cleanup_spell the spell and
      bind it again: the spell_id stays the same, and so does its pool - every object
      alive stays alive and counted, and the pool takes the new settings.

      An ownership transfer moves the spell to another root, and the pool goes with it,
      idle objects included. The new owner leases from it; releases keep routing by
      class, so holders change nothing.
SURFACE EXERCISED: md.Spellbook.conjure(dynamic=True), md.Conduit.bind (managed
                   options), md.Conduit.cleanup_spell, md.Conduit.get_spell_by_spell_id,
                   md.Conduit.link, md.Conduit.transfer_spell_ownership,
                   md.ManagedSpellExhaustedError, md.ReleaseManagedSpell (release,
                   release_all, describe), md.Conduit.cleanup
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class ExportWorker:
    """A pooled export worker; `close` disposes it when its pool destroys it."""

    def __init__(self) -> None:
        """Start the worker."""
        self.closed: bool = False

    def close(self) -> None:
        """Stop the worker for good."""
        self.closed = True


def pool_snapshot(cls: type) -> Dict[str, Any]:
    """Return the one pool snapshot of a managed class (this lesson binds it once)."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    snapshot = pool_snapshot(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def raise_the_limit(reports: md.Conduit, spell_id: str) -> List[ExportWorker]:
    """Fill a limit-1 pool, rebind it with limit 3, lease up to the new limit.

    Contract:
        The rebind keeps the spell_id and the pool: the worker that was out stays
        alive and counted under the new limit. Every worker is released at the end.
    Args:
        reports: The dynamic root that owns the managed spell.
        spell_id: The spell_id the first bind returned.
    Returns:
        List[ExportWorker]: The three workers the pool now holds, all idle.
    """
    busy: ExportWorker = reports.meld("ExportWorker")
    try:
        reports.meld("ExportWorker")
        raise AssertionError("limit 1 leased a second worker")
    except md.ManagedSpellExhaustedError:
        print("limit 1: a second worker is refused while one is out")

    # Settings are not identity: rebinding with a higher limit keeps the spell_id and the pool.
    reports.cleanup_spell(spell=reports.get_spell_by_spell_id(spell_id))
    rebound_id = reports.bind(
        spell=ExportWorker,
        existence=md.Existence.managed_spell_quantity,
        managed_spell_mode="limited_quantity",
        managed_spell_limit=3,
        disposal_method_names=["close"],
    )
    assert rebound_id == spell_id
    assert pool_snapshot(ExportWorker)["limit"] == 3
    assert pool_counts(ExportWorker) == (1, 0, 1) and not busy.closed
    print("rebound with limit 3, same spell_id; the busy worker still counts:", pool_counts(ExportWorker))

    workers = [busy, reports.meld("ExportWorker"), reports.meld("ExportWorker")]
    assert pool_counts(ExportWorker) == (3, 0, 3)
    md.ReleaseManagedSpell().release_all(workers)
    assert pool_counts(ExportWorker) == (3, 3, 0)
    print("three workers under the new limit, all back:", pool_counts(ExportWorker))
    return workers


def transfer_the_pool(reports: md.Conduit, archive: md.Conduit, spell_id: str, workers: List[ExportWorker]) -> None:
    """Transfer the managed spell to another root and lease from the moved pool.

    Contract:
        After the transfer the pool lives in the archive root's store, with its idle
        workers; the archive leases them, the old owner can no longer meld the spell.
    Args:
        reports: The current owner.
        archive: The new owner, linked from `reports`.
        spell_id: The managed spell's spell_id.
        workers: The pool's idle workers before the transfer.
    Returns:
        None.
    """
    assert pool_snapshot(ExportWorker)["holding_conduit_id"] == reports.id
    reports.link(archive)
    reports.transfer_spell_ownership(spell=spell_id, target_conduit=archive)
    assert pool_snapshot(ExportWorker)["holding_conduit_id"] == archive.id
    assert pool_counts(ExportWorker) == (3, 3, 0)
    moved: ExportWorker = archive.meld("ExportWorker")
    assert any(moved is worker for worker in workers)
    print("the archive root now holds the pool and leases its idle workers:", pool_counts(ExportWorker))

    try:
        reports.meld("ExportWorker")
        raise AssertionError("the old owner still melds the transferred spell")
    except KeyError as gone:
        print("the old owner can no longer meld it:", type(gone).__name__)
    md.ReleaseManagedSpell().release(moved)
    assert pool_counts(ExportWorker) == (3, 3, 0)


def main() -> None:
    """Raise a pool's limit by rebinding, then transfer the spell and its pool.

    Contract:
        Both roots and both books are cleaned in finally blocks; the archive root's
        teardown disposes the idle workers its moved pool holds.
    Returns:
        None.
    """
    reports_book = dynamic_spellbook()
    try:
        spell_id = reports_book.bind(
            spell=ExportWorker,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_mode="limited_quantity",
            managed_spell_limit=1,
            disposal_method_names=["close"],
        )
        reports = reports_book.conjure(dynamic=True, name="reports")
        try:
            archive_book = dynamic_spellbook()
            try:
                archive = archive_book.conjure(dynamic=True, name="archive")
                try:
                    workers = raise_the_limit(reports, spell_id)
                    transfer_the_pool(reports, archive, spell_id, workers)
                finally:
                    archive.cleanup()
                # The new owner's teardown disposed the idle workers its pool held.
                assert all(worker.closed for worker in workers)
                print("the new owner's teardown closed the pooled workers:", len(workers))
            finally:
                archive_book.cleanup()
        finally:
            reports.cleanup()
    finally:
        reports_book.cleanup()


if __name__ == "__main__":
    main()
