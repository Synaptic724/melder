"""
Item (b), deterministic interleaving. A borrower's contract inspection (Conduit.get_spell_in_contracts ->
ConduitWard._get_spell_in_contracts) walks the owner's per-spell detail map of each contract while holding only the
BORROWER's ward lock and no transaction. The owner writes that map when its index gains a member (bind_inactive onto
an index-linked index -> _emit_index_member_added -> _contract_member_spell -> Contract._add), inside the owner's
bind transaction and without the borrower's ward lock.

Owner index I = {A active, B parked}, index-linked to borrower B1, so the owner's detail map in their contract holds
A and B. B1 looks up a spell id the walk must pass over; it is paused after the real has_spell of the first detail;
the main thread binds C inactive onto I; B1 resumes.

Usage: python b_interleaving_probe.py <src copy> <dir holding _frame_posture_test_support.py>
"""
import sys
import threading

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether


class ServiceA:
    """Active head of index I."""


class ServiceB:
    """Parked member of I."""


class ServiceC:
    """Member staged onto I while the borrower inspects its contracts."""


def make_book() -> Spellbook:
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


owner_book = make_book()
id_a = owner_book.bind(spell=ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
owner = owner_book.conjure(dynamic=True, name="owner")
borrower = make_book().conjure(dynamic=True, name="b1")
owner.link(borrower)
index = owner_book.find_spell_by_id(id_a).spell_index
id_b = owner.bind_inactive(spell=ServiceB, spell_index=index, existence=Existence.unique,
                           permissions="create", binding_name="b")
with borrower.transaction("link", conduits=[borrower, owner]):
    assert borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")

parked, release, staged = threading.Event(), threading.Event(), threading.Event()
outcome = {}
original = Detail.has_spell


def pausing_has_spell(self, spell_id):
    answer = original(self, spell_id)
    if threading.current_thread() is reader and not parked.is_set():
        parked.set()
        assert release.wait(timeout=30)
    return answer


Detail.has_spell = pausing_has_spell


def inspect():
    try:
        outcome["result"] = repr(borrower.get_spell_in_contracts("0" * 64))
    except BaseException as exc:
        outcome["result"] = repr(exc)


reader = threading.Thread(target=inspect, name="reader")
reader.start()
assert parked.wait(timeout=30), "reader never reached the detail walk"


def stage_c():
    owner.bind_inactive(spell=ServiceC, spell_index=index, existence=Existence.unique,
                        permissions="create", binding_name="c")
    staged.set()


writer = threading.Thread(target=stage_c, name="writer")
writer.start()
print(f"gil={sys._is_gil_enabled()}")
print("owner staged C onto the linked index while the borrower was paused in its walk:", staged.wait(timeout=10))
release.set()
reader.join(timeout=30)
writer.join(timeout=30)
print("get_spell_in_contracts outcome:", outcome.get("result"))
