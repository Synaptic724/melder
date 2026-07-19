"""
TIER: beginner (26)
GOAL: Melding without the class in hand - binding_name alone can be the
      whole address (the lambda example already leaned on this; here it
      is the headline). The class stays an implementation detail.
SURFACE EXERCISED: md.Conduit.meld(binding_name=...) with no spell object
"""
import melder as md


class HiddenImplementation:
    def answer(self) -> int:
        return 42


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=HiddenImplementation, existence="unique",
              binding_name="the-service")
    conduit = book.conjure()

    service = conduit.meld(binding_name="the-service")
    assert service is not None and service.answer() == 42
    print("resolved by name alone:", service.answer())


if __name__ == "__main__":
    main()
