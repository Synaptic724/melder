"""
Deadlock probe: ConduitWard._get_spells_in_contract_by_conduit (public Conduit.get_spells_in_contract_by_conduit)
holds the ward lock and resolves inbound spells through Conduit.find_contracted_spell, which takes the CONDUIT lock;
Conduit.sever_link (and link) take the conduit lock first and the ward locks second. Opposite orders.

Thread X lists the borrower's contract with the owner and is paused right after it took the borrower's ward lock (on
its first Contract._get_detail_map; nothing skipped). Thread Y calls borrower.sever_link(owner): admitted by the
mediator, it takes the borrower's conduit lock and waits for the ward lock. X is released and needs the conduit lock.

Usage: python d_deadlock_probe.py <src copy> <dir holding _frame_posture_test_support.py>
"""
import os
import sys
import threading

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether


class Lent:
    """Spell the owner lends to the borrower."""


def make_book() -> Spellbook:
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


owner_book = make_book()
lent_id = owner_book.bind(spell=Lent, existence=Existence.unique, permissions="create", binding_name="lent")
owner = owner_book.conjure(dynamic=True, name="owner")
borrower = make_book().conjure(dynamic=True, name="borrower")
owner.link(borrower)
with borrower.transaction("link", conduits=[borrower, owner]):
    assert borrower.add_index_to_contract(index=owner_book.find_spell_by_id(lent_id).spell_index,
                                          conduit=owner, permissions="create")
print("before: inbound listing =", borrower.get_spells_in_contract_by_conduit(owner._id)["inbound"] != [])

parked, release = threading.Event(), threading.Event()
real = Contract._get_detail_map
outcome = {}


def parking(self, ward):
    answer = real(self, ward)
    if threading.current_thread() is lister and not parked.is_set():
        parked.set()
        release.wait(timeout=30)
    return answer


Contract._get_detail_map = parking


def list_contract():
    try:
        outcome["list"] = borrower.get_spells_in_contract_by_conduit(owner._id)
    except BaseException as exc:
        outcome["list"] = repr(exc)


def sever():
    try:
        outcome["sever"] = borrower.sever_link(owner)
    except BaseException as exc:
        outcome["sever"] = repr(exc)


lister = threading.Thread(target=list_contract, daemon=True)
severer = threading.Thread(target=sever, daemon=True)
lister.start()
assert parked.wait(timeout=30)
severer.start()
severer.join(timeout=1.0)
print("sever finished while the lister held the ward lock:", not severer.is_alive())
release.set()
lister.join(timeout=5)
severer.join(timeout=5)
print("after release: lister alive =", lister.is_alive(), "| severer alive =", severer.is_alive())
print("DEADLOCK" if lister.is_alive() and severer.is_alive() else f"no deadlock: {outcome}")
sys.stdout.flush()
os._exit(0)
