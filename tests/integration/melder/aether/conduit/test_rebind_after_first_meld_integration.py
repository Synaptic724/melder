"""Integration coverage: rebind after first meld resolves again in every conduit (0.2.8219 repair).

Operation prefix (MelderOps Actions replacement, reported 2026-10-03): bind -> meld -> withdraw the peer
grant when linked -> cleanup_spell -> bind the same class at the same address -> meld. Before the repair
the second meld raised RuntimeError "Cannot build CreationContext before spell_codegen_creation exists."
whenever the first meld had happened: the per-conduit resolution verdict recorded for the content-stable
spell id survived the definition's removal, the rebind minted the same id for a new Spell with no
compiler artifact, and Meld read the dead `valid` and skipped phases 5-11. The registry now retires an
id's conduit verdicts when its definition is unregistered and when a definition is registered under it.

Fixture: Melder's own cold reset (`Aether._reset_singleton_for_tests` plus rebinding the class
references), no application import.
"""

from collections.abc import Iterator

import pytest

from melder import Aether, Cleanable, Conduit, Spellbook
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


@pytest.fixture(autouse=True)
def reset_melder() -> Iterator[None]:
    """Fresh cold Aether before and after every case, exactly as Melder's integration fixtures do."""
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    try:
        yield
    finally:
        Aether._reset_singleton_for_tests()
        world = Aether()
        Spellbook._aether = world
        Conduit._aether = world


class RebindProbe(Cleanable):
    """Minimal tracked object with no application collaborators."""

    def __init__(self, value: int = 1) -> None:
        """Store one supplied scalar without constructing another dependency."""
        super().__init__()
        self.value: int = value

    def cleanup(self) -> None:
        """Retire once and drop the scalar; old products survive definition removal."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.value


class Provider(Cleanable):
    """Dependency of `Consumer`; the first provider class."""

    generation: int = 1

    def __init__(self) -> None:
        """Record which class built this instance."""
        super().__init__()
        self.generation: int = type(self).generation

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class ProviderV2(Cleanable):
    """A different class bound under the provider's address after the first one is removed."""

    generation: int = 2

    def __init__(self) -> None:
        """Record which class built this instance."""
        super().__init__()
        self.generation: int = type(self).generation

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True


