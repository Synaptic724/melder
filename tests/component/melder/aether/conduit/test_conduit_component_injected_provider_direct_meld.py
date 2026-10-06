"""
Regression contracts: a provider bound after conjure melds directly after it was injected.

A service bound on a live dynamic root after conjure, and first built as a consumer's dependency, could not be
melded directly afterwards: the direct meld raised "Cannot build CreationContext before spell_codegen_creation
exists." The consumer's target-local resolution pass compiled the service only inside the consumer's plan and
left it stamped valid for the conduit with no plan of its own, so nothing resolved it before its own first meld.
These cases run that public sequence - bind after conjure, meld the consumer, meld the service directly - across
scopes, lifetimes, a root holding a spell at conjure, system caching and the SpellSpace door, and assert the real
result: the instance the scope already holds, as each lifetime defines it. The two controls (the provider melded
first, the pair bound before conjure) never failed and must keep passing.
"""

import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import List, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook


class NativeService:
    """The provider: a concrete no-argument class with observable state."""

    def __init__(self) -> None:
        """Give each instance a value a caller can read back."""
        self.value: int = 7


class NativeConsumer:
    """The consumer: requires a NativeService, which the graph injects."""

    def __init__(self, service: NativeService) -> None:
        """Keep the injected service so identity can be checked."""
        self.service: NativeService = service


class ResidentService:
    """An unrelated spell a root already holds at conjure, as a host framework's root does."""

    def __init__(self) -> None:
        """Mark the instance ready."""
        self.ready: bool = True


class InjectedProviderWorld:
    """
    Build dynamic worlds on public APIs for the injected-provider regressions and remove the caches they write.

    Contract:
        - Every root is a dynamic conjure of its own Spellbook on its own frame. The service and consumer pair is
          bound at spellframe "native_probe" on the live root after conjure, unless a case binds it on the Book
          before conjure or not at all.
        - Worlds live in the process Aether, which the `world` fixture replaces before and after each case.
        - A cached world clears its frame's conjure cache folder first unless told to keep it (a warm start), and
          every folder it resolved is removed at teardown.
    """

    def __init__(self) -> None:
        """Start with no conjure cache folder to remove."""
        self.cache_folders: List[Path] = []

    @staticmethod
    def reset_aether() -> None:
        """Replace the process Aether with a fresh one and point the Spellbook and Conduit classes at it."""
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    def remove_cache_folders(self) -> None:
        """Delete every conjure cache folder a case wrote; a missing folder is not an error."""
        for folder in self.cache_folders:
            shutil.rmtree(folder, ignore_errors=True)

    def build(self, frame: str, *, service_existence: str = "unique_per_conduit", caching: bool = False,
              resident: bool = False, bind_before_conjure: bool = False, bind_pair: bool = True,
              clear_cache: bool = True) -> Conduit:
        """
        Conjure a dynamic root named "<frame>-root" and bind the service and consumer pair.

        Args:
            frame: The frame the Spellbook lives on; with caching it also names the conjure cache folder.
            service_existence: The service's lifetime; the consumer is always bound `many`.
            caching: Enable the frame's system caching (the conjure cache).
            resident: Bind ResidentService (`many`) on the Book before conjure.
            bind_before_conjure: Bind the pair on the Book before conjure instead of on the root after it.
            bind_pair: Bind the pair at all (False only primes a warm cache).
            clear_cache: With caching, empty the frame's cache folder first so the conjure starts cold.

        Returns:
            Conduit: The conjured dynamic root.
        """
        book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
        book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                    system_caching_enabled=caching)
        if caching:
            self._track_cache_folder(frame, clear_cache)
        if resident:
            book.bind(spell=ResidentService, existence="many")
        if bind_pair and bind_before_conjure:
            self.bind_pair(book, service_existence)
        root = book.conjure(name=f"{frame}-root", dynamic=True)
        if bind_pair and not bind_before_conjure:
            self.bind_pair(root, service_existence)
        return root

    def _track_cache_folder(self, frame: str, clear: bool) -> None:
        """Resolve the frame's conjure cache folder, empty it when asked, and remember it for teardown."""
        frame_configuration = Aether().get_frame(frame).frame_configuration
        if frame_configuration is None:
            raise RuntimeError(f"Frame {frame!r} has no posture to resolve its conjure cache folder from.")
        folder = frame_configuration.resolve_conjure_cache_root_path() / frame
        if clear:
            shutil.rmtree(folder, ignore_errors=True)
        self.cache_folders.append(folder)

    @staticmethod
    def bind_pair(target: Union[Spellbook, Conduit], service_existence: str) -> None:
        """Bind NativeService with `service_existence` and NativeConsumer (`many`) on a Book or a normal root."""
        target.bind(spell=NativeService, existence=service_existence, spellframe="native_probe",
                    binding_name="NativeService", disposal_method_names=[])
        target.bind(spell=NativeConsumer, existence="many", spellframe="native_probe",
                    binding_name="NativeConsumer", disposal_method_names=[])

    @staticmethod
    def meld_service(owner: Union[Conduit, SpellSpace]) -> NativeService:
        """Meld the service by spellframe and binding name through a conduit or SpellSpace door."""
        service = owner.meld(spellframe="native_probe", binding_name="NativeService")
        assert isinstance(service, NativeService)
        return service

    @staticmethod
    def meld_consumer(owner: Union[Conduit, SpellSpace]) -> NativeConsumer:
        """Meld the consumer by spellframe and binding name through a conduit or SpellSpace door."""
        consumer = owner.meld(spellframe="native_probe", binding_name="NativeConsumer")
        assert isinstance(consumer, NativeConsumer)
        return consumer

    def assert_direct_meld_returns_injected(self, scope: Conduit) -> NativeService:
        """
        Run the diagnostic sequence in one scope and return the scope's service.

        The consumer is melded first and receives a working service; the direct service meld must return that
        instance, a repeated direct meld the same one, and a later consumer must be injected with it too.
        """
        consumer = self.meld_consumer(scope)
        assert consumer.service.value == 7
        service = self.meld_service(scope)
        assert service is consumer.service
        assert self.meld_service(scope) is service
        assert self.meld_consumer(scope).service is service
        return service


