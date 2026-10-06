"""Isolate native rebind after a many creation using only public Melder operations."""

import pytest
from melder import Cleanable, Spellbook

from tests.mocks.melder_isolation import reset_spectrum_and_melder


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


@pytest.mark.parametrize("linked", [False, True])
@pytest.mark.parametrize("first_meld", [False, True])
def test_rebind_rebuilds_creation_context(linked: bool, first_meld: bool) -> None:
    """Rebinding the exact class/address must allow the next ordinary lesser meld."""
    book = Spellbook(aetheric_frame="rebind-probe")
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    root = book.conjure(dynamic=True, name="action_definitions")
    peer_book = Spellbook(aetheric_frame="rebind-probe")
    peer_book.get_configuration().freeze()
    peer = peer_book.conjure(dynamic=True, name="application")
    scope = root.create_lesser_conduit(name="center_actions")
    try:
        identifier = root.bind(spell=RebindProbe, existence="many", spellframe="actions",
                               binding_name="probe", disposal_method_names=["cleanup"])
        if linked:
            peer.link(root)
            peer.add_spell_to_contract(spell_id=identifier, conduit=root,
                                        aetheric_frame="rebind-probe", permissions="create")
        original = scope.meld(spellframe="actions", binding_name="probe") if first_meld else None
        definition = root.get_spell_by_id(identifier, "rebind-probe")
        if linked:
            with peer.transaction("link", conduits=[peer, root]):
                peer.remove_spell_from_contract(spell=definition, conduit=root,
                                                  aetheric_frame="rebind-probe")
        root.cleanup_spell(spell=definition)
        if original is not None:
            assert original.value == 1 and not original.cleaned
        replacement = root.bind(spell=RebindProbe, existence="many", spellframe="actions",
                                binding_name="probe", disposal_method_names=["cleanup"])
        if linked:
            peer.link(root)
            peer.add_spell_to_contract(spell_id=replacement, conduit=root,
                                        aetheric_frame="rebind-probe", permissions="create")
        assert scope.meld(spellframe="actions", binding_name="probe", override={"value": 2}).value == 2
    finally:
        root.cleanup()
        peer.cleanup()
