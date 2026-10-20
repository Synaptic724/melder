"""
Design-phase probe for TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1, 2026-10-16).

Read-only on src/: every change below is a monkeypatch in this process. Run from the repository root with PYTHONPATH=src.
Three modes, each scenario in a fresh Aether:
  today  - the meld's contract scan live, as shipped (0.2.8247);
  noscan - the scan removed, nothing else changed (state only);
  rule2  - the scan removed, and the borrower Book's five contracted-map mutators mark the copy's key's consumers
           (`mark_contract_dependents_dirty`, mark only) after any change of an active contracted copy.
Scenarios: S1 index-link notch, notch back and repeat notch; S2 a version-anchored grant and a notch; S3 a notch to a
version whose __init__ cannot be resolved, against the first meld of that version; S4 an index destroy; S5 a notch of
the provider's own dependency; S6 a unique consumer (stored objects keep their provider). Cost of a warm meld per mode.
"""
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Tuple, runtime_checkable

from melder import Aether, Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


@runtime_checkable
class IService(Protocol):
    """The contract a lender provides."""

    def ping(self) -> str:
        ...


class Missing:
    """A type nobody binds."""


class Dep:
    """A dependency of the lent service, first version."""

    def tag(self) -> str:
        return "d1"


class Dep2(Dep):
    """Second version of the dependency (a subclass, so `dep: Dep` still matches it)."""

    def tag(self) -> str:
        return "d2"


class ImplA:
    """First version of the lent service."""

    def ping(self) -> str:
        return "A"


class ImplB:
    """Second version of the lent service."""

    def ping(self) -> str:
        return "B"


class ImplBroken:
    """A version whose __init__ needs a type nobody binds."""

    def __init__(self, missing: Missing) -> None:
        self.missing = missing

    def ping(self) -> str:
        return "broken"


class ImplWithDep:
    """A version of the lent service with a dependency of its own."""

    def __init__(self, dep: Dep) -> None:
        self.dep = dep

    def ping(self) -> str:
        return "P+" + self.dep.tag()


class Consumer:
    """Borrower-side consumer of the contract."""

    def __init__(self, service: IService = SpellContract(spellframe=IService, binding_name="svc")) -> None:
        self.service = service


COUNTS: Dict[str, int] = {"gate": 0, "scan": 0, "pass511": 0, "marks": 0}
ORIGINAL: Dict[str, Callable[..., Any]] = {
    "gate": Meld._ensure_lineage_resolvable,
    "scan": Meld._check_contracts_and_force_revalidation,
    "pass511": Spellbook._run_resolution_phases_for_target_spell,
    "add": Spellbook._add_contracted_spell,
    "park": Spellbook._deactivate_contracted_spell,
    "reactivate": Spellbook._reactivate_contracted_spell,
    "remove": Spellbook._remove_contracted_spell,
    "clear": Spellbook._clear_contracted_spells_for_conduit,
}


def counting_gate(self: Meld, spell: Any) -> None:
    COUNTS["gate"] += 1
    return ORIGINAL["gate"](self, spell)


def counting_scan(self: Meld, spell: Any) -> None:
    COUNTS["scan"] += 1
    return ORIGINAL["scan"](self, spell)


def removed_scan(self: Meld, spell: Any) -> None:
    return None


def counting_pass(self: Spellbook, conduit_id: str, spell: Any) -> Any:
    COUNTS["pass511"] += 1
    return ORIGINAL["pass511"](self, conduit_id, spell)


def mark(book: Spellbook, keys: Set[Tuple[str, str]]) -> None:
    """The emulated rule-2 marking: gate the Book's consumers of these keys, mark only."""
    if keys and book._conjured:
        COUNTS["marks"] += 1
        book._spell_system_states.mark_contract_dependents_dirty(spellbook_id=book._id, contract_keys=keys)


def marking_add(self: Spellbook, spell: Any, conduit_id: str) -> None:
    ORIGINAL["add"](self, spell, conduit_id)
    mark(self, {spell._key})


