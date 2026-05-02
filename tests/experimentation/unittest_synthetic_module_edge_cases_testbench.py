"""
Experiment deeper same-process unittest edge cases against synthetic modules.

Purpose:
    Exercise the synthetic-module seams that the first unittest bench did not
    cover:
    - circular imports
    - larger package graphs
    - aggressive patching/mocking across module graphs
    - richer unittest features
    - concurrent import/use cycles
    - deactivate/reactivate/reload behavior
    - collision and authority behavior
    - file-backed morph interaction
    - larger unload/cleanup scale

This is an experimentation bench, not production runtime code.
"""

import faulthandler
import gc
import importlib
import io
import os
import shutil
import sys
import threading
import unittest
import uuid
import weakref
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set
from unittest.mock import patch

from unittest_synthetic_module_testbench import (
    SyntheticModuleLoader,
    SyntheticModuleRecord,
    _run_suite,
)


EXPERIMENT_TIMEOUT_SECONDS = 15.0


def _clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove cached modules for one dotted-name prefix from sys.modules.
    """
    stale_names = [
        module_name
        for module_name in list(sys.modules.keys())
        if module_name == prefix or module_name.startswith(prefix + ".")
    ]
    for module_name in stale_names:
        sys.modules.pop(module_name, None)


def _create_workspace_temp_dir(prefix: str) -> Path:
    """
    Create one deterministic scratch directory inside the experiment folder.
    """
    temp_root = Path(__file__).resolve().parent / "_synthetic_edge_tmp"
    temp_root.mkdir(exist_ok=True)
    temp_dir = temp_root / "{0}_{1}".format(prefix, uuid.uuid4().hex)
    temp_dir.mkdir()
    return temp_dir


def _emit_marker(marker: str) -> None:
    """
    Write one unbuffered progress marker for long-running bench steps.
    """
    sys.stdout.write(marker + "\n")
    sys.stdout.flush()


def _run_with_timeout(
        label: str,
        func: Callable[[], None],
        timeout_seconds: float = EXPERIMENT_TIMEOUT_SECONDS,
) -> None:
    """
    Run one experiment on the main thread with a hard watchdog timer.
    """
    def watchdog() -> None:
        sys.stderr.write(
            "TIMEOUT_{0}_{1:.1f}s\n".format(
                label,
                timeout_seconds,
            )
        )
        faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
        sys.stderr.flush()
        os._exit(124)

    _emit_marker("START_{0}".format(label))
    timer = threading.Timer(
        timeout_seconds,
        watchdog,
    )
    timer.daemon = True
    timer.start()
    try:
        func()
    finally:
        timer.cancel()
    _emit_marker("DONE_{0}".format(label))


def _circular_import_experiment() -> None:
    """
    Prove circular synthetic imports and package-init participation work.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_edge_circular",
                    source_text=(
                        "from . import module_a\n"
                        "PACKAGE_READY = True\n"
                    ),
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_circular.module_a",
                    parent_name="synthetic_edge_circular",
                    source_text=(
                        "from synthetic_edge_circular import module_b\n"
                        "VALUE_A = 'A'\n"
                        "\n"
                        "def pair() -> str:\n"
                        "    return VALUE_A + module_b.VALUE_B\n"
                    ),
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_circular.module_b",
                    parent_name="synthetic_edge_circular",
                    source_text=(
                        "from synthetic_edge_circular import module_a\n"
                        "VALUE_B = 'B'\n"
                        "\n"
                        "def pair() -> str:\n"
                        "    return module_a.VALUE_A + VALUE_B\n"
                    ),
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_circular.tests_runtime",
                    parent_name="synthetic_edge_circular",
                    source_text=(
                        "import importlib\n"
                        "import unittest\n"
                        "from synthetic_edge_circular import module_a, module_b\n"
                        "\n"
                        "class CircularImportTests(unittest.TestCase):\n"
                        "    def test_module_a_reads_module_b(self) -> None:\n"
                        "        self.assertEqual(module_a.pair(), 'AB')\n"
                        "\n"
                        "    def test_module_b_reads_module_a(self) -> None:\n"
                        "        self.assertEqual(module_b.pair(), 'AB')\n"
                        "\n"
                        "    def test_package_init_circularity(self) -> None:\n"
                        "        package = importlib.import_module('synthetic_edge_circular')\n"
                        "        self.assertTrue(package.PACKAGE_READY)\n"
                        "        self.assertIs(package.module_a, module_a)\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        suite = unittest.defaultTestLoader.loadTestsFromName(
            "synthetic_edge_circular.tests_runtime"
        )
        _run_suite(
            "UNITTEST_SYNTH_EDGE_CIRCULAR_IMPORTS",
            suite,
            expected_tests=3,
        )
    finally:
        loader.unload_all()


