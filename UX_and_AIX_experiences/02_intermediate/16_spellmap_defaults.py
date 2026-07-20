"""
TIER: intermediate (16)
GOAL: SpellMap - the declarative DI placeholder. As a constructor
      DEFAULT it declares exactly which spell fills the parameter,
      including frame + binding_name targeting. Exactly-one law:
      ambiguous or missing targets fail at conjure, not at runtime.
SURFACE EXERCISED: md.SpellMap as a constructor default
"""
import melder as md


class PrimaryStore:
    label = "primary"


class Consumer:
    def __init__(self, store=md.SpellMap(PrimaryStore)) -> None:
        self.store = store


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=PrimaryStore, existence="unique")
    book.bind(spell=Consumer, existence="unique")
    conduit = book.conjure()

    consumer = conduit.meld(spell=Consumer)
    assert isinstance(consumer.store, PrimaryStore)
    print("SpellMap default resolved:", consumer.store.label)


if __name__ == "__main__":
    main()
