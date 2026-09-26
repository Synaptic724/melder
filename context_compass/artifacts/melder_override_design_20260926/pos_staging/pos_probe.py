"""Probe: call shape a class receives when melded through each family (keyword vs positional)."""
import sys
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class A:
    def __init__(self) -> None:
        pass


class NewBase:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.seen = (len(args), tuple(sorted(kwargs)))
        return instance


class InheritedNewMany(NewBase):
    def __init__(self, a: A) -> None:
        self.a = a


class InheritedNewShared(NewBase):
    def __init__(self, a: A) -> None:
        self.a = a


def run(existence_root: Existence, existence_dep: Existence, root_cls: type, tag: str) -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame=f"pos-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    book.bind(spell=A, existence=existence_dep, permissions="create")
    root_id = book.bind(spell=root_cls, existence=existence_root, permissions="create")
    conduit = book.conjure()
    first = conduit.meld(spell_id=root_id)
    print(f"{tag:28s} seen(args, kwargs)={first.seen}")
    book.cleanup()


run(Existence.many, Existence.many, InheritedNewMany, "many_only (all many)")
run(Existence.unique_per_conduit, Existence.many, InheritedNewShared, "generalized (upc root)")
