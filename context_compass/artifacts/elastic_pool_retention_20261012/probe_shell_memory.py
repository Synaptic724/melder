"""
Probe: memory held by one pooled lesser-conduit shell and one pooled spellspace shell (tracemalloc), and the time to
build and to destroy each, so the retention ceiling (max_idle) can be chosen from numbers.

Usage: PYTHONPATH=<tree>/src python probe_shell_memory.py
"""
import gc
import sys
import time
import tracemalloc

from melder import Spellbook


def write(line: str) -> None:
    """Write one result line."""
    sys.stdout.write(line + "\n")


def main() -> int:
    """Measure 100 lesser shells and 100 spellspace shells held at once; return 0."""
    book = Spellbook()
    root = book.conjure(name="memory_probe_root")
    try:
        warm = [root.create_lesser_conduit() for _ in range(5)]
        for lesser in warm:
            lesser.cleanup()
        count = 100
        gc.collect()
        tracemalloc.start()
        before = tracemalloc.take_snapshot()
        t0 = time.perf_counter_ns()
        held = [root.create_lesser_conduit() for _ in range(count)]
        build_ns = (time.perf_counter_ns() - t0) / count
        gc.collect()
        after = tracemalloc.take_snapshot()
        lesser_bytes = sum(stat.size_diff for stat in after.compare_to(before, "filename")) / count
        tracemalloc.stop()
        write(f"lesser shell: {lesser_bytes / 1024:.1f} KiB each (incl. its fresh pool reuse of 5 warm shells), "
              f"create {build_ns / 1000:.1f} us each over {count}")
        t0 = time.perf_counter_ns()
        for lesser in held:
            lesser.permanent_cleanup()
        destroy_ns = (time.perf_counter_ns() - t0) / count
        write(f"lesser shell: permanent_cleanup {destroy_ns / 1000:.1f} us each")

        gc.collect()
        tracemalloc.start()
        before = tracemalloc.take_snapshot()
        t0 = time.perf_counter_ns()
        spaces = [root._spellspace_pool.create_object() for _ in range(count)]
        space_build_ns = (time.perf_counter_ns() - t0) / count
        gc.collect()
        after = tracemalloc.take_snapshot()
        space_bytes = sum(stat.size_diff for stat in after.compare_to(before, "filename")) / count
        tracemalloc.stop()
        write(f"spellspace shell: {space_bytes / 1024:.1f} KiB each, create {space_build_ns / 1000:.1f} us each")
        t0 = time.perf_counter_ns()
        for space in spaces:
            space.permanent_cleanup()
        write(f"spellspace shell: permanent_cleanup {(time.perf_counter_ns() - t0) / count / 1000:.1f} us each")
    finally:
        root.permanent_cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
