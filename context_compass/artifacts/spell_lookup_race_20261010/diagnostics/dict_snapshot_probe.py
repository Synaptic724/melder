"""
Which one-call dict snapshots stay consistent under concurrent writers (melder_1, 2026-10-10). Measurement only.

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

Writer threads insert and pop keys of a shared dict whose keys hash in Python (like SpellIndex); reader threads
take a snapshot in each of four ways and walk it, for a fixed number of reads. Counted per way: RuntimeErrors
raised while taking or walking the snapshot, snapshots that miss the one key no writer ever touches, and the time
per snapshot. All threads start on one Barrier.
"""

import sys
import threading
import time
from typing import Callable, Dict, List


class Key:
    """A key with a Python-level __hash__/__eq__, as SpellIndex has."""

    def __init__(self, ident: int) -> None:
        self.ident = ident

    def __hash__(self) -> int:
        return hash(self.ident)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Key) and other.ident == self.ident


def main() -> int:
    """Run each way with 2 writers and 2 readers and print the counts."""
    ways: Dict[str, Callable[[dict], list]] = {
        "live for-loop": lambda d: [k for k, _ in d.items()],
        "dict.copy()": lambda d: [k for k, _ in d.copy().items()],
        "list(d.items())": lambda d: [k for k, _ in list(d.items())],
        "tuple(d.items())": lambda d: [k for k, _ in tuple(d.items())],
    }
    reads = 200_000
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} reads_per_reader={reads}")
    for name, way in ways.items():
        stable = Key(-1)
        shared: dict = {stable: "stable"}
        stop = threading.Event()
        barrier = threading.Barrier(4)
        errors: List[int] = [0, 0]
        misses: List[int] = [0, 0]
        seconds: List[float] = [0.0, 0.0]

        def writer(base: int) -> None:
            barrier.wait()
            n = 0
            while not stop.is_set():
                key = Key(base + n % 64)
                shared[key] = n
                shared.pop(key, None)
                n += 1

        def reader(slot: int) -> None:
            barrier.wait()
            started = time.perf_counter()
            for _ in range(reads):
                try:
                    if stable not in way(shared):
                        misses[slot] += 1
                except RuntimeError:
                    errors[slot] += 1
            seconds[slot] = time.perf_counter() - started

        threads = [threading.Thread(target=writer, args=(base,)) for base in (0, 1000)]
        readers = [threading.Thread(target=reader, args=(slot,)) for slot in (0, 1)]
        for thread in threads + readers:
            thread.start()
        for thread in readers:
            thread.join()
        stop.set()
        for thread in threads:
            thread.join()
        per_read_ns = 1e9 * sum(seconds) / (2 * reads)
        print(f"{name:18s} runtime_errors={sum(errors):7d} missed_stable_key={sum(misses):7d} "
              f"ns_per_read={per_read_ns:8.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
