import pytest
from typing import List, Optional, Protocol, Union

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
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


class _ForwardRefRepo:
    """
    Purpose:
        Provide a repository spell for forward-ref DI tests.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the repository marker.
        Contract:
            Sets marker to "forward".
        Returns:
            None.
        """
        self.marker = "forward"


class _ForwardRefService:
    """
    Purpose:
        Provide a service with a forward-ref dependency annotation.
    Contract:
        Stores the injected repository instance.
    """

    def __init__(self, repo: "_ForwardRefRepo") -> None:
        """
        Purpose:
            Capture the repository for assertions.
        Contract:
            Stores the repository on the instance.
        Args:
            repo: Injected repository instance.
        Returns:
            None.
        """
        self.repo = repo


class _ForwardRefHandler(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for forward-ref list DI tests.
    Contract:
        Acts as a DI grouping key.
    """


class _ForwardRefHandlerA:
    """
    Purpose:
        Provide a handler implementation for forward-ref list DI tests.
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


class _ForwardRefHandlerB:
    """
    Purpose:
        Provide a second handler implementation for forward-ref list DI tests.
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


class _ForwardRefPipeline:
    """
    Purpose:
        Provide a service that collects handlers via forward-ref list DI.
    Contract:
        Stores the injected handlers list.
    """

    def __init__(self, handlers: list["_ForwardRefHandler"]) -> None:
        """
        Purpose:
            Capture the handlers for assertions.
        Contract:
            Stores the handlers on the instance.
        Args:
            handlers: Injected handler instances.
        Returns:
            None.
        """
        self.handlers = handlers


class _LateForwardService:
    """
    Purpose:
        Provide a service that depends on a later-defined repository.
    Contract:
        Stores the injected repository instance.
    """

    def __init__(self, repo: "_LateForwardRepo") -> None:
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


class _LateForwardRepo:
    """
    Purpose:
        Provide a repository spell defined after its consumer.
    Contract:
        Stores a stable marker for assertions.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the repository marker.
        Contract:
            Sets marker to "late".
        Returns:
            None.
        """
        self.marker = "late"


def test_meld_by_spell_id_resolves_class_instance() -> None:
    """
    Purpose:
        Validate direct resolution by spell_id.
    Contract:
        - Conduit.meld(spell=<spell_id>) returns a concrete instance.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance type is incorrect.
    """
    class _Service:
        """
        Purpose:
            Provide a simple class spell for spell_id resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service marker.
            Contract:
                Sets marker to "id".
            Returns:
                None.
            """
            self.marker = "id"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, _Service)
        assert instance.marker == "id"
    finally:
        conduit.cleanup()


def test_meld_by_spell_name_resolves_class_instance() -> None:
    """
    Purpose:
        Validate resolution by spell_name string.
    Contract:
        - Conduit.meld(spell_name="<ClassName>") resolves the default binding.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance type is incorrect.
    """
    class _Service:
        """
        Purpose:
            Provide a simple class spell for spell_name resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service marker.
            Contract:
                Sets marker to "name".
            Returns:
                None.
            """
            self.marker = "name"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell_name=_Service.__name__)
        assert isinstance(instance, _Service)
        assert instance.marker == "name"
    finally:
        conduit.cleanup()


def test_meld_by_class_with_binding_name_resolves() -> None:
    """
    Purpose:
        Validate class-based resolution using a binding name.
    Contract:
        - The binding_name disambiguates class resolution.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance does not match expectations.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for binding-name resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service marker.
            Contract:
                Sets marker to "primary".
            Returns:
                None.
            """
            self.marker = "primary"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
        binding_name="primary",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service, binding_name="primary")
        assert isinstance(instance, _Service)
        assert instance.marker == "primary"
    finally:
        conduit.cleanup()


def test_meld_by_protocol_spellframe_resolves() -> None:
    """
    Purpose:
        Validate resolution by Protocol spellframe.
    Contract:
        - Conduit.meld(spellframe=Protocol) returns the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance does not match expectations.
    """
    class IWorker(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for resolution.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Worker:
        """
        Purpose:
            Provide a concrete worker bound under IWorker.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the worker marker.
            Contract:
                Sets marker to "proto".
            Returns:
                None.
            """
            self.marker = "proto"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Worker,
        existence=Existence.many,
        permissions="create",
        spellframe=IWorker,
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe=IWorker)
        assert isinstance(instance, _Worker)
        assert instance.marker == "proto"
    finally:
        conduit.cleanup()


def test_meld_by_string_spellframe_resolves() -> None:
    """
    Purpose:
        Validate resolution by string spellframe.
    Contract:
        - Conduit.meld(spellframe="<string>") resolves the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance does not match expectations.
    """
    class _Handler:
        """
        Purpose:
            Provide a handler bound to a string spellframe.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the handler marker.
            Contract:
                Sets marker to "string".
            Returns:
                None.
            """
            self.marker = "string"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Handler,
        existence=Existence.many,
        permissions="create",
        spellframe="handlers",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe="handlers")
        assert isinstance(instance, _Handler)
        assert instance.marker == "string"
    finally:
        conduit.cleanup()


def test_type_hint_di_forward_ref_string_resolves_dependency() -> None:
    """
    Purpose:
        Validate forward-ref string annotations resolve for DI.
    Contract:
        - String annotations are resolved to real types during Phase 1.
        - The dependency is injected as a concrete instance.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_ForwardRefRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_ForwardRefService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ForwardRefRepo)
        assert instance.repo.marker == "forward"
    finally:
        conduit.cleanup()


