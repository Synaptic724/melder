import importlib


def test_package_importable():
    module = importlib.import_module(
        "melder.spellbook.spell_crafter.spell_examiner.inspectors"
    )
    assert module is not None


def test_submodule_imports():
    inspector_utility = importlib.import_module(
        "melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility"
    )
    assert hasattr(inspector_utility, "InspectorUtility")
