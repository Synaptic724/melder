"""S6 probe: what an ownership transfer does with managed pools on the current tree.

Scenarios (each in a fresh dynamic world, two Books in one frame, root "owner" -> root "target"):
  A  move (default), active member only: the pool, its idle objects, the registry, leases and releases after the move
  B  move with a version parked after conjure: where its pool and its owner store go; a notch to it on the target
  C  no move: the target's pool, the old pool's idle objects
  D  a failed transfer (forced after the creations step), move: what rollback leaves (stores, owner store, leases)
  E  the same with no move
  F  a `unique` spell: a failed transfer (move), then a meld on the owner - which store holds the object
  G  a `unique` version parked after conjure, moved, then notched in on the target - which store
Run from the tree root: PYTHONPATH=src:. python -X gil=0|1 probe_s6_managed_transfer.py
"""
import sys
import traceback

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Session:
    """The managed class."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Anchor:
    """A plain spell for the target Book."""


def world():
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(spell=Session, existence=Existence.managed_spell_quantity, permissions="create",
                               disposal_method_names=["close"], managed_spell_limit=16)
    target_book = Spellbook(configuration=configuration)
    target_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    return owner_book, target_book, owner, target, spell_id


def pools(owner, target, spell_id):
    a = owner._creations.get_managed_quantity(spell_id)
    b = target._creations.get_managed_quantity(spell_id)
    return a, b


def show(label, owner, target, spell_id):
    a, b = pools(owner, target, spell_id)
    rows = [(r["spell_id"][:8], r["holding_conduit_id"] == owner.id and "owner" or
             r["holding_conduit_id"] == target.id and "target" or r["holding_conduit_id"], r["count"], r["idle_count"])
            for r in ReleaseManagedSpell().describe(Session)]
    print(f"  {label}: owner pool={None if a is None else (a.count, a.idle_count)} "
          f"target pool={None if b is None else (b.count, b.idle_count)} registry={rows}")
    return a, b


def lease_two(conduit, spell_id):
    one, two = conduit.meld(spell_id=spell_id), conduit.meld(spell_id=spell_id)
    ReleaseManagedSpell().release(one)
    ReleaseManagedSpell().release(two)
    return one, two


def scenario_a():
    print("A move (default), active member only")
    owner_book, target_book, owner, target, spell_id = world()
    one, two = lease_two(owner, spell_id)
    before, _ = show("before", owner, target, spell_id)
    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)
    _, after = show("after", owner, target, spell_id)
    print("  same pool object moved:", after is before)
    spell = target_book.find_spell_by_id(spell_id)
    print("  spell owner store is target's:", spell._owner_creations is target._creations)
    leased = target.meld(spell_id=spell_id)
    print("  target meld reuses an idle object:", leased in (one, two))
    ReleaseManagedSpell().release(leased)
    show("after release", owner, target, spell_id)


def scenario_b():
    print("B move with a version parked after conjure, then a notch to it on the target")
    owner_book, target_book, owner, target, spell_id = world()
    parked_id = owner.bind_inactive(
        spell=Session, spell_index=owner_book.find_spell_by_id(spell_id).spell_index,
        existence=Existence.managed_spell_quantity, permissions="create", disposal_method_names=["close"],
        managed_spell_limit=8,
    )
    parked = owner_book._get_owned_spell(parked_id)
    print("  parked owner store is owner's before:", parked._owner_creations is owner._creations,
          "pool:", owner._creations.get_managed_quantity(parked_id) is not None)
    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)
    print("  parked pool in target store:", target._creations.get_managed_quantity(parked_id) is not None,
          "in owner store:", owner._creations.get_managed_quantity(parked_id) is not None)
    print("  parked owner store after: owner's =", parked._owner_creations is owner._creations,
          "target's =", parked._owner_creations is target._creations,
          "owner conduit id = target:", parked._owner_conduit_id == target.id)
    target.notch_spell(spell_index=parked.spell_index, spell=parked)
    try:
        obj = target.meld(spell=Session)
        print("  meld after notch:", type(obj).__name__, "from target pool:",
              target._creations.get_managed_quantity(parked_id).count)
    except Exception as exc:
        print("  meld after notch raised:", type(exc).__name__, str(exc)[:240])


def scenario_c():
    print("C no move")
    owner_book, target_book, owner, target, spell_id = world()
    one, two = lease_two(owner, spell_id)
    before, _ = show("before", owner, target, spell_id)
    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target, move_creations=False)
    _, after = show("after", owner, target, spell_id)
    print("  new pool on the target:", after is not None and after is not before,
          "old idle objects undisposed:", not one.closed and not two.closed)
    leased = target.meld(spell_id=spell_id)
    print("  target meld builds new:", leased not in (one, two))


def failing_transfer(move):
    original = TransferOfOwnership._gate_transfer_impacts

    def boom(self, **kwargs):
        raise RuntimeError("forced failure after the creations step")

    TransferOfOwnership._gate_transfer_impacts = boom
    try:
        return world_and_fail(move)
    finally:
        TransferOfOwnership._gate_transfer_impacts = original


def world_and_fail(move):
    owner_book, target_book, owner, target, spell_id = world()
    one, two = lease_two(owner, spell_id)
    before, _ = show("before", owner, target, spell_id)
    try:
        owner.transfer_spell_ownership(spell=spell_id, target_conduit=target, move_creations=move)
        print("  transfer did not fail")
    except Exception as exc:
        print("  transfer raised:", type(exc).__name__, str(exc)[:120])
    a, b = show("after rollback", owner, target, spell_id)
    print("  owner keeps the same pool:", a is before)
    spell = owner_book.find_spell_by_id(spell_id)
    print("  spell found in owner book:", spell is not None)
    if spell is not None:
        print("  spell owner store: owner's =", spell._owner_creations is owner._creations,
              "target's =", spell._owner_creations is target._creations)
    try:
        obj = owner.meld(spell_id=spell_id)
        print("  owner meld after rollback:", "reused" if obj in (one, two) else "new object")
        ReleaseManagedSpell().release(obj)
        print("  release by class: ok")
    except Exception as exc:
        print("  owner meld/release after rollback raised:", type(exc).__name__, str(exc)[:240])


class Keeper:
    """A plain `unique` class for scenarios F and G (a second version differs by its disposal names)."""

    def close(self) -> None:
        """Nothing to release."""


def unique_world():
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(spell=Keeper, existence=Existence.unique, permissions="create")
    target_book = Spellbook(configuration=configuration)
    target_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    return owner_book, target_book, owner, target, spell_id


def scenario_f():
    print("F unique: failed transfer (move), then a meld on the owner")
    original = TransferOfOwnership._gate_transfer_impacts

    def boom(self, **kwargs):
        raise RuntimeError("forced failure after the creations step")

    TransferOfOwnership._gate_transfer_impacts = boom
    try:
        owner_book, target_book, owner, target, spell_id = unique_world()
        first = owner.meld(spell_id=spell_id)
        try:
            owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)
        except Exception as exc:
            print("  transfer raised:", type(exc).__name__)
    finally:
        TransferOfOwnership._gate_transfer_impacts = original
    spell = owner_book.find_spell_by_id(spell_id)
    print("  spell owner store: owner's =", spell._owner_creations is owner._creations,
          "target's =", spell._owner_creations is target._creations)
    print("  owner store holds the first object:", owner._creations.get_creation(spell_id) is first)
    again = owner.meld(spell_id=spell_id)
    print("  owner meld returns the first object:", again is first,
          "| target store holds an object:", target._creations.get_creation(spell_id) is not None)


def scenario_g():
    print("G unique: version parked after conjure, moved, notched in on the target")
    owner_book, target_book, owner, target, spell_id = unique_world()
    parked_id = owner.bind_inactive(spell=Keeper, spell_index=owner_book.find_spell_by_id(spell_id).spell_index,
                                    existence=Existence.unique, permissions="create",
                                    disposal_method_names=["close"])
    parked = owner_book._get_owned_spell(parked_id)
    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)
    target.notch_spell(spell_index=parked.spell_index, spell=parked)
    obj = target.meld(spell=Keeper)
    print("  object stored in: owner store =", owner._creations.get_creation(parked_id) is obj,
          "target store =", target._creations.get_creation(parked_id) is obj)


def main() -> int:
    for scenario in (scenario_a, scenario_b, scenario_c):
        try:
            scenario()
        except Exception:
            traceback.print_exc(limit=4)
    print("D failed transfer, move")
    failing_transfer(True)
    print("E failed transfer, no move")
    failing_transfer(False)
    for scenario in (scenario_f, scenario_g):
        try:
            scenario()
        except Exception:
            traceback.print_exc(limit=4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
