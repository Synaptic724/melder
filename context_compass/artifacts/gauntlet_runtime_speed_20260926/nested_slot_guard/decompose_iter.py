"""Per-iteration decomposition of owner gauntlet runs (melder_2 helper).

A lane cycle is one outer scope with its request scopes; `outer_total` times the whole cycle. The harness's
"active" rate covers only the request-scope part (sum of `request_total`). Averages print with 1 us resolution,
so whole-cycle sums over 30 cycles carry about +/-0.015 ms of rounding per library.
"""
import re, pathlib, sys
PER_ITER = {"request": 10, "worker_a": 25, "worker_b": 30}
def runs(path):
    out, cur = [], None
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m = re.search(r"\[(dependency-injector|dishka|melder)\] gauntlet config: .*iterations=(\d+)", line)
        if m:
            if m.group(1) == "dependency-injector" or cur is None or m.group(1) in cur:
                cur = {"iters": int(m.group(2))}; out.append(cur)
            cur[m.group(1)] = {}
            continue
        m = re.search(r"\[(dependency-injector|dishka|melder)\] (.*)$", line)
        if not m or cur is None or m.group(1) not in cur: continue
        lib, rest = m.groups(); d = cur[lib]
        for key, tag in (("thr", "gauntlet threaded phase"), ("tot", "gauntlet total"), ("boot", "gauntlet bootstrap")):
            if rest.startswith(tag):
                d[key] = float(re.search(r"avg=([\d.]+)ms", rest).group(1))
        if rest.startswith("lane="):
            lane = re.match(r"lane=(\w+)", rest).group(1)
            d[lane + "_outer"] = float(re.search(r"outer_total\[avg=([\d.]+)ms", rest).group(1))
            d[lane + "_req"] = 1000.0 / int(re.search(r"active_cycles/s=([\d,]+)", rest).group(1).replace(",", ""))
    return out
for path in sys.argv[1:]:
    for r in runs(path):
        if r["iters"] != 30000 or not all(l in r for l in ("melder", "dishka", "dependency-injector")): continue
        print("==", path)
        for lib in ("melder", "dishka", "dependency-injector"):
            d = r[lib]
            whole = {k: PER_ITER[k] * d[k + "_outer"] for k in PER_ITER}
            crit = max(whole.values())
            print(f"  {lib:20s} total {d['tot']:.3f} threaded {d['thr']:.3f} | whole-cycle us "
                  f"{d['request_outer']*1000:.0f}/{d['worker_a_outer']*1000:.0f}/{d['worker_b_outer']*1000:.0f} "
                  f"request-part us {d['request_req']*1000:.2f}/{d['worker_a_req']*1000:.2f}/{d['worker_b_req']*1000:.2f} "
                  f"| critical lane ms/iter {crit:.3f} | threaded outside cycles {d['thr']-crit:.3f}")
