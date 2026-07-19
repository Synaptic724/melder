"""
TIER: beginner (01)
GOAL: The sixty-second first contact - bind one class, conjure a conduit,
      meld an instance. The whole DGR in four lines.
SURFACE EXERCISED: md.Spellbook, md.Existence, md.Conduit (returned type)
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


class Greeter:
    """A plain user class - melder needs no base class, no metaclass."""

    def greet(self) -> str:
        return "hello from a melded instance"


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Greeter, existence=md.Existence.unique)
    conduit = book.conjure()

    greeter = conduit.meld(spell=Greeter)
    assert isinstance(greeter, Greeter)
    assert isinstance(conduit, md.Conduit)
    print(greeter.greet())

    # unique existence means the SAME instance comes back every meld
    again = conduit.meld(spell=Greeter)
    assert again is greeter
    print("unique lifecycle held:", again is greeter)


if __name__ == "__main__":
    main()
