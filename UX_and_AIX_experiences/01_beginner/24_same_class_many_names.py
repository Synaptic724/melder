"""
TIER: beginner (24)
GOAL: One class, one spell - a spell_id is the SHA256 of the class's
      code, so the SAME class registers once, whatever binding name or
      lifecycle you give it (beginner 30). The working pattern for one
      shape in many roles: tiny subclasses, one per role - each is a new
      class, so its own spell, at its own address. (Same-NAMED classes
      with different code may also coexist at different addresses since
      0.2.8206; the contract probes pin both rules.)
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