def _large_graph_and_cleanup_scale_experiment() -> None:
    """
    Prove a larger synthetic graph can load and unload cleanly.
    """
    loader = SyntheticModuleLoader()
    root_name = "synthetic_edge_scale"
    branch_count = 8
    leaf_count = 8
    all_module_names: List[str] = [root_name]
    total_expected = 0

    records: List[SyntheticModuleRecord] = [
        SyntheticModuleRecord(
            module_name=root_name,
            source_text="PACKAGE_NAME = 'synthetic_edge_scale'\n",
            is_package=True,
        )
    ]

    for branch_index in range(branch_count):
        branch_name = "{0}.branch_{1}".format(root_name, branch_index)
        all_module_names.append(branch_name)
        records.append(
            SyntheticModuleRecord(
                module_name=branch_name,
                parent_name=root_name,
                source_text="BRANCH_INDEX = {0}\n".format(branch_index),
                is_package=True,
            )
        )

        leaf_import_lines: List[str] = []
        sum_terms: List[str] = []
        for leaf_index in range(leaf_count):
            leaf_name = "{0}.leaf_{1}".format(branch_name, leaf_index)
            leaf_alias = "leaf_{0}".format(leaf_index)
            all_module_names.append(leaf_name)
            value = (branch_index * 100) + leaf_index
            total_expected += value
            records.append(
                SyntheticModuleRecord(
                    module_name=leaf_name,
                    parent_name=branch_name,
                    source_text=(
                        "VALUE = {0}\n"
                        "\n"
                        "def read() -> int:\n"
                        "    return VALUE\n"
                    ).format(value),
                )
            )
            leaf_import_lines.append(
                "from {0} import read as {1}_read\n".format(leaf_name, leaf_alias)
            )
            sum_terms.append("{0}_read()".format(leaf_alias))

        aggregate_name = "{0}.aggregate".format(branch_name)
        all_module_names.append(aggregate_name)
        records.append(
            SyntheticModuleRecord(
                module_name=aggregate_name,
                parent_name=branch_name,
                source_text=(
                    "".join(leaf_import_lines)
                    + "\n"
                    + "def branch_total() -> int:\n"
                    + "    return {0}\n".format(" + ".join(sum_terms))
                ),
            )
        )

    consumer_imports: List[str] = []
    consumer_terms: List[str] = []
    for branch_index in range(branch_count):
        aggregate_name = "{0}.branch_{1}.aggregate".format(root_name, branch_index)
        consumer_imports.append(
            "from {0} import branch_total as branch_{1}_total\n".format(
                aggregate_name,
                branch_index,
            )
        )
        consumer_terms.append("branch_{0}_total()".format(branch_index))

    consumer_name = "{0}.consumer".format(root_name)
    test_name = "{0}.tests_runtime".format(root_name)
    all_module_names.extend((consumer_name, test_name))
    records.extend(
        (
            SyntheticModuleRecord(
                module_name=consumer_name,
                parent_name=root_name,
                source_text=(
                    "".join(consumer_imports)
                    + "\n"
                    + "def total() -> int:\n"
                    + "    return {0}\n".format(" + ".join(consumer_terms))
                ),
            ),
            SyntheticModuleRecord(
                module_name=test_name,
                parent_name=root_name,
                source_text=(
                    "import unittest\n"
                    "from synthetic_edge_scale.consumer import total\n"
                    "\n"
                    "class LargeGraphTests(unittest.TestCase):\n"
                    "    def test_large_graph_total(self) -> None:\n"
                    "        self.assertEqual(total(), {0})\n"
                ).format(total_expected),
            ),
        )
    )

    weak_module_refs: List[weakref.ReferenceType[object]] = []
    try:
        loader.register_records(records)
        loader.install_import_hook()
        suite = unittest.defaultTestLoader.loadTestsFromName(test_name)
        _run_suite(
            "UNITTEST_SYNTH_EDGE_LARGE_GRAPH",
            suite,
            expected_tests=1,
        )
        loaded_modules = [
            sys.modules[module_name]
            for module_name in all_module_names
            if module_name in sys.modules
        ]
        if len(loaded_modules) != len(all_module_names):
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_LARGE_GRAPH expected {0} loaded modules, got {1}.".format(
                    len(all_module_names),
                    len(loaded_modules),
                )
            )
        weak_module_refs = [weakref.ref(module) for module in loaded_modules]
    finally:
        loader.unload_all()

    loaded_modules = []
    gc.collect()
    leaked_module_names = [
        module_name
        for module_name in all_module_names
        if module_name in sys.modules
    ]
    if leaked_module_names:
        raise AssertionError(
            "UNITTEST_SYNTH_EDGE_SCALE_CLEANUP leaked modules in sys.modules: {0}".format(
                leaked_module_names
            )
        )
    if any(reference() is not None for reference in weak_module_refs):
        raise AssertionError(
            "UNITTEST_SYNTH_EDGE_SCALE_CLEANUP retained module objects after unload."
        )
    print("OK_UNITTEST_SYNTH_EDGE_SCALE_CLEANUP")


