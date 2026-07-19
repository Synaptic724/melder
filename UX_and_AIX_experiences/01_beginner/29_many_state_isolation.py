"""
TIER: beginner (29)
GOAL: "many" means ISOLATED - each melded instance owns its own state;
      mutating one never leaks into the next. The confusion this
      example prevents: expecting fresh objects to share anything.
SURFACE EXERCISED: md.Existence "many" state isolation
"""
import melder as md


class Basket:
    def __init__(self) -> None:
        self.items: list[str] = []


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Basket, existence="many")
    conduit = book.conjure()

    first = conduit.meld(spell=Basket)
    first.items.append("apples")
    second = conduit.meld(spell=Basket)
    assert first.items == ["apples"] and second.items == []
    print("fresh instances, fresh state:", first.items, "vs", second.items)


if __name__ == "__main__":
    main()
