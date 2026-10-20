"""
D2 design probe for TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1, 2026-10-16).

Read-only on src/: every change is a monkeypatch in this process. Run from the repository root with
PYTHONPATH=src plus this folder (it imports probe_rule2_design.py). Modes, each scenario in a fresh Aether:
  today   - as shipped (0.2.8248);
  rule2   - the meld's contract scan removed; the five contracted-map mutators mark the key's consumers;
  closure - rule2, and the notch marks its dependent closure: registry edges plus contract keys (the consumers of
            an impacted lineage's key, in every Book); a mutator's mark walks on from the consumers it marked;
  catchup - closure, and before the gate a meld refreshes every stale lineage its plan expands (registry edges,
            contract providers through the melding Book): phases 1-4 with the lineage's owner Book under its rebuild
            window and lock, then its own plan reset (Phase 5+ artifacts, CreationContext, resolution_required).
Scenarios: C1 a chain Q -> P -> Dep in one Book, Q melded before the notch; C2 the same, nothing melded before it;
C3 P and Q melded before it, Q first after it - Dep is bound under a Protocol and notched to another implementer;
C4 C1 with P annotated with Dep's class and a notch to a subclass, which the kind rule does not select; X1 across
Books: the lender's P(dep: IDep) and Dep index-linked into a Book whose Consumer holds a SpellContract on P's key and
whose User depends on Consumer; the lender notches Dep.
"""
import sys
from typing import Any, Callable, Dict, List, Protocol, Set, runtime_checkable

import probe_rule2_design as base
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_compiler_system import SpellCompilerSystem
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError

MANY = Existence.many
BOOKS: List[Spellbook] = []
EXTRA: Dict[str, int] = {"closure": 0, "refresh": 0}
ORIGINAL_NOTCH = Conduit.notch_spell
ORIGINAL_MARK = base.mark


@runtime_checkable
class IDep(Protocol):
    """The dependency's contract."""

    def tag(self) -> str:
        ...


class DepA:
    """First implementer of IDep."""

    def tag(self) -> str:
        return "d1"


class DepB:
    """Second implementer of IDep, the notch target."""

    def tag(self) -> str:
        return "d2"


class PChain:
    """Depends on IDep."""

    def __init__(self, dep: IDep) -> None:
        self.dep = dep


class QChain:
    """Depends on PChain."""

    def __init__(self, p: PChain) -> None:
        self.p = p


class PClass:
    """Depends on Dep's class (C4)."""

    def __init__(self, dep: base.Dep) -> None:
        self.dep = dep


class QClass:
    """Depends on PClass (C4)."""

    def __init__(self, p: PClass) -> None:
        self.p = p


class ImplWithIDep:
    """The lender's provider with a dependency of its own (X1)."""

    def __init__(self, dep: IDep) -> None:
        self.dep = dep

    def ping(self) -> str:
        return "P+" + self.dep.tag()


class User:
    """Depends on the borrower's contract Consumer."""

    def __init__(self, c: base.Consumer) -> None:
        self.c = c


def key_of_index(index_id: str) -> Any:
    """The binding key of the lineage's active owned version, from the world's Books."""
    for book in BOOKS:
        for index, spell in list(book._spells.items()):
            if index.id == index_id:
                return spell._key
    return None


def propagate(states: Any, seeds: Set[str]) -> Set[str]:
    """Mark everything downstream of `seeds` (edges and contract keys); the seeds themselves stay as they are."""
    seen: Set[str] = set(seeds)
    by_contract: Set[str] = set()
    work = list(seeds)
    with states._lock:
        while work:
            state = states._states_by_index_id.get(work.pop())
            if state is None:
                continue
            following = set(state.direct_dependents)
            key = key_of_index(state.spell_index_id)
            if key is not None:
                for by_key in states._contract_dependents_by_spellbook.values():
                    contract_dependents = set(by_key.get(key, ()))
                    by_contract.update(contract_dependents)
                    following.update(contract_dependents)
            for index_id in following - seen:
                seen.add(index_id)
                work.append(index_id)
        for index_id in seen - set(seeds):
            state = states._states_by_index_id.get(index_id)
            if state is None:
                continue
            if index_id in by_contract:
                state.set_validity(SpellValidity.gated, change_reason=SpellStateChangeReason.contract_unvalidated,
                                   flags_to_add=[SpellState.contract_unvalidated], transitively_dirty=False)
            else:
                state.mark_transitively_dirty()
            EXTRA["closure"] += 1
    return seen - set(seeds)


def notch_with_closure(self: Conduit, *, spell_index: Any, spell: Any, **kwargs: Any) -> Any:
    result = ORIGINAL_NOTCH(self, spell_index=spell_index, spell=spell, **kwargs)
    propagate(self._spellbook._spell_system_states, {spell_index.id})
    return result


def mark_and_walk(book: Spellbook, keys: Set[Any]) -> None:
    if keys and book._conjured:
        base.COUNTS["marks"] += 1
        states = book._spell_system_states
        propagate(states, states.mark_contract_dependents_dirty(spellbook_id=book._id, contract_keys=keys))


