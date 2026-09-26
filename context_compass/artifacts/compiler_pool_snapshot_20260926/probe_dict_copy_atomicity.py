"""Probe: live dict iteration vs dict.copy() while another thread inserts and removes keys.

Counts, over a fixed number of reader rounds, RuntimeError ("dictionary changed size during iteration") and
short reads (fewer than the 300 keys that are never removed).
Run on free-threaded 3.14 (default) and with PYTHON_GIL=1.
"""
import sys
import threading
from typing import Dict, List


def run(mode: str, rounds: int) -> tuple:
    """Return (errors, short reads) over `rounds` reader rounds in `mode` ("live" or "copy")."""
    pool: Dict[str, object] = {f"k{i}": object() for i in range(300)}
    stop = threading.Event()

    def writer() -> None:
        """Insert and remove keys until stopped, as bind/notch/transfer do."""
        n = 0
        while not stop.is_set():
            key = f"w{n % 64}"
            pool[key] = object()
            pool.pop(key, None)
            n += 1

    thread = threading.Thread(target=writer)
    thread.start()
    errors = 0
    short = 0
    try:
        for _ in range(rounds):
            try:
                if mode == "live":
                    visible: List[str] = [k for k, v in pool.items() if v is not None]
                else:
                    visible = [k for k, v in pool.copy().items() if v is not None]
                if sum(1 for k in visible if k.startswith("k")) < 300:
                    short += 1
            except RuntimeError:
                errors += 1
    finally:
        stop.set()
        thread.join()
    return errors, short


if __name__ == "__main__":
    gil = sys._is_gil_enabled()
    for mode in ("live", "copy"):
        errors, short = run(mode, 20000)
        print(f"gil={gil} mode={mode} errors={errors} short_reads={short} of 20000")
