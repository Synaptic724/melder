"""Probe: the real objects behind the owner's four questions (melder_1, 2026-10-16).

Read-only on src/. usage, from a scratch directory, one world per process:
  PYTHONPATH=<tree>/src python <this script> contract|lookup|notch|transfer
contract - the objects a borrow is made of: the Contract's rows (Detail per version, IndexDetail per linked index)
           and the borrower Book's copy maps, before and after the lender notches; an index link and a version grant.
lookup   - how a spell_id is looked up in the owner Book (find_spell_by_id vs _get_owned_spell) and what that does
           to add_spell_to_contract for a parked version.
trace    - each hop of get_spell_by_id(<parked French>): the frame registry, then the owner Book's three maps.
notch    - the registry objects rule 2 walks (state, edges, contract keys, contract users) and what a notch marks.
transfer - the same world, but the lender first transfers English to a third root: what the registry, the contract
           and the Books hold after it, and what the same notch marks then.
"""
import sys
from typing import Any, Dict, List, Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class Mark(Protocol):
    def mark(self) -> str: ...


class Bang:
    def mark(self) -> str:
        return "!"


class Dot:
    def mark(self) -> str:
        return "."


class English:
    def __init__(self, mark: Mark) -> None:
        self._mark = mark

    def greet(self) -> str:
        return "hello" + self._mark.mark()


class French:
    def __init__(self, mark: Mark) -> None:
        self._mark = mark

    def greet(self) -> str:
        return "bonjour" + self._mark.mark()


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


class Note:
    pass


NAMES: Dict[str, str] = {}
WATCH: List[str] = []


def nm(value: Any) -> str:
    return NAMES.get(value, str(value)[:8]) if isinstance(value, str) else repr(value)


def attempt(step: str, call: Any) -> Any:
    try:
        result = call()
        print(f"  {step}: {result!r}")
        return result
    except Exception as error:
        text = " | ".join(str(error).splitlines())
        for key, name in NAMES.items():
            text = text.replace(key, name)
        print(f"  {step}: {type(error).__name__}: {text[:260]}")
        return None


def registry(states: Any, title: str) -> None:
    print(f"  -- registry objects (SpellSystemStates, one per frame): {title}")
    for index_id in WATCH:
        state = states._states_by_index_id.get(index_id)
        if state is None:
            print(f"     state[{nm(index_id)}]: none")
            continue
        print(f"     state[{nm(index_id)}]: version={nm(state.current_spell_id)} validity={state.validity.name} "
              f"flags={sorted(flag.name for flag in state.flags)}")
        print(f"        direct_dependencies={sorted(nm(d) for d in state.direct_dependencies)} "
              f"direct_dependents={sorted(nm(d) for d in state.direct_dependents)}")
        print(f"        _binding_key_by_index[{nm(index_id)}]={states._binding_key_by_index.get(index_id)}")
    for book_id, by_key in states._contract_dependents_by_spellbook.items():
        for key, users in by_key.items():
            print(f"     _contract_dependents_by_spellbook[{nm(book_id)}][{key}]={sorted(nm(u) for u in users)}")


def contract_rows(holder: Any, peer: Any, title: str) -> None:
    contract = holder._conduit_ward._find_contract_by_id(peer._id)
    print(f"  -- Contract between {nm(holder._id)} and {nm(peer._id)}: {title}")
    if contract is None:
        print("     no contract")
        return
    for ward in (contract._ward_a, contract._ward_b):
        side = nm(ward._conduit._id)
        for spell_id, row in contract._get_detail_map(ward).items():
            print(f"     Detail under {side}: spell_id={nm(spell_id)} spell_index={nm(row.spell_index.id)} "
                  f"permissions={row.permissions.name} type={row.contract_type.name} reason={row.reason.name} "
                  f"sources={sorted(nm(s) for s in row.sources)}")
        for index_id, row in contract._get_index_detail_map(ward).items():
            print(f"     IndexDetail under {side}: index={nm(index_id)} selected_spell_id={nm(row.selected_spell_id)} "
                  f"permissions={row.permissions.name} type={row.contract_type.name} reason={row.reason.name}")


def copies(book: Any, peer: Any, title: str) -> None:
    peer_id = peer._id
    print(f"  -- {nm(book._id)} copies borrowed from {nm(peer_id)}: {title}")
    active = book._contracted_spells.get(peer_id) or {}
    print(f"     _contracted_spells (index -> active copy)={[(nm(i.id), nm(s.spell_id)) for i, s in active.items()]}")
    print(f"     _contracted_spells_by_id={sorted(nm(x) for x in (book._contracted_spells_by_id.get(peer_id) or {}))}")
    lookup = book._lookup_contracted_spells.get(peer_id) or {}
    print(f"     _lookup_contracted_spells (key -> index)={[(k, nm(i.id)) for k, i in lookup.items()]}")
    print(f"     _inactive_contracted_spells (parked)={sorted(nm(x) for x in (book._inactive_contracted_spells.get(peer_id) or {}))}")
    print(f"     _contracted_spell_ids={sorted(nm(x) for x in (book._contracted_spell_ids.get(peer_id) or set()))}")


