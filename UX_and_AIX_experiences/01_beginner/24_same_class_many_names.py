"""
TIER: beginner (24)
GOAL: One spell name, one visible spell - CURRENT RUNTIME TRUTH (probe-
      proven): conjure refuses ANY two spells sharing a name, even
      across frames, even with different internals. The working pattern
      for one shape in many roles: tiny subclasses, one name each.
      (The probe suite flags the intended SHA-content semantics as an
      open runtime question - the lesson here is what works TODAY.)
SURFACE EXERCISED: subclass-per-role registration, mixed lifecycles
"""
import melder as md


class Buffer:
    pass


class SharedBuffer(Buffer):
    pass


class ScratchBuffer(Buffer):
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=SharedBuffer, existence="unique",
              spellframe="pools", binding_name="shared")
    book.bind(spell=ScratchBuffer, existence="many",
              spellframe="pools", binding_name="scratch")
    conduit = book.conjure()

    shared_a = conduit.meld(spellframe="pools", binding_name="shared")
    shared_b = conduit.meld(spellframe="pools", binding_name="shared")
    scratch_a = conduit.meld(spellframe="pools", binding_name="scratch")
    scratch_b = conduit.meld(spellframe="pools", binding_name="scratch")
    assert shared_a is shared_b
    assert scratch_a is not scratch_b
    assert isinstance(shared_a, Buffer) and isinstance(scratch_a, Buffer)
    print("one shape, two roles via subclasses: shared + scratch")


if __name__ == "__main__":
    main()
