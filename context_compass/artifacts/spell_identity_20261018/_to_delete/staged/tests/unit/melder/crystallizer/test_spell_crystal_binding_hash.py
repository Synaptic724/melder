"""
Unit: the spell crystal records its spell's binding hash (STORY-2026-10-18-binding_manifest_hash, S2; record 4.3.0).

The crystal captures `Spell.binding_hash` - the SHA256 of the spell's binding manifest: how the version is bound,
apart from its code - gives it through the `binding_hash` property and `describe()`, and refuses the read once it is
cleaned, like every focused read. A restore compares it with the binding it rebuilds
(`RestoreReport.record_binding_change`; the integration tests of the ordered-disposal replay).
"""
from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests.mocks.crystallizer.spell_crystal_harness import DummySpell


@pytest.fixture(autouse=True)
def reset_hosted_runtime() -> Iterator[None]:
    """Fresh hosted singletons around each test."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


def _crystallizer() -> Crystallizer:
    """One activated hosted crystallizer with default policy."""
    crystallizer = Aether()._crystallizer
    configuration = crystallizer.create_configuration().with_defaults().activate()
    crystallizer.activate(configuration)
    return crystallizer


def _bound(spell_id: str, binding_hash: str) -> DummySpell:
    """A spell double bound under `spell_id` with the given binding hash."""
    spell = DummySpell(spell_id, type("BoundService", (), {"__module__": __name__}))
    spell.binding_hash = binding_hash
    return spell


def test_the_crystal_records_its_spells_binding_hash() -> None:
    """The property and `describe()` give the binding hash the spell carried at capture."""
    crystal = _crystallizer().create_spell_crystal(_bound("bound-spell", "b" * 64))
    try:
        assert crystal.binding_hash == "b" * 64
        assert crystal.describe()["binding_hash"] == "b" * 64
    finally:
        crystal.cleanup()


def test_two_bindings_of_one_spell_id_record_two_binding_hashes() -> None:
    """The record keeps how a version was bound apart from its code: one spell_id, two binding hashes."""
    crystallizer = _crystallizer()
    first = crystallizer.create_spell_crystal(_bound("one-spell", "1" * 64))
    second = crystallizer.create_spell_crystal(_bound("one-spell", "2" * 64))
    try:
        assert first.id == second.id == "one-spell"
        assert (first.binding_hash, second.binding_hash) == ("1" * 64, "2" * 64)
        assert first.describe()["binding_hash"] != second.describe()["binding_hash"]
    finally:
        first.cleanup()
        second.cleanup()


def test_binding_hash_refuses_a_cleaned_crystal() -> None:
    """The read raises once the crystal is cleaned, and cleanup stays idempotent."""
    crystal = _crystallizer().create_spell_crystal(_bound("bound-spell", "b" * 64))
    crystal.cleanup()
    crystal.cleanup()
    with pytest.raises(RuntimeError):
        crystal.binding_hash
