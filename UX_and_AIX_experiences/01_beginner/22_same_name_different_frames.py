"""
TIER: beginner (22)
GOAL: binding_name is a SUB-key - the same name under two different
      frames is two different addresses. (frame, name) is always the
      full address; names never collide across frames.
SURFACE EXERCISED: the (frame, name) address space
"""
import melder as md


class UsersRepo:
    kind = "repo"


class UsersApi:
    kind = "api"


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=UsersRepo, existence="unique",
              spellframe="storage", binding_name="users")
    book.bind(spell=UsersApi, existence="unique",
              spellframe="web", binding_name="users")
    conduit = book.conjure()

    repo = conduit.meld(spellframe="storage", binding_name="users")
    api = conduit.meld(spellframe="web", binding_name="users")
    assert repo.kind == "repo" and api.kind == "api"
    print("same name, two frames, two addresses: no collision")


if __name__ == "__main__":
    main()
