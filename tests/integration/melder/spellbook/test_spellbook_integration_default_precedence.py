"""Regress ordinary constructor defaults taking precedence over inferred DI.

These assert the owner-selected contract established by the red baseline.
Ordinary defaults are PLAIN; explicit descriptors still request DI.
No skip/xfail markers hide the bug, and production methods are not patched.
"""

from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar, Optional, Union

import pytest

from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)

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


class CollectionDefaults:
    """Resource-free collection defaults borrowed intact by each consumer.

    Tests never mutate the class-owned lists. Their contents must neither be
    replaced with registered providers nor become inferred collection sockets.
    """

    SELECTED: ClassVar[list[Something]] = [Something("selected-list")]
    EMPTY: ClassVar[list[Something]] = []

    def __init__(
            self,
            selected: list[Something] = SELECTED,
            empty: list[Something] = EMPTY,
            nullable: Optional[list[Something]] = None,
    ) -> None:
        """Borrow the supplied lists and nullable value without copying or mutating them."""
        self.selected = selected
        self.empty = empty
        self.nullable = nullable


class ExplicitContractDefault:
    """An explicit contract descriptor must retain its contract DI classification."""

    def __init__(
            self,
            dependency: Union[Something, SpellContract] = SpellContract(spellframe=Something),
    ) -> None:
        """Retain the provider or contract supplied through the explicit descriptor."""
        self.dependency = dependency


class RequiresSomething:
    """No default: the constructor still requires inferred class DI."""

    def __init__(self, dependency: Something) -> None:
        """Retain the required injected argument for identity assertions."""
        self.dependency = dependency


class RequiresNullableSomething:
    """Nullable type without a default still requires a supplied constructor argument."""

    def __init__(self, dependency: Optional[Something]) -> None:
        """Retain the argument; Optional alone must not disable inferred DI."""
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
def test_none_default_is_preserved_with_registered_provider(
        optional_runtime: OptionalResolutionRuntime,
        registration: str,
) -> None:
    """An ordinary None default must survive regardless of provider registration.

    The provider must remain uncreated: retaining None must also eliminate
    the inferred dependency edge, not merely replace the constructor argument
    after unnecessarily creating a provider.
    """
    provider_id = optional_runtime.bind_provider(registration)
    consumer_id = optional_runtime.bind_consumer(NeedsOptionalSomething)
    conduit = optional_runtime.ensure_conduit()
    assert not conduit.has_live_creation(spell=provider_id)
    optional_runtime.stage = "meld"
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, NeedsOptionalSomething)
    assert consumer.dependency is None, "An ordinary None default must beat inferred class DI."
    assert not conduit.has_live_creation(spell=provider_id)


