"""Probe: a version bound inactive BEFORE conjure, notched in AFTER conjure - does its first meld work?"""
import traceback

from melder import Aether, Existence, Spellbook
from melder.aether.conduit.conduit import Conduit


class ServiceA:
    def __init__(self) -> None:
        self.version = "a"


class ServiceB:
    def __init__(self) -> None:
        self.version = "b"


def run(existence: Existence, dynamic: bool) -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    label = f"{existence.name}/{'dynamic' if dynamic else 'automatic'}"
    book = Spellbook()
    if dynamic:
        book._aetheric_frame_configuration.with_system_state("dynamic")
    id_a = book.bind(spell=ServiceA, existence=existence, permissions="create", binding_name="a")
    index = book.find_spell_by_id(id_a).spell_index
    id_b = book.bind_inactive(
        spell=ServiceB, spell_index=index, existence=existence, permissions="create", binding_name="b",
    )
    spell_b = book._get_owned_spell(id_b)
    print(label, "parked B owner store before conjure:", spell_b._owner_creations)
    conduit = book.conjure(name="root", dynamic=dynamic)
    print(label, "parked B owner store after conjure:", type(spell_b._owner_creations).__name__)
    print(label, "meld A ->", type(conduit.meld(spell_id=id_a)).__name__)
    conduit.notch_spell(spell_index=index, spell=spell_b)
    print(label, "B owner store after notch:", type(spell_b._owner_creations).__name__)
    try:
        obj = conduit.meld(spell_id=id_b)
        print(label, "meld B after notch ->", type(obj).__name__)
    except Exception as exc:
        print(label, "meld B after notch FAILED:", type(exc).__name__, str(exc)[:300])
        traceback.print_exc(limit=12)
    conduit.cleanup()


for existence in (Existence.unique, Existence.unique_per_conduit, Existence.many):
    for dynamic in (True,):
        try:
            run(existence, dynamic)
        except Exception:
            traceback.print_exc(limit=8)
Aether._reset_singleton_for_tests()