def marking_park(self: Spellbook, conduit_id: str, spell: Any) -> None:
    ORIGINAL["park"](self, conduit_id, spell)
    mark(self, {spell._key})


def marking_reactivate(self: Spellbook, conduit_id: str, spell: Any) -> None:
    ORIGINAL["reactivate"](self, conduit_id, spell)
    mark(self, {spell._key})


def marking_remove(self: Spellbook, spell_id: str, conduit_id: str) -> None:
    active = (self._contracted_spells_by_id.get(conduit_id) or {}).get(spell_id)
    if active is None:
        for spell in list((self._contracted_spells.get(conduit_id) or {}).values()):
            if spell.spell_id == spell_id or spell_id in (spell.spell_index._spells_in_index or ()):
                active = spell
    ORIGINAL["remove"](self, spell_id, conduit_id)
    if active is not None:
        mark(self, {active._key})


def marking_clear(self: Spellbook, conduit_id: str) -> None:
    keys = {spell._key for spell in list((self._contracted_spells.get(conduit_id) or {}).values())}
    ORIGINAL["clear"](self, conduit_id)
    mark(self, keys)


def set_mode(mode: str) -> None:
    """Install one mode's patches."""
    Meld._ensure_lineage_resolvable = counting_gate
    Spellbook._run_resolution_phases_for_target_spell = counting_pass
    Meld._check_contracts_and_force_revalidation = counting_scan if mode == "today" else removed_scan
    rule2 = mode == "rule2"
    Spellbook._add_contracted_spell = marking_add if rule2 else ORIGINAL["add"]
    Spellbook._deactivate_contracted_spell = marking_park if rule2 else ORIGINAL["park"]
    Spellbook._reactivate_contracted_spell = marking_reactivate if rule2 else ORIGINAL["reactivate"]
    Spellbook._remove_contracted_spell = marking_remove if rule2 else ORIGINAL["remove"]
    Spellbook._clear_contracted_spells_for_conduit = marking_clear if rule2 else ORIGINAL["clear"]


def fresh_world(frame: str) -> Tuple[Spellbook, Spellbook]:
    """A fresh Aether with a dynamic frame, caching off, and two Books on it."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                       system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    return lender_book, borrower_book


def lineage(book: Spellbook, spell_id: str) -> str:
    """The consumer lineage's validity and flags, and the Book flag."""
    spell = book.find_spell_by_id(spell_id)
    state = book._spell_system_states.get_by_index_id(spell.spell_index.id)
    flags = sorted(flag.name for flag in state.flags)
    return f"{state.validity.name} {flags} bookflag={book._spellbook_validation_required}"


def attempt(label: str, meld: Callable[[], Any], read: Callable[[Any], str]) -> None:
    """Meld once and print what came back, with the gate, scan and 5-11 counts of that meld."""
    COUNTS.update(gate=0, scan=0, pass511=0)
    try:
        value = meld()
        print(f"  {label}: got {read(value)} (gate={COUNTS['gate']} scan={COUNTS['scan']} 5-11={COUNTS['pass511']})")
    except Exception as exc:
        text = " ".join(str(exc).split())
        print(f"  {label}: {type(exc).__name__}: {text[:420]}")


def warm_cost(meld: Callable[[], Any], rounds: int) -> str:
    """Microseconds per warm meld, with the gate, scan and 5-11 counts per meld."""
    for _ in range(20):
        meld()
    COUNTS.update(gate=0, scan=0, pass511=0)
    start = time.perf_counter()
    for _ in range(rounds):
        meld()
    elapsed = (time.perf_counter() - start) / rounds * 1e6
    per = {key: COUNTS[key] / rounds for key in ("gate", "scan", "pass511")}
    return f"{elapsed:.1f} us per meld (gate={per['gate']:.2f} scan={per['scan']:.2f} 5-11={per['pass511']:.2f})"


