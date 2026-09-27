"""S2b discovery: step rows and construction counts for shared sites today (run from a tree root, PYTHONPATH=src:.).

G1: Root(a: A many, s: S unique_per_conduit), S(x: X many).
G2: Root(p: P many, q: Q many), P(s: S upc), Q(s: S upc), S(x: X many) - S reached along two paths.
Prints each graph's generalized no-overrides rows (instance key, existence, dependency order) captured at hydration,
and per-class construction counts for a cold meld and a warm meld.
"""
import collections, warnings
warnings.simplefilter("ignore")
from melder import Aether, Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration import generalized_hydrator as gh

COUNTS = collections.Counter()
CAPTURED = []
real = gh.hydrate_no_overrides_executor


def capture(**kwargs):
    CAPTURED.append(kwargs["rows"])
    return real(**kwargs)


gh.hydrate_no_overrides_executor = capture


def counted(name, params):
    def __init__(self, **kw):
        COUNTS[name] += 1
    ns = {"__init__": __init__}
    return type(name, (), ns)


class X:
    def __init__(self) -> None:
        COUNTS["X"] += 1


class S:
    def __init__(self, x: X) -> None:
        COUNTS["S"] += 1
        self.x = x


class A:
    def __init__(self) -> None:
        COUNTS["A"] += 1


class Root1:
    def __init__(self, a: A, s: S) -> None:
        COUNTS["Root1"] += 1


class P:
    def __init__(self, s: S) -> None:
        COUNTS["P"] += 1


class Q:
    def __init__(self, s: S) -> None:
        COUNTS["Q"] += 1


class Root2:
    def __init__(self, p: P, q: Q) -> None:
        COUNTS["Root2"] += 1


def world(bindings, root):
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame="probe")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    ids = {cls: book.bind(spell=cls, existence=ex, permissions="create") for cls, ex in bindings}
    conduit = book.conjure(name="probe")
    names = {sid: cls.__name__ for cls, sid in ids.items()}
    return conduit, ids[root], names


for label, bindings, root in (
    ("G1", [(X, Existence.many), (S, Existence.unique_per_conduit), (A, Existence.many), (Root1, Existence.many)], Root1),
    ("G2", [(X, Existence.many), (S, Existence.unique_per_conduit), (P, Existence.many), (Q, Existence.many),
            (Root2, Existence.many)], Root2),
):
    CAPTURED.clear()
    COUNTS.clear()
    conduit, rid, names = world(bindings, root)
    conduit.meld(spell_id=rid)
    cold = dict(COUNTS)
    COUNTS.clear()
    conduit.meld(spell_id=rid)
    warm = dict(COUNTS)
    print(f"{label}: cold {cold} | warm {warm}")
    for rows in CAPTURED:
        for row in rows:
            key = row["instance_key"]
            deps = [(p, [(names.get(k[0], k[0][:6]), k[1]) for k in ks]) for p, ks in row["dependency_resolution_order"]]
            print(f"   {names.get(key[0], key[0][:6]):6} path={key[1]} {row['existence']:22} deps={deps}")
    conduit.cleanup()
