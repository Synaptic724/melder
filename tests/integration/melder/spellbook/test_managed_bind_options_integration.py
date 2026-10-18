"""
Integration: managed bind options through a real Spellbook and its root conduit
(STORY-2026-10-15-managed_bind_options, S2).

The options reach the Spell through every public bind surface - Spellbook.bind, Conduit.bind,
Conduit.bind_inactive and SpellBinder - and a refused binding leaves the Book as it was. Managed spells are not
melded here: dispensing arrives with STORY-2026-10-15-managed_dispense_codegen (S5).
"""
import uuid
from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests._spell_identity_test_support import version_of


class PooledLogger:
    """A managed target with two reset methods."""

    def reset(self) -> None:
        """Clear per-holder state."""

    def flush(self) -> None:
        """Write out buffered lines."""


class Steady:
    """A plain unique target so the root has something to conjure."""


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Fresh Aether per test; every test binds into its own frame."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _dynamic_book() -> Spellbook:
    """A dynamic Book in a fresh frame, configuration finalized first."""
    frame = f"managed_bind_{uuid.uuid4().hex}"
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def test_spellbook_bind_puts_the_options_on_the_spell() -> None:
    """A managed bind stores the normalized options on the Spell, not in its metadata."""
    book = _dynamic_book()
    try:
        spell_id = book.bind(
            spell=PooledLogger, existence=Existence.managed_spell_quantity, managed_spell_mode="limited_quantity",
            managed_spell_limit=4, managed_spell_reset_methods=["reset", "flush"],
        )
        spell = book.find_spell_by_spell_id(spell_id)
        assert spell.existence is Existence.managed_spell_quantity
        assert spell.managed_spell_mode is ManagedSpellMode.limited_quantity
        assert spell.managed_spell_limit == 4
        assert spell.managed_spell_timeout_seconds is None
        assert spell.managed_spell_reset_methods == ("reset", "flush")
        assert spell.metadata == {}
    finally:
        book.cleanup()


def test_a_managed_binding_keeps_the_spell_id_and_moves_the_binding_hash() -> None:
    """
    The same class bound unique, managed and managed with a limit is one spell_id - the class's code (S1 of
    EPIC-2026-10-18-spell_identity_is_the_code) - and three bindings: the existence and the settings are the
    binding, so each binding has its own binding hash (S2).
    """
    ids = []
    hashes = []
    for options in (
            {"existence": Existence.unique},
            {"existence": Existence.managed_spell_quantity},
            {"existence": Existence.managed_spell_quantity, "managed_spell_limit": 8},
    ):
        book = _dynamic_book()
        try:
            spell_id = book.bind(spell=PooledLogger, **options)
            ids.append(spell_id)
            hashes.append(book.find_spell_by_spell_id(spell_id).binding_hash)
        finally:
            book.cleanup()
    assert ids[0] == ids[1] == ids[2]
    assert len(set(hashes)) == 3


def test_a_refused_binding_leaves_the_book_unchanged() -> None:
    """A managed option on a unique binding raises before anything is registered."""
    book = _dynamic_book()
    try:
        with pytest.raises(ValueError, match="managed_spell_limit"):
            book.bind(spell=PooledLogger, existence=Existence.unique, managed_spell_limit=2)
        assert book.describe_spells_in_spellbook() == []
        spell_id = book.bind(spell=PooledLogger, existence=Existence.unique)
        assert book.find_spell_by_spell_id(spell_id) is not None
    finally:
        book.cleanup()


def test_a_managed_function_is_refused() -> None:
    """Functions cannot be managed: TypeError, nothing registered."""

    def make_logger() -> PooledLogger:
        """Factory."""
        return PooledLogger()

    book = _dynamic_book()
    try:
        with pytest.raises(TypeError, match="classes only"):
            book.bind(spell=make_logger, existence=Existence.managed_spell_quantity)
        assert book.describe_spells_in_spellbook() == []
    finally:
        book.cleanup()


def test_conduit_bind_and_bind_inactive_forward_the_options() -> None:
    """A root binds a managed class after conjure, then parks a second version of it (other code) with its own."""
    book = _dynamic_book()
    try:
        book.bind(spell=Steady, existence=Existence.unique)
        root = book.conjure(dynamic=True, name="managed-root")
        active_id = root.bind(
            spell=PooledLogger, existence=Existence.managed_spell_quantity, managed_spell_mode="queue",
            managed_spell_limit=2, managed_spell_timeout_seconds=0.25,
        )
        active = book.find_spell_by_spell_id(active_id)
        assert (active.managed_spell_mode, active.managed_spell_limit, active.managed_spell_timeout_seconds) == (
            ManagedSpellMode.queue, 2, 0.25,
        )
        parked_id = root.bind_inactive(
            spell=version_of(PooledLogger, version=2), spell_index=active.spell_index,
            existence=Existence.managed_spell_quantity,
            disposal_method_names=["flush"], managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=16,
            managed_spell_reset_methods=["reset"],
        )
        assert parked_id != active_id
        parked = book._get_owned_spell(parked_id)
        assert parked.managed_spell_mode is ManagedSpellMode.elastic
        assert parked.managed_spell_limit == 16
        assert parked.managed_spell_reset_methods == ("reset",)
    finally:
        book.cleanup()


def test_spellbinder_binds_a_managed_class_into_a_real_book() -> None:
    """The fluent path ends in the same Spell as a direct bind."""
    book = _dynamic_book()
    binder = SpellBinder(book)
    try:
        spell_id = (
            binder.bind(PooledLogger)
            .as_managed_spell_quantity("elastic", limit=32, reset_methods=["flush"])
            .finalize()
        )
        spell = book.find_spell_by_spell_id(spell_id)
        assert spell.managed_spell_mode is ManagedSpellMode.elastic
        assert spell.managed_spell_limit == 32
        assert spell.managed_spell_reset_methods == ("flush",)
    finally:
        binder.cleanup()
        book.cleanup()