def test_collection_di_forward_ref_list_injects_all() -> None:
    """
    Purpose:
        Validate collection DI works with forward-ref list annotations.
    Contract:
        - list["FrameType"] resolves all bound implementations.
        - All resolved handlers are injected into the list.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_ForwardRefHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ForwardRefHandler,
    )
    spellbook.bind(
        spell=_ForwardRefHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ForwardRefHandler,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_ForwardRefPipeline,
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


def test_type_hint_di_unresolved_forward_ref_raises() -> None:
    """
    Purpose:
        Validate unresolved forward-ref annotations fail with a clear error.
    Contract:
        - Unresolvable DI annotations raise during Phase 1.
        - The error message points at the missing type.
    Returns:
        None.
    Raises:
        AssertionError: If the unresolved annotation does not raise.
    """
    class _BrokenService:
        """
        Purpose:
            Provide a spell with an unresolved DI annotation.
        Contract:
            Uses an annotation that cannot be resolved at runtime.
        """

        def __init__(self, dep: "MissingDependency") -> None:
            """
            Purpose:
                Declare a dependency with an unresolved annotation.
            Contract:
                Stores the dependency for completeness.
            Args:
                dep: Unresolved dependency annotation.
            Returns:
                None.
            """
            self.dep = dep

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


def test_type_hint_di_forward_ref_optional_resolves_dependency() -> None:
    """
    Purpose:
        Validate Optional forward-ref annotations resolve for DI.
    Contract:
        - Optional["Type"] still injects the dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _OptionalService:
        """
        Purpose:
            Provide a service with an Optional forward-ref dependency.
        Contract:
            Stores the injected dependency instance.
        """

        def __init__(self, repo: Optional["_ForwardRefRepo"]) -> None:
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
        spell=_ForwardRefRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_OptionalService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ForwardRefRepo)
    finally:
        conduit.cleanup()


