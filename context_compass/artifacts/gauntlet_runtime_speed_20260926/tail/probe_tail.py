"""melder_2 VM probe (no src change): attribute the gauntlet's slow scope cycles turn by turn.

Runs the harness's own per-iteration function (_run_gauntlet_once) for one library and keeps, per turn, the
total / bootstrap / threaded time and the slowest outer cycle and request window of each lane, with the cycle's
position inside the turn. A sys audit hook records compile / exec / open events with the turn they fell in, so
lazy compilation and file I/O on the loop are visible; gc.callbacks records collections.

usage: probe_tail.py <lib> <iterations> [top]
"""
import gc, os, statistics, sys, threading, time
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "combined")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

lib = sys.argv[1]
iterations = int(sys.argv[2])
top = int(sys.argv[3]) if len(sys.argv) > 3 else 12
events = []
turn = [-2]
WATCH = {"compile", "exec", "open"}


def audit(event: str, args: tuple) -> None:
    if event in WATCH:
        detail = str(args[1] if event == "compile" and len(args) > 1 else args[0])[:80]
        events.append((turn[0], event, detail))


gc_events = []
gc_start = {}


def on_gc(phase: str, info: dict) -> None:
    tid = threading.get_ident()
    if phase == "start":
        gc_start[tid] = time.perf_counter_ns()
    else:
        t0 = gc_start.pop(tid, None)
        if t0 is not None:
            gc_events.append((turn[0], (time.perf_counter_ns() - t0) / 1e6, info.get("generation")))


os.environ["DI_GAUNTLET_ITERS"] = str(iterations)
cfg = g._GauntletConfig.from_env()
t_setup = time.perf_counter_ns()
ops = g._build_ops(lib)
ops.spawn_singletons()
setup_ms = (time.perf_counter_ns() - t_setup) / 1e6
sys.addaudithook(audit)
gc.callbacks.append(on_gc)
rows = []
for ix in range(iterations):
    turn[0] = ix
    r = g._run_gauntlet_once(ops, cfg, ix)
    lanes = {}
    for name, m in r.lane_metrics.items():
        outer = list(m.outer_total_ns)
        req = list(m.request_total_ns)
        if not outer:
            continue
        oi = max(range(len(outer)), key=outer.__getitem__)
        ri = max(range(len(req)), key=req.__getitem__)
        lanes[name] = (outer[oi] / 1e6, oi, req[ri] / 1e6, ri)
    rows.append((ix, r.total_ns / 1e6, r.bootstrap_ns / 1e6, r.threaded_ns / 1e6, lanes))
turn[0] = -1
ev_by_turn = {}
for t, e, d in events:
    ev_by_turn.setdefault(t, []).append(f"{e}:{d}")
print(f"== {lib} iterations={iterations} setup={setup_ms:.1f}ms gc_collections_in_loop={len(gc_events)} "
      f"audit_events_in_loop={sum(1 for t, _, _ in events if t >= 0)}")
cycles = [(lanes[n][0], ix, n, lanes[n][1], "outer") for ix, _, _, _, lanes in rows for n in lanes]
cycles += [(lanes[n][2], ix, n, lanes[n][3], "request") for ix, _, _, _, lanes in rows for n in lanes]
cycles.sort(reverse=True)
print(f"-- slowest {top} single cycles (ms | turn | lane | cycle# in turn | window)")
for v, ix, n, ci, kind in cycles[:top]:
    ev = ev_by_turn.get(ix, [])
    print(f"   {v:7.3f} | turn {ix:6d} | {n:8s} | #{ci:2d} | {kind:7s} | turn events: {len(ev)} {ev[:3]}")
outer_all = sorted((lanes[n][0] for _, _, _, _, lanes in rows for n in lanes), reverse=True)
for thr in (1.0, 2.0, 4.0):
    print(f"-- turns whose slowest outer cycle > {thr} ms: {sum(1 for v in outer_all if v > thr)}")
slow_turns = sorted(rows, key=lambda r: r[1], reverse=True)[:top]
print(f"-- slowest {top} turns (turn | total | bootstrap | threaded | outside=total-boot-thr | events)")
for ix, tot, boot, thr, lanes in sorted(slow_turns):
    ev = ev_by_turn.get(ix, [])
    print(f"   turn {ix:6d} | {tot:7.3f} | {boot:6.3f} | {thr:7.3f} | {tot - boot - thr:6.3f} | {len(ev)} {ev[:2]}")
outside = [r[1] - r[2] - r[3] for r in rows]
print(f"-- outside-threaded per turn: median={statistics.median(outside):.3f} p99={sorted(outside)[int(len(outside)*0.99)]:.3f} max={max(outside):.3f} ms")
print(f"-- events by turn (first 8 turns with events): {[(t, len(v)) for t, v in sorted(ev_by_turn.items()) if t >= 0][:8]}")
if gc_events:
    print(f"-- gc in loop: {gc_events[:10]}")
