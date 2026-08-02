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
"""
import melder as md


class TenantCache:
    pass


def main() -> None:
    # Two books, two WORLDS. Naming the frame births it (lazy frames).
    book_a = md.Spellbook(aetheric_frame="tenant-a")
    book_b = md.Spellbook(aetheric_frame="tenant-b")

    # The SAME class, the same shape, in both worlds - no collision:
    # name uniqueness is a per-frame law, and these are different frames.
    book_a.bind(spell=TenantCache, existence="unique")
    book_b.bind(spell=TenantCache, existence="unique")

    conduit_a = book_a.conjure()
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
