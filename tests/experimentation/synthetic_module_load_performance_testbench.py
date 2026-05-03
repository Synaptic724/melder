"""
Measure synthetic/codegen module load and object construction cost.

Purpose:
    Compare a simple runner-driven synthetic package load against the equivalent
    physical package load in a separate bench.

Shape:
    - 5 synthetic modules
    - 4 mock classes per module
    - 20 objects built through one runner module

This is a directional performance bench, not a production benchmark harness.
"""

import importlib
import statistics
import sys
import time
from typing import Iterable, List

from synthetic_module_import_testbench import (
    SyntheticModuleLoader,
    SyntheticModuleRecord,
)


TRIALS = 60
WARM_TRIALS = 1000
PACKAGE_NAME = "synthetic_load_perf_pkg"
CLASSES_PER_MODULE = 4
MODULE_COUNT = 5
EXPECTED_OBJECTS = CLASSES_PER_MODULE * MODULE_COUNT


def _build_module_source(module_index: int) -> str:
    """
    Build one synthetic module source string containing four simple classes.
    """
    lines: List[str] = []
    for class_index in range(CLASSES_PER_MODULE):
        global_index = (module_index * CLASSES_PER_MODULE) + class_index
        lines.extend(
            (
                "class PerfThing{0}:\n".format(global_index),
                "    def __init__(self) -> None:\n",
                "        self.value = {0}\n".format(global_index),
                "\n",
                "    def read(self) -> int:\n",
                "        return self.value\n",
                "\n",
            )
        )
    return "".join(lines)


def _build_runner_source() -> str:
    """
    Build the synthetic runner that imports all five modules and instantiates all objects.
    """
    import_lines: List[str] = []
    body_lines: List[str] = [
        "def build_objects() -> list[object]:\n",
        "    objects = []\n",
    ]

    for module_index in range(MODULE_COUNT):
        import_lines.append(
            "from {0}.module_{1} import *\n".format(PACKAGE_NAME, module_index)
        )
        for class_index in range(CLASSES_PER_MODULE):
            global_index = (module_index * CLASSES_PER_MODULE) + class_index
            body_lines.append(
                "    objects.append(PerfThing{0}())\n".format(global_index)
            )

    body_lines.extend(
        (
            "    return objects\n",
            "\n",
            "def checksum(objects: list[object]) -> int:\n",
            "    return sum(object_instance.read() for object_instance in objects)\n",
        )
    )
    return "".join(import_lines + ["\n"] + body_lines)


def _build_records() -> Iterable[SyntheticModuleRecord]:
    """
    Build the full synthetic package graph for the benchmark.
    """
    records: List[SyntheticModuleRecord] = [
        SyntheticModuleRecord(
            module_name=PACKAGE_NAME,
            source_text="PACKAGE_NAME = '{0}'\n".format(PACKAGE_NAME),
            is_package=True,
        )
    ]
    for module_index in range(MODULE_COUNT):
        records.append(
            SyntheticModuleRecord(
                module_name="{0}.module_{1}".format(PACKAGE_NAME, module_index),
                parent_name=PACKAGE_NAME,
                source_text=_build_module_source(module_index),
            )
        )
    records.append(
        SyntheticModuleRecord(
            module_name="{0}.runner".format(PACKAGE_NAME),
            parent_name=PACKAGE_NAME,
            source_text=_build_runner_source(),
        )
    )
    return records


