"""
Meld entry-frame overhead probe: price the `Conduit.meld` facade prologue.

Purpose:
    Put a number on the two candidate savings at the OUTERMOST meld door
    (`Conduit.meld`, conduit.py:4062-4097) before either is applied to `src/`:

      1. `self.check_cleaned()` - a full Python call frame per meld for one
         attribute read and one branch. `SpellSpace.meld` (spell_space.py:478)
         performs the same delegation with NO guard at all, and
         `spell_space.py:408,430` document dropping `check_cleaned()`
         deliberately on recycled surfaces. The two meld entry points disagree
         and the guarded one is the hot one.

      2. Skipping keyword marshaling of the four always-`None` keyword-only
         arguments on the warm lane by branching to a bare `door.meld(spell)`.
         NOTE: on CPython 3.10 this measured NEGATIVE - the four `is None`
         compares cost more than the callee's keyword binding against a
         constant kwnames tuple. It is included here so the result can be
         confirmed or overturned on 3.14t rather than assumed either way.

Method:
    Pure synthetic shapes mirroring the real call chain - no melder import, so
    this runs on any interpreter including free-threaded builds. Every variant
    pays the identical outer frame, so the deltas isolate exactly the prologue
    difference and nothing else.

    Shapes measured:
      - current:      `check_cleaned()` frame + 4 keyword arguments
      - inline_check: guard inlined, 4 keyword arguments
      - inline_both:  guard inlined + warm-lane positional branch

Interpretation caveat:
    CPython 3.11 inlined Python-to-Python calls, so the `check_cleaned` frame
    is cheaper on 3.11+ than on 3.10 and the measured saving should shrink.
    The DIRECTION is what this probe is for; the magnitude must come from the
    3.14t run, not from a 3.10 sandbox.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_meld_entry_frame_overhead.py

Env knobs:
    BENCH_ENTRY_ITERS    iterations per variant (default 3000000)
    BENCH_ENTRY_REPEAT   timeit repeat count, best-of (default 7)
"""

import os
import sys
import timeit
from typing import Any, Optional


class _Door:
    """
    Stand-in for `ConduitMeld` with the real keyword-only meld signature.

    Contract:
        - Mirrors `ConduitMeld.meld`'s parameter shape exactly: one positional
          `spell` seat followed by four keyword-only parameters.
        - Performs no work, so the measurement is pure call-shape cost.
    """

    __slots__ = ()

    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_name: Optional[str] = None,
            spellframe: str | object | None = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Any:
        """
        Return the positional spell seat unchanged.

        Returns:
            Any: The `spell` argument as received.
        """
        return spell


class _CleanableBase:
    """
    Stand-in for `Cleanable` carrying the real `check_cleaned` implementation.

    Contract:
        - `check_cleaned` is copied verbatim in shape from
          `utilities/general_base/cleanable.py:129-144`, including the
          `self.__class__.__name__` read that only executes on the raise path.
    """

    __slots__ = ("_cleaned", "_meld")

    def __init__(self) -> None:
        """Initialize the live (uncleaned) state and the delegate door."""
        self._cleaned: bool = False
        self._meld: _Door = _Door()

    def check_cleaned(self) -> None:
        """
        Raise when the object has already been cleaned.

        Raises:
            RuntimeError: If `_cleaned` is set.

        Returns:
            None.
        """
        if self._cleaned:
            raise RuntimeError(
                f"{self.__class__.__name__} has already been cleaned. "
            )


class CurrentShape(_CleanableBase):
    """Current `Conduit.meld` prologue: guard frame plus four keywords."""

    __slots__ = ()

    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_name: Optional[str] = None,
            spellframe: str | object | None = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Any:
        """Delegate exactly as `conduit.py:4062-4097` does today."""
        self.check_cleaned()
        meld_component = self._meld
        return meld_component.meld(
            spell,
            spell_name=spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )


class InlinedCheckShape(_CleanableBase):
    """Guard inlined; keyword marshaling left exactly as-is."""

    __slots__ = ()

    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_name: Optional[str] = None,
            spellframe: str | object | None = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Any:
        """Delegate with the use-after-clean latch read inline."""
        if self._cleaned:
            raise RuntimeError("Conduit has already been cleaned. ")
        meld_component = self._meld
        return meld_component.meld(
            spell,
            spell_name=spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )


class InlinedBothShape(_CleanableBase):
    """Guard inlined plus a warm-lane branch that drops the four keywords."""

    __slots__ = ()

    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_name: Optional[str] = None,
            spellframe: str | object | None = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Any:
        """Delegate, taking a bare positional call when all extras are None."""
        if self._cleaned:
            raise RuntimeError("Conduit has already been cleaned. ")
        meld_component = self._meld
        if (
                spell_name is None
                and spellframe is None
                and binding_name is None
                and spell_override is None
        ):
            return meld_component.meld(spell)
        return meld_component.meld(
            spell,
            spell_name=spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )


def main() -> None:
    """
    Run every variant and print per-call nanoseconds against the baseline.

    Returns:
        None.
    """
    iterations = int(os.environ.get("BENCH_ENTRY_ITERS", "3000000"))
    repeat = int(os.environ.get("BENCH_ENTRY_REPEAT", "7"))

    print(f"[meld-entry] python={sys.version.split()[0]}")
    print(
        "[meld-entry] free_threaded="
        f"{not getattr(sys, '_is_gil_enabled', lambda: True)()}"
    )
    print(f"[meld-entry] iters={iterations} repeat={repeat} (best-of)\n")

    variants = (
        ("current (guard frame + 4 kwargs)", CurrentShape),
        ("inline check_cleaned only", InlinedCheckShape),
        ("inline check + kwarg branch", InlinedBothShape),
    )

    baseline_ns = None
    for label, shape_class in variants:
        subject = shape_class()
        elapsed = min(
            timeit.repeat(
                lambda subject=subject: subject.meld("warm-spell-id"),
                number=iterations,
                repeat=repeat,
            )
        )
        nanoseconds = elapsed / iterations * 1e9
        if baseline_ns is None:
            baseline_ns = nanoseconds
            print(f"[meld-entry] {label:34} {nanoseconds:7.2f} ns   baseline")
            continue
        delta = baseline_ns - nanoseconds
        percent = delta / baseline_ns * 100.0
        sign = "-" if delta >= 0 else "+"
        print(
            f"[meld-entry] {label:34} {nanoseconds:7.2f} ns   "
            f"{sign}{abs(delta):5.2f} ns  ({percent:+5.1f}%)"
        )

    print(
        "\n[meld-entry] A NEGATIVE percent means the variant is SLOWER and the "
        "idea is dead."
    )


if __name__ == "__main__":
    main()
