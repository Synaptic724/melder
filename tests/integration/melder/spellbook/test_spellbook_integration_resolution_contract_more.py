import inspect
from typing import Protocol

import pytest

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


def test_meld_by_class_default_binding_resolves_instance() -> None:
    """
    Purpose:
        Validate Conduit.meld resolves a bound class without binding_name.
    Contract:
        - Binding a class under the default binding can be resolved by class.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is not of the expected type.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for default binding resolution.
        Contract:
            Exposes a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service marker.
            Contract:
                Sets marker to "default".
            Returns:
                None.
            """
            self.marker = "default"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance, _Service)
        assert instance.marker == "default"
    finally:
        conduit.cleanup()


def test_meld_by_protocol_with_binding_name_resolves() -> None:
    """
    Purpose:
        Validate Protocol spellframe resolution with binding_name.
    Contract:
        - Binding_name selects the correct implementation under the frame.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance type is incorrect.
    """
    class IService(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for resolution.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _PrimaryService:
        """
        Purpose:
            Provide the primary implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the primary marker.
            Contract:
                Sets marker to "primary".
            Returns:
                None.
            """
            self.marker = "primary"

    class _SecondaryService:
        """
        Purpose:
            Provide the secondary implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the secondary marker.
            Contract:
                Sets marker to "secondary".
            Returns:
                None.
            """
            self.marker = "secondary"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_PrimaryService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    spellbook.bind(
        spell=_SecondaryService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="secondary",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=IService, binding_name="secondary")
        assert isinstance(instance, _SecondaryService)
        assert instance.marker == "secondary"
    finally:
        conduit.cleanup()


def test_meld_by_string_spellframe_with_binding_name_resolves() -> None:
    """
    Purpose:
        Validate string spellframe resolution with binding_name.
    Contract:
        - Binding_name selects the correct implementation under the string frame.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance type is incorrect.
    """
    class _ServiceA:
        """
        Purpose:
            Provide a binding "a" implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the "a" marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _ServiceB:
        """
        Purpose:
            Provide a binding "b" implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the "b" marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_ServiceA,
        existence=Existence.unique,
        permissions="create",
        spellframe="svc",
        binding_name="a",
    )
    spellbook.bind(
        spell=_ServiceB,
        existence=Existence.unique,
        permissions="create",
        spellframe="svc",
        binding_name="b",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe="svc", binding_name="b")
        assert isinstance(instance, _ServiceB)
        assert instance.marker == "B"
    finally:
        conduit.cleanup()


def test_type_hint_di_by_concrete_class_resolves_dependency() -> None:
    """
    Purpose:
        Validate type-hint DI by concrete class.
    Contract:
        - A concrete class annotation resolves its matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency instance is not injected.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell for injection.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the dependency marker.
            Contract:
                Sets marker to "dep".
            Returns:
                None.
            """
            self.marker = "dep"

    class _Service:
        """
        Purpose:
            Provide a service that depends on _Dependency.
        Contract:
            Stores the injected dependency on the instance.
        """
        def __init__(self, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the dependency for assertions.
            Contract:
                Stores the dependency on the instance.
            Args:
                dep: Injected dependency instance.
            Returns:
                None.
            """
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Dependency,
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
        service = conduit.meld(spell=service_id)
        assert isinstance(service.dep, _Dependency)
        assert service.dep.marker == "dep"
    finally:
        conduit.cleanup()


def test_spellmap_default_with_string_frame_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap defaults resolve by string spellframe.
    Contract:
        - SpellMap(spell=None, spellframe="config") resolves the matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency is not resolved.
    """
    class _Config:
        """
        Purpose:
            Provide a config spell bound under a string frame.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the config marker.
            Contract:
                Sets marker to "config".
            Returns:
                None.
            """
            self.marker = "config"

    class _Service:
        """
        Purpose:
            Provide a service that resolves config via SpellMap.
        Contract:
            Stores the resolved config instance.
        """
        def __init__(self, cfg=SpellMap(spell=None, spellframe="config")) -> None:
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
        spellframe="config",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=service_id)
        assert isinstance(service.cfg, _Config)
        assert service.cfg.marker == "config"
    finally:
        conduit.cleanup()


