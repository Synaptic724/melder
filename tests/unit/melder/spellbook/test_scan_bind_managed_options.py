"""
Unit: scan_bind declares the managed options and a scan replays them (STORY-2026-10-15-managed_bind_options, S2).

`scan_bind` takes the four managed options as target options, checks the reset-name group at decoration (as it
checks disposal names), stores the rest as given for Bind to validate at scan time, refuses the names as
application-metadata keys, and `Scan.scan_module` replays them into `Spellbook.bind`.
"""
import types
import uuid
from collections.abc import Iterator
from typing import Any, Dict, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.scan import Scan, ScanBindMetadata, scan_bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

MANAGED_NAMES = (
    "managed_spell_mode", "managed_spell_limit", "managed_spell_timeout_seconds", "managed_spell_reset_methods",
)


class RecordingBook:
    """Spellbook double recording every bind call a scan makes."""

    def __init__(self) -> None:
        """Start with no calls."""
        self.calls: List[Dict[str, Any]] = []

    def bind(self, **kwargs: Any) -> str:
        """Record the keywords and return a fake spell id."""
        self.calls.append(kwargs)
        return f"id-{len(self.calls)}"


def _module_with(target: type) -> types.ModuleType:
    """Place `target` in a fresh module that owns it (the scan refuses re-exports)."""
    module = types.ModuleType(f"managed_scan_{uuid.uuid4().hex}")
    target.__module__ = module.__name__
    module.__dict__[target.__name__] = target
    return module


def _fresh_class() -> type:
    """A new class per call, with one zero-argument reset method."""

    class Pooled:
        """Managed scan target."""

        def reset(self) -> None:
            """Zero-argument reset."""

    return Pooled


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Fresh Aether per test so frames and registries never leak."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_scan_bind_stores_the_options_as_given() -> None:
    """Mode, limit and timeout are stored unchanged; reset names become a tuple."""
    target = scan_bind(
        existence=Existence.managed_spell_quantity, permissions="create", managed_spell_mode="queue",
        managed_spell_limit=2, managed_spell_timeout_seconds=1, managed_spell_reset_methods=["reset"],
    )(_fresh_class())
    metadata = target.__dict__["__melder_scan_bind__"]
    assert isinstance(metadata, ScanBindMetadata)
    assert metadata.managed_spell_mode == "queue"
    assert metadata.managed_spell_limit == 2
    assert metadata.managed_spell_timeout_seconds == 1
    assert metadata.managed_spell_reset_methods == ("reset",)


def test_scan_bind_without_options_stores_none() -> None:
    """An undeclared option is None, so the replay passes bind's defaults."""
    target = scan_bind(existence=Existence.unique, permissions="create")(_fresh_class())
    metadata = target.__dict__["__melder_scan_bind__"]
    assert [getattr(metadata, name) for name in MANAGED_NAMES] == [None, None, None, None]


@pytest.mark.parametrize("names", ["reset", {"reset"}])
def test_reset_names_must_be_a_list_or_tuple_at_decoration(names: Any) -> None:
    """A bare string or a set is refused when the decorator is built, not at scan time."""
    with pytest.raises(TypeError, match="managed_spell_reset_methods must be a list or tuple"):
        scan_bind(existence=Existence.managed_spell_quantity, permissions="create", managed_spell_reset_methods=names)


def test_reset_names_must_be_strings_at_decoration() -> None:
    """A non-string element is refused at decoration."""
    with pytest.raises(TypeError, match="method-name strings"):
        scan_bind(
            existence=Existence.managed_spell_quantity, permissions="create", managed_spell_reset_methods=["reset", 3],
        )


@pytest.mark.parametrize("name", MANAGED_NAMES)
def test_the_option_names_are_reserved_metadata_keys(name: str) -> None:
    """Each option is native to the bind chain, so the metadata check refuses it like every native name."""
    from melder.aether.spellbook.bind import scan as scan_module

    assert name in ScanBindMetadata.RESERVED_SPELL_METADATA_KEYS
    with pytest.raises(TypeError, match=name):
        scan_module._normalize_spell_metadata({name: "value"})


def test_repr_names_the_options() -> None:
    """The declaration's repr shows the four options for diagnostics."""
    target = scan_bind(
        existence=Existence.managed_spell_quantity, permissions="create", managed_spell_mode="limited_quantity",
        managed_spell_limit=4,
    )(_fresh_class())
    text = repr(target.__dict__["__melder_scan_bind__"])
    assert "managed_spell_mode='limited_quantity'" in text
    assert "managed_spell_limit=4" in text
    assert "managed_spell_timeout_seconds=None" in text
    assert "managed_spell_reset_methods=None" in text


def test_scan_replays_the_options_into_spellbook_bind() -> None:
    """scan_module passes the four options to Spellbook.bind explicitly."""
    target = scan_bind(
        existence=Existence.managed_spell_quantity, permissions="create", managed_spell_mode="queue",
        managed_spell_limit=2, managed_spell_timeout_seconds=0.5, managed_spell_reset_methods=("reset",),
    )(_fresh_class())
    book = RecordingBook()
    scanner = Scan(book)
    try:
        scanner.scan_module(_module_with(target))
    finally:
        scanner.cleanup()
    call = book.calls[0]
    assert call["managed_spell_mode"] == "queue"
    assert call["managed_spell_limit"] == 2
    assert call["managed_spell_timeout_seconds"] == 0.5
    assert call["managed_spell_reset_methods"] == ("reset",)


def test_scan_without_options_replays_none() -> None:
    """A non-managed declaration replays None for every option."""
    target = scan_bind(existence=Existence.many, permissions="create")(_fresh_class())
    book = RecordingBook()
    scanner = Scan(book)
    try:
        scanner.scan_module(_module_with(target))
    finally:
        scanner.cleanup()
    assert [book.calls[0][name] for name in MANAGED_NAMES] == [None, None, None, None]


def test_a_scan_binds_a_managed_class_with_its_options_through_a_real_book() -> None:
    """End to end: the scanned Spell carries the normalized options."""
    frame = f"managed_scan_{uuid.uuid4().hex}"
    configuration = SpellbookConfiguration(frame)
    configuration.with_defaults()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=True)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    try:
        target = scan_bind(
            existence=Existence.managed_spell_quantity, permissions="create", managed_spell_mode="limited_quantity",
            managed_spell_limit=3, managed_spell_reset_methods=["reset"],
        )(_fresh_class())
        (spell_id,) = book.scan(_module_with(target))
        spell = book.find_spell_by_id(spell_id)
        assert spell.managed_spell_mode is ManagedSpellMode.limited_quantity
        assert spell.managed_spell_limit == 3
        assert spell.managed_spell_timeout_seconds is None
        assert spell.managed_spell_reset_methods == ("reset",)
    finally:
        book.cleanup()


def test_bind_validates_scanned_options_at_scan_time() -> None:
    """Mode, limit and timeout are checked by Bind when the module is scanned."""
    frame = f"managed_scan_{uuid.uuid4().hex}"
    configuration = SpellbookConfiguration(frame)
    configuration.with_defaults()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=True)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    try:
        target = scan_bind(
            existence=Existence.managed_spell_quantity, permissions="create", managed_spell_mode="queue",
            managed_spell_limit=1,
        )(_fresh_class())
        with pytest.raises(ValueError, match="needs managed_spell_timeout_seconds"):
            book.scan(_module_with(target))
    finally:
        book.cleanup()
