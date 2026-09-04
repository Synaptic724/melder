"""Load standalone CI scripts without creating a runtime package or booting Melder."""

import importlib.util
import pathlib
from types import ModuleType

import pytest


def load_script(name: str) -> ModuleType:
    """Load one checked-in CI helper by path and return its public test surface."""
    root = pathlib.Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(name, root / ".github" / "scripts" / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load CI helper {name}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def policy() -> ModuleType:
    """Provide the real policy module with no external process execution at import."""
    return load_script("ci_policy")


@pytest.fixture
def distributions() -> ModuleType:
    """Provide the real distribution verifier with no archive reads at import."""
    return load_script("verify_distributions")


@pytest.fixture
def runtime() -> ModuleType:
    """Provide the runtime test driver without invoking the test suite recursively."""
    return load_script("run_runtime_tests")
