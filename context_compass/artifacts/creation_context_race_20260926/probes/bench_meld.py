"""Warm-meld micro-benchmark: ns per meld for automatic and dynamic worlds (one process per variant)."""
import sys, time, statistics, pathlib
root = pathlib.Path(sys.argv[1]); mode = sys.argv[2]; lane = sys.argv[3]
sys.path.insert(0, str(root / "src")); sys.path.insert(0, str(root))
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration, apply_automatic_defaults_for_spellbook_configuration)
from tests.mocks.spellbook.core_classes import BasicService

configuration = SpellbookConfiguration()
if mode == "dynamic":
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
else:
    apply_automatic_defaults_for_spellbook_configuration(configuration)
book = Spellbook(configuration=configuration)
kwargs = {}
if lane == "hooks":
    kwargs["pre_hooks"] = [lambda *a, **k: None]
spell_id = book.bind(spell=BasicService, existence=Existence.unique, **kwargs)
conduit = book.conjure(dynamic=(mode == "dynamic"), name="bench")
meld = conduit.meld
for _ in range(20000):
    meld(spell_id=spell_id)
N = 200000; samples = []
for _ in range(7):
    t0 = time.perf_counter_ns()
    for _ in range(N):
        meld(spell_id=spell_id)
    samples.append((time.perf_counter_ns() - t0) / N)
print(f"{mode:8s} {lane:8s} min={min(samples):7.1f} median={statistics.median(samples):7.1f} ns/meld")
conduit.cleanup()