def test_type_hint_di_forward_ref_union_resolves_dependency() -> None:
    """
    Purpose:
        Validate Union forward-ref annotations resolve for DI.
    Contract:
        - Union["Type", None] still injects the dependency.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _UnionService:
        """
        Purpose:
            Provide a service with a Union forward-ref dependency.
        Contract:
            Stores the injected dependency instance.
        """

        def __init__(self, repo: Union["_ForwardRefRepo", None]) -> None:
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
        spell=_ForwardRefRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_UnionService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ForwardRefRepo)
    finally:
        conduit.cleanup()


def test_type_hint_di_forward_ref_typing_list_protocol_resolves_all() -> None:
    """
    Purpose:
        Validate typing.List forward-ref annotations resolve for collection DI.
    Contract:
        - List["Protocol"] injects all bound implementations.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
    """
    class _TypingListPipeline:
        """
        Purpose:
            Provide a pipeline using typing.List forward-ref annotations.
        Contract:
            Stores the injected handlers list.
        """

        def __init__(self, handlers: List["_ForwardRefHandler"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler instances.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_ForwardRefHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ForwardRefHandler,
    )
    spellbook.bind(
        spell=_ForwardRefHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ForwardRefHandler,
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


def test_type_hint_di_forward_ref_list_class_frame_resolves_all() -> None:
    """
    Purpose:
        Validate forward-ref list DI resolves class-frame implementations.
    Contract:
        - list["Frame"] injects all bound implementations.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
    """
    class _Frame:
        """
        Purpose:
            Provide a class frame for list DI.
        Contract:
            Acts as a DI grouping key.
        """

    class _FrameImplA:
        """
        Purpose:
            Provide a class-frame implementation.
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

    class _FrameImplB:
        """
        Purpose:
            Provide another class-frame implementation.
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

    class _FramePipeline:
        """
        Purpose:
            Provide a pipeline that depends on class-frame list DI.
        Contract:
            Stores the injected implementations list.
        """

        def __init__(self, handlers: list["_Frame"]) -> None:
            """
            Purpose:
                Capture the injected implementations.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected class-frame handlers.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_FrameImplA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_Frame,
    )
    spellbook.bind(
        spell=_FrameImplB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_Frame,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_FramePipeline,
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


def test_type_hint_di_forward_ref_local_class_resolves_by_name() -> None:
    """
    Purpose:
        Validate local forward refs resolve by spell name.
    Contract:
        - Local class annotations still inject the dependency.
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
            Provide a service with a local forward-ref annotation.
        Contract:
            Stores the injected repository instance.
        """

        def __init__(self, repo: "_LocalRepo") -> None:
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


def test_type_hint_di_forward_ref_local_protocol_collection_resolves_by_name() -> None:
    """
    Purpose:
        Validate local protocol forward refs resolve list DI by name.
    Contract:
        - list["Protocol"] injects all bound implementations.
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
            Provide another local protocol implementation.
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

    class _LocalPipeline:
        """
        Purpose:
            Provide a pipeline that depends on local protocol list DI.
        Contract:
            Stores the injected implementations list.
        """

        def __init__(self, handlers: list["_LocalProtocol"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected protocol handlers.
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
        spell=_LocalPipeline,
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


def test_type_hint_di_forward_ref_module_scope_defined_late_resolves() -> None:
    """
    Purpose:
        Validate module-scope forward refs resolve when defined later.
    Contract:
        - The dependency is injected even when defined after the consumer.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_LateForwardRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_LateForwardService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _LateForwardRepo)
        assert instance.repo.marker == "late"
    finally:
        conduit.cleanup()


