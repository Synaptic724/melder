from importlib import import_module

import pytest

def test_lesser_creations_module_is_removed() -> None:
    """
    Purpose:
        Verify the legacy LesserCreations module is removed.
    Contract:
        Importing `melder.aether.conduit.creations.lesser_creations` raises.
    """
    with pytest.raises(ModuleNotFoundError):
        import_module("melder.aether.conduit.creations.lesser_creations")

