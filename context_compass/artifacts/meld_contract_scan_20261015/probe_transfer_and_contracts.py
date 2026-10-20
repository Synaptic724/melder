"""Probe: how an ownership transfer meets contracts (melder_1, 2026-10-16; for the owner's question).

usage: PYTHONPATH=<tree>/src python <this script> t1|t2|t3|t4a|t4b   (from a scratch directory; one world per
process, because process-wide spell ids refuse the same classes bound twice in a frame)
T1/T2: the lender owns the Greeter index (English) and the borrower index-links it; Banner holds a SpellContract on
it. The lender transfers the lineage to a third root, `steward` (T1 force_unshare=True, the default; T2
force_unshare=False, repoint). Then the steward stages French and notches to it, and finally the borrower unlinks.
T3: the CONSUMER moves - the borrower transfers Banner to a root that borrows nothing.
T4a/T4b: as T1/T2 with a version grant (add_spell_to_contract) instead of the index link.
Each step prints the borrower's copies per peer, which contracts link the index or grant a version, and Banner's meld.
"""
from typing import Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


NAMES = {}


def label(text):
    for spell_id, name in NAMES.items():
        text = text.replace(spell_id, name)
    return text


def attempt(step, call):
    try:
        result = call()
        print(f"  {step}: {result!r}")
    except Exception as error:
        print(f"  {step}: {type(error).__name__}: {label(' | '.join(str(error).splitlines()))[:230]}")


def copies(book, conduit):
    cid = conduit._id
    active = sorted(NAMES.get(s, s[:8]) for s in book._contracted_spells_by_id.get(cid, {}))
    parked = sorted(NAMES.get(s, s[:8]) for s in book._inactive_contracted_spells.get(cid, {}))
    return f"active={active} parked={parked}"


def links(borrower, peer, index, ids):
    contract = borrower._conduit_ward._find_contract_by_id(peer._id)
    if contract is None:
        return "no contract"
    peer_ward = peer._conduit_ward
    index_link = contract._check_index_exists(peer_ward, index.id)
    details = sorted(NAMES[s] for s in ids if contract._check_if_exists(peer_ward, s))
    return f"index link={index_link} spell details={details}"


def show(step, borrower_book, borrower, peers, index, ids):
    print(f"{step}:")
    for peer in peers:
        print(f"    from {peer._name}: {copies(borrower_book, peer)}; {links(borrower, peer, index, ids)}")


def world(tag, force_unshare, grant=False):
    kind = "a version grant" if grant else "an index link"
    print(f"== {tag}: the borrower holds {kind}; the lender transfers the provider to steward "
          f"(force_unshare={force_unshare})")
    lender_book, borrower_book, steward_book = md.Spellbook(), md.Spellbook(), md.Spellbook()
    english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                               permissions="create")
    NAMES[english] = "English"
    borrower_book.bind(spell=Banner, existence="many", permissions="create")
    lender = lender_book.conjure(dynamic=True, name=f"lender_{tag}")
    borrower = borrower_book.conjure(dynamic=True, name=f"borrower_{tag}")
    steward = steward_book.conjure(dynamic=True, name=f"steward_{tag}")
    lender.link(borrower)
    index = lender.get_spell_by_id(english).spell_index
    if grant:
        with borrower.transaction("link", conduits=[borrower, lender]):
            borrower.add_spell_to_contract(spell_id=english, conduit=lender, permissions="create")
    else:
        borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    ids = [english]
    attempt("Banner before the transfer", lambda: borrower.meld(spell=Banner).text)
    show("before the transfer", borrower_book, borrower, [lender, steward], index, ids)
    attempt("transfer_spell_ownership",
            lambda: sorted(lender.transfer_spell_ownership(spell=english, target_conduit=steward,
                                                           force_unshare=force_unshare)["borrowers"][0].items()))
    show("after the transfer", borrower_book, borrower, [lender, steward], index, ids)
    states = steward_book._spell_system_states
    print(f"  owner Book ids: English in steward._spell_ids={english in steward_book._spell_ids}, "
          f"in lender._spell_ids={english in lender_book._spell_ids}; "
          f"registry binding key={states._binding_key_by_index.get(index)}")
    attempt("Banner after the transfer", lambda: borrower.meld(spell=Banner).text)
    attempt("steward meld English", lambda: type(steward.meld(spell_id=english)).__name__)
    french_holder = []

    def stage():
        french_holder.append(steward.bind_inactive(spell=French, spell_index=index, spellframe=Greeter,
                                                   binding_name="greeter", existence="many", permissions="create"))
        return "staged"

    attempt("steward bind_inactive(French) on the transferred index", stage)
    if not french_holder:
        print("  (the steward cannot stage on the index; the rest of the world is skipped)")
        return
    french = french_holder[0]
    NAMES[french] = "French"
    ids.append(french)
    attempt("steward notch to French", lambda: steward.notch_spell(spell_index=index, spell_id=french))
    show("after the steward notches to French", borrower_book, borrower, [lender, steward], index, ids)
    attempt("Banner after the notch", lambda: borrower.meld(spell=Banner).text)
    attempt("borrower unlinks the index from the lender",
            lambda: borrower.remove_index_from_contract(index_id=index.id, conduit=lender))
    show("after the unlink", borrower_book, borrower, [lender, steward], index, ids)


def consumer_moves():
    print("== T3: the borrower transfers the consumer (Banner) to a root that borrows nothing")
    lender_book, borrower_book, other_book = md.Spellbook(), md.Spellbook(), md.Spellbook()
    english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                               permissions="create")
    NAMES[english] = "English"
    banner = borrower_book.bind(spell=Banner, existence="many", permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender_t3")
    borrower = borrower_book.conjure(dynamic=True, name="borrower_t3")
    other = other_book.conjure(dynamic=True, name="other_t3")
    lender.link(borrower)
    index = lender.get_spell_by_id(english).spell_index
    borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    attempt("Banner on the borrower", lambda: borrower.meld(spell=Banner).text)
    attempt("transfer Banner to other", lambda: sorted(
        borrower.transfer_spell_ownership(spell=banner, target_conduit=other).keys()))
    attempt("Banner on other", lambda: other.meld(spell=Banner).text)
    attempt("Banner on the borrower", lambda: borrower.meld(spell=Banner).text)


import sys

CHOICE = sys.argv[1] if len(sys.argv) > 1 else "t1"
if CHOICE == "t1":
    world("t1", True)
elif CHOICE == "t2":
    world("t2", False)
elif CHOICE == "t4a":
    world("t4a", True, grant=True)
elif CHOICE == "t4b":
    world("t4b", False, grant=True)
else:
    consumer_moves()
print(f"melder {md.__version__}")
