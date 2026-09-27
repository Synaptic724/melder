"""Render what a user sees for self-referencing constructors. One case per process: probe_self_dependency.py <case>.

Cases:
  single      Node(parent: Node, name: str) alone
  mixed       Node, an unrelated spell, and Tree(root: Node) that consumes Node
  collection  Branch(children: list[Branch])
  default     Leaf(parent: Optional[Leaf] = None) - a default makes the parameter plain (control)
  late        dynamic world: conjure with one unrelated spell, then bind Node and meld it
Prints the exception type and full text, or CONJURED / MELDED.
"""
import sys
from typing import Optional

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Node:
    def __init__(self, parent: "Node", name: str) -> None:
        self.parent = parent


class Unrelated:
    def __init__(self) -> None:
        pass


class Tree:
    def __init__(self, root: Node) -> None:
        self.root = root


class Branch:
    def __init__(self, children: list["Branch"]) -> None:
        self.children = children


class Leaf:
    def __init__(self, parent: Optional["Leaf"] = None) -> None:
        self.parent = parent


def main(case: str) -> None:
    """Bind the case's classes, conjure (and meld for `late`), print the outcome."""
    book = Spellbook()
    many = Existence.many
    try:
        if case == "late":
            book.bind(spell=Unrelated, existence=many, permissions="create")
            conduit = book.conjure(dynamic=True, name="root")
            book.bind(spell=Node, existence=many, permissions="create")
            conduit.meld(spell=Node, override={"parent": None, "name": "n"})
            print("MELDED")
            return
        classes = {"single": (Node,), "mixed": (Node, Unrelated, Tree), "collection": (Branch,),
                   "default": (Leaf,)}[case]
        for cls in classes:
            book.bind(spell=cls, existence=many, permissions="create")
        book.conjure(dynamic=True, name="root")
    except Exception as error:
        print(f"RAISED {type(error).__module__}.{type(error).__qualname__}")
        print(str(error))
        return
    print("CONJURED")


if __name__ == "__main__":
    main(sys.argv[1])
