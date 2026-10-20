"""Verify the 0.2.8250 release-note examples as written, and measure the first (melder_1, 2026-10-16).

usage: PYTHONPATH=<tree>/src python <this script>   (run from a scratch directory, never inside the repository)
The two blocks between the BEGIN/END markers are the note's code, verbatim. After the first block the script times
warm melds of the contract consumer, then severs the link and prints the error the next meld raises (a sever, not
`remove_index_from_contract`: with a parked member in the index the latter can raise RuntimeError before 0.2.8250
and after it - probe_index_uncontract_after_notch.py). Prints the Melder version it ran against. The observations on the tree before 0.2.8250 come from
release_example_rule2_before_2026_10_16.py, which runs the same steps without the note's asserts.
"""
import time
from typing import Protocol

import melder as md

# BEGIN NOTE BLOCK 1
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


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender.get_spell_by_id(english).spell_index
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "HELLO"

french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
lender.notch_spell(spell_index=index, spell_id=french)
assert borrower.meld(spell=Banner).text == "BONJOUR"   # rebuilt once, at this meld
# END NOTE BLOCK 1

N = 20_000
for _ in range(2_000):
    borrower.meld(spell=Banner)
best = None
for _ in range(5):
    start = time.perf_counter_ns()
    for _ in range(N):
        borrower.meld(spell=Banner)
    per = (time.perf_counter_ns() - start) / N / 1000.0
    best = per if best is None or per < best else best
print(f"melder {md.__version__}: warm meld of Banner, best of 5 x {N}: {best:.2f} us")

lender.sever_link(borrower)
try:
    banner = borrower.meld(spell=Banner)
    print(f"after sever_link: built {banner.text!r}")
except Exception as error:
    print(f"after sever_link: {type(error).__name__}: {error}")

# BEGIN NOTE BLOCK 2
class Clock(Protocol):
    def now(self) -> str: ...


class Utc:
    def now(self) -> str:
        return "utc"


class Local:
    def now(self) -> str:
        return "local"


class Stamp:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock


class Report:
    def __init__(self, stamp: Stamp) -> None:
        self.stamp = stamp


book = md.Spellbook()
utc = book.bind(spell=Utc, spellframe=Clock, binding_name="clock", existence="many")
book.bind(spell=Stamp, existence="many")
book.bind(spell=Report, existence="many")
reports = book.conjure(dynamic=True, name="reports")
assert reports.meld(spell=Report).stamp.clock.now() == "utc"

clock_index = reports.get_spell_by_id(utc).spell_index
local = reports.bind_inactive(spell=Local, spell_index=clock_index, spellframe=Clock, binding_name="clock",
                              existence="many")
reports.notch_spell(spell_index=clock_index, spell_id=local)
assert reports.meld(spell=Report).stamp.clock.now() == "local"   # "utc" before 0.2.8250
# END NOTE BLOCK 2

print("release examples OK")
