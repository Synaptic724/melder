"""Distinguish available definition source from externally supplied live state.

These carrier-level probes do not claim a complete checkpoint restore. Source
inspection separately establishes RestoreEngine's replay_required shortfall.
"""

import hashlib
import json
import sys

import pytest

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.synthetic_module import SyntheticModule
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)


@pytest.mark.parametrize("bind_definition", (False, True))
def test_synthetic_source_and_instance_rebindability(
        instance_book: Spellbook, bind_definition: bool,
) -> None:
    """A source-bearing synthetic module preserves code but does not preserve instance state.

    The class control is hydratable; the supplied instance remains replay_required.
    Synthetic registration is cleaned explicitly, including on assertion failure.
    """
    source = 'class ExternalValue:\n    """External value with no constructor dependencies."""\n'
    module_name = "_melder_external_reference_discovery"
    module = SyntheticModule(
        module_name=module_name, spell_crystal_id="reference-discovery",
        source_text=source, source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        binding_signature="external-reference-discovery", export_names=["ExternalValue"],
    )
    crystal = None
    try:
        module.materialize()
        definition = module.ExternalValue
        target = definition if bind_definition else definition()
        if not bind_definition:
            target.runtime_marker = "unrecorded-live-instance-state"
        spell_id = instance_book.bind(spell=target, existence="unique")
        crystal = SpellCrystal(
            instance_book._spell_id_pool[spell_id],
            site_package_dependency_descent=False,
        )
        payload = crystal.describe()
        assert payload["root_module_kind"] == "synthetic_module"
        assert payload["synthetic_module_sources"][module_name]["source_text"] == source
        assert payload["rebindability"] == ("hydratable" if bind_definition else "replay_required")
        assert "unrecorded-live-instance-state" not in json.dumps(payload)
        print("CRYSTAL " + json.dumps({
            "case": "synthetic", "bind_definition": bind_definition,
            "kind": payload["root_module_kind"], "source_retained": True,
            "rebindability": payload["rebindability"], "instance_state_recorded": False,
        }, sort_keys=True))
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()


def test_live_only_named_origin_remains_an_unknown_leaf(instance_book: Spellbook) -> None:
    """Bind a real reference with no importable module or physical source.

    A nonempty module name permits a crystal, but does not manufacture source.
    """
    module_name = "_melder_absent_external_reference_origin"
    assert module_name not in sys.modules
    definition = type("LiveOnlyValue", (), {
        "__module__": module_name, "__doc__": "Live-only external value.",
    })
    supplied = definition()
    spell_id = instance_book.bind(spell=supplied, existence="unique")
    crystal = SpellCrystal(
        instance_book._spell_id_pool[spell_id], site_package_dependency_descent=False,
    )
    try:
        payload = crystal.describe()
        assert payload["root_module_kind"] == "unknown"
        assert payload["root_module_path"] is None
        assert payload["synthetic_module_sources"] == {}
        assert payload["user_module_sources"] == {}
        assert payload["rebindability"] == "replay_required"
        print("CRYSTAL " + json.dumps({
            "case": "live_only_named_origin", "kind": payload["root_module_kind"],
            "source_retained": False, "rebindability": payload["rebindability"],
        }, sort_keys=True))
    finally:
        crystal.cleanup()


def test_live_reference_without_module_name_cannot_form_current_crystal(instance_book: Spellbook) -> None:
    """A completely unnamed origin binds in memory but cannot satisfy current crystal identity."""
    definition = type("NamelessValue", (), {
        "__module__": None, "__doc__": "Externally supplied value without module coordinates.",
    })
    spell_id = instance_book.bind(spell=definition(), existence="unique")
    with pytest.raises(ValueError, match="resolvable module name"):
        SpellCrystal(instance_book._spell_id_pool[spell_id], site_package_dependency_descent=False)
    print('CRYSTAL {"case": "no_module_name", "bind": "accepted", "crystal": "refused"}')


def test_instance_fingerprint_is_not_a_reference_identity() -> None:
    """Equal metadata/repr can hash alike; separate binding names can identify one reference twice.

    This tests fingerprint inputs only, not whether all registry admissions are
    allowed. It documents why definition IDs cannot stand in for live custody IDs.
    """
    class SameRepresentation:
        """Two distinct user values intentionally expose the same representation."""

        def __repr__(self) -> str:
            """Supply an identical fingerprint input without changing Python identity."""
            return "same-value-description"

    first = SameRepresentation()
    second = SameRepresentation()
    assert first is not second
    assert Bind.spell_id_inspector(first) == Bind.spell_id_inspector(second)
    assert Bind.spell_id_inspector(first, binding_name="a") != Bind.spell_id_inspector(first, binding_name="b")
    print('CRYSTAL {"case": "fingerprint", "distinct_references_can_hash_alike": true}')
