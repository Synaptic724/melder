"""Native registration capability contracts; runtime enforcement is qualified separately."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from types import ModuleType
from typing import Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.internal_registration_error import (
    InternalRegistrationError,
)


class RegistrationService:
    """Ordinary class whose registration needs no constructor execution."""


class AbstractDefinition(ABC):
    """Application abstraction retained for inspection without constructing it."""

    @abstractmethod
    def render(self) -> str:
        """Return a representation supplied by a concrete implementation."""


class ProtocolDefinition(Protocol):
    """Application Protocol with a real shared render contract."""

    def render(self) -> str:
        """Return the implementation's representation."""


def registered_function() -> str:
    """Return a fixed value if invoked; registration must not invoke this function."""
    return "function"


@pytest.fixture
def book() -> Iterator[Spellbook]:
    """Own a small isolated world and retire its book and singleton after each test."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(aetheric_frame="resolvable-registration")
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    try:
        yield spellbook
    finally:
        spellbook.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def active_spell(book: Spellbook, spell_id: str) -> Spell:
    """Return the selected local record and fail if registration did not publish it."""
    spell = book.find_spell_by_id(spell_id)
    assert spell is not None
    assert spell.spell_id == spell_id
    return spell


@pytest.mark.parametrize("mode", ["omitted", "true", "false"])
def test_resolvable_is_native_and_described_without_metadata_leak(book: Spellbook, mode: str) -> None:
    """Capability is immutable registration data; ordinary metadata remains independent."""
    options = {} if mode == "omitted" else {"resolvable": mode == "true"}
    spell_id = book.bind(spell=RegistrationService, existence="unique", owner_team="tools", **options)
    spell = active_spell(book, spell_id)
    assert spell.resolvable is (mode != "false")
    assert spell.metadata == {"owner_team": "tools"}
    rows = book.describe_spells_in_spellbook()
    assert len(rows) == 1
    assert rows[0]["spell_id"] == spell_id
    assert rows[0]["resolvable"] is (mode != "false")
    with pytest.raises(AttributeError):
        spell.resolvable = mode == "false"


@pytest.mark.parametrize("resolvable", [True, False])
def test_inspector_and_real_bind_agree_on_effective_inputs(book: Spellbook, resolvable: bool) -> None:
    """The inspector uses the same capability and effective naming inputs as a real bind."""
    expected = Bind.spell_id_inspector(
        RegistrationService, spell_name="RegistrationService", spellframe="services",
        binding_name="sample", existence=Existence.unique, resolvable=resolvable,
    )
    actual = book.bind(
        spell=RegistrationService, spellframe="services", binding_name="sample",
        existence="unique", resolvable=resolvable,
    )
    assert actual == expected


@pytest.mark.parametrize("invalid", [None, 0, 1, "false", [], {}])
def test_non_bool_capability_refuses_without_publishing(book: Spellbook, invalid: object) -> None:
    """Truthiness must not turn configuration mistakes into a different registration policy."""
    with pytest.raises(TypeError, match="resolvable.*bool"):
        book.bind(spell=RegistrationService, existence="unique", resolvable=invalid)
    assert book.describe_spells_in_spellbook() == []


@pytest.mark.parametrize("inspector", [False, True])
def test_invalid_capability_is_rejected_before_user_reflection(book: Spellbook, inspector: bool) -> None:
    """Independent bind and inspection reject invalid policy before observing a user's object."""
    observations: list[str] = []

    class ObservedInstance:
        """Report representation requests made during binding-profile reflection."""

        def __repr__(self) -> str:
            """Record a user-visible reflection effect and return a stable description."""
            observations.append("repr")
            return "ObservedInstance"

    target = ObservedInstance()
    with pytest.raises(TypeError, match="resolvable.*bool"):
        if inspector:
            Bind.spell_id_inspector(target, resolvable=0)
        else:
            book.bind(spell=target, existence="unique", resolvable=0)
    assert observations == []


