"""Diagnose: run the race until an unexpected exception of the wanted kind appears; print its traceback."""
import sys, threading, traceback
TREE = sys.argv[1]; WANT = sys.argv[2]; MAXRUNS = int(sys.argv[3])
sys.path[:0] = [f"{TREE}/src", TREE]
from tests.integration.melder.conduit import test_conduit_integration_notch_revalidation as t
from melder.aether.aether import Aether
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.conduit import Conduit
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError

for run in range(MAXRUNS):
    Aether._reset_singleton_for_tests(); a = Aether(); Spellbook._aether = a; Conduit._aether = a
    world = t._lend("race", t.ImplA)
    stop = threading.Event(); found = []
    def loop():
        while not stop.is_set():
            try:
                world.meld_ping()
            except SpellbookValidationError:
                continue
            except BaseException as exc:
                if type(exc).__name__ == WANT:
                    found.append("".join(traceback.format_exception(exc)))
                return
    ths = [threading.Thread(target=loop) for _ in range(4)]
    world.meld_ping()
    for th in ths: th.start()
    b = world.notch_to(t.ImplB)
    for v in ([b, world.provider_id] * 10)[1:]:
        world.notch_back(v)
    stop.set()
    for th in ths: th.join(60)
    world.cleanup()
    if found:
        print(f"run {run}:")
        print(found[0][-6000:])
        break
else:
    print("not found")
