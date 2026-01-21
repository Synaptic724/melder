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
        Validate SpellMap defaults resolve protocol spellframes via frame-only keys.
    Contract:
        - SpellMap(spell=None, spellframe=Protocol) resolves by the protocol frame.
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
            Provide a service with a protocol SpellMap default.
        Contract:
            Stores the resolved cache instance.
        """
        def __init__(self, cache=SpellMap(spell=None, spellframe=ICache)) -> None:
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
        Validate SpellMap defaults can resolve bound method spells by frame.
    Contract:
        - The method spell is resolved by frame+binding and its result injected.
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
    method_spell = factory.build
    method_spell = factory.build

    class _Service:
        """
        Purpose:
            Provide a service that depends on a method spell result.
        Contract:
            Stores the built product instance.
        """
        def __init__(
                self,
                built=SpellMap(
                    spell=None,
                    spellframe="builders",
                    binding_name="builder",
                ),
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
        spellframe="builders",
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


def test_type_hint_di_allows_method_spell_candidates() -> None:
    """
    Purpose:
        Validate method spell candidates can satisfy protocol type-hint DI.
    Contract:
        - Single DI by protocol resolves a method spell when it is the only match.
    Returns:
        None.
    Raises:
        AssertionError: If the method spell is not injected.
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

    conduit = spellbook.conjure(name="root")
    try:
        service = conduit.meld(spell=_Service)
        assert service.worker == "built"
    finally:
        conduit.cleanup()


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


def test_meld_by_spell_id_resolves_class_instance_unique() -> None:
    """
    Purpose:
        Validate meld by spell_id resolves unique class instances.
    Contract:
        - Meld by spell_id returns the same instance for Existence.unique.
    Returns:
        None.
    Raises:
        AssertionError: If the unique instance is not reused.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for spell_id resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service marker.
            Contract:
                Sets marker to "unique".
            Returns:
                None.
            """
            self.marker = "unique"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert first.marker == "unique"
    finally:
        conduit.cleanup()


def test_meld_by_spell_id_resolves_existing_instance_identity() -> None:
    """
    Purpose:
        Validate meld by spell_id returns existing instances.
    Contract:
        - Existing-creation spells return the original object.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is not the original object.
    """
    class _Config:
        """
        Purpose:
            Provide an existing config instance for binding.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Initialize the config marker.
            Contract:
                Stores the label on the instance.
            Args:
                label: Identifier for the config instance.
            Returns:
                None.
            """
            self.label = label

    config_obj = _Config("existing")
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=config_obj,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        resolved = conduit.meld(spell=spell_id)
        assert resolved is config_obj
        assert resolved.label == "existing"
    finally:
        conduit.cleanup()


def test_meld_by_class_with_binding_name_resolves_specific() -> None:
    """
    Purpose:
        Validate class-based meld honors binding_name.
    Contract:
        - A class bound under a non-default binding resolves with that binding_name.
    Returns:
        None.
    Raises:
        AssertionError: If binding_name resolution fails.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell bound under a named binding.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the service marker.
            Contract:
                Sets marker to "named".
            Returns:
                None.
            """
            self.marker = "named"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
        binding_name="named",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service, binding_name="named")
        assert isinstance(instance, _Service)
        assert instance.marker == "named"
    finally:
        conduit.cleanup()


def test_meld_by_function_with_binding_name_resolves_instance() -> None:
    """
    Purpose:
        Validate function-based meld honors binding_name.
    Contract:
        - A function spell bound under a named binding resolves by binding_name.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is incorrect.
    """
    class _Built:
        """
        Purpose:
            Provide a built instance for function spell resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, marker: str) -> None:
            """
            Purpose:
                Initialize the built marker.
            Contract:
                Stores the marker on the instance.
            Args:
                marker: Identifier for the built instance.
            Returns:
                None.
            """
            self.marker = marker

    def _builder() -> _Built:
        """
        Purpose:
            Provide a function spell that builds _Built instances.
        Contract:
            Returns an instance with marker "built".
        Returns:
            _Built: Newly created instance.
        """
        return _Built("built")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_builder,
        existence=Existence.unique,
        permissions="create",
        binding_name="builder",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_builder, binding_name="builder")
        assert isinstance(instance, _Built)
        assert instance.marker == "built"
    finally:
        conduit.cleanup()


def test_type_hint_di_by_concrete_class_reuses_unique_dependency() -> None:
    """
    Purpose:
        Validate concrete type-hint DI reuses unique dependencies.
    Contract:
        - A unique dependency is shared across multiple service melds.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency instance is not reused.
    """
    class _Dependency:
        """
        Purpose:
            Provide a unique dependency spell.
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
            Stores the dependency for assertions.
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
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=_Service)
        second = conduit.meld(spell=_Service)
        assert first.dep is second.dep
        assert first.dep.marker == "dep"
    finally:
        conduit.cleanup()


