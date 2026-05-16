"""
Experiment Melder bind and later object creation with dropped synthetic dependencies.

Purpose:
    Answer one concrete runtime question:
    what happens when a bindable object from synthetic module `A` depends on
    synthetic module `B`, but `B` has been removed from `sys.modules` and from
    the synthetic loader's live registry before bind or before later object
    creation?

This bench uses two cases:
    1. eager dependency capture
       - module `A` imports `Dependency` from `B` at module-import time
       - `B` is then dropped from live visibility
       - bind and later meld are attempted
    2. lazy runtime import
       - module `A` imports `Dependency` from `B` inside `__init__`
       - `B` is then dropped from live visibility
       - bind and later meld are attempted

This is an experimentation bench, not production runtime code.
"""

import faulthandler
import os
import sys
import threading
import traceback
from typing import Any, Dict, Optional


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
if "src" not in sys.path:
    sys.path.insert(0, "src")

EXPERIMENT_DIR = os.path.dirname(__file__)
if EXPERIMENT_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENT_DIR)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
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


def _run_with_timeout(label: str, func: Any, timeout_seconds: float = EXPERIMENT_TIMEOUT_SECONDS) -> None:
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


def _drop_synthetic_module(
        loader: SyntheticModuleLoader,
        module_name: str,
) -> None:
    """
    Remove one synthetic module from live import visibility.

    Contract:
        - removes the module from `sys.modules`
        - removes loader-owned record/module references
        - removes load-order tracking for that module
        - detaches the module from its parent package object when applicable
    """
    record = loader._records_by_name.get(module_name)
    child_name = module_name.rsplit(".", 1)[-1]
    parent_name = None if record is None else record.parent_name
    if parent_name is not None:
        parent_module = sys.modules.get(parent_name)
        if parent_module is not None and hasattr(parent_module, child_name):
            delattr(parent_module, child_name)

    sys.modules.pop(module_name, None)
    loader._modules_by_name.pop(module_name, None)
    loader._records_by_name.pop(module_name, None)
    loader._load_order = [
        loaded_name
        for loaded_name in loader._load_order
        if loaded_name != module_name
    ]


