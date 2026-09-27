"""Steps 1-2 check: a provider-less typed parameter compiles as UNRESOLVED_INPUT, executes by override, and a
missing value raises UnresolvedInputError in every executor family."""
import json, os, sys, tempfile
os.chdir(tempfile.mkdtemp())
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spellbook import Spellbook
sys.path.insert(0, os.environ["REPO"])
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


def attempt(fn):
    try:
        return fn()
    except Exception as e:
        cause = e.__cause__
        row = {"error": type(e).__name__, "msg": str(e)[:400],
               "cause": (type(cause).__name__ + ": " + str(cause)[:120]) if cause else None}
        for field in ("expected_type", "unresolved_params", "param_name"):
            if hasattr(e, field):
                row[field] = getattr(e, field)
        return row


class Pkg:
    pass


class Task:
    def __init__(self, work: Pkg, label: str = "t"):
        self.work = work


class Leaf:
    pass


class Pool:
    def __init__(self, task: Task, leaf: Leaf):
        self.task = task


class Faulty:
    """Supplied input present, but the body raises its own TypeError: the generic error must stay."""
    def __init__(self, work: Pkg):
        raise TypeError("body failure unrelated to inputs")


class Wrap:
    def __init__(self, faulty: Faulty):
        self.faulty = faulty


def world(dynamic):
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether(); Conduit._aether = Spellbook._aether
    c = SpellbookConfiguration().with_defaults(); c.with_phase_scheduler_workers(1)
    configure_frame_posture_for_spellbook_configuration(c, dynamic=dynamic).with_system_caching_enabled(False)
    return Spellbook(configuration=c)


CASES = {
    "root_supplied": lambda c, p: c.meld(Task, override={"work": p}).work is p,
    "root_missing": lambda c, p: c.meld(Task),
    "nested_missing": lambda c, p: c.meld(Pool),
    "nested_supplied_path": lambda c, p: c.meld(Pool, override={"task>work": p}).task.work is p,
    "nested_supplied_broadcast": lambda c, p: c.meld(Pool, override={"**work": p}).task.work is p,
    "none_by_presence": lambda c, p: c.meld(Task, override={"work": None}).work is None,
    "nested_missing_other_override": lambda c, p: c.meld(Pool, override={"leaf": Leaf()}),
    "unrelated_typeerror_root": lambda c, p: c.meld(Faulty, override={"work": p}),
    "unrelated_typeerror_nested": lambda c, p: c.meld(Wrap, override={"faulty>work": p}),
    "positional_root_supplied": lambda c, p: c.meld(Task, override={"__args__": [p]}).work is p,
}

out = {}
for existence in ("many", "unique_per_conduit"):
    r = {}
    for name, case in CASES.items():
        # Fresh world per case so a stored shared Task never masks the next case.
        book = world(dynamic=False)
        task_id = book.bind(spell=Task, existence=existence)
        book.bind(spell=Leaf, existence="many")
        book.bind(spell=Pool, existence="many")
        book.bind(spell=Faulty, existence=existence)
        book.bind(spell=Wrap, existence="many")
        conduit = attempt(book.conjure)
        if isinstance(conduit, dict):
            r[name] = {"conjure": conduit}
            continue
        if name == "root_supplied":
            task = book.find_spell_by_id(task_id)
            topo = book._spell_system_states.get_local_topology(task.spell_index)
            s = [x for x in topo.sockets if x.param_name == "work"][0]
            r["socket"] = [s.socket_kind.name, s.dependency_key, s.position, s.parameter_kind, s.target_spell_ids]
            r["phase4_after_conjure"] = task.validation_result_phase4
        r[name] = attempt(lambda: case(conduit, Pkg()))
    out[existence] = r

# Late provider in a dynamic world: bind Pkg after conjure, next meld injects it.
book = world(dynamic=True)
task_id = book.bind(spell=Task, existence="many")
conduit = book.conjure(dynamic=True)
late = {"before": attempt(lambda: type(conduit.meld(Task)).__name__)}
book.bind(spell=Pkg, existence="many")
late["after"] = attempt(lambda: type(conduit.meld(Task).work).__name__)
task = book.find_spell_by_id(task_id)
topo = book._spell_system_states.get_local_topology(task.spell_index)
late["socket_after"] = [x.socket_kind.name for x in topo.sockets if x.param_name == "work"]
out["late_provider_dynamic"] = late
print(json.dumps(out, indent=1, default=str))
