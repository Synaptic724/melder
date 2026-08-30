"""
Integration tests -- transfer of ownership with the INDEX as the unit (area D).

Transfer moves a whole SpellIndex (lineage), not just the active version. These
cover the baseline flip plus the NEW multi-member behavior added in the index work:
`_migrate_inactive_members` carries the index's inactive members to the target too,
so the whole lineage ends up owned by the target.

Modeled on `tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py`.
Transactions are OUT OF SCOPE. Runtime: Python 3.14t; the 3.10 sandbox cannot run
these -> user runs on 3.14t (the multi-member setup shares the notch-harness
assumptions -- validate those first).
"""

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _ServiceA:
    def __init__(self) -> None:
        self.tag = "A"


class _ServiceB:
    def __init__(self) -> None:
        self.tag = "B"


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_transfer() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _config() -> SpellbookConfiguration:
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _single_member_transfer_ready():
    """owner_book/target_book with one bound service, both conjured dynamic."""
    config = _config()
    owner_book = Spellbook(configuration=config)
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    target_book = Spellbook(configuration=config)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    return owner_book, target_book, owner, target, id_a


def _multi_member_transfer_ready():
    """owner index has 2 members (A active, B inactive); target ready."""
    config = _config()
    owner_book = Spellbook(configuration=config)
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    target_book = Spellbook(configuration=config)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    index = owner_book.find_spell_by_id(id_a).spell_index
    id_b = owner.bind_inactive(  # index = {A, B}
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = owner_book._get_owned_spell(id_b)
    return owner_book, target_book, owner, target, id_a, id_b, index


# --- D1 single-member transfer ---------------------------------------------

def test_transfer_moves_ownership_to_target():
    owner_book, target_book, owner, target, id_a = _single_member_transfer_ready()
    try:
        summary = owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        assert summary["source"] == owner.id
        assert summary["target"] == target.id
        assert owner.get_conduit_by_spell_id(id_a) is target
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_flips_meld_resolution_to_target():
    owner_book, target_book, owner, target, id_a = _single_member_transfer_ready()
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        assert isinstance(target.meld(spell_id=id_a), _ServiceA)
        with pytest.raises(Exception):
            owner.meld(spell_id=id_a)
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


# --- D2 multi-member transfer carries inactive members ---------------------

def test_transfer_multi_member_target_owns_active():
    owner_book, target_book, owner, target, id_a, id_b, index = _multi_member_transfer_ready()
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        assert owner.get_conduit_by_spell_id(id_a) is target
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_multi_member_carries_inactive_member_to_target():
    owner_book, target_book, owner, target, id_a, id_b, index = _multi_member_transfer_ready()
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        # The inactive member B travels with the index (index is the transfer unit).
        assert id_b in target_book._inactive_spells
        assert id_b in target_book._spell_ids
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_multi_member_source_loses_inactive_member():
    owner_book, target_book, owner, target, id_a, id_b, index = _multi_member_transfer_ready()
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        assert id_b not in owner_book._inactive_spells
        assert id_b not in owner_book._spell_ids
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_multi_member_repoints_inactive_owner_spellbook():
    owner_book, target_book, owner, target, id_a, id_b, index = _multi_member_transfer_ready()
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        moved_b = target_book._get_owned_spell(id_b)
        assert moved_b is not None
        # The migrated inactive member is repointed at the target spellbook.
        assert moved_b._spellbook is target_book
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


# --- D-selective ------------------------------------------------------------

def test_transfer_moves_only_the_targeted_index():
    config = _config()
    owner_book = Spellbook(configuration=config)
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    id_other = owner_book.bind(spell=_ServiceB, existence=Existence.unique, permissions="create", binding_name="other")
    target_book = Spellbook(configuration=config)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        assert owner.get_conduit_by_spell_id(id_a) is target
        # The untargeted spell stays with the source owner.
        assert owner.get_conduit_by_spell_id(id_other) is owner
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()
