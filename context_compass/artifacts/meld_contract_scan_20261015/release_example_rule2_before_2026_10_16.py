"""Run the 0.2.8250 release-note scenarios without their asserts and print what happens (melder_1, 2026-10-16).

usage: PYTHONPATH=<tree>/src python <this script>   (run from a scratch directory, never inside the repository)
For the tree before 0.2.8250 (and, as a control, after it): the same steps as release_example_rule2_2026_10_16.py,
each result printed instead of asserted, and the warm meld of the contract consumer timed the same way.
"""
import time
from typing import Protocol

import melder as md


def attempt(label, call):
    try:
        print(f"{label}: {call()!r}")
    except Exception as error:
        print(f"{label}: {type(error).__name__}: {' | '.join(str(error).splitlines())[:600]}")


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
attempt("Banner before the notch", lambda: borrower.meld(spell=Banner).text)

french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
lender.notch_spell(spell_index=index, spell_id=french)
attempt("Banner after the notch", lambda: borrower.meld(spell=Banner).text)

N = 2_000
for _ in range(200):
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
attempt("Banner after sever_link", lambda: borrower.meld(spell=Banner).text)


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
attempt("Report before the notch", lambda: reports.meld(spell=Report).stamp.clock.now())

clock_index = reports.get_spell_by_id(utc).spell_index
local = reports.bind_inactive(spell=Local, spell_index=clock_index, spellframe=Clock, binding_name="clock",
                              existence="many")
reports.notch_spell(spell_index=clock_index, spell_id=local)
attempt("Report after the notch", lambda: reports.meld(spell=Report).stamp.clock.now())
attempt("Report again", lambda: reports.meld(spell=Report).stamp.clock.now())
