"""
Experiment physical-to-synthetic module swap semantics inside one Python process.

Purpose:
    Prove what actually happens when a file-backed provider module is replaced
    with a synthetic module after import-time references already exist.

This bench focuses on semantic correctness, not performance. It covers:
    1. eager from-import retention in module-level functions
    2. module-object retention from `from . import provider`
    3. lazy import rebinding after swap
    4. class-method retention after eager import
    5. importlib.reload rebinding behavior
    6. nested package/submodule swap behavior
    7. existing instance coexistence
    8. Melder bind-after-swap using an old class object
    9. Melder conjure/meld-after-swap eager dependency capture
    10. Melder conjure/meld-after-swap lazy dependency import

This is an experimentation bench, not production runtime code.
"""

import faulthandler
import importlib
import os
import shutil
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)
if "src" not in sys.path:
    sys.path.insert(0, "src")

EXPERIMENT_DIR = os.path.dirname(__file__)
if EXPERIMENT_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENT_DIR)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
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


def _write(path: Path, content: str) -> None:
    """
    Write UTF-8 text to one file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _create_temp_package(
        package_name: str,
        files_by_relative_path: Dict[str, str],
) -> Path:
    """
    Create one temporary physical package tree for an experiment.
    """
    temp_root = Path(__file__).resolve().parent / "_physical_to_synth_swap_tmp"
    temp_root.mkdir(exist_ok=True)
    root = temp_root / "{0}_{1}".format(
        package_name,
        threading.get_native_id(),
    )
    suffix = 0
    while root.exists():
        suffix += 1
        root = temp_root / "{0}_{1}_{2}".format(
            package_name,
            threading.get_native_id(),
            suffix,
        )
    root.mkdir()
    for relative_path, content in files_by_relative_path.items():
        _write(root / relative_path, content)
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


def _clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove one dotted-name prefix from sys.modules and parent package attrs.
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


def _drop_module_only(module_name: str) -> None:
    """
    Remove one module from live visibility without clearing sibling modules.
    """
    parent_name, _, child_name = module_name.rpartition(".")
    if parent_name:
        parent_module = sys.modules.get(parent_name)
        if parent_module is not None and hasattr(parent_module, child_name):
            try:
                delattr(parent_module, child_name)
            except AttributeError:
                pass
    sys.modules.pop(module_name, None)


def _materialize_synthetic_module(
        loader: SyntheticModuleLoader,
        *,
        module_name: str,
        parent_name: Optional[str],
        source_text: str,
) -> Any:
    """
    Materialize one synthetic replacement module into sys.modules.
    """
    record = SyntheticModuleRecord(
        module_name=module_name,
        parent_name=parent_name,
        source_text=source_text,
    )
    return loader.materialize(record)


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


def _cleanup_melder_runtime(
        spellbook: Optional[Spellbook] = None,
        conduit: Optional[Conduit] = None,
) -> None:
    """
    Cleanup Melder runtime objects used by one experiment.
    """
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


def _bind_only(
        *,
        root_type: type,
        frame_name: str,
) -> Dict[str, object]:
    """
    Bind one type and return the spell object for inspection.
    """
    spellbook: Optional[Spellbook] = None
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
        spell = spellbook._spells_by_id[spell_id]
        return {
            "spell_id": spell_id,
            "bound_spell_object": spell.spell,
        }
    finally:
        _cleanup_melder_runtime(spellbook=spellbook, conduit=None)


def _bind_and_meld(
        *,
        root_type: type,
        frame_name: str,
) -> Dict[str, object]:
    """
    Bind one type, conjure a conduit, and meld it once.
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
        _cleanup_melder_runtime(spellbook=spellbook, conduit=conduit)


