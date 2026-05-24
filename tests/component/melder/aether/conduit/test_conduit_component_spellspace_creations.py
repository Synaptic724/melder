from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)
class DisposableService:
    """
    Purpose:
        Provide a disposable service for component spellspace cleanup tests.
    Contract:
        - cleanup increments cleanup_calls for verification.
    """

    def __init__(self) -> None:
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup invocations for disposal verification.
        Contract:
            - Increments cleanup_calls.
        """
        self.cleanup_calls += 1


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_conduit() -> None:
    """
    Purpose:
        Reset the Aether singleton for component Conduit tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook(
    *,
    disposal: bool = False,
    disposal_methods: list[str] | None = None,
) -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component Conduit tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
        - Optional disposal settings are applied before conjure.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    if disposal:
        configuration = SpellbookConfiguration()
        set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
        configuration.set_property("disposal", True)
        configuration.set_property(
            "disposal_method_names",
            list(disposal_methods or ["cleanup"]),
        )
        configuration.load_default_dictionary()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        return Spellbook(configuration=configuration)

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def test_component_conduit_registers_existing_object_after_conjure() -> None:
    """
    Purpose:
        Validate existing-object binds are registered into Creations post-conjure.
    Contract:
        - Binding an instance after conjure registers it in shared creations.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not registered into Creations.
    """
    spellbook = _make_spellbook()

    class SeedService:
        def __init__(self) -> None:
            self.marker = "seed"

    spellbook.bind(
        spell=SeedService,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook._aetheric_frame_configuration.with_system_state("dynamic")
    conduit = spellbook.conjure(automatic=False, name="root")
    existing = BasicService(marker="existing")
    try:
        spellbook.begin_transaction("bind")
        existing_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.end_transaction("bind")
        creations = conduit._creations
        creation = creations._creations.get(existing_id)
        assert creation is not None
        assert creation.value is existing
    finally:
        conduit.cleanup()


def test_component_spellspace_cleanup_disposes_and_clears_bucket() -> None:
    """
    Purpose:
        Validate spellspace cleanup disposes instances and clears the bucket.
    Contract:
        - cleanup triggers disposal for spellspace instances.
        - spellspace creation bucket is cleared after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If disposal or bucket clearing fails.
    """
    spellbook = _make_spellbook(disposal=True, disposal_methods=["cleanup"])
    spell_id = spellbook.bind(
        spell=DisposableService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        with conduit.enter_spellspace() as space:
            instance = space.meld(spell=spell_id)
            creation = creations.get_spellspace_creation(space.id, spell_id)
            assert creation is not None
            assert creation.value is instance
            space_id = space.id
        assert instance.cleanup_calls == 1
        assert creations.get_spellspace_creation(space_id, spell_id) is None
    finally:
        conduit.cleanup()


def test_component_spellspace_cleanup_preserves_other_spellspaces() -> None:
    """
    Purpose:
        Validate cleaning one spellspace does not clear other buckets.
    Contract:
        - cleanup clears only the active spellspace bucket.
        - other spellspace buckets remain intact.
    Returns:
        None.
    Raises:
        AssertionError: If unrelated spellspace buckets are cleared.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        with conduit.enter_spellspace() as outer:
            outer_instance = outer.meld(spell=spell_id)
            with conduit.enter_spellspace() as inner:
                inner.meld(spell=spell_id)
                inner_id = inner.id
            assert creations.get_spellspace_creation(inner_id, spell_id) is None
            outer_creation = creations.get_spellspace_creation(outer.id, spell_id)
            assert outer_creation is not None
            assert outer_creation.value is outer_instance
    finally:
        conduit.cleanup()


def test_component_creations_extract_restore_spellspace_reuses_instance() -> None:
    """
    Purpose:
        Validate spellspace creations extract and restore with live Conduit/Meld.
    Contract:
        - extract_spell_creations removes the spellspace bucket entry.
        - restore_spell_creations rehydrates and enables reuse.
    Returns:
        None.
    Raises:
        AssertionError: If extract/restore does not preserve reuse semantics.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        with conduit.enter_spellspace() as space:
            instance = space.meld(spell=spell_id)
            snapshot = creations.extract_spell_creations(spell_id)
            assert len(snapshot) == 1
            entry = snapshot[0]
            assert entry["scope"] == "spellspace"
            assert entry["spellspace_id"] == space.id
            assert creations.get_spellspace_creation(space.id, spell_id) is None
            creations.restore_spell_creations(spell_id, snapshot)
            restored = space.meld(spell=spell_id)
            assert restored is instance
    finally:
        conduit.cleanup()


def test_component_creations_extract_restore_unique_per_conduit_reuses_instance() -> None:
    """
    Purpose:
        Validate unique-per-conduit creations extract and restore via Meld.
    Contract:
        - extract_spell_creations removes the shared unique entry.
        - restore_spell_creations rehydrates and enables reuse.
    Returns:
        None.
    Raises:
        AssertionError: If extract/restore does not preserve reuse semantics.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=spell_id)
        creations = conduit._creations
        snapshot = creations.extract_spell_creations(spell_id)
        assert len(snapshot) == 1
        entry = snapshot[0]
        assert entry["scope"] == "unique"
        assert creations._creations.get(spell_id) is None
        creations.restore_spell_creations(spell_id, snapshot)
        restored = conduit.meld(spell=spell_id)
        assert restored is instance
    finally:
        conduit.cleanup()