def stale(spell: Any) -> bool:
    state = spell.system_state
    return state is not None and state.validity in (SpellValidity.gated, SpellValidity.unknown)


def neighbors(book: Spellbook, states: Any, spell: Any) -> List[Any]:
    """What `spell`'s plan expands, as Phase 8 does: topology targets by lineage, contracts through `book`."""
    topology = states._local_topologies.get(spell.spell_id)
    if topology is None:
        return []
    found: List[Any] = []
    for socket in topology.sockets:
        if socket.socket_kind is SocketKind.SPELL_CONTRACT and socket.contract_key is not None:
            for conduit_id, lookup in list(book._lookup_contracted_spells.items()):
                index = lookup.get(socket.contract_key)
                provider = (book._contracted_spells.get(conduit_id) or {}).get(index) if index else None
                if provider is not None:
                    found.append(provider)
            continue
        for target_id in socket.target_spell_ids:
            state = states._states_by_spell_id.get(target_id)
            current_id = state.current_spell_id if state is not None else target_id
            dependency = book._spell_id_pool.get(current_id)
            if dependency is not None:
                found.append(dependency)
    return found


def refresh(dependency: Any) -> None:
    """Phases 1-4 with the owner Book, then the dependency's own plan reset."""
    compiler_system = SpellCompilerSystem()
    try:
        with Meld._rebuild_window(dependency), dependency._lock:
            if not stale(dependency):
                return
            EXTRA["refresh"] += 1
            compiler_system.run_structural_phases(dependency._spellbook, dependency)
            state = dependency.system_state
            if dependency.is_broken or state is None or state.validity is not SpellValidity.valid:
                raise SpellbookValidationError([dependency])
            dependency._cleanup_creation_context()
            dependency._compiler_artifact.clear_phase5_artifacts()
            dependency.resolution_complete = False
            dependency.resolution_required = True
            dependency._door_epoch += 1
    finally:
        compiler_system.cleanup()


def catchup_gate(self: Meld, spell: Any) -> None:
    base.COUNTS["gate"] += 1
    states = spell._spell_system_states
    seen = {spell.spell_id}
    work = neighbors(self._spellbook, states, spell)
    while work:
        dependency = work.pop()
        if dependency.spell_id in seen:
            continue
        seen.add(dependency.spell_id)
        if stale(dependency):
            refresh(dependency)
        work.extend(neighbors(self._spellbook, states, dependency))
    return base.ORIGINAL["gate"](self, spell)


def set_mode(mode: str) -> None:
    base.set_mode("today" if mode == "today" else "rule2")
    walk = mode in ("closure", "catchup")
    Conduit.notch_spell = notch_with_closure if walk else ORIGINAL_NOTCH
    base.mark = mark_and_walk if walk else ORIGINAL_MARK
    if mode == "catchup":
        Meld._ensure_lineage_resolvable = catchup_gate
    EXTRA.update(closure=0, refresh=0)


def attempt(label: str, meld: Callable[[], Any], read: Callable[[Any], str]) -> None:
    base.COUNTS.update(gate=0, scan=0, pass511=0)
    EXTRA["refresh"] = 0
    counts = lambda: (f"gate={base.COUNTS['gate']} 5-11={base.COUNTS['pass511']} "
                      f"refreshed={EXTRA['refresh']}")
    try:
        value = meld()
        print(f"  {label}: got {read(value)} ({counts()})")
    except Exception as exc:
        print(f"  {label}: {type(exc).__name__}: {' '.join(str(exc).split())[:300]} ({counts()})")


def risky(book: Spellbook, conduit: Any) -> str:
    """The conduit's risky keys in RiskManager, named by the Books' spells where possible."""
    manager = book._spell_system_states._risk_manager
    bucket = manager._conduit_states.get(conduit._id)
    if bucket is None:
        return "no bucket"
    names: Dict[str, str] = {}
    for each in BOOKS:
        for index, spell in list(each._spells.items()):
            names[index.id] = spell.spell_name
            names[f"spell:{spell.spell_id}"] = spell.spell_name
    def show(keys: Set[str]) -> List[str]:
        return sorted(names.get(key, key[:18]) for key in keys)
    return f"structural={show(bucket.risky_structural)} resolution={show(bucket.risky_resolution)}"


def state_of(book: Spellbook, spell_id: str) -> str:
    spell = book.find_spell_by_id(spell_id)
    state = book._spell_system_states.get_by_index_id(spell.spell_index.id)
    return f"{state.validity.name}{sorted(flag.name for flag in state.flags)}"


