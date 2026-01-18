import types
import uuid

import pytest

from melder.spellbook.bind.scan import scan_bind
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Create a Spellbook with a unique aetheric frame for scan tests.
    Contract:
        Returns a fresh Spellbook instance isolated by frame name.
    Returns:
        Spellbook: A new Spellbook instance.
    """
    frame = f"scan_bind_test_{uuid.uuid4().hex}"
    return Spellbook(aetheric_frame=frame)


def _make_module(name: str) -> types.ModuleType:
    """
    Purpose:
        Construct a simple module object for scan binding tests.
    Contract:
        Returns a ModuleType with the provided name.
    Args:
        name (str): Module name to assign.
    Returns:
        types.ModuleType: New module instance.
    """
    return types.ModuleType(name)


def test_scan_binds_marked_objects() -> None:
    """
    Purpose:
        Verify scan binds all scan_bind-decorated objects in a module.
    Contract:
        A module with two decorated classes yields two bound spell IDs.
    """
    spellbook = _make_spellbook()
    module = _make_module("scan_bind_mod_a")

    @scan_bind(existence=Existence.unique, permissions="create")
    class First:
        pass

    @scan_bind(existence=Existence.unique, permissions="create")
    class Second:
        pass

    First.__module__ = module.__name__
    Second.__module__ = module.__name__
    module.First = First
    module.Second = Second

    spell_ids = spellbook.scan(module)

    assert len(spell_ids) == 2
    assert len(spellbook.spells) == 2


def test_scan_rejects_reexports() -> None:
    """
    Purpose:
        Ensure scan rejects decorated objects not owned by the scanned module.
    Contract:
        A decorated object with a mismatched __module__ triggers ValueError.
    """
    spellbook = _make_spellbook()
    module = _make_module("scan_bind_mod_b")

    @scan_bind(existence=Existence.unique, permissions="create")
    class Exported:
        pass

    Exported.__module__ = "other_module"
    module.Exported = Exported

    with pytest.raises(ValueError):
        spellbook.scan(module)


def test_scan_bind_requires_explicit_metadata() -> None:
    """
    Purpose:
        Validate that scan_bind enforces explicit existence and permissions.
    Contract:
        Passing None for existence or permissions raises ValueError.
    """
    with pytest.raises(ValueError):
        scan_bind(existence=None, permissions="create")

    with pytest.raises(ValueError):
        scan_bind(existence=Existence.unique, permissions=None)


def test_scan_duplicate_binding_raises() -> None:
    """
    Purpose:
        Ensure duplicate binding keys raise during scan binding.
    Contract:
        Two decorated classes with the same frame/binding raise RuntimeError.
    """
    spellbook = _make_spellbook()
    module = _make_module("scan_bind_mod_dup")

    @scan_bind(
        existence=Existence.unique,
        permissions="create",
        spellframe="dup_frame",
        binding_name="primary",
    )
    class Alpha:
        pass

    @scan_bind(
        existence=Existence.unique,
        permissions="create",
        spellframe="dup_frame",
        binding_name="primary",
    )
    class Beta:
        pass

    Alpha.__module__ = module.__name__
    Beta.__module__ = module.__name__
    module.Alpha = Alpha
    module.Beta = Beta

    with pytest.raises(RuntimeError):
        spellbook.scan(module)


def test_conduit_scan_after_conjure() -> None:
    """
    Purpose:
        Confirm Conduit.scan delegates to Spellbook after conjure.
    Contract:
        Conduit.scan binds decorated objects and returns spell IDs.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure()
    module = _make_module("scan_bind_mod_conduit")

    @scan_bind(existence=Existence.unique, permissions="create")
    class ConduitSpell:
        pass

    ConduitSpell.__module__ = module.__name__
    module.ConduitSpell = ConduitSpell

    spell_ids = conduit.scan(module)

    assert len(spell_ids) == 1
    assert len(spellbook.spells) == 1
