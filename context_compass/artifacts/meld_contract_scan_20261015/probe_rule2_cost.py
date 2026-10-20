"""Cost of rule 2 on one tree, before or after the change (melder_1, TASK-2026-10-16-recheck_contract_consumers...).

No monkeypatch changes behaviour; two counters only wrap the 5-11 target pass
(`Spellbook._run_resolution_phases_for_target_spell`) and the meld-time structural rerun
(`SpellCompilerSystem.run_structural_phases`).
  W  a warm borrower SpellContract consumer (`many`), lent an index-linked provider: microseconds per meld
     (time-boxed loop) and the passes and reruns those melds ran.
  N  one lender notch, then one meld of the consumer: passes and reruns, the version built, the meld's time;
     then the warm cost again.
  F  a fan-out: one provider and 200 `many` consumers of it in one Book, each melded once; the time of a notch of
     the provider and of the notch back (the registry walk marks the 200 dependents).
usage: python -X gil=0|1 <this script> <tree root>
"""
import sys
import time

TREE = sys.argv[1]
sys.path[:0] = [f"{TREE}/src", TREE]

from tests.integration.melder.conduit import test_conduit_integration_notch_revalidation as t  # noqa: E402
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.spellbook.existence.existence import Existence  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.aether.spellbook.spell_compiler.spell_compiler_system import SpellCompilerSystem  # noqa: E402

COUNTS = {"passes": 0, "reruns": 0}
_pass = Spellbook._run_resolution_phases_for_target_spell
_rerun = SpellCompilerSystem.run_structural_phases


def counting_pass(self, conduit_id, spell):
    COUNTS["passes"] += 1
    return _pass(self, conduit_id, spell)


def counting_rerun(self, spellbook, spell, cancel_event=None):
    COUNTS["reruns"] += 1
    return _rerun(self, spellbook, spell, cancel_event)


Spellbook._run_resolution_phases_for_target_spell = counting_pass
SpellCompilerSystem.run_structural_phases = counting_rerun


def fresh() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def reset_counts() -> None:
    COUNTS["passes"] = 0
    COUNTS["reruns"] = 0


def warm(world, seconds: float = 1.0, cap: int = 200000) -> str:
    reset_counts()
    melds = 0
    started = time.perf_counter()
    while melds < cap and time.perf_counter() - started < seconds:
        world.meld_ping()
        melds += 1
    elapsed = time.perf_counter() - started
    return f"{melds} melds, {elapsed / melds * 1e6:.2f} us/meld, passes={COUNTS['passes']} reruns={COUNTS['reruns']}"


print(f"tree={TREE} gil_enabled={sys._is_gil_enabled()}")
fresh()
world = t._lend("cost", t.ImplA)
print(f"first meld: {world.meld_ping()}")
print(f"W warm consumer: {warm(world)}")
reset_counts()
b_id = world.notch_to(t.ImplB)
started = time.perf_counter()
try:
    version = world.meld_ping()
except Exception as exc:  # the before tree may not follow
    version = f"{type(exc).__name__}"
meld_us = (time.perf_counter() - started) * 1e6
print(f"N notch to B, then one meld: built {version} in {meld_us:.0f} us; passes={COUNTS['passes']} "
      f"reruns={COUNTS['reruns']}")
print(f"  warm after: {warm(world)}")
reset_counts()
world.notch_back(world.provider_id)
started = time.perf_counter()
version = world.meld_ping()
print(f"N notch back to A, then one meld: built {version} in {(time.perf_counter() - started) * 1e6:.0f} us; "
      f"passes={COUNTS['passes']} reruns={COUNTS['reruns']}")
world.cleanup()


class P:
    """The fan-out's provider."""


class P2(P):
    """A second version of P."""


fresh()
book = Spellbook()
book.bind(spell=P, existence=Existence.unique, permissions="create")
consumers = []
for i in range(200):
    namespace = {"P": P}
    exec(f"class C{i}:\n    def __init__(self, p: P) -> None:\n        self.p = p\n", namespace)
    consumers.append(namespace[f"C{i}"])
    book.bind(spell=consumers[-1], existence=Existence.many, permissions="create")
conduit = book.conjure(name="fanout", dynamic=True)
for consumer in consumers:
    conduit.meld(spell=consumer)
p_spell = next(spell for spell in book._spells.values() if spell.spell_name == "P")
index = p_spell.spell_index
p_id = p_spell.spell_id
p2_id = conduit.bind_inactive(spell=P2, spell_index=index, existence=Existence.unique)
for label, target in (("notch to P2", p2_id), ("notch back to P", p_id)):
    started = time.perf_counter()
    conduit.notch_spell(spell_index=index, spell_id=target)
    print(f"F {label} with 200 dependents: {(time.perf_counter() - started) * 1e3:.2f} ms")
conduit.cleanup()
