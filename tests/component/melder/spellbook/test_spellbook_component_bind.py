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
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
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
        assert isinstance(spell.profile, SpellGeneralProfile)
        assert isinstance(spell.profile.binding_profile, ClassBindingProfile)
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
        assert isinstance(spell.profile, SpellGeneralProfile)
        assert isinstance(spell.profile.binding_profile, CallableBindingProfile)
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
        assert isinstance(spell.profile, SpellGeneralProfile)
        assert isinstance(spell.profile.binding_profile, InstanceBindingProfile)
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_can_attach_detailed_profile_for_class_spell() -> None:
    """
    Purpose:
        Validate Bind can attach the detailed profile for class spells.
    Contract:
        - `.profile` is a SpellDetailedProfile when requested explicitly.
        - The detailed profile still carries the class binding profile.
        - The detailed inspection payloads and resolution profile are populated.
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
            profile="detailed",
        )

        assert isinstance(spell.profile, SpellDetailedProfile)
        assert isinstance(spell.profile.binding_profile, ClassBindingProfile)
        assert spell.profile.class_profile is not None
        assert spell.profile.callable_profile is not None
        assert spell.profile.resolution_profile is not None
        assert spell.profile.resolution_profile.spell_id == spell.spell_index.current
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_can_attach_detailed_profile_for_callable_spell() -> None:
    """
    Purpose:
        Validate Bind can attach the detailed profile for callable spells.
    Contract:
        - `.profile` is a SpellDetailedProfile when requested explicitly.
        - Callable spells keep callable binding and callable inspector payloads.
        - Class-only inspector payloads remain absent.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    def build_service() -> BasicService:
        return BasicService()

    try:
        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=build_service,
            profile="detailed",
        )

        assert isinstance(spell.profile, SpellDetailedProfile)
        assert isinstance(spell.profile.binding_profile, CallableBindingProfile)
        assert spell.profile.class_profile is None
        assert spell.profile.callable_profile is not None
        assert spell.profile.resolution_profile is not None
        assert spell.profile.resolution_profile.spell_id == spell.spell_index.current
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


def test_component_bind_decorator_creates_spell_with_binding_metadata() -> None:
    """
    Purpose:
        Validate decorator-style Bind usage produces a Spell with metadata.
    Contract:
        - Decorator returns a Spell instance.
        - Binding name and spellframe influence spell type.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    class DecoratedService:
        def __init__(self) -> None:
            self.marker = "decorated"

    try:
        decorator = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spellframe="decorator-frame",
            binding_name="decorator-name",
        )
        spell = decorator(DecoratedService)
        assert spell.spell is DecoratedService
        assert spell.spellframe == "decorator-frame"
        assert spell.binding_name == "decorator-name"
        assert spell.spell_type is SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_rejects_protocol_as_spell() -> None:
    """
    Purpose:
        Validate Protocols cannot be bound as concrete spells.
    Contract:
        - Binding a Protocol class raises TypeError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    class IService(Protocol):
        def ping(self) -> str:
            ...

    try:
        with pytest.raises(TypeError, match="Protocol"):
            binder.bind(
                Permissions.create,
                Existence.unique,
                aetheric_frame="default",
                spell=IService,
            )
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_callable_under_protocol_spellframe_is_allowed() -> None:
    """
    Purpose:
        Validate callable spells can use Protocol spellframes without structural checks.
    Contract:
        - Callable bound under a Protocol spellframe succeeds.
        - Spell type reflects callable + binding name + spellframe.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    class IServiceFactory(Protocol):
        def build(self) -> BasicService:
            ...

    def factory() -> BasicService:
        return BasicService(marker="factory")

    try:
        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=factory,
            spellframe=IServiceFactory,
            binding_name="factory",
        )
        assert spell.spellframe is IServiceFactory
        assert spell.spell_type is SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_function_without_binding_name_uses_method_spell_type() -> None:
    """
    Purpose:
        Validate callable spells without binding metadata use METHOD spell type.
    Contract:
        - Function bindings default to METHOD spell type when unnamed.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    def build_service() -> BasicService:
        return BasicService(marker="built")

    try:
        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=build_service,
        )
        assert spell.spell_type is SpellType.METHOD
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_class_with_spellframe_only_sets_spell_type() -> None:
    """
    Purpose:
        Validate class bindings with a spellframe use SPELL_WITH_SPELLFRAME.
    Contract:
        - Spell type reflects spellframe-only classification.
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
            spellframe="frame-only",
        )
        assert spell.spell_type is SpellType.SPELL_WITH_SPELLFRAME
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_class_with_binding_name_only_sets_spell_type() -> None:
    """
    Purpose:
        Validate class bindings with a binding name use SPELL_WITH_BINDING_NAME.
    Contract:
        - Spell type reflects binding-name-only classification.
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
            binding_name="named",
        )
        assert spell.spell_type is SpellType.SPELL_WITH_BINDING_NAME
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_existing_object_with_spellframe_and_name_sets_spell_type() -> None:
    """
    Purpose:
        Validate existing-object bindings honor spellframe + binding name metadata.
    Contract:
        - Existing object uses EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)
    instance = BasicService(marker="existing")
    try:
        spell = binder.bind(
            Permissions.create,
            Existence.unique,
            aetheric_frame="default",
            spell=instance,
            spellframe="existing-frame",
            binding_name="existing-name",
        )
        assert spell.user_created_object is instance
        assert spell.spell_type is SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_callable_with_non_unique_existence_raises() -> None:
    """
    Purpose:
        Validate callable spells reject non-unique existence modes.
    Contract:
        - Non-unique existence raises ValueError for callables.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    binder = Bind(spellbook)

    def factory() -> BasicService:
        return BasicService()

    try:
        with pytest.raises(ValueError):
            binder.bind(
                Permissions.create,
                Existence.many,
                aetheric_frame="default",
                spell=factory,
            )
    finally:
        binder.cleanup()
        spellbook.cleanup()


def test_component_bind_lambda_with_spellframe_and_name_sets_spell_type() -> None:
    """
    Purpose:
        Validate lambdas with spellframe + binding name use the correct spell type.
    Contract:
        - Lambda bindings with spellframe and name use LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME.
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
            spell=lambda: BasicService(),
            spellframe="lambda-frame",
            binding_name="lambda-name",
        )
        assert spell.spell_type is SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME
    finally:
        binder.cleanup()
        spellbook.cleanup()
