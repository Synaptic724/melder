"""
Experiment same-process unittest behavior against live synthetic modules.

Purpose:
    Answer the question:
    "Can a lighter in-process test framework operate directly on synthetic
    modules without forcing us back into normal static file-first semantics?"

This bench tries three ideas:
    1. load tests directly from a synthetic module object
    2. load tests by fully qualified synthetic module name through a synthetic
       import hook
    3. use `unittest.mock` against a sibling synthetic module inside a package
       graph

This is an experimentation bench, not production runtime code.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.abc
import importlib.util
import io
import sys
import threading
import unittest
from dataclasses import dataclass
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Dict, Iterable, List, Optional


@dataclass(slots=True)
class SyntheticModuleRecord:
    """
    Describe one synthetic module source unit for this bench.
    """

    module_name: str
    source_text: str
    is_package: bool = False
    parent_name: Optional[str] = None


class SyntheticModule(ModuleType):
    """
    Minimal live synthetic module object used by the bench.
    """

    def __init__(self, record: SyntheticModuleRecord) -> None:
        super().__init__(record.module_name)
        self.__file__ = "<synthetic:{0}>".format(record.module_name)
        self.__package__ = (
            record.module_name
            if record.is_package
            else (record.parent_name or record.module_name.rpartition(".")[0])
        )
        if record.is_package:
            self.__path__ = [self.__file__]
        self._synthetic_source_text = record.source_text


class SyntheticModuleFinder(importlib.abc.MetaPathFinder):
    """
    Finder exposing registered synthetic module records to importlib.
    """

    def __init__(self, loader: "SyntheticModuleLoader") -> None:
        self._loader = loader

    def find_spec(
            self,
            fullname: str,
            path: object = None,
            target: object = None,
    ) -> Optional[ModuleSpec]:
        return self._loader.find_spec(fullname)


class SyntheticModuleLoader:
    """
    Small same-process synthetic module loader.
    """

    def __init__(self) -> None:
        self._records_by_name: Dict[str, SyntheticModuleRecord] = {}
        self._modules_by_name: Dict[str, SyntheticModule] = {}
        self._load_order: List[str] = []
        self._finder: Optional[SyntheticModuleFinder] = None

    def register_record(self, record: SyntheticModuleRecord) -> None:
        self._records_by_name[record.module_name] = record

    def register_records(self, records: Iterable[SyntheticModuleRecord]) -> None:
        for record in records:
            self.register_record(record)

    def find_spec(self, module_name: str) -> Optional[ModuleSpec]:
        record = self._records_by_name.get(module_name)
        if record is None:
            return None
        spec = importlib.util.spec_from_loader(
            module_name,
            self,
            is_package=record.is_package,
        )
        if spec is None:
            return None
        origin = "<synthetic:{0}>".format(module_name)
        spec.origin = origin
        if record.is_package:
            spec.submodule_search_locations = [origin]
        return spec

    def create_module(self, spec: ModuleSpec) -> SyntheticModule:
        existing = self._modules_by_name.get(spec.name)
        if existing is not None:
            return existing
        record = self._records_by_name[spec.name]
        module = SyntheticModule(record)
        self._modules_by_name[spec.name] = module
        if spec.name not in self._load_order:
            self._load_order.append(spec.name)
        return module

    def exec_module(self, module: ModuleType) -> None:
        record = self._records_by_name[module.__name__]
        if record.parent_name is not None:
            parent_module = sys.modules[record.parent_name]
            setattr(parent_module, record.module_name.rsplit(".", 1)[-1], module)
        exec(record.source_text, module.__dict__, module.__dict__)

    def materialize(self, record: SyntheticModuleRecord) -> SyntheticModule:
        self.register_record(record)
        spec = self.find_spec(record.module_name)
        if spec is None:
            raise RuntimeError(
                "Synthetic module spec could not be created for '{0}'.".format(
                    record.module_name
                )
            )
        module = self.create_module(spec)
        sys.modules[record.module_name] = module
        self.exec_module(module)
        return module

    def install_import_hook(self) -> None:
        if self._finder is not None:
            return
        self._finder = SyntheticModuleFinder(self)
        sys.meta_path.insert(0, self._finder)

    def remove_import_hook(self) -> None:
        finder = self._finder
        if finder is None:
            return
        sys.meta_path = [entry for entry in sys.meta_path if entry is not finder]
        self._finder = None

    def unload_all(self) -> None:
        self.remove_import_hook()
        for module_name in reversed(self._load_order):
            sys.modules.pop(module_name, None)
            self._modules_by_name.pop(module_name, None)
        self._records_by_name.clear()
        self._modules_by_name.clear()
        self._load_order.clear()


def _run_suite(label: str, suite: unittest.TestSuite, *, expected_tests: int) -> None:
    """
    Run one unittest suite and require success.
    """
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    if result.testsRun != expected_tests:
        raise AssertionError(
            "{0} ran {1} tests, expected {2}.\nOUTPUT:\n{3}".format(
                label,
                result.testsRun,
                expected_tests,
                stream.getvalue(),
            )
        )
    if not result.wasSuccessful():
        raise AssertionError(
            "{0} failed.\nOUTPUT:\n{1}".format(
                label,
                stream.getvalue(),
            )
        )
    print("OK_{0}".format(label))


def _direct_module_object_experiment() -> None:
    """
    Load tests directly from a synthetic module object already in memory.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_ut_helper",
                source_text=(
                    "def multiply(a: int, b: int) -> int:\n"
                    "    return a * b\n"
                ),
            )
        )
        test_module = loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_ut_case",
                source_text=(
                    "import unittest\n"
                    "from unittest.mock import MagicMock\n"
                    "from synthetic_ut_helper import multiply\n"
                    "\n"
                    "class SyntheticDirectTests(unittest.TestCase):\n"
                    "    def test_helper(self) -> None:\n"
                    "        self.assertEqual(multiply(6, 7), 42)\n"
                    "\n"
                    "    def test_mock(self) -> None:\n"
                    "        fake = MagicMock(return_value=42)\n"
                    "        self.assertEqual(fake('alpha'), 42)\n"
                    "        fake.assert_called_once_with('alpha')\n"
                ),
            )
        )
        suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
        _run_suite(
            "UNITTEST_SYNTH_DIRECT_MODULE",
            suite,
            expected_tests=2,
        )
    finally:
        loader.unload_all()


