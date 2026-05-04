import importlib
import sys

import pytest

from melder.crystallizer.synthetic_module import SyntheticModule


def _clear_modules_by_prefix(prefix: str) -> None:
    """
    Remove one dotted-name prefix from `sys.modules`.
    """
    stale_names = [
        module_name
        for module_name in list(sys.modules.keys())
        if module_name == prefix or module_name.startswith(prefix + ".")
    ]
    for module_name in reversed(stale_names):
        sys.modules.pop(module_name, None)


@pytest.fixture(autouse=True)
def reset_synthetic_module_registry() -> None:
    """
    Reset synthetic import registry state around each unit test.

    Returns:
        None.
    """
    SyntheticModule.clear_import_registry()
    _clear_modules_by_prefix("synthetic_module_unit")
    yield
    SyntheticModule.clear_import_registry()
    _clear_modules_by_prefix("synthetic_module_unit")


def test_synthetic_module_materialize_executes_and_publishes() -> None:
    """
    Verify direct materialization publishes and executes one module.

    Returns:
        None.
    """
    module = SyntheticModule(
        module_name="synthetic_module_unit.simple",
        spell_crystal_id="simple-crystal",
        source_text=(
            "VALUE = 42\n"
            "\n"
            "def read() -> int:\n"
            "    return VALUE\n"
        ),
        source_sha256="simple-sha",
        binding_signature="simple-binding",
    )

    materialized = module.materialize(install_import_hook=True)

    assert materialized is module
    assert module.published_in_sys_modules is True
    assert module.executed_source is True
    assert sys.modules[module.__name__] is module
    assert module.read() == 42


def test_synthetic_module_import_hook_loads_nested_package_graph() -> None:
    """
    Verify importlib can load a nested synthetic package graph from the registry.

    Returns:
        None.
    """
    package_shell = SyntheticModule.create_package_shell(
        module_name="synthetic_module_unit.pkg",
        spell_crystal_id="pkg-crystal",
    )
    helper_module = SyntheticModule(
        module_name="synthetic_module_unit.pkg.helper",
        spell_crystal_id="helper-crystal",
        source_text="def answer() -> int:\n    return 42\n",
        source_sha256="helper-sha",
        binding_signature="helper-binding",
        parent_name="synthetic_module_unit.pkg",
    )
    consumer_module = SyntheticModule(
        module_name="synthetic_module_unit.pkg.consumer",
        spell_crystal_id="consumer-crystal",
        source_text=(
            "from synthetic_module_unit.pkg.helper import answer\n"
            "\n"
            "def read() -> int:\n"
            "    return answer()\n"
        ),
        source_sha256="consumer-sha",
        binding_signature="consumer-binding",
        parent_name="synthetic_module_unit.pkg",
    )

    package_shell.register_in_import_registry()
    helper_module.register_in_import_registry()
    consumer_module.register_in_import_registry()
    SyntheticModule.install_import_hook()

    imported_consumer = SyntheticModule.import_registered_module(
        "synthetic_module_unit.pkg.consumer"
    )

    assert imported_consumer is consumer_module
    assert consumer_module.read() == 42
    assert helper_module.executed_source is True
    assert package_shell.is_package is True
    assert getattr(sys.modules["synthetic_module_unit.pkg"], "consumer") is consumer_module


def test_synthetic_module_reload_via_importlib_reexecutes_updated_source() -> None:
    """
    Verify reload re-executes source after the source text changes.

    Returns:
        None.
    """
    module = SyntheticModule(
        module_name="synthetic_module_unit.reloadable",
        spell_crystal_id="reload-crystal",
        source_text="VALUE = 1\n",
        source_sha256="reload-sha-1",
        binding_signature="reload-binding",
    )
    module.materialize(install_import_hook=True)
    assert module.VALUE == 1

    module.update_source_text(
        "VALUE = 2\n",
        "reload-sha-2",
    )
    reloaded = module.reload_via_importlib()

    assert reloaded is module
    assert module.VALUE == 2
    assert module.executed_source is True


