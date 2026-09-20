"""Characterize Optional[Something] = None through real public Melder calls.

These tests record current behavior, including the missing-provider refusal.
They do not change dependency resolution policy or suppress production errors.
"""

from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar, Optional, Union

import pytest

from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.meld.contracts.spell_map import SpellMap

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
    from melder.aether.conduit.conduit import Conduit


class Something:
    """A constructible provider whose identity can be checked after injection."""

    def __init__(self, marker: str = "injected-provider") -> None:
        """Mark the provider as a real constructed object without external work."""
        self.marker: str = marker


class NeedsOptionalSomething:
    """Consumer with the exact Optional user-class annotation and None default."""

    def __init__(self, dependency: Optional[Something] = None) -> None:
        """Retain the actual constructor argument for public behavior assertions."""
        self.dependency: Optional[Something] = dependency


class PlainOptionalDefault:
    """Control: a builtin object annotation is plain data rather than class DI."""

    def __init__(self, dependency: Optional[object] = None) -> None:
        """Retain the argument so the original None default remains observable."""
        self.dependency: Optional[object] = dependency


class ScalarDefaults:
    """Control for ordinary and falsy Python defaults that do not request class DI."""

    def __init__(
            self,
            count: int = 42,
            zero: int = 0,
            ratio: float = 1.5,
            enabled: bool = False,
            label: str = "selected",
            empty: str = "",
            items: tuple[int, ...] = (1, 2),
            maybe: Optional[int] = None,
    ) -> None:
        """Expose exactly what the constructor received without altering any values."""
        self.values = (count, zero, ratio, enabled, label, empty, items, maybe)


class SelectedInstanceDefault:
    """Consumer with an explicit, valid user-owned instance as its Python default.

    The class owns the resource-free marker instance. Tests borrow it without
    mutation; the runtime must not confuse it with a Melder-created provider.
    """

    DEFAULT_DEPENDENCY: ClassVar[Something] = Something("selected-default")

    def __init__(self, dependency: Something = DEFAULT_DEPENDENCY) -> None:
        """Retain the selected argument for comparison with the declared default."""
        self.dependency = dependency


class ExplicitMapDefault:
    """Control for an explicit DI request expressed through a SpellMap default."""

    def __init__(self, dependency: Union[Something, SpellMap] = SpellMap(Something)) -> None:
        """Retain the injected provider or unresolved descriptor for the test to inspect."""
        self.dependency = dependency


class OptionalResolutionRuntime:
    """Own one isolated book/frame/root and report the current public-call stage.

    The fixture cleans the root, book and frame even when binding or conjure
    fails. Each test receives fresh state and disables disk caching, recording
    and Nexus publication. No production methods are patched.
    """

    def __init__(self, mode: str) -> None:
        """Initialize runtime ownership and configure the selected lifecycle mode."""
        self.mode = mode
        self.stage = "setup"
        self._cleaned = False
        self.book = Spellbook(aetheric_frame=f"optional_none_experiment_{mode}")
        self.frame: AethericFrame = self.book._aetheric_frame
        self.conduit: Optional[Conduit] = None
        self.book.configure_aether_frame(
            system_state="automatic" if mode == "automatic_prebind" else "dynamic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
            ai_native=False,
            rift_enabled=False,
        )
        assert not self.book._crystallizer.activated
        if mode == "dynamic_postbind":
            self.ensure_conduit()

    def cleanup(self) -> None:
        """Release owned runtime surfaces in order, including failed-setup state."""
        if self._cleaned:
            return
        self._cleaned = True
        try:
            if self.conduit is not None:
                self.conduit.permanent_cleanup()
        finally:
            try:
                if not self.book.cleaned:
                    self.book.cleanup()
            finally:
                if not self.frame.cleaned:
                    self.frame.cleanup()
        del self.conduit
        del self.book
        del self.frame

    def bind_provider(self, registration: str) -> str:
        """Register exactly one Something, optionally with lookup qualifiers."""
        self.stage = "bind_provider"
        return self.book.bind(
            spell=Something,
            existence="unique",
            binding_name="test" if registration != "default" else None,
            spellframe="ProviderFrame" if registration == "named_and_framed" else None,
        )

    def bind_consumer(self, consumer_type: type) -> str:
        """Register the consumer and retain the stage if bind-time validation fails."""
        self.stage = "bind_consumer"
        return self.book.bind(spell=consumer_type, existence="unique")

    def ensure_conduit(self) -> Conduit:
        """Conjure once, recording that stage if structural validation refuses."""
        if self.conduit is None:
            self.stage = "conjure"
            self.conduit = self.book.conjure(dynamic=self.mode != "automatic_prebind")
        return self.conduit


