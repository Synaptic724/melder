"""Characterize current reference custody; these passing observations are not repair acceptance.

Public bind/notch/transfer/meld verbs drive the transitions. Private store reads
observe custody only; no production behavior is patched. The imported fixture
provides a fresh dynamic world, disabled disk cache and deterministic cleanup.
"""

import json
from pathlib import Path

import pytest

import melder.aether.spellbook.spellbook as spellbook_module
from melder.aether.spellbook.spellbook import Spellbook
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)


class ProbeValue:
    """Externally constructed, non-callable value with observable disposal and identity."""

    def __init__(self, marker: str) -> None:
        """Retain a marker and count disposal without allocating external resources."""
        self.marker = marker
        self.disposals = 0

    def dispose(self) -> None:
        """Count actual lifecycle calls; metadata presence alone is insufficient."""
        self.disposals += 1


@pytest.mark.parametrize("move_creations", (False, True))
def test_transfer_store_and_returned_reference(
        instance_book: Spellbook, move_creations: bool,
) -> None:
    """Observe whether store custody follows the same reference returned after transfer.

    Contract: use the public transaction-backed transfer unchanged, compare both
    stores before any target meld, then verify the actual returned identity.
    """
    assert Path(spellbook_module.__file__).resolve() == (
        Path.cwd() / "src/melder/aether/spellbook/spellbook.py"
    ).resolve()
    supplied = ProbeValue("external")
    spell_id = instance_book.bind(
        spell=supplied, existence="unique", spellframe=ProbeValue,
        binding_name="value", disposal_method_names=["dispose"],
    )
    source = instance_book.conjure(dynamic=True, name="source")
    target_book = Spellbook(aetheric_frame=instance_book._aetheric_frame_name)
    target = target_book.conjure(dynamic=True, name="target")
    try:
        assert source._creations.get_creation(spell_id) is supplied
        source.transfer_spell_ownership(
            spell=spell_id, target_conduit=target, move_creations=move_creations,
        )
        source_has_value = source._creations.get_creation(spell_id) is supplied
        target_has_value = target._creations.get_creation(spell_id) is supplied
        result = target.meld(spell_id=spell_id)
        assert result is supplied
        assert not source_has_value
        assert target_has_value is move_creations
        print("REFERENCE " + json.dumps({
            "case": "transfer", "move_creations": move_creations,
            "source_store_has_value": source_has_value,
            "target_store_has_value_before_meld": target_has_value,
            "target_store_has_value_after_meld": target._creations.get_creation(spell_id) is supplied,
            "meld_returns_supplied": result is supplied,
            "disposals_before_cleanup": supplied.disposals,
        }, sort_keys=True))
    finally:
        target.permanent_cleanup()
    assert supplied.disposals == 0


@pytest.mark.parametrize("stage_before_conjure", (False, True))
def test_staged_reference_selection_and_store_admission(
        instance_book: Spellbook, stage_before_conjure: bool,
) -> None:
    """Observe stored-versus-resolvable state through staging and public selection.

    These are characterization assertions. Any runtime refusal is printed with
    its exact type/message and is not called successful injection.
    """
    active = ProbeValue("active")
    staged = ProbeValue("staged")
    active_id = instance_book.bind(
        spell=active, existence="unique", spellframe=ProbeValue, binding_name="value",
    )
    index = instance_book._spells_by_id[active_id].spell_index
    root = None
    if not stage_before_conjure:
        root = instance_book.conjure(dynamic=True, name="root")
    staged_id = instance_book.bind_inactive(
        spell=staged, spell_index=index, existence="unique",
        spellframe=ProbeValue, binding_name="value",
    )
    staged_spell = instance_book._inactive_spells[staged_id]
    if stage_before_conjure:
        root = instance_book.conjure(dynamic=True, name="root")
    assert root is not None
    assert root._creations.get_creation(active_id) is active
    assert root._creations.get_creation(staged_id) is None
    report: dict[str, object] = {
        "case": "staged", "stage_before_conjure": stage_before_conjure,
        "stage": "notch", "stored_before_notch": False,
    }
    try:
        root.notch_spell(spell_index=index, spell=staged_spell)
        report["stored_after_notch"] = root._creations.get_creation(staged_id) is staged
        report["stage"] = "meld"
        result = root.meld(spell_id=staged_id)
    except (RuntimeError, ValueError, KeyError, AttributeError) as error:
        report.update(outcome="refused", error_type=type(error).__name__, error=str(error))
    else:
        assert result is staged
        report.update(
            outcome="returned_supplied", meld_returns_staged=True,
            stored_after_meld=root._creations.get_creation(staged_id) is staged,
        )
    print("REFERENCE " + json.dumps(report, sort_keys=True))