def chain(mode: str, tag: str, label: str, warm_q: bool, warm_p: bool, by_class: bool = False) -> None:
    print(f"[{label}, {mode}]")
    set_mode(mode)
    book, other = base.fresh_world(f"{tag}{mode}")
    BOOKS[:] = [book, other]
    p_cls, q_cls = (PClass, QClass) if by_class else (PChain, QChain)
    frame = {} if by_class else {"spellframe": IDep, "binding_name": "dep"}
    dep_id = book.bind(spell=base.Dep if by_class else DepA, existence=MANY, permissions="create", **frame)
    p_id = book.bind(spell=p_cls, existence=MANY, permissions="create")
    q_id = book.bind(spell=q_cls, existence=MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    q_read = lambda value: value.p.dep.tag()
    p_read = lambda value: value.dep.tag()
    if warm_p:
        attempt("P before the notch", lambda: root.meld(spell=p_cls), p_read)
    if warm_q:
        attempt("Q before the notch", lambda: root.meld(spell=q_cls), q_read)
    index = book.find_spell_by_id(dep_id).spell_index
    new_id = root.bind_inactive(spell=base.Dep2 if by_class else DepB, spell_index=index, existence=MANY,
                                permissions="create", **frame)
    root.notch_spell(spell_index=index, spell=book._inactive_spells[new_id])
    print(f"  after the notch: P {state_of(book, p_id)} Q {state_of(book, q_id)} "
          f"bookflag={book._spellbook_validation_required} closure_marked={EXTRA['closure']}")
    attempt("Q after the notch", lambda: root.meld(spell=q_cls), q_read)
    attempt("Q again", lambda: root.meld(spell=q_cls), q_read)
    attempt("P", lambda: root.meld(spell=p_cls), p_read)
    attempt("Q after P", lambda: root.meld(spell=q_cls), q_read)
    print(f"  end: P {state_of(book, p_id)} Q {state_of(book, q_id)} bookflag={book._spellbook_validation_required}")
    root.cleanup()


def across(mode: str) -> None:
    print(f"[X1 across Books, {mode}]")
    set_mode(mode)
    lender_book, borrower_book = base.fresh_world(f"x1{mode}")
    BOOKS[:] = [lender_book, borrower_book]
    dep_id = lender_book.bind(spell=DepA, spellframe=IDep, binding_name="dep", existence=MANY, permissions="create")
    p_id = lender_book.bind(spell=ImplWithIDep, spellframe=base.IService, binding_name="svc", existence=MANY,
                            permissions="create")
    c_id = borrower_book.bind(spell=base.Consumer, existence=MANY, permissions="create")
    u_id = borrower_book.bind(spell=User, existence=MANY, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    p_index = lender_book.find_spell_by_id(p_id).spell_index
    d_index = lender_book.find_spell_by_id(dep_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=p_index, conduit=lender, permissions="create")
        assert borrower.add_index_to_contract(index=d_index, conduit=lender, permissions="create")
    u_read = lambda value: value.c.service.ping()
    print(f"  before any meld: flags L={lender_book._spellbook_validation_required} "
          f"B={borrower_book._spellbook_validation_required}; B risky {risky(borrower_book, borrower)}")
    attempt("User before the notch", lambda: borrower.meld(spell=User), u_read)
    new_id = lender.bind_inactive(spell=DepB, spell_index=d_index, spellframe=IDep, binding_name="dep",
                                  existence=MANY, permissions="create")
    lender.notch_spell(spell_index=d_index, spell=lender_book._inactive_spells[new_id])
    print(f"  after the notch: P {state_of(lender_book, p_id)} Consumer {state_of(borrower_book, c_id)} "
          f"User {state_of(borrower_book, u_id)} flags L={lender_book._spellbook_validation_required} "
          f"B={borrower_book._spellbook_validation_required} closure_marked={EXTRA['closure']}")
    attempt("User after the notch", lambda: borrower.meld(spell=User), u_read)
    attempt("User again", lambda: borrower.meld(spell=User), u_read)
    attempt("Consumer", lambda: borrower.meld(spell=base.Consumer), base.ping)
    attempt("lender meld of P", lambda: lender.meld(spellframe=base.IService, binding_name="svc"),
            lambda value: value.ping())
    attempt("User after both", lambda: borrower.meld(spell=User), u_read)
    print(f"  end: P {state_of(lender_book, p_id)} User {state_of(borrower_book, u_id)} "
          f"flags L={lender_book._spellbook_validation_required} B={borrower_book._spellbook_validation_required}")
    print(f"  end: B risky {risky(borrower_book, borrower)}; L risky {risky(lender_book, lender)}")
    borrower.cleanup()
    lender.cleanup()


def main() -> None:
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")
    only = set(sys.argv[1:])
    for mode in ("today", "rule2", "closure", "catchup"):
        if only and not only & {mode, "all-modes"}:
            continue
        for tag, run in (("C1", lambda m: chain(m, "c1", "C1 chain, Q warm", True, False)),
                         ("C2", lambda m: chain(m, "c2", "C2 chain, cold", False, False)),
                         ("C3", lambda m: chain(m, "c3", "C3 chain, P and Q warm", True, True)),
                         ("C4", lambda m: chain(m, "c4", "C4 chain by class, notch to a subclass", True, False,
                                                True)),
                         ("X1", across)):
            if only and not only & {tag, "all-scenarios"}:
                continue
            try:
                run(mode)
            except Exception as exc:
                print(f"  scenario aborted: {type(exc).__name__}: {' '.join(str(exc).split())[:300]}")


if __name__ == "__main__":
    main()
