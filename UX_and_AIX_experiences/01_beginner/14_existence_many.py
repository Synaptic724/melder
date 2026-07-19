"""
TIER: beginner (14)
GOAL: many, studied closely - construction EVERY meld, no caching anywhere.
      The mode for request-shaped, disposable things.
SURFACE EXERCISED: md.Existence.many
"""
import melder as md


class WorkOrder:
    counter = 0

    def __init__(self) -> None:
        WorkOrder.counter += 1
        self.number = WorkOrder.counter


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=WorkOrder, existence="many")
    conduit = book.conjure()

    orders = [conduit.meld(spell=WorkOrder) for _ in range(4)]
    assert len({id(o) for o in orders}) == 4
    assert [o.number for o in orders] == [1, 2, 3, 4]
    print("many: four melds, four fresh WorkOrders:", [o.number for o in orders])


if __name__ == "__main__":
    main()
