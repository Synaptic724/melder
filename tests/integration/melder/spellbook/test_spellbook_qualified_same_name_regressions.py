"""Regress qualified spell addresses through real bind, conjure and meld paths.

Every book uses an isolated frame with disk caching disabled. Same-named classes
must retain independent addresses and identities; true address conflicts remain
registration errors even when one registration is discoverable only.
"""

from collections.abc import Iterator
from typing import Optional
from uuid import uuid4

import pytest

from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class ModuleA:
    """First namespace containing a class named Repo."""

    class Repo:
        """First independently addressable implementation."""

        def __init__(self) -> None:
            """Create an inert instance whose concrete type identifies its binding."""


class ModuleB:
    """Second namespace containing an unrelated class with the same name."""

    class Repo:
        """Second independently addressable implementation."""

        def __init__(self) -> None:
            """Create an inert instance whose concrete type identifies its binding."""


@pytest.fixture(params=["automatic", "dynamic"])
def qualified_book(request: pytest.FixtureRequest) -> Iterator[Spellbook]:
    """Yield one frame-isolated book in each posture and clean it after the test.

    Configuration is frozen before binding; caching is disabled so the current
    validator must run. Tests clean their created root before this book teardown.
    """
    frame = f"qualified-spells-{uuid4().hex}"
    configuration = SpellbookConfiguration(aether_frame=frame)
    configuration.with_defaults()
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    book.configure_aether_frame(
        system_state=request.param,
        ai_native=False,
        rift_enabled=False,
        system_caching_enabled=False,
        disposal=None,
        disposal_method_names=None,
    )
    configuration.freeze()
    try:
        yield book
    finally:
        book.cleanup()


@pytest.mark.parametrize(
    "first_frame,first_binding,second_frame,second_binding",
    [
        ("users", None, "orders", None),
        ("repos", "first", "repos", "second"),
        ("users", "first", "orders", "second"),
        (None, None, None, "secondary"),
    ],
)
def test_same_named_classes_conjure_and_resolve_by_distinct_addresses(
    qualified_book: Spellbook,
    first_frame: Optional[str],
    first_binding: Optional[str],
    second_frame: Optional[str],
    second_binding: Optional[str],
) -> None:
    """Both registered types resolve by id and qualified address after conjure.

    Repeated lookups cover warmed resolution too; each result must have the
    exact registered class, not merely its shared display name.
    """
    first_id = qualified_book.bind(
        spell=ModuleA.Repo, spellframe=first_frame, binding_name=first_binding, existence="many",
    )
    second_id = qualified_book.bind(
        spell=ModuleB.Repo, spellframe=second_frame, binding_name=second_binding, existence="many",
    )
    root = qualified_book.conjure(name="qualified-root")
    try:
        for _ in range(2):
            assert type(root.meld(spell_id=first_id)) is ModuleA.Repo
            assert type(root.meld(spell_id=second_id)) is ModuleB.Repo
            assert type(root.meld("Repo", spellframe=first_frame, binding_name=first_binding)) is ModuleA.Repo
            assert type(root.meld("Repo", spellframe=second_frame, binding_name=second_binding)) is ModuleB.Repo
    finally:
        root.cleanup()


def test_discoverable_same_name_does_not_break_resolvable_twin(qualified_book: Spellbook) -> None:
    """A descriptive twin at another address permits conjure but still refuses meld."""
    first_id = qualified_book.bind(spell=ModuleA.Repo, spellframe="users", existence="many")
    descriptive_id = qualified_book.bind(
        spell=ModuleB.Repo, spellframe="orders", existence="many", resolvable=False,
    )
    root = qualified_book.conjure(name="discoverable-root")
    try:
        assert type(root.meld(spell_id=first_id)) is ModuleA.Repo
        assert type(root.meld(spellframe="USERS")) is ModuleA.Repo
        with pytest.raises(MeldExecutionError):
            root.meld(spell_id=descriptive_id)
    finally:
        root.cleanup()


@pytest.mark.parametrize("resolvable", [True, False])
def test_same_normalized_address_still_refused_at_bind(
    qualified_book: Spellbook, resolvable: bool,
) -> None:
    """Case variants cannot evade address ownership, including discoverable entries."""
    qualified_book.bind(
        spell=ModuleA.Repo, spellframe="REPOS", binding_name="PRIMARY",
        existence="many", resolvable=resolvable,
    )
    with pytest.raises(RuntimeError, match="Binding signature already active"):
        qualified_book.bind(
            spell=ModuleB.Repo, spellframe="repos", binding_name="primary", existence="many",
        )
