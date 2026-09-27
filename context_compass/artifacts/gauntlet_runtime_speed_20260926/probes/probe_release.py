"""melder_2 VM probe: are user objects released promptly (no gc.collect) after Melder cleanup, base vs P3?"""
import gc, os, sys, weakref
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy")))
sys.path.insert(0, str(ROOT / "src"))
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.existence.existence import Existence
gc.disable()
class Service:
    pass
class Scoped:
    def __init__(self, service: Service) -> None:
        self.service = service
class Plain:
    pass
results = {}
# 1) existing object bound into a spellbook, then the book is cleaned
book = Spellbook()
inst = Plain()
ref_existing = weakref.ref(inst)
id_inst = book.bind(spell=inst, existence=Existence.unique)
id_svc = book.bind(spell=Service, existence=Existence.unique)
id_scoped = book.bind(spell=Scoped, existence=Existence.unique_per_spell_space)
conduit = book.conjure()
svc = conduit.meld(spell_id=id_svc); ref_service = weakref.ref(svc)
lesser = conduit.create_lesser_conduit()
with lesser.enter_spellspace() as space:
    scoped = space.meld(spell_id=id_scoped); ref_scoped = weakref.ref(scoped)
del scoped
results["scoped object released at spellspace exit"] = ref_scoped() is None
lesser.cleanup(); del lesser
del svc, inst
conduit.cleanup(); book.cleanup()
del conduit, book
results["existing object released after book+conduit cleanup"] = ref_existing() is None
results["unique service released after book+conduit cleanup"] = ref_service() is None
print(ROOT.name, results)
