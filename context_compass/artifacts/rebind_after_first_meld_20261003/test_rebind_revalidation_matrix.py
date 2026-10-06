"""Revalidation matrix for the rebind-after-first-meld repair (Melder-only fixture).

Each case states what a CORRECT revalidation must observably do after `cleanup_spell` and a rebind
under the same content-stable spell id: the replacement is compiled again for every conduit that
resolved the old definition, dependents are rebuilt, the old product survives until its scope
disposes it, and the Book's validation flag follows the verdicts.
"""

from collections.abc import Iterator

import pytest
from melder import Aether, Cleanable, Conduit, Spellbook
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity


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


def _world() -> tuple[Spellbook, Conduit, Conduit, Conduit]:
    book = Spellbook(aetheric_frame="rebind-matrix")
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    root = book.conjure(dynamic=True, name="action_definitions")
    peer_book = Spellbook(aetheric_frame="rebind-matrix")
    peer_book.get_configuration().freeze()
    peer = peer_book.conjure(dynamic=True, name="application")
    scope = root.create_lesser_conduit(name="center_actions")
    return book, root, peer, scope


def _bind_probe(root: Conduit) -> str:
    return root.bind(spell=RebindProbe, existence="many", spellframe="actions",
                     binding_name="probe", disposal_method_names=["cleanup"])


def test_m1_replacement_is_resolved_again_and_old_product_survives() -> None:
    """After cleanup + rebind the replacement gets its own phase 5-11 artifacts and a fresh verdict."""
    book, root, peer, scope = _world()
    try:
        identifier = _bind_probe(root)
        original = scope.meld(spellframe="actions", binding_name="probe")
        states = book._spell_system_states
        before = states.get_conduit_resolution_state(root._id)
        assert before.get_root_validity(identifier) is SpellValidity.valid
        definition = root.get_spell_by_id(identifier, "rebind-matrix")
        root.cleanup_spell(spell=definition)
        # the dead definition left no verdict behind
        assert before.get_root_validity(identifier) is SpellValidity.unknown
        assert before.get_spell_validity(identifier) is SpellValidity.unknown
        replacement_id = _bind_probe(root)
        assert replacement_id == identifier
        replacement_spell = root.get_spell_by_id(replacement_id, "rebind-matrix")
        assert replacement_spell is not definition
        assert replacement_spell._compiler_artifact._spell_codegen_creation is None
        product = scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
        assert product.value == 2 and product is not original
        assert original.value == 1 and not original.cleaned
        assert replacement_spell._compiler_artifact._spell_codegen_creation is not None
        assert replacement_spell._compiler_artifact._root_blueprint_phase5 is not None
        after = states.get_conduit_resolution_state(root._id)
        assert after.get_root_validity(replacement_id) is SpellValidity.valid
    finally:
        root.cleanup()
        peer.cleanup()


def test_m2_dependent_consumer_is_rebuilt_against_the_replacement_class() -> None:
    """A consumer compiled against the first provider rebuilds its plan when the address is rebound."""
    book, root, peer, scope = _world()
    try:
        provider_id = root.bind(spell=Provider, existence="many", spellframe="provider",
                                disposal_method_names=["cleanup"])
        root.bind(spell=Consumer, existence="many", spellframe="consumers",
                  binding_name="consumer", disposal_method_names=["cleanup"])
        first = scope.meld(spellframe="consumers", binding_name="consumer")
        assert first.p.generation == 1
        definition = root.get_spell_by_id(provider_id, "rebind-matrix")
        root.cleanup_spell(spell=definition)
        root.bind(spell=ProviderV2, existence="many", spellframe="provider",
                  disposal_method_names=["cleanup"])
        second = scope.meld(spellframe="consumers", binding_name="consumer")
        assert second.p.generation == 2, "consumer plan still constructs the removed provider class"
        assert first.p.generation == 1 and not first.p.cleaned
    finally:
        root.cleanup()
        peer.cleanup()


def test_m2b_dependent_consumer_survives_same_class_rebind_of_its_dependency() -> None:
    """Same class, same id: the consumer's next meld rebuilds and constructs a live provider."""
    book, root, peer, scope = _world()
    try:
        provider_id = root.bind(spell=Provider, existence="many", spellframe="provider",
                                disposal_method_names=["cleanup"])
        root.bind(spell=Consumer, existence="many", spellframe="consumers",
                  binding_name="consumer", disposal_method_names=["cleanup"])
        first = scope.meld(spellframe="consumers", binding_name="consumer")
        definition = root.get_spell_by_id(provider_id, "rebind-matrix")
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