def owned(book: Any, title: str) -> None:
    print(f"  -- {nm(book._id)} owned maps: {title}")
    print(f"     _spells (index -> active)={[(nm(i.id), nm(s.spell_id)) for i, s in book._spells.items()]}")
    print(f"     _spells_by_id={sorted(nm(x) for x in book._spells_by_id)} "
          f"_inactive_spells={sorted(nm(x) for x in book._inactive_spells)} _spell_ids={sorted(nm(x) for x in book._spell_ids)}")


def base_world(tag: str, extra_books: int) -> Any:
    books = [md.Spellbook() for _ in range(2 + extra_books)]
    lender_book, borrower_book = books[0], books[1]
    bang = lender_book.bind(spell=Bang, spellframe=Mark, binding_name="mark", existence="many", permissions="create")
    english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                               permissions="create")
    banner = borrower_book.bind(spell=Banner, existence="many", permissions="create")
    for number, extra in enumerate(books[2:]):
        extra.bind(spell=Note, binding_name=f"note_{number}", existence="many", permissions="create")
    names = ["lender", "borrower", "steward", "borrower2"]
    conduits = [book.conjure(dynamic=True, name=f"{names[i]}_{tag}") for i, book in enumerate(books)]
    for i, book in enumerate(books):
        NAMES[book._id] = f"{names[i]}_book"
        NAMES[conduits[i]._id] = names[i]
    NAMES.update({bang: "Bang", english: "English", banner: "Banner"})
    lender = conduits[0]
    mark_index = lender.get_spell_by_id(bang).spell_index
    greeter_index = lender.get_spell_by_id(english).spell_index
    banner_index = conduits[1].get_spell_by_id(banner).spell_index
    NAMES.update({mark_index.id: "Mark-index", greeter_index.id: "Greeter-index", banner_index.id: "Banner-index"})
    WATCH[:] = [mark_index.id, greeter_index.id, banner_index.id]
    return books, conduits, (bang, english, banner), (mark_index, greeter_index)


def mode_contract() -> None:
    books, conduits, ids, indexes = base_world("c", 2)
    lender, borrower, _steward, borrower2 = conduits
    english = ids[1]
    mark_index, greeter_index = indexes
    french = lender.bind_inactive(spell=French, spell_index=greeter_index, spellframe=Greeter, binding_name="greeter",
                                  existence="many", permissions="create")
    NAMES[french] = "French"
    lender.link(borrower)
    lender.link(borrower2)
    borrower.add_index_to_contract(index=greeter_index, conduit=lender, permissions="create")
    borrower.add_index_to_contract(index=mark_index, conduit=lender, permissions="create")
    with borrower2.transaction("link", conduits=[borrower2, lender]):
        borrower2.add_spell_to_contract(spell_id=english, conduit=lender, permissions="create")
    attempt("Banner", lambda: borrower.meld(spell=Banner).text)
    for title in ("before the notch", "after the lender notches Greeter-index to French"):
        if title.startswith("after"):
            lender.notch_spell(spell_index=greeter_index, spell_id=french)
            attempt("Banner", lambda: borrower.meld(spell=Banner).text)
        print(f"== {title}")
        contract_rows(borrower, lender, "index links (Greeter-index, Mark-index)")
        copies(books[1], lender, "")
        contract_rows(borrower2, lender, "one version grant (English)")
        copies(books[3], lender, "")


def mode_lookup() -> None:
    books, conduits, ids, indexes = base_world("l", 0)
    lender, borrower = conduits
    lender_book = books[0]
    mark_index, greeter_index = indexes
    french = lender.bind_inactive(spell=French, spell_index=greeter_index, spellframe=Greeter, binding_name="greeter",
                                  existence="many", permissions="create")
    NAMES[french] = "French"
    owned(lender_book, "English active, French parked on Greeter-index")
    attempt("lender_book.find_spell_by_id(French)", lambda: nm(lender_book.find_spell_by_id(french).spell_id))
    attempt("lender.get_spell_by_id(French)", lambda: nm(lender.get_spell_by_id(french).spell_id))
    attempt("lender_book._get_owned_spell(French)", lambda: nm(lender_book._get_owned_spell(french).spell_id))
    lender.link(borrower)
    borrower.add_index_to_contract(index=mark_index, conduit=lender, permissions="create")

    def grant(**kwargs: Any) -> Any:
        with borrower.transaction("link", conduits=[borrower, lender]):
            return borrower.add_spell_to_contract(conduit=lender, permissions="create", **kwargs)

    attempt("borrower.add_spell_to_contract(spell_id=French)", lambda: grant(spell_id=french))
    attempt("borrower.add_spell_to_contract(spell=<French Spell object>)",
            lambda: grant(spell=lender_book._inactive_spells[french]))
    copies(books[1], lender, "after granting the parked French")
    attempt("Banner (French is parked)", lambda: borrower.meld(spell=Banner).text)
    lender.notch_spell(spell_index=greeter_index, spell_id=french)
    copies(books[1], lender, "after the lender notches to French")
    attempt("Banner", lambda: borrower.meld(spell=Banner).text)