def test_type_hint_di_by_protocol_reuses_unique_dependency() -> None:
    """
    Purpose:
        Validate protocol type-hint DI reuses unique dependencies.
    Contract:
        - A unique protocol-bound dependency is shared across service melds.
    Returns:
        None.
    Raises:
        AssertionError: If the dependency instance is not reused.
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
            Provide a repository implementation.
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
            Stores the repository for assertions.
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
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=_Service)
        second = conduit.meld(spell=_Service)
        assert first.repo is second.repo
        assert first.repo.marker == "repo"
    finally:
        conduit.cleanup()


def test_spellmap_default_frame_only_string_resolves() -> None:
    """
    Purpose:
        Validate frame-only SpellMap resolution for string spellframes.
    Contract:
        - SpellMap(frame-only, binding_name) resolves the bound instance.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is incorrect.
    """
    class _Cache:
        """
        Purpose:
            Provide a cache implementation for string-frame DI.
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
            Provide a service with a frame-only SpellMap dependency.
        Contract:
            Stores the cache instance for assertions.
        """
        def __init__(
                self,
                cache=SpellMap(spell=None, spellframe="cache", binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture the cache for assertions.
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
        spellframe="cache",
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.cache, _Cache)
        assert instance.cache.marker == "cache"
    finally:
        conduit.cleanup()


def test_spellmap_default_explicit_class_with_binding_name_resolves() -> None:
    """
    Purpose:
        Validate SpellMap explicit class defaults honor binding_name.
    Contract:
        - SpellMap(explicit class, binding_name=...) resolves unambiguously.
    Returns:
        None.
    Raises:
        AssertionError: If the explicit class binding is not resolved.
    """
    class _Config:
        """
        Purpose:
            Provide a config dependency for explicit SpellMap resolution.
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
            Provide a service with an explicit-class SpellMap default.
        Contract:
            Stores the config instance for assertions.
        """
        def __init__(
                self,
                cfg=SpellMap(_Config, binding_name="secondary"),
        ) -> None:
            """
            Purpose:
                Capture the config for assertions.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Injected config instance selected by binding_name.
            Returns:
                None.
            """
            self.cfg = cfg

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Config,
        existence=Existence.many,
        permissions="create",
        binding_name="secondary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.cfg, _Config)
        assert instance.cfg.marker == "config"
    finally:
        conduit.cleanup()


def test_collection_di_by_list_protocol_includes_all_bindings() -> None:
    """
    Purpose:
        Validate collection DI includes all bindings.
    Contract:
        - list[Protocol] dependencies include every bound implementation.
    Returns:
        None.
    Raises:
        AssertionError: If any handler is missing.
    """
    class IHandler(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for handler DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _HandlerA:
        """
        Purpose:
            Provide a first handler implementation.
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

    class _HandlerC:
        """
        Purpose:
            Provide a third handler implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the handler marker.
            Contract:
                Sets marker to "C".
            Returns:
                None.
            """
            self.marker = "C"

    class _Service:
        """
        Purpose:
            Provide a service that depends on handler collection.
        Contract:
            Stores the handlers for assertions.
        """
        def __init__(self, handlers: list[IHandler]) -> None:
            """
            Purpose:
                Capture the handler list for assertions.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler list.
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
    spellbook.bind(
        spell=_HandlerC,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
        binding_name="c",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        markers = {handler.marker for handler in instance.handlers}
        assert markers == {"A", "B", "C"}
    finally:
        conduit.cleanup()


def test_meld_by_class_with_spell_override_dict_applies_kwargs() -> None:
    """
    Purpose:
        Validate root spell_override works when melding by class.
    Contract:
        - spell_override dict maps onto root constructor parameters.
    Returns:
        None.
    Raises:
        AssertionError: If override values are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell with explicit constructor parameters.
        Contract:
            Stores constructor arguments for assertions.
        """
        def __init__(self, value: int, label: str) -> None:
            """
            Purpose:
                Capture constructor arguments for assertions.
            Contract:
                Stores value and label on the instance.
            Args:
                value: Numeric value passed to the constructor.
                label: String label passed to the constructor.
            Returns:
                None.
            """
            self.value = value
            self.label = label

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
        instance = conduit.meld(
            spell=_Service,
            spell_override={"value": 5, "label": "root"},
        )
        assert instance.value == 5
        assert instance.label == "root"
    finally:
        conduit.cleanup()


def test_spellmap_explicit_class_with_protocol_frame_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap explicit class + protocol frame resolution.
    Contract:
        - SpellMap(explicit class, spellframe=Protocol, binding_name=...) resolves.
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
            Provide a service with an explicit SpellMap dependency.
        Contract:
            Stores the resolved cache instance.
        """
        def __init__(
                self,
                cache=SpellMap(_Cache, spellframe=ICache, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture the cache for assertions.
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
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.cache, _Cache)
        assert instance.cache.marker == "cache"
    finally:
        conduit.cleanup()


def test_spellmap_explicit_class_with_string_frame_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap explicit class + string frame resolution.
    Contract:
        - SpellMap(explicit class, spellframe="cache", binding_name=...) resolves.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved dependency is incorrect.
    """
    class _Cache:
        """
        Purpose:
            Provide a cache implementation for string-frame DI.
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
            Provide a service with an explicit SpellMap dependency.
        Contract:
            Stores the resolved cache instance.
        """
        def __init__(
                self,
                cache=SpellMap(_Cache, spellframe="cache", binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture the cache for assertions.
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
        spellframe="cache",
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.cache, _Cache)
        assert instance.cache.marker == "cache"
    finally:
        conduit.cleanup()


def test_spellmap_explicit_method_with_frame_and_binding_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap explicit method + frame + binding resolution.
    Contract:
        - SpellMap(explicit method, frame, binding_name) resolves and invokes.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved dependency is incorrect.
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
    method_spell = factory.build

    class _Service:
        """
        Purpose:
            Provide a service that depends on a method spell result.
        Contract:
            Stores the built product instance.
        """
        def __init__(
                self,
                built=SpellMap(method_spell, spellframe="builders", binding_name="builder"),
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
        spell=method_spell,
        existence=Existence.unique,
        permissions="create",
        spellframe="builders",
        binding_name="builder",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.built, _Built)
        assert instance.built.marker == "built"
    finally:
        conduit.cleanup()


def test_spellmap_explicit_method_default_binding_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap explicit method resolution without binding_name.
    Contract:
        - SpellMap(explicit method) resolves and invokes the bound method spell.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved dependency is incorrect.
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
    method_spell = factory.build

    class _Service:
        """
        Purpose:
            Provide a service that depends on a method spell result.
        Contract:
            Stores the built product instance.
        """
        def __init__(self, built=SpellMap(method_spell)) -> None:
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
        spell=method_spell,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.built, _Built)
        assert instance.built.marker == "built"
    finally:
        conduit.cleanup()


def test_collection_di_by_list_protocol_includes_method_spells() -> None:
    """
    Purpose:
        Validate collection DI includes method spells bound to the frame.
    Contract:
        - list[Protocol] dependencies include class and method spell results.
    Returns:
        None.
    Raises:
        AssertionError: If any expected worker is missing.
    """
    class IWorker(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for worker DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Worker:
        """
        Purpose:
            Provide a worker implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the worker marker.
            Contract:
                Sets marker to "class".
            Returns:
                None.
            """
            self.marker = "class"

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
            Provide a service that depends on worker collection.
        Contract:
            Stores the workers for assertions.
        """
        def __init__(self, workers: list[IWorker]) -> None:
            """
            Purpose:
                Capture the worker list for assertions.
            Contract:
                Stores the workers on the instance.
            Args:
                workers: Injected worker list.
            Returns:
                None.
            """
            self.workers = workers

    builder = _Builder()

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Worker,
        existence=Existence.unique,
        permissions="create",
        spellframe=IWorker,
        binding_name="class",
    )
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

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        workers = instance.workers
        assert any(isinstance(worker, _Worker) for worker in workers)
        assert "built" in workers
    finally:
        conduit.cleanup()