def test_spellmap_default_with_string_frame_and_binding_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap defaults resolve string frame + binding_name.
    Contract:
        - SpellMap(spell=None, spellframe="config", binding_name="primary")
          resolves the matching binding.
    Returns:
        None.
    Raises:
        AssertionError: If the primary binding is not resolved.
    """
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
                Capture the config label.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label assigned to this binding.
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
                Capture the config label.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label assigned to this binding.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service that resolves config via SpellMap.
        Contract:
            Stores the resolved config instance.
        """
        def __init__(
                self,
                cfg=SpellMap(spell=None, spellframe="config", binding_name="primary"),
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
        spellframe="config",
        binding_name="secondary",
    )
    spellbook.bind(
        spell=_PrimaryConfig("primary"),
        existence=Existence.unique,
        permissions="create",
        spellframe="config",
        binding_name="primary",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=service_id)
        assert service.cfg.label == "primary"
    finally:
        conduit.cleanup()


def test_spellmap_default_with_function_spell_resolves() -> None:
    """
    Purpose:
        Validate SpellMap defaults can resolve function spells.
    Contract:
        - SpellMap(function) resolves to the function's output instance.
    Returns:
        None.
    Raises:
        AssertionError: If the function is not invoked or result is missing.
    """
    calls: list[str] = []

    def _factory() -> object:
        """
        Purpose:
            Provide a function spell for SpellMap resolution.
        Contract:
            Records the call and returns a new object instance.
        Returns:
            object: Created instance.
        """
        calls.append("called")
        return object()

    class _Service:
        """
        Purpose:
            Provide a service that resolves a function via SpellMap.
        Contract:
            Stores the resolved product instance.
        """
        def __init__(self, product=SpellMap(_factory)) -> None:
            """
            Purpose:
                Capture the product for assertions.
            Contract:
                Stores the product on the instance.
            Args:
                product: Instance returned by the function spell.
            Returns:
                None.
            """
            self.product = product

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_factory,
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
        service = conduit.meld(spell=service_id)
        assert service.product is not None
        assert calls == ["called"]
    finally:
        conduit.cleanup()


def test_collection_di_by_protocol_includes_all_bindings() -> None:
    """
    Purpose:
        Validate list[Protocol] DI includes all bindings.
    Contract:
        - Multiple bindings under a Protocol frame are injected as a list.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
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
            Provide a handler implementation for binding "a".
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
            Provide a handler implementation for binding "b".
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
            Provide a service with list-based DI.
        Contract:
            Stores the injected handler list.
        """
        def __init__(self, handlers: list[IHandler]) -> None:
            """
            Purpose:
                Capture handlers for assertions.
            Contract:
                Stores handlers on the instance.
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
        binding_name="a",
    )
    spellbook.bind(
        spell=_HandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
        binding_name="b",
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


def test_spellmap_default_frame_resolves_existing_instance() -> None:
    """
    Purpose:
        Validate SpellMap defaults resolve existing instance spells.
    Contract:
        - SpellMap(spell=None, spellframe=IConfig) returns the bound instance.
    Returns:
        None.
    Raises:
        AssertionError: If the existing instance is not injected.
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
            Provide a config object for existing-instance binding.
        Contract:
            Stores a stable label for assertions.
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
            Provide a service that resolves config via SpellMap.
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

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=service_id)
        assert service.cfg is config_instance
        assert service.cfg.label == "existing"
    finally:
        conduit.cleanup()


