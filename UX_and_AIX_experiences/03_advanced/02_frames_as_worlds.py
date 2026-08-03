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

      A spell_id is a SHA256 over the BIND FINGERPRINT - structural
      profile, lookup signature, existence, resolved disposal metadata.
      READ THAT LIST AGAIN AND NOTICE WHAT IS ABSENT: the frame. So two
      books on two different frames binding the same class with the same
      parameters mint THE SAME ID, and the second conjure is refused
      process-wide. Moving to another frame is not a fix, because the id
      follows the fingerprint and the fingerprint has no frame in it.

      The fix is to make the BINDINGS different, not the worlds:
      `binding_name=` or `spellframe=`. Once you do, everything you
      expect from a world wall holds - `unique` is one instance PER
      FRAME, each world reuses its own singleton forever, and nothing
      leaks across.

      WHY IT IS BUILT THIS WAY: one spell_id names one spell, everywhere.
      An id that silently meant different things in different frames
      would make every checkpoint, every crystal and every research lane
      ambiguous the moment two frames existed.
SURFACE EXERCISED: Spellbook(aetheric_frame=...), binding_name as the
                   identity differentiator, per-frame instance isolation
VERIFY: rides the owner's 3.14t run; asserts are the contract.

HISTORY: this lesson used to teach that two frames could bind the same
class under the same name "with zero collision", and it carried a note
warning that S2 of EPIC-2026-08-02-process-wide-spell-id-uniqueness would
retire exactly that claim. S2 landed. The claim is retired, and the
lesson now teaches the line instead of the half of it that survived.
"""
import melder as md


class TenantCache:
    pass


def main() -> None:
    # Two books, two WORLDS. Naming the frame births it (lazy frames).
    book_a = md.Spellbook(aetheric_frame="tenant-a")
    book_b = md.Spellbook(aetheric_frame="tenant-b")

    # THE SAME CLASS IN BOTH WORLDS - but the BINDINGS must differ.
    # Bind these two identically and the second conjure is refused: the
    # fingerprint would be byte-identical and the frame is not in it.
    book_a.bind(spell=TenantCache, existence="unique", binding_name="tenant-a")
    book_b.bind(spell=TenantCache, existence="unique", binding_name="tenant-b")

    conduit_a = book_a.conjure(name="cache-a")
    conduit_b = book_b.conjure(name="cache-b")

    cache_a = conduit_a.meld(spell=TenantCache, binding_name="tenant-a")
    cache_b = conduit_b.meld(spell=TenantCache, binding_name="tenant-b")

    # "unique" = one instance per FRAME. Two frames, two singletons.
    assert type(cache_a) is type(cache_b) is TenantCache
    assert cache_a is not cache_b
    print("one class, two worlds, two singletons:", cache_a is not cache_b)

    # Each world reuses ITS OWN singleton, forever.
    assert conduit_a.meld(spell=TenantCache, binding_name="tenant-a") is cache_a
    assert conduit_b.meld(spell=TenantCache, binding_name="tenant-b") is cache_b
    print("per-frame reuse holds; nothing leaked across the wall")

    # THE LINE, PROVEN. A third world binding the SAME class the SAME way
    # as tenant-a is refused - and the refusal names the id, not the
    # frame, because the frame was never what made them different.
    book_c = md.Spellbook(aetheric_frame="tenant-c")
    try:
        book_c.bind(spell=TenantCache, existence="unique",
                    binding_name="tenant-a")
        book_c.conjure(name="cache-c")
        raise AssertionError("expected a process-wide spell_id refusal")
    except RuntimeError as error:
        assert "spell_id" in str(error) or "Spell ID" in str(error)
        print()
        print("a third frame with an IDENTICAL binding was refused:")
        print("  frames isolate instances; they do not namespace identity")


if __name__ == "__main__":
    main()