def linked(mode: str, frame: str, impl: type, consumer_existence: Existence, index_link: bool,
           impl_existence: Existence = Existence.many) -> Tuple[Spellbook, Spellbook, Any, Any, str, str]:
    """Lender lends `impl` under (IService, "svc"); borrower binds Consumer; link plus index link or grant."""
    set_mode(mode)
    lender_book, borrower_book = fresh_world(frame)
    provider_id = lender_book.bind(spell=impl, spellframe=IService, binding_name="svc", existence=impl_existence,
                                   permissions="create")
    consumer_id = borrower_book.bind(spell=Consumer, existence=consumer_existence, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    index = lender_book.find_spell_by_id(provider_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        if index_link:
            assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
        else:
            assert borrower.add_spell_to_contract(spell_id=provider_id, conduit=lender, permissions="create")
    return lender_book, borrower_book, lender, borrower, provider_id, consumer_id


def notch_to(lender: Any, lender_book: Spellbook, index: Any, impl: type) -> str:
    """bind_inactive `impl` into the provider's index and notch to it; return its id."""
    new_id = lender.bind_inactive(spell=impl, spell_index=index, spellframe=IService, binding_name="svc",
                                  existence=Existence.many, permissions="create")
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[new_id])
    return new_id


def ping(value: Any) -> str:
    return value.service.ping()


def s1_index_link(mode: str) -> None:
    """Index link: notch to B, notch back to A, repeat notch to B."""
    print(f"[S1 index link, {mode}]")
    lender_book, borrower_book, lender, borrower, a_id, c_id = linked(mode, f"s1{mode}", ImplA, Existence.many, True)
    index = lender_book.find_spell_by_id(a_id).spell_index
    attempt("first meld", lambda: borrower.meld(spell=Consumer), ping)
    print(f"  warm: {warm_cost(lambda: borrower.meld(spell=Consumer), 200)}")
    b_id = notch_to(lender, lender_book, index, ImplB)
    print(f"  after notch to B: consumer {lineage(borrower_book, c_id)}")
    attempt("meld after notch", lambda: borrower.meld(spell=Consumer), ping)
    attempt("next meld", lambda: borrower.meld(spell=Consumer), ping)
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[a_id])
    print(f"  after notch back to A: consumer {lineage(borrower_book, c_id)}")
    attempt("meld after notch back", lambda: borrower.meld(spell=Consumer), ping)
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[b_id])
    attempt("meld after repeat notch to B", lambda: borrower.meld(spell=Consumer), ping)
    print(f"  warm: {warm_cost(lambda: borrower.meld(spell=Consumer), 200)}")
    borrower.cleanup()
    lender.cleanup()


def s2_grant(mode: str) -> None:
    """Version-anchored grant of A, then a notch to B and back."""
    print(f"[S2 grant, {mode}]")
    lender_book, borrower_book, lender, borrower, a_id, c_id = linked(mode, f"s2{mode}", ImplA, Existence.many, False)
    index = lender_book.find_spell_by_id(a_id).spell_index
    attempt("first meld", lambda: borrower.meld(spell=Consumer), ping)
    notch_to(lender, lender_book, index, ImplB)
    print(f"  after notch to B: consumer {lineage(borrower_book, c_id)}")
    attempt("meld after notch", lambda: borrower.meld(spell=Consumer), ping)
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[a_id])
    attempt("meld after notch back", lambda: borrower.meld(spell=Consumer), ping)
    borrower.cleanup()
    lender.cleanup()


def s3_unresolvable(mode: str) -> None:
    """A notch to a version whose __init__ needs an unbound type, and the first meld of that version."""
    print(f"[S3 unresolvable version, {mode}]")
    lender_book, borrower_book, lender, borrower, a_id, c_id = linked(mode, f"s3{mode}", ImplA, Existence.many, True)
    index = lender_book.find_spell_by_id(a_id).spell_index
    attempt("first meld", lambda: borrower.meld(spell=Consumer), ping)
    notch_to(lender, lender_book, index, ImplBroken)
    attempt("meld after notch to ImplBroken", lambda: borrower.meld(spell=Consumer), ping)
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[a_id])
    attempt("meld after notch back to A", lambda: borrower.meld(spell=Consumer), ping)
    borrower.cleanup()
    lender.cleanup()
    lender_book, borrower_book, lender, borrower, _, _ = linked(mode, f"s3f{mode}", ImplBroken, Existence.many, True)
    attempt("first meld with ImplBroken lent from the start", lambda: borrower.meld(spell=Consumer), ping)
    borrower.cleanup()
    lender.cleanup()


