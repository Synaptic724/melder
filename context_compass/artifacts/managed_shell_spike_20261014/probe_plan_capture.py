"""Probe B0: capture the emitted normal plan of the worker shape (Manager unique -> Worker many) on 0.2.8238."""
import os
import sys

import codegen_strategy_certification as cert  # the harness: patches SitePlanLowering.emit to capture plans

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    shape = cert.shapes()[0]
    cert.captured.clear()
    book, conduit = cert.build_world(shape, "probe-b0")
    try:
        instance = conduit.meld("Worker")
        assert type(instance) is shape.root
        root_id = None
        for sid, (_src, ns) in cert.captured.items():
            if any(s.spell is shape.root and s.spell_id == ns.get("root_spell_id") for s in ns.get("spells", ())):
                root_id = sid
        source, namespace = cert.captured[root_id]
        out = os.path.join(HERE, "logs", "probe_plan_capture_worker_source.txt")
        with open(out, "w", encoding="utf-8") as handle:
            handle.write(source)
        print(source)
        print("--- namespace keys:", sorted(k for k in namespace if not k.startswith("__")))
        print("--- site_groups:", cert.site_groups(source))
        spells = namespace["spells"]
        for i, s in enumerate(spells):
            print(i, s.spell.__name__, s.existence, "owner_store" , type(s._owner_creations).__name__)
    finally:
        conduit.cleanup()
        book.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