def mode_registry(transfer: bool) -> None:
    books, conduits, ids, indexes = base_world("t" if transfer else "n", 1)
    lender, borrower, steward = conduits
    english = ids[1]
    mark_index, greeter_index = indexes
    states = books[0]._spell_system_states
    dot = lender.bind_inactive(spell=Dot, spell_index=mark_index, spellframe=Mark, binding_name="mark",
                               existence="many", permissions="create")
    NAMES[dot] = "Dot"
    lender.link(borrower)
    borrower.add_index_to_contract(index=greeter_index, conduit=lender, permissions="create")
    borrower.add_index_to_contract(index=mark_index, conduit=lender, permissions="create")
    attempt("Banner", lambda: borrower.meld(spell=Banner).text)
    registry(states, "after Banner's first meld")
    if transfer:
        result = attempt("lender.transfer_spell_ownership(spell=English, target_conduit=steward) borrowers",
                         lambda: lender.transfer_spell_ownership(spell=english, target_conduit=steward)["borrowers"])
        registry(states, "after the transfer")
        contract_rows(borrower, lender, "after the transfer")
        copies(books[1], lender, "after the transfer")
        owned(books[0], "after the transfer")
        owned(books[2], "after the transfer")
        attempt("Banner", lambda: borrower.meld(spell=Banner).text)
        attempt("steward.bind_inactive(French) on Greeter-index",
                lambda: steward.bind_inactive(spell=French, spell_index=greeter_index, spellframe=Greeter,
                                              binding_name="greeter", existence="many", permissions="create"))
    lender.notch_spell(spell_index=mark_index, spell_id=dot)
    registry(states, "after the lender notches Mark-index from Bang to Dot")
    attempt("Banner", lambda: borrower.meld(spell=Banner).text)
    registry(states, "after Banner's meld")


def mode_trace() -> None:
    books, conduits, ids, indexes = base_world("r", 0)
    lender, borrower = conduits
    lender_book = books[0]
    greeter_index = indexes[1]
    french = lender.bind_inactive(spell=French, spell_index=greeter_index, spellframe=Greeter, binding_name="greeter",
                                  existence="many", permissions="create")
    NAMES[french] = "French"
    frame = lender_book._aether._aetheric_frames[lender_book._aetheric_frame_name]
    print("hop 1 - Aether asks the frame which conduit owns the id: frame._spell_registry (conduit -> its SpellIndexes)")
    for conduit_id, index_set in frame._spell_registry.items():
        print(f"     {nm(conduit_id)}: {sorted(nm(i.id) for i in index_set)}")
    print(f"     Greeter-index members (_spells_in_index)={sorted(nm(s) for s in greeter_index._spells_in_index)} "
          f"selected_spell_id={nm(greeter_index.selected_spell_id)}")
    print(f"     frame.find_conduit_id_for_spell(French) -> {nm(frame.find_conduit_id_for_spell(french))}")
    print("hop 2 - the owner Book's find_spell_by_id(French), line by line")
    print(f"     _spells_by_id (active versions by id) = {sorted(nm(x) for x in lender_book._spells_by_id)}")
    print(f"     _spells_by_id.get(French) -> {lender_book._spells_by_id.get(french)}")
    parked = lender_book._inactive_spells.get(french)
    print(f"     _inactive_spells (parked versions by id) = {sorted(nm(x) for x in lender_book._inactive_spells)}")
    print(f"     _inactive_spells.get(French) -> the Spell whose spell_id is {nm(parked.spell_id)}")
    print(f"     that Spell's spell_index -> {nm(parked.spell_index.id)}")
    print(f"     _spells (each index -> its ACTIVE Spell) = {[(nm(i.id), nm(s.spell_id)) for i, s in lender_book._spells.items()]}")
    print(f"     _spells.get(Greeter-index) -> the Spell whose spell_id is {nm(lender_book._spells.get(parked.spell_index).spell_id)}")
    print(f"     find_spell_by_id(French) returns the Spell whose spell_id is {nm(lender_book.find_spell_by_id(french).spell_id)}")
    print(f"hop 3 - the grant compares: asked {nm(french)}, got {nm(borrower.get_spell_by_id(french).spell_id)} -> refuses")
    print(f"     _get_owned_spell(French) returns the Spell whose spell_id is {nm(lender_book._get_owned_spell(french).spell_id)}")


CHOICE = sys.argv[1] if len(sys.argv) > 1 else "contract"
print(f"== mode {CHOICE}; melder {md.__version__}; gil_enabled={sys._is_gil_enabled()}")
if CHOICE == "contract":
    mode_contract()
elif CHOICE == "lookup":
    mode_lookup()
elif CHOICE == "trace":
    mode_trace()
else:
    mode_registry(CHOICE == "transfer")
