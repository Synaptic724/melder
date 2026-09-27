"""Version-portable probe: does conjure accept an unbound caller-supplied parameter, and does meld use it?"""
import json, sys, tempfile, os
os.chdir(tempfile.mkdtemp())
import melder
from melder.aether.spellbook.spellbook import Spellbook

class Package:
    pass

class Task:
    def __init__(self, work: Package):
        self.work = work

out = {"melder": getattr(melder, "__version__", "?"), "file": melder.__file__}
book = Spellbook()
try:
    book.bind(spell=Task, existence="many")
    out["bind"] = "ok"
except Exception as e:
    out["bind"] = f"{type(e).__name__}: {str(e)[:200]}"
try:
    conduit = book.conjure()
    out["conjure"] = "ok"
except Exception as e:
    out["conjure"] = f"{type(e).__name__}: {str(e)[:240]}"
    conduit = None
if conduit is not None:
    pkg = Package()
    try:
        task = conduit.meld(Task, override={"work": pkg})
        out["meld_override"] = "ok, identity kept" if task.work is pkg else f"ok, got {type(task.work).__name__}"
    except Exception as e:
        out["meld_override"] = f"{type(e).__name__}: {str(e)[:240]}"
    try:
        task = conduit.meld(Task)
        out["meld_plain"] = f"ok, work={type(task.work).__name__}"
    except Exception as e:
        out["meld_plain"] = f"{type(e).__name__}: {str(e)[:200]}"
print(json.dumps(out))
