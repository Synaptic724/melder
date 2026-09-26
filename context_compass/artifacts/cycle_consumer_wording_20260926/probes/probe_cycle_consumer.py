"""How conjure reports spells that only CONSUME a dependency cycle (one case per process, argv[1]).

Cases:
  member  - Consumer(a: CycleA) with CycleA <-> CycleB.
  inter   - Outer(c: Consumer), Consumer(a: CycleA), CycleA <-> CycleB (Outer reaches the cycle via Consumer).
  selfloop - Tree(node: Node), Node(parent: Node) (a consumer of a self-loop).
"""
import sys

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


class Outer:
    def __init__(self, c: Consumer) -> None:
        self.c = c


class Node:
    def __init__(self, parent: "Node") -> None:
        self.parent = parent


class Tree:
    def __init__(self, node: Node) -> None:
        self.node = node


CASES = {
    "member": (CycleA, CycleB, Consumer),
    "inter": (CycleA, CycleB, Consumer, Outer),
    "selfloop": (Node, Tree),
}


def main() -> None:
    """Bind the case's spells, conjure, print the outcome."""
    book = Spellbook()
    for cls in CASES[sys.argv[1]]:
        book.bind(spell=cls, existence=Existence.many, permissions="create")
    try:
        book.conjure(dynamic=True, name="root")
    except Exception as error:
        print(f"RAISED {type(error).__module__}.{type(error).__qualname__}")
        print(str(error))
        return
    finally:
        book.cleanup()
    print("CONJURED")


if __name__ == "__main__":
    main()
