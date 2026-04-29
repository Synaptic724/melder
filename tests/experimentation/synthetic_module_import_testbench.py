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
    - deep package/subpackage modules can re-export objects from deeper
      synthetic modules and still behave like normal Python imports
    - a synthetic ``meta_path`` finder/loader can materialize the dependency
      graph from an in-memory record registry without physical files
    - the graph can be cleaned back out of ``sys.modules`` deterministically

This is an experimentation bench, not production runtime code.
"""

import importlib
import importlib.abc
import importlib.util
import sys
from dataclasses import dataclass
from importlib.machinery import ModuleSpec
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


class SyntheticModuleFinder(importlib.abc.MetaPathFinder):
    """
    Finder that exposes registered synthetic module records to importlib.
    """

    def __init__(
            self,
            loader: "SyntheticModuleLoader",
    ) -> None:
        self._loader = loader

    def find_spec(
            self,
            fullname: str,
            path: object = None,
            target: object = None,
    ) -> Optional[ModuleSpec]:
        """
        Return a synthetic module spec when the loader owns the requested name.
        """
        return self._loader.find_spec(fullname)


class SyntheticModuleLoader:
    """
    Small manager that materializes synthetic modules into ``sys.modules``.

    The loader supports two experiment styles:
    - direct manual materialization
    - importlib-driven loading through a synthetic ``meta_path`` finder
    """

    def __init__(self) -> None:
        self._records_by_name: Dict[str, SyntheticModuleRecord] = {}
        self._modules_by_name: Dict[str, SyntheticModule] = {}
        self._load_order: List[str] = []
        self._finder: Optional[SyntheticModuleFinder] = None

    def register_record(
            self,
            record: SyntheticModuleRecord,
    ) -> None:
        """
        Register one synthetic module source record under its module name.
        """
        self._records_by_name[record.module_name] = record

    def register_records(
            self,
            records: Iterable[SyntheticModuleRecord],
    ) -> None:
        """
        Register many synthetic module source records.
        """
        for record in records:
            self.register_record(record)

    def find_spec(
            self,
            module_name: str,
    ) -> Optional[ModuleSpec]:
        """
        Build a module spec for one registered synthetic module name.
        """
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

    def create_module(
            self,
            spec: ModuleSpec,
    ) -> SyntheticModule:
        """
        Create one live synthetic module object for importlib.
        """
        existing_module = self._modules_by_name.get(spec.name)
        if existing_module is not None:
            return existing_module

        record = self._records_by_name[spec.name]
        module = SyntheticModule(record)
        self._modules_by_name[spec.name] = module
        if spec.name not in self._load_order:
            self._load_order.append(spec.name)
        return module

    def exec_module(
            self,
            module: ModuleType,
    ) -> None:
        """
        Execute one registered synthetic module into its live namespace.
        """
        record = self._records_by_name[module.__name__]
        if record.parent_name is not None:
            parent_module = sys.modules[record.parent_name]
            setattr(parent_module, record.module_name.rsplit(".", 1)[-1], module)
        exec(record.source_text, module.__dict__, module.__dict__)

    def materialize(
            self,
            record: SyntheticModuleRecord,
    ) -> SyntheticModule:
        """
        Materialize one synthetic record into a live module object.

        The module is inserted into ``sys.modules`` before executing the source
        so normal import semantics and circular references behave naturally.
        """
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
        """
        Install the synthetic finder at the front of ``sys.meta_path``.
        """
        if self._finder is not None:
            return
        self._finder = SyntheticModuleFinder(self)
        sys.meta_path.insert(0, self._finder)

    def remove_import_hook(self) -> None:
        """
        Remove the synthetic finder from ``sys.meta_path`` when installed.
        """
        finder = self._finder
        if finder is None:
            return
        sys.meta_path = [entry for entry in sys.meta_path if entry is not finder]
        self._finder = None

    def loaded_module_names(self) -> List[str]:
        """
        Return the currently tracked synthetic module names in load order.
        """
        return list(self._load_order)

    def unload_all(self) -> None:
        """
        Remove all bench-created modules from ``sys.modules`` in reverse order.
        """
        self.remove_import_hook()
        for module_name in reversed(self._load_order):
            sys.modules.pop(module_name, None)
            self._modules_by_name.pop(module_name, None)
        self._records_by_name.clear()
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
            module_name="synthetic_pkg.runtime",
            parent_name="synthetic_pkg",
            source_text="RUNTIME_NAME = 'runtime'\n",
            is_package=True,
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.runtime.primitives",
            parent_name="synthetic_pkg.runtime",
            source_text="PRIMITIVES_NAME = 'primitives'\n",
            is_package=True,
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.runtime.primitives.base",
            parent_name="synthetic_pkg.runtime.primitives",
            source_text=(
                "class DeepNumber:\n"
                "    def __init__(self, value: int) -> None:\n"
                "        self.value = value\n"
                "    def read(self) -> int:\n"
                "        return self.value\n"
            ),
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
                "from synthetic_pkg.runtime.primitives.base import DeepNumber\n"
                "\n"
                "class FeatureTool:\n"
                "    def __init__(self, seed: int) -> None:\n"
                "        self._helper = BaseHelper(seed)\n"
                "    def amplify(self, factor: int) -> int:\n"
                "        return self._helper.read() * factor\n"
                "\n"
                "def build_deep_number(value: int) -> DeepNumber:\n"
                "    return DeepNumber(value)\n"
            ),
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.api",
            parent_name="synthetic_pkg",
            source_text="API_NAME = 'api'\n",
            is_package=True,
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.api.v1",
            parent_name="synthetic_pkg.api",
            source_text="API_VERSION = 'v1'\n",
            is_package=True,
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.api.v1.surface",
            parent_name="synthetic_pkg.api.v1",
            source_text=(
                "from synthetic_pkg.feature import FeatureTool, build_deep_number\n"
                "from synthetic_pkg.runtime.primitives.base import DeepNumber\n"
                "\n"
                "DeepNumberAlias = DeepNumber\n"
                "\n"
                "def build_tool(seed: int) -> FeatureTool:\n"
                "    return FeatureTool(seed)\n"
                "\n"
                "def build_wrapped_value(seed: int, offset: int) -> int:\n"
                "    tool = build_tool(seed)\n"
                "    wrapped = build_deep_number(offset)\n"
                "    return tool.amplify(wrapped.read())\n"
            ),
        ),
        SyntheticModuleRecord(
            module_name="synthetic_pkg.consumer",
            parent_name="synthetic_pkg",
            source_text=(
                "from synthetic_pkg.api.v1.surface import (\n"
                "    DeepNumberAlias,\n"
                "    FeatureTool,\n"
                "    build_tool,\n"
                "    build_wrapped_value,\n"
                ")\n"
                "\n"
                "def build_result() -> int:\n"
                "    tool = build_tool(7)\n"
                "    deep_value = DeepNumberAlias(6)\n"
                "    return tool.amplify(deep_value.read())\n"
                "\n"
                "def build_surface_result() -> int:\n"
                "    return build_wrapped_value(5, 8)\n"
                "\n"
                "def build_direct_tool() -> FeatureTool:\n"
                "    return FeatureTool(9)\n"
            ),
        ),
    )


def _expected_loaded_module_names() -> List[str]:
    """
    Return the expected deep synthetic graph module set.
    """
    return [
        "synthetic_pkg",
        "synthetic_pkg.api",
        "synthetic_pkg.api.v1",
        "synthetic_pkg.api.v1.surface",
        "synthetic_pkg.base",
        "synthetic_pkg.consumer",
        "synthetic_pkg.feature",
        "synthetic_pkg.runtime",
        "synthetic_pkg.runtime.primitives",
        "synthetic_pkg.runtime.primitives.base",
    ]


def _assert_graph_behavior() -> None:
    """
    Assert the expected deep synthetic graph behavior for the current process.
    """
    consumer = importlib.import_module("synthetic_pkg.consumer")
    assert consumer.build_result() == 42
    assert consumer.build_surface_result() == 40

    feature = importlib.import_module("synthetic_pkg.feature")
    tool = feature.FeatureTool(9)
    assert tool.amplify(5) == 45

    surface = importlib.import_module("synthetic_pkg.api.v1.surface")
    runtime_base = importlib.import_module("synthetic_pkg.runtime.primitives.base")
    deep_tool = surface.build_tool(11)
    assert deep_tool.amplify(4) == 44
    assert surface.build_wrapped_value(3, 9) == 27
    assert surface.FeatureTool is feature.FeatureTool
    assert surface.DeepNumberAlias is runtime_base.DeepNumber
    assert consumer.build_direct_tool().amplify(2) == 18

    package = importlib.import_module("synthetic_pkg")
    assert package.PACKAGE_NAME == "synthetic_pkg"
    assert getattr(package, "feature") is feature
    assert getattr(package, "consumer") is consumer
    assert getattr(package, "runtime") is importlib.import_module("synthetic_pkg.runtime")
    assert getattr(package, "api") is importlib.import_module("synthetic_pkg.api")

    runtime_package = importlib.import_module("synthetic_pkg.runtime")
    primitives_package = importlib.import_module("synthetic_pkg.runtime.primitives")
    api_package = importlib.import_module("synthetic_pkg.api")
    api_v1_package = importlib.import_module("synthetic_pkg.api.v1")
    assert getattr(runtime_package, "primitives") is primitives_package
    assert getattr(primitives_package, "base") is runtime_base
    assert getattr(api_package, "v1") is api_v1_package
    assert getattr(api_v1_package, "surface") is surface


def _assert_graph_removed() -> None:
    """
    Assert the full synthetic graph is absent from ``sys.modules``.
    """
    for module_name in _expected_loaded_module_names():
        assert module_name not in sys.modules


def _print_loaded_modules(loader: SyntheticModuleLoader) -> None:
    """
    Print the loaded module list for bench visibility.
    """
    print("LOADED_MODULES")
    for module_name in sorted(loader.loaded_module_names()):
        print(module_name)


def _run_manual_materialization_bench() -> None:
    """
    Execute the direct materialization experiment.
    """
    loader = SyntheticModuleLoader()
    try:
        for record in _build_records():
            loader.materialize(record)

        assert sorted(loader.loaded_module_names()) == _expected_loaded_module_names()
        _assert_graph_behavior()

        print("OK_SYNTHETIC_MODULE_IMPORT_DEEP")
        _print_loaded_modules(loader)
    finally:
        loader.unload_all()
        _assert_graph_removed()


def _run_importlib_loader_bench() -> None:
    """
    Execute the importlib-driven synthetic loader experiment.
    """
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(_build_records())
        loader.install_import_hook()

        consumer = importlib.import_module("synthetic_pkg.consumer")
        assert consumer.build_result() == 42
        assert sorted(loader.loaded_module_names()) == _expected_loaded_module_names()
        _assert_graph_behavior()

        print("OK_SYNTHETIC_MODULE_IMPORT_DEEP_IMPORTLIB")
        _print_loaded_modules(loader)
    finally:
        loader.unload_all()
        _assert_graph_removed()


def _run_bench() -> None:
    """
    Execute both the direct and importlib-driven synthetic-module experiments.
    """
    _run_manual_materialization_bench()
    _run_importlib_loader_bench()


if __name__ == "__main__":
    _run_bench()
