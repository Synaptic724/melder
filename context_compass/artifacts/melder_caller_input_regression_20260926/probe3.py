"""Version-portable probe: register a Package INSTANCE as an existing object, then meld a consumer."""
import json, os, tempfile
os.chdir(tempfile.mkdtemp())
import melder
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.helpers.package import Package

def attempt(fn):
    try:
        return fn()
    except Exception as e:
        return f"{type(e).__name__}: {str(e)[:220]}"

def work():
    return 1

class MTask:
    def __init__(self, work: Package):
        self.work = work

out = {"melder": getattr(melder, "__version__", "?")}
book = Spellbook()
registered = attempt(lambda: Package(work))
out["make_package"] = "ok" if isinstance(registered, Package) else registered
if isinstance(registered, Package):
    out["bind_instance"] = attempt(lambda: book.bind(spell=registered, existence="unique") and "ok")
out["bind_MTask"] = attempt(lambda: book.bind(spell=MTask, existence="many") and "ok")
conduit = None
def conj():
    global conduit
    conduit = book.conjure()
    return "ok"
out["conjure"] = attempt(conj)
if conduit is not None:
    other = Package(work)
    out["meld_override"] = attempt(lambda: "supplied identity" if conduit.meld(MTask, override={"work": other}).work is other else "other")
    out["meld_plain"] = attempt(lambda: "registered identity" if conduit.meld(MTask).work is registered else "other")
print(json.dumps(out))
