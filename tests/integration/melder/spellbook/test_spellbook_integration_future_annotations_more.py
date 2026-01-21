from __future__ import annotations

import typing

import pytest
from typing import Optional, Protocol, Union

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_future_annotation_more_tests() -> None:
    """
    Purpose:
        Ensure future-annotation integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
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


class _ExtraRepo:
    """
    Purpose:
        Provide a repository spell for future-annotation tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the repository marker.
        Contract:
            Sets marker to "extra".
        Returns:
            None.
        """
        self.marker = "extra"


class _ExtraRepoAlt:
    """
    Purpose:
        Provide an alternate repository spell for SpellMap tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the alternate repository marker.
        Contract:
            Sets marker to "alt".
        Returns:
            None.
        """
        self.marker = "alt"


class _ExtraProtocol(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for list DI tests.
    Contract:
        Acts as a DI grouping key.
    """


class _ExtraHandlerA:
    """
    Purpose:
        Provide a protocol implementation for collection DI tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the handler marker.
        Contract:
            Sets marker to "A".
        Returns:
            None.
        """
        self.marker = "A"


class _ExtraHandlerB:
    """
    Purpose:
        Provide a second protocol implementation for collection DI tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the handler marker.
        Contract:
            Sets marker to "B".
        Returns:
            None.
        """
        self.marker = "B"


class _FramePrimaryRepo:
    """
    Purpose:
        Provide a primary binding for string-frame SpellMap tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the primary repository marker.
        Contract:
            Sets marker to "primary".
        Returns:
            None.
        """
        self.marker = "primary"


class _FrameSecondaryRepo:
    """
    Purpose:
        Provide a secondary binding for string-frame SpellMap tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the secondary repository marker.
        Contract:
            Sets marker to "secondary".
        Returns:
            None.
        """
        self.marker = "secondary"


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for future-annotation integration tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def test_future_annotations_optional_string_inner_resolves_by_name() -> None:
    """
    Purpose:
        Validate Optional string-inner forward refs resolve by name.
    Contract:
        - Optional["_ExtraRepo"] resolves the repository dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _OptionalStringService:
        """
        Purpose:
            Provide a service that uses Optional string-inner forward refs.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: Optional["_ExtraRepo"]) -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_OptionalStringService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ExtraRepo)
        assert instance.repo.marker == "extra"
    finally:
        conduit.cleanup()


def test_future_annotations_typing_optional_string_inner_resolves_by_name() -> None:
    """
    Purpose:
        Validate typing.Optional string-inner forward refs resolve by name.
    Contract:
        - typing.Optional["_ExtraRepo"] resolves the repository dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _TypingOptionalStringService:
        """
        Purpose:
            Provide a service that uses typing.Optional string-inner forward refs.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: typing.Optional["_ExtraRepo"]) -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_TypingOptionalStringService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ExtraRepo)
        assert instance.repo.marker == "extra"
    finally:
        conduit.cleanup()


def test_future_annotations_union_string_inner_resolves_by_name() -> None:
    """
    Purpose:
        Validate Union string-inner forward refs resolve by name.
    Contract:
        - Union["_ExtraRepo", None] resolves the repository dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _UnionStringService:
        """
        Purpose:
            Provide a service that uses Union string-inner forward refs.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: Union["_ExtraRepo", None]) -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_UnionStringService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ExtraRepo)
        assert instance.repo.marker == "extra"
    finally:
        conduit.cleanup()


def test_future_annotations_typing_union_string_inner_resolves_by_name() -> None:
    """
    Purpose:
        Validate typing.Union string-inner forward refs resolve by name.
    Contract:
        - typing.Union["_ExtraRepo", None] resolves the repository dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _TypingUnionStringService:
        """
        Purpose:
            Provide a service that uses typing.Union string-inner forward refs.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: typing.Union["_ExtraRepo", None]) -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_TypingUnionStringService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ExtraRepo)
        assert instance.repo.marker == "extra"
    finally:
        conduit.cleanup()


