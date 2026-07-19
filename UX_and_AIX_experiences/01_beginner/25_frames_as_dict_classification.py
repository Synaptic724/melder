"""
TIER: beginner (25)
GOAL: THE dict-style classifier - spellframes are top-level keys,
      binding names are sub-keys, and (frame, name) is a full address.
      Registering a world feels like populating a two-level dict;
      melding feels like indexing it.
SURFACE EXERCISED: spellframe + binding_name as a dict-shaped address space
"""
import melder as md


class UsersRepo:
    pass


class OrdersRepo:
    pass


class SlackNotifier:
    pass


class EmailNotifier:
    pass


WORLD = {
    "repositories": {"users": UsersRepo, "orders": OrdersRepo},
    "notifiers": {"slack": SlackNotifier, "email": EmailNotifier},
}


def main() -> None:
    book = md.Spellbook()
    for frame, members in WORLD.items():
        for name, cls in members.items():
            book.bind(spell=cls, existence="unique",
                      spellframe=frame, binding_name=name)
    conduit = book.conjure()

    # melding = indexing the classified world
    users = conduit.meld(spell=UsersRepo, spellframe="repositories",
                         binding_name="users")
    email = conduit.meld(spell=EmailNotifier, spellframe="notifiers",
                         binding_name="email")
    assert isinstance(users, UsersRepo) and isinstance(email, EmailNotifier)
    print("dict-style world: 2 frames x 2 names, addressed as [frame][name]")


if __name__ == "__main__":
    main()
