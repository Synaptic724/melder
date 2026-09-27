"""Stored dependent after provider cleanup and rebind: does meld return the old object?

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


class Dep1:
    pass


class Root:
    def __init__(self, dep1: Dep1):
        self.dep1 = dep1


def attempt(fn):
    try:
        return fn()
    except Exception as exc:
        return f"{type(exc).__name__}: {str(exc)[:120]}"


Aether._reset_singleton_for_tests()
Spellbook._aether = Aether(); Conduit._aether = Spellbook._aether
c = SpellbookConfiguration(); apply_dynamic_defaults_for_spellbook_configuration(c)
c.set_property("phase_scheduler_workers_per_spellbook", 1)
book = Spellbook(configuration=c)
conduit = book.conjure(dynamic=True, name="root")
with book.transaction("bind"):
    dep1_id = book.bind(spell=Dep1, existence=Existence.unique, permissions="create")
    root_id = book.bind(spell=Root, existence=Existence.unique, permissions="create")
first = conduit.meld(spell_id=root_id)
old_dep = first.dep1
conduit.cleanup_spell(spell=book._spell_id_pool.get(dep1_id))
out = {"after_cleanup": attempt(lambda: "same stored Root" if conduit.meld(spell_id=root_id) is first else "new Root")}
with book.transaction("bind"):
    new_dep_id = book.bind(spell=Dep1, existence=Existence.unique, permissions="create")
def after_rebind():
    r = conduit.meld(spell_id=root_id)
    return {"root": "same stored Root" if r is first else "new Root",
            "root.dep1": "old (disposed) Dep1" if r.dep1 is old_dep else "new Dep1",
            "meld(Dep1) is root.dep1": conduit.meld(spell_id=new_dep_id) is r.dep1}
out["after_rebind"] = attempt(after_rebind)
print(json.dumps(out, indent=1))