def _eager_from_import_function_retention_experiment() -> None:
    """
    Prove a module-level from-import function keeps the old value after swap.
    """
    package_name = "swap_case_eager_function"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "VALUE = 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from .provider import VALUE\n"
                "\n"
                "def read_value() -> str:\n"
                "    return VALUE\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer = importlib.import_module("{0}.consumer".format(package_name))
        if consumer.read_value() != "physical":
            raise AssertionError("Expected physical eager function value before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text="VALUE = 'synthetic'\n",
        )
        provider = importlib.import_module("{0}.provider".format(package_name))
        if provider.VALUE != "synthetic":
            raise AssertionError("Expected synthetic provider after swap.")
        if consumer.read_value() != "physical":
            raise AssertionError(
                "Expected eager from-import function to retain the old value after swap."
            )
        _emit("OK_PHYS_TO_SYNTH_EAGER_FUNCTION_RETENTION")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _module_object_retention_experiment() -> None:
    """
    Prove a retained module-object reference keeps the old module after swap.
    """
    package_name = "swap_case_module_object"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "VALUE = 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from . import provider\n"
                "\n"
                "def read_value() -> str:\n"
                "    return provider.VALUE\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer = importlib.import_module("{0}.consumer".format(package_name))
        if consumer.read_value() != "physical":
            raise AssertionError("Expected physical module-object value before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text="VALUE = 'synthetic'\n",
        )
        provider = importlib.import_module("{0}.provider".format(package_name))
        if provider.VALUE != "synthetic":
            raise AssertionError("Expected synthetic provider after swap.")
        if consumer.read_value() != "physical":
            raise AssertionError(
                "Expected module-object retention to keep the old provider reference after swap."
            )
        _emit("OK_PHYS_TO_SYNTH_MODULE_OBJECT_RETENTION")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _lazy_import_rebinding_experiment() -> None:
    """
    Prove a lazy import observes the swapped synthetic provider.
    """
    package_name = "swap_case_lazy_import"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "VALUE = 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "def read_value() -> str:\n"
                "    from .provider import VALUE\n"
                "    return VALUE\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer = importlib.import_module("{0}.consumer".format(package_name))
        if consumer.read_value() != "physical":
            raise AssertionError("Expected physical lazy import value before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text="VALUE = 'synthetic'\n",
        )
        if consumer.read_value() != "synthetic":
            raise AssertionError(
                "Expected lazy import to resolve the swapped synthetic provider."
            )
        _emit("OK_PHYS_TO_SYNTH_LAZY_IMPORT_REBIND")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _function_globals_retention_experiment() -> None:
    """
    Prove function globals keep the eagerly imported object after swap.
    """
    package_name = "swap_case_function_globals"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from .provider import Dependency\n"
                "\n"
                "def build() -> str:\n"
                "    return Dependency().read()\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer = importlib.import_module("{0}.consumer".format(package_name))
        if consumer.build() != "physical":
            raise AssertionError("Expected physical function-global result before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text=(
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'synthetic'\n"
            ),
        )
        if consumer.build() != "physical":
            raise AssertionError(
                "Expected function globals to keep the old imported class after swap."
            )
        _emit("OK_PHYS_TO_SYNTH_FUNCTION_GLOBALS_RETENTION")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _class_method_retention_experiment() -> None:
    """
    Prove class methods keep eagerly imported provider classes after swap.
    """
    package_name = "swap_case_class_method"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from .provider import Dependency\n"
                "\n"
                "class Consumer:\n"
                "    def build(self) -> str:\n"
                "        return Dependency().read()\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer_module = importlib.import_module("{0}.consumer".format(package_name))
        if consumer_module.Consumer().build() != "physical":
            raise AssertionError("Expected physical class-method result before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text=(
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'synthetic'\n"
            ),
        )
        if consumer_module.Consumer().build() != "physical":
            raise AssertionError(
                "Expected class methods to keep the old imported class after swap."
            )
        _emit("OK_PHYS_TO_SYNTH_CLASS_METHOD_RETENTION")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _importlib_reload_rebind_experiment() -> None:
    """
    Prove reloading the consumer after swap rebinds it to the synthetic provider.
    """
    package_name = "swap_case_reload"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "VALUE = 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from .provider import VALUE\n"
                "\n"
                "def read_value() -> str:\n"
                "    return VALUE\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer = importlib.import_module("{0}.consumer".format(package_name))
        if consumer.read_value() != "physical":
            raise AssertionError("Expected physical reload case before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text="VALUE = 'synthetic'\n",
        )
        if consumer.read_value() != "physical":
            raise AssertionError(
                "Expected pre-reload consumer to keep the old eager value."
            )
        consumer = importlib.reload(consumer)
        if consumer.read_value() != "synthetic":
            raise AssertionError(
                "Expected importlib.reload to rebind the consumer to the synthetic provider."
            )
        _emit("OK_PHYS_TO_SYNTH_IMPORTLIB_RELOAD_REBIND")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _nested_package_submodule_swap_experiment() -> None:
    """
    Prove nested package/provider swaps show the same eager-retention split.
    """
    package_name = "swap_case_nested"
    provider_module_name = "{0}.topic.provider".format(package_name)
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/topic/__init__.py".format(package_name): "",
            "{0}/topic/provider.py".format(package_name): (
                "VALUE = 'physical'\n"
            ),
            "{0}/topic/consumer.py".format(package_name): (
                "from .provider import VALUE\n"
                "\n"
                "def read_value() -> str:\n"
                "    return VALUE\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer = importlib.import_module("{0}.topic.consumer".format(package_name))
        if consumer.read_value() != "physical":
            raise AssertionError("Expected physical nested result before swap.")
        _drop_module_only(provider_module_name)
        _materialize_synthetic_module(
            loader,
            module_name=provider_module_name,
            parent_name="{0}.topic".format(package_name),
            source_text="VALUE = 'synthetic'\n",
        )
        provider = importlib.import_module(provider_module_name)
        if provider.VALUE != "synthetic":
            raise AssertionError("Expected nested provider to swap to synthetic.")
        if consumer.read_value() != "physical":
            raise AssertionError(
                "Expected nested eager consumer to retain the old provider value after swap."
            )
        _emit("OK_PHYS_TO_SYNTH_NESTED_SUBMODULE_SWAP")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _existing_instance_coexistence_experiment() -> None:
    """
    Prove old instances and new instances can coexist after a module swap.
    """
    package_name = "swap_case_instances"
    provider_module_name = "{0}.provider".format(package_name)
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'physical'\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        physical_provider = importlib.import_module(provider_module_name)
        old_instance = physical_provider.Dependency()
        _drop_module_only(provider_module_name)
        _materialize_synthetic_module(
            loader,
            module_name=provider_module_name,
            parent_name=package_name,
            source_text=(
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'synthetic'\n"
            ),
        )
        synthetic_provider = importlib.import_module(provider_module_name)
        new_instance = synthetic_provider.Dependency()
        if old_instance.read() != "physical":
            raise AssertionError("Expected old instance to keep physical behavior.")
        if new_instance.read() != "synthetic":
            raise AssertionError("Expected new instance to use synthetic behavior.")
        if old_instance.__class__ is new_instance.__class__:
            raise AssertionError(
                "Expected old and new instances to come from different class objects."
            )
        _emit("OK_PHYS_TO_SYNTH_EXISTING_INSTANCE_COEXISTENCE")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _bind_after_swap_experiment() -> None:
    """
    Prove bind after swap still binds the old class object when it was imported eagerly.
    """
    package_name = "swap_case_bind_only"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "PROVIDER_TAG = 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from .provider import PROVIDER_TAG\n"
                "\n"
                "class Root:\n"
                "    provider_tag = PROVIDER_TAG\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer_module = importlib.import_module("{0}.consumer".format(package_name))
        root_type = consumer_module.Root
        if root_type.provider_tag != "physical":
            raise AssertionError("Expected physical provider_tag before swap.")
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text="PROVIDER_TAG = 'synthetic'\n",
        )
        bind_result = _bind_only(
            root_type=root_type,
            frame_name="phys-to-synth-bind-frame",
        )
        bound_root = bind_result["bound_spell_object"]
        if bound_root.provider_tag != "physical":
            raise AssertionError(
                "Expected bind-after-swap to still bind the old eager class object."
            )
        _emit("OK_PHYS_TO_SYNTH_BIND_AFTER_SWAP")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _conjure_meld_after_swap_eager_experiment() -> None:
    """
    Prove eager dependency capture still drives meld after swap.
    """
    package_name = "swap_case_meld_eager"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "from .provider import Dependency\n"
                "\n"
                "class Root:\n"
                "    def __init__(self) -> None:\n"
                "        self._dependency = Dependency()\n"
                "\n"
                "    def read(self) -> str:\n"
                "        return self._dependency.read()\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer_module = importlib.import_module("{0}.consumer".format(package_name))
        root_type = consumer_module.Root
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text=(
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'synthetic'\n"
            ),
        )
        result = _bind_and_meld(
            root_type=root_type,
            frame_name="phys-to-synth-meld-eager-frame",
        )
        if not result["meld_success"]:
            raise AssertionError(
                "Expected eager conjure/meld to succeed, got {0}: {1}".format(
                    result["error_type"],
                    result["error_message"],
                )
            )
        if result["meld_value"] != "physical":
            raise AssertionError(
                "Expected eager conjure/meld to keep the old dependency world."
            )
        _emit("OK_PHYS_TO_SYNTH_CONJURE_MELD_EAGER")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _conjure_meld_after_swap_lazy_experiment() -> None:
    """
    Prove lazy dependency imports observe the synthetic provider during meld.
    """
    package_name = "swap_case_meld_lazy"
    root = _create_temp_package(
        package_name,
        {
            "{0}/__init__.py".format(package_name): "",
            "{0}/provider.py".format(package_name): (
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'physical'\n"
            ),
            "{0}/consumer.py".format(package_name): (
                "class Root:\n"
                "    def __init__(self) -> None:\n"
                "        from .provider import Dependency\n"
                "        self._dependency = Dependency()\n"
                "\n"
                "    def read(self) -> str:\n"
                "        return self._dependency.read()\n"
            ),
        },
    )
    loader = SyntheticModuleLoader()
    try:
        consumer_module = importlib.import_module("{0}.consumer".format(package_name))
        root_type = consumer_module.Root
        _drop_module_only("{0}.provider".format(package_name))
        _materialize_synthetic_module(
            loader,
            module_name="{0}.provider".format(package_name),
            parent_name=package_name,
            source_text=(
                "class Dependency:\n"
                "    def read(self) -> str:\n"
                "        return 'synthetic'\n"
            ),
        )
        result = _bind_and_meld(
            root_type=root_type,
            frame_name="phys-to-synth-meld-lazy-frame",
        )
        if not result["meld_success"]:
            raise AssertionError(
                "Expected lazy conjure/meld to succeed, got {0}: {1}".format(
                    result["error_type"],
                    result["error_message"],
                )
            )
        if result["meld_value"] != "synthetic":
            raise AssertionError(
                "Expected lazy conjure/meld to resolve the swapped synthetic provider."
            )
        _emit("OK_PHYS_TO_SYNTH_CONJURE_MELD_LAZY")
    finally:
        loader.unload_all()
        _teardown_temp_package(root, package_name)


