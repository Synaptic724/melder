"""
Probe: force the E interleaving through public calls and report whether it hangs (0.2.8233 evidence).

Usage: PYTHONPATH=<tree>/src python deadlock_probe.py <teardown|conjure>

Thread A runs a direct `Spell.cleanup()` and is parked right after the Book's real cleaned check (the first statement
of `cleanup_and_remove_spell`). Thread B then runs a root teardown (or a conjure of the Book) and A is released once B
holds the Book lock (inside teardown's spell walk, or inside conjure's
creation system). Prints HANG when both threads are still alive after 10 seconds, else the
outcome of each; exits with os._exit so hung daemon threads cannot keep the process alive.
"""
import os
import sys
import threading

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

sys.path.insert(0, os.getcwd())
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Doomed:
    """Removed by the direct cleanup."""


class Keeper:
    """Second spell, stamped by conjure."""


def main(mode: str) -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    doomed_id = book.bind(spell=Doomed, existence=Existence.unique, permissions="create", binding_name="doomed")
    book.bind(spell=Keeper, existence=Existence.unique, permissions="create", binding_name="keeper")
    root = book.conjure(dynamic=True, name="owner") if mode == "teardown" else None
    spell = book.find_spell_by_id(doomed_id)
    parked, release, b_inside = threading.Event(), threading.Event(), threading.Event()
    outcome = {}
    real_check, real_cleanup_spells = Spellbook.check_cleaned, Spellbook._cleanup_spells

    def parking(target):
        real_check(target)
        if target is book and threading.current_thread() is a and not parked.is_set():
            outcome["a_held_spell_lock"] = spell._lock._is_owned()
            parked.set()
            release.wait(30)

    Spellbook.check_cleaned = parking

    def b_entered(*args, **kwargs):
        b_inside.set()

    if mode == "teardown":
        def cleanup_spells(target):
            b_entered()
            return real_cleanup_spells(target)
        Spellbook._cleanup_spells = cleanup_spells
        b_work = root.cleanup
    else:
        # Conjure holds the Book lock across its creation system (`_conjure_within_transaction_window`); signal once
        # inside it, before the structural hydration and ownership stamping take spell locks under it.
        from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
        real_prepare = SpellbookCreationSystem._prepare_spellbook_for_conjure

        def prepare(*args, **kwargs):
            b_entered()
            return real_prepare(*args, **kwargs)
        SpellbookCreationSystem._prepare_spellbook_for_conjure = staticmethod(prepare)
        b_work = lambda: book.conjure(dynamic=True, name="owner")

    def run(label, work):
        try:
            work()
            outcome[label] = "ok"
        except BaseException as exc:
            outcome[label] = f"{type(exc).__name__}: {exc}"

    a = threading.Thread(target=run, args=("a", spell.cleanup), daemon=True)
    a.start()
    assert parked.wait(30)
    b = threading.Thread(target=run, args=("b", b_work), daemon=True)
    b.start()
    assert b_inside.wait(30)
    release.set()
    a.join(10)
    b.join(10)
    hung = [name for name, t in (("a", a), ("b", b)) if t.is_alive()]
    print(f"mode={mode} a_held_spell_lock={outcome.get('a_held_spell_lock')} "
          f"{'HANG ' + ','.join(hung) if hung else 'completed'} a={outcome.get('a')} b={outcome.get('b')}", flush=True)
    os._exit(0)


main(sys.argv[1])
