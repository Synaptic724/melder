"""Integration regressions: bind, SpellMap, SpellContract and meld name one provider the same way.

Reported 2026-10-04 (MelderOps on 0.2.8224): with a ScanProfile bound at (spellframe="agents",
binding_name="ScanProfile"), the consumer default `SpellMap(spellframe="agents", binding_name="ScanProfile")`
raised "SpellMap default could not be resolved". Bind kept the binding name as written, SpellMap stored it
lowercased, and Phase 3 compared the two raw strings. Owner ruling (2026-10-04): SpellMap and SpellContract
behave as Bind does - they keep the binding name as written - and every surface selects a provider by the
same case-insensitive address meld uses (0.2.8226).
"""

from collections.abc import Iterator
from typing import Any

import pytest

from melder import Aether, Conduit, Spellbook, SpellContract, SpellMap
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.helpers.general_helpers import SpellInputUtils
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


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


class ScanProfile:
    """The provider, bound once under "agents" and once under "artificial_intelligence_tools"."""

    def __init__(self) -> None:
        """No collaborators."""


def _scanner_with(default: Any) -> type:
    """
    Build a consumer class whose one parameter defaults to `default` (a SpellMap or a SpellContract).

    One class per descriptor, because a descriptor is read from the constructor's default.
    """

    class MCPScanner:
        """Consumer of one ScanProfile, selected by its descriptor default (the MelderOps shape)."""

        def __init__(self, profile: ScanProfile = default) -> None:
            """Hold the injected profile."""
            self.profile = profile

    return MCPScanner


def _automatic_book(frame: str) -> Spellbook:
    """One automatic Spellbook with caching off on a fresh frame, so conjure runs every phase cold."""
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(system_state="automatic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    return book


def _dynamic_configuration() -> SpellbookConfiguration:
    """A shared dynamic configuration for an owner and a borrower Spellbook."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_bind_spellmap_spellcontract_and_meld_keep_the_name_and_share_one_address() -> None:
    """
    Bind, SpellMap and SpellContract all keep "ScanProfile" exactly as written, and all three address the
    provider by the one case-insensitive key meld resolves: ("agents", "scanprofile").
    """
    book = _automatic_book("binding-name-case-address")
    try:
        spell_id = book.bind(spell=ScanProfile, existence="unique", spellframe="agents", binding_name="ScanProfile")
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        spellmap = SpellMap(spellframe="agents", binding_name="ScanProfile")
        contract = SpellContract(spellframe="agents", binding_name="ScanProfile")
        assert spell.binding_name == spellmap.binding_name == contract.binding_name == "ScanProfile"
        key = SpellInputUtils.normalize_spell_key(spellframe="agents", binding_name="ScanProfile")
        assert key == ("agents", "scanprofile")
        assert spell.key == spellmap.canonical_key == contract.canonical_key == key
        for frame, written in (("AGENTS", "scanprofile"), ("Agents", "SCANPROFILE")):
            assert SpellMap(spellframe=frame, binding_name=written).canonical_key == key
            assert SpellContract(spellframe=frame, binding_name=written).canonical_key == key
            assert SpellMap(spellframe=frame, binding_name=written).binding_name == written
    finally:
        book.cleanup()


@pytest.mark.parametrize(("explicit", "frame", "written"), [
    (False, "agents", "ScanProfile"),
    (False, "agents", "scanprofile"),
    (False, "Agents", "SCANPROFILE"),
    (True, "agents", "ScanProfile"),
    (True, "AGENTS", "scanprofile"),
], ids=["reported", "lower", "upper-frame-and-name", "explicit-spell", "explicit-spell-lower"])
def test_capitalized_spellmap_binding_name_no_longer_fails_to_resolve(explicit: bool, frame: str,
                                                                     written: str) -> None:
    """
    The reported composition: two ScanProfile providers at ("agents", "ScanProfile") and
    ("artificial_intelligence_tools", "ScanProfile"), and a consumer whose SpellMap default names the first.
    Conjure resolves it for every spelling of the frame and binding name, the injected object is the one meld
    returns for that address (and never its namesake), and the SpellMap keeps the name as written.
    """
    book = _automatic_book("binding-name-case-spellmap")
    book.bind(spell=ScanProfile, existence="unique", spellframe="agents", binding_name="ScanProfile")
    book.bind(spell=ScanProfile, existence="unique", spellframe="artificial_intelligence_tools",
              binding_name="ScanProfile")
    if explicit:
        default = SpellMap(ScanProfile, spellframe=frame, binding_name=written)
    else:
        default = SpellMap(spellframe=frame, binding_name=written)
    book.bind(spell=_scanner_with(default), existence="many", spellframe="scanners", binding_name="MCPScanner")
    root = book.conjure(name="root")
    try:
        scanner = root.meld(spellframe="scanners", binding_name="MCPScanner")
        agents = root.meld(spellframe="agents", binding_name="ScanProfile")
        tools = root.meld(spellframe="artificial_intelligence_tools", binding_name="ScanProfile")
        assert scanner.profile is agents
        assert scanner.profile is not tools
        assert root.meld(spellframe=frame, binding_name=written) is agents
        assert default.binding_name == written
    finally:
        root.cleanup()


@pytest.mark.parametrize("written", ["ScanProfile", "scanprofile", "SCANPROFILE"])
def test_capitalized_spellcontract_binding_name_is_satisfied_by_its_provider(written: str) -> None:
    """
    A SpellContract keeps the binding name as written and is satisfied, across a conduit link, by the provider
    bound as ("agents", "ScanProfile") whatever the spelling, exactly as meld finds that provider.
    """
    configuration = _dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    provider_id = owner_book.bind(spell=ScanProfile, existence=Existence.unique, permissions="create",
                                  spellframe="agents", binding_name="ScanProfile")
    borrower_book = Spellbook(configuration=configuration)
    default = SpellContract(spellframe="agents", binding_name=written)
    consumer_id = borrower_book.bind(spell=_scanner_with(default), existence=Existence.unique,
                                     permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=provider_id, conduit=owner, permissions="create")
        assert borrower.validate_contracts_and_define()
        scanner = borrower.meld(spell_id=consumer_id)
        assert scanner.profile is owner.meld(spell_id=provider_id)
        assert scanner.profile is owner.meld(spellframe="agents", binding_name=written)
        assert default.binding_name == written
    finally:
        borrower.cleanup()
        owner.cleanup()
