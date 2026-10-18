"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A6): managed pools across a version's life.

What it checks, each case in a fresh Aether and its own dynamic frame with caching off. `Worker` is one class; a
version is a binding of it with its own managed options (so its own spell_id and its own pool):
  Q1  control: one limited_quantity version (limit 1) - lease, `ReleaseManagedSpell().release(obj)`, lease again.
  Q2  two versions of the one class on one index: A (limited_quantity, limit 1) active, an object leased from A;
      B (limited_quantity, limit 2) staged and notched in; the object released with no filter; then B leased,
      then a notch back to A and A leased.
  Q3  Q2 with the release naming its version: `release(obj, spell_id=A)`.
  Q4  Q2 with A disposed (cleanup_spell) after the notch away, before the release.
  Q5  a disposed version bound again under the same content-stable spell_id: its pool is met and re-pointed.
  Q6  control: two versions that are two classes (the usual agent loop) - the release finds its pool by class.
For each step it prints every pool of the class (`ReleaseManagedSpell().describe`): version, count, idle, active.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_managed_release_routing.py
"""
import itertools
from typing import Dict

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

SERIALS = itertools.count(1)


class Worker:
    """The managed class every case leases; each object carries the serial of its construction."""

    def __init__(self) -> None:
        """Take the next serial."""
        self.serial = next(SERIALS)

    def reset(self) -> None:
        """The reset a release runs."""


class WorkerV2:
    """A second class, for the two-class control."""

    def __init__(self) -> None:
        """Take the next serial."""
        self.serial = next(SERIALS)


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str, cls: type = Worker, limit: int = 1):
    """One dynamic Book on `frame` with `cls` bound managed limited_quantity (`limit`), conjured."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                     system_caching_enabled=False)
    spell_id = spellbook.bind(spell=cls, spellframe="workers", binding_name="worker",
                              existence=Existence.managed_spell_quantity, permissions="create",
                              managed_spell_mode="limited_quantity", managed_spell_limit=limit,
                              managed_spell_reset_methods=["reset"] if cls is Worker else None)
    conduit = spellbook.conjure(dynamic=True, name="root")
    return spellbook, conduit, spell_id


def stage(conduit: Conduit, index, cls: type = Worker, limit: int = 2) -> str:
    """Stage `cls` managed limited_quantity (`limit`) parked on `index`."""
    return conduit.bind_inactive(spell=cls, spell_index=index, spellframe="workers", binding_name="worker",
                                 existence=Existence.managed_spell_quantity, permissions="create",
                                 managed_spell_mode="limited_quantity", managed_spell_limit=limit,
                                 managed_spell_reset_methods=["reset"] if cls is Worker else None)


def pools(step: str, cls: type, names: Dict[str, str]) -> None:
    """Print every pool of `cls`: version, count, idle, active."""
    print(f"  [{step}]")
    for snapshot in ReleaseManagedSpell().describe(cls):
        print(f"    pool {names.get(snapshot['spell_id'], snapshot['spell_id'][:10])}: count {snapshot['count']},"
              f" idle {snapshot['idle_count']}, active_version {snapshot['active_version']}")


def lease(conduit: Conduit, spell_id: str, label: str):
    """Meld `spell_id` (a plain meld; the holder gives the object back through the registry)."""
    try:
        obj = conduit.meld(spell_id=spell_id)
        print(f"    meld {label} -> Worker #{obj.serial}")
        return obj
    except Exception as error:
        print(f"    meld {label} raised {type(error).__name__}: {str(error)[:170]}")
        return None


def q1() -> None:
    """Control: one version."""
    print("Q1 control: one limited_quantity version (limit 1)")
    spellbook, conduit, a = world("q1")
    names = {a: "A"}
    obj = lease(conduit, a, "A")
    pools("after the lease", Worker, names)
    ReleaseManagedSpell().release(obj)
    pools("after release(obj)", Worker, names)
    lease(conduit, a, "A again")


