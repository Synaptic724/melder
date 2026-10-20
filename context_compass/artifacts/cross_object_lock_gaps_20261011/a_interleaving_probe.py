"""
Item (a), deterministic interleaving. The owner-side index emissions walk the owner ward's contract registry
(ConduitWard._contracts) with no ward lock, and they run outside any transaction window: Conduit.cleanup_spell takes
no transaction at all, and notch_spell ends its NOTCH transaction before it emits. A link admitted by the mediator in
that window writes the registry under the two ward locks.

Scenario "cleanup": owner holds index I with one member; the owner is linked to D first and to B second, and B
borrows I through an index link. The thread running owner.cleanup_spell is paused inside _emit_index_destroy while it
looks at D's contract (after the real read; nothing skipped); the main thread then calls owner.link(C) - the public
verb, admitted through the frame mediator with its EXCLUSIVE conduit claims - and the emitter resumes.

Scenario "notch": owner holds index I = {A active, B parked}, linked to B1 then B2, both borrowing I. The thread
running owner.notch_spell is paused inside _emit_index_notch while it moves B1's head; the main thread calls
owner.link(C); the emitter resumes.

Usage: python a_interleaving_probe.py <src copy> <dir holding _frame_posture_test_support.py> <cleanup|notch>
"""
import sys
import threading

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
scenario = sys.argv[3]
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import IndexDetail
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether


class ServiceA:
    """Owner's spell (head of index I)."""


class ServiceB:
    """Second member of I (notch scenario)."""


def make_book() -> Spellbook:
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def link_index(borrower: Conduit, owner: Conduit, index) -> None:
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")


owner_book = make_book()
id_a = owner_book.bind(spell=ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
owner = owner_book.conjure(dynamic=True, name="owner")
index = owner_book.find_spell_by_id(id_a).spell_index
index_id = index.id
others = {name: make_book().conjure(dynamic=True, name=name) for name in ("d", "b1", "b2", "c")}
parked, release, linked = threading.Event(), threading.Event(), threading.Event()
outcome = {}

if scenario == "cleanup":
    owner.link(others["d"])
    owner.link(others["b1"])
    link_index(others["b1"], owner, index)
    first_contract = owner._conduit_ward._find_contract(others["d"])
    original = Contract._get_index_detail_map

    def pausing_get_index_detail_map(self, ward):
        answer = original(self, ward)
        if threading.current_thread() is emitter and self is first_contract and not parked.is_set():
            parked.set()
            assert release.wait(timeout=30)
        return answer

    Contract._get_index_detail_map = pausing_get_index_detail_map

    def emit():
        try:
            owner.cleanup_spell(spell=owner_book.find_spell_by_id(id_a))
            outcome["result"] = "ok"
        except BaseException as exc:
            outcome["result"] = repr(exc)
else:
    owner.link(others["b1"])
    owner.link(others["b2"])
    id_b = owner.bind_inactive(spell=ServiceB, spell_index=index, existence=Existence.unique,
                               permissions="create", binding_name="b")
    spell_b = owner_book._get_owned_spell(id_b)
    link_index(others["b1"], owner, index)
    link_index(others["b2"], owner, index)
    original = IndexDetail.update_selected

    def pausing_update_selected(self, spell_id):
        answer = original(self, spell_id)
        if threading.current_thread() is emitter and not parked.is_set():
            parked.set()
            assert release.wait(timeout=30)
        return answer

    IndexDetail.update_selected = pausing_update_selected

    def emit():
        try:
            owner.notch_spell(spell_index=index, spell=spell_b)
            outcome["result"] = "ok"
        except BaseException as exc:
            outcome["result"] = repr(exc)

emitter = threading.Thread(target=emit, name="emitter")
emitter.start()
assert parked.wait(timeout=30), "emitter never reached its contract walk"


def link_c():
    owner.link(others["c"])     # public verb: admitted by the frame mediator, writes both wards under their locks
    linked.set()


linker = threading.Thread(target=link_c, name="linker")
linker.start()
print(f"scenario={scenario} gil={sys._is_gil_enabled()}")
print("owner.link(C) admitted and completed while the emitter was paused in its walk:", linked.wait(timeout=10))
release.set()
emitter.join(timeout=30)
linker.join(timeout=30)
print(f"{scenario} outcome:", outcome.get("result"))
if scenario == "cleanup":
    b1_book = others["b1"]._spellbook
    contract = others["b1"]._conduit_ward._find_contract_by_id(owner._id)
    print("spell disposed in the owner Book:", owner_book.find_spell_by_id(id_a) is None)
    print("borrower B still tracks the destroyed index:", index_id in b1_book._contracted_indexes)
    print("borrower B's contract still holds its IndexDetail:", contract._check_index_exists(owner._conduit_ward, index_id))
else:
    for name in ("b1", "b2"):
        active = others[name]._spellbook._contracted_spells_by_id.get(owner._id, {})
        print(f"{name}: active borrowed copy is the new head B: {id_b in active}; still holds old head A: {id_a in active}")
