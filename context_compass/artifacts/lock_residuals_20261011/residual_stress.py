"""
Unforced stress for the two lock residuals (nothing patched or paused; public calls only).

contracted - Conduit.find_contracted_spell walks the Book's `_contracted_spells` keys under the CONDUIT lock while
             link and sever write those keys under the BOOK lock. A link or sever the owner starts holds the owner's
             conduit lock and is excluded; one the PEER starts holds only the peer's. One thread has eight peers link
             to and sever from the owner; the other calls owner.find_contracted_spell(...) in a loop.
inspect    - Spellbook.inspect_spell walks `frame._conduits` holding only its own Book lock while root registration
             writes that map under the FRAME lock, and turns any error into None. Twenty Books are registered
             between the inspector and the provider, so the walk passes them before it finds the provider. One thread
             conjures fresh Books in the frame and cleans their roots up again; the other asks inspect_spell for the
             provider's class and counts wrong (None) answers.

Usage: python residual_stress.py <src copy> <tests dir> <dir of gen_classes.py> <contracted|inspect> <cycles>
"""
import collections
import importlib
import sys
import threading
import time
import traceback

src, tests_dir, gen_dir, mode, cycles = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
for path in (src, tests_dir, gen_dir):
    sys.path.insert(0, path)
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

gen = importlib.import_module("gen_classes")
Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
next_class = iter(range(3000))


def dynamic_book(frame: str) -> Spellbook:
    config = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=config)


def conjured(frame: str, name: str):
    book = dynamic_book(frame)
    cls = getattr(gen, f"S{next(next_class)}")
    book.bind(spell=cls, existence=Existence.unique, permissions="create")
    return book, cls, book.conjure(name=name, dynamic=True)


failures = collections.Counter()
writer_failures = collections.Counter()
done = threading.Event()
stats = {"reads": 0, "writes": 0, "wrong": 0}


def record(counter: collections.Counter, exc: BaseException) -> None:
    where = traceback.extract_tb(exc.__traceback__)[-1].name
    counter[f"{type(exc).__name__} in {where}: {str(exc).splitlines()[0][:80]}"] += 1


if mode == "contracted":
    _, _, owner = conjured("f", "owner")
    peers = [conjured("f", f"peer-{i}")[2] for i in range(8)]

    def writer() -> None:
        for _ in range(cycles):
            for peer in peers:
                try:
                    peer.link(owner)
                    peer.sever_link(owner)
                    stats["writes"] += 2
                except Exception as exc:
                    record(writer_failures, exc)
        done.set()

    def reader() -> None:
        while not done.is_set():
            try:
                owner.find_contracted_spell("no-such-version")
            except Exception as exc:
                record(failures, exc)
            stats["reads"] += 1
else:
    inspector_book, _, _ = conjured("g", "inspector")
    fillers = [conjured("g", f"filler-{i}") for i in range(20)]
    _, target_cls, _ = conjured("g", "provider")
    expected = inspector_book.inspect_spell(target_cls, "g")
    assert expected is not None, "the quiet inspect must find the provider's spell"

    def writer() -> None:
        for j in range(cycles):
            try:
                _, _, root = conjured("g", f"tenant-{j}")
                stats["writes"] += 1
                root.cleanup()
            except Exception as exc:
                record(writer_failures, exc)
        done.set()

    def reader() -> None:
        while not done.is_set():
            try:
                answer = inspector_book.inspect_spell(target_cls, "g")
                if answer != expected:
                    stats["wrong"] += 1
            except Exception as exc:
                record(failures, exc)
            stats["reads"] += 1

t0 = time.perf_counter()
threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"mode={mode} gil={sys._is_gil_enabled()} cycles={cycles} writes={stats['writes']} reads={stats['reads']} "
      f"wrong_answers={stats['wrong']} elapsed={time.perf_counter() - t0:.2f}s")
print("read failures:", dict(failures) if failures else "none")
print("writer failures:", dict(writer_failures) if writer_failures else "none")