def test_meld_by_protocol_default_binding_resolves_existing_instance() -> None:
    """
    Purpose:
        Validate protocol root meld resolves existing instance spells.
    Contract:
        - Conduit.meld(spell=IConfig) returns the bound existing instance.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance does not match the binding.
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
            Provide a config object bound as an existing instance.
        Contract:
            Stores a stable label for assertions.
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

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    config_instance = _Config("root")
    spellbook.bind(
        spell=config_instance,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=IConfig)
        assert instance is config_instance
        assert instance.label == "root"
    finally:
        conduit.cleanup()


def test_meld_by_function_default_binding_resolves_instance() -> None:
    """
    Purpose:
        Validate Conduit.meld resolves a bound function by object reference.
    Contract:
        - A function bound under the default binding resolves by the function object.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is not the expected product.
    """
    class _Built:
        """
        Purpose:
            Provide a simple product type for function spell construction.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, marker: str) -> None:
            """
            Purpose:
                Initialize the product marker.
            Contract:
                Stores the provided marker.
            Args:
                marker: Identifier for the product instance.
            Returns:
                None.
            """
            self.marker = marker

    def _factory() -> _Built:
        """
        Purpose:
            Provide a function spell that constructs a _Built instance.
        Contract:
            Returns a _Built object with a stable marker.
        Returns:
            _Built: Newly created product instance.
        """
        return _Built("fn")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_factory,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_factory)
        assert isinstance(instance, _Built)
        assert instance.marker == "fn"
    finally:
        conduit.cleanup()


def test_type_hint_di_by_protocol_resolves_dependency_secondary() -> None:
    """
    Purpose:
        Validate protocol-annotated DI resolves a single candidate.
    Contract:
        - A protocol-typed dependency resolves to the bound implementation.
    Returns:
        None.
    Raises:
        AssertionError: If the injected dependency is not the bound type.
    """
    class IStorage(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for storage DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Storage:
        """
        Purpose:
            Provide a storage implementation for protocol DI.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the storage marker.
            Contract:
                Sets marker to "storage".
            Returns:
                None.
            """
            self.marker = "storage"

    class _Service:
        """
        Purpose:
            Provide a service that depends on IStorage.
        Contract:
            Stores the resolved storage instance.
        """
        def __init__(self, storage: IStorage) -> None:
            """
            Purpose:
                Capture the injected storage dependency.
            Contract:
                Stores the storage on the instance.
            Args:
                storage: Storage dependency resolved by DI.
            Returns:
                None.
            """
            self.storage = storage

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Storage,
        existence=Existence.unique,
        permissions="create",
        spellframe=IStorage,
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=_Service)
        assert isinstance(service.storage, _Storage)
        assert service.storage.marker == "storage"
    finally:
        conduit.cleanup()


def test_spellmap_default_with_protocol_spell_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap defaults accept protocol spellframes directly.
    Contract:
        - SpellMap(Protocol) resolves by the protocol frame.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved dependency is incorrect.
    """
    class ICache(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for cache DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Cache:
        """
        Purpose:
            Provide a cache implementation for protocol DI.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the cache marker.
            Contract:
                Sets marker to "cache".
            Returns:
                None.
            """
            self.marker = "cache"

    class _Service:
        """
        Purpose:
            Provide a service with a SpellMap protocol default.
        Contract:
            Stores the resolved cache instance.
        """
        def __init__(self, cache=SpellMap(ICache)) -> None:
            """
            Purpose:
                Capture the cache dependency for assertions.
            Contract:
                Stores the cache on the instance.
            Args:
                cache: Injected cache instance.
            Returns:
                None.
            """
            self.cache = cache

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Cache,
        existence=Existence.unique,
        permissions="create",
        spellframe=ICache,
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=_Service)
        assert isinstance(service.cache, _Cache)
        assert service.cache.marker == "cache"
    finally:
        conduit.cleanup()


def test_spellmap_default_with_method_spell_resolves() -> None:
    """
    Purpose:
        Validate SpellMap defaults can resolve bound method spells.
    Contract:
        - The method spell is invoked and its result injected.
    Returns:
        None.
    Raises:
        AssertionError: If the method result is not injected.
    """
    class _Built:
        """
        Purpose:
            Provide a product instance for method spell construction.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, marker: str) -> None:
            """
            Purpose:
                Initialize the product marker.
            Contract:
                Stores the provided marker value.
            Args:
                marker: Identifier for the product instance.
            Returns:
                None.
            """
            self.marker = marker

    class _Factory:
        """
        Purpose:
            Provide a factory with a bound method spell.
        Contract:
            Produces a _Built instance with a stable marker.
        """
        def build(self) -> _Built:
            """
            Purpose:
                Construct a product instance.
            Contract:
                Returns a _Built instance with marker "built".
            Returns:
                _Built: Newly created product instance.
            """
            return _Built("built")

    factory = _Factory()

    class _Service:
        """
        Purpose:
            Provide a service that depends on a method spell result.
        Contract:
            Stores the built product instance.
        """
        def __init__(
                self,
                built=SpellMap(factory.build, binding_name="builder"),
        ) -> None:
            """
            Purpose:
                Capture the method spell result for assertions.
            Contract:
                Stores the built product on the instance.
            Args:
                built: Product resolved from the method spell.
            Returns:
                None.
            """
            self.built = built

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=factory.build,
        existence=Existence.unique,
        permissions="create",
        binding_name="builder",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=_Service)
        assert isinstance(service.built, _Built)
        assert service.built.marker == "built"
    finally:
        conduit.cleanup()