@pytest.mark.parametrize("decorator", [False, True])
def test_bind_gateway_preserves_false_for_direct_and_decorator_paths(book: Spellbook, decorator: bool) -> None:
    """Both internal gateway call forms return the same native policy on their Spell record."""
    gateway = Bind(book)
    spell = None
    try:
        if decorator:
            decorate = gateway.bind(
                Permissions.create, Existence.unique,
                aetheric_frame="resolvable-registration", resolvable=False,
            )
            spell = decorate(RegistrationService)
        else:
            spell = gateway.bind(
                Permissions.create, Existence.unique, spell=RegistrationService,
                aetheric_frame="resolvable-registration", resolvable=False,
            )
        assert spell.resolvable is False
        assert spell.spell is RegistrationService
        assert spell.metadata == {}
    finally:
        # Direct Bind produces an unregistered record; the test owns its teardown.
        if spell is not None:
            spell._spellbook_cleanup = True
            spell.spell_index.cleanup()
            spell.cleanup()
        gateway.cleanup()


@pytest.mark.parametrize("through_kwargs", [False, True])
def test_fluent_capability_does_not_leak_to_next_registration(book: Spellbook, through_kwargs: bool) -> None:
    """Finalize and a fresh bind clear the prior capability choice with other staged kwargs."""
    binder = SpellBinder(book)
    try:
        if through_kwargs:
            first_id = binder.bind(RegistrationService).named("first").with_kwargs(resolvable=False).finalize()
        else:
            first_id = binder.bind(RegistrationService, binding_name="first", resolvable=False).finalize()
        second_id = binder.bind(RegistrationService, binding_name="second").finalize()
        assert active_spell(book, first_id).resolvable is False
        assert active_spell(book, second_id).resolvable is True
        binder.bind(RegistrationService, resolvable=False)
        third_id = binder.bind(RegistrationService, binding_name="third").finalize()
        assert active_spell(book, third_id).resolvable is True
    finally:
        binder.cleanup()


@pytest.mark.parametrize("through_conduit", [False, True])
@pytest.mark.parametrize("active_mode", [False, True])
def test_parked_capability_is_per_version_and_does_not_change_selection(
    book: Spellbook, through_conduit: bool, active_mode: bool,
) -> None:
    """Both facades keep parked policy separate from the selected member of the shared index."""
    # Conjure first: S2 tests registration transport, before S3 adds non-resolvable root compilation.
    conduit = book.conjure(dynamic=True, name="registration-host")
    surface = conduit if through_conduit else book
    active_id = surface.bind(spell=RegistrationService, existence="unique", resolvable=active_mode)
    selected = active_spell(book, active_id)
    parked_id = surface.bind_inactive(
        spell=RegistrationService, spell_index=selected.spell_index,
        existence="unique", resolvable=not active_mode,
    )
    assert parked_id != active_id
    assert selected.resolvable is active_mode
    assert selected.spell_index.selected_spell_id == active_id
    # Public find_spell_by_id follows the selected member; use the exact parked record here.
    parked = book._inactive_spells[parked_id]
    assert parked.resolvable is (not active_mode)
    assert parked.metadata == {}
    assert {row["spell_id"] for row in book.describe_spells_in_spellbook()} == {active_id}


def test_false_does_not_create_another_active_binding_slot(book: Spellbook) -> None:
    """Distinct capability fingerprints still obey the existing active signature claim."""
    original_id = book.bind(spell=RegistrationService, existence="unique")
    with pytest.raises(RuntimeError, match="Binding signature already active"):
        book.bind(spell=RegistrationService, existence="unique", resolvable=False)
    assert active_spell(book, original_id).resolvable is True
    definition_id = book.bind(
        spell=RegistrationService, existence="unique", binding_name="definition", resolvable=False,
    )
    assert {row["spell_id"] for row in book.describe_spells_in_spellbook()} == {original_id, definition_id}


