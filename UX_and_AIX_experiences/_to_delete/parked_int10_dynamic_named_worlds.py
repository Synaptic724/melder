"""
TIER: intermediate (10)
GOAL: Dynamic mode - static worlds stand alone; dynamic worlds are
      SOCIAL. conjure(dynamic=True, name=...) registers a NAMED root in
      the frame, and named roots can link() to share across books. This
      is the door to clusters, contracts, and the cloud - and it is why
      dynamic mode waits for tier two. (Canonical pattern lifted from
      the component suite: owner/borrower named roots + link.)
SURFACE EXERCISED: conjure(dynamic=True, name=...), md.Conduit.link
"""
import melder as md


class SharedDirectory:
    pass


def main() -> None:
    owner_book = md.Spellbook()
    owner_book.bind(spell=SharedDirectory, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="owner")

    borrower = md.Spellbook().conjure(dynamic=True, name="borrower")

    linked = owner.link(borrower)
    print("dynamic roots linked:", linked)
    assert linked is True

    # static contrast: a static conjure takes no name and joins nothing -
    # one book, one private world (the whole beginner tier lived there)
    print("static = private world; dynamic = named, linkable, social")


if __name__ == "__main__":
    main()