def _create_spellbook(frame_name: str) -> Spellbook:
    """
    Build one small automatic Spellbook for the bench.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    configuration = SpellbookConfiguration(frame_name)
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(
        aetheric_frame=frame_name,
        configuration=configuration,
    )


def _cleanup_runtime(
        loader: SyntheticModuleLoader,
        spellbook: Optional[Spellbook] = None,
        conduit: Optional[Conduit] = None,
) -> None:
    """
    Cleanup the synthetic loader and Melder runtime objects.
    """
    try:
        loader.unload_all()
    except Exception:
        pass
    try:
        if conduit is not None:
            conduit.cleanup()
    except Exception:
        pass
    try:
        if spellbook is not None:
            spellbook.cleanup()
    except Exception:
        pass
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _build_loader_for_case(
        *,
        package_name: str,
        dependency_module_name: str,
        root_module_name: str,
        root_class_name: str,
        root_source_text: str,
) -> SyntheticModuleLoader:
    """
    Build the synthetic package graph for one bench case.
    """
    loader = SyntheticModuleLoader()
    loader.register_records(
        (
            SyntheticModuleRecord(
                module_name=package_name,
                source_text="PACKAGE_NAME = '{0}'\n".format(package_name),
                is_package=True,
            ),
            SyntheticModuleRecord(
                module_name=dependency_module_name,
                parent_name=package_name,
                source_text=(
                    "class Dependency:\n"
                    "    def __init__(self) -> None:\n"
                    "        self.value = 42\n"
                ),
            ),
            SyntheticModuleRecord(
                module_name=root_module_name,
                parent_name=package_name,
                source_text=root_source_text,
            ),
        )
    )
    return loader


def _bind_and_meld(
        *,
        root_type: type,
        frame_name: str,
) -> Dict[str, object]:
    """
    Bind one type into a Spellbook and then conjure + meld it.

    Returns:
        dict with:
        - bind_success
        - spell_id
        - conjure_success
        - meld_success
        - meld_value
        - error_type
        - error_message
    """
    result: Dict[str, object] = {
        "bind_success": False,
        "spell_id": None,
        "conjure_success": False,
        "meld_success": False,
        "meld_value": None,
        "error_type": None,
        "error_message": None,
    }
    spellbook: Optional[Spellbook] = None
    conduit: Optional[Conduit] = None
    try:
        spellbook = _create_spellbook(frame_name)
        try:
            spell_id = spellbook.bind(
                spell=root_type,
                existence=Existence.unique,
                permissions="create",
            )
        except RuntimeError as exc:
            if "requires an active binding transaction" not in str(exc):
                raise
            with spellbook.binding_transaction():
                spell_id = spellbook.bind(
                    spell=root_type,
                    existence=Existence.unique,
                    permissions="create",
                )
        result["bind_success"] = True
        result["spell_id"] = spell_id

        conduit = spellbook.conjure(name="root")
        result["conjure_success"] = True
        root_object = conduit.meld(spell=spell_id)
        result["meld_success"] = True
        result["meld_value"] = root_object.read()
        return result
    except Exception as exc:
        result["error_type"] = exc.__class__.__name__
        result["error_message"] = str(exc)
        return result
    finally:
        _cleanup_runtime(SyntheticModuleLoader(), spellbook=spellbook, conduit=conduit)


def _eager_dependency_capture_experiment() -> None:
    """
    Test a module-level eager dependency capture from synthetic module `B`.
    """
    package_name = "synthetic_bind_case_eager"
    dependency_module_name = "{0}.module_b".format(package_name)
    root_module_name = "{0}.module_a".format(package_name)
    root_class_name = "BoundRoot"
    root_source_text = (
        "from {0} import Dependency\n"
        "\n"
        "class {1}:\n"
        "    def __init__(self) -> None:\n"
        "        self.dependency = Dependency()\n"
        "\n"
        "    def read(self) -> int:\n"
        "        return self.dependency.value\n"
    ).format(
        dependency_module_name,
        root_class_name,
    )

    loader = _build_loader_for_case(
        package_name=package_name,
        dependency_module_name=dependency_module_name,
        root_module_name=root_module_name,
        root_class_name=root_class_name,
        root_source_text=root_source_text,
    )
    try:
        loader.materialize(loader._records_by_name[package_name])
        loader.materialize(loader._records_by_name[dependency_module_name])
        root_module = loader.materialize(loader._records_by_name[root_module_name])

        _drop_synthetic_module(loader, dependency_module_name)
        root_type = getattr(root_module, root_class_name)
        result = _bind_and_meld(
            root_type=root_type,
            frame_name="synthetic-eager-dependency-frame",
        )

        if not result["bind_success"]:
            raise AssertionError(
                "Eager dependency case failed during bind: {0}: {1}".format(
                    result["error_type"],
                    result["error_message"],
                )
            )
        if not result["meld_success"]:
            raise AssertionError(
                "Eager dependency case failed during meld: {0}: {1}".format(
                    result["error_type"],
                    result["error_message"],
                )
            )
        if result["meld_value"] != 42:
            raise AssertionError(
                "Eager dependency case returned {0}, expected 42.".format(
                    result["meld_value"]
                )
            )
        _emit("OK_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_EAGER")
    finally:
        loader.unload_all()


def _lazy_dependency_import_experiment() -> None:
    """
    Test a runtime lazy dependency import after the synthetic dependency is dropped.
    """
    package_name = "synthetic_bind_case_lazy"
    dependency_module_name = "{0}.module_b".format(package_name)
    root_module_name = "{0}.module_a".format(package_name)
    root_class_name = "BoundRoot"
    root_source_text = (
        "class {0}:\n"
        "    def __init__(self) -> None:\n"
        "        from {1} import Dependency\n"
        "        self.dependency = Dependency()\n"
        "\n"
        "    def read(self) -> int:\n"
        "        return self.dependency.value\n"
    ).format(
        root_class_name,
        dependency_module_name,
    )

    loader = _build_loader_for_case(
        package_name=package_name,
        dependency_module_name=dependency_module_name,
        root_module_name=root_module_name,
        root_class_name=root_class_name,
        root_source_text=root_source_text,
    )
    try:
        loader.materialize(loader._records_by_name[package_name])
        loader.materialize(loader._records_by_name[dependency_module_name])
        root_module = loader.materialize(loader._records_by_name[root_module_name])

        _drop_synthetic_module(loader, dependency_module_name)
        root_type = getattr(root_module, root_class_name)
        result = _bind_and_meld(
            root_type=root_type,
            frame_name="synthetic-lazy-dependency-frame",
        )

        if not result["bind_success"]:
            raise AssertionError(
                "Lazy dependency case failed during bind: {0}: {1}".format(
                    result["error_type"],
                    result["error_message"],
                )
            )
        if result["meld_success"]:
            raise AssertionError(
                "Lazy dependency case unexpectedly succeeded during meld with dropped dependency."
            )
        if result["error_type"] not in (
                "ModuleNotFoundError",
                "ImportError",
                "MeldExecutionError",
        ):
            raise AssertionError(
                "Lazy dependency case failed with unexpected error type {0}: {1}".format(
                    result["error_type"],
                    result["error_message"],
                )
            )
        if (
                result["error_type"] == "MeldExecutionError"
                and "ModuleNotFoundError" not in str(result["error_message"])
        ):
            raise AssertionError(
                "Lazy dependency case expected inner ModuleNotFoundError in MeldExecutionError, got: {0}".format(
                    result["error_message"]
                )
            )
        _emit(
            "OK_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_LAZY_{0}".format(
                result["error_type"]
            )
        )
    finally:
        loader.unload_all()


def _run_bench() -> None:
    """
    Execute the dropped synthetic-dependency Melder integration experiment.
    """
    _emit("START_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_EXPERIMENT")
    _run_with_timeout(
        "MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_EAGER_BLOCK",
        _eager_dependency_capture_experiment,
    )
    _run_with_timeout(
        "MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_LAZY_BLOCK",
        _lazy_dependency_import_experiment,
    )
    _emit("OK_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_EXPERIMENT")


if __name__ == "__main__":
    _run_bench()