@pytest.mark.parametrize("through_conduit", [False, True])
def test_inactive_bind_defaults_to_true_independently_of_selected_mode(
    book: Spellbook, through_conduit: bool,
) -> None:
    """Omitting the staged mode must not inherit False from another member of its index."""
    conduit = book.conjure(dynamic=True, name="registration-host")
    surface = conduit if through_conduit else book
    active_id = surface.bind(spell=RegistrationService, existence="unique", resolvable=False)
    selected = active_spell(book, active_id)
    parked_id = surface.bind_inactive(
        spell=RegistrationService, spell_index=selected.spell_index, existence="unique",
    )
    assert book._inactive_spells[parked_id].resolvable is True
    assert selected.resolvable is False
    assert selected.spell_index.selected_spell_id == active_id


@pytest.mark.parametrize("target", [AbstractDefinition, ProtocolDefinition])
def test_abstract_and_protocol_definitions_can_be_registered_false(book: Spellbook, target: type) -> None:
    """A non-resolvable definition retains its real target and profile without construction."""
    spell_id = book.bind(spell=target, existence="unique", resolvable=False)
    spell = active_spell(book, spell_id)
    assert spell.resolvable is False
    assert spell.spell is target
    assert spell.profile.binding_profile.original_object is target
    assert spell.profile.binding_profile.name == target.__name__


@pytest.mark.parametrize("mode", ["omitted", "true"])
def test_protocol_target_still_refuses_resolvable_registration(book: Spellbook, mode: str) -> None:
    """The exception for descriptive Protocol records does not admit them as concrete providers."""
    options = {} if mode == "omitted" else {"resolvable": True}
    with pytest.raises(TypeError, match="Cannot bind Protocol"):
        book.bind(spell=ProtocolDefinition, existence="unique", **options)


def test_false_does_not_bypass_protocol_spellframe_admission(book: Spellbook) -> None:
    """Only the Protocol-as-target refusal changes; a declared interface still requires its members."""
    with pytest.raises(TypeError, match="Missing members: render"):
        book.bind(
            spell=RegistrationService, spellframe=ProtocolDefinition, existence="unique", resolvable=False,
        )


@pytest.mark.parametrize("family", ["function", "lambda", "instance"])
def test_false_preserves_supported_callable_and_instance_families(book: Spellbook, family: str) -> None:
    """The capability applies to supported targets without changing their type or unique lifetime."""
    target = registered_function if family == "function" else (
        (lambda: "lambda") if family == "lambda" else RegistrationService()
    )
    spell_id = book.bind(spell=target, binding_name="reference", existence="unique", resolvable=False)
    spell = active_spell(book, spell_id)
    assert spell.resolvable is False
    assert spell.spell is target
    assert spell.existence is Existence.unique
    if family == "instance":
        assert spell.user_created_object is target


@pytest.mark.parametrize("family", ["function", "instance"])
def test_false_does_not_relax_unique_only_lifetimes(book: Spellbook, family: str) -> None:
    """No new creation or ownership semantics come from disabling resolution."""
    target = registered_function if family == "function" else RegistrationService()
    with pytest.raises(ValueError, match="Existence.unique"):
        book.bind(spell=target, existence="many", resolvable=False)


def test_false_keeps_kernel_module_and_primitive_refusals(book: Spellbook) -> None:
    """A discovery flag does not bypass the public registration boundary."""
    with pytest.raises(InternalRegistrationError):
        book.bind(spell=Spellbook, existence="unique", resolvable=False)
    with pytest.raises(TypeError, match="Cannot bind module"):
        book.bind(spell=ModuleType("candidate"), existence="unique", resolvable=False)
    with pytest.raises(TypeError, match="primitive"):
        book.bind(spell=42, existence="unique", resolvable=False)


def test_cleaned_spell_does_not_expose_live_capability(book: Spellbook) -> None:
    """The read-only policy follows the Spell's existing cleaned-object contract."""
    spell_id = book.bind(spell=RegistrationService, existence="unique", resolvable=False)
    spell = active_spell(book, spell_id)
    book.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = spell.resolvable
