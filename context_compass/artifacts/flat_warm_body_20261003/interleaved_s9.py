"""Interleaved plain vs S9 on every shape's normal plan: alternating 40k-call batches, 7 rounds, medians."""
import gc
import statistics
import time

import codegen_strategy_certification as h


def run(shape: h.Shape) -> None:
    h.captured.clear()
    book, conduit = h.build_world(shape, shape.name)
    try:
        conduit.meld(shape.root.__name__)
        root_id = next(sid for sid, (_s, ns) in h.captured.items()
                       if any(s.spell is shape.root and s.spell_id == ns.get("root_spell_id") for s in ns.get("spells", ())))
        source, namespace = h.captured[root_id]
        meld = conduit._meld
        s9_src, s9_extra = h.transform_owner_store_constants(source, namespace)
        plain = h.compile_variant(source, namespace, {}, "plain")
        s9 = h.compile_variant(s9_src, namespace, s9_extra, "s9")
        for fn in (plain, s9):
            for _ in range(20000):
                fn(meld)
        gc.disable()
        try:
            res = {"plain": [], "s9": []}
            for r in range(7):
                order = [("plain", plain), ("s9", s9)] if r % 2 == 0 else [("s9", s9), ("plain", plain)]
                for label, fn in order:
                    t0 = time.perf_counter_ns()
                    for _ in range(40000):
                        fn(meld)
                    res[label].append((time.perf_counter_ns() - t0) / 40000)
                    store = meld._conduit_creations
                    for key, bucket in list(store._creations.items()):
                        if isinstance(bucket, list):
                            bucket.clear()
                    for key, bucket in list(store._disposable_creations.items()):
                        if isinstance(bucket, list):
                            bucket.clear()
                gc.collect()
        finally:
            gc.enable()
        p, s = statistics.median(res["plain"]), statistics.median(res["s9"])
        print(f"| {shape.name} | {p:.0f} ({min(res['plain']):.0f}-{max(res['plain']):.0f}) | "
              f"{s:.0f} ({min(res['s9']):.0f}-{max(res['s9']):.0f}) | {(s - p) / p * 100:+.0f}% |")
    finally:
        conduit.cleanup()
        book.cleanup()


if __name__ == "__main__":
    print("| shape | plain ns (min-max) | S9 ns (min-max) | delta |")
    print("| --- | --- | --- | --- |")
    for shape in h.shapes():
        run(shape)
