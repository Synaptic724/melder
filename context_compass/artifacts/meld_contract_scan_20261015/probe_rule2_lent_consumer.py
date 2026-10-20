"""
Design-phase probe for TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1, 2026-10-16).

A SpellContract consumer lent to a second Book (a "lent consumer"): the second Book melds it and resolves its contract
against its own contracted maps. Read-only on src/: the modes are the monkeypatches of probe_rule2_design.py (run from
the repository root with PYTHONPATH=src; this file sits beside that probe and imports it).
  today - as shipped (0.2.8247); rule2 - the scan removed, the five Book mutators mark the copy's key's consumers.
World: lender L, owner O, third Book T; O and T index-link L's provider; T borrows Consumer from O; both meld it (A).
L1: L notches A -> B; the two Books meld again, T first (L1a) or O first (L1b).
L3: T alone drops its index link to the provider; T melds the lent consumer, then O melds it.
L4: T alone severs its link to L; T melds the lent consumer, then O melds it.
(A first version had L2: T borrowing the key from a second lender. Bind refuses it: one active spell per
spellframe/binding signature per frame, so one key has one provider lineage frame-wide.)
"""
import sys
from typing import Any, Tuple

import probe_rule2_design as base
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


def book(frame: str) -> Spellbook:
    """Another Book on the probe's frame."""
    return Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())


def borrow_index(borrower: Any, lender: Any, index: Any) -> None:
    """The borrower takes an index link to the lender's index."""
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")


def borrow_spell(borrower: Any, lender: Any, spell_id: str) -> None:
    """The borrower takes a version-anchored grant of one of the lender's spells."""
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_spell_to_contract(spell_id=spell_id, conduit=lender, permissions="create")


def world(mode: str, frame: str) -> Tuple[Any, ...]:
    """Lender L, owner O, third Book T; O and T borrow L's provider index; T borrows Consumer from O; both meld."""
    base.set_mode(mode)
    l_book, o_book = base.fresh_world(frame)
    t_book = book(frame)
    a_id = l_book.bind(spell=base.ImplA, spellframe=base.IService, binding_name="svc", existence=Existence.many,
                       permissions="create")
    c_id = o_book.bind(spell=base.Consumer, existence=Existence.many, permissions="create")
    lender = l_book.conjure(dynamic=True, name="lender")
    owner = o_book.conjure(dynamic=True, name="owner")
    third = t_book.conjure(dynamic=True, name="third")
    lender.link(owner)
    lender.link(third)
    owner.link(third)
    index = l_book.find_spell_by_id(a_id).spell_index
    borrow_index(owner, lender, index)
    borrow_index(third, lender, index)
    borrow_spell(third, owner, c_id)
    base.attempt("O first meld", lambda: owner.meld(spell=base.Consumer), base.ping)
    base.attempt("T first meld", lambda: third.meld(spell=base.Consumer), base.ping)
    return l_book, o_book, t_book, lender, owner, third, index, c_id


def l1(mode: str, third_first: bool) -> None:
    """The lender notches; both Books meld again in the given order."""
    order = "T first" if third_first else "O first"
    print(f"[L1 lent consumer, lender notch, {order}, {mode}]")
    l_book, o_book, t_book, lender, owner, third, index, c_id = world(mode, f"l1{mode}{int(third_first)}")
    base.notch_to(lender, l_book, index, base.ImplB)
    print(f"  after notch to B: consumer {base.lineage(o_book, c_id)}; T bookflag={t_book._spellbook_validation_required}")
    pair = (("T", third), ("O", owner)) if third_first else (("O", owner), ("T", third))
    for name, conduit in pair:
        base.attempt(f"{name} meld after notch", lambda: conduit.meld(spell=base.Consumer), base.ping)
    for name, conduit in pair:
        base.attempt(f"{name} next meld", lambda: conduit.meld(spell=base.Consumer), base.ping)
    for conduit in (third, owner, lender):
        conduit.cleanup()


def l3(mode: str) -> None:
    """T alone drops its index link to the provider."""
    print(f"[L3 lent consumer, T drops its provider index link, {mode}]")
    l_book, o_book, t_book, lender, owner, third, index, c_id = world(mode, f"l3{mode}")
    third.remove_index_from_contract(index_id=index.id, conduit=lender)
    print(f"  after T's removal: consumer {base.lineage(o_book, c_id)}; T bookflag={t_book._spellbook_validation_required}")
    base.attempt("T meld", lambda: third.meld(spell=base.Consumer), base.ping)
    base.attempt("O meld", lambda: owner.meld(spell=base.Consumer), base.ping)
    base.attempt("T meld after O's", lambda: third.meld(spell=base.Consumer), base.ping)
    for conduit in (third, owner, lender):
        conduit.cleanup()


def l4(mode: str) -> None:
    """T alone severs its link to the lender."""
    print(f"[L4 lent consumer, T severs its link to L, {mode}]")
    l_book, o_book, t_book, lender, owner, third, index, c_id = world(mode, f"l4{mode}")
    third.sever_link(lender)
    print(f"  after T's sever: consumer {base.lineage(o_book, c_id)}; T bookflag={t_book._spellbook_validation_required}")
    base.attempt("T meld", lambda: third.meld(spell=base.Consumer), base.ping)
    base.attempt("O meld", lambda: owner.meld(spell=base.Consumer), base.ping)
    base.attempt("T meld after O's", lambda: third.meld(spell=base.Consumer), base.ping)
    for conduit in (third, owner, lender):
        conduit.cleanup()


def main() -> None:
    """Run every scenario in both modes."""
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")
    for mode in ("today", "rule2"):
        base.COUNTS["marks"] = 0
        for scenario in (lambda m: l1(m, True), lambda m: l1(m, False), l3, l4):
            try:
                scenario(mode)
            except Exception as exc:
                text = " ".join(str(exc).split())
                print(f"  scenario aborted: {type(exc).__name__}: {text[:400]}")
        print(f"[{mode}] marks issued: {base.COUNTS['marks']}")


if __name__ == "__main__":
    main()
