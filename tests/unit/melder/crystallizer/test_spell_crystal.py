import sys
import tempfile
import shutil
from pathlib import Path
from types import ModuleType

from melder.crystallizer.spell_crystal import SpellCrystal
from melder.crystallizer.synthetic_module import SyntheticModule


class _DummySpell:
    """
    Minimal spell double for `SpellCrystal` construction tests.
    """

    def __init__(self, spell_id: str, spell) -> None:
        self.spell_id = spell_id
        self.spell = spell


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
        crystal = SpellCrystal(_DummySpell("spell-1", generated_service))

        assert "missing_dep" in crystal.unknown_targets
        assert "another_missing" in crystal.unknown_targets
        assert "missing_dep" in crystal.module_to_direct_dependencies[module_name]
        assert "another_missing" in crystal.module_to_direct_dependencies[module_name]
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()


def test_spell_crystal_uses_configured_user_source_roots() -> None:
    """
    Verify user-source classification can be driven by explicit source roots.

    Returns:
        None.
    """
    temp_root = Path(tempfile.mkdtemp(prefix="spell_crystal_", dir="C:\\tmp"))
    package_root = temp_root / "demo_pkg"
    package_root.mkdir()
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
        crystal = SpellCrystal(
            _DummySpell("spell-2", target_service),
            user_source_root_paths=[temp_root],
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
        shutil.rmtree(temp_root, ignore_errors=True)
