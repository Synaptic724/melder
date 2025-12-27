from __future__ import annotations

import typing

import pytest
from typing import Optional, Protocol, Union

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_future_annotation_tests() -> None:
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


class _FutureLateService:
    """
    Purpose:
        Provide a service that depends on a later-defined repository.
    Contract:
        Stores the injected repository instance.
    """

    def __init__(self, repo: _FutureLateRepo) -> None:
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


class _FutureLateRepo:
    """
    Purpose:
        Provide a repository spell for forward-ref tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the repository marker.
        Contract:
            Sets marker to "future".
        Returns:
            None.
        """
        self.marker = "future"


class _FutureProtocol(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for future-annotation DI.
    Contract:
        Acts as a DI grouping key.
    """


class _FutureHandlerA:
    """
    Purpose:
        Provide a handler implementation for future-annotation list DI.
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


class _FutureHandlerB:
    """
    Purpose:
        Provide a second handler implementation for future-annotation list DI.
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


class _FuturePipeline:
    """
    Purpose:
        Provide a pipeline that collects handlers via list DI.
    Contract:
        Stores the injected handlers list.
    """

    def __init__(self, handlers: list[_FutureProtocol]) -> None:
        """
        Purpose:
            Capture the injected handlers list.
        Contract:
            Stores the handlers on the instance.
        Args:
            handlers: Injected handler instances.
        Returns:
            None.
        """
        self.handlers = handlers


class _FutureFrame:
    """
    Purpose:
        Provide a class-based spellframe for forward-ref list DI.
    Contract:
        Acts as a DI grouping key.
    """


class _FutureFrameImplA:
    """
    Purpose:
        Provide a class-frame implementation for list DI.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the frame marker.
        Contract:
            Sets marker to "A".
        Returns:
            None.
        """
        self.marker = "A"


class _FutureFrameImplB:
    """
    Purpose:
        Provide another class-frame implementation for list DI.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the frame marker.
        Contract:
            Sets marker to "B".
        Returns:
            None.
        """
        self.marker = "B"


class _FutureFramePipeline:
    """
    Purpose:
        Provide a pipeline that collects class-frame implementations.
    Contract:
        Stores the injected implementations list.
    """

    def __init__(self, handlers: list[_FutureFrame]) -> None:
        """
        Purpose:
            Capture the injected class-frame handlers.
        Contract:
            Stores the handlers on the instance.
        Args:
            handlers: Injected class-frame handlers.
        Returns:
            None.
        """
        self.handlers = handlers


class _FutureOptionalService:
    """
    Purpose:
        Provide a service that uses Optional forward-ref DI.
    Contract:
        Stores the injected repository instance.
    """

    def __init__(self, repo: Optional[_FutureLateRepo]) -> None:
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


class _FutureUnionService:
    """
    Purpose:
        Provide a service that uses Union forward-ref DI.
    Contract:
        Stores the injected repository instance.
    """

    def __init__(self, repo: Union[_FutureLateRepo, None]) -> None:
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


class _FuturePep604Service:
    """
    Purpose:
        Provide a service that uses PEP 604 forward-ref DI.
    Contract:
        Stores the injected repository instance.
    """

    def __init__(self, repo: _FutureLateRepo | None) -> None:
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


class _FutureSpellMapService:
    """
    Purpose:
        Provide a service that uses SpellMap defaults with future annotations.
    Contract:
        Uses the SpellMap default for DI regardless of the annotation token.
    """

    def __init__(self, repo: "MissingType" = SpellMap(_FutureLateRepo)) -> None:
        """
        Purpose:
            Capture the injected repository from the SpellMap default.
        Contract:
            Stores the repository on the instance.
        Args:
            repo: Injected repository instance.
        Returns:
            None.
        """
        self.repo = repo


def test_future_annotations_single_di_resolves_module_forward_ref_class() -> None:
    """
    Purpose:
        Validate forward-ref class annotations resolve under future annotations.
    Contract:
        - The repository spell is injected into the service.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_FutureLateService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
        assert instance.repo.marker == "future"
    finally:
        conduit.cleanup()


def test_future_annotations_single_di_resolves_module_forward_ref_protocol() -> None:
    """
    Purpose:
        Validate forward-ref protocol annotations resolve under future annotations.
    Contract:
        - The protocol-bound spell is injected into the service.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _ProtocolConsumer:
        """
        Purpose:
            Provide a consumer that depends on a protocol spellframe.
        Contract:
            Stores the injected dependency instance.
        """

        def __init__(self, worker: _FutureProtocol) -> None:
            """
            Purpose:
                Capture the injected dependency.
            Contract:
                Stores the dependency on the instance.
            Args:
                worker: Injected protocol implementation.
            Returns:
                None.
            """
            self.worker = worker

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureProtocol,
    )
    consumer_id = spellbook.bind(
        spell=_ProtocolConsumer,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=consumer_id)
        assert isinstance(instance.worker, _FutureHandlerA)
    finally:
        conduit.cleanup()


def test_future_annotations_collection_di_protocol_list_resolves_all() -> None:
    """
    Purpose:
        Validate list DI resolves all protocol implementations under future annotations.
    Contract:
        - All bound handlers are injected into the list.
    Returns:
        None.
    Raises:
        AssertionError: If handler collection is incomplete.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureProtocol,
    )
    spellbook.bind(
        spell=_FutureHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureProtocol,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_FuturePipeline,
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


def test_future_annotations_collection_di_class_frame_list_resolves_all() -> None:
    """
    Purpose:
        Validate list DI resolves all class-frame implementations under future annotations.
    Contract:
        - All class-frame implementations are injected into the list.
    Returns:
        None.
    Raises:
        AssertionError: If handler collection is incomplete.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureFrameImplA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureFrame,
    )
    spellbook.bind(
        spell=_FutureFrameImplB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureFrame,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_FutureFramePipeline,
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


def test_future_annotations_optional_forward_ref_injects_dependency() -> None:
    """
    Purpose:
        Validate Optional forward-ref annotations still inject dependencies.
    Contract:
        - The repository instance is injected.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_FutureOptionalService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
    finally:
        conduit.cleanup()


def test_future_annotations_typing_optional_forward_ref_injects_dependency() -> None:
    """
    Purpose:
        Validate typing.Optional forward-ref annotations inject dependencies.
    Contract:
        - typing.Optional[_FutureLateRepo] resolves the repository dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _TypingOptionalService:
        """
        Purpose:
            Provide a service that uses typing.Optional forward-ref DI.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: typing.Optional[_FutureLateRepo]) -> None:
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

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_TypingOptionalService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
    finally:
        conduit.cleanup()


