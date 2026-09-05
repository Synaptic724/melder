"""Established method-list ownership across scoped registration, transfer, and reuse."""

import pytest

from melder.aether.conduit.creations.creations import Creations
from tests.unit.melder.aether.conduit.creations.test_creations_disposal_all_methods_regression import (
    MultiMethodDisposalProbe,
)


@pytest.mark.parametrize("many", [False, True])
@pytest.mark.parametrize("with_methods", [False, True])
def test_registration_and_transfer_preserve_disposal_reference(many: bool, with_methods: bool) -> None:
    """Both transfer shapes carry the same list and invoke it correctly after the source is gone."""
    names = ["release", "close", "flush"] if with_methods else []
    source = Creations(owner_conduit_id="owner", id="source")
    target = Creations(owner_conduit_id="owner", id="target")
    probes = [MultiMethodDisposalProbe() for _ in range(2 if many else 1)]
    try:
        register = source.add_many_creations if many else source.add_creation
        for probe in probes:
            register("spell", probe, has_disposal_methods=True, disposal_methods=names)
        extracted = source.extract_spell_creations("spell")
        assert source.get_creation("spell") is None
        assert len(extracted) == len(probes)
        for row, probe in zip(extracted, probes):
            assert row["stored"] is probe
            assert row["disposal_methods"] is names
        source.cleanup()
        assert all(probe.calls == [] for probe in probes)
        target.restore_spell_creations("spell", extracted)
        restored = target.extract_spell_creations("spell")
        for row in restored:
            assert row["disposal_methods"] is names
        target.restore_spell_creations("spell", restored)
        target.cleanup()
        expected = ["release", "close", "flush"] if with_methods else []
        assert names == expected
        assert all(probe.calls == expected for probe in probes)
    finally:
        source.cleanup()
        target.cleanup()


@pytest.mark.parametrize("many", [False, True])
@pytest.mark.parametrize("clear_mode", ["clear", "pool", "confined_pool"])
def test_reusable_clearing_keeps_borrowed_names(many: bool, clear_mode: str) -> None:
    """Clearing a scope executes names once without emptying the policy needed by its next use."""
    names = ["release", "close", "flush"]
    store = Creations(owner_conduit_id="owner", id="scope")
    first = MultiMethodDisposalProbe()
    second = MultiMethodDisposalProbe()
    try:
        register = store.add_many_creations if many else store.add_creation
        register("spell", first, has_disposal_methods=True, disposal_methods=names)
        rows = store.extract_spell_creations("spell")
        assert rows[0]["disposal_methods"] is names
        store.restore_spell_creations("spell", rows)
        if clear_mode == "clear":
            store.clear_all()
        elif clear_mode == "pool":
            store.reset_for_pool()
        else:
            # This test owns the store on one thread, satisfying the confined caller contract.
            store.reset_for_pool_unlocked()
        assert store.get_creation("spell") is None
        assert first.calls == ["release", "close", "flush"]
        assert names == ["release", "close", "flush"]
        register("spell", second, has_disposal_methods=True, disposal_methods=names)
        store.cleanup()
        assert second.calls == ["release", "close", "flush"]
    finally:
        store.cleanup()


@pytest.mark.parametrize("many", [False, True])
def test_omitted_names_keep_existing_empty_metadata_behavior(many: bool) -> None:
    """Optional missing names retain their existing empty-list behavior through a transfer."""
    store = Creations(owner_conduit_id="owner", id="scope")
    probe = MultiMethodDisposalProbe()
    try:
        register = store.add_many_creations if many else store.add_creation
        register("spell", probe, has_disposal_methods=True)
        rows = store.extract_spell_creations("spell")
        assert rows[0]["disposal_methods"] == []
        store.restore_spell_creations("spell", rows)
        store.cleanup()
        assert probe.calls == []
    finally:
        store.cleanup()


@pytest.mark.parametrize("many", [False, True])
def test_disabled_disposal_does_not_attach_names(many: bool) -> None:
    """A false registration flag still prevents disposal even when names are supplied."""
    store = Creations(owner_conduit_id="owner", id="scope")
    probe = MultiMethodDisposalProbe()
    try:
        register = store.add_many_creations if many else store.add_creation
        register("spell", probe, disposal_methods=["release", "close"])
        rows = store.extract_spell_creations("spell")
        assert rows[0]["disposable"] is False
        store.restore_spell_creations("spell", rows)
        store.cleanup()
        assert probe.calls == []
    finally:
        store.cleanup()
