"""
Per-test world isolation for the example harness.

WHY THIS RESETS FIVE SINGLETONS AND NOT ONE
-------------------------------------------
This fixture used to reset only `Aether`, mirroring the component suite's
frame-truth fixture. That was sufficient while examples stayed below the
substrate - beginner, intermediate and advanced never touch the hosted
roots. EXPERT DOES, and the omission surfaced as a real red on the
2026-08-04 owner run.

`test_expert_probes.py` already carries the correct fixture and states the
reason exactly: "All five carry process-wide state; without the reset one
row's checkpoints, profiles or research lanes surface in the next row."
The PROBES had that isolation; the EXAMPLES did not, so expert lessons ran
against whatever record the previous lesson left behind.

WHAT THAT LOOKED LIKE, so the next reader recognises it
-------------------------------------------------------
Expert 27 seals a checkpoint, tears the runtime down, and unfolds the
record into a fresh root. It failed at admission with

    owning spellbook '01K...' is not in this bundle; the custody cannot
    bind ... nothing was built

and the run reported SEVENTY-SIX cached checkpoint ids in a session where
that lesson mints exactly one. `Aether` was being reset between examples
while `Crystallizer` was not, so each lesson's frames were cleaned out from
under a record that survived them - leaving custody rows whose owning
spellbook had been evicted, in a profile shared by every example in the
file. A whole-world load then folds that shared chain and refuses.

THE ORDER MATTERS
-----------------
Reset the hosted roots BEFORE `Aether`, then construct a fresh `Aether`
and rebind the class seams. `Aether` boots the hosted singletons, so
resetting it first and the children second would leave the fresh root
holding children that are about to be discarded.
"""
import pytest

from melder import Aether, Conduit, Crystallizer, MutationResearch, Nexus
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_world_per_example() -> None:
    """
    Purpose:
        Every example runs in a FRESH world - no shared frames, no
        root-conduit name collisions, and no inherited record.

    Contract:
        - Resets the four process-wide roots plus `Aether`, matching
          `test_expert_probes.py`'s fixture rather than the narrower
          Aether-only reset this file used to carry.
        - Runs before AND after every example, so a lesson cannot leak
          into its neighbour in either direction.
        - Rebinds the `Spellbook`/`Conduit` class seams to the fresh
          `Aether`, which is what makes the new root the one those types
          resolve against.
    """
    def _fresh() -> None:
        MutationResearch._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _fresh()
    yield
    _fresh()