class Consumer(Cleanable):
    """Depends on the provider address by annotation."""

    def __init__(self, p: Provider) -> None:
        """Hold the injected provider."""
        super().__init__()
        self.p = p

    def cleanup(self) -> None:
        """Retire once."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.p


def _world(frame: str) -> tuple[Spellbook, Conduit, Conduit, Conduit]:
    """One dynamic owner root with a named lesser, and a dynamic peer root on the same frame."""
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    root = book.conjure(dynamic=True, name="action_definitions")
    peer_book = Spellbook(aetheric_frame=frame)
    peer_book.get_configuration().freeze()
    peer = peer_book.conjure(dynamic=True, name="application")
    scope = root.create_lesser_conduit(name="center_actions")
    return book, root, peer, scope


def _bind_probe(root: Conduit) -> str:
    """Late-bind the probe as a `many` definition under the Actions-style address."""
    return root.bind(spell=RebindProbe, existence="many", spellframe="actions",
                     binding_name="probe", disposal_method_names=["cleanup"])


@pytest.mark.parametrize("linked", [False, True])
@pytest.mark.parametrize("first_meld", [False, True])
def test_rebind_after_first_meld_melds_again(linked: bool, first_meld: bool) -> None:
    """The reported four-case matrix: the two first-meld cases used to raise, the two controls passed."""
    frame = "rebind-probe"
    book, root, peer, scope = _world(frame)
    try:
        identifier = _bind_probe(root)
        if linked:
            peer.link(root)
            peer.add_spell_to_contract(spell_id=identifier, conduit=root,
                                        aetheric_frame=frame, permissions="create")
        original = scope.meld(spellframe="actions", binding_name="probe") if first_meld else None
        definition = root.get_spell_by_id(identifier, frame)
        if linked:
            with peer.transaction("link", conduits=[peer, root]):
                peer.remove_spell_from_contract(spell=definition, conduit=root, aetheric_frame=frame)
        root.cleanup_spell(spell=definition)
        if original is not None:
            assert original.value == 1 and not original.cleaned
        replacement = _bind_probe(root)
        assert replacement == identifier
        if linked:
            peer.link(root)
            peer.add_spell_to_contract(spell_id=replacement, conduit=root,
                                        aetheric_frame=frame, permissions="create")
        product = scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
        assert product.value == 2
        assert product is not original
    finally:
        root.cleanup()
        peer.cleanup()


def test_replacement_is_resolved_again_and_the_old_product_survives() -> None:
    """The dead definition leaves no verdict; the replacement gets its own phase 5-11 artifacts and verdict."""
    frame = "rebind-matrix-m1"
    book, root, peer, scope = _world(frame)
    try:
        identifier = _bind_probe(root)
        original = scope.meld(spellframe="actions", binding_name="probe")
        states = book._spell_system_states
        root_state = states.get_conduit_resolution_state(root._id)
        assert root_state is not None
        assert root_state.get_root_validity(identifier) is SpellValidity.valid
        definition = root.get_spell_by_id(identifier, frame)
        root.cleanup_spell(spell=definition)
        assert root_state.get_root_validity(identifier) is SpellValidity.unknown
        assert root_state.get_spell_validity(identifier) is SpellValidity.unknown
        replacement_id = _bind_probe(root)
        replacement_spell = root.get_spell_by_id(replacement_id, frame)
        assert replacement_spell is not definition
        assert replacement_spell._compiler_artifact._spell_codegen_creation is None
        product = scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
        assert product.value == 2 and product is not original
        assert original.value == 1 and not original.cleaned
        assert replacement_spell._compiler_artifact._spell_codegen_creation is not None
        assert replacement_spell._compiler_artifact._root_blueprint_phase5 is not None
        assert root_state.get_root_validity(replacement_id) is SpellValidity.valid
    finally:
        root.cleanup()
        peer.cleanup()


def test_dependent_consumer_is_rebuilt_against_the_replacement_class() -> None:
    """GUARD (green before the repair): a consumer compiled against the first provider rebuilds its plan."""
    frame = "rebind-matrix-m2"
    book, root, peer, scope = _world(frame)
    try:
        provider_id = root.bind(spell=Provider, existence="many", spellframe="provider",
                                disposal_method_names=["cleanup"])
        root.bind(spell=Consumer, existence="many", spellframe="consumers",
                  binding_name="consumer", disposal_method_names=["cleanup"])
        first = scope.meld(spellframe="consumers", binding_name="consumer")
        assert first.p.generation == 1
        definition = root.get_spell_by_id(provider_id, frame)
        root.cleanup_spell(spell=definition)
        root.bind(spell=ProviderV2, existence="many", spellframe="provider",
                  disposal_method_names=["cleanup"])
        second = scope.meld(spellframe="consumers", binding_name="consumer")
        assert second.p.generation == 2, "consumer plan still constructs the removed provider class"
        assert first.p.generation == 1 and not first.p.cleaned
    finally:
        root.cleanup()
        peer.cleanup()


def test_dependent_consumer_survives_a_same_class_rebind_of_its_dependency() -> None:
    """GUARD (green before the repair): same class, same id - the consumer's next meld builds a live provider."""
    frame = "rebind-matrix-m2b"
    book, root, peer, scope = _world(frame)
    try:
        provider_id = root.bind(spell=Provider, existence="many", spellframe="provider",
                                disposal_method_names=["cleanup"])
        root.bind(spell=Consumer, existence="many", spellframe="consumers",
                  binding_name="consumer", disposal_method_names=["cleanup"])
        first = scope.meld(spellframe="consumers", binding_name="consumer")
        definition = root.get_spell_by_id(provider_id, frame)
        root.cleanup_spell(spell=definition)
        again = root.bind(spell=Provider, existence="many", spellframe="provider",
                          disposal_method_names=["cleanup"])
        assert again == provider_id
        second = scope.meld(spellframe="consumers", binding_name="consumer")
        assert second is not first and second.p is not first.p and not second.p.cleaned
        direct = scope.meld(spellframe="provider")
        assert direct.generation == 1 and direct is not second.p
    finally:
        root.cleanup()
        peer.cleanup()