def _import_by_name_graph_experiment() -> None:
    """
    Load tests by fully qualified synthetic module name through the loader.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_ut_pkg",
                    source_text="PACKAGE_NAME = 'synthetic_ut_pkg'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_pkg.maths",
                    parent_name="synthetic_ut_pkg",
                    source_text="def add(a: int, b: int) -> int:\n    return a + b\n",
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_pkg.logic",
                    parent_name="synthetic_ut_pkg",
                    source_text=(
                        "from synthetic_ut_pkg.maths import add\n"
                        "\n"
                        "def answer() -> int:\n"
                        "    return add(19, 23)\n"
                    ),
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_pkg.tests_runtime",
                    parent_name="synthetic_ut_pkg",
                    source_text=(
                        "import unittest\n"
                        "from synthetic_ut_pkg.logic import answer\n"
                        "\n"
                        "class RuntimeGraphTests(unittest.TestCase):\n"
                        "    def test_answer(self) -> None:\n"
                        "        self.assertEqual(answer(), 42)\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        suite = unittest.defaultTestLoader.loadTestsFromName(
            "synthetic_ut_pkg.tests_runtime"
        )
        _run_suite(
            "UNITTEST_SYNTH_IMPORT_BY_NAME",
            suite,
            expected_tests=1,
        )
    finally:
        loader.unload_all()


def _mock_patch_sibling_experiment() -> None:
    """
    Use unittest.mock.patch.object against a sibling synthetic module.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_ut_patch_pkg",
                    source_text="PACKAGE_NAME = 'synthetic_ut_patch_pkg'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_patch_pkg.service",
                    parent_name="synthetic_ut_patch_pkg",
                    source_text=(
                        "def compute() -> int:\n"
                        "    return 21\n"
                    ),
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_patch_pkg.tests_patch",
                    parent_name="synthetic_ut_patch_pkg",
                    source_text=(
                        "import unittest\n"
                        "from unittest.mock import patch\n"
                        "from synthetic_ut_patch_pkg import service\n"
                        "\n"
                        "class PatchRuntimeTests(unittest.TestCase):\n"
                        "    def test_patch(self) -> None:\n"
                        "        with patch.object(service, 'compute', return_value=42):\n"
                        "            self.assertEqual(service.compute(), 42)\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        module = importlib.import_module("synthetic_ut_patch_pkg.tests_patch")
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        _run_suite(
            "UNITTEST_SYNTH_PATCH_SIBLING",
            suite,
            expected_tests=1,
        )
    finally:
        loader.unload_all()


def _relative_imports_experiment() -> None:
    """
    Use relative imports inside a synthetic package test module.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_ut_rel",
                    source_text="PACKAGE_NAME = 'synthetic_ut_rel'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_rel.helpers",
                    parent_name="synthetic_ut_rel",
                    source_text="def meaning() -> int:\n    return 42\n",
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_rel.tests_relative",
                    parent_name="synthetic_ut_rel",
                    source_text=(
                        "import unittest\n"
                        "from .helpers import meaning\n"
                        "\n"
                        "class RelativeImportTests(unittest.TestCase):\n"
                        "    def test_relative_import(self) -> None:\n"
                        "        self.assertEqual(meaning(), 42)\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        suite = unittest.defaultTestLoader.loadTestsFromName(
            "synthetic_ut_rel.tests_relative"
        )
        _run_suite(
            "UNITTEST_SYNTH_RELATIVE_IMPORTS",
            suite,
            expected_tests=1,
        )
    finally:
        loader.unload_all()


def _lifecycle_hooks_experiment() -> None:
    """
    Verify setUp/tearDown and class-level hooks on a synthetic test module.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_ut_lifecycle",
                source_text=(
                    "import unittest\n"
                    "\n"
                    "CALLS = []\n"
                    "\n"
                    "class LifecycleTests(unittest.TestCase):\n"
                    "    @classmethod\n"
                    "    def setUpClass(cls) -> None:\n"
                    "        CALLS.append('setUpClass')\n"
                    "\n"
                    "    @classmethod\n"
                    "    def tearDownClass(cls) -> None:\n"
                    "        CALLS.append('tearDownClass')\n"
                    "\n"
                    "    def setUp(self) -> None:\n"
                    "        CALLS.append('setUp')\n"
                    "\n"
                    "    def tearDown(self) -> None:\n"
                    "        CALLS.append('tearDown')\n"
                    "\n"
                    "    def test_one(self) -> None:\n"
                    "        self.assertTrue(True)\n"
                    "\n"
                    "    def test_two(self) -> None:\n"
                    "        self.assertEqual(40 + 2, 42)\n"
                ),
            )
        )
        module = importlib.import_module("synthetic_ut_lifecycle")
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        _run_suite(
            "UNITTEST_SYNTH_LIFECYCLE",
            suite,
            expected_tests=2,
        )
        expected = [
            "setUpClass",
            "setUp",
            "tearDown",
            "setUp",
            "tearDown",
            "tearDownClass",
        ]
        if module.CALLS != expected:
            raise AssertionError(
                "UNITTEST_SYNTH_LIFECYCLE unexpected hook order: {0}".format(
                    module.CALLS
                )
            )
        print("OK_UNITTEST_SYNTH_LIFECYCLE_ORDER")
    finally:
        loader.unload_all()