def test_m3_peer_conduit_that_resolved_the_old_definition_revalidates_the_replacement() -> None:
    """A linked peer that melded the old definition through its contract melds the replacement."""
    book, root, peer, scope = _world()
    try:
        identifier = _bind_probe(root)
        peer.link(root)
        peer.add_spell_to_contract(spell_id=identifier, conduit=root,
                                    aetheric_frame="rebind-matrix", permissions="create")
        from_peer = peer.meld(spellframe="actions", binding_name="probe")
        from_scope = scope.meld(spellframe="actions", binding_name="probe")
        assert from_peer.value == 1 and from_scope.value == 1
        peer_state = book._spell_system_states.get_conduit_resolution_state(peer._id)
        assert peer_state is not None
        assert peer_state.get_root_validity(identifier) is SpellValidity.valid
        definition = root.get_spell_by_id(identifier, "rebind-matrix")
        with peer.transaction("link", conduits=[peer, root]):
            peer.remove_spell_from_contract(spell=definition, conduit=root,
                                              aetheric_frame="rebind-matrix")
        root.cleanup_spell(spell=definition)
        assert peer_state.get_root_validity(identifier) is SpellValidity.unknown
        replacement = _bind_probe(root)
        peer.link(root)
        peer.add_spell_to_contract(spell_id=replacement, conduit=root,
                                    aetheric_frame="rebind-matrix", permissions="create")
        assert peer.meld(spellframe="actions", binding_name="probe", override={"value": 3}).value == 3
        assert scope.meld(spellframe="actions", binding_name="probe", override={"value": 2}).value == 2
        assert peer_state.get_root_validity(replacement) is SpellValidity.valid
        assert from_peer.value == 1 and not from_peer.cleaned
    finally:
        root.cleanup()
        peer.cleanup()


def test_m4_both_products_are_disposed_by_the_scope_that_built_them() -> None:
    """The surviving old product and the replacement product are both disposed on scope cleanup."""
    book, root, peer, scope = _world()
    try:
        identifier = _bind_probe(root)
        original = scope.meld(spellframe="actions", binding_name="probe")
        definition = root.get_spell_by_id(identifier, "rebind-matrix")
        root.cleanup_spell(spell=definition)
        _bind_probe(root)
        product = scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
        assert not original.cleaned and not product.cleaned
        scope.cleanup()
        assert original.cleaned and product.cleaned
    finally:
        root.cleanup()
        peer.cleanup()


def test_m5_validation_flag_follows_the_replacement() -> None:
    """The Book reports validation required after the rebind and clears it once the meld revalidates."""
    book, root, peer, scope = _world()
    try:
        identifier = _bind_probe(root)
        scope.meld(spellframe="actions", binding_name="probe")
        assert book._spellbook_validation_required is False
        definition = root.get_spell_by_id(identifier, "rebind-matrix")
        root.cleanup_spell(spell=definition)
        _bind_probe(root)
        assert book._spellbook_validation_required is True
        scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
        assert book._spellbook_validation_required is False
    finally:
        root.cleanup()
        peer.cleanup()


def test_m7_informational_unique_per_conduit_replacement_shares_the_old_slot() -> None:
    """INFORMATIONAL: a unique_per_conduit replacement under the same id meets the old product's slot."""
    book, root, peer, scope = _world()
    try:
        identifier = root.bind(spell=RebindProbe, existence="unique_per_conduit", spellframe="actions",
                               binding_name="probe", disposal_method_names=["cleanup"])
        original = root.meld(spellframe="actions", binding_name="probe")
        definition = root.get_spell_by_id(identifier, "rebind-matrix")
        root.cleanup_spell(spell=definition)
        assert not original.cleaned
        again = root.bind(spell=RebindProbe, existence="unique_per_conduit", spellframe="actions",
                          binding_name="probe", disposal_method_names=["cleanup"])
        assert again == identifier
        product = root.meld(spellframe="actions", binding_name="probe")
        print(f"\nM7: same object as the surviving old product: {product is original}; value={product.value}")
    finally:
        root.cleanup()
        peer.cleanup()