def _run_bench() -> None:
    """
    Execute the full physical->synthetic swap semantic matrix.
    """
    _emit("START_PHYSICAL_TO_SYNTHETIC_MODULE_SWAP_SEMANTICS")
    _run_with_timeout(
        "PHYS_TO_SYNTH_EAGER_FUNCTION_BLOCK",
        _eager_from_import_function_retention_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_MODULE_OBJECT_BLOCK",
        _module_object_retention_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_LAZY_IMPORT_BLOCK",
        _lazy_import_rebinding_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_FUNCTION_GLOBALS_BLOCK",
        _function_globals_retention_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_CLASS_METHOD_BLOCK",
        _class_method_retention_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_IMPORTLIB_RELOAD_BLOCK",
        _importlib_reload_rebind_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_NESTED_PACKAGE_BLOCK",
        _nested_package_submodule_swap_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_EXISTING_INSTANCE_BLOCK",
        _existing_instance_coexistence_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_BIND_AFTER_SWAP_BLOCK",
        _bind_after_swap_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_CONJURE_MELD_EAGER_BLOCK",
        _conjure_meld_after_swap_eager_experiment,
    )
    _run_with_timeout(
        "PHYS_TO_SYNTH_CONJURE_MELD_LAZY_BLOCK",
        _conjure_meld_after_swap_lazy_experiment,
    )
    _emit("OK_PHYSICAL_TO_SYNTHETIC_MODULE_SWAP_SEMANTICS")


if __name__ == "__main__":
    _run_bench()
