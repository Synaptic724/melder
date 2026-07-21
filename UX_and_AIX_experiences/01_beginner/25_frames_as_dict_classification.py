"""
TIER: beginner (25)
GOAL: Spellframes are CATEGORIES. Organize one world's spells by the
      resolution ideas your app already has - "repositories",
      "notifiers" - and (category, name) becomes the full address.
      The addressing FEELS like a two-level dict, but frames are NOT
      dicts: they are grouping and contract keys. A string frame
      groups; a Protocol frame also VALIDATES what binds under it
      (intermediate tier).
      Seed for later: when a category needs its own OWNER and its own
      resolution conditions, the category graduates into a whole
      CONDUIT - that story is intermediate lesson 26.
SURFACE EXERCISED: spellframe + binding_name as a category address space
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

    # melding = looking up a category member by its full address
    users = conduit.meld(spell=UsersRepo, spellframe="repositories",
                         binding_name="users")
    email = conduit.meld(spell=EmailNotifier, spellframe="notifiers",
                         binding_name="email")
    assert isinstance(users, UsersRepo) and isinstance(email, EmailNotifier)
    print("categories addressed as [category][name]: repositories, notifiers")


if __name__ == "__main__":
    main()
