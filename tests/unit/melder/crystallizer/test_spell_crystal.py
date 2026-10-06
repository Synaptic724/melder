import sys
import shutil
from pathlib import Path
from types import ModuleType

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
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

def test_spell_crystal_records_the_frame_kind_and_a_contracts_coordinates() -> None:
    """
    The crystal carries `spellframe_kind` and, for a contract, the Protocol's module and qualname (record 4.1.0).

    A bare binding records "none" with no coordinates; a string category records "category" and the label; a
    Protocol frame records "contract" with the coordinates a loader hydrates it from.
    """
    from typing import Protocol

    from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind

    class IRepo(Protocol):
        def fetch(self) -> None: ...

    crystallizer = _create_activated_crystallizer()
    bare = DummySpell("bare-spell", type("BareService", (), {"__module__": __name__}))
    category = DummySpell("category-spell", type("CategoryService", (), {"__module__": __name__}))
    category.spellframe = "storage"
    category.spellframe_kind = SpellframeKind.category
    contract = DummySpell("contract-spell", type("ContractService", (), {"__module__": __name__}))
    contract.spellframe = IRepo
    contract.spellframe_kind = SpellframeKind.contract
    contract.implemented_protocols = (IRepo,)
    crystals = []
    try:
        for spell in (bare, category, contract):
            crystals.append(crystallizer.create_spell_crystal(spell))
        bare_crystal, category_crystal, contract_crystal = crystals
        assert bare_crystal.spellframe_kind == "none"
        assert bare_crystal.spellframe_module is None and bare_crystal.spellframe_qualname is None
        assert category_crystal.spellframe_kind == "category"
        assert category_crystal.spellframe_name == "storage"
        assert category_crystal.spellframe_module is None and category_crystal.spellframe_qualname is None
        assert contract_crystal.spellframe_kind == "contract"
        assert contract_crystal.spellframe_name == "IRepo"
        assert contract_crystal.spellframe_module == IRepo.__module__
        assert contract_crystal.spellframe_qualname == IRepo.__qualname__
        payload = contract_crystal.describe()
        assert payload["spellframe_kind"] == "contract"
        assert payload["spellframe_module"] == IRepo.__module__
        assert payload["spellframe_qualname"] == IRepo.__qualname__
    finally:
        for crystal in crystals:
            crystal.cleanup()


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


def _keyed_service_module(module_name: str) -> SyntheticModule:
    """Publish one trivial synthetic module for a KeyedService target; the caller cleans it and pops sys.modules."""
    module = SyntheticModule(
        module_name=module_name,
        spell_crystal_id="keyed-crystal",
        source_text="class KeyedService:\n    pass\n",
        source_sha256="keyed-sha",
        binding_signature="keyed-binding",
    )
    sys.modules[module_name] = module
    return module


def _keyed_spell(spell_id: str, module_name: str, frame_name: str) -> DummySpell:
    """Build one spell double bound in `frame_name` whose target lives in the keyed synthetic module."""
    spell = DummySpell(spell_id, type("KeyedService", (), {"__module__": module_name}))
    spell.aetheric_frame = frame_name
    return spell


def _install_regime(process_wide: bool) -> None:
    """Configure and activate the fixture's Aether with one spell-id regime before any frame exists."""
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(process_wide)
    policy.activate()
    Aether().activate(policy)


def test_spell_crystal_default_custody_key_is_the_spell_id_and_records_the_frame() -> None:
    """
    Verify the process-wide key (0.2.8214): the custody key is the bare spell id, and the frame rides along.

    Returns:
        None.
    """
    module_name = "test.keyed_custody_default"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = SpellCrystal(_keyed_spell("sha-keyed", module_name, "tenant_a"))
        assert crystal.custody_key == "sha-keyed"
        assert crystal.frame_name == "tenant_a"
        description = crystal.describe()
        assert description["custody_key"] == "sha-keyed"
        assert description["frame_name"] == "tenant_a"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)


def test_spell_crystal_per_frame_custody_key_composes_the_frame() -> None:
    """
    Verify the per-frame key: "<spell_id>@<frame>", so one spell bound in two frames records twice.

    Returns:
        None.
    """
    module_name = "test.keyed_custody_per_frame"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = SpellCrystal(_keyed_spell("sha-keyed", module_name, "tenant_b"), per_frame_custody=True)
        assert crystal.id == "sha-keyed"
        assert crystal.custody_key == "sha-keyed@tenant_b"
        assert crystal.describe()["custody_key"] == "sha-keyed@tenant_b"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)


def test_custody_key_statics_round_trip_including_an_at_sign_in_the_frame() -> None:
    """
    Verify the key grammar: composition appends "@<frame>", and parsing splits at the FIRST "@", because a spell id
    (a SHA256 hex digest) never holds one while a frame name may.

    Returns:
        None.
    """
    assert SpellCrystal.compose_custody_key("abc", "tenant@eu") == "abc@tenant@eu"
    assert SpellCrystal.spell_id_of_custody_key("abc@tenant@eu") == "abc"
    assert SpellCrystal.spell_id_of_custody_key("abc") == "abc"


def test_facade_keys_custody_per_frame_under_per_frame_ids() -> None:
    """
    Verify the facade reads the regime: under per-frame ids `create_spell_crystal` builds a frame-scoped key.

    Returns:
        None.
    """
    _install_regime(False)
    module_name = "test.keyed_custody_facade_per_frame"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = _create_activated_crystallizer().create_spell_crystal(
            _keyed_spell("sha-keyed", module_name, "tenant_a")
        )
        assert crystal.custody_key == "sha-keyed@tenant_a"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)


def test_facade_keeps_bare_keys_under_process_wide_ids() -> None:
    """
    Verify default worlds keep their record keys: under process-wide ids the facade builds the bare spell id key.

    Returns:
        None.
    """
    _install_regime(True)
    module_name = "test.keyed_custody_facade_process_wide"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = _create_activated_crystallizer().create_spell_crystal(
            _keyed_spell("sha-keyed", module_name, "tenant_a")
        )
        assert crystal.custody_key == "sha-keyed"
        assert crystal.frame_name == "tenant_a"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)
