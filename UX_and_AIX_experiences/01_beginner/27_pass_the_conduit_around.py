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

    print(welcome_new_user(conduit, "ada"))
    print(welcome_new_user(conduit, "grace"))
    print("one world handle, passed where needed")


if __name__ == "__main__":
    main()
