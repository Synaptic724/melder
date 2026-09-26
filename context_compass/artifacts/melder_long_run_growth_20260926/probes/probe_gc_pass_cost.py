"""Cost of one full gc.collect() vs the harness's retained timing-sample entries (sandbox)."""
import gc, sys, time
per_iter = 393  # 3 per-iteration lists + 65 cycles x 6 lane metrics
lists = [[] for _ in range(21)]
done_iters = 0
print(sys.version.split()[0], "gil", sys._is_gil_enabled())
for target in (0, 5_000, 25_000, 50_000, 100_000):
    while done_iters < target:
        base = 1_000_000 + done_iters
        for j in range(3):
            lists[j].append(base * 7 + j)
        for j in range(3, 21):
            L = lists[j]
            for k in range(65 // 6 + 1 if j < 20 else 65 - 18 * (65 // 6 + 1) + (65 // 6 + 1)):
                L.append(base * 13 + j * 101 + k)
        done_iters += 1
    entries = sum(len(L) for L in lists)
    samples = []
    for _ in range(3):
        t0 = time.perf_counter_ns(); gc.collect(); samples.append(time.perf_counter_ns() - t0)
    print(f"iterations={target:7d} retained_entries={entries:11d} gc.collect ms: " + ", ".join(f"{s/1e6:.1f}" for s in samples), flush=True)
