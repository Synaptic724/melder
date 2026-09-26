"""How does a missing OVERRIDE_REQUIRED input fail today? Uses the existing resolvable=False route."""
import json, os, sys, tempfile
os.chdir(tempfile.mkdtemp())
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
sys.path.insert(0, os.environ["REPO"])
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

def attempt(fn):
    try:
        return fn()
    except Exception as e:
        cause = e.__cause__
        return {"error": type(e).__name__, "msg": str(e)[:160],
                "cause": (type(cause).__name__ + ": " + str(cause)[:120]) if cause else None}

class Pkg:
    pass

class Task:
    def __init__(self, work: Pkg, label: str = "t"):
        self.work = work

class Leaf:
    pass

class TaskWithDep:
    def __init__(self, work: Pkg, leaf: Leaf):
        self.work = work

class Pool:
    def __init__(self, task: Task, leaf: Leaf):
        self.task = task

def world():
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether(); Conduit._aether = Spellbook._aether
    c = SpellbookConfiguration().with_defaults(); c.with_phase_scheduler_workers(1)
    configure_frame_posture_for_spellbook_configuration(c, dynamic=False).with_system_caching_enabled(False)
    return Spellbook(configuration=c)

out = {}
for existence in ("many", "unique_per_conduit"):
    book = world()
    book.bind(spell=Pkg, existence="many", resolvable=False)
    book.bind(spell=Task, existence=existence)
    book.bind(spell=Leaf, existence="many")
    book.bind(spell=TaskWithDep, existence=existence)
    book.bind(spell=Pool, existence="many")
    conduit = book.conjure()
    p = Pkg()
    r = {}
    r["root_supplied"] = attempt(lambda: conduit.meld(Task, override={"work": p}).work is p)
    r["root_missing"] = attempt(lambda: conduit.meld(Task))
    r["root_with_dep_missing"] = attempt(lambda: conduit.meld(TaskWithDep))
    r["nested_missing"] = attempt(lambda: conduit.meld(Pool))
    r["nested_other_override_only"] = attempt(lambda: conduit.meld(Pool, override={"leaf": Leaf()}))
    r["nested_supplied_path"] = attempt(lambda: conduit.meld(Pool, override={"task>work": p}).task.work is p)
    r["nested_supplied_broadcast"] = attempt(lambda: conduit.meld(Pool, override={"**work": p}).task.work is p)
    out[existence] = r
    conduit.permanent_cleanup(); book.cleanup()
print(json.dumps(out, indent=1, default=str))
