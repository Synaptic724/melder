"""How conjure reports a spell that only CONSUMES a two-spell cycle (CycleA <-> CycleB, Consumer(a: CycleA))."""
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class CycleA:
    def __init__(self, b: "CycleB") -> None:
        self.b = b


class CycleB:
    def __init__(self, a: CycleA) -> None:
        self.a = a


class Consumer:
    def __init__(self, a: CycleA) -> None:
        self.a = a


def main() -> None:
    """Bind the three spells, conjure, print the outcome."""
    book = Spellbook()
    for cls in (CycleA, CycleB, Consumer):
        book.bind(spell=cls, existence=Existence.many, permissions="create")
    try:
        book.conjure(dynamic=True, name="root")
    except Exception as error:
        print(f"RAISED {type(error).__module__}.{type(error).__qualname__}")
        print(str(error))
        return
    print("CONJURED")


if __name__ == "__main__":
    main()
