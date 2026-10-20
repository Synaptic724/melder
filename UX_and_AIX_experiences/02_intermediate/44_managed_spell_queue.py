"""
TIER: intermediate (44)
GOAL: Wait for a pooled object instead of failing - managed_spell_mode="queue".
      A queue pool is limited_quantity with patience: at its limit a meld WAITS for a
      release, up to managed_spell_timeout_seconds (required for a queue, refused for
      the other modes). A release hands the waiting meld the released object. When the
      timeout passes first, the meld raises ManagedSpellExhaustedError naming the
      queue, its limit and its timeout.

      The timeout bounds every wait, so a queue never blocks forever: choose it from
      how long a caller may afford to wait for a turn.
SURFACE EXERCISED: md.Spellbook.bind (managed_spell_mode, managed_spell_limit,
                   managed_spell_timeout_seconds), md.ManagedSpellMode.queue,
                   md.Conduit.meld, md.ManagedSpellExhaustedError (mode, limit,
                   timeout_seconds), md.ReleaseManagedSpell (release, describe),
                   md.Conduit.cleanup
"""
import threading
import time
from typing import List, Tuple

import melder as md


class GpuSlot:
    """The one GPU slot a renderer may use; callers queue for it.

    Bound with a generous timeout, so a waiting meld is served by a release.
    """

    def __init__(self) -> None:
        """Reserve the slot; `jobs` counts the work done with it."""
        self.jobs: int = 0


class ExportSlot:
    """A single export slot bound with a short timeout, to show the queue's refusal."""

    def __init__(self) -> None:
        """Reserve the slot."""
        self.jobs: int = 0


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def main() -> None:
    """Hand a released slot to a waiting meld, then let a short wait run out.

    Contract:
        The waiting meld runs on a second thread. Its outcome is deterministic: the
        pool's only slot is out, so the waiter can only finish after the release,
        and it then holds exactly that slot. The refusal asserts the wait lasted at
        least the bound timeout and carries the queue's policy.
    Returns:
        None.
    """
    book = md.Spellbook()
    try:
        book.bind(
            spell=GpuSlot,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_mode=md.ManagedSpellMode.queue,
            managed_spell_limit=1,
            managed_spell_timeout_seconds=5.0,
        )
        book.bind(
            spell=ExportSlot,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_mode="queue",
            managed_spell_limit=1,
            managed_spell_timeout_seconds=0.25,
        )
        conduit = book.conjure()
        try:
            held: GpuSlot = conduit.meld("GpuSlot")
            held.jobs += 1
            received: List[GpuSlot] = []
            started = threading.Event()

            def wait_for_slot() -> None:
                """Meld a GpuSlot; with the only slot out, this waits for a release."""
                started.set()
                received.append(conduit.meld("GpuSlot"))

            waiter = threading.Thread(target=wait_for_slot, name="renderer-2")
            waiter.start()
            started.wait()
            time.sleep(0.2)
            # The only slot is out, so the waiter cannot have finished.
            assert waiter.is_alive() and not received
            print("the second renderer is queued while the slot is out:", waiter.is_alive())

            md.ReleaseManagedSpell().release(held)
            waiter.join(timeout=5.0)
            assert not waiter.is_alive()
            assert received and received[0] is held and received[0].jobs == 1
            assert pool_counts(GpuSlot) == (1, 0, 1)
            print("the release handed the same slot to the waiting renderer:", received[0] is held)
            md.ReleaseManagedSpell().release(received[0])

            # A short timeout: the wait runs out and the meld is refused.
            busy: ExportSlot = conduit.meld("ExportSlot")
            began = time.monotonic()
            try:
                conduit.meld("ExportSlot")
                raise AssertionError("a second export slot was leased past the limit")
            except md.ManagedSpellExhaustedError as refused:
                waited = time.monotonic() - began
                assert waited >= 0.25
                assert refused.mode == "queue" and refused.limit == 1
                assert refused.timeout_seconds == 0.25
                print(f"the export queue gave up after {waited:.2f} s:", refused.mode, "timeout", refused.timeout_seconds)
            md.ReleaseManagedSpell().release(busy)
            assert pool_counts(ExportSlot) == (1, 1, 0)
        finally:
            conduit.cleanup()
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