def test_future_annotations_list_string_inner_protocol_resolves_all() -> None:
    """
    Purpose:
        Validate list string-inner forward refs resolve protocol collections.
    Contract:
        - list["_ExtraProtocol"] injects all bound implementations.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is incomplete.
    """
    class _ListStringPipeline:
        """
        Purpose:
            Provide a pipeline that uses list string-inner forward refs.
        Contract:
            Stores the injected handlers list.
        """

        def __init__(self, handlers: list["_ExtraProtocol"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler implementations.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ExtraProtocol,
    )
    spellbook.bind(
        spell=_ExtraHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ExtraProtocol,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_ListStringPipeline,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        pipeline = conduit.meld(spell=pipeline_id)
        markers = {handler.marker for handler in pipeline.handlers}
        assert markers == {"A", "B"}
    finally:
        conduit.cleanup()


def test_future_annotations_typing_list_string_inner_protocol_resolves_all() -> None:
    """
    Purpose:
        Validate typing.List string-inner forward refs resolve protocol collections.
    Contract:
        - typing.List["_ExtraProtocol"] injects all bound implementations.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is incomplete.
    """
    class _TypingListStringPipeline:
        """
        Purpose:
            Provide a pipeline that uses typing.List string-inner forward refs.
        Contract:
            Stores the injected handlers list.
        """

        def __init__(self, handlers: typing.List["_ExtraProtocol"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler implementations.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ExtraProtocol,
    )
    spellbook.bind(
        spell=_ExtraHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ExtraProtocol,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_TypingListStringPipeline,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        pipeline = conduit.meld(spell=pipeline_id)
        markers = {handler.marker for handler in pipeline.handlers}
        assert markers == {"A", "B"}
    finally:
        conduit.cleanup()


def test_future_annotations_list_string_spellframe_resolves_all() -> None:
    """
    Purpose:
        Validate list string-literal spellframes resolve collections.
    Contract:
        - list["extra_frame"] injects all bound implementations for that frame.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is incomplete.
    """
    class _StringFramePipeline:
        """
        Purpose:
            Provide a pipeline that uses a string-literal spellframe list.
        Contract:
            Stores the injected implementations list.
        """

        def __init__(self, handlers: list["extra_frame"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler implementations.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_FramePrimaryRepo,
        existence=Existence.unique,
        permissions="create",
        spellframe="extra_frame",
    )
    spellbook.bind(
        spell=_FrameSecondaryRepo,
        existence=Existence.unique,
        permissions="create",
        spellframe="extra_frame",
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_StringFramePipeline,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        pipeline = conduit.meld(spell=pipeline_id)
        markers = {handler.marker for handler in pipeline.handlers}
        assert markers == {"primary", "secondary"}
    finally:
        conduit.cleanup()


def test_future_annotations_string_literal_frame_annotation_resolves_single() -> None:
    """
    Purpose:
        Validate string-literal spellframe annotations resolve single DI.
    Contract:
        - "extra_frame" annotations resolve to the bound spellframe.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _StringFrameService:
        """
        Purpose:
            Provide a service that uses a string-literal spellframe annotation.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: "extra_frame") -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_FramePrimaryRepo,
        existence=Existence.unique,
        permissions="create",
        spellframe="extra_frame",
    )
    service_id = spellbook.bind(
        spell=_StringFrameService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FramePrimaryRepo)
        assert instance.repo.marker == "primary"
    finally:
        conduit.cleanup()


def test_future_annotations_spellmap_default_string_frame_binding_resolves_specific() -> None:
    """
    Purpose:
        Validate SpellMap defaults resolve specific string-frame bindings.
    Contract:
        - SpellMap with binding_name selects the matching implementation.
    Returns:
        None.
    Raises:
        AssertionError: If the binding selection fails.
    """
    class _BindingService:
        """
        Purpose:
            Provide a service with a SpellMap default and string-frame binding.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(
            self,
            repo: "Missing" = SpellMap(
                spell=None,
                spellframe="extra_frame",
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_FramePrimaryRepo,
        existence=Existence.unique,
        permissions="create",
        spellframe="extra_frame",
        binding_name="primary",
    )
    spellbook.bind(
        spell=_FrameSecondaryRepo,
        existence=Existence.unique,
        permissions="create",
        spellframe="extra_frame",
        binding_name="secondary",
    )
    service_id = spellbook.bind(
        spell=_BindingService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FramePrimaryRepo)
        assert instance.repo.marker == "primary"
    finally:
        conduit.cleanup()


def test_future_annotations_spellmap_default_explicit_spell_ignores_string_annotation() -> None:
    """
    Purpose:
        Validate explicit SpellMap defaults override unresolved annotations.
    Contract:
        - SpellMap explicit spell selection is honored.
    Returns:
        None.
    Raises:
        AssertionError: If the explicit SpellMap spell is not injected.
    """
    class _ExplicitSpellService:
        """
        Purpose:
            Provide a service that uses a SpellMap explicit spell default.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: "Missing" = SpellMap(_ExtraRepoAlt)) -> None:
            """
            Purpose:
                Capture the injected repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = _make_spellbook()
    spellbook.bind(
        spell=_ExtraRepo,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=_ExtraRepoAlt,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_ExplicitSpellService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ExtraRepoAlt)
        assert instance.repo.marker == "alt"
    finally:
        conduit.cleanup()
