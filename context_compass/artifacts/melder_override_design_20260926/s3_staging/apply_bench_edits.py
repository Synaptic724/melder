"""Owner-approved benchmark fixes for test_overrides_all.py (2026-09-26) - anchored edits.

Usage: python apply_bench_edits.py <tree_root> [--check]

1. Every supported library is imported before the first case, so every case runs with the same heap.
2. GC defaults to off for the timed window (switched once by the main thread); each case collects at its end.
3. The stop time is stored before the start barrier releases the workers (fixes 0-step runs).
Each anchor must match exactly once (either line ending) or nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

TARGET = "benchmarks/testing_other_di/test_overrides_all.py"

PRELOAD = '''    if lib == "melder":
        return _build_override_melder(g)
    raise AssertionError(f"Unknown lib: {lib}")


# Modules each builder imports, per library. `_preload_all_libraries` imports all of them before the
# first case so every case runs with the same process heap: a collection walks every tracked object,
# `import melder` alone adds ~57k, and a library timed before another was imported would otherwise be
# measured against a smaller heap.
_LIBRARY_MODULES: dict[str, tuple[str, ...]] = {
    "dependency-injector": ("dependency_injector", "dependency_injector.providers"),
    "lagom": ("lagom",),
    "injector": ("injector",),
    "dishka": ("dishka",),
    "melder": (
        "melder",
        "melder.aether.aether",
        "melder.aether.conduit.conduit",
        "melder.aether.spellbook.existence.existence",
        "melder.aether.spellbook.spellbook",
    ),
}


@pytest.fixture(scope="module", autouse=True)
def _preload_all_libraries() -> None:
    """
    Import every supported library before the first case, whatever DI_LIBS selects, then collect once.

    A library that is not installed is left to its builder's importorskip.
    """
    for module_names in _LIBRARY_MODULES.values():
        for module_name in module_names:
            try:
                importlib.import_module(module_name)
            except ImportError:
                break
    gc.collect()
'''

OLD_WORKER_AND_TIMED = '''    def _run_worker(ix: int) -> None:
        try:
            was_enabled = gc.isenabled()
            if cfg.gc_mode == "disabled" and was_enabled:
                gc.disable()

            try:
                start_barrier.wait()
                stop_at = stop_time_holder[0]
                local_i = 0
                local_stats = stats[ix]

                while not stop_event.is_set() and time.perf_counter() < stop_at:
                    root = ops.get_root()
                    local_stats.steps += 1
                    local_i += 1

                    if cfg.validate_every > 0 and (local_i % cfg.validate_every) == 0:
                        observed = g.override_accessor(root)
                        for value in observed:
                            if value is not ops.override_instance:
                                raise AssertionError(
                                    f"{ops.name}:{g.name} override did not apply "
                                    f"({value!r} is not override instance)"
                                )

                    if cfg.gc_mode == "periodic" and cfg.gc_every > 0:
                        if (local_i % cfg.gc_every) == 0:
                            gc.collect()
            finally:
                if cfg.gc_mode == "disabled" and was_enabled:
                    gc.enable()

        except BaseException as e:
            stats[ix].errors += 1
            errors.append(e)
            stop_event.set()

    threads_list: list[threading.Thread] = []
    for i in range(cfg.threads):
        t = threading.Thread(target=_run_worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    def _run_timed() -> None:
        start_barrier.wait()
        start_t = time.perf_counter()
        stop_time_holder[0] = start_t + cfg.duration_s

        for t in threads_list:
            t.join()

        elapsed_s = time.perf_counter() - start_t
        if errors:
'''

NEW_WORKER_AND_TIMED = '''    def _run_worker(ix: int) -> None:
        try:
            start_barrier.wait()
            stop_at = stop_time_holder[0]
            local_i = 0
            local_stats = stats[ix]

            while not stop_event.is_set() and time.perf_counter() < stop_at:
                root = ops.get_root()
                local_stats.steps += 1
                local_i += 1

                if cfg.validate_every > 0 and (local_i % cfg.validate_every) == 0:
                    observed = g.override_accessor(root)
                    for value in observed:
                        if value is not ops.override_instance:
                            raise AssertionError(
                                f"{ops.name}:{g.name} override did not apply "
                                f"({value!r} is not override instance)"
                            )

                if cfg.gc_mode == "periodic" and cfg.gc_every > 0:
                    if (local_i % cfg.gc_every) == 0:
                        gc.collect()

        except BaseException as e:
            stats[ix].errors += 1
            errors.append(e)
            stop_event.set()

    threads_list: list[threading.Thread] = []
    for i in range(cfg.threads):
        t = threading.Thread(target=_run_worker, args=(i,), daemon=True)
        threads_list.append(t)
        t.start()

    def _run_timed() -> None:
        # GC is switched once, by this thread, around the whole window (workers toggling the
        # process-global flag raced with threads > 1). The case collects at its end, in cleanup.
        gc_was_enabled = gc.isenabled()
        if cfg.gc_mode == "disabled":
            gc.disable()
        try:
            # The stop time is stored before the barrier releases the workers, which read it right
            # after the barrier (storing it afterwards let a worker read 0.0 and run zero steps).
            start_t = time.perf_counter()
            stop_time_holder[0] = start_t + cfg.duration_s
            start_barrier.wait()

            for t in threads_list:
                t.join()

            elapsed_s = time.perf_counter() - start_t
        finally:
            if gc_was_enabled:
                gc.enable()
        if errors:
'''

EDITS = [
    ("replace", "import gc\nimport inspect\n", "import gc\nimport importlib\nimport inspect\n"),
    ("replace",
     '    if lib == "melder":\n'
     "        return _build_override_melder(g)\n"
     '    raise AssertionError(f"Unknown lib: {lib}")\n',
     PRELOAD),
    ("replace",
     "        DI_OVERRIDE_GC_EVERY         default 2000\n"
     "        DI_OVERRIDE_GC_MODE          periodic | disabled | none (default periodic)\n",
     "        DI_OVERRIDE_GC_EVERY         default 2000 (periodic mode only)\n"
     "        DI_OVERRIDE_GC_MODE          disabled | periodic | none (default disabled)\n"
     "            disabled: automatic GC is off for the timed window and each case collects once\n"
     "                      when it ends (its cleanup), so no collection is timed.\n"
     "            periodic: gc.collect() every DI_OVERRIDE_GC_EVERY steps inside the window.\n"
     "            none:     automatic GC stays on; no explicit collections.\n"
     "    Every supported library is imported before the first case (`_preload_all_libraries`).\n"),
    ("replace",
     '            gc_mode=_env_str("DI_OVERRIDE_GC_MODE", "periodic").lower(),\n',
     '            gc_mode=_env_str("DI_OVERRIDE_GC_MODE", "disabled").lower(),\n'),
    ("replace", OLD_WORKER_AND_TIMED, NEW_WORKER_AND_TIMED),
]


def main() -> None:
    """Check every edit, then write (unless --check)."""
    path = pathlib.Path(sys.argv[1]) / TARGET
    check = "--check" in sys.argv[2:]
    data = path.read_bytes().decode("utf-8")
    for edit in EDITS:
        data = _apply_one(data, edit, TARGET)
    compile(data, TARGET, "exec")
    if not check:
        path.write_bytes(data.encode("utf-8"))
    print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
