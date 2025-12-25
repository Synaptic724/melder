import inspect
from typing import Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.bind import Bind
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_bind() -> None:
    """
    Purpose:
        Reset the Aether singleton for component Bind tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component Bind tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def test_component_bind_creates_class_spell_with_metadata() -> None:
    """
    Purpose:
        Validate Bind produces a fully populated class Spell.
    Contract:
        - Spell metadata reflects the bound class and binding profile.
        - SpellIndex points at the computed spell_id.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)
    try:
        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=BasicService,
        )

        assert spell.spell is BasicService
        assert spell.spell_type is SpellType.SPELL
        assert spell.spell_name == "BasicService"
        assert spell.existence is Existence.unique
        assert spell.permissions is Permissions.create
        assert spell.spell_index.current == spell.spell_id
        assert spell.spell_index.has_version(spell.spell_id) is True
        assert isinstance(spell.profile, ClassBindingProfile)
        assert spell._spellbook is spellbook
        assert Bind.spell_id_inspector(BasicService) == spell.spell_id
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_enforces_protocol_members_for_class_spellframe() -> None:
    """
    Purpose:
        Validate protocol spellframes enforce required class members.
    Contract:
        - Classes missing protocol members raise TypeError.
        - Classes implementing the protocol bind successfully.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    class IServiceContract(Protocol):
        def ping(self) -> str:
            ...

    class Good:
        def ping(self) -> str:
            return "ok"

    class Bad:
        pass

    try:
        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=Good,
            spellframe=IServiceContract,
        )
        assert spell.spellframe is IServiceContract

        with pytest.raises(TypeError):
            binder.bind(
                Permissions.create,
                Existence.unique,
                aetheric_frame="default",
                spell=Bad,
                spellframe=IServiceContract,
            )
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_lambda_requires_binding_name() -> None:
    """
    Purpose:
        Validate lambda spells require explicit binding names.
    Contract:
        - Lambdas without binding_name raise ValueError.
        - Named lambdas are classified as lambda spell types.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)
    try:
        with pytest.raises(ValueError):
            binder.bind(
                Permissions.create,
                Existence.unique,
                aetheric_frame="default",
                spell=lambda x: x,
            )

        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=lambda x: x,
            binding_name="lam",
        )
        assert spell.spell_type is SpellType.LAMBDA_METHOD_WITH_BINDING_NAME
        assert isinstance(spell.profile, CallableBindingProfile)
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_existing_object_requires_unique_existence() -> None:
    """
    Purpose:
        Validate existing objects require Existence.unique.
    Contract:
        - Non-unique existences raise ValueError.
        - Unique existences create EXISTING_CREATION spells.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)
    instance = BasicService()
    try:
        with pytest.raises(ValueError):
            binder.bind(
                Permissions.create,
                Existence.many,
                aetheric_frame="default",
                spell=instance,
            )

        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=instance,
            binding_name="inst",
        )
        assert spell.spell_type is SpellType.EXISTING_CREATION
        assert spell.user_created_object is instance
        assert isinstance(spell.profile, InstanceBindingProfile)
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_rejects_module_spells() -> None:
    """
    Purpose:
        Validate Bind rejects module bindings.
    Contract:
        - Modules raise TypeError when bound as spells.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)
    try:
        with pytest.raises(TypeError):
            binder.bind(
                Permissions.create,
                Existence.unique,
                aetheric_frame="default",
                spell=inspect,
            )
    finally:
        binder.cleanup()
        spellbook.cleanup()
