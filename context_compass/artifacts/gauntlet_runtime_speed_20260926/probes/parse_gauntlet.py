"""Parse owner gauntlet pastes into per-run, per-library metrics and same-run ratios (melder_2 helper)."""
import re, sys, pathlib

def parse(path):
    runs, cur = [], None
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m = re.search(r"\[(dependency-injector|dishka|melder)\] gauntlet config: .*iterations=(\d+).*setup=([\d.]+)ms", line)
        if m:
            lib, iters, setup = m.group(1), int(m.group(2)), float(m.group(3))
            if lib == "dependency-injector":
                cur = {"iters": iters}
                runs.append(cur)
            cur[lib] = {"setup": setup}
            continue
        m = re.search(r"\[(dependency-injector|dishka|melder)\] (.*)$", line)
        if not m or cur is None:
            continue
        lib, rest = m.group(1), m.group(2)
        d = cur.setdefault(lib, {})
        def grab(tag, key):
            mm = re.search(tag + r".*?p99=([\d.]+)ms.*?max=([\d.]+)ms", rest)
            if mm:
                d[key + "_p99"], d[key + "_max"] = float(mm.group(1)), float(mm.group(2))
        if rest.startswith("gauntlet total"):
            grab("gauntlet total", "iter")
        elif rest.startswith("gauntlet threaded phase"):
            grab("threaded", "thr")
        elif rest.startswith("gauntlet bootstrap"):
            grab("bootstrap", "boot")
        elif rest.startswith("outer-scope whole-cycle"):
            grab("whole-cycle", "outer")
        elif rest.startswith("request-scope whole-cycle"):
            grab("whole-cycle", "req")
        elif rest.startswith("gauntlet throughput"):
            d["hot"] = int(re.search(r"hot_scopes/s=([\d,]+)", rest).group(1).replace(",", ""))
            d["cleanup"] = float(re.search(r"cleanup=([\d.]+)ms", rest).group(1))
        elif rest.startswith("lane="):
            lane = re.match(r"lane=(\w+)", rest).group(1)
            d["active_" + lane] = int(re.search(r"active_cycles/s=([\d,]+)", rest).group(1).replace(",", ""))
            d["wall_" + lane] = int(re.search(r"wall_cycles/s=([\d,]+)", rest).group(1).replace(",", ""))
            mm = re.search(r"outer_total\[.*?p99=([\d.]+)ms.*?max=([\d.]+)ms", rest)
            d["outer_" + lane + "_max"] = float(mm.group(2))
            mm = re.search(r"request_total\[.*?p99=([\d.]+)ms.*?max=([\d.]+)ms", rest)
            d["req_" + lane + "_max"] = float(mm.group(2))
    return runs

for path in sys.argv[1:]:
    for run in parse(path):
        if "melder" not in run or "dishka" not in run:
            continue
        m, k, di = run["melder"], run["dishka"], run["dependency-injector"]
        print(f"== {pathlib.Path(path).name} iterations={run['iters']}")
        print(f"  hot_scopes/s  melder={m['hot']:,} dishka={k['hot']:,} DI={di['hot']:,} | melder/dishka={m['hot']/k['hot']:.3f} melder/DI={m['hot']/di['hot']:.3f}")
        for lane in ("request", "worker_a", "worker_b"):
            print(f"  {lane:8s} active melder/dishka={m['active_'+lane]/k['active_'+lane]:.3f} (m={m['active_'+lane]:,} d={k['active_'+lane]:,})"
                  f" | wall melder/dishka={m['wall_'+lane]/k['wall_'+lane]:.3f} melder/DI={m['wall_'+lane]/di['wall_'+lane]:.3f}")
        print(f"  iteration p99/max ms: melder {m['iter_p99']}/{m['iter_max']} dishka {k['iter_p99']}/{k['iter_max']} DI {di['iter_p99']}/{di['iter_max']}")
        print(f"  threaded  p99/max ms: melder {m['thr_p99']}/{m['thr_max']} dishka {k['thr_p99']}/{k['thr_max']} DI {di['thr_p99']}/{di['thr_max']}")
        print(f"  bootstrap p99/max ms: melder {m['boot_p99']}/{m['boot_max']} dishka {k['boot_p99']}/{k['boot_max']} DI {di['boot_p99']}/{di['boot_max']}")
        print(f"  outer-cycle p99/max : melder {m['outer_p99']}/{m['outer_max']} dishka {k['outer_p99']}/{k['outer_max']} DI {di['outer_p99']}/{di['outer_max']}")
        print(f"  request-cycle p99/max: melder {m['req_p99']}/{m['req_max']} dishka {k['req_p99']}/{k['req_max']} DI {di['req_p99']}/{di['req_max']}")
        print(f"  setup ms: melder {m['setup']} dishka {k['setup']} DI {di['setup']} | end cleanup ms: melder {m['cleanup']} dishka {k['cleanup']} DI {di['cleanup']}")
