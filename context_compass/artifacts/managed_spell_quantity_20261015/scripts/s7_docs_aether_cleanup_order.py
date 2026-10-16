"""S7 D7: state Aether.cleanup's real order in both source maps (found while scoring them).

`Aether.cleanup` (src/melder/aether/aether.py:268-361) opens the LoadGate and cleans the aetheric mediator plane
first, so parked waiters wake; then the frames; then ReleaseManagedSpell (the frames' root stores unregistered their
pools); then Crystallizer, MutationResearch, the configuration, Nexus and the utility system; the singleton
bookkeeping resets in a `finally`; the logger goes last. src_architecture's cleanup sequence said "cleans frames,
then ReleaseManagedSpell, then the other hosted roots" (the gate and the plane go first, not after), and
src_components' Aether entry said only "tears down frames and resets singleton state". Each block is replaced once
(asserted); regenerate both indexes after this script.
Run from the repository root: python <this file>
"""
import pathlib

EDITS = (
    ("context_compass/system_docs/src_architecture.md",
     "3. `Aether.cleanup()` cleans frames, then `ReleaseManagedSpell` (the frames' root stores have unregistered their\n"
     "   pools), then the other hosted roots, resets singleton state, cleans logger.\n",
     "3. `Aether.cleanup()` opens the LoadGate and cleans the aetheric mediator plane first, so parked waiters wake;\n"
     "   then the frames; then `ReleaseManagedSpell` (the frames' root stores have unregistered their pools); then\n"
     "   Crystallizer, MutationResearch, the configuration, Nexus and the utility system. It resets singleton state in a\n"
     "   `finally`, whatever a child raised, and cleans the logger last.\n"),
    ("context_compass/system_docs/src_components.md",
     "Lifecycle/Cleanup:\n- `cleanup()` tears down frames and resets singleton state.\n",
     "Lifecycle/Cleanup:\n- `cleanup()` opens the LoadGate and cleans the mediator plane first (parked waiters wake), then tears down\n"
     "  the frames, then cleans `ReleaseManagedSpell` (the frames' root stores unregistered their pools), Crystallizer,\n"
     "  MutationResearch, the configuration, Nexus and the utility system; it resets the singleton bookkeeping in a\n"
     "  `finally` whatever a child raised, so `Aether()` can build a fresh root, and cleans its logger last.\n"),
)
for path, old, new in EDITS:
    p = pathlib.Path(path)
    t = p.read_bytes().decode("utf-8")
    if t.count(old) != 1:
        raise SystemExit(f"{path}: the old block occurs {t.count(old)} times (expected 1); nothing written")
    p.write_bytes(t.replace(old, new).encode("utf-8"))
    print("updated", path)
