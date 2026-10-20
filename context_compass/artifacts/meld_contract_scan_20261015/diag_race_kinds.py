"""Classify the meld-vs-notch race's unexpected exceptions on one tree, with the first traceback and timeline of each.

Each run is the integration race (four threads meld the borrower's SpellContract consumer while the lender notches its
provider 20 times, A, B, A, ...). Wrappers timestamp the consumer's target passes (done with or without a plan, or
raised), the borrower Book's contracted-map mutations and every CreationContext build of the consumer. The first
occurrence of each kind (exception type plus its message up to the first quote) prints its traceback and the 14
events before it, each with the thread that recorded it. The wrappers take a lock and append per event, so they
perturb the timing; the rates come from probe_rule2_race_rate.py, not from this script (melder_1).

usage: python -X gil=0|1 <this script> <tree root> <max runs> <time budget seconds>
"""
import collections
import sys
import threading
import time
import traceback

TREE = sys.argv[1]
MAX_RUNS = int(sys.argv[2])
BUDGET = float(sys.argv[3])
sys.path[:0] = [f"{TREE}/src", TREE]

from tests.integration.melder.conduit import test_conduit_integration_notch_revalidation as t  # noqa: E402
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.conduit.meld.creation_context.creation_context_builder import CreationContextBuilder  # noqa: E402
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError  # noqa: E402

EVENTS: list = []
EVENT_LOCK = threading.Lock()
STATE = {"borrower_book": None, "names": {}}


def note(kind: str, detail: str) -> None:
    """Append one timestamped event with the recording thread's name."""
    with EVENT_LOCK:
        EVENTS.append((time.perf_counter(), threading.current_thread().name, kind, detail))


def short(spell_id: str) -> str:
    """Name a provider version by its letter when it is one, else its first 12 characters."""
    return STATE["names"].get(spell_id, spell_id[:12])


ORIGINAL_PASS = Spellbook._run_resolution_phases_for_target_spell


def wrapped_pass(self, conduit_id, spell):
    """Record a target pass of the consumer: done (plan or none) or raised."""
    try:
        result = ORIGINAL_PASS(self, conduit_id, spell)
    except BaseException as exc:
        note("pass-raised", f"{spell.spell_name} {type(exc).__name__}")
        raise
    plan = spell._compiler_artifact._spell_codegen_creation is not None
    note("pass-done", f"{spell.spell_name} plan={plan}")
    return result


Spellbook._run_resolution_phases_for_target_spell = wrapped_pass


def wrap_mutator(name: str) -> None:
    """Record a contracted-map mutation of the borrower Book; spell or spell id is in the arguments."""
    original = getattr(Spellbook, name)

    def wrapper(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        if self is STATE["borrower_book"]:
            target = next((a for a in args if hasattr(a, "spell_id")), None)
            label = short(target.spell_id) if target is not None else short(str(args[0]))
            note(name.strip("_").replace("_contracted_spell", ""), label)
        return result

    setattr(Spellbook, name, wrapper)


for mutator in ("_deactivate_contracted_spell", "_reactivate_contracted_spell", "_add_contracted_spell",
                "_remove_contracted_spell"):
    wrap_mutator(mutator)

ORIGINAL_BUILD = CreationContextBuilder.__dict__["build"].__func__


def wrapped_build(spell, **kwargs):
    """Record a CreationContext build of the consumer: ok or raised."""
    try:
        result = ORIGINAL_BUILD(spell, **kwargs)
    except BaseException as exc:
        note("ctx-raised", f"{spell.spell_name} {type(exc).__name__}")
        raise
    note("ctx-built", spell.spell_name)
    return result


CreationContextBuilder.build = staticmethod(wrapped_build)


def kind_of(exc: BaseException) -> str:
    """The exception type plus its message up to the first quote (ids and names left out)."""
    return f"{type(exc).__name__}: {str(exc).split(chr(39))[0][:80]}"


def one_run(run: int, seen: set, kinds: collections.Counter) -> int:
    """Run the race once; print the first occurrence of each new kind; return the unexpected count."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    with EVENT_LOCK:
        EVENTS.clear()
    world = t._lend("race", t.ImplA)
    STATE["borrower_book"] = world.borrower_book
    STATE["names"] = {world.provider_id: "A"}
    stop = threading.Event()
    failures: list = []

    def loop() -> None:
        while not stop.is_set():
            try:
                world.meld_ping()
            except SpellbookValidationError:
                note("meld-refused", "SVE")
            except BaseException as exc:
                note("meld-raised", kind_of(exc))
                with EVENT_LOCK:
                    failures.append((exc, len(EVENTS)))
                return

    threads = [threading.Thread(target=loop, name=f"meld{i}") for i in range(4)]
    world.meld_ping()
    for thread in threads:
        thread.start()
    b_id = world.notch_to(t.ImplB)
    STATE["names"][b_id] = "B"
    note("notched", "B")
    for version_id in ([b_id, world.provider_id] * 10)[1:]:
        world.notch_back(version_id)
        note("notched", short(version_id))
    stop.set()
    for thread in threads:
        thread.join(60)
    world.cleanup()
    with EVENT_LOCK:
        snapshot = list(EVENTS)
    for exc, upto in failures:
        kind = kind_of(exc)
        kinds[kind] += 1
        if kind in seen:
            continue
        seen.add(kind)
        start = snapshot[0][0]
        print(f"--- first {kind} (run {run}) ---")
        for stamp, thread_name, event, detail in snapshot[max(0, upto - 15):upto]:
            print(f"  {(stamp - start) * 1e3:8.3f} ms {thread_name:10s} {event:12s} {detail}")
        message = str(exc)
        for spell_id, letter in STATE["names"].items():
            message = message.replace(spell_id, f"<{letter}>")
        print(f"  message: {message[:200]}")
        frames = traceback.format_exception(exc)
        print("".join(frames)[-2400:])
    return len(failures)


print(f"tree={TREE} gil_enabled={sys._is_gil_enabled()} max_runs={MAX_RUNS} budget={BUDGET}s")
began = time.perf_counter()
seen: set = set()
kinds: collections.Counter = collections.Counter()
bad = 0
runs = 0
while runs < MAX_RUNS and time.perf_counter() - began < BUDGET:
    runs += 1
    if one_run(runs, seen, kinds):
        bad += 1
print(f"runs={runs} runs_with_unexpected={bad} seconds={time.perf_counter() - began:.1f}")
for kind, count in kinds.most_common():
    print(f"  {count} x {kind}")
