"""
TIER: beginner (27)
GOAL: App structure 101 - main() owns the conduit and PASSES it to the
      functions that need things. Don't re-conjure, don't stash globals:
      the conduit is the world handle, hand it around like one.
SURFACE EXERCISED: the conduit as an argument
"""
import melder as md


class Mailer:
    def send(self, to: str) -> str:
        return "sent to " + to


def welcome_new_user(conduit: md.Conduit, username: str) -> str:
    mailer = conduit.meld(spell=Mailer)
    return mailer.send(username)


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Mailer, existence="unique")
    conduit = book.conjure()

    first = welcome_new_user(conduit, "ada")
    second = welcome_new_user(conduit, "grace")
    print(first)
    print(second)

    # The function got a real world handle, not a copy of one.
    assert first == "sent to ada"
    assert second == "sent to grace"

    # AND IT IS THE SAME WORLD. `existence="unique"` means one Mailer, so
    # two calls in two different functions melded the SAME object. That is
    # the whole reason to pass the conduit instead of re-conjuring: a
    # second conjure would have built a second world with its own Mailer,
    # and these two would not be the same object.
    assert conduit.meld(spell=Mailer) is conduit.meld(spell=Mailer)
    print("one world handle, passed where needed - and the SAME Mailer")
    print("  answered both calls, which is what re-conjuring would break")


if __name__ == "__main__":
    main()