def test_synthetic_module_importlib_support_allows_benign_circular_cycle() -> None:
    """
    Verify benign synthetic cycles load correctly with importlib semantics.

    Returns:
        None.
    """
    package_shell = SyntheticModule.create_package_shell(
        module_name="synthetic_module_unit.cycle_ok",
        spell_crystal_id="cycle-ok",
    )
    module_a = SyntheticModule(
        module_name="synthetic_module_unit.cycle_ok.module_a",
        spell_crystal_id="cycle-a",
        source_text=(
            "from synthetic_module_unit.cycle_ok import module_b\n"
            "VALUE_A = 'A'\n"
            "\n"
            "def pair() -> str:\n"
            "    return VALUE_A + module_b.VALUE_B\n"
        ),
        source_sha256="cycle-a-sha",
        binding_signature="cycle-a-binding",
        parent_name="synthetic_module_unit.cycle_ok",
    )
    module_b = SyntheticModule(
        module_name="synthetic_module_unit.cycle_ok.module_b",
        spell_crystal_id="cycle-b",
        source_text=(
            "from synthetic_module_unit.cycle_ok import module_a\n"
            "VALUE_B = 'B'\n"
            "\n"
            "def pair() -> str:\n"
            "    return module_a.VALUE_A + VALUE_B\n"
        ),
        source_sha256="cycle-b-sha",
        binding_signature="cycle-b-binding",
        parent_name="synthetic_module_unit.cycle_ok",
    )

    package_shell.register_in_import_registry()
    module_a.register_in_import_registry()
    module_b.register_in_import_registry()
    SyntheticModule.install_import_hook()

    imported_a = SyntheticModule.import_registered_module(
        "synthetic_module_unit.cycle_ok.module_a"
    )
    imported_b = SyntheticModule.import_registered_module(
        "synthetic_module_unit.cycle_ok.module_b"
    )

    assert imported_a.pair() == "AB"
    assert imported_b.pair() == "AB"


def test_synthetic_module_importlib_support_surfaces_bad_circular_cycle() -> None:
    """
    Verify bad partial-init synthetic cycles fail visibly.

    Returns:
        None.
    """
    package_shell = SyntheticModule.create_package_shell(
        module_name="synthetic_module_unit.cycle_bad",
        spell_crystal_id="cycle-bad",
    )
    module_a = SyntheticModule(
        module_name="synthetic_module_unit.cycle_bad.module_a",
        spell_crystal_id="cycle-bad-a",
        source_text=(
            "from synthetic_module_unit.cycle_bad.module_b import VALUE_B\n"
            "VALUE_A = 'A'\n"
        ),
        source_sha256="cycle-bad-a-sha",
        binding_signature="cycle-bad-a-binding",
        parent_name="synthetic_module_unit.cycle_bad",
    )
    module_b = SyntheticModule(
        module_name="synthetic_module_unit.cycle_bad.module_b",
        spell_crystal_id="cycle-bad-b",
        source_text=(
            "from synthetic_module_unit.cycle_bad.module_a import VALUE_A\n"
            "VALUE_B = 'B'\n"
        ),
        source_sha256="cycle-bad-b-sha",
        binding_signature="cycle-bad-b-binding",
        parent_name="synthetic_module_unit.cycle_bad",
    )

    package_shell.register_in_import_registry()
    module_a.register_in_import_registry()
    module_b.register_in_import_registry()
    SyntheticModule.install_import_hook()

    with pytest.raises((ImportError, AttributeError)) as exc_info:
        SyntheticModule.import_registered_module(
            "synthetic_module_unit.cycle_bad.module_a"
        )

    message = str(exc_info.value)
    assert (
        "partially initialized module" in message
        or "cannot import name" in message
        or "has no attribute" in message
    )
