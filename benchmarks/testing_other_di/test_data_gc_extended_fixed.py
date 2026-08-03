from __future__ import annotations

import gc
import time
from dataclasses import dataclass
from typing import Any, Iterable, Callable, Tuple

import pytest


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


@dataclass(slots=True)
class Node:
    """
    Object that can carry:
      - buf (payload)
      - next pointer (can form cycles)
      - children list and meta dict
    """
    buf: bytearray
    next: "Node | None" = None
    children: list["Node"] | None = None
    meta: dict[str, Any] | None = None

    def cleanup(self) -> None:
        # Break graph links + drop containers + drop payload
        self.next = None
        if self.children is not None:
            self.children.clear()
            self.children = None
        if self.meta is not None:
            self.meta.clear()
            self.meta = None
        self.buf = bytearray()


def _make_no_cycle_chain(n: int, payload_bytes: int) -> Node:
    head = Node(buf=bytearray(payload_bytes))
    cur = head
    for _ in range(n - 1):
        nxt = Node(buf=bytearray(payload_bytes))
        cur.next = nxt
        cur = nxt
    head.children = [Node(buf=bytearray(64)) for _ in range(4)]
    head.meta = {"k": 1, "v": "x" * 8}
    return head


def _make_ring_cycle(n: int, payload_bytes: int) -> Node:
    nodes = [Node(buf=bytearray(payload_bytes)) for _ in range(n)]
    for i in range(n):
        nodes[i].next = nodes[(i + 1) % n]
    nodes[0].children = [Node(buf=bytearray(64)) for _ in range(4)]
    nodes[0].meta = {"k": 1, "v": "x" * 8}
    return nodes[0]


def _make_cycle_with_acyclic_tail(cycle_n: int, tail_n: int, payload_bytes: int) -> Node:
    head = _make_ring_cycle(cycle_n, payload_bytes)
    cur = head
    for _ in range(cycle_n // 2):
        assert cur.next is not None
        cur = cur.next
    tail_payload = payload_bytes // 4 if payload_bytes >= 4 else payload_bytes
    tail = _make_no_cycle_chain(tail_n, tail_payload)
    cur.children = cur.children or []
    cur.children.append(tail)
    return head


def _iter_nodes_from_root(root: Node, limit: int = 50_000) -> Iterable[Node]:
    # Avoid infinite loops on cycles with a seen set.
    seen: set[int] = set()
    stack = [root]
    steps = 0
    while stack:
        node = stack.pop()
        nid = id(node)
        if nid in seen:
            continue
        seen.add(nid)
        yield node
        steps += 1
        if steps >= limit:
            return
        if node.next is not None:
            stack.append(node.next)
        if node.children:
            stack.extend(node.children)


def _run_case(
    *,
    iters: int,
    maker: Callable[[int], Node],
    payload_bytes: int,
    do_cleanup: bool,
    gc_mode: str,
) -> dict[str, float | int | str]:
    """
    Measures:
      - loop_time: allocate/build (+ optional cleanup) repeated iters times
      - gc_time: one gc.collect() after loop
      - unreachable: count returned by gc.collect()
    """
    gc.collect()

    old_enabled = gc.isenabled()
    if gc_mode == "disabled_during_loop":
        gc.disable()

    try:
        t0 = time.perf_counter()
        for _ in range(iters):
            root = maker(payload_bytes)
            if do_cleanup:
                for n in _iter_nodes_from_root(root):
                    n.cleanup()
            root = None
        loop_s = time.perf_counter() - t0
    finally:
        if gc_mode == "disabled_during_loop":
            if old_enabled:
                gc.activate()
            else:
                gc.disable()

    t_gc0 = time.perf_counter()
    unreachable = gc.collect()
    gc_s = time.perf_counter() - t_gc0

    return {
        "iters": iters,
        "payload_bytes": payload_bytes,
        "cleanup": int(do_cleanup),
        "gc_mode": gc_mode,
        "loop_ms": _ms(loop_s),
        "per_iter_us": _us(loop_s) / iters,
        "gc_ms": _ms(gc_s),
        "unreachable": int(unreachable),
    }


# Keep runtime reasonable while still covering small → large payloads.
_PAYLOAD_CASES = [
    (256, 50_000),
    (2_048, 20_000),
    (65_536, 2_000),
    (1_048_576, 200),
]


# IMPORTANT: include has_cycle explicitly (string matching "cycle" was a bug
# because "no_cycle_chain_9" contains "cycle" as a substring).
_PATTERNS: Tuple[Tuple[str, bool, Callable[[int], Node]], ...] = (
    ("no_cycle_chain_9", False, lambda pb: _make_no_cycle_chain(9, pb)),
    ("ring_cycle_9", True, lambda pb: _make_ring_cycle(9, pb)),
    ("cycle9_tail6", True, lambda pb: _make_cycle_with_acyclic_tail(9, 6, pb)),
)


@pytest.mark.parametrize("payload_bytes,iters", _PAYLOAD_CASES)
@pytest.mark.parametrize("gc_mode", ["enabled", "disabled_during_loop"])
@pytest.mark.parametrize("pattern", _PATTERNS)
def test_cleanup_vs_gc_extended(payload_bytes: int, iters: int, gc_mode: str, pattern) -> None:
    """
    Run:
      pytest -q benchmarks/testing_other_di/test_data_gc_extended_fixed.py -s
    """
    name, has_cycle, maker = pattern

    a = _run_case(
        iters=iters,
        maker=maker,
        payload_bytes=payload_bytes,
        do_cleanup=True,
        gc_mode=gc_mode,
    )
    b = _run_case(
        iters=iters,
        maker=maker,
        payload_bytes=payload_bytes,
        do_cleanup=False,
        gc_mode=gc_mode,
    )

    a_total = float(a["loop_ms"]) + float(a["gc_ms"])
    b_total = float(b["loop_ms"]) + float(b["gc_ms"])
    speed = (b_total / a_total) if a_total else float("inf")

    print(
        f"\n=== {name} payload={payload_bytes}B iters={iters} gc_mode={gc_mode} ===\n"
        f"explicit cleanup: loop={a['loop_ms']:9.3f}ms ({a['per_iter_us']:8.3f}us/iter) "
        f"+ gc={a['gc_ms']:7.3f}ms unreachable={a['unreachable']}\n"
        f"gc/refcount only: loop={b['loop_ms']:9.3f}ms ({b['per_iter_us']:8.3f}us/iter) "
        f"+ gc={b['gc_ms']:7.3f}ms unreachable={b['unreachable']}\n"
        f"total speedup(cleanup vs gc_only) = {speed:5.2f}x\n"
    )

    # Sanity: for cyclic patterns, gc.collect() should find something when we don't cleanup.
    if has_cycle:
        assert int(b["unreachable"]) >= 1
