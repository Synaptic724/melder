"""
Compiler passes on the meld-time path read one copy of the spell pool.

A bind, notch, contract grant or transfer on another thread changes `Spellbook._spell_id_pool` under the
Spellbook lock while meld-time revalidation runs compiler passes without it. Iterating the live dict then
raised "dictionary changed size during iteration" (seen in the free-threaded multithreading suite), and the
Phase-8 pool walk swallowed the same error and dropped its analysis. These tests stand a pool that grows during
iteration in for the concurrent writer, and a pool entry without a registered state in for a bind caught
between publishing the entry and registering its state.
"""
from typing import Any, Dict, Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import CompilerPhase5
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_6 import CompilerPhase6
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import SpellCompilerSystem
from melder.aether.spellbook.spellbook import Spellbook


class PoolConfig:
    """Leaf dependency of the test graph."""

    def __init__(self) -> None:
        """Take no inputs."""
        self.name = "config"


class PoolRepository:
    """Middle dependency of the test graph."""

    def __init__(self, config: PoolConfig) -> None:
        """Keep the injected config."""
        self.config = config


class PoolService:
    """Root of the test graph."""

    def __init__(self, repository: PoolRepository) -> None:
        """Keep the injected repository."""
        self.repository = repository


class _GrowsWhileIterated(dict):
    """
    Spell pool that gains an entry while it is being iterated, as it does when another thread binds.

    Contract:
        - `items()`, `values()`, `keys()` and plain iteration yield the first entry, then insert one more entry,
          so the underlying dict iterator raises "dictionary changed size during iteration" on its next step,
          exactly as a live iteration does under a concurrent bind.
        - `copy()` returns a plain dict of the current entries without growing, as a real pool's copy does
          (dict's own copy would go through the overridden iteration), so a pass that iterates a copy sees the
          pool as it was when the copy was taken.
    """

    def __init__(self, source: Dict[str, Spell], late_spell: Spell) -> None:
        """
        Copy `source` and remember the spell object the simulated bind inserts.

        Args:
            source: The live pool to stand in for.
            late_spell: Spell object stored under the inserted id.
        """
        super().__init__(source)
        self._late_spell = late_spell

    def _grow_after_first(self, source: Iterator[Any]) -> Iterator[Any]:
        """Yield from `source`, inserting one entry after the first item."""
        grown = False
        for item in source:
            yield item
            if not grown:
                grown = True
                dict.__setitem__(self, "concurrent-bind-id", self._late_spell)

    def copy(self) -> Dict[str, Spell]:
        """Return a plain dict of the current entries, without growing."""
        return dict(dict.items(self))

    def items(self) -> Iterator[Tuple[str, Spell]]:  # the override returns an iterator on purpose
        """Iterate items while growing."""
        return self._grow_after_first(iter(dict.items(self)))

    def values(self) -> Iterator[Spell]:
        """Iterate values while growing."""
        return self._grow_after_first(iter(dict.values(self)))

    def keys(self) -> Iterator[str]:
        """Iterate keys while growing."""
        return self._grow_after_first(iter(dict.keys(self)))

    def __iter__(self) -> Iterator[str]:
        """Iterate keys while growing."""
        return self._grow_after_first(dict.__iter__(self))


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """
    Give each test a fresh Aether and rebind Spellbook and Conduit to it, before and after.

    Yields:
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


def _conjured_book() -> Tuple[Spellbook, Conduit, Dict[type, Spell]]:
    """
    Bind PoolService -> PoolRepository -> PoolConfig and conjure.

    Returns:
        Tuple[Spellbook, Conduit, Dict[type, Spell]]: The book, its root conduit and the spells by class.
    """
    book = Spellbook()
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.bind(spell=PoolConfig, existence="unique")
    book.bind(spell=PoolRepository, existence="many")
    book.bind(spell=PoolService, existence="many")
    conduit = book.conjure()
    spells = {spell.spell: spell for spell in book._spell_id_pool.values()}
    return book, conduit, spells


def _install_growing_pool(book: Spellbook, late_spell: Spell) -> _GrowsWhileIterated:
    """Replace the book's pool with a copy that grows while iterated; return it."""
    pool = _GrowsWhileIterated(book._spell_id_pool, late_spell)
    book._spell_id_pool = pool
    return pool


def test_structural_rerun_survives_a_bind_during_its_pool_scans() -> None:
    """Phases 1-4 of one spell (the meld-time rerun) complete while the pool grows under them."""
    book, _conduit, spells = _conjured_book()
    service = spells[PoolService]
    repository = spells[PoolRepository]
    _install_growing_pool(book, spells[PoolConfig])

    system = SpellCompilerSystem()
    try:
        system.run_structural_phases(book, service)
    finally:
        system.cleanup()

    assert repository.spell_id in service.dependencies


def test_local_resolution_survives_a_bind_during_phase5() -> None:
    """Phase 5 local builds the target's closure while the pool grows under it."""
    book, conduit, spells = _conjured_book()
    service = spells[PoolService]
    _install_growing_pool(book, spells[PoolConfig])

    CompilerPhase5().run_local(
        service,
        service._compiler_artifact,
        book,
        book._spell_system_states,
        conduit._id,
    )

    node_ids = set(service._compiler_artifact._spell_system_index_phase5.nodes.keys())
    assert node_ids == {spell.spell_id for spell in spells.values()}


def test_frame_wide_phases_5_and_6_survive_a_bind() -> None:
    """Phase 5 and Phase 6 frame-wide complete while the pool grows under them."""
    book, conduit, spells = _conjured_book()
    service = spells[PoolService]
    _install_growing_pool(book, spells[PoolConfig])

    CompilerPhase5().run_frame_wide(
        service,
        service._compiler_artifact,
        book,
        book._spell_system_states,
        conduit._id,
    )
    CompilerPhase6().run_frame_wide(
        service._compiler_artifact,
        book,
        book._spell_system_states,
        conduit._id,
    )

    node_ids = set(service._compiler_artifact._spell_system_index_phase5.nodes.keys())
    assert node_ids == {spell.spell_id for spell in spells.values()}
    assert service._compiler_artifact._validated_phase6 is True


def test_frame_wide_phase5_leaves_out_a_pool_entry_whose_state_is_not_registered_yet() -> None:
    """A bind publishes its pool entry before its state; Phase 5 leaves that spell to the next revalidation."""
    book, conduit, spells = _conjured_book()
    service = spells[PoolService]
    book._spell_id_pool["registered-later-id"] = spells[PoolConfig]

    CompilerPhase5().run_frame_wide(
        service,
        service._compiler_artifact,
        book,
        book._spell_system_states,
        conduit._id,
    )

    node_ids = set(service._compiler_artifact._spell_system_index_phase5.nodes.keys())
    assert "registered-later-id" not in node_ids
    assert node_ids == {spell.spell_id for spell in spells.values()}


def test_phase8_pool_walk_keeps_its_rows_when_a_bind_lands() -> None:
    """The Phase-8 walk returns its rows, not None, while the pool grows under it."""
    book, _conduit, spells = _conjured_book()
    pool = _install_growing_pool(book, spells[PoolConfig])

    walk = SpellOccurrenceGraphAnalyzerStrategy._build_spell_walk_rows(spell_lookup=pool)

    assert walk is not None
    spell_rows = walk[0]
    assert {row[0] for row in spell_rows} == {spell.spell_id for spell in spells.values()}
