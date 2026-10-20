"""Verify the 0.2.8247 release-note example and measure it (melder_1, 2026-10-16).

usage: PYTHONPATH=<tree>/src python <this script>   (run from a scratch directory, never inside the repository)
Runs the example as written in the note, then times warm melds of the override consumer, and checks that a meld
of the definition itself is still refused with the same error. Prints the Melder version it ran against.
"""
import time
from typing import Protocol

import melder as md


class Clock(Protocol):
    def now(self) -> float: ...


class Report:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock


class SystemClock:
    def now(self) -> float:
        return time.time()


time_source = SystemClock()

book = md.Spellbook()
book.bind(spell=Clock, existence="unique", resolvable=False)   # discoverable, never resolved
book.bind(spell=Report, existence="many")
root = book.conjure()

report = root.meld(spell=Report, override={"clock": time_source})
assert report.clock is time_source

N = 50_000
for _ in range(2_000):
    root.meld(spell=Report, override={"clock": time_source})
best = None
for _ in range(5):
    start = time.perf_counter_ns()
    for _ in range(N):
        root.meld(spell=Report, override={"clock": time_source})
    per = (time.perf_counter_ns() - start) / N / 1000.0
    best = per if best is None or per < best else best

try:
    root.meld(spell=Clock)
    refused = "NOT REFUSED"
except md.MeldExecutionError as error:
    refused = type(error).__name__ + ": " + str(error).splitlines()[0][:110]

print(f"melder {md.__version__}: warm override meld best of 5 x {N}: {best:.2f} us")
print(f"meld(Clock): {refused}")
root.cleanup()
