"""
Items (a) and (b), unforced: nothing is patched or paused; every call is a public verb.

notch_vs_link: owner index I = {A, B} is index-linked to two borrowers; one thread notches I back and forth (each
  notch is a sealed NOTCH transaction whose borrower emission runs after the transaction ends); another thread links
  and severs a third conduit to the owner (sealed LINK/UNLINK transactions). Counts notch failures.
inspect_vs_stage: one thread repeats a borrower's get_spell_in_contracts; another stages a member onto the linked
  index (bind_inactive) and splits it out again (remove_from_spell_index). Counts inspection failures.
double_cleanup: cleanup_spell called twice on one spell, sequentially - what the second caller sees.

Usage: python ab_unforced_stress.py <src copy> <dir holding _frame_posture_test_support.py> <mode> <seconds>
Both threads run for the given number of seconds.
"""
import collections
import sys
import threading
import time

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
mode, seconds = sys.argv[3], float(sys.argv[4])
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether


class ServiceA:
    """Head of the linked index."""


class ServiceB:
    """Second member of the linked index."""


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
failures = collections.Counter()
done = threading.Event()


def record(exc: BaseException) -> None:
    failures[f"{type(exc).__name__}: {str(exc).splitlines()[0][:90]}"] += 1


if mode == "double_cleanup":
    spell = owner_book.find_spell_by_id(id_a)
    owner.cleanup_spell(spell=spell)
    try:
        owner.cleanup_spell(spell=spell)
        print("second cleanup_spell: returned")
    except BaseException as exc:
        print("second cleanup_spell raised:", repr(exc))
    sys.exit(0)

b1 = make_book().conjure(dynamic=True, name="b1")
b2 = make_book().conjure(dynamic=True, name="b2")
churn = make_book().conjure(dynamic=True, name="churn")
owner.link(b1)
owner.link(b2)
id_b = owner.bind_inactive(spell=ServiceB, spell_index=index, existence=Existence.unique,
                           permissions="create", binding_name="b")
link_index(b1, owner, index)
link_index(b2, owner, index)
spells = {id_a: owner_book._get_owned_spell(id_a), id_b: owner_book._get_owned_spell(id_b)}
ops = {"first": 0, "second": 0}


def notcher():
    deadline = time.monotonic() + seconds
    i = 0
    while time.monotonic() < deadline:
        i += 1
        target = id_b if i % 2 == 0 else id_a
        try:
            owner.notch_spell(spell_index=index, spell=spells[target])
        except Exception as exc:
            record(exc)
        ops["first"] += 1
    done.set()


def linker():
    while not done.is_set():
        try:
            owner.link(churn)
            owner.sever_link(churn)
        except Exception as exc:
            failures[f"(linker) {type(exc).__name__}: {str(exc).splitlines()[0][:80]}"] += 1
        ops["second"] += 1


def inspector():
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            b1.get_spell_in_contracts("0" * 64)
        except Exception as exc:
            record(exc)
        ops["first"] += 1
    done.set()


def stager():
    j = 0
    while not done.is_set():
        try:
            staged_class = type(f"Staged{j}", (), {"__module__": __name__})
            sid = owner.bind_inactive(spell=staged_class, spell_index=index, existence=Existence.unique,
                                      permissions="create", binding_name=f"staged{j}")
            owner.remove_from_spell_index(spell=owner_book._get_owned_spell(sid), source_index=index)
        except Exception as exc:
            failures[f"(stager) {type(exc).__name__}: {str(exc).splitlines()[0][:80]}"] += 1
        j += 1
        ops["second"] += 1


pair = (notcher, linker) if mode == "notch_vs_link" else (inspector, stager)
threads = [threading.Thread(target=fn) for fn in pair]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"mode={mode} gil={sys._is_gil_enabled()} first_ops={ops['first']} second_ops={ops['second']}")
print("failures:", dict(failures) if failures else "none")