def test_type_hint_di_rejects_method_spell_candidates() -> None:
    """
    Purpose:
        Validate method-only candidates are rejected for type-hint DI.
    Contract:
        - Single DI by protocol ignores method spells and raises when none remain.
    Returns:
        None.
    Raises:
        AssertionError: If the ambiguity error is not surfaced.
    """
    class IWorker(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for worker DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Builder:
        """
        Purpose:
            Provide a builder with a bound method spell.
        Contract:
            Produces a stable marker for assertions.
        """
        def build(self) -> str:
            """
            Purpose:
                Produce a stable marker.
            Contract:
                Returns "built".
            Returns:
                str: Stable marker value.
            """
            return "built"

    class _Service:
        """
        Purpose:
            Provide a service that depends on IWorker.
        Contract:
            Triggers single DI by protocol.
        """
        def __init__(self, worker: IWorker) -> None:
            """
            Purpose:
                Capture the worker dependency for validation.
            Contract:
                Stores the worker on the instance.
            Args:
                worker: Dependency resolved by DI.
            Returns:
                None.
            """
            self.worker = worker

    builder = _Builder()
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=builder.build,
        existence=Existence.unique,
        permissions="create",
        spellframe=IWorker,
        binding_name="builder",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError) as excinfo:
        spellbook.conjure(name="root")

    errors = [str(err) for err in excinfo.value.errors]
    assert any("no DI candidate found" in message for message in errors)


def test_bind_rejects_protocol_as_spell() -> None:
    """
    Purpose:
        Validate Spellbook.bind rejects Protocols as concrete spells.
    Contract:
        - Binding a Protocol as a spell raises TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If Protocol binding does not raise.
    """
    class IThing(Protocol):
        """
        Purpose:
            Provide a protocol spellframe candidate.
        Contract:
            Used only as a frame, not a concrete spell.
        """
        pass

    spellbook = Spellbook()
    with pytest.raises(TypeError):
        spellbook.bind(
            spell=IThing,
            existence=Existence.unique,
            permissions="create",
        )


def test_bind_rejects_module_as_spell() -> None:
    """
    Purpose:
        Validate Spellbook.bind rejects module objects as spells.
    Contract:
        - Binding a module object raises TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If module binding does not raise.
    """
    spellbook = Spellbook()
    with pytest.raises(TypeError):
        spellbook.bind(
            spell=inspect,
            existence=Existence.unique,
            permissions="create",
        )


def test_type_hint_di_ambiguous_concrete_class_raises() -> None:
    """
    Purpose:
        Validate ambiguity errors for type-hint DI by concrete class.
    Contract:
        - Multiple bindings of the same class trigger an ambiguity error.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity is not detected.
    """
    class _Repo:
        """
        Purpose:
            Provide a repository implementation for DI.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, marker: str) -> None:
            """
            Purpose:
                Initialize the repository marker.
            Contract:
                Stores the provided marker value.
            Args:
                marker: Identifier for the repository instance.
            Returns:
                None.
            """
            self.marker = marker

    class _Service:
        """
        Purpose:
            Provide a service that depends on _Repo.
        Contract:
            Triggers concrete-class DI resolution.
        """
        def __init__(self, repo: _Repo) -> None:
            """
            Purpose:
                Capture the repository for validation.
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
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
        binding_name="secondary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError) as excinfo:
        spellbook.conjure(name="root")

    errors = [str(err) for err in excinfo.value.errors]
    assert any("multiple DI candidates" in message for message in errors)
