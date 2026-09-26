"""What does a stored consumer hold after cleanup_spell disposes its provider?

Run with REPO=<checkout> PYTHONPATH=src from a checkout; results are recorded in the task notes.
"""
import json, os, sys, tempfile
os.chdir(tempfile.mkdtemp())
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
sys.path.insert(0, os.environ["REPO"])
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Testing1:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class Tester:
    def __init__(self, testing1: Testing1):
        self.testing1 = testing1


Aether._reset_singleton_for_tests()
Spellbook._aether = Aether(); Conduit._aether = Spellbook._aether
c = SpellbookConfiguration(); apply_dynamic_defaults_for_spellbook_configuration(c)
c.set_property("phase_scheduler_workers_per_spellbook", 1)
book = Spellbook(configuration=c)
conduit = book.conjure(dynamic=True, name="root")
with book.transaction("bind"):
    t1_id = book.bind(spell=Testing1, existence=Existence.unique, permissions="create",
                      disposal_method_names=["close"])
    tester_id = book.bind(spell=Tester, existence=Existence.unique, permissions="create")
tester = conduit.meld(spell_id=tester_id)
held = tester.testing1
conduit.cleanup_spell(spell=book._spell_id_pool.get(t1_id))
again = conduit.meld(spell_id=tester_id)
print(json.dumps({
    "meld(tester) after cleanup is the stored tester": again is tester,
    "tester.testing1 is the same Python object": again.testing1 is held,
    "that object's close() was run by cleanup_spell": held.closed,
    "Melder still resolves Testing1": book.find_spell_by_id(t1_id) is not None,
}, indent=1))
conduit.cleanup()
