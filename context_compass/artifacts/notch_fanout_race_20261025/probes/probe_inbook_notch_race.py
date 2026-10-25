"""Measure the in-Book variant of the meld-vs-notch race on one tree (melder_0, 2026-10-25).

TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout asks whether a notch inside ONE Book races a
dependent's in-flight meld the way a lender's notch races a borrower's. Each run: a fresh Aether, the integration
file's one-Book chain (`_chain`: QChain -> PChain -> IDep, all `many`, caching off, dynamic), DepB staged on IDep's
index; four threads meld QChain and read `p.dep.tag()` while the main thread notches the index 20 times between
DepA ("d1") and DepB ("d2"), ending on DepA. Per run it counts the melds that returned each version, the clean
refusals (SpellbookValidationError) and any other exception that ended a thread, and the version the first meld
after the race returns (the last notch selects DepA, so "d1").

usage: python -X gil=0|1 <this script> <tree root> <runs>
"""
import collections
import sys
import threading
import time
from typing import Any, Dict, List, Tuple


def load(tree: str) -> Dict[str, Any]:
    """Put the tree first on sys.path and import what a run needs from it."""
    sys.path[:0] = [f"{tree}/src", tree]
    from tests.integration.melder.conduit import test_conduit_integration_notch_revalidation as t
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
    return {"t": t, "Aether": Aether, "Conduit": Conduit, "Existence": Existence, "Spellbook": Spellbook,
            "SVE": SpellbookValidationError}


def fresh(m: Dict[str, Any]) -> None:
    """Give the run a fresh Aether, as the integration file's autouse fixture does."""
    m["Aether"]._reset_singleton_for_tests()
    aether = m["Aether"]()
    m["Spellbook"]._aether = aether
    m["Conduit"]._aether = aether


def one_run(m: Dict[str, Any], run: int) -> Tuple[collections.Counter, List[str], str, float]:
    """Run the in-Book race once; return (counts, unexpected messages, final tag, seconds)."""
    t = m["t"]
    fresh(m)
    started = time.perf_counter()
    book, root, index, _p_cls, q_cls = t._chain(f"inbook{run}")
    dep_a_id = index.selected_spell_id
    dep_b_id = root.bind_inactive(spell=t.DepB, spell_index=index, spellframe=t.IDep, binding_name="dep",
                                  existence=m["Existence"].many, permissions="create")
    stop = threading.Event()
    counts: collections.Counter = collections.Counter()
    unexpected: List[str] = []
    lock = threading.Lock()

    def loop() -> None:
        while not stop.is_set():
            try:
                tag = root.meld(spell=q_cls).p.dep.tag()
                with lock:
                    counts[tag] += 1
            except m["SVE"]:
                with lock:
                    counts["refused"] += 1
            except Exception as error:  # every other kind is what this probe measures
                with lock:
                    unexpected.append(f"{type(error).__name__}: {str(error)[:90]}")
                return

    threads = [threading.Thread(target=loop, name=f"meld{i}") for i in range(4)]
    try:
        for thread in threads:
            thread.start()
        for step in range(20):
            root.notch_spell(spell_index=index, spell_id=dep_b_id if step % 2 == 0 else dep_a_id)
        stop.set()
        for thread in threads:
            thread.join()
        final = root.meld(spell=q_cls).p.dep.tag()
    finally:
        stop.set()
        root.cleanup()
    return counts, unexpected, final, time.perf_counter() - started


def main() -> None:
    tree, runs = sys.argv[1], int(sys.argv[2])
    m = load(tree)
    print(f"tree={tree} runs={runs} gil_enabled={sys._is_gil_enabled()}")
    total: collections.Counter = collections.Counter()
    finals: collections.Counter = collections.Counter()
    kinds: collections.Counter = collections.Counter()
    runs_with_unexpected = 0
    for run in range(1, runs + 1):
        counts, unexpected, final, seconds = one_run(m, run)
        total.update(counts)
        finals[final] += 1
        kinds.update(unexpected)
        runs_with_unexpected += 1 if unexpected else 0
        print(f"run {run:3d}: {dict(counts)} unexpected={len(unexpected)} final={final} {seconds:.2f}s")
    print(f"runs with an unexpected exception: {runs_with_unexpected} of {runs}")
    for kind, count in kinds.most_common():
        print(f"  {count} x {kind}")
    print(f"melds: {dict(total)}")
    print(f"first meld after the race: {dict(finals)}")


if __name__ == "__main__":
    main()
