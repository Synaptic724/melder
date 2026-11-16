"""
Integration regressions (STORY-2026-11-16-spellmap_miss_waits, GitHub #329; epic #328): a SpellMap consumer bound
before its provider waits for it, as a class-annotated consumer does, instead of being refused.

Reported from MelderOps on 0.2.8302: its configure conjures its root, then binds a batch in which `SpectrumBuilders`
(`SpellMap(spellframe="spectrum", binding_name="ServiceBuilder")`) comes before `ServiceBuilder`, and the bind raised
"SpellCrafter Phase 3: SpellMap default could not be resolved" from its commit-time compile. The owner's rule
(2026-11-16): bind order must not matter. A SpellMap default that matches nothing is now an UNRESOLVED_INPUT socket at
the SpellMap's address - at a late bind and at conjure - so the bind succeeds, the consumer's meld raises
UnresolvedInputError naming the SpellMap until a provider is bound there (or the value is supplied), and the bind of
that provider re-gates the consumer. The reproduction before the fix:
context_compass/artifacts/bind_order_free_20261116/runs/spellmap_bind_order_check_0_2_8302.txt.

Every world is a fresh Aether (autouse fixture) with creation caching off.
"""
from collections.abc import Iterator
from typing import Any

import pytest

from melder import Aether, Conduit, Spellbook, SpellMap
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


class Anchor:
    """An unrelated spell, so a root has something to conjure before the batch."""


class ServiceBuilder:
    """The provider SpectrumBuilders asks for, filed at ('spectrum', 'ServiceBuilder') or bound bare."""


class CommandCenterConfig:
    """The provider CommandCenter asks for, filed at ('spectrum', 'CommandCenterConfig')."""


class SpectrumBuilders:
    """Asks for its builder by frame address - the spell MelderOps binds before ServiceBuilder."""

    def __init__(
            self,
            service_builder: Any = SpellMap(spellframe="spectrum", binding_name="ServiceBuilder"),
    ) -> None:
        """Hold the builder."""
        self.service_builder = service_builder


class CommandCenter:
    """Asks for its configuration by frame address - the second consumer of the reported configure."""

    def __init__(
            self,
            config: Any = SpellMap(spellframe="spectrum", binding_name="CommandCenterConfig"),
    ) -> None:
        """Hold the configuration."""
        self.config = config


class ByClassMap:
    """Asks for ServiceBuilder through the class form of a SpellMap: ServiceBuilder bound bare."""

    def __init__(self, service_builder: Any = SpellMap(ServiceBuilder)) -> None:
        """Hold the builder."""
        self.service_builder = service_builder


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and reset it again afterwards."""
    _reset_aether()
    yield
    _reset_aether()


def _book(frame: str, mode: str = "dynamic") -> Spellbook:
    """
    A Book on its own frame, one phase worker, not conjured.

    Args:
        frame: The frame name; each world uses its own.
        mode: "dynamic" or "automatic" - the frame's posture.

    Returns:
        Spellbook: The Book.
    """
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(system_state=mode, system_caching_enabled=False, disposal=None,
                                disposal_method_names=None)
    return book


def _conjured(frame: str) -> tuple[Spellbook, Conduit]:
    """A dynamic Book with only Anchor bound, conjured - the state MelderOps' batch of late binds starts from."""
    book = _book(frame)
    book.bind(spell=Anchor, existence="many", permissions="create")
    return book, book.conjure(name="root", dynamic=True)


def _unsupplied(root: Conduit, consumer: type, param: str) -> str:
    """
    Meld a consumer that must miss `param`; return its UnresolvedInputError's sentence.

    Returns:
        str: The text after "(parameter '<param>'): "; otherwise "<Type>: <message>" for another RuntimeError, or
        "no error" when the meld built the consumer.
    """
    try:
        root.meld(consumer)
    except UnresolvedInputError as error:
        return str(error).split(f"(parameter '{param}'): ", 1)[-1]
    except RuntimeError as error:
        return f"{type(error).__name__}: {error}"
    return "no error"


