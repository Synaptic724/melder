"""Probe (melder_0, 2026-10-17; STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): what a
change of managed settings does to the spell_id and the pool - on the tree as it is, and on a prototype of the fix
(the managed settings out of the spell_id; a same-id rebind re-composes its pool).

Cases, each in a fresh Aether and its own dynamic frame with caching off; `Worker` is one class:
  R1  Worker bound limited_quantity (limit 1), one object leased; `cleanup_spell`, then `bind` with limit 2: is the
      spell_id the same, is the pool the same object, what are its limit and count; a second lease; the first
      object released with no filter - which pool takes it, and are the counts true.
  R2  Q2's staging: Worker limit 1 active, Worker limit 2 staged with `bind_inactive` on its index.
  R3  a mode change: Worker elastic (default limit), three objects leased and released (three idle), then
      `cleanup_spell` and `bind` limited_quantity limit 1: the pool's sizes and counts, then a lease and a release.
For each step it prints every pool of Worker (`ReleaseManagedSpell().describe`): count, idle, limit, mode.

Read-only on src/: run from this folder with a source tree first on sys.path, e.g.
    PYTHONPATH=<repo or prototype>/src python -X gil=0 probes/probe_settings_rebind.py
"""
import itertools

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

SERIALS = itertools.count(1)


class Worker:
    """The managed class; each object carries the serial of its construction."""

    def __init__(self) -> None:
        """Take the next serial."""
        self.serial = next(SERIALS)

    def reset(self) -> None:
        """The reset a release runs."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def options(mode: str, limit: object) -> dict:
    """Bind options of Worker at its one address."""
    found = dict(spell=Worker, spellframe="workers", binding_name="worker",
                 existence=Existence.managed_spell_quantity, permissions="create",
                 managed_spell_mode=mode, managed_spell_reset_methods=["reset"])
    if limit is not None:
        found["managed_spell_limit"] = limit
    return found


def world(frame: str, mode: str, limit: object):
    """One dynamic Book on `frame` with Worker bound managed, conjured."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                     system_caching_enabled=False)
    spell_id = spellbook.bind(**options(mode, limit))
    conduit = spellbook.conjure(dynamic=True, name="root")
    return spellbook, conduit, spell_id


def pools(step: str) -> None:
    """Print every pool of Worker."""
    print(f"  [{step}]")
    for snapshot in ReleaseManagedSpell().describe(Worker):
        print(f"    pool {snapshot['spell_id'][:10]}: mode {snapshot['mode']}, limit {snapshot['limit']}, "
              f"count {snapshot['count']}, idle {snapshot['idle_count']}")


def lease(conduit: Conduit, spell_id: str, label: str):
    """Meld `spell_id`; the holder gives the object back through the registry."""
    try:
        obj = conduit.meld(spell_id=spell_id)
        print(f"    meld {label} -> Worker #{obj.serial}")
        return obj
    except Exception as error:
        print(f"    meld {label} raised {type(error).__name__}: {' '.join(str(error).split())[:170]}")
        return None


def r1() -> None:
    """A settings change by cleanup_spell and bind."""
    print("R1 limit 1, one object out; cleanup_spell, then bind with limit 2")
    spellbook, conduit, a = world("r1", "limited_quantity", 1)
    first = lease(conduit, a, "A")
    pool_before = conduit._creations._managed_quantities[a]
    conduit.cleanup_spell(spell=spellbook.find_spell_by_spell_id(a))
    b = conduit.bind(**options("limited_quantity", 2))
    pool_after = conduit._creations._managed_quantities.get(b)
    print(f"    same spell_id: {b == a}; same pool object: {pool_after is pool_before}")
    pools("after the rebind")
    second = lease(conduit, b, "B")
    pools("after a second lease")
    ReleaseManagedSpell().release(first)
    pools("after releasing the first object with no filter")
    third = lease(conduit, b, "B again")
    pools("after another lease")


def r2() -> None:
    """Q2's staging of the same class with another limit."""
    print("R2 Worker limit 1 active; Worker limit 2 staged on its index")
    spellbook, conduit, a = world("r2", "limited_quantity", 1)
    index = spellbook.find_spell_by_spell_id(a).spell_index
    try:
        b = conduit.bind_inactive(spell_index=index, **options("limited_quantity", 2))
        print(f"    staged: same spell_id: {b == a}")
    except Exception as error:
        print(f"    raised {type(error).__name__}: {' '.join(str(error).split())[:120]}")
    pools("after the staging")


def r3() -> None:
    """A mode change with idle objects above the new limit."""
    print("R3 elastic, three objects leased and released; cleanup_spell, then bind limited_quantity limit 1")
    spellbook, conduit, a = world("r3", "elastic", None)
    objects = [lease(conduit, a, f"A{n}") for n in (1, 2, 3)]
    for obj in objects:
        ReleaseManagedSpell().release(obj)
    pools("three idle")
    conduit.cleanup_spell(spell=spellbook.find_spell_by_spell_id(a))
    b = conduit.bind(**options("limited_quantity", 1))
    print(f"    same spell_id: {b == a}")
    pools("after the rebind")
    obj = lease(conduit, b, "B")
    pools("after a lease")
    ReleaseManagedSpell().release(obj)
    pools("after its release")


if __name__ == "__main__":
    for case in (r1, r2, r3):
        fresh_aether()
        case()
        print()
