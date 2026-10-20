"""
Why test_quiet_root_pool_decays_to_baseline_and_burst_restretches (0.2.8234) fails about once in a hundred runs.

The test records its burst's misses at `t0 = clock.value` (the real monotonic time when the fake clock was made), then
advances `clock.value += settle - 1.0` and `clock.value += 1.0` and expects the next return to decay the target.
AbstractElasticPool decays only when `now - last_miss >= settle` and `now >= t0 + settle`. Two float additions do not
always land on `t0 + settle`: for some origins the sum is one ulp short and the step is skipped (target stays 40).

Run: python probe_fake_clock_rounding.py
"""
import random
import time


def main() -> int:
    settle = 1800.0
    random.seed(1)
    base = time.monotonic()
    trials = 200000
    skipped = 0
    for _ in range(trials):
        t0 = base + random.uniform(0.0, 100000.0)
        now = (t0 + (settle - 1.0)) + 1.0
        if now - t0 < settle or now < t0 + settle:
            skipped += 1
    print(f"clock origins where the decay step is skipped: {skipped}/{trials} = {skipped / trials:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
