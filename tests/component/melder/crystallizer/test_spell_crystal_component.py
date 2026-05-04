import importlib
from pathlib import Path

import pytest

from melder.crystallizer.spell_crystal import SpellCrystal
from tests.mocks.crystallizer.spell_crystal_harness import (
    DummySpell,
    PHYSICAL_CASES,
    PHYSICAL_PACKAGE_PREFIX,
    PHYSICAL_USER_SOURCE_ROOT,
    clear_modules,
    clear_modules_by_prefix,
    install_component_synthetic_dependency,
    physical_case_id,
)


@pytest.fixture(params=PHYSICAL_CASES, ids=physical_case_id)
def physical_case_crystal(request):
    """
    Build one component-level physical or mixed graph `SpellCrystal`.
    """
    case = request.param
    clear_modules_by_prefix(PHYSICAL_PACKAGE_PREFIX)
    synthetic_module = None
    if case.get("requires_synthetic_dependency"):
        synthetic_module = install_component_synthetic_dependency()

    root_module = importlib.import_module(case["root_module_name"])
    root_type = getattr(root_module, case["root_class_name"])
    crystal = SpellCrystal(
        DummySpell("component-{0}".format(case["case_id"]), root_type),
        user_source_root_paths=[PHYSICAL_USER_SOURCE_ROOT],
    )
    try:
        yield case, crystal
    finally:
        crystal.cleanup()
        if synthetic_module is not None:
            synthetic_module.cleanup()
            clear_modules(case["expected_module_targets"][-1])
        clear_modules_by_prefix(PHYSICAL_PACKAGE_PREFIX)


def test_component_case_collects_expected_module_targets(
        physical_case_crystal,
) -> None:
    """
    Verify each physical case records the expected module target set.
    """
    case, crystal = physical_case_crystal
    assert set(crystal.module_targets) == set(case["expected_module_targets"])


def test_component_case_collects_expected_direct_dependencies(
        physical_case_crystal,
) -> None:
    """
    Verify each physical case records the expected direct dependency map.
    """
    case, crystal = physical_case_crystal
    assert {
        module_name: set(dependency_names)
        for module_name, dependency_names in crystal.module_to_direct_dependencies.items()
    } == {
        module_name: set(dependency_names)
        for module_name, dependency_names in case["expected_direct_dependencies"].items()
    }


def test_component_case_collects_expected_kind_mapping(
        physical_case_crystal,
) -> None:
    """
    Verify each physical case records the expected module-kind mapping.
    """
    case, crystal = physical_case_crystal
    assert crystal.module_to_kind == case["expected_kind_by_module"]


def test_component_case_collects_expected_paths_and_extensions(
        physical_case_crystal,
) -> None:
    """
    Verify each physical case records stable path and extension data.
    """
    case, crystal = physical_case_crystal
    for module_name in case["expected_module_targets"]:
        module_kind = case["expected_kind_by_module"][module_name]
        if module_kind == "synthetic_module":
            assert module_name not in crystal.module_to_path
            assert module_name not in crystal.module_to_extension
            continue
        assert module_name in crystal.module_to_path
        assert crystal.module_to_path[module_name].endswith(".py")
        assert crystal.module_to_extension[module_name] == ".py"
