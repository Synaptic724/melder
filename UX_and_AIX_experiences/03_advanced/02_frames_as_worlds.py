"""
TIER: advanced (02)
GOAL: Aetheric frames are WORLDS - the categories arc, act three.
      Act 1 (beginner 25): spellframes categorize spells WITHIN a world.
      Act 2 (intermediate 26): conduits categorize worlds of resolution.
      Act 3: aetheric_frame= names an ENTIRE ISOLATED WORLD - its own
      registries, its own control plane, its own posture, its own
      singletons. Two frames can bind the SAME class under the SAME
      name with zero collision, and "unique" means one instance PER
      FRAME, not per process. Conduits link within a frame, never
      across one - the wall is real.
SURFACE EXERCISED: Spellbook(aetheric_frame=...), per-frame isolation
VERIFY: rides the owner's 3.14t run; asserts are the contract.

BUG FIXED 2026-08-02: this lesson previously named the SAME frame twice
("tenant-a" on both books) while its prose claimed two worlds. It passed
only because duplicate spell_ids across two Spellbooks on one frame were
not yet caught. `_spell_id_integrity_checker` (EPIC-2026-08-02-process-
wide-spell-id-uniqueness, S1) now refuses exactly that at conjure, so the
lesson was about to go red for a good reason. The frames now differ.

ON NOTICE: the checker as landed is PER-FRAME - its own contract says it
refuses "when any spell_id this Spellbook owns is already registered in
the aetheric frame". Per-frame isolation therefore still holds TODAY and
this lesson is correct. S2 of that epic ("unified set", process-wide) is
READY AND UNASSIGNED, and landing it would retire what this lesson
teaches. Whoever picks up S2 should retire or rewrite this lesson in the
same change - the attention board already names this file as the thing
that would be invalidated.
"""
import melder as md


class TenantCache:
    pass


def main() -> None:
    # Two books, two WORLDS. Naming the frame births it (lazy frames).
    # THE FRAME NAMES MUST DIFFER. Two Spellbooks on the SAME frame that
    # bind the same class is not multi-tenancy - it is the duplicate
    # spell_id bug EPIC-2026-08-02-process-wide-spell-id-uniqueness
    # closed, and `_spell_id_integrity_checker` now refuses it at conjure.
    book_a = md.Spellbook(aetheric_frame="tenant-a")
    book_b = md.Spellbook(aetheric_frame="tenant-b")

    # The SAME class, the same shape, in both worlds - no collision:
    # name uniqueness is a per-frame law, and these are different frames.
    book_a.bind(spell=TenantCache, existence="unique")
    book_b.bind(spell=TenantCache, existence="unique")

    conduit_a = book_a.conjure(name="test")
    conduit_b = book_b.conjure()

    cache_a = conduit_a.meld(spell=TenantCache)
    cache_b = conduit_b.meld(spell=TenantCache)

    # "unique" = one instance per FRAME. Two frames, two singletons.
    assert type(cache_a) is type(cache_b) is TenantCache
    assert cache_a is not cache_b
    print("one class, two worlds, two singletons:",
          cache_a is not cache_b)

    # Each world reuses ITS OWN singleton, forever.
    assert conduit_a.meld(spell=TenantCache) is cache_a
    assert conduit_b.meld(spell=TenantCache) is cache_b
    print("per-frame reuse holds; nothing leaked across the wall")


if __name__ == "__main__":
    main()