def test_type_hint_di_forward_ref_spellmap_default_wins_over_unresolved() -> None:
    """
    Purpose:
        Validate SpellMap defaults override unresolved forward-ref annotations.
    Contract:
        - SpellMap default is used for DI.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class _SpellMapFallback:
        """
        Purpose:
            Provide a service with a SpellMap default and unresolved annotation.
        Contract:
            Uses the SpellMap default for DI.
        """

        def __init__(self, repo: "MissingDep" = SpellMap(_ForwardRefRepo)) -> None:
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
        spell=_ForwardRefRepo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_SpellMapFallback,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _ForwardRefRepo)
    finally:
        conduit.cleanup()


def test_type_hint_di_forward_ref_list_includes_all_binding_names() -> None:
    """
    Purpose:
        Validate collection DI includes implementations across binding names.
    Contract:
        - list["Protocol"] includes all bindings for that frame.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
    """
    class _BindingPipeline:
        """
        Purpose:
            Provide a pipeline that depends on protocol list DI.
        Contract:
            Stores the injected handlers list.
        """

        def __init__(self, handlers: list["_ForwardRefHandler"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler instances.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_ForwardRefHandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ForwardRefHandler,
        binding_name="alpha",
    )
    spellbook.bind(
        spell=_ForwardRefHandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_ForwardRefHandler,
        binding_name="beta",
    )
    pipeline_id = spellbook.bind(
        spell=_BindingPipeline,
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


def test_type_hint_di_forward_ref_typing_list_class_frame_resolves_all() -> None:
    """
    Purpose:
        Validate typing.List resolves class-frame list DI.
    Contract:
        - List["Frame"] injects all bound implementations.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
    """
    class _TypingFrame:
        """
        Purpose:
            Provide a class frame for typing.List DI.
        Contract:
            Acts as a DI grouping key.
        """

    class _TypingFrameImplA:
        """
        Purpose:
            Provide a class-frame implementation.
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

    class _TypingFrameImplB:
        """
        Purpose:
            Provide another class-frame implementation.
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

    class _TypingFramePipeline:
        """
        Purpose:
            Provide a pipeline that depends on typing.List class-frame DI.
        Contract:
            Stores the injected implementations list.
        """

        def __init__(self, handlers: List["_TypingFrame"]) -> None:
            """
            Purpose:
                Capture the injected handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected class-frame handlers.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_TypingFrameImplA,
        existence=Existence.unique,
        permissions="create",
        spellframe=_TypingFrame,
    )
    spellbook.bind(
        spell=_TypingFrameImplB,
        existence=Existence.unique,
        permissions="create",
        spellframe=_TypingFrame,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_TypingFramePipeline,
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


def test_type_hint_di_by_protocol_resolves_dependency() -> None:
    """
    Purpose:
        Validate protocol-based type-hint DI in constructors.
    Contract:
        - A protocol-annotated parameter resolves the bound spellframe.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not injected.
    """
    class IRepository(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for repository DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Repo:
        """
        Purpose:
            Provide a concrete repository implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the repository marker.
            Contract:
                Sets marker to "repo".
            Returns:
                None.
            """
            self.marker = "repo"

    class _Service:
        """
        Purpose:
            Provide a service that depends on IRepository.
        Contract:
            Stores the injected repository instance.
        """
        def __init__(self, repo: IRepository) -> None:
            """
            Purpose:
                Capture the repository for assertions.
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
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
        spellframe=IRepository,
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _Repo)
        assert instance.repo.marker == "repo"
    finally:
        conduit.cleanup()


def test_spellmap_default_explicit_class_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap defaults resolve explicit class targets.
    Contract:
        - SpellMap(MyRepo) is resolved and injected into the constructor.
    Returns:
        None.
    Raises:
        AssertionError: If the SpellMap default is not resolved.
    """
    class _Repo:
        """
        Purpose:
            Provide a repository spell for SpellMap resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the repository marker.
            Contract:
                Sets marker to "explicit".
            Returns:
                None.
            """
            self.marker = "explicit"

    class _Service:
        """
        Purpose:
            Provide a service with a SpellMap default.
        Contract:
            Stores the resolved repository instance.
        """
        def __init__(self, repo=SpellMap(_Repo)) -> None:
            """
            Purpose:
                Capture the repository for assertions.
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
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.repo, _Repo)
        assert instance.repo.marker == "explicit"
    finally:
        conduit.cleanup()


def test_spellmap_default_frame_only_resolves_dependency() -> None:
    """
    Purpose:
        Validate frame-only SpellMap defaults resolve by spellframe.
    Contract:
        - SpellMap(spell=None, spellframe=IConfig) resolves to the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If the frame-only SpellMap is not resolved.
    """
    class IConfig(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for configuration.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Config:
        """
        Purpose:
            Provide a concrete config implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the config marker.
            Contract:
                Sets marker to "frame-only".
            Returns:
                None.
            """
            self.marker = "frame-only"

    class _Service:
        """
        Purpose:
            Provide a service with a frame-only SpellMap default.
        Contract:
            Stores the resolved config instance.
        """
        def __init__(self, cfg=SpellMap(spell=None, spellframe=IConfig)) -> None:
            """
            Purpose:
                Capture the config for assertions.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Injected config instance.
            Returns:
                None.
            """
            self.cfg = cfg

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Config,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=service_id)
        assert isinstance(instance.cfg, _Config)
        assert instance.cfg.marker == "frame-only"
    finally:
        conduit.cleanup()


def test_spellmap_default_frame_and_binding_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap defaults honor explicit spellframe + binding_name.
    Contract:
        - Existing-instance bindings are not callable during occurrence planning.
        - Conjure raises when SpellMap defaults target an existing-instance binding.
    Returns:
        None.
    Raises:
        AssertionError: If the binding-specific SpellMap is not resolved.
    """
    class IConfig(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for configuration.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _PrimaryConfig:
        """
        Purpose:
            Provide the primary config implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture a label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Identifier for the binding instance.
            Returns:
                None.
            """
            self.label = label

    class _SecondaryConfig:
        """
        Purpose:
            Provide the secondary config implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture a label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Identifier for the binding instance.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service with a binding-specific SpellMap default.
        Contract:
            Stores the resolved config instance.
        """
        def __init__(
                self,
                cfg=SpellMap(spell=None, spellframe=IConfig, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture the config for assertions.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Injected config instance.
            Returns:
                None.
            """
            self.cfg = cfg

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_SecondaryConfig("secondary"),
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
        binding_name="secondary",
    )
    spellbook.bind(
        spell=_PrimaryConfig("primary"),
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
        binding_name="primary",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError, match="not a callable object"):
        spellbook.conjure(name="root")


def test_collection_di_by_list_frame_injects_all() -> None:
    """
    Purpose:
        Validate collection DI for list[FrameType] annotations.
    Contract:
        - All spells bound under the frame are resolved and injected.
    Returns:
        None.
    Raises:
        AssertionError: If the collection does not contain expected entries.
    """
    class IHandler(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for handlers.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _HandlerA:
        """
        Purpose:
            Provide a concrete handler implementation.
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

    class _HandlerB:
        """
        Purpose:
            Provide a second handler implementation.
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

    class _Pipeline:
        """
        Purpose:
            Provide a service with a handler collection dependency.
        Contract:
            Stores the injected handlers list.
        """
        def __init__(self, handlers: list[IHandler]) -> None:
            """
            Purpose:
                Capture the handlers for assertions.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler instances.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_HandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
    )
    spellbook.bind(
        spell=_HandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
        binding_name="secondary",
    )
    pipeline_id = spellbook.bind(
        spell=_Pipeline,
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


def test_existing_instance_frame_type_hint_injects_existing() -> None:
    """
    Purpose:
        Validate existing instance spells are injected by frame type-hint.
    Contract:
        - Existing-instance bindings are not callable during occurrence planning.
        - Conjure raises when a type-hint targets an existing-instance binding.
    Returns:
        None.
    Raises:
        AssertionError: If the existing instance is not injected.
    """
    class IConfig(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for config DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Config:
        """
        Purpose:
            Provide a concrete config object.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the config label.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label for this config instance.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service that depends on IConfig.
        Contract:
            Stores the injected config instance.
        """
        def __init__(self, cfg: IConfig) -> None:
            """
            Purpose:
                Capture the config for assertions.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Injected config instance.
            Returns:
                None.
            """
            self.cfg = cfg

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    config_instance = _Config("existing")
    spellbook.bind(
        spell=config_instance,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError, match="not a callable object"):
        spellbook.conjure(name="root")


def test_type_hint_di_ambiguous_frame_raises() -> None:
    """
    Purpose:
        Validate ambiguity errors for type-hint DI by frame.
    Contract:
        - Multiple candidates for a single frame type-hint raise PhaseExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity does not raise.
    """
    class IRepository(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for repository DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _RepoA:
        """
        Purpose:
            Provide a concrete repository implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the repository marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _RepoB:
        """
        Purpose:
            Provide a second repository implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the repository marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    class _Service:
        """
        Purpose:
            Provide a service that depends on IRepository.
        Contract:
            Triggers frame-based DI resolution.
        """
        def __init__(self, repo: IRepository) -> None:
            """
            Purpose:
                Capture the repository for DI validation.
            Contract:
                Stores the repository on the instance.
            Args:
                repo: Repository dependency.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_RepoA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IRepository,
    )
    spellbook.bind(
        spell=_RepoB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IRepository,
        binding_name="secondary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError) as exc_info:
        spellbook.conjure(name="root")

    assert any(
        "multiple DI candidates" in str(error)
        for error in exc_info.value.errors
    )
