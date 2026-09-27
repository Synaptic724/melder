"""Python 3.14 deferred annotations preserve normal DI and selected defaults.

The dependency import exists only for static checking. Tests deliberately use
native deferred evaluation, without a future import or runtime fallback alias.
"""

import inspect
from typing import TYPE_CHECKING, Optional

import pytest

from melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)
from tests.mocks.spellbook.core_classes import BasicService as RuntimeService

if TYPE_CHECKING:
    from tests.mocks.spellbook.core_classes import BasicService


class DeferredConsumer:
    """Request a required provider through a TYPE_CHECKING-only annotation."""

    def __init__(self, service: BasicService) -> None:
        """Retain the exact injected provider for identity assertions."""
        self.service = service


class DeferredCollectionConsumer:
    """Request a collection containing an unresolved annotation name."""

    def __init__(self, services: list[BasicService]) -> None:
        """Retain all resolved providers in constructor order."""
        self.services = services


class DeferredNoneDefault:
    """An unresolved type name must not prevent honoring an ordinary None default."""

    def __init__(self, service: Optional[BasicService] = None) -> None:
        """Retain the selected default without inferring a provider dependency."""
        self.service = service


class DeferredChosenDefault:
    """Keep an existing selected default distinct from a registered class provider."""

    selected = RuntimeService()

    def __init__(self, service: BasicService = selected) -> None:
        """Retain the exact chosen default object."""
        self.service = service


class LiteralNameConsumer:
    """Control for the already-supported literal forward-name form."""

    def __init__(self, service: "BasicService") -> None:
        """Deliberately retain a literal string annotation as the compatibility control."""
        self.service = service


def deferred_consumer_factory(service: BasicService) -> DeferredConsumer:
    """A function binding must preserve deferred parameter annotations too."""
    return DeferredConsumer(service)


@pytest.mark.parametrize("kind", ("class", "function", "collection"))
@pytest.mark.parametrize("late_bind", (False, True))
def test_typechecking_dependency_resolves_before_and_after_conjure(
        instance_book: Spellbook, kind: str, late_bind: bool,
) -> None:
    """Exercise real bind/conjure/meld with unresolved scalar and nested type names."""
    provider_id = instance_book.bind(spell=RuntimeService, existence="unique")
    root = instance_book.conjure(dynamic=True) if late_bind else None
    consumer_type = {"class": DeferredConsumer, "function": deferred_consumer_factory,
                     "collection": DeferredCollectionConsumer}[kind]
    target = instance_book.bind(spell=consumer_type, existence="unique")
    if root is None:
        root = instance_book.conjure(dynamic=True)
    result = root.meld(spell_id=target)
    # Query the instance created by consumer DI without starting a second
    # compilation path; provider-remeld invalidation has its own regression lane.
    provider = root.meld_existing_spell(spell=provider_id)
    if kind == "collection":
        assert len(result.services) == 1
        assert result.services[0] is provider
    else:
        assert result.service is provider


@pytest.mark.parametrize("selected", (False, True), ids=("none", "chosen_instance"))
def test_typechecking_annotation_preserves_default(instance_book: Spellbook, selected: bool) -> None:
    """A matching provider must not replace an ordinary default with a deferred annotation."""
    provider_id = instance_book.bind(spell=RuntimeService, existence="unique")
    target = instance_book.bind(spell=DeferredChosenDefault if selected else DeferredNoneDefault, existence="many")
    root = instance_book.conjure(dynamic=True)
    result = root.meld(spell_id=target)
    assert result.service is (DeferredChosenDefault.selected if selected else None)
    assert not root.has_live_creation(spell=provider_id)


def test_typechecking_dependency_without_provider_is_a_required_meld_input(instance_book: Spellbook) -> None:
    """
    An unresolved name without a provider stays a required input, never an empty requirement.

    Conjure succeeds; the meld must supply the value. Omitting it raises
    UnresolvedInputError naming the TYPE_CHECKING-only type by its written name.
    """
    target = instance_book.bind(spell=DeferredConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    with pytest.raises(UnresolvedInputError) as caught:
        root.meld(spell_id=target)
    assert caught.value.expected_type == "BasicService"
    assert caught.value.unresolved_params == ("service",)
    supplied = RuntimeService("supplied")
    assert root.meld(spell_id=target, override={"service": supplied}).service is supplied


@pytest.mark.parametrize("late_bind", (False, True))
@pytest.mark.parametrize("defaulted", (False, True))
def test_typechecking_annotation_accepts_explicit_override(
        instance_book: Spellbook, late_bind: bool, defaulted: bool,
) -> None:
    """Runtime override specialization preserves caller identity for deferred annotations."""
    provider_id = instance_book.bind(spell=RuntimeService, existence="unique")
    root = instance_book.conjure(dynamic=True) if late_bind else None
    target = instance_book.bind(spell=DeferredNoneDefault if defaulted else DeferredConsumer, existence="many")
    if root is None:
        root = instance_book.conjure(dynamic=True)
    replacement = RuntimeService("replacement")
    result = root.meld(spell_id=target, override={"service": replacement})
    assert result.service is replacement
    if defaulted:
        assert not root.has_live_creation(spell=provider_id)


def test_literal_forward_annotation_still_resolves(instance_book: Spellbook) -> None:
    """Preserve the existing literal-string annotation path alongside native deferred evaluation."""
    provider_id = instance_book.bind(spell=RuntimeService, existence="unique")
    target = instance_book.bind(spell=LiteralNameConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=target).service is root.meld(spell_id=provider_id)


def test_resolved_signature_keeps_binding_fingerprint_text() -> None:
    """Normal resolved signatures retain the text used by existing bind fingerprints."""
    profile = BindingProfileStrategy().build_profile(RuntimeService)
    try:
        assert profile.init_signature_object == inspect.signature(RuntimeService)
        assert profile.init_signature == str(inspect.signature(RuntimeService))
    finally:
        profile.cleanup()
