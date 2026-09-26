"""Render what a user sees when conjure refuses spells. One case per process: probe_error_rendering.py <case>.

Cases: owner (the CommandOps CodecPacket/ClassProfile shapes), ambiguous (a real Phase-3/4 error beside caller
inputs), cycle (a two-spell cycle beside two unrelated spells), scope (a unique spell depending on a
unique_per_spell_space spell, beside an unrelated spell). Prints the exception type and full text, or CONJURED.
"""
import sys
from typing import Any

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class MethodProfile:
    def __init__(self, name: str) -> None:
        self.name = name


class ClassProfile:
    def __init__(self, name: str, qualname: str, module: str, mro: list[str], bases: list[str],
                 methods: dict[str, MethodProfile]) -> None:
        self.name = name


class CodecPacket:
    def __init__(self, v: int, id: str, ts: float, kind: str, intent: str, ttl_ms: int,
                 policy: dict[str, Any], payload: dict[str, Any]) -> None:
        self.v = v


class Repo:
    pass


class RepoA(Repo):
    pass


class RepoB(Repo):
    pass


class Service:
    def __init__(self, repo: Repo, name: str, region: str) -> None:
        self.repo = repo


class CycleA:
    def __init__(self, b: "CycleB") -> None:
        self.b = b


class CycleB:
    def __init__(self, a: CycleA) -> None:
        self.a = a


class Unrelated1:
    def __init__(self, name: str) -> None:
        self.name = name


class Unrelated2:
    def __init__(self, size: int) -> None:
        self.size = size


class Leaf:
    def __init__(self) -> None:
        pass


class Holder:
    def __init__(self, leaf: Leaf) -> None:
        self.leaf = leaf


def main(case: str) -> None:
    book = Spellbook()
    many = Existence.many
    if case == "owner":
        for cls in (MethodProfile, ClassProfile, CodecPacket):
            book.bind(spell=cls, existence=many, permissions="create")
    elif case == "ambiguous":
        for cls in (RepoA, RepoB, Service):
            book.bind(spell=cls, existence=many, permissions="create")
    elif case == "cycle":
        for cls in (CycleA, CycleB, Unrelated1, Unrelated2):
            book.bind(spell=cls, existence=many, permissions="create")
    elif case == "scope":
        book.bind(spell=Leaf, existence=Existence.unique_per_spell_space, permissions="create")
        book.bind(spell=Holder, existence=Existence.unique, permissions="create")
        book.bind(spell=Unrelated1, existence=many, permissions="create")
    else:
        raise SystemExit(f"unknown case {case}")
    try:
        book.conjure(dynamic=True, name="root")
    except Exception as error:
        print(f"RAISED {type(error).__module__}.{type(error).__qualname__}")
        print(str(error))
        return
    print("CONJURED")


if __name__ == "__main__":
    main(sys.argv[1])