@pytest.fixture(params=("automatic_prebind", "dynamic_prebind", "dynamic_postbind"))
def optional_runtime(request: pytest.FixtureRequest) -> Iterator[OptionalResolutionRuntime]:
    """Give each case an isolated, explicitly cleaned runtime with the requested mode."""
    runtime = OptionalResolutionRuntime(str(request.param))
    try:
        yield runtime
    finally:
        runtime.cleanup()


@pytest.mark.parametrize("registration", ("default", "named", "named_and_framed"))
def test_registered_class_is_injected_despite_optional_none_default(
        optional_runtime: OptionalResolutionRuntime,
        registration: str,
) -> None:
    """Prove one matching provider is injected instead of leaving the default None.

    The provider has no live instance before the consumer meld. The injected
    object must be the exact existing instance retrieved by its registered
    SHA, including named and differently framed registrations. The reuse-only
    query avoids initiating an unrelated provider-root compile after injection.
    """
    provider_id = optional_runtime.bind_provider(registration)
    consumer_id = optional_runtime.bind_consumer(NeedsOptionalSomething)
    conduit = optional_runtime.ensure_conduit()
    assert not conduit.has_live_creation(spell=provider_id)
    optional_runtime.stage = "meld"
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, NeedsOptionalSomething)
    assert isinstance(consumer.dependency, Something)
    assert consumer.dependency.marker == "injected-provider"
    assert consumer.dependency is conduit.meld_existing_spell(spell=provider_id)
    print(f"{optional_runtime.mode}/{registration}: Optional[Something] = None received the registered Something")


def test_missing_optional_provider_currently_fails_instead_of_using_none(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Characterize the current missing-provider behavior, not an intended fallback.

    Phase 1 records optionality, but the current single-candidate resolver still
    rejects zero matches. Capture the public stage and message for the owner.
    """
    with pytest.raises(RuntimeError, match="no DI candidate found for parameter 'dependency'") as failure:
        consumer_id = optional_runtime.bind_consumer(NeedsOptionalSomething)
        conduit = optional_runtime.ensure_conduit()
        optional_runtime.stage = "meld"
        conduit.meld(spell_id=consumer_id)
    print(
        f"{optional_runtime.mode}/absent: {type(failure.value).__name__} "
        f"during {optional_runtime.stage}: {failure.value}"
    )


def test_plain_optional_object_default_stays_none_with_provider_registered(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Prove a plain-value optional annotation preserves None without creating Something."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(PlainOptionalDefault)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, PlainOptionalDefault)
    assert consumer.dependency is None
    assert not conduit.has_live_creation(spell=provider_id)
    print(f"{optional_runtime.mode}/plain Optional[object] = None: None retained, Something not created")


def test_numeric_falsy_and_other_plain_defaults_are_preserved(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Prove concrete scalar defaults survive even with an unrelated provider registered."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(ScalarDefaults)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, ScalarDefaults)
    assert consumer.values == (42, 0, 1.5, False, "selected", "", (1, 2), None)
    assert not conduit.has_live_creation(spell=provider_id)
    print(f"{optional_runtime.mode}/scalar defaults: {consumer.values!r}")


def test_registered_provider_currently_replaces_a_selected_instance_default(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Characterize the same precedence defect with a non-None, correctly typed default."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(SelectedInstanceDefault)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, SelectedInstanceDefault)
    assert consumer.dependency is not SelectedInstanceDefault.DEFAULT_DEPENDENCY
    assert consumer.dependency.marker == "injected-provider"
    assert consumer.dependency is conduit.meld_existing_spell(spell=provider_id)
    print(f"{optional_runtime.mode}/instance default: selected-default was replaced by injected-provider")


def test_selected_instance_default_without_provider_currently_still_refuses(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Prove a usable explicit default does not currently rescue missing inferred class DI."""
    with pytest.raises(RuntimeError, match="no DI candidate found for parameter 'dependency'") as failure:
        consumer_id = optional_runtime.bind_consumer(SelectedInstanceDefault)
        conduit = optional_runtime.ensure_conduit()
        optional_runtime.stage = "meld"
        conduit.meld(spell_id=consumer_id)
    print(
        f"{optional_runtime.mode}/instance default without provider: "
        f"{type(failure.value).__name__} during {optional_runtime.stage}"
    )


def test_explicit_spellmap_default_requests_injection(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Verify the existing descriptor gives callers an explicit way to request DI."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(ExplicitMapDefault)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, ExplicitMapDefault)
    assert isinstance(consumer.dependency, Something)
    assert consumer.dependency is conduit.meld_existing_spell(spell=provider_id)
    print(f"{optional_runtime.mode}/SpellMap default: explicit DI injected Something")