def _clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove cached synthetic modules for one package prefix from sys.modules.
    """
    stale_names = [
        module_name
        for module_name in list(sys.modules.keys())
        if module_name == prefix or module_name.startswith(prefix + ".")
    ]
    for module_name in sorted(stale_names, reverse=True):
        parent_name, _, child_name = module_name.rpartition(".")
        if parent_name:
            parent_module = sys.modules.get(parent_name)
            if parent_module is not None and hasattr(parent_module, child_name):
                try:
                    delattr(parent_module, child_name)
                except AttributeError:
                    pass
        sys.modules.pop(module_name, None)


def _run_trial(records: Iterable[SyntheticModuleRecord]) -> float:
    """
    Run one synthetic import + build_objects trial and return elapsed milliseconds.
    """
    _clear_modules_by_prefix(PACKAGE_NAME)
    loader = SyntheticModuleLoader()
    start = time.perf_counter()
    try:
        loader.register_records(records)
        loader.install_import_hook()
        runner = importlib.import_module("{0}.runner".format(PACKAGE_NAME))
        objects = runner.build_objects()
        checksum = runner.checksum(objects)
    finally:
        loader.unload_all()
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    if len(objects) != EXPECTED_OBJECTS:
        raise AssertionError(
            "synthetic bench expected {0} objects, got {1}".format(
                EXPECTED_OBJECTS,
                len(objects),
            )
        )
    expected_checksum = sum(range(EXPECTED_OBJECTS))
    if checksum != expected_checksum:
        raise AssertionError(
            "synthetic bench checksum mismatch: expected {0}, got {1}".format(
                expected_checksum,
                checksum,
            )
        )
    return elapsed_ms


def _run_warm_trial(runner: object) -> float:
    """
    Run one warm build_objects call with modules already loaded.
    """
    start = time.perf_counter()
    objects = runner.build_objects()
    checksum = runner.checksum(objects)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    if len(objects) != EXPECTED_OBJECTS:
        raise AssertionError(
            "synthetic warm bench expected {0} objects, got {1}".format(
                EXPECTED_OBJECTS,
                len(objects),
            )
        )
    expected_checksum = sum(range(EXPECTED_OBJECTS))
    if checksum != expected_checksum:
        raise AssertionError(
            "synthetic warm bench checksum mismatch: expected {0}, got {1}".format(
                expected_checksum,
                checksum,
            )
        )
    return elapsed_ms


def _run_bench() -> None:
    """
    Execute the full synthetic load benchmark.
    """
    records = tuple(_build_records())
    timings: List[float] = []
    for _ in range(TRIALS):
        timings.append(_run_trial(records))
    _clear_modules_by_prefix(PACKAGE_NAME)
    warm_loader = SyntheticModuleLoader()
    try:
        warm_loader.register_records(records)
        warm_loader.install_import_hook()
        warm_runner = importlib.import_module("{0}.runner".format(PACKAGE_NAME))
        warm_timings: List[float] = []
        for _ in range(WARM_TRIALS):
            warm_timings.append(_run_warm_trial(warm_runner))
    finally:
        warm_loader.unload_all()
    print("START_SYNTHETIC_MODULE_LOAD_PERF")
    print("BENCH_KIND\tsynthetic")
    print("MODULE_COUNT\t{0}".format(MODULE_COUNT))
    print("OBJECT_COUNT\t{0}".format(EXPECTED_OBJECTS))
    print("TRIALS\t{0}".format(TRIALS))
    print("AVG_MS\t{0:.6f}".format(statistics.mean(timings)))
    print("MEDIAN_MS\t{0:.6f}".format(statistics.median(timings)))
    print("MIN_MS\t{0:.6f}".format(min(timings)))
    print("MAX_MS\t{0:.6f}".format(max(timings)))
    print("WARM_TRIALS\t{0}".format(WARM_TRIALS))
    print("WARM_AVG_MS\t{0:.6f}".format(statistics.mean(warm_timings)))
    print("WARM_MEDIAN_MS\t{0:.6f}".format(statistics.median(warm_timings)))
    print("WARM_MIN_MS\t{0:.6f}".format(min(warm_timings)))
    print("WARM_MAX_MS\t{0:.6f}".format(max(warm_timings)))
    print("OK_SYNTHETIC_MODULE_LOAD_PERF")


if __name__ == "__main__":
    _run_bench()