def test_collection_di_by_list_protocol_includes_existing_instances() -> None:
    """
    Purpose:
        Validate collection DI includes existing instance spells.
    Contract:
        - list[Protocol] dependencies include existing instance objects.
    Returns:
        None.
    Raises:
        AssertionError: If the existing instance is not injected.
    """
    class IConfig(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for configuration DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Config:
        """
        Purpose:
            Provide a configuration implementation.
        Contract:
            Stores a stable label for assertions.
        """
        def __init__(self, label: str = "class") -> None:
            """
            Purpose:
                Initialize the config label.
            Contract:
                Stores the provided label.
            Args:
                label: Identifier for the config instance.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service that depends on config collection.
        Contract:
            Stores the configs for assertions.
        """
        def __init__(self, configs: list[IConfig]) -> None:
            """
            Purpose:
                Capture the config list for assertions.
            Contract:
                Stores the configs on the instance.
            Args:
                configs: Injected config list.
            Returns:
                None.
            """
            self.configs = configs

    class _ExistingConfig:
        """
        Purpose:
            Provide a distinct config implementation for existing instance DI.
        Contract:
            Stores a stable label for assertions.
        """
        def __init__(self, label: str = "existing") -> None:
            """
            Purpose:
                Initialize the existing config label.
            Contract:
                Stores the provided label.
            Args:
                label: Identifier for the config instance.
            Returns:
                None.
            """
            self.label = label

    existing_config = _ExistingConfig("existing")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=existing_config,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
        binding_name="existing",
    )
    spellbook.bind(
        spell=_Config,
        existence=Existence.many,
        permissions="create",
        spellframe=IConfig,
        binding_name="class",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert any(cfg is existing_config for cfg in instance.configs)
        assert any(isinstance(cfg, _Config) and cfg is not existing_config for cfg in instance.configs)
    finally:
        conduit.cleanup()


def test_spellmap_explicit_class_with_wrong_frame_raises() -> None:
    """
    Purpose:
        Validate explicit SpellMap frame mismatches raise during resolution.
    Contract:
        - SpellMap(explicit class, spellframe=wrong) fails during conjure.
    Returns:
        None.
    Raises:
        AssertionError: If the mismatch does not raise.
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
            Provide a cache implementation for mismatch testing.
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
            Provide a service with a mismatched SpellMap.
        Contract:
            Declares a SpellMap that should not resolve.
        """
        def __init__(
                self,
                cache=SpellMap(_Cache, spellframe="wrong"),
        ) -> None:
            """
            Purpose:
                Capture the cache for mismatch validation.
            Contract:
                Stores the cache on the instance.
            Args:
                cache: Mismatched cache dependency.
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
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError):
        spellbook.conjure(name="root")


def test_spellmap_explicit_class_with_wrong_binding_name_raises() -> None:
    """
    Purpose:
        Validate explicit SpellMap binding_name mismatches raise during resolution.
    Contract:
        - SpellMap(explicit class, binding_name=wrong) fails during conjure.
    Returns:
        None.
    Raises:
        AssertionError: If the mismatch does not raise.
    """
    class _Config:
        """
        Purpose:
            Provide a config implementation for mismatch testing.
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
            Provide a service with a mismatched SpellMap binding.
        Contract:
            Declares a SpellMap that should not resolve.
        """
        def __init__(
                self,
                cfg=SpellMap(_Config, binding_name="wrong"),
        ) -> None:
            """
            Purpose:
                Capture the config for mismatch validation.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Mismatched config dependency.
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
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError):
        spellbook.conjure(name="root")