def test_future_annotations_union_forward_ref_injects_dependency() -> None:
    """
    Purpose:
        Validate Union forward-ref annotations still inject dependencies.
    Contract:
        - The repository instance is injected.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_FutureUnionService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
    finally:
        conduit.cleanup()


def test_future_annotations_typing_union_forward_ref_injects_dependency() -> None:
    """
    Purpose:
        Validate typing.Union forward-ref annotations inject dependencies.
    Contract:
        - typing.Union[_FutureLateRepo, None] resolves the repository dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    class _TypingUnionService:
        """
        Purpose:
            Provide a service that uses typing.Union forward-ref DI.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: typing.Union[_FutureLateRepo, None]) -> None:
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

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_TypingUnionService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
    finally:
        conduit.cleanup()


def test_future_annotations_pep604_forward_ref_injects_dependency() -> None:
    """
    Purpose:
        Validate PEP 604 forward-ref annotations still inject dependencies.
    Contract:
        - The repository instance is injected.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is missing.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_FuturePep604Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
    finally:
        conduit.cleanup()


def test_future_annotations_typing_list_forward_ref_collection_resolves_all() -> None:
    """
    Purpose:
        Validate typing.List forward-ref annotations resolve for collection DI.
    Contract:
        - typing.List[_FutureProtocol] injects all bound implementations.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is incomplete.
    """
    class _TypingListPipeline:
        """
        Purpose:
            Provide a pipeline that depends on typing.List forward-ref DI.
        Contract:
            Stores the injected handlers list.
        """

        def __init__(self, handlers: typing.List[_FutureProtocol]) -> None:
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

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureProtocol,
    )
    spellbook.bind(
        spell=_FutureHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_FutureProtocol,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_TypingListPipeline,
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


def test_future_annotations_local_optional_forward_ref_resolves_by_name() -> None:
    """
    Purpose:
        Validate Optional local forward refs resolve by name under future annotations.
    Contract:
        - Optional local dependencies are injected by spell name.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _LocalRepo:
        """
        Purpose:
            Provide a local repository spell for Optional forward-ref tests.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the local repository marker.
            Contract:
                Sets marker to "optional".
            Returns:
                None.
            """
            self.marker = "optional"

    class _LocalOptionalService:
        """
        Purpose:
            Provide a service that uses Optional local forward-ref DI.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: Optional[_LocalRepo]) -> None:
            """
            Purpose:
                Capture the injected local repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected local repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_LocalRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_LocalOptionalService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _LocalRepo)
        assert instance.repo.marker == "optional"
    finally:
        conduit.cleanup()


def test_future_annotations_local_pep604_forward_ref_resolves_by_name() -> None:
    """
    Purpose:
        Validate PEP 604 local forward refs resolve by name under future annotations.
    Contract:
        - Local dependencies declared as `_LocalRepo | None` are injected.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _LocalRepo:
        """
        Purpose:
            Provide a local repository spell for PEP 604 forward-ref tests.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the local repository marker.
            Contract:
                Sets marker to "pep604".
            Returns:
                None.
            """
            self.marker = "pep604"

    class _LocalPep604Service:
        """
        Purpose:
            Provide a service that uses PEP 604 local forward-ref DI.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: _LocalRepo | None) -> None:
            """
            Purpose:
                Capture the injected local repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected local repository instance.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_LocalRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_LocalPep604Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _LocalRepo)
        assert instance.repo.marker == "pep604"
    finally:
        conduit.cleanup()


