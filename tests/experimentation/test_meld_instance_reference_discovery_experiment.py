"""Characterize instance-reference Meld lookup before extending purge discovery."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, ClassVar, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)

if TYPE_CHECKING:
    from melder.aether.conduit.spell_space.spell_space import SpellSpace


class ReferenceResource:
    """
    Purpose: Observe construction, returned identity and normal disposal.
    Contract: Own no external resources; the fixture resets the construction counter.
    """

    constructions: ClassVar[int] = 0

    def __init__(self, marker: int = 0) -> None:
        """
        Purpose: Distinguish new construction from lookup or singleton reuse.
        Args: marker: Plain input retained for resolution assertions.
        Contract: Increment the shared test counter once per construction.
        Returns: None.
        """
        ReferenceResource.constructions += 1
        self.marker = marker
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose: Make retained many entries participate in existing disposal tracking.
        Contract: Record a call without destroying observable test state.
        Returns: None.
        """
        self.cleanup_calls += 1


class ReferenceFrame:
    """
    Purpose: Supply a logical frame distinct from the concrete resource name.
    Contract: Used only as a binding address; never constructed by these tests.
    """


class UnhashableReferenceResource(ReferenceResource):
    """
    Purpose: Exercise instance lookup when its input cannot be cached as a dict key.
    Contract: Inherit construction behavior and explicitly disable instance hashing.
    """

    __hash__ = None


def make_reference_resource() -> ReferenceResource:
    """
    Purpose: Return a product whose type name differs from its registered factory name.
    Contract: Construct one ordinary resource without registering its class separately.
    Returns: ReferenceResource with the factory marker.
    """
    return ReferenceResource(marker=42)


