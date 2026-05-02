"""
Experiment same-process pytest behavior against in-memory synthetic modules.

Purpose:
    Answer the question:
    "Can pytest use our synthetic modules in memory if we stay in one
    interpreter and let pytest run against that live runtime state?"

This bench tries three ideas:
    1. a physical bridge test file importing a preloaded synthetic helper
    2. a physical bridge test file re-exporting test functions from a preloaded
       synthetic module
    3. a same-process importlib/meta_path synthetic graph used by a bridge test
       file

This is an experimentation bench, not production runtime code.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Dict, Iterable, List, Optional

import pytest


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
    Minimal live synthetic module object used for the bench.
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


def _write(path: str, content: str) -> None:
    """
    Write UTF-8 text to one file path.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def _run_pytest_inprocess(test_target: str) -> int:
    """
    Run pytest in-process against one target path.
    """
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return pytest.main([test_target, "-q", "-s", "-p", "no:cacheprovider"])


def _prepare_synthetic_runtime() -> SyntheticModuleLoader:
    """
    Create the same-process synthetic module world used by every pytest idea.
    """
    loader = SyntheticModuleLoader()
    loader.materialize(
        SyntheticModuleRecord(
            module_name="synthetic_pytest_helper",
            source_text=(
                "def multiply(a: int, b: int) -> int:\n"
                "    return a * b\n"
            ),
        )
    )
    loader.materialize(
        SyntheticModuleRecord(
            module_name="synthetic_pytest_case",
            source_text=(
                "def test_synthetic_reexport() -> None:\n"
                "    assert (20 + 22) == 42\n"
                "    print('OK_PYTEST_SYNTH_REEXPORT')\n"
            ),
        )
    )
    loader.register_records(
        (
            SyntheticModuleRecord(
                module_name="synthetic_pytest_pkg",
                source_text="PACKAGE_NAME = 'synthetic_pytest_pkg'\n",
                is_package=True,
            ),
            SyntheticModuleRecord(
                module_name="synthetic_pytest_pkg.maths",
                parent_name="synthetic_pytest_pkg",
                source_text="def add(a: int, b: int) -> int:\n    return a + b\n",
            ),
            SyntheticModuleRecord(
                module_name="synthetic_pytest_pkg.logic",
                parent_name="synthetic_pytest_pkg",
                source_text=(
                    "from synthetic_pytest_pkg.maths import add\n"
                    "\n"
                    "def answer() -> int:\n"
                    "    return add(19, 23)\n"
                ),
            ),
        )
    )
    loader.install_import_hook()
    return loader


def _run_bench() -> None:
    """
    Execute the same-process pytest / synthetic-module experiments.
    """
    root = tempfile.mkdtemp(prefix="pytest_synth_experiment_", dir="C:\\tmp")
    loader: Optional[SyntheticModuleLoader] = None
    try:
        loader = _prepare_synthetic_runtime()
        _write(
            os.path.join(root, "test_bridge_import_helper.py"),
            "from synthetic_pytest_helper import multiply\n"
            "\n"
            "def test_bridge_import_helper() -> None:\n"
            "    assert multiply(6, 7) == 42\n"
            "    print('OK_PYTEST_SYNTH_BRIDGE_HELPER')\n",
        )
        _write(
            os.path.join(root, "test_bridge_reexport.py"),
            "from synthetic_pytest_case import *\n",
        )
        _write(
            os.path.join(root, "test_importlib_graph_runtime.py"),
            "from synthetic_pytest_pkg.logic import answer\n"
            "\n"
            "def test_importlib_graph_runtime() -> None:\n"
            "    assert answer() == 42\n"
            "    print('OK_PYTEST_SYNTH_IMPORTLIB_GRAPH')\n",
        )
        print("START_PYTEST_SYNTHETIC_MODULE_EXPERIMENTS")
        exit_code = _run_pytest_inprocess(root)
        if exit_code != 0:
            raise AssertionError(
                "same-process pytest synthetic-module experiments failed with exit code {0}".format(
                    exit_code
                )
            )
        print("OK_PYTEST_SYNTHETIC_MODULE_EXPERIMENTS")
    finally:
        if loader is not None:
            loader.unload_all()
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    _run_bench()
