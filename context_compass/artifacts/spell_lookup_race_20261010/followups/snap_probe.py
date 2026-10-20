"""Is a one-call snapshot of a dict exact under concurrent writers? Counts exceptions and missed stable keys."""
import sys, threading, time
STABLE = [f"stable{i}" for i in range(64)]
def run(label, op, seconds=2.0):
    d = {k: k for k in STABLE}
    stop = threading.Event(); errors = [0]; misses = [0]; reads = [0]
    def writer(seed):
        i = 0
        while not stop.is_set():
            k = f"w{seed}-{i % 4000}"
            d[k] = k
            if i % 3 == 0:
                d.pop(f"w{seed}-{(i - 1500) % 4000}", None)
            i += 1
    def reader():
        while not stop.is_set():
            try:
                got = op(d)
                reads[0] += 1
                if got is not None and not all(s in got for s in STABLE[:8]):
                    misses[0] += 1
            except Exception:
                errors[0] += 1
    ts = [threading.Thread(target=writer, args=(n,)) for n in range(2)] + [threading.Thread(target=reader) for _ in range(2)]
    [t.start() for t in ts]; time.sleep(seconds); stop.set(); [t.join() for t in ts]
    print(f"{label:34s} reads={reads[0]:8d} errors={errors[0]:6d} misses={misses[0]:5d}")
def ext(d):
    out = []; out.extend(d.values()); return set(out)
run("list(d.values())", lambda d: set(list(d.values())))
run("list(d)", lambda d: set(list(d)))
run("lst.extend(d.values())", ext)
run("list(d.items())", lambda d: {k for k, _ in list(d.items())})
run("[v for v in d.values()] (control)", lambda d: set([v for v in d.values()]))
run("next(iter(d.values())) (control)", lambda d: (next(iter(d.values())), None)[1])
print(sys.version.split()[0], "gil_enabled=", sys._is_gil_enabled())
