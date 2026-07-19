"""
TIER: beginner (24)
GOAL: One class, several registrations - the same type binds under
      different names with DIFFERENT lifecycles. The binding, not the
      class, is the unit of vocabulary.
SURFACE EXERCISED: binding_name reuse, mixed Existence on one type
"""
import melder as md


class Buffer:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Buffer, existence="unique",
              binding_name="shared-buffer")
    book.bind(spell=Buffer, existence="many",
              binding_name="scratch-buffer")
    conduit = book.conjure()

    shared_a = conduit.meld(spell=Buffer, binding_name="shared-buffer")
    shared_b = conduit.meld(spell=Buffer, binding_name="shared-buffer")
    scratch_a = conduit.meld(spell=Buffer, binding_name="scratch-buffer")
    scratch_b = conduit.meld(spell=Buffer, binding_name="scratch-buffer")
    assert shared_a is shared_b
    assert scratch_a is not scratch_b
    print("one class, two vocabularies: shared (unique) + scratch (many)")


if __name__ == "__main__":
    main()