def test_spellmap_explicit_method_with_wrong_frame_raises() -> None:
    """
    Purpose:
        Validate explicit method SpellMap frame mismatches raise during resolution.
    Contract:
        - SpellMap(explicit method, spellframe=wrong) fails during conjure.
    Returns:
        None.
    Raises:
        AssertionError: If the mismatch does not raise.
    """
    class _Factory:
        """
        Purpose:
            Provide a factory with a bound method spell.
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

    factory = _Factory()

    class _Service:
        """
        Purpose:
            Provide a service with a mismatched method SpellMap.
        Contract:
            Declares a SpellMap that should not resolve.
        """
        def __init__(
                self,
                built=SpellMap(factory.build, spellframe="wrong"),
        ) -> None:
            """
            Purpose:
                Capture the built dependency for mismatch validation.
            Contract:
                Stores the built value on the instance.
            Args:
                built: Mismatched method dependency.
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
        spellframe="builders",
        binding_name="builder",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    with pytest.raises(PhaseExecutionError):
        spellbook.conjure(name="root")


def test_collection_di_by_list_protocol_reuses_unique_instances() -> None:
    """
    Purpose:
        Validate collection DI reuses unique instances across melds.
    Contract:
        - list[Protocol] dependencies return identical instances for unique spells.
    Returns:
        None.
    Raises:
        AssertionError: If instances are not reused.
    """
    class IHandler(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for handler DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _HandlerA:
        """
        Purpose:
            Provide a first handler implementation.
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

    class _Service:
        """
        Purpose:
            Provide a service that depends on handler collection.
        Contract:
            Stores the handlers for assertions.
        """
        def __init__(self, handlers: list[IHandler]) -> None:
            """
            Purpose:
                Capture the handler list for assertions.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler list.
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
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=_Service)
        second = conduit.meld(spell=_Service)
        first_ids = {id(handler) for handler in first.handlers}
        second_ids = {id(handler) for handler in second.handlers}
        assert first_ids == second_ids
    finally:
        conduit.cleanup()