def test_peer_conduit_that_resolved_the_old_definition_revalidates_the_replacement() -> None:
    """A linked peer that melded the old definition through its contract melds the replacement again."""
    frame = "rebind-matrix-m3"
    book, root, peer, scope = _world(frame)
    try:
        identifier = _bind_probe(root)
        peer.link(root)
        peer.add_spell_to_contract(spell_id=identifier, conduit=root, aetheric_frame=frame,
                                    permissions="create")
        from_peer = peer.meld(spellframe="actions", binding_name="probe")
        from_scope = scope.meld(spellframe="actions", binding_name="probe")
        assert from_peer.value == 1 and from_scope.value == 1
        peer_state = book._spell_system_states.get_conduit_resolution_state(peer._id)
        assert peer_state is not None
        assert peer_state.get_root_validity(identifier) is SpellValidity.valid
        definition = root.get_spell_by_id(identifier, frame)
        with peer.transaction("link", conduits=[peer, root]):
            peer.remove_spell_from_contract(spell=definition, conduit=root, aetheric_frame=frame)
        root.cleanup_spell(spell=definition)
        assert peer_state.get_root_validity(identifier) is SpellValidity.unknown
        replacement = _bind_probe(root)
        peer.link(root)
        peer.add_spell_to_contract(spell_id=replacement, conduit=root, aetheric_frame=frame,
                                    permissions="create")
        assert peer.meld(spellframe="actions", binding_name="probe", override={"value": 3}).value == 3
        assert scope.meld(spellframe="actions", binding_name="probe", override={"value": 2}).value == 2
        assert peer_state.get_root_validity(replacement) is SpellValidity.valid
        assert from_peer.value == 1 and not from_peer.cleaned
    finally:
        root.cleanup()
        peer.cleanup()


def test_both_products_are_disposed_by_the_scope_that_built_them() -> None:
    """The surviving old product and the replacement product are both disposed on the scope's cleanup."""
    frame = "rebind-matrix-m4"
    book, root, peer, scope = _world(frame)
    try:
        identifier = _bind_probe(root)
        original = scope.meld(spellframe="actions", binding_name="probe")
        definition = root.get_spell_by_id(identifier, frame)
        root.cleanup_spell(spell=definition)
        _bind_probe(root)
        product = scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
        assert not original.cleaned and not product.cleaned
        scope.cleanup()
        assert original.cleaned and product.cleaned
    finally:
        root.cleanup()
        peer.cleanup()


def test_slotted_replacement_meets_the_surviving_singleton_in_its_slot() -> None:
    """unique_per_conduit: the object built from the removed definition is deliberately left alive and keeps
    its id-keyed slot (owner ruling, 2026-10-03), so the replacement's first meld in that scope returns it and
    an override against it is refused as against any stored shared instance. Before the repair this case
    raised the CreationContext RuntimeError instead."""
    frame = "rebind-matrix-m7"
    book, root, peer, scope = _world(frame)
    try:
        identifier = root.bind(spell=RebindProbe, existence="unique_per_conduit", spellframe="actions",
                               binding_name="probe", disposal_method_names=["cleanup"])
        original = root.meld(spellframe="actions", binding_name="probe")
        definition = root.get_spell_by_id(identifier, frame)
        root.cleanup_spell(spell=definition)
        assert not original.cleaned
        assert root.bind(spell=RebindProbe, existence="unique_per_conduit", spellframe="actions",
                         binding_name="probe", disposal_method_names=["cleanup"]) == identifier
        product = root.meld(spellframe="actions", binding_name="probe")
        assert product is original and product.value == 1
        with pytest.raises(MeldExecutionError, match="already exists"):
            root.meld(spellframe="actions", binding_name="probe", override={"value": 2})
    finally:
        root.cleanup()
        peer.cleanup()
