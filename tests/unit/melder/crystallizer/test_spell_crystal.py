import sys
import shutil
from pathlib import Path
from types import ModuleType

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.synthetic_module import SyntheticModule
from tests.mocks.crystallizer.spell_crystal_harness import (
    DummySpell,
    SYNTHETIC_CASES,
    cleanup_synthetic_case,
    install_synthetic_case,
    synthetic_case_id,
)


@pytest.fixture(autouse=True)
def reset_hosted_crystallizer_runtime() -> None:
    """
    Reset the hosted crystallizer runtime around each unit test.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


def _create_activated_crystallizer(
        user_source_root_paths=None,
) -> Crystallizer:
    """
    Build one activated hosted crystallizer for test use.

    Args:
        user_source_root_paths:
            Optional explicit user-source roots for the activation config.

    Returns:
        Crystallizer: Activated hosted crystallizer.
    """
    aether = Aether()
    crystallizer = aether._crystallizer
    configuration = crystallizer.create_configuration()
    if user_source_root_paths is None:
        configuration = configuration.with_defaults().activate()
    else:
        configuration = configuration.with_user_source_root_paths(
            user_source_root_paths
        ).activate()
    crystallizer.activate(configuration)
    return crystallizer


def test_spell_crystal_records_unknown_import_targets_honestly() -> None:
    """
    Verify unknown imports are recorded instead of being silently skipped.

    Returns:
        None.
    """
    module_name = "test.synthetic_spell_module"
    module = SyntheticModule(
        module_name=module_name,
        spell_crystal_id="source-crystal",
        source_text=(
            "import missing_dep\n"
            "from another_missing import helper\n"
            "class GeneratedService:\n"
            "    pass\n"
        ),
        source_sha256="abc123",
        binding_signature="binding-1",
    )
    sys.modules[module_name] = module
    crystal = None

    try:
        generated_service = type(
            "GeneratedService",
            (),
            {"__module__": module_name},
        )
        crystal = _create_activated_crystallizer().create_spell_crystal(
            DummySpell("spell-1", generated_service)
        )

        assert "missing_dep" in crystal.unknown_targets
        assert "another_missing" in crystal.unknown_targets
        assert "missing_dep" in crystal.module_to_direct_dependencies[module_name]
        assert "another_missing" in crystal.module_to_direct_dependencies[module_name]
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)

@pytest.fixture(params=SYNTHETIC_CASES, ids=synthetic_case_id)
def synthetic_case_crystal(request):
    """
    Build one synthetic graph case and the resulting `SpellCrystal`.
    """
    case = request.param
    root_type, installed_modules = install_synthetic_case(case)
    crystal = _create_activated_crystallizer().create_spell_crystal(
        DummySpell("unit-{0}".format(case["case_id"]), root_type)
    )
    try:
        yield case, crystal
    finally:
        crystal.cleanup()
        cleanup_synthetic_case(case, installed_modules)


def test_unit_synthetic_case_collects_expected_module_targets(
        synthetic_case_crystal,
) -> None:
    """
    Verify each synthetic case records the full expected module target set.
    """
    case, crystal = synthetic_case_crystal
    assert set(crystal.module_targets) == set(case["expected_module_targets"])


def test_unit_synthetic_case_collects_expected_direct_dependencies(
        synthetic_case_crystal,
) -> None:
    """
    Verify each synthetic case records the expected direct dependency map.
    """
    case, crystal = synthetic_case_crystal
    expected_direct_dependencies = case["expected_direct_dependencies"]
    assert {
        module_name: set(dependency_names)
        for module_name, dependency_names in crystal.module_to_direct_dependencies.items()
    } == {
        module_name: set(dependency_names)
        for module_name, dependency_names in expected_direct_dependencies.items()
    }


def test_unit_synthetic_case_classifies_all_modules_as_synthetic(
        synthetic_case_crystal,
) -> None:
    """
    Verify each synthetic case classifies every tracked module as synthetic.
    """
    case, crystal = synthetic_case_crystal
    expected_kinds = case["expected_kind_by_module"]
    assert crystal.module_to_kind == expected_kinds


def test_unit_synthetic_case_collects_all_synthetic_targets(
        synthetic_case_crystal,
) -> None:
    """
    Verify each synthetic case mirrors all tracked modules into synthetic targets.
    """
    case, crystal = synthetic_case_crystal
    assert set(crystal.synthetic_module_targets) == set(case["expected_module_targets"])


def test_unit_synthetic_case_reports_no_unknown_targets_for_closed_graphs(
        synthetic_case_crystal,
) -> None:
    """
    Verify closed synthetic graph cases do not report unknown targets.
    """
    _case, crystal = synthetic_case_crystal
    assert crystal.unknown_targets == []


def test_unit_synthetic_case_reports_no_walk_errors_for_closed_graphs(
        synthetic_case_crystal,
) -> None:
    """
    Verify closed synthetic graph cases do not report walk errors.
    """
    _case, crystal = synthetic_case_crystal
    assert crystal.walk_errors == []


def test_unit_synthetic_case_root_metadata_is_stable(
        synthetic_case_crystal,
) -> None:
    """
    Verify each synthetic case exposes stable root manifest metadata.
    """
    case, crystal = synthetic_case_crystal
    assert crystal.root_module_name == case["root_module_name"]
    assert crystal.root_module_kind == "synthetic_module"
    assert crystal.root_target_kind == "class"


def test_unit_synthetic_case_describe_snapshot_matches_dependency_maps(
        synthetic_case_crystal,
) -> None:
    """
    Verify each synthetic case `describe()` snapshot mirrors the dependency map.
    """
    case, crystal = synthetic_case_crystal
    description = crystal.describe()
    assert set(description["module_targets"]) == set(case["expected_module_targets"])
    assert {
        module_name: set(dependency_names)
        for module_name, dependency_names in description["module_to_direct_dependencies"].items()
    } == {
        module_name: set(dependency_names)
        for module_name, dependency_names in case["expected_direct_dependencies"].items()
    }


def test_unit_synthetic_case_keeps_path_targets_empty_without_physical_projection(
        synthetic_case_crystal,
) -> None:
    """
    Verify pure synthetic cases do not fabricate physical path targets.
    """
    _case, crystal = synthetic_case_crystal
    assert crystal.path_targets == []


def test_spell_crystal_uses_configured_user_source_roots() -> None:
    """
    Verify user-source classification can be driven by explicit source roots.

    Returns:
        None.
    """
    temp_root = (
        Path(__file__).resolve().parent
        / "_spell_crystal_test_data"
        / "configured_user_source_roots"
    )
    shutil.rmtree(temp_root.parent, ignore_errors=True)
    package_root = temp_root / "demo_pkg"
    package_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "helper.py").write_text(
        "class Helper:\n"
        "    pass\n",
        encoding="utf-8",
    )
    (package_root / "target.py").write_text(
        "from demo_pkg.helper import Helper\n"
        "class TargetService:\n"
        "    helper_type = Helper\n",
        encoding="utf-8",
    )

    package_module = ModuleType("demo_pkg")
    package_module.__path__ = [str(package_root)]
    package_module.__file__ = str(package_root / "__init__.py")
    package_module.__package__ = "demo_pkg"

    helper_module = ModuleType("demo_pkg.helper")
    helper_module.__file__ = str(package_root / "helper.py")
    helper_module.__package__ = "demo_pkg"

    target_module = ModuleType("demo_pkg.target")
    target_module.__file__ = str(package_root / "target.py")
    target_module.__package__ = "demo_pkg"

    sys.modules["demo_pkg"] = package_module
    sys.modules["demo_pkg.helper"] = helper_module
    sys.modules["demo_pkg.target"] = target_module

    target_service = type(
        "TargetService",
        (),
        {"__module__": "demo_pkg.target"},
    )
    crystal = None
    try:
        crystal = _create_activated_crystallizer(
            user_source_root_paths=[temp_root],
        ).create_spell_crystal(
            DummySpell("spell-2", target_service)
        )

        assert crystal.root_module_kind == "user_source"
        assert "demo_pkg.target" in crystal.user_source_targets
        assert "demo_pkg.helper" in crystal.user_source_targets
        assert str(temp_root.resolve()) in crystal.user_source_root_paths
    finally:
        if crystal is not None:
            crystal.cleanup()
        sys.modules.pop("demo_pkg.target", None)
        sys.modules.pop("demo_pkg.helper", None)
        sys.modules.pop("demo_pkg", None)
        shutil.rmtree(temp_root.parent, ignore_errors=True)