def _waiting(consumer: str, param: str, spell_map: str) -> str:
    """The UnresolvedInputError sentence of a SpellMap parameter whose address has nothing bound."""
    return (
        f"{consumer}.{param} asks for the spell its default {spell_map} names, but nothing is bound there and this "
        f"meld did not supply it. Supply it with override={{{param!r}: ...}} when melding {consumer}, a path key "
        f"ending in '>{param}' (or '**{param}') when {consumer} is built as a dependency, or bind a spell at that "
        "address."
    )


def test_spellmap_consumer_bound_before_its_provider_binds_and_melds_once_the_provider_is_bound() -> None:
    """
    Regression (MelderOps, 0.2.8302): after conjure, SpectrumBuilders is bound before ServiceBuilder. The bind
    succeeds; the meld raises UnresolvedInputError naming the SpellMap and builds nothing; once ServiceBuilder is
    bound at ('spectrum', 'ServiceBuilder') the consumer's next meld wires it.
    """
    book, root = _conjured("late-frame-named")
    book.bind(spell=SpectrumBuilders, existence="many", permissions="create")
    assert _unsupplied(root, SpectrumBuilders, "service_builder") == _waiting(
        "SpectrumBuilders", "service_builder", "SpellMap(spellframe='spectrum', binding_name='ServiceBuilder')")
    book.bind(spell=ServiceBuilder, existence="many", permissions="create", spellframe="spectrum",
              binding_name="ServiceBuilder")
    assert type(root.meld(SpectrumBuilders).service_builder) is ServiceBuilder


def test_configure_batch_binds_every_spellmap_consumer_before_its_provider() -> None:
    """
    The reported configure shape: one batch bound after conjure, each SpellMap consumer before its provider
    (SpectrumBuilders before ServiceBuilder, CommandCenter before CommandCenterConfig). Every bind succeeds, and after
    the batch both consumers meld with their providers.
    """
    book, root = _conjured("configure-batch")
    book.bind(spell=SpectrumBuilders, existence="many", permissions="create")
    book.bind(spell=CommandCenter, existence="many", permissions="create")
    book.bind(spell=ServiceBuilder, existence="many", permissions="create", spellframe="spectrum",
              binding_name="ServiceBuilder")
    book.bind(spell=CommandCenterConfig, existence="many", permissions="create", spellframe="spectrum",
              binding_name="CommandCenterConfig")
    assert type(root.meld(SpectrumBuilders).service_builder) is ServiceBuilder
    assert type(root.meld(CommandCenter).config) is CommandCenterConfig


def test_class_form_spellmap_waits_for_its_class_bound_bare_later() -> None:
    """
    `SpellMap(ServiceBuilder)` bound after conjure, with ServiceBuilder bound nowhere: the bind succeeds, the meld
    names `SpellMap(ServiceBuilder)`, and once ServiceBuilder is bound bare the consumer melds with it.
    """
    book, root = _conjured("late-class-form")
    book.bind(spell=ByClassMap, existence="many", permissions="create")
    assert _unsupplied(root, ByClassMap, "service_builder") == _waiting(
        "ByClassMap", "service_builder", "SpellMap(ServiceBuilder)")
    book.bind(spell=ServiceBuilder, existence="many", permissions="create")
    assert type(root.meld(ByClassMap).service_builder) is ServiceBuilder


def test_conjure_with_nothing_at_the_address_succeeds_and_a_meld_override_supplies_it() -> None:
    """
    An automatic Book with SpectrumBuilders alone conjures (before 0.2.8303 it raised PhaseExecutionError for the
    'local_frame' phase); the meld refuses naming the SpellMap, and an override supplies the value by identity.
    """
    book = _book("conjure-empty-address", "automatic")
    book.bind(spell=SpectrumBuilders, existence="many", permissions="create")
    root = book.conjure(name="root")
    assert _unsupplied(root, SpectrumBuilders, "service_builder") == _waiting(
        "SpectrumBuilders", "service_builder", "SpellMap(spellframe='spectrum', binding_name='ServiceBuilder')")
    builder = ServiceBuilder()
    assert root.meld(SpectrumBuilders, override={"service_builder": builder}).service_builder is builder
