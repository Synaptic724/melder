"""Stand-in shapes for the five reported CommandOps refusals (the CommandOps repo is not available here)."""
from melder import Spellbook, Conduit, UnresolvedInputError

class Package:
    """Unregistered, caller-owned type (the reported work_callable: Package)."""

class Task:
    def __init__(self, work_callable: Package) -> None:
        self.work_callable = work_callable

class CommandCenter:
    def __init__(self, conduit: Conduit) -> None:
        self.conduit = conduit

class AgentPools:
    def __init__(self, task: Task) -> None:
        self.task = task

# 1. consumer bound before conjure; Conduit-typed parameter (kernel-guarded type)
book = Spellbook()
book.bind(spell=Task, existence="many")
book.bind(spell=CommandCenter, existence="many")
book.bind(spell=AgentPools, existence="many")
root = book.conjure(dynamic=True)
pkg = Package()
print("1 bound-before-conjure:", root.meld(spell=Task, override={"work_callable": pkg}).work_callable is pkg)
print("2 conduit-typed input:", root.meld(spell=CommandCenter, override={"conduit": root}).conduit is root)
print("3 nested via path key:", root.meld(spell=AgentPools, override={"task>work_callable": pkg}).task.work_callable is pkg)

# 4. consumer bound into an already-conjured dynamic root (late bind)
class LateStack:
    def __init__(self, entry: Package) -> None:
        self.entry = entry
book.bind(spell=LateStack, existence="many")
print("4 late bind into dynamic root:", root.meld(spell=LateStack, override={"entry": pkg}).entry is pkg)
try:
    root.meld(spell=LateStack)
except UnresolvedInputError as exc:
    print("5 missing ->", exc.param_name, exc.expected_type)
