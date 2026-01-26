from __future__ import annotations

import gc
import time
from dataclasses import dataclass

import pytest


def _ms(seconds: float) -> float:
    return seconds * 1000.0


@dataclass(slots=True)
class Payload:
    """
    A small object that can optionally form a reference cycle.

    Why cycles matter:
      - Pure refcounting can't reclaim cycles immediately.
      - The cyclic GC must run to collect them.
    """

    # A non-trivial buffer to simulate "real objects" holding memory.
    buf: bytearray
    # Optional cycle
    other: "Payload | None" = None

    def cleanup(self) -> None:
        """
        Deterministic teardown:
          - Break cycles
          - Drop buffers
        """
        self.other = None
        # Replace with empty buffer (drops the big allocation)
        self.buf = bytearray()


def _make_cycle(payload_bytes: int) -> Payload:
    a = Payload(buf=bytearray(payload_bytes))
    b = Payload(buf=bytearray(payload_bytes))
    a.other = b
    b.other = a
    return a  # returning one node keeps the cycle reachable


def _make_no_cycle(payload_bytes: int) -> Payload:
    return Payload(buf=bytearray(payload_bytes), other=None)


def _bench_explicit_cleanup(*, iters: int, payload_bytes: int, with_cycle: bool) -> tuple[float, int]:
    """
    Create -> cleanup -> drop ref.
    We also count how many cyclic objects GC finds at the end.
    """
    # Try to stabilize: start from a clean-ish GC state
    gc.collect()

    t0 = time.perf_counter()
    for _ in range(iters):
        obj = _make_cycle(payload_bytes) if with_cycle else _make_no_cycle(payload_bytes)
        obj.cleanup()
        obj = None  # drop ref
    t_total = time.perf_counter() - t0

    # Force a collection and report what was left for GC to do
    unreachable = gc.collect()
    return t_total, unreachable


def _bench_no_cleanup_gc_at_end(*, iters: int, payload_bytes: int, with_cycle: bool) -> tuple[float, int]:
    """
    Create -> drop ref.
    If with_cycle=True, the cycle survives until GC runs.
    """
    gc.collect()

    t0 = time.perf_counter()
    for _ in range(iters):
        obj = _make_cycle(payload_bytes) if with_cycle else _make_no_cycle(payload_bytes)
        obj = None
    t_total = time.perf_counter() - t0

    unreachable = gc.collect()
    return t_total, unreachable


@pytest.mark.parametrize(
    "iters,payload_bytes",
    [
        (10_000, 256),
        (10_000, 2_048),
        (50_000, 256),
    ],
)
@pytest.mark.parametrize("with_cycle", [False, True])
def test_cleanup_up_front_vs_gc_at_end(iters: int, payload_bytes: int, with_cycle: bool) -> None:
    """
    Compare:
      A) explicit cleanup each iteration
      B) no cleanup, rely on GC at end

    Run:
      pytest -q benchmarks/test_cleanup_vs_gc_perf.py -s
    """
    # Optional: keep GC enabled during the loop (default Python behavior).
    # If you want to see pure refcount vs cycle behavior, leave it enabled.
    # We'll just measure the overall wall time + the final gc.collect() result.

    t_a, unreachable_a = _bench_explicit_cleanup(
        iters=iters,
        payload_bytes=payload_bytes,
        with_cycle=with_cycle,
    )
    t_b, unreachable_b = _bench_no_cleanup_gc_at_end(
        iters=iters,
        payload_bytes=payload_bytes,
        with_cycle=with_cycle,
    )

    kind = "cycle" if with_cycle else "no-cycle"

    print(
        f"\n=== payload={payload_bytes}B iters={iters} kind={kind} ===\n"
        f"explicit cleanup:  total={_ms(t_a):9.3f} ms | per_iter={_ms(t_a)/iters:9.6f} ms"
        f" | gc_unreachable_after={unreachable_a}\n"
        f"gc at end only:    total={_ms(t_b):9.3f} ms | per_iter={_ms(t_b)/iters:9.6f} ms"
        f" | gc_unreachable_after={unreachable_b}\n"
        f"speedup(cleanup vs gc_end) = {t_b / t_a if t_a else float('inf'):.2f}x\n"
    )

    # Sanity assertions (not performance assertions):
    # If we made cycles and did NOT cleanup, GC should typically find unreachable objects.
    if with_cycle:
        assert unreachable_b >= 1
