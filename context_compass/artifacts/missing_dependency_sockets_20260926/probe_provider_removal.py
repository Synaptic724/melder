"""After cleanup_spell removes a provider, what happens to a dependent's stored and fresh instances?"""
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


def run(root_existence):
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether(); Conduit._aether = Spellbook._aether
    c = SpellbookConfiguration(); apply_dynamic_defaults_for_spellbook_configuration(c)
    c.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=c)
    conduit = book.conjure(dynamic=True, name="root")
    with book.transaction("bind"):
        dep1_id = book.bind(spell=Dep1, existence=Existence.unique, permissions="create")
        root_id = book.bind(spell=Root, existence=root_existence, permissions="create")
    before = conduit.meld(spell_id=root_id)
    conduit.cleanup_spell(spell=book._spell_id_pool.get(dep1_id))
    out = {"validity_after_cleanup": str(book._spell_id_pool.get(root_id).system_state.validity)}
    try:
        after = conduit.meld(spell_id=root_id)
        out["meld_after"] = "same stored instance" if after is before else type(after).__name__
    except Exception as exc:
        out["meld_after"] = f"{type(exc).__name__}: {str(exc)[:160]}"
    root = book._spell_id_pool.get(root_id)
    topo = book._spell_system_states.get_local_topology(root.spell_index)
    out["socket_after"] = [s.socket_kind.name for s in topo.sockets] if topo is not None else None
    conduit.cleanup()
    return out


print(json.dumps({"unique_root": run(Existence.unique), "many_root": run(Existence.many)}, indent=1))