def _suite_composition_experiment() -> None:
    """
    Compose a suite from multiple synthetic modules in one package.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name="synthetic_ut_suite",
                    source_text="PACKAGE_NAME = 'synthetic_ut_suite'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_suite.test_alpha",
                    parent_name="synthetic_ut_suite",
                    source_text=(
                        "import unittest\n"
                        "class AlphaTests(unittest.TestCase):\n"
                        "    def test_alpha(self) -> None:\n"
                        "        self.assertEqual(21 * 2, 42)\n"
                    ),
                ),
                SyntheticModuleRecord(
                    module_name="synthetic_ut_suite.test_beta",
                    parent_name="synthetic_ut_suite",
                    source_text=(
                        "import unittest\n"
                        "class BetaTests(unittest.TestCase):\n"
                        "    def test_beta(self) -> None:\n"
                        "        self.assertEqual(84 // 2, 42)\n"
                    ),
                ),
            )
        )
        loader.install_import_hook()
        alpha = importlib.import_module("synthetic_ut_suite.test_alpha")
        beta = importlib.import_module("synthetic_ut_suite.test_beta")
        suite = unittest.TestSuite(
            [
                unittest.defaultTestLoader.loadTestsFromModule(alpha),
                unittest.defaultTestLoader.loadTestsFromModule(beta),
            ]
        )
        _run_suite(
            "UNITTEST_SYNTH_SUITE_COMPOSITION",
            suite,
            expected_tests=2,
        )
    finally:
        loader.unload_all()


def _failure_reporting_experiment() -> None:
    """
    Verify failure output still includes the synthetic module identity.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_ut_failure",
                source_text=(
                    "import unittest\n"
                    "class FailureTests(unittest.TestCase):\n"
                    "    def test_failure(self) -> None:\n"
                    "        self.assertEqual(1, 2)\n"
                ),
            )
        )
        module = importlib.import_module("synthetic_ut_failure")
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)
        output = stream.getvalue()
        if result.testsRun != 1 or len(result.failures) != 1:
            raise AssertionError(
                "UNITTEST_SYNTH_FAILURE_REPORTING did not produce one clean failure.\nOUTPUT:\n{0}".format(
                    output
                )
            )
        if "synthetic_ut_failure" not in output:
            raise AssertionError(
                "UNITTEST_SYNTH_FAILURE_REPORTING did not include synthetic module identity.\nOUTPUT:\n{0}".format(
                    output
                )
            )
        print("OK_UNITTEST_SYNTH_FAILURE_REPORTING")
    finally:
        loader.unload_all()


