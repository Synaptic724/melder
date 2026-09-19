"""Native provider ownership regressions for borrower validation and teardown.

These minimal runtime contracts complement the unchanged CommandOps GraphCache
acceptance tests. Each prefix receives a fresh world and one final provider
lookup, so an earlier diagnostic lookup cannot repair a later failing prefix.
"""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


class RetainedProvider:
    """Own a resource-free list whose identity and contents survive borrower work."""

    def __init__(self) -> None:
        """Initialize state once per provider-owned unique creation."""
        self.entries: list[str] = []


class ProviderConsumer:
    """Borrow a required provider instance without acquiring its lifecycle."""

    def __init__(self, provider: RetainedProvider) -> None:
        """Retain the injected provider for identity and state assertions."""
        self.provider = provider


class ProviderRuntime:
    """Own all books in one isolated runtime and clean them in reverse order.

    The provider is melded once during setup. Subsequent provider lookups belong
    exclusively to each test's final assertion boundary.
    """

    def __init__(self) -> None:
        """Initialize ownership fields before any runtime allocation can fail."""
        self.books: list[Spellbook] = []
        self.frame_name = "provider-artifact-ownership-regression"
        self.provider: Optional[Conduit] = None
        self.original: Optional[RetainedProvider] = None
        self.provider_spell: Optional[Spell] = None
        self.provider_id: Optional[str] = None

    def cleanup(self) -> None:
        """Retire borrowers before the provider, including failed setup paths."""
        for book in reversed(self.books):
            if not book.cleaned:
                if book.conduit is None:
                    book.cleanup()
                else:
                    book.conduit.cleanup()
        self.books.clear()
        self.provider = None
        self.original = None
        self.provider_spell = None

    def new_book(self) -> Spellbook:
        """Retain each new book before any later configuration or binding step."""
        book = Spellbook(aetheric_frame=self.frame_name)
        self.books.append(book)
        return book

    def start(self) -> None:
        """Construct the original unique provider with caching disabled."""
        book = self.new_book()
        book.configure_aether_frame(
            system_state="dynamic", system_caching_enabled=False,
            disposal=None, disposal_method_names=None,
        )
        book.get_configuration().freeze()
        self.provider_id = book.bind(
            spell=RetainedProvider, existence="unique",
            spellframe="providers", binding_name="retained",
        )
        self.provider = book.conjure(dynamic=True, name="provider")
        self.original = self.provider.meld(spellframe="providers", binding_name="retained")
        self.original.entries.append("provider-owned")
        self.provider_spell = self.provider.get_spell_by_id(self.provider_id, self.frame_name)

    def create_borrower(self, name: str) -> Conduit:
        """Link and import read access, then bind the required consumer locally."""
        book = self.new_book()
        book.get_configuration().freeze()
        borrower = book.conjure(dynamic=True, name=name)
        assert borrower.link(self.provider)
        assert borrower.add_spell_to_contract(
            spell_id=self.provider_id, conduit=self.provider,
            aetheric_frame=self.frame_name, permissions="read",
        )
        assert borrower.find_contracted_spell(self.provider_id) is self.provider_spell
        borrower.bind(
            spell=ProviderConsumer, existence="many",
            spellframe="consumers", binding_name=name,
        )
        return borrower

    def assert_provider_usable(self) -> None:
        """Perform the final provider meld and verify original definition and data."""
        assert self.provider.get_spell_by_id(self.provider_id, self.frame_name) is self.provider_spell
        assert self.provider.meld(spellframe="providers", binding_name="retained") is self.original
        assert self.original.entries == ["provider-owned"]


@pytest.fixture
def provider_runtime() -> Iterator[ProviderRuntime]:
    """Isolate the singleton host and release the complete owned runtime after each case."""
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    runtime = ProviderRuntime()
    try:
        runtime.start()
        yield runtime
    finally:
        try:
            runtime.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            world = Aether()
            Spellbook._aether = world
            Conduit._aether = world