def two_versions(frame: str):
    """A active (limit 1) with one object out; B (limit 2) staged on A's index and notched in."""
    spellbook, conduit, a = world(frame)
    index = spellbook.find_spell_by_spell_id(a).spell_index
    names = {a: "A"}
    obj = lease(conduit, a, "A")
    b = stage(conduit, index)
    names[b] = "B"
    conduit.notch_spell(spell_index=index, spell_id=b)
    pools("A leased once, B staged and notched in", Worker, names)
    return spellbook, conduit, index, a, b, names, obj


def q2() -> None:
    """Two versions of one class; release with no filter."""
    print("Q2 two versions of Worker on one index; the object leased from A released with no filter after a notch")
    spellbook, conduit, index, a, b, names, obj = two_versions("q2")
    ReleaseManagedSpell().release(obj)
    pools("after release(obj)", Worker, names)
    leased = lease(conduit, b, "B")
    print(f"    B served the object leased from A: {leased is obj}")
    conduit.notch_spell(spell_index=index, spell_id=a)
    pools("after a notch back to A", Worker, names)
    lease(conduit, a, "A")


def q3() -> None:
    """Q2 with the release naming its version."""
    print("Q3 Q2 with release(obj, spell_id=A)")
    spellbook, conduit, index, a, b, names, obj = two_versions("q3")
    ReleaseManagedSpell().release(obj, spell_id=a)
    pools("after release(obj, spell_id=A)", Worker, names)
    conduit.notch_spell(spell_index=index, spell_id=a)
    leased = lease(conduit, a, "A after a notch back")
    print(f"    A served its own object again: {leased is obj}")


def q4() -> None:
    """Q2 with A disposed before the release."""
    print("Q4 Q2 with A disposed (cleanup_spell) after the notch away, before the release")
    spellbook, conduit, index, a, b, names, obj = two_versions("q4")
    conduit.cleanup_spell(spell=spellbook._inactive_spells[a])
    print(f"    A owned by the Book after cleanup_spell: {a in spellbook._spell_ids}")
    pools("after cleanup_spell(A)", Worker, names)
    ReleaseManagedSpell().release(obj)
    pools("after release(obj)", Worker, names)


def q5() -> None:
    """A disposed version bound again under the same spell_id."""
    print("Q5 cleanup_spell of the only version, then the same binding again (same content-stable spell_id)")
    spellbook, conduit, a = world("q5")
    names = {a: "A"}
    obj = lease(conduit, a, "A")
    ReleaseManagedSpell().release(obj)
    conduit.cleanup_spell(spell=spellbook.find_spell_by_spell_id(a))
    pools("after cleanup_spell(A)", Worker, names)
    again = conduit.bind(spell=Worker, spellframe="workers", binding_name="worker",
                         existence=Existence.managed_spell_quantity, permissions="create",
                         managed_spell_mode="limited_quantity", managed_spell_limit=1,
                         managed_spell_reset_methods=["reset"])
    print(f"    the same spell_id again: {again == a}")
    pools("after the same binding again", Worker, names)
    leased = lease(conduit, again, "A again")
    print(f"    served the object idle in the pool its earlier definition left: {leased is obj}")


def q6() -> None:
    """Control: two versions that are two classes."""
    print("Q6 control: A binds Worker, B binds WorkerV2 on the same index")
    spellbook, conduit, a = world("q6")
    index = spellbook.find_spell_by_spell_id(a).spell_index
    names = {a: "A"}
    obj = lease(conduit, a, "A")
    b = stage(conduit, index, cls=WorkerV2)
    names[b] = "B"
    conduit.notch_spell(spell_index=index, spell_id=b)
    ReleaseManagedSpell().release(obj)
    pools("Worker pools after the release", Worker, names)
    pools("WorkerV2 pools", WorkerV2, names)


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (q1, q2, q3, q4, q5, q6):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
