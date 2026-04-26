"""
Experiment synthetic module import behavior inside one Python process.

Purpose:
    Provide a focused proof harness for the synthetic-module discussion.

What this bench proves:
    - a real module object can be created fully in memory
    - package and submodule shells can be registered into ``sys.modules``
    - one synthetic module can import another by normal Python import syntax
    - a later consumer module can import and instantiate exports from the
      synthetic module graph
    - the graph can be cleaned back out of ``sys.modules`` deterministically

This is an experimentation bench, not production runtime code.
"""

import importlib
import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Dict, Iterable, List, Optional


@dataclass(slots=True)
class SyntheticModuleRecord:
    """
    Describe one synthetic module source unit for this bench.

    Attributes:
        module_name:
            Fully qualified module name.
        source_text:
            Python source executed into the synthetic module namespace.
        is_package:
            True when the synthetic unit should behave like a package shell.
        parent_name:
            Optional parent package name.
    """

    module_name: str
    source_text: str
    is_package: bool = False
    parent_name: Optional[str] = None


class SyntheticModule(ModuleType):
    """
    Simple in-memory module object used by the bench.

    Purpose:
        Carry source and synthetic metadata directly on the live module object
        so later experiments can inspect what was materialized.
    """

    def __init__(
            self,
            record: SyntheticModuleRecord,
    ) -> None:
        super().__init__(record.module_name)
        self._synthetic_source_text: str = record.source_text
        self._synthetic_parent_name: Optional[str] = record.parent_name
        self._synthetic_is_package: bool = record.is_package
        self.__file__ = "<synthetic:{0}>".format(record.module_name)
        self.__package__ = (
            record.module_name
            if record.is_package
            else (record.parent_name or record.module_name.rpartition(".")[0])
        )
        if record.is_package:
            self.__path__ = [self.__file__]


class SyntheticModuleLoader:
    """
    Small manager that materializes synthetic modules into ``sys.modules``.
    """

    def __init__(self) -> None:
        self._modules_by_name: Dict[str, SyntheticModule] = {}
        self._load_order: List[str] = []

    def materialize(
            self,
            record: SyntheticModuleRecord,
    ) -> SyntheticModule:
        """
        Materialize one synthetic record into a live module object.

        The module is inserted into ``sys.modules`` before executing the source
        so normal import semantics and circular references behave naturally.
        """
        module = SyntheticModule(record)
        self._modules_by_name[record.module_name] = module
        self._load_order.append(record.module_name)
        sys.modules[record.module_name] = module
        if record.parent_name is not None:
            parent_module = sys.modules[record.parent_name]
            setattr(parent_module, record.module_name.rsplit(".", 1)[-1], module)
        exec(record.source_text, module.__dict__, module.__dict__)
        return module

    def unload_all(self) -> None:
        """
        Remove all bench-created modules from ``sys.modules`` in reverse order.
        """
        for module_name in reversed(self._load_order):
            sys.modules.pop(module_name, None)
        self._modules_by_name.clear()
        self._load_order.clear()


def _build_records() -> Iterable[SyntheticModuleRecord]:
    """
    Build the synthetic package and submodule graph for the bench.
    """
    return (
        SyntheticModuleRecord(
            module_name="synthetic_pkg",
            source_text="PACKAGE_NAME = 'synthetic_pkg'\n",
            is_package=True,
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.base",
            parent_name="synthetic_pkg",
            source_text=(
                "class BaseHelper:\n"
                "    def __init__(self, value: int) -> None:\n"
                "        self.value = value\n"
                "    def read(self) -> int:\n"
                "        return self.value\n"
            ),
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.feature",
            parent_name="synthetic_pkg",
            source_text=(
                "from synthetic_pkg.base import BaseHelper\n"
                "\n"
                "class FeatureTool:\n"
                "    def __init__(self, seed: int) -> None:\n"
                "        self._helper = BaseHelper(seed)\n"
                "    def amplify(self, factor: int) -> int:\n"
                "        return self._helper.read() * factor\n"
            ),
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.consumer",
            parent_name="synthetic_pkg",
            source_text=(
                "from synthetic_pkg.feature import FeatureTool\n"
                "\n"
                "def build_result() -> int:\n"
                "    tool = FeatureTool(7)\n"
                "    return tool.amplify(6)\n"
            ),
        ),
    )


def _run_bench() -> None:
    """
    Execute the synthetic-module experiment and assert the expected behavior.
    """
    loader = SyntheticModuleLoader()
    try:
        for record in _build_records():
            loader.materialize(record)

        consumer = importlib.import_module("synthetic_pkg.consumer")
        assert consumer.build_result() == 42

        feature = importlib.import_module("synthetic_pkg.feature")
        tool = feature.FeatureTool(9)
        assert tool.amplify(5) == 45

        package = importlib.import_module("synthetic_pkg")
        assert package.PACKAGE_NAME == "synthetic_pkg"
        assert getattr(package, "feature") is feature
        assert getattr(package, "consumer") is consumer

        print("OK_SYNTHETIC_MODULE_IMPORT")
        print("LOADED_MODULES")
        for module_name in sorted(loader._modules_by_name.keys()):
            print(module_name)
    finally:
        loader.unload_all()
        for module_name in (
                "synthetic_pkg",
                "synthetic_pkg.base",
                "synthetic_pkg.feature",
                "synthetic_pkg.consumer",
        ):
            assert module_name not in sys.modules


if __name__ == "__main__":
    _run_bench()
