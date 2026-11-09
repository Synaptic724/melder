"""Departure-path probe (patch hidden_provider_2026_11_07, the UNKNOWN "which departure paths announce the removed
spell's frame key"; implementation subagent of melder_0, 2026-11-07).

A consumer `ByClass(greeter: English)` is refused (HIDDEN_PROVIDER) while English is filed under the Protocol frame
Greeter; English then departs by one public path - in a borrower: remove_spell_from_contract, sever_link, the lender's
cleanup_spell, remove_index_from_contract; in its own Book: cleanup_spell. Each step prints the consumer's validity and
sockets, every `mark_collection_dependents_dirty` call ([mark] keys -> consumers reached; diagnosis only, through a
class-level wrapper in this process), the refused consumer's next meld (LIVE) and a fresh twin's bind and meld (FRESH).

Run: python -X gil=0 departure_marks_probe.py  (and -X gil=1). Writes nothing outside the process.
"""
from typing import Protocol

from melder import Aether, Conduit, Spellbook
from melder.aether.spellbook.existence.existence import Existence

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
_original_watch = SpellSystemStates.mark_collection_dependents_dirty


def _watch(self, *, spellbook_id, frame_keys, change_reason=None):
    keys = sorted({key for key in frame_keys if key})
    impacted = _original_watch(self, spellbook_id=spellbook_id, frame_keys=keys, change_reason=change_reason)
    print(f"    [mark] {keys} -> {len(impacted)} reached")
    return impacted


SpellSystemStates.mark_collection_dependents_dirty = _watch


class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class ByClass:
    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


class LateByClass:
    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


def attempt(fn):
    try:
        value = fn()
    except Exception as error:  # scratch measurement only
        return f"raises {type(error).__name__}: {str(error)[:260]}"
    return repr(value)


def show(label, value):
    print(f"[{label}] {value}")


def reset():
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world


def book(frame, first=True):
    b = Spellbook(aetheric_frame=frame)
    if first:
        b.configure_aether_frame(system_state="dynamic", system_caching_enabled=False, disposal=None,
                                 disposal_method_names=None)
    return b


def state(b, cls):
    for s in list(b._spell_id_pool.values()):
        if s.spell is cls:
            st = s.system_state
            topo = s._spell_system_states.get_local_topology(s.spell_index)
            sockets = [] if topo is None else [(x.socket_kind.name, x.hidden_spell_ids, x.hidden_frame_keys)
                                               for x in topo.sockets]
            return f"validity={st.validity.name} sockets={sockets}"
    return "not in pool"


def pool_has(b, spell_id):
    return spell_id in b._spell_id_pool


for departure in ("remove_spell_from_contract", "sever_link", "owner_cleanup_spell", "remove_index_from_contract"):
    reset()
    frame = f"diag-{departure}"
    owner_book = book(frame)
    english_id = owner_book.bind(spell=English, existence=Existence.many, permissions="create", spellframe=Greeter,
                                 binding_name="greeter")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower_book = book(frame, first=False)
    borrower_book.bind(spell=ByClass, existence=Existence.many, permissions="create")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    if departure == "remove_index_from_contract":
        index = owner_book.find_spell_by_spell_id(english_id).spell_index
        with borrower.transaction("link", conduits=[borrower, owner]):
            show("index link", borrower.add_index_to_contract(index=index, conduit=owner, permissions="create"))
    else:
        borrower.add_spell_to_contract(spell_id=english_id, conduit=owner, permissions="create")
    show(f"{departure} meld after grant", attempt(lambda: borrower.meld(ByClass)))
    show(f"{departure} state after refusal", state(borrower_book, ByClass))
    show(f"{departure} copy in borrower pool", pool_has(borrower_book, english_id))
    if departure == "remove_spell_from_contract":
        def go():
            with borrower.transaction("link", conduits=[borrower, owner]):
                return borrower.remove_spell_from_contract(spell_id=english_id, conduit=owner)
        result = attempt(go)
    elif departure == "remove_index_from_contract":
        def go():
            with borrower.transaction("link", conduits=[borrower, owner]):
                return borrower.remove_index_from_contract(index_id=index.id, conduit=owner)
        result = attempt(go)
    elif departure == "sever_link":
        result = attempt(lambda: owner.sever_link(borrower))
    else:
        spell = owner.get_spell_by_spell_id(english_id, frame)
        result = attempt(lambda: owner.cleanup_spell(spell=spell))
    show(f"{departure} departure", result)
    show(f"{departure} copy in borrower pool after", pool_has(borrower_book, english_id))
    show(f"{departure} state after departure", state(borrower_book, ByClass))
    show(f"{departure} meld after departure", attempt(lambda: borrower.meld(ByClass)))
    show(f"{departure} late twin bind", attempt(lambda: borrower.bind(spell=LateByClass, existence=Existence.many,
                                                                       permissions="create")))
    show(f"{departure} late twin meld", attempt(lambda: borrower.meld(LateByClass)))
    print()
    borrower.cleanup()
    owner.cleanup()

# Same-Book cleanup_spell
reset()
b = book("diag-cleanup")
english_id = b.bind(spell=English, existence=Existence.many, permissions="create", spellframe=Greeter,
                    binding_name="greeter")
root = b.conjure(dynamic=True, name="root")
show("cleanup late bind", attempt(lambda: root.bind(spell=ByClass, existence=Existence.many, permissions="create")))
show("cleanup state after refusal", state(b, ByClass))
spell = root.get_spell_by_spell_id(english_id, "diag-cleanup")
show("cleanup departure", attempt(lambda: root.cleanup_spell(spell=spell)))
show("cleanup english in pool after", pool_has(b, english_id))
show("cleanup state after departure", state(b, ByClass))
show("cleanup meld after", attempt(lambda: root.meld(ByClass)))
show("cleanup late twin bind", attempt(lambda: root.bind(spell=LateByClass, existence=Existence.many,
                                                         permissions="create")))
show("cleanup late twin meld", attempt(lambda: root.meld(LateByClass)))
root.cleanup()
