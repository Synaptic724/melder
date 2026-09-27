"""Version-portable probe, variants: dynamic late bind; binding melder's own Package."""
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

class LocalPackage:
    pass

class Task:
    def __init__(self, work: LocalPackage):
        self.work = work

class MTask:
    def __init__(self, work: Package):
        self.work = work

out = {"melder": getattr(melder, "__version__", "?")}

def dynamic_late_bind():
    book = Spellbook()
    conduit = book.conjure(dynamic=True)
    r = {"bind_after_conjure": attempt(lambda: book.bind(spell=Task, existence="many") and "ok")}
    pkg = LocalPackage()
    r["meld_override"] = attempt(lambda: "identity" if conduit.meld(Task, override={"work": pkg}).work is pkg else "other")
    return r

def bind_melder_package():
    book = Spellbook()
    r = {"bind_Package": attempt(lambda: book.bind(spell=Package, existence="many") and "ok")}
    r["bind_MTask"] = attempt(lambda: book.bind(spell=MTask, existence="many") and "ok")
    conduit = None
    def conj():
        nonlocal conduit
        conduit = book.conjure()
        return "ok"
    r["conjure"] = attempt(conj)
    if conduit is not None:
        sentinel = object()
        r["meld_override"] = attempt(lambda: "identity" if conduit.meld(MTask, override={"work": sentinel}).work is sentinel else "other")
    return r

import sys
if sys.argv[1] == "dyn":
    out["dynamic_late_bind"] = attempt(dynamic_late_bind)
else:
    out["bind_melder_package"] = attempt(bind_melder_package)
print(json.dumps(out))
