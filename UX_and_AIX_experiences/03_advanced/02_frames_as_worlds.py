"""
TIER: advanced (02)
GOAL: Aetheric frames are WORLDS - the categories arc, act three.
      Act 1 (beginner 25): spellframes categorize spells WITHIN a world.
      Act 2 (intermediate 26): conduits categorize worlds of resolution.
      Act 3: aetheric_frame= names an ENTIRE ISOLATED WORLD - its own
      registries, its own control plane, its own posture, its own
      singletons.

      AND THE LINE THAT WALL DOES NOT CROSS, which is the real lesson:

        A FRAME IS A WORLD FOR INSTANCES AND RESOLUTION.
        IT IS NOT A NAMESPACE FOR IDENTITY.

      A spell_id is the SHA256 of the registered object's CODE - its
      methods and constructor, its class-level values, its bases - and
      of nothing from the bind call. READ THAT AGAIN AND NOTICE WHAT IS
      ABSENT: the frame, the spellframe, the binding_name. So two books
      on two different frames binding the same class mint THE SAME ID,
      whatever names they give it, and the second registration is
      refused process-wide. Moving to another frame is not a fix, and
      neither is another binding_name: one object is one spell.

      The fix is to make the CLASSES different, not the worlds or the
      names: one subclass per world. A subclass is a new class, so a new
      spell_id, and every world can then keep it at the SAME address.
      Once you do, everything you expect from a world wall holds -
      `unique` is one instance PER FRAME, each world reuses its own
      singleton forever, and nothing leaks across.

      THE OTHER WAY is a regime, not a binding: with
      `process_wide_unique_spell_ids` turned off before the first frame
      exists, a spell_id is unique per FRAME, and one class may live in
      several worlds. That is Aether configuration, and a lesson never
      installs it - lessons share one interpreter (advanced 07). The
      probe suite pins it in a reset world.

      WHY IT IS BUILT THIS WAY: one spell_id names one spell, everywhere.
      An id that silently meant different things in different frames
      would make every checkpoint, every crystal and every research lane
      ambiguous the moment two frames existed.
SURFACE EXERCISED: Spellbook(aetheric_frame=...), one class per world at
                   one address, per-frame instance isolation
VERIFY: rides the owner's 3.14t run; asserts are the contract.

HISTORY: this lesson used to teach that two frames could bind the same
class under the same name "with zero collision", and it carried a note
warning that S2 of EPIC-2026-08-02-process-wide-spell-id-uniqueness would
retire exactly that claim. S2 landed. The claim is retired, and the
lesson now teaches the line instead of the half of it that survived.

0.2.8257: a spell_id became the SHA256 of the object's code, with nothing
from the bind call in it, so a binding_name no longer makes one class two
spells. The lesson used to bind TenantCache in both worlds under two
binding_names; each world now binds its own subclass at one address.
"""
import melder as md


class TenantCache:
    pass


class TenantACache(TenantCache):
    """Tenant A's cache - a new class, so its own spell_id."""


class TenantBCache(TenantCache):
    """Tenant B's cache - a new class, so its own spell_id."""


def main() -> None:
    # Two books, two WORLDS. Naming the frame births it (lazy frames).
    book_a = md.Spellbook(aetheric_frame="tenant-a")
    book_b = md.Spellbook(aetheric_frame="tenant-b")

    # ONE ADDRESS IN BOTH WORLDS, ONE CLASS PER WORLD. Binding TenantCache
    # itself in both would be refused: its spell_id is its code, the same
    # in every frame, and neither the frame nor a binding_name is in it.
    book_a.bind(spell=TenantACache, existence="unique",
                spellframe="tenant", binding_name="cache")
    book_b.bind(spell=TenantBCache, existence="unique",
                spellframe="tenant", binding_name="cache")

    conduit_a = book_a.conjure(name="cache-a")
    conduit_b = book_b.conjure(name="cache-b")

    # The same address melds each world's own class.
    cache_a = conduit_a.meld(spellframe="tenant", binding_name="cache")
    cache_b = conduit_b.meld(spellframe="tenant", binding_name="cache")

    # "unique" = one instance per FRAME. Two frames, two singletons.
    assert type(cache_a) is TenantACache
    assert type(cache_b) is TenantBCache
    assert isinstance(cache_a, TenantCache) and isinstance(cache_b, TenantCache)
    assert cache_a is not cache_b
    print("one shape, two worlds, two singletons:", cache_a is not cache_b)

    # Each world reuses ITS OWN singleton, forever.
    assert conduit_a.meld(spellframe="tenant", binding_name="cache") is cache_a
    assert conduit_b.meld(spellframe="tenant", binding_name="cache") is cache_b
    print("per-frame reuse holds; nothing leaked across the wall")

    # THE LINE, PROVEN. A third world binding tenant A's class - under a
    # binding_name of its own - is refused, and the refusal names the
    # spell_id: neither the frame nor the name was ever part of it.
    book_c = md.Spellbook(aetheric_frame="tenant-c")
    try:
        book_c.bind(spell=TenantACache, existence="unique",
                    binding_name="another-name")
        book_c.conjure(name="cache-c")
        raise AssertionError("expected a process-wide spell_id refusal")
    except RuntimeError as error:
        assert "spell_id" in str(error) or "Spell ID" in str(error)
        print()
        print("a third frame binding the SAME class was refused:")
        print("  frames isolate instances; they do not namespace identity")


if __name__ == "__main__":
    main()