@pytest.fixture
def reference_book() -> Iterator[Spellbook]:
    """
    Purpose: Give each experiment a fresh dynamic runtime with disposal enabled.
    Contract: Reset singleton references and counters; callers close their scopes
        before this fixture cleans the book and resets the world. No external I/O.
    Yields: Spellbook accepting the experiment's bindings before conjure.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    ReferenceResource.constructions = 0
    book = _make_spellbook(dynamic=True, disposal=True)
    try:
        yield book
    finally:
        if not book.cleaned:
            book.cleanup()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Aether()


@contextmanager
def _caller(
        book: Spellbook,
        *,
        spellspace: bool,
) -> Iterator[Union[Conduit, SpellSpace]]:
    """
    Purpose: Exercise the same selector through either public facade.
    Args:
        book: Borrowed book whose bindings are ready to conjure.
        spellspace: Select a manual SpellSpace instead of the root conduit.
    Contract: Own the created scopes and close the space before the root on exit.
    Yields: The real public scope object, with no mocked resolution machinery.
    """
    root = book.conjure(dynamic=True)
    try:
        if spellspace:
            space = root.create_spellspace()
            try:
                yield space
            finally:
                space.cleanup()
        else:
            yield root
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize(
    ("spellspace", "existence"),
    [
        (False, Existence.unique),
        (False, Existence.unique_per_conduit),
        (False, Existence.many),
        (True, Existence.unique),
        (True, Existence.unique_per_spell_space),
        (True, Existence.many),
    ],
)
def test_instance_selects_the_binding_then_obeys_its_existence(
        reference_book: Spellbook,
        spellspace: bool,
        existence: Existence,
) -> None:
    """
    Purpose: Separate pure reference discovery from the actual Meld result.
    Contract: Lookup returns the bound definition without construction. Public
        meld(instance) reuses singleton entries and creates another many instance.
    Args: reference_book: Isolated book; spellspace: Facade; existence: Lifetime.
    Returns: None; assertions prove lookup and returned object identity separately.
    """
    spell_id = reference_book.bind(spell=ReferenceResource, existence=existence)
    with _caller(reference_book, spellspace=spellspace) as caller:
        original = caller.meld(spell_id=spell_id, override={"marker": 17})
        before = ReferenceResource.constructions
        selected = caller._meld._resolve_spell(
            spell=original, spell_name=None, spellframe=None, binding_name=None,
        )
        assert selected is reference_book._spells_by_id[spell_id]
        assert ReferenceResource.constructions == before
        resolved = caller.meld(original)
        if existence is Existence.many:
            assert resolved is not original
            assert resolved.marker == 0
            assert ReferenceResource.constructions == before + 1
        else:
            assert resolved is original
            assert resolved.marker == 17
            assert ReferenceResource.constructions == before


@pytest.mark.parametrize("spellspace", [False, True])
def test_named_instance_still_requires_its_binding_name(
        reference_book: Spellbook,
        spellspace: bool,
) -> None:
    """
    Purpose: Test whether the object carries its originating binding name into lookup.
    Contract: Omission fails before and after a successful explicitly named call.
    Args: reference_book: Isolated book; spellspace: Public facade under test.
    Returns: None.
    """
    spell_id = reference_book.bind(
        spell=ReferenceResource, existence="unique", binding_name="blue",
    )
    with _caller(reference_book, spellspace=spellspace) as caller:
        original = caller.meld(spell_id=spell_id)
        with pytest.raises(KeyError, match="binding='__default__'"):
            caller.meld(original)
        assert caller.meld(original, binding_name="blue") is original
        with pytest.raises(KeyError, match="binding='__default__'"):
            caller.meld(original)


@pytest.mark.parametrize("spellspace", [False, True])
@pytest.mark.parametrize("frame", ["reference-services", ReferenceFrame])
def test_framed_instance_still_requires_its_frame_address(
        reference_book: Spellbook,
        spellspace: bool,
        frame: Union[str, type],
) -> None:
    """
    Purpose: Test reference discovery when binding uses a distinct frame.
    Contract: The class-derived name misses; an explicit frame/name selects the instance.
    Args: reference_book: Isolated book; spellspace: Facade; frame: Bound frame key.
    Returns: None.
    """
    spell_id = reference_book.bind(
        spell=ReferenceResource, existence="unique", spellframe=frame, binding_name="blue",
    )
    with _caller(reference_book, spellspace=spellspace) as caller:
        original = caller.meld(spell_id=spell_id)
        with pytest.raises(KeyError, match="frame='referenceresource'"):
            caller.meld(original, binding_name="blue")
        assert caller.meld(original, spellframe=frame, binding_name="blue") is original


@pytest.mark.parametrize("spellspace", [False, True])
def test_unregistered_reference_selects_a_binding_without_becoming_its_creation(
        reference_book: Spellbook,
        spellspace: bool,
) -> None:
    """
    Purpose: Check whether instance lookup requires membership in the creations store.
    Contract: A never-registered instance selects the default binding, but Melder
        constructs and reuses its own unique object instead of adopting the input.
    Args: reference_book: Isolated book; spellspace: Public facade under test.
    Returns: None.
    """
    default_id = reference_book.bind(spell=ReferenceResource, existence="unique")
    with _caller(reference_book, spellspace=spellspace) as caller:
        outsider = ReferenceResource(marker=3)
        before = ReferenceResource.constructions
        resolved = caller.meld(outsider)
        assert resolved is not outsider
        assert resolved.marker == 0
        assert ReferenceResource.constructions == before + 1
        assert caller.meld(outsider) is resolved
        assert caller.meld(spell_id=default_id) is resolved
        assert outsider.cleanup_calls == 0


@pytest.mark.parametrize("spellspace", [False, True])
def test_reference_from_another_scope_resolves_in_the_calling_scope(
        reference_book: Spellbook,
        spellspace: bool,
) -> None:
    """
    Purpose: Determine whether an instance selector preserves its originating scope.
    Contract: The same input reference selects the other scope's own instance.
    Args: reference_book: Isolated book; spellspace: Compare spaces instead of lessers.
    Returns: None; both scopes and the root are cleaned explicitly.
    """
    existence = Existence.unique_per_spell_space if spellspace else Existence.unique_per_conduit
    spell_id = reference_book.bind(spell=ReferenceResource, existence=existence)
    root = reference_book.conjure(dynamic=True)
    left = root.create_spellspace() if spellspace else root.create_lesser_conduit()
    right = root.create_spellspace() if spellspace else root.create_lesser_conduit()
    try:
        original = left.meld(spell_id=spell_id)
        local = right.meld(spell_id=spell_id)
        assert original is not local
        assert right.meld(original) is local
        assert left.meld(local) is original
    finally:
        left.cleanup()
        right.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_bound_existing_instance_is_returned_by_reference_lookup(
        reference_book: Spellbook,
        spellspace: bool,
) -> None:
    """
    Purpose: Exercise an application-created object registered as the unique provider.
    Contract: Reference lookup returns the supplied instance without constructing another.
    Args: reference_book: Isolated book; spellspace: Public facade under test.
    Returns: None.
    """
    supplied = ReferenceResource(marker=9)
    spell_id = reference_book.bind(spell=supplied, existence="unique")
    with _caller(reference_book, spellspace=spellspace) as caller:
        before = ReferenceResource.constructions
        assert caller.meld(supplied) is supplied
        assert caller.meld(spell_id=spell_id) is supplied
        assert ReferenceResource.constructions == before


@pytest.mark.parametrize("spellspace", [False, True])
def test_factory_product_does_not_identify_its_registered_factory(
        reference_book: Spellbook,
        spellspace: bool,
) -> None:
    """
    Purpose: Exercise a created object whose class name is not its provider's address.
    Contract: A product reference misses; the factory or explicit frame name resolves.
    Args: reference_book: Isolated book; spellspace: Public facade under test.
    Returns: None.
    """
    spell_id = reference_book.bind(spell=make_reference_resource, existence="unique")
    with _caller(reference_book, spellspace=spellspace) as caller:
        product = caller.meld(spell_id=spell_id)
        assert isinstance(product, ReferenceResource)
        with pytest.raises(KeyError, match="frame='referenceresource'"):
            caller.meld(product)
        assert caller.meld(make_reference_resource) is product
        assert caller.meld(product, spellframe="make_reference_resource") is product


@pytest.mark.parametrize("spellspace", [False, True])
def test_unhashable_instance_still_resolves_without_the_input_cache(
        reference_book: Spellbook,
        spellspace: bool,
) -> None:
    """
    Purpose: Check that a reference does not need to be hashable for normal discovery.
    Contract: Repeated calls return the singleton even when input-cache keys are unusable.
    Args: reference_book: Isolated book; spellspace: Public facade under test.
    Returns: None.
    """
    spell_id = reference_book.bind(spell=UnhashableReferenceResource, existence="unique")
    with _caller(reference_book, spellspace=spellspace) as caller:
        original = caller.meld(spell_id=spell_id)
        with pytest.raises(TypeError):
            hash(original)
        assert caller.meld(original) is original
        assert caller.meld(original) is original
