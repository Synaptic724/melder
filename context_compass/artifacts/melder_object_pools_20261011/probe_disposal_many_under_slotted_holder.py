"""
Probe: is a disposal-bearing `many` dependency disposed while a longer-lived holder still holds it?

Question (pools epic, HYPOTHESIS note of 2026-10-11): a `many` child built inside a slotted holder's
miss registers in the meld's innermost scope store, while the holder publishes in its own store.
When the holder's store outlives that scope, does the scope's exit dispose the child under a holder
that later melds return again?

Cases, all through the public API on one automatic root:
    A. `unique_per_conduit` holder first built inside a spellspace; the space exits.
    B. `unique` holder first built through a lesser conduit; the lesser returns to its pool.
    C. Control: `unique_per_conduit` holder first built at the root conduit itself.

Run on a copy of `src` (the conjure cache writes under the package root):
    PYTHONPATH=<copy>/src PYTHONDONTWRITEBYTECODE=1 python probe_disposal_many_under_slotted_holder.py
"""
import sys

from melder import Existence, Spellbook


class Child:
    """A `many` dependency with one disposal method that records that it ran."""

    def __init__(self) -> None:
        """Start open."""
        self.closed = False

    def close(self) -> None:
        """Disposal method Melder calls when the store holding this child retires."""
        self.closed = True


class HolderPerConduit:
    """`unique_per_conduit` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class HolderUnique:
    """`unique` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class ControlHolder:
    """`unique_per_conduit` holder built at the root conduit (control case)."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


def report(line: str) -> None:
    """Write one result line to stdout."""
    sys.stdout.write(line + "\n")


def main() -> int:
    """Run the three cases and return 0; the printed lines are the evidence."""
    book = Spellbook()
    book.bind(spell=Child, existence=Existence.many, disposal_method_names=["close"])
    per_conduit_id = book.bind(spell=HolderPerConduit, existence=Existence.unique_per_conduit)
    unique_id = book.bind(spell=HolderUnique, existence=Existence.unique)
    control_id = book.bind(spell=ControlHolder, existence=Existence.unique_per_conduit)
    root = book.conjure(name="probe_root")
    try:
        with root.enter_spellspace() as space:
            holder_a = space.meld(spell_id=per_conduit_id)
            report(f"A inside the spellspace: child closed={holder_a.child.closed}")
        again_a = root.meld(spell_id=per_conduit_id)
        report(
            f"A after the spellspace exit: root meld returns the same holder={again_a is holder_a}, "
            f"its child closed={again_a.child.closed}"
        )

        lesser = root.create_lesser_conduit()
        holder_b = lesser.meld(spell_id=unique_id)
        report(f"B inside the lesser: child closed={holder_b.child.closed}")
        lesser.cleanup()
        again_b = root.meld(spell_id=unique_id)
        report(
            f"B after the lesser's pool return: root meld returns the same holder={again_b is holder_b}, "
            f"its child closed={again_b.child.closed}"
        )

        holder_c = root.meld(spell_id=control_id)
        with root.enter_spellspace() as space:
            space.meld(spell_id=control_id)
        report(f"C control after a spellspace cycle: child closed={holder_c.child.closed}")
    finally:
        root.permanent_cleanup()
    report(f"C control after root teardown: child closed={holder_c.child.closed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
