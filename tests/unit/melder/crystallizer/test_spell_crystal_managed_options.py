"""
Unit: the spell crystal records a managed spell's options (STORY-2026-10-15-managed_bind_options, S2; record 4.2.0).

The crystal reads the four options only for `Existence.managed_spell_quantity`, so every other crystal and its
`describe()` payload are unchanged; the mode is recorded by name. `SpellCrystal.managed_bind_options(payload)`
turns a recorded payload back into the bind keywords the restore and graft lanes replay.
"""
from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.persistence.record_version import RecordVersion
from melder.nexus.nexus import Nexus
from tests.mocks.crystallizer.spell_crystal_harness import DummySpell

MANAGED_KEYS = (
    "managed_spell_mode", "managed_spell_limit", "managed_spell_timeout_seconds", "managed_spell_reset_methods",
)


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


def _managed_dummy() -> DummySpell:
    """A DummySpell bound managed with every option set."""
    spell = DummySpell("managed-spell", type("PooledService", (), {"__module__": __name__}))
    spell.existence = Existence.managed_spell_quantity
    spell.managed_spell_mode = ManagedSpellMode.queue
    spell.managed_spell_limit = 2
    spell.managed_spell_timeout_seconds = 0.5
    spell.managed_spell_reset_methods = ("reset", "clear")
    return spell


def test_a_managed_crystal_records_the_options_as_plain_values() -> None:
    """describe() carries the mode's name, the limit, the timeout and the reset names in order."""
    crystal = _crystallizer().create_spell_crystal(_managed_dummy())
    try:
        payload = crystal.describe()
        assert payload["existence_name"] == "managed_spell_quantity"
        assert payload["managed_spell_mode"] == "queue"
        assert payload["managed_spell_limit"] == 2
        assert payload["managed_spell_timeout_seconds"] == 0.5
        assert payload["managed_spell_reset_methods"] == ["reset", "clear"]
    finally:
        crystal.cleanup()


def test_other_crystals_carry_no_managed_keys() -> None:
    """A non-managed spell's payload is unchanged: none of the four keys, and no options."""
    crystal = _crystallizer().create_spell_crystal(
        DummySpell("plain-spell", type("PlainService", (), {"__module__": __name__}))
    )
    try:
        payload = crystal.describe()
        assert not any(key in payload for key in MANAGED_KEYS)
        assert crystal.managed_spell_options is None
    finally:
        crystal.cleanup()


def test_managed_spell_options_is_a_detached_copy() -> None:
    """The property returns the recorded options; changing the returned list does not reach the crystal."""
    crystal = _crystallizer().create_spell_crystal(_managed_dummy())
    try:
        options = crystal.managed_spell_options
        assert options == {
            "managed_spell_mode": "queue",
            "managed_spell_limit": 2,
            "managed_spell_timeout_seconds": 0.5,
            "managed_spell_reset_methods": ["reset", "clear"],
        }
        options["managed_spell_reset_methods"].append("extra")
        assert crystal.managed_spell_options["managed_spell_reset_methods"] == ["reset", "clear"]
    finally:
        crystal.cleanup()


def test_managed_spell_options_refuses_a_cleaned_crystal() -> None:
    """Like every focused read, the property raises once the crystal is cleaned."""
    crystal = _crystallizer().create_spell_crystal(_managed_dummy())
    crystal.cleanup()
    with pytest.raises(RuntimeError):
        crystal.managed_spell_options


def test_managed_bind_options_replays_a_recorded_payload() -> None:
    """A managed payload becomes the four bind keywords; the mode stays a name for bind to convert."""
    assert SpellCrystal.managed_bind_options({
        "existence_name": "managed_spell_quantity",
        "managed_spell_mode": "queue",
        "managed_spell_limit": 2,
        "managed_spell_timeout_seconds": 0.5,
        "managed_spell_reset_methods": ["reset"],
    }) == {
        "managed_spell_mode": "queue",
        "managed_spell_limit": 2,
        "managed_spell_timeout_seconds": 0.5,
        "managed_spell_reset_methods": ["reset"],
    }


def test_managed_bind_options_passes_no_resets_as_none() -> None:
    """An empty recorded reset list replays as None (no resets), like disposal names."""
    options = SpellCrystal.managed_bind_options({
        "managed_spell_mode": "elastic", "managed_spell_limit": 256, "managed_spell_timeout_seconds": None,
        "managed_spell_reset_methods": [],
    })
    assert options["managed_spell_reset_methods"] is None
    assert options["managed_spell_mode"] == "elastic"


def test_managed_bind_options_is_empty_without_a_recorded_mode() -> None:
    """A payload of another existence, or a 4.1 record, replays no managed keyword at all."""
    assert SpellCrystal.managed_bind_options({"existence_name": "unique"}) == {}
    assert SpellCrystal.managed_bind_options({}) == {}


def test_record_version_is_4_3_and_reads_4_1_and_4_2_records() -> None:
    """4.2.0 added the managed options and 4.3.0 the binding hash (minors); 4.1-4.3 payloads stay readable."""
    assert RecordVersion.CURRENT == "4.3.0"
    RecordVersion.check_readable({RecordVersion.KEY: "4.1.0"}, "older record")
    RecordVersion.check_readable({RecordVersion.KEY: "4.2.0"}, "managed-options record")
    RecordVersion.check_readable({RecordVersion.KEY: "4.3.0"}, "current record")
    with pytest.raises(ValueError, match="newer than this code's 4.3.0"):
        RecordVersion.check_readable({RecordVersion.KEY: "5.0.0"}, "future record")