@pytest.fixture
def world() -> Iterator[InjectedProviderWorld]:
    """Give each case a fresh Aether, then replace it again and remove the conjure caches the case wrote."""
    InjectedProviderWorld.reset_aether()
    builder = InjectedProviderWorld()
    try:
        yield builder
    finally:
        InjectedProviderWorld.reset_aether()
        builder.remove_cache_folders()


def test_named_lesser_melds_injected_provider_directly(world: InjectedProviderWorld) -> None:
    """The reported sequence: a named lesser melds the consumer, then the service directly, which used to raise."""
    root = world.build("injected-provider-named")
    scope = root.create_lesser_conduit(name="native-provider-probe")
    world.assert_direct_meld_returns_injected(scope)


def test_unnamed_lesser_melds_injected_provider_directly(world: InjectedProviderWorld) -> None:
    """The same sequence in an anonymous lesser; naming the scope plays no part."""
    root = world.build("injected-provider-unnamed")
    scope = root.create_lesser_conduit()
    world.assert_direct_meld_returns_injected(scope)


def test_root_melds_injected_provider_directly(world: InjectedProviderWorld) -> None:
    """The same sequence on the dynamic root itself, with no lesser involved."""
    root = world.build("injected-provider-root")
    world.assert_direct_meld_returns_injected(root)


def test_sibling_lessers_meld_their_own_injected_provider_directly(world: InjectedProviderWorld) -> None:
    """
    Each sibling lesser melds its own service directly after injecting it; the siblings stay isolated.

    Both lessers resolve through their root's conduit id, so the second sibling meets a consumer already
    resolved by the first and a service whose first direct meld already happened in the other scope.
    """
    root = world.build("injected-provider-siblings")
    left = root.create_lesser_conduit(name="native-provider-left")
    right = root.create_lesser_conduit(name="native-provider-right")
    left_service = world.assert_direct_meld_returns_injected(left)
    right_service = world.assert_direct_meld_returns_injected(right)
    assert left_service is not right_service