def test_none_default_needs_no_registered_provider(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Binding/conjure/meld must succeed using None without an inferred provider edge."""
    consumer_id = optional_runtime.bind_consumer(NeedsOptionalSomething)
    conduit = optional_runtime.ensure_conduit()
    optional_runtime.stage = "meld"
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, NeedsOptionalSomething)
    assert consumer.dependency is None


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


def test_selected_instance_default_is_preserved_with_registered_provider(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Use the exact user-selected object and leave the unrelated provider uncreated."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(SelectedInstanceDefault)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, SelectedInstanceDefault)
    assert consumer.dependency is SelectedInstanceDefault.DEFAULT_DEPENDENCY
    assert consumer.dependency.marker == "selected-default"
    assert not conduit.has_live_creation(spell=provider_id)


def test_selected_instance_default_needs_no_registered_provider(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """A valid instance default must work even when its class has no registered provider."""
    consumer_id = optional_runtime.bind_consumer(SelectedInstanceDefault)
    conduit = optional_runtime.ensure_conduit()
    optional_runtime.stage = "meld"
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, SelectedInstanceDefault)
    assert consumer.dependency is SelectedInstanceDefault.DEFAULT_DEPENDENCY


@pytest.mark.parametrize("register_provider", (False, True))
def test_collection_defaults_preserve_identity_without_inferred_providers(
        optional_runtime: OptionalResolutionRuntime,
        register_provider: bool,
) -> None:
    """Preserve selected, empty and nullable list defaults with or without a provider."""
    provider_id = optional_runtime.bind_provider("default") if register_provider else None
    consumer_id = optional_runtime.bind_consumer(CollectionDefaults)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, CollectionDefaults)
    assert consumer.selected is CollectionDefaults.SELECTED
    assert consumer.empty is CollectionDefaults.EMPTY
    assert consumer.nullable is None
    if provider_id is not None:
        assert not conduit.has_live_creation(spell=provider_id)


@pytest.mark.parametrize("consumer_type", (NeedsOptionalSomething, SelectedInstanceDefault))
def test_explicit_override_replaces_plain_default_without_creating_provider(
        optional_runtime: OptionalResolutionRuntime,
        consumer_type: type,
) -> None:
    """An explicit meld override wins over a PLAIN default without restoring inferred DI."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(consumer_type)
    selected_override = Something("explicit-override")
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id, override={"dependency": selected_override})
    assert consumer.dependency is selected_override
    assert not conduit.has_live_creation(spell=provider_id)


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


@pytest.mark.parametrize("consumer_type", (RequiresSomething, RequiresNullableSomething))
def test_annotation_without_default_still_requests_injection(
        optional_runtime: OptionalResolutionRuntime,
        consumer_type: type,
) -> None:
    """Guard ordinary and nullable required parameters against disabling DI too broadly."""
    provider_id = optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(consumer_type)
    conduit = optional_runtime.ensure_conduit()
    consumer = conduit.meld(spell_id=consumer_id)
    assert isinstance(consumer, (RequiresSomething, RequiresNullableSomething))
    assert isinstance(consumer.dependency, Something)
    assert consumer.dependency is conduit.meld_existing_spell(spell=provider_id)


def test_required_dependency_without_provider_still_refuses(
        optional_runtime: OptionalResolutionRuntime,
) -> None:
    """Guard the existing no-provider failure for a parameter with no Python default."""
    with pytest.raises(RuntimeError, match="no DI candidate found for parameter 'dependency'"):
        consumer_id = optional_runtime.bind_consumer(RequiresSomething)
        conduit = optional_runtime.ensure_conduit()
        conduit.meld(spell_id=consumer_id)


@pytest.mark.parametrize("optional_runtime", ("dynamic_prebind",), indirect=True)
@pytest.mark.parametrize(
    "consumer_type, expected_shape",
    (
        pytest.param(NeedsOptionalSomething, ParameterDIShape.PLAIN, id="none-default-is-plain"),
        pytest.param(SelectedInstanceDefault, ParameterDIShape.PLAIN, id="instance-default-is-plain"),
        pytest.param(ExplicitMapDefault, ParameterDIShape.SPELLMAP_DEFAULT, id="explicit-spellmap"),
        pytest.param(ExplicitContractDefault, ParameterDIShape.SPELL_CONTRACT, id="explicit-contract"),
    ),
)
def test_default_precedence_is_classified_before_graph_construction(
        optional_runtime: OptionalResolutionRuntime,
        consumer_type: type,
        expected_shape: ParameterDIShape,
) -> None:
    """Assert the agreed Phase-1 contract, rather than hiding an unwanted DI edge later.

    Bind's completed profile exposes the requirements artifact before conjure.
    Provider presence must not make an ordinary default become inferred DI.
    """
    optional_runtime.bind_provider("default")
    consumer_id = optional_runtime.bind_consumer(consumer_type)
    profile = optional_runtime.book._spell_id_pool[consumer_id].profile
    requirements = profile.resolution_profile.requirements
    assert requirements is not None
    parameter = next(item for item in requirements.parameters if item.name == "dependency")
    assert parameter.di_shape is expected_shape