def _activation_deactivation_experiment() -> None:
    """
    Verify imports fail after synthetic module unload.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_ut_activation",
                source_text="VALUE = 42\n",
            )
        )
        importlib.import_module("synthetic_ut_activation")
        loader.unload_all()
        try:
            importlib.import_module("synthetic_ut_activation")
        except ModuleNotFoundError:
            print("OK_UNITTEST_SYNTH_DEACTIVATION")
            return
        raise AssertionError(
            "UNITTEST_SYNTH_DEACTIVATION expected ModuleNotFoundError after unload."
        )
    finally:
        loader.unload_all()


def _async_and_thread_probe_experiment() -> None:
    """
    Exercise one async call and one threaded import against a synthetic module.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.materialize(
            SyntheticModuleRecord(
                module_name="synthetic_ut_async_thread",
                source_text=(
                    "async def async_answer() -> int:\n"
                    "    return 42\n"
                    "\n"
                    "def sync_answer() -> int:\n"
                    "    return 42\n"
                ),
            )
        )
        module = importlib.import_module("synthetic_ut_async_thread")
        async_result = asyncio.run(module.async_answer())
        if async_result != 42:
            raise AssertionError("UNITTEST_SYNTH_ASYNC expected 42.")

        thread_result: list[int] = []

        def worker() -> None:
            imported = importlib.import_module("synthetic_ut_async_thread")
            thread_result.append(imported.sync_answer())

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join(timeout=2.0)
        if thread.is_alive():
            raise AssertionError("UNITTEST_SYNTH_THREAD import thread did not finish.")
        if thread_result != [42]:
            raise AssertionError(
                "UNITTEST_SYNTH_THREAD expected one threaded result of 42, got {0}".format(
                    thread_result
                )
            )
        print("OK_UNITTEST_SYNTH_ASYNC_THREAD")
    finally:
        loader.unload_all()


def _run_bench() -> None:
    """
    Execute the runtime unittest / synthetic-module experiments.
    """
    print("START_UNITTEST_SYNTHETIC_MODULE_EXPERIMENTS")
    _direct_module_object_experiment()
    _import_by_name_graph_experiment()
    _mock_patch_sibling_experiment()
    _relative_imports_experiment()
    _lifecycle_hooks_experiment()
    _suite_composition_experiment()
    _failure_reporting_experiment()
    _activation_deactivation_experiment()
    _async_and_thread_probe_experiment()
    print("OK_UNITTEST_SYNTHETIC_MODULE_EXPERIMENTS")


if __name__ == "__main__":
    _run_bench()