def test_unique_provider_melds_directly_after_injection(world: InjectedProviderWorld) -> None:
    """A `unique` service melded directly after injection is the one Book-wide instance, from any scope."""
    root = world.build("injected-provider-unique", service_existence="unique")
    scope = root.create_lesser_conduit(name="native-provider-probe")
    service = world.assert_direct_meld_returns_injected(scope)
    assert world.meld_service(root) is service


def test_many_provider_melds_a_new_instance_directly_after_injection(world: InjectedProviderWorld) -> None:
    """A `many` service melded directly after injection is a working new instance on every meld."""
    root = world.build("injected-provider-many", service_existence="many")
    scope = root.create_lesser_conduit(name="native-provider-probe")
    consumer = world.meld_consumer(scope)
    service = world.meld_service(scope)
    assert service.value == 7
    assert service is not consumer.service
    assert world.meld_service(scope) is not service
    assert world.meld_consumer(scope).service is not consumer.service


def test_root_holding_a_spell_at_conjure_melds_injected_provider_directly(world: InjectedProviderWorld) -> None:
    """A root that already holds an unrelated spell at conjure, as a host framework's root does."""
    root = world.build("injected-provider-resident", resident=True)
    scope = root.create_lesser_conduit(name="native-provider-probe")
    world.assert_direct_meld_returns_injected(scope)


@pytest.mark.parametrize("cache_state", ["cold", "warm"])
def test_cached_world_melds_injected_provider_directly(world: InjectedProviderWorld, cache_state: str) -> None:
    """
    With system caching on, cold or warm, the sequence behaves as without it.

    The warm case conjures the same frame and root once in an earlier world, so the second conjure loads its
    conduit bundle; the pair is bound after conjure in both cases, so neither bundle holds it.
    """
    frame = f"injected-provider-cache-{cache_state}"
    if cache_state == "warm":
        world.build(frame, caching=True, resident=True, bind_pair=False)
        InjectedProviderWorld.reset_aether()
    root = world.build(frame, caching=True, resident=True, clear_cache=cache_state == "cold")
    scope = root.create_lesser_conduit(name="native-provider-probe")
    world.assert_direct_meld_returns_injected(scope)


@pytest.mark.parametrize("consumer_door", ["conduit", "spellspace"])
def test_spellspace_door_melds_injected_provider_directly(world: InjectedProviderWorld, consumer_door: str) -> None:
    """
    A SpellSpace melds the service directly after the consumer was injected through the conduit or the space.

    A `unique_per_conduit` service melded through a space lives in its owner conduit's store, so the space,
    the conduit and the consumer all see one instance, also after the space is released.
    """
    root = world.build(f"injected-provider-space-{consumer_door}")
    scope = root.create_lesser_conduit(name="native-provider-probe")
    with scope.enter_spellspace() as space:
        consumer = world.meld_consumer(scope if consumer_door == "conduit" else space)
        assert consumer.service.value == 7
        service = world.meld_service(space)
        assert service is consumer.service
        assert world.meld_service(space) is service
    assert world.meld_service(scope) is service


def test_control_provider_melded_before_its_consumer_keeps_one_instance(world: InjectedProviderWorld) -> None:
    """Control: melding the service first, then the consumer, always worked and keeps one instance."""
    root = world.build("injected-provider-first")
    scope = root.create_lesser_conduit(name="native-provider-probe")
    service = world.meld_service(scope)
    consumer = world.meld_consumer(scope)
    assert consumer.service is service
    assert world.meld_service(scope) is service


def test_control_pair_bound_before_conjure_melds_provider_directly(world: InjectedProviderWorld) -> None:
    """Control: with both binds on the Book before conjure, the sequence always worked."""
    root = world.build("injected-provider-before-conjure", bind_before_conjure=True)
    scope = root.create_lesser_conduit(name="native-provider-probe")
    world.assert_direct_meld_returns_injected(scope)