@pytest.mark.parametrize("stop_after", (
    "consumer-book", "consumer-configuration-freeze", "empty-conjure", "link",
    "contract", "late-bind", "validate-resolution", "consumer-meld",
))
def test_provider_survives_independent_borrower_operation_prefix(
        provider_runtime: ProviderRuntime,
        stop_after: str,
) -> None:
    """Keep provider artifacts usable after precisely one independent public prefix."""
    runtime = provider_runtime
    book = runtime.new_book()
    if stop_after == "consumer-book":
        runtime.assert_provider_usable()
        return
    book.get_configuration().freeze()
    if stop_after == "consumer-configuration-freeze":
        runtime.assert_provider_usable()
        return
    borrower = book.conjure(dynamic=True, name="consumer")
    if stop_after == "empty-conjure":
        runtime.assert_provider_usable()
        return
    assert borrower.link(runtime.provider)
    if stop_after == "link":
        runtime.assert_provider_usable()
        return
    assert borrower.add_spell_to_contract(
        spell_id=runtime.provider_id, conduit=runtime.provider,
        aetheric_frame=runtime.frame_name, permissions="read",
    )
    if stop_after == "contract":
        runtime.assert_provider_usable()
        return
    borrower.bind(
        spell=ProviderConsumer, existence="many",
        spellframe="consumers", binding_name="consumer",
    )
    if stop_after == "late-bind":
        runtime.assert_provider_usable()
        return
    assert borrower.validate_resolution(refresh_structural=True) is not None
    if stop_after == "consumer-meld":
        consumer = borrower.meld(spellframe="consumers", binding_name="consumer")
        assert consumer.provider is runtime.original
    runtime.assert_provider_usable()


@pytest.mark.parametrize("borrower_count,validation_count", ((1, 1), (1, 3), (2, 2)))
def test_provider_survives_repeated_borrower_validation_and_cleanup(
        provider_runtime: ProviderRuntime,
        borrower_count: int,
        validation_count: int,
) -> None:
    """Preserve provider identity/state through repeated and independent borrower lifecycles."""
    runtime = provider_runtime
    borrowers = [
        (f"consumer-{index}", runtime.create_borrower(f"consumer-{index}"))
        for index in range(borrower_count)
    ]
    for _ in range(validation_count):
        for name, borrower in borrowers:
            assert borrower.validate_resolution(refresh_structural=True) is not None
            consumer = borrower.meld(spellframe="consumers", binding_name=name)
            assert consumer.provider is runtime.original
    for _name, borrower in reversed(borrowers):
        borrower.cleanup()
    runtime.assert_provider_usable()


@pytest.mark.parametrize("validate_explicitly", (True, False), ids=("resolution_only", "implicit_meld"))
def test_provider_survives_resolution_only_and_implicit_local_compilation(
        provider_runtime: ProviderRuntime,
        validate_explicitly: bool,
) -> None:
    """Preserve provider ownership through both explicit and lazy local compilation paths."""
    runtime = provider_runtime
    borrower = runtime.create_borrower("consumer-boundary")
    if validate_explicitly:
        borrower.validate_resolution(refresh_structural=False)
    consumer = borrower.meld(spellframe="consumers", binding_name="consumer-boundary")
    assert consumer.provider is runtime.original
    borrower.cleanup()
    runtime.assert_provider_usable()


def test_provider_survives_same_book_local_consumer_compilation(
        provider_runtime: ProviderRuntime,
) -> None:
    """Keep an owned dependency usable when local compilation rebuilds only a consumer.

    The consumer is bound after conjure and melded through the normal lazy
    compilation path. The provider is probed only at the final boundary so a
    diagnostic meld cannot repair a later observation.
    """
    runtime = provider_runtime
    consumer_id = runtime.provider.bind(
        spell=ProviderConsumer, existence="many",
        spellframe="consumers", binding_name="local-consumer",
    )
    consumer = runtime.provider.meld(spell_id=consumer_id)
    assert consumer.provider is runtime.original
    runtime.assert_provider_usable()