def test_future_annotations_spellmap_default_overrides_unresolved_annotation() -> None:
    """
    Purpose:
        Validate SpellMap defaults override unresolved annotations.
    Contract:
        - The SpellMap default is used for DI.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FutureLateRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_FutureSpellMapService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _FutureLateRepo)
    finally:
        conduit.cleanup()


def test_future_annotations_local_forward_ref_resolves_by_name() -> None:
    """
    Purpose:
        Validate local forward refs resolve by spell name under future annotations.
    Contract:
        - The local dependency is injected.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _LocalRepo:
        """
        Purpose:
            Provide a local repository spell for name-based resolution.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the local repository marker.
            Contract:
                Sets marker to "local".
            Returns:
                None.
            """
            self.marker = "local"

    class _LocalService:
        """
        Purpose:
            Provide a service that depends on the local repository.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: _LocalRepo) -> None:
            """
            Purpose:
                Capture the injected local repository.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Injected local repository.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_LocalRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_LocalService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _LocalRepo)
        assert instance.repo.marker == "local"
    finally:
        conduit.cleanup()


def test_future_annotations_local_forward_ref_collection_resolves_by_name() -> None:
    """
    Purpose:
        Validate local forward-ref lists resolve by frame name under future annotations.
    Contract:
        - All local implementations are injected into the list.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is incomplete.
    """
    class _LocalFrame:
        """
        Purpose:
            Provide a local class-based frame for list DI.
        Contract:
            Acts as a DI grouping key.
        """

    class _LocalFrameImplA:
        """
        Purpose:
            Provide a local class-frame implementation.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _LocalFrameImplB:
        """
        Purpose:
            Provide a second local class-frame implementation.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    class _LocalFramePipeline:
        """
        Purpose:
            Provide a pipeline that depends on local class-frame list DI.
        Contract:
            Stores the injected implementations list.
        """

        def __init__(self, handlers: list[_LocalFrame]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected local handlers.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_LocalFrameImplA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_LocalFrame,
    )
    spellbook.bind(
        spell=_LocalFrameImplB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_LocalFrame,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_LocalFramePipeline,
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


def test_future_annotations_local_protocol_forward_ref_collection_resolves_by_name() -> None:
    """
    Purpose:
        Validate local protocol list DI resolves by protocol name under future annotations.
    Contract:
        - All local protocol implementations are injected into the list.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is incomplete.
    """
    class _LocalProtocol(Protocol):
        """
        Purpose:
            Provide a local protocol frame for list DI.
        Contract:
            Acts as a DI grouping key.
        """

    class _LocalProtoImplA:
        """
        Purpose:
            Provide a local protocol implementation.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _LocalProtoImplB:
        """
        Purpose:
            Provide a second local protocol implementation.
        Contract:
            Stores a stable marker for assertions.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    class _LocalProtoPipeline:
        """
        Purpose:
            Provide a pipeline that depends on local protocol list DI.
        Contract:
            Stores the injected implementations list.
        """

        def __init__(self, handlers: list[_LocalProtocol]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected local protocol handlers.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_LocalProtoImplA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_LocalProtocol,
    )
    spellbook.bind(
        spell=_LocalProtoImplB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_LocalProtocol,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_LocalProtoPipeline,
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


def test_future_annotations_missing_forward_ref_raises_no_candidate() -> None:
    """
    Purpose:
        Validate unresolved forward refs raise a clear no-candidate error.
    Contract:
        - Conjure fails when no DI candidates exist for the forward ref.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    class _BrokenService:
        """
        Purpose:
            Provide a service with a missing forward-ref dependency.
        Contract:
            Declares a dependency that is never bound.
        """

        def __init__(self, missing: "MissingDependency") -> None:
            """
            Purpose:
                Capture the missing dependency for completeness.
            Contract:
                Stores the dependency on the instance.
            Args:
                missing: Unresolved dependency.
            Returns:
                None.
            """
            self.missing = missing

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_BrokenService,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError) as exc_info:
        spellbook.conjure(name="root")

    assert any(
        "no DI candidate found" in str(error) and "MissingDependency" in str(error)
        for error in exc_info.value.errors
    )
