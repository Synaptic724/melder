"""
Experiment importlib-style circular dependency semantics for synthetic modules.

Purpose:
    Answer one concrete question:
    can importlib-style loading give us useful circular-dependency behavior
    for synthetic modules and mixed physical/synthetic graphs, and what exact
    failure signal appears when the cycle is semantically bad rather than only
    present?

This bench covers four cases:
    1. benign synthetic <-> synthetic cycle
    2. failing synthetic <-> synthetic partial-init cycle
    3. benign mixed physical <-> synthetic cycle
    4. failing mixed physical <-> synthetic partial-init cycle

This is an experimentation bench, not production runtime code.
"""

import faulthandler
import importlib
import os
import shutil
import sys
import threading
import uuid
from pathlib import Path
from typing import Callable, Dict, Optional

EXPERIMENT_DIR = os.path.dirname(__file__)
if EXPERIMENT_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENT_DIR)

from synthetic_module_import_testbench import (
    SyntheticModuleLoader,
    SyntheticModuleRecord,
)


EXPERIMENT_TIMEOUT_SECONDS = 20.0


def _emit(marker: str) -> None:
    """
    Print one unbuffered progress marker.
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

    _emit("START_{0}".format(label))
    timer = threading.Timer(timeout_seconds, watchdog)
    timer.daemon = True
    timer.start()
    try:
        func()
    finally:
        timer.cancel()
    _emit("DONE_{0}".format(label))


def _clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove one dotted-name prefix from `sys.modules` and parent package attrs.
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


def _create_temp_package(
        package_name: str,
        files_by_relative_path: Dict[str, str],
) -> Path:
    """
    Create one temporary physical package tree for a mixed-cycle experiment.
    """
    temp_root = Path(__file__).resolve().parent / "_importlib_cycle_tmp"
    temp_root.mkdir(exist_ok=True)
    root = temp_root / "{0}_{1}".format(package_name, uuid.uuid4().hex)
    root.mkdir()
    for relative_path, content in files_by_relative_path.items():
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8", newline="\n")
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    _clear_modules_by_prefix(package_name)
    return root


def _teardown_temp_package(root: Path, package_name: str) -> None:
    """
    Remove one temporary package tree and its loaded modules.
    """
    _clear_modules_by_prefix(package_name)
    importlib.invalidate_caches()
    root_str = str(root)
    if root_str in sys.path:
        sys.path.remove(root_str)
    shutil.rmtree(root, ignore_errors=True)


def _assert_partial_init_failure(exc: BaseException) -> None:
    """
    Assert one exception matches the expected partial-init cycle failure signal.
    """
    message = str(exc)
    if exc.__class__.__name__ not in ("ImportError", "AttributeError"):
        raise AssertionError(
            "Expected ImportError or AttributeError for a bad cycle, got {0}: {1}".format(
                exc.__class__.__name__,
                message,
            )
        )
    accepted_markers = (
        "partially initialized module",
        "cannot import name",
        "has no attribute",
    )
    if not any(marker in message for marker in accepted_markers):
        raise AssertionError(
            "Expected partial-init failure message, got: {0}: {1}".format(
                exc.__class__.__name__,
                message,
            )
        )


def _synthetic_benign_cycle_experiment() -> None:
    """
    Prove a benign synthetic cycle succeeds under importlib-style loading.
    """
    package_name = "synthetic_importlib_cycle_ok"
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name=package_name,
                    source_text="PACKAGE_NAME = 'synthetic_importlib_cycle_ok'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="{0}.module_a".format(package_name),
                    parent_name=package_name,
                    source_text=(
                        "from {0} import module_b\n"
                        "VALUE_A = 'A'\n"
                        "\n"
                        "def pair() -> str:\n"
                        "    return VALUE_A + module_b.VALUE_B\n"
                    ).format(package_name),
                ),
                SyntheticModuleRecord(
                    module_name="{0}.module_b".format(package_name),
                    parent_name=package_name,
                    source_text=(
                        "from {0} import module_a\n"
                        "VALUE_B = 'B'\n"
                        "\n"
                        "def pair() -> str:\n"
                        "    return module_a.VALUE_A + VALUE_B\n"
                    ).format(package_name),
                ),
            )
        )
        loader.install_import_hook()
        module_a = importlib.import_module("{0}.module_a".format(package_name))
        module_b = importlib.import_module("{0}.module_b".format(package_name))
        if module_a.pair() != "AB" or module_b.pair() != "AB":
            raise AssertionError(
                "Expected benign synthetic cycle to resolve both sides to 'AB'."
            )
        _emit("OK_IMPORTLIB_SYNTHETIC_BENIGN_CYCLE")
    finally:
        loader.unload_all()
        _clear_modules_by_prefix(package_name)


def _synthetic_bad_cycle_experiment() -> None:
    """
    Prove a bad synthetic partial-init cycle fails with an importlib signal.
    """
    package_name = "synthetic_importlib_cycle_bad"
    loader = SyntheticModuleLoader()
    try:
        loader.register_records(
            (
                SyntheticModuleRecord(
                    module_name=package_name,
                    source_text="PACKAGE_NAME = 'synthetic_importlib_cycle_bad'\n",
                    is_package=True,
                ),
                SyntheticModuleRecord(
                    module_name="{0}.module_a".format(package_name),
                    parent_name=package_name,
                    source_text=(
                        "from {0}.module_b import VALUE_B\n"
                        "VALUE_A = 'A'\n"
                    ).format(package_name),
                ),
                SyntheticModuleRecord(
                    module_name="{0}.module_b".format(package_name),
                    parent_name=package_name,
                    source_text=(
                        "from {0}.module_a import VALUE_A\n"
                        "VALUE_B = 'B'\n"
                    ).format(package_name),
                ),
            )
        )
        loader.install_import_hook()
        try:
            importlib.import_module("{0}.module_a".format(package_name))
        except Exception as exc:
            _assert_partial_init_failure(exc)
            _emit("OK_IMPORTLIB_SYNTHETIC_BAD_CYCLE_DETECTED")
            return
        raise AssertionError(
            "Expected bad synthetic cycle to fail during import."
        )
    finally:
        loader.unload_all()
        _clear_modules_by_prefix(package_name)


def _mixed_benign_cycle_experiment() -> None:
    """
    Prove a benign mixed physical/synthetic cycle succeeds.
    """
    package_name = "mixed_importlib_cycle_ok"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/physical_side.py".format(package_name): (
                "from . import synthetic_side\n"
                "PHYSICAL_VALUE = 'physical'\n"
                "\n"
                "def pair() -> str:\n"
                "    return PHYSICAL_VALUE + '-' + synthetic_side.SYNTH_VALUE\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        loader.register_record(
            SyntheticModuleRecord(
                module_name="{0}.synthetic_side".format(package_name),
                parent_name=package_name,
                source_text=(
                    "from . import physical_side\n"
                    "SYNTH_VALUE = 'synthetic'\n"
                    "\n"
                    "def pair() -> str:\n"
                    "    return physical_side.PHYSICAL_VALUE + '-' + SYNTH_VALUE\n"
                ),
            )
        )
        loader.install_import_hook()
        physical_side = importlib.import_module("{0}.physical_side".format(package_name))
        synthetic_side = importlib.import_module("{0}.synthetic_side".format(package_name))
        if physical_side.pair() != "physical-synthetic":
            raise AssertionError(
                "Expected benign mixed cycle to resolve through the physical side."
            )
        if synthetic_side.pair() != "physical-synthetic":
            raise AssertionError(
                "Expected benign mixed cycle to resolve through the synthetic side."
            )
        _emit("OK_IMPORTLIB_MIXED_BENIGN_CYCLE")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _mixed_bad_cycle_experiment() -> None:
    """
    Prove a bad mixed physical/synthetic partial-init cycle fails visibly.
    """
    package_name = "mixed_importlib_cycle_bad"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/physical_side.py".format(package_name): (
                "from .synthetic_side import SYNTH_VALUE\n"
                "PHYSICAL_VALUE = 'physical'\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        loader.register_record(
            SyntheticModuleRecord(
                module_name="{0}.synthetic_side".format(package_name),
                parent_name=package_name,
                source_text=(
                    "from .physical_side import PHYSICAL_VALUE\n"
                    "SYNTH_VALUE = 'synthetic'\n"
                ),
            )
        )
        loader.install_import_hook()
        try:
            importlib.import_module("{0}.physical_side".format(package_name))
        except Exception as exc:
            _assert_partial_init_failure(exc)
            _emit("OK_IMPORTLIB_MIXED_BAD_CYCLE_DETECTED")
            return
        raise AssertionError(
            "Expected bad mixed cycle to fail during import."
        )
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _run_bench() -> None:
    """
    Execute the importlib circular-dependency experiment matrix.
    """
    _emit("START_IMPORTLIB_SYNTHETIC_CIRCULAR_DEPENDENCY_EXPERIMENTS")
    _run_with_timeout(
        "IMPORTLIB_SYNTHETIC_BENIGN_CYCLE_BLOCK",
        _synthetic_benign_cycle_experiment,
    )
    _run_with_timeout(
        "IMPORTLIB_SYNTHETIC_BAD_CYCLE_BLOCK",
        _synthetic_bad_cycle_experiment,
    )
    _run_with_timeout(
        "IMPORTLIB_MIXED_BENIGN_CYCLE_BLOCK",
        _mixed_benign_cycle_experiment,
    )
    _run_with_timeout(
        "IMPORTLIB_MIXED_BAD_CYCLE_BLOCK",
        _mixed_bad_cycle_experiment,
    )
    _emit("OK_IMPORTLIB_SYNTHETIC_CIRCULAR_DEPENDENCY_EXPERIMENTS")


if __name__ == "__main__":
    _run_bench()