def _aggressive_patching_experiment() -> None:
    """
    Prove stacked patches across siblings and package-level access work.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_edge_patch",
                    source_text="from .service_c import compute as package_compute\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_patch.service_a",
                    parent_name="synthetic_edge_patch",
                    source_text="def compute() -> int:\n    return 5\n",
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_patch.service_b",
                    parent_name="synthetic_edge_patch",
                    source_text="def compute() -> int:\n    return 7\n",
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_patch.service_c",
                    parent_name="synthetic_edge_patch",
                    source_text="def compute() -> int:\n    return 11\n",
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_patch.aggregator",
                    parent_name="synthetic_edge_patch",
                    source_text=(
                        "import synthetic_edge_patch as package_root\n"
                        "from synthetic_edge_patch import service_a, service_b\n"
                        "\n"
                        "def total() -> int:\n"
                        "    return service_a.compute() + service_b.compute() + package_root.package_compute()\n"
                    ),
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_patch.tests_runtime",
                    parent_name="synthetic_edge_patch",
                    source_text=(
                        "import unittest\n"
                        "from unittest.mock import patch\n"
                        "import synthetic_edge_patch as package_root\n"
                        "from synthetic_edge_patch import aggregator, service_a, service_b\n"
                        "\n"
                        "class AggressivePatchTests(unittest.TestCase):\n"
                        "    def test_stacked_patches(self) -> None:\n"
                        "        with patch.object(service_a, 'compute', return_value=10), \\\n"
                        "             patch.object(service_b, 'compute', return_value=20), \\\n"
                        "             patch.object(package_root, 'package_compute', return_value=12):\n"
                        "            self.assertEqual(aggregator.total(), 42)\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        suite = unittest.defaultTestLoader.loadTestsFromName(
            "synthetic_edge_patch.tests_runtime"
        )
        _run_suite(
            "UNITTEST_SYNTH_EDGE_AGGRESSIVE_PATCHING",
            suite,
            expected_tests=1,
        )
    finally:
        loader.unload_all()


def _rich_unittest_features_experiment() -> None:
    """
    Prove richer unittest features behave sensibly on synthetic modules.
    """
    class RecordingResult(unittest.TextTestResult):
        """
        Count successful subtests for one run.
        """

        def __init__(
                self,
                stream: io.StringIO,
                descriptions: bool,
                verbosity: int,
        ) -> None:
            super().__init__(stream, descriptions, verbosity)
            self.successful_subtests = 0

        def addSubTest(
                self,
                test: unittest.TestCase,
                subtest: unittest.TestCase,
                err: Optional[object],
        ) -> None:
            super().addSubTest(test, subtest, err)
            if err is None:
                self.successful_subtests += 1

    loader = SyntheticModuleLoader()
    try:
        loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_edge_features",
                source_text=(
                    "import unittest\n"
                    "\n"
                    "class CustomLoader(unittest.TestLoader):\n"
                    "    pass\n"
                    "\n"
                    "def build_suite() -> unittest.TestSuite:\n"
                    "    loader = CustomLoader()\n"
                    "    return unittest.TestSuite([\n"
                    "        loader.loadTestsFromTestCase(RichFeatureTests),\n"
                    "    ])\n"
                    "\n"
                    "class RichFeatureTests(unittest.TestCase):\n"
                    "    def test_subtests(self) -> None:\n"
                    "        for value in (40, 41, 42):\n"
                    "            with self.subTest(value=value):\n"
                    "                self.assertLessEqual(value, 42)\n"
                    "\n"
                    "    @unittest.skipIf(False, 'skipIf false should execute')\n"
                    "    def test_skipif_false(self) -> None:\n"
                    "        self.assertTrue(True)\n"
                    "\n"
                    "    @unittest.skip('synthetic skip path')\n"
                    "    def test_skipped(self) -> None:\n"
                    "        self.fail('skip should prevent execution')\n"
                    "\n"
                    "    @unittest.expectedFailure\n"
                    "    def test_expected_failure(self) -> None:\n"
                    "        self.assertEqual(1, 2)\n"
                ),
            )
        )
        module = importlib.import_module("synthetic_edge_features")
        suite = module.build_suite()
        stream = io.StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2,
            resultclass=RecordingResult,
        )
        result = runner.run(suite)
        if result.testsRun != 4:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_FEATURES ran {0} tests, expected 4.\nOUTPUT:\n{1}".format(
                    result.testsRun,
                    stream.getvalue(),
                )
            )
        if len(result.skipped) != 1:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_FEATURES expected 1 skipped test.\nOUTPUT:\n{0}".format(
                    stream.getvalue()
                )
            )
        if len(result.expectedFailures) != 1:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_FEATURES expected 1 expected failure.\nOUTPUT:\n{0}".format(
                    stream.getvalue()
                )
            )
        if result.successful_subtests != 3:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_FEATURES expected 3 successful subtests, got {0}.\nOUTPUT:\n{1}".format(
                    result.successful_subtests,
                    stream.getvalue(),
                )
            )
        if not result.wasSuccessful():
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_FEATURES did not end successfully.\nOUTPUT:\n{0}".format(
                    stream.getvalue()
                )
            )
        print("OK_UNITTEST_SYNTH_EDGE_FEATURES")
    finally:
        loader.unload_all()


def _concurrent_import_cycle_experiment() -> None:
    """
    Stress repeated same-process imports from multiple threads.
    """
    loader = SyntheticModuleLoader()
    module_ids: Set[int] = set()
    lock = threading.Lock()
    thread_errors: List[str] = []

    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_edge_concurrent",
                    source_text="PACKAGE_NAME = 'synthetic_edge_concurrent'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_concurrent.helper",
                    parent_name="synthetic_edge_concurrent",
                    source_text="def answer() -> int:\n    return 42\n",
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_edge_concurrent.worker",
                    parent_name="synthetic_edge_concurrent",
                    source_text=(
                        "from synthetic_edge_concurrent.helper import answer\n"
                        "\n"
                        "def run() -> int:\n"
                        "    return answer()\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        start_barrier = threading.Barrier(9)

        def worker() -> None:
            try:
                start_barrier.wait(timeout=2.0)
                for _ in range(50):
                    module = importlib.import_module("synthetic_edge_concurrent.worker")
                    value = module.run()
                    with lock:
                        module_ids.add(id(module))
                    if value != 42:
                        raise AssertionError(
                            "synthetic_edge_concurrent.worker returned {0}".format(value)
                        )
            except Exception as exc:
                with lock:
                    thread_errors.append(str(exc))

        threads = [
            threading.Thread(target=worker, daemon=True)
            for _ in range(8)
        ]
        for thread in threads:
            thread.start()
        start_barrier.wait(timeout=2.0)
        for thread in threads:
            thread.join(timeout=5.0)
            if thread.is_alive():
                raise AssertionError(
                    "UNITTEST_SYNTH_EDGE_CONCURRENT thread did not finish."
                )
        if thread_errors:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_CONCURRENT errors: {0}".format(thread_errors)
            )
        if len(module_ids) != 1:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_CONCURRENT expected 1 worker module identity, got {0}.".format(
                    len(module_ids)
                )
            )
        print("OK_UNITTEST_SYNTH_EDGE_CONCURRENT")
    finally:
        loader.unload_all()


def _reactivation_reload_experiment() -> None:
    """
    Prove unload/re-register/reactivate resets module identity and state.
    """
    loader = SyntheticModuleLoader()
    target_record = SyntheticModuleRecord(
        module_name="synthetic_edge_reload",
        source_text=(
            "COUNTER = 0\n"
            "\n"
            "def increment() -> int:\n"
            "    global COUNTER\n"
            "    COUNTER += 1\n"
            "    return COUNTER\n"
        ),
    )
    test_record = SyntheticModuleRecord(
        module_name="synthetic_edge_reload_tests",
        source_text=(
            "import unittest\n"
            "from synthetic_edge_reload import increment\n"
            "\n"
            "class ReloadTests(unittest.TestCase):\n"
            "    def test_increment(self) -> None:\n"
            "        self.assertEqual(increment(), 1)\n"
        ),
    )

    try:
        loader.register_record(target_record)
        first_module = loader.materialize(target_record)
        if first_module.increment() != 1:
            raise AssertionError("UNITTEST_SYNTH_EDGE_REACTIVATE first increment failed.")
        with patch.object(first_module, "increment", return_value=99):
            if first_module.increment() != 99:
                raise AssertionError("UNITTEST_SYNTH_EDGE_REACTIVATE patch did not apply.")

        first_id = id(first_module)
        loader.unload_all()

        loader.register_records((target_record, test_record))
        loader.install_import_hook()
        second_module = importlib.import_module("synthetic_edge_reload")
        if id(second_module) == first_id:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_REACTIVATE reused the old module identity."
            )
        if second_module.COUNTER != 0:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_REACTIVATE did not reset module state after reactivation."
            )
        suite = unittest.defaultTestLoader.loadTestsFromName(
            "synthetic_edge_reload_tests"
        )
        _run_suite(
            "UNITTEST_SYNTH_EDGE_REACTIVATE",
            suite,
            expected_tests=1,
        )
    finally:
        loader.unload_all()


def _collision_authority_experiment() -> None:
    """
    Exercise physical-vs-synthetic authority and duplicate synthetic names.
    """
    _emit_marker("COLLISION_STEP_FUNCTION_ENTER")
    module_name = "synthetic_edge_collision_target"
    duplicate_name = "synthetic_edge_duplicate_target"
    loader = SyntheticModuleLoader()

    _emit_marker("COLLISION_STEP_TEMP_DIR_START")
    temp_path = _create_workspace_temp_dir("collision")
    _emit_marker("COLLISION_STEP_TEMP_DIR_DONE")
    try:
        physical_file = temp_path / (module_name + ".py")
        physical_file.write_text("VALUE = 'physical'\n", encoding="utf-8")
        sys.path.insert(0, str(temp_path))
        importlib.invalidate_caches()

        _emit_marker("COLLISION_STEP_PHYSICAL_IMPORT_START")
        physical_module = importlib.import_module(module_name)
        _emit_marker("COLLISION_STEP_PHYSICAL_IMPORT_DONE")
        if physical_module.VALUE != "physical":
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_COLLISION did not load the physical module first."
            )

        loader.register_record(
            SyntheticModuleRecord(
                module_name=module_name,
                source_text="VALUE = 'synthetic'\n",
            )
        )
        loader.install_import_hook()
        _emit_marker("COLLISION_STEP_CACHED_IMPORT_START")
        cached_module = importlib.import_module(module_name)
        _emit_marker("COLLISION_STEP_CACHED_IMPORT_DONE")
        if cached_module.VALUE != "physical":
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_COLLISION expected sys.modules cache to win first."
            )

        sys.modules.pop(module_name, None)
        _emit_marker("COLLISION_STEP_SYNTHETIC_IMPORT_START")
        synthetic_module = importlib.import_module(module_name)
        _emit_marker("COLLISION_STEP_SYNTHETIC_IMPORT_DONE")
        if synthetic_module.VALUE != "synthetic":
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_COLLISION expected synthetic loader to win after cache clear."
            )

        loader.unload_all()
        _emit_marker("COLLISION_STEP_DUPLICATE_REGISTER_START")
        loader.register_record(
            SyntheticModuleRecord(
                module_name=duplicate_name,
                source_text="VALUE = 'first'\n",
            )
        )
        loader.register_record(
            SyntheticModuleRecord(
                module_name=duplicate_name,
                source_text="VALUE = 'second'\n",
            )
        )
        loader.install_import_hook()
        _emit_marker("COLLISION_STEP_DUPLICATE_IMPORT_START")
        duplicate_module = importlib.import_module(duplicate_name)
        _emit_marker("COLLISION_STEP_DUPLICATE_IMPORT_DONE")
        if duplicate_module.VALUE != "second":
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_COLLISION expected last synthetic record to win duplicate registration."
            )
        loader.unload_all()

        sys.modules.pop(module_name, None)
        importlib.invalidate_caches()
        _emit_marker("COLLISION_STEP_PHYSICAL_REIMPORT_START")
        physical_again = importlib.import_module(module_name)
        _emit_marker("COLLISION_STEP_PHYSICAL_REIMPORT_DONE")
        if physical_again.VALUE != "physical":
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_COLLISION expected physical module to return after synthetic unload."
            )
        print("OK_UNITTEST_SYNTH_EDGE_COLLISION")
    finally:
        loader.unload_all()
        _clear_modules_by_prefix(module_name)
        _clear_modules_by_prefix(duplicate_name)
        if str(temp_path) in sys.path:
            sys.path.remove(str(temp_path))
        importlib.invalidate_caches()
        shutil.rmtree(temp_path, ignore_errors=True)


def _file_backed_morph_experiment() -> None:
    """
    Simulate physical -> synthetic -> physical module projection.
    """
    package_name = "synthetic_edge_morph"
    loader = SyntheticModuleLoader()

    root = _create_workspace_temp_dir("morph")
    try:
        package_dir = root / package_name
        package_dir.mkdir()

        (package_dir / "__init__.py").write_text(
            "PACKAGE_KIND = 'physical'\n",
            encoding="utf-8",
        )
        (package_dir / "helper.py").write_text(
            "def base_value() -> int:\n    return 41\n",
            encoding="utf-8",
        )
        physical_core_source = (
            "from .helper import base_value\n"
            "\n"
            "def compute() -> int:\n"
            "    return base_value() + 1\n"
        )
        synthetic_core_source = (
            "from .helper import base_value\n"
            "\n"
            "def compute() -> int:\n"
            "    return base_value() + 2\n"
        )
        (package_dir / "core.py").write_text(physical_core_source, encoding="utf-8")

        sys.path.insert(0, str(root))
        importlib.invalidate_caches()

        physical_core = importlib.import_module("{0}.core".format(package_name))
        if physical_core.compute() != 42:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_MORPH expected physical phase to return 42."
            )

        package_record = SyntheticModuleRecord(
            module_name=package_name,
            source_text="PACKAGE_KIND = 'synthetic'\n",
            is_package=True,
        )
        helper_record = SyntheticModuleRecord(
            module_name="{0}.helper".format(package_name),
            parent_name=package_name,
            source_text=(package_dir / "helper.py").read_text(encoding="utf-8"),
        )
        core_record = SyntheticModuleRecord(
            module_name="{0}.core".format(package_name),
            parent_name=package_name,
            source_text=synthetic_core_source,
        )

        _clear_modules_by_prefix(package_name)
        loader.register_records((package_record, helper_record, core_record))
        loader.install_import_hook()
        synthetic_core = importlib.import_module("{0}.core".format(package_name))
        if synthetic_core.compute() != 43:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_MORPH expected synthetic phase to return 43."
            )

        loader.unload_all()
        _clear_modules_by_prefix(package_name)
        (package_dir / "core.py").write_text(synthetic_core_source, encoding="utf-8")
        shutil.rmtree(package_dir / "__pycache__", ignore_errors=True)
        importlib.invalidate_caches()
        physical_projected = importlib.import_module("{0}.core".format(package_name))
        if physical_projected.compute() != 43:
            raise AssertionError(
                "UNITTEST_SYNTH_EDGE_MORPH expected projected physical phase to return 43."
            )
        print("OK_UNITTEST_SYNTH_EDGE_MORPH")
    finally:
        loader.unload_all()
        _clear_modules_by_prefix(package_name)
        if str(root) in sys.path:
            sys.path.remove(str(root))
        importlib.invalidate_caches()
        shutil.rmtree(root, ignore_errors=True)


def _run_bench() -> None:
    """
    Execute the deeper synthetic-module unittest edge-case experiments.
    """
    _emit_marker("START_UNITTEST_SYNTHETIC_MODULE_EDGE_CASE_EXPERIMENTS")
    _run_with_timeout("UNITTEST_SYNTH_EDGE_CIRCULAR_IMPORTS_BLOCK", _circular_import_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_LARGE_GRAPH_BLOCK", _large_graph_and_cleanup_scale_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_AGGRESSIVE_PATCHING_BLOCK", _aggressive_patching_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_FEATURES_BLOCK", _rich_unittest_features_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_CONCURRENT_BLOCK", _concurrent_import_cycle_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_REACTIVATE_BLOCK", _reactivation_reload_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_COLLISION_BLOCK", _collision_authority_experiment)
    _run_with_timeout("UNITTEST_SYNTH_EDGE_MORPH_BLOCK", _file_backed_morph_experiment)
    _emit_marker("OK_UNITTEST_SYNTHETIC_MODULE_EDGE_CASE_EXPERIMENTS")


if __name__ == "__main__":
    _run_bench()