def s4_destroy(mode: str) -> None:
    """The provider's sole-member index is destroyed by cleanup_spell."""
    print(f"[S4 index destroy, {mode}]")
    lender_book, borrower_book, lender, borrower, a_id, c_id = linked(mode, f"s4{mode}", ImplA, Existence.many, True)
    attempt("first meld", lambda: borrower.meld(spell=Consumer), ping)
    lender.cleanup_spell(spell=lender_book.find_spell_by_id(a_id))
    print(f"  after destroy: consumer {lineage(borrower_book, c_id)}")
    attempt("meld after destroy", lambda: borrower.meld(spell=Consumer), ping)
    borrower.cleanup()
    lender.cleanup()


def s5_dependency_notch(mode: str) -> None:
    """The provider has a dependency of its own, also index-linked; the lender notches the dependency."""
    print(f"[S5 provider dependency notch, {mode}]")
    set_mode(mode)
    lender_book, borrower_book = fresh_world(f"s5{mode}")
    dep_id = lender_book.bind(spell=Dep, existence=Existence.many, permissions="create")
    lender_book.bind(spell=ImplWithDep, spellframe=IService, binding_name="svc", existence=Existence.many,
                     permissions="create")
    c_id = borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    p_index = next(index for index, spell in lender_book._spells.items() if spell.spell is ImplWithDep)
    d_index = lender_book.find_spell_by_id(dep_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=p_index, conduit=lender, permissions="create")
        assert borrower.add_index_to_contract(index=d_index, conduit=lender, permissions="create")
    attempt("first meld", lambda: borrower.meld(spell=Consumer), ping)
    d2_id = lender.bind_inactive(spell=Dep2, spell_index=d_index, existence=Existence.many, permissions="create")
    lender.notch_spell(spell_index=d_index, spell=lender_book._inactive_spells[d2_id])
    print(f"  after the dependency notch: consumer {lineage(borrower_book, c_id)}")
    attempt("meld after the dependency notch", lambda: borrower.meld(spell=Consumer), ping)
    attempt("lender meld of the provider", lambda: lender.meld(spellframe=IService, binding_name="svc"),
            lambda value: value.ping())
    attempt("borrower meld after the lender's meld", lambda: borrower.meld(spell=Consumer), ping)
    borrower.cleanup()
    lender.cleanup()


def s6_unique_consumer(mode: str) -> None:
    """A unique consumer: after a notch its stored object keeps its provider (mark only)."""
    print(f"[S6 unique consumer, {mode}]")
    lender_book, borrower_book, lender, borrower, a_id, c_id = linked(mode, f"s6{mode}", ImplA, Existence.unique,
                                                                      True)
    index = lender_book.find_spell_by_id(a_id).spell_index
    first = borrower.meld(spell=Consumer)
    print(f"  first meld: got {first.service.ping()}")
    notch_to(lender, lender_book, index, ImplB)
    attempt("meld after notch", lambda: borrower.meld(spell=Consumer),
            lambda value: f"{value.service.ping()} same_object={value is first}")
    borrower.purge(spell=Consumer)
    attempt("meld after purge", lambda: borrower.meld(spell=Consumer), ping)
    borrower.cleanup()
    lender.cleanup()


def main() -> None:
    """Run every scenario in every mode."""
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")
    for mode in ("today", "noscan", "rule2"):
        COUNTS["marks"] = 0
        for scenario in (s1_index_link, s2_grant, s3_unresolvable, s4_destroy, s5_dependency_notch,
                         s6_unique_consumer):
            try:
                scenario(mode)
            except Exception as exc:
                text = " ".join(str(exc).split())
                print(f"  scenario {scenario.__name__} aborted: {type(exc).__name__}: {text[:300]}")
        print(f"[{mode}] marks issued: {COUNTS['marks']}")


if __name__ == "__main__":
    main()
