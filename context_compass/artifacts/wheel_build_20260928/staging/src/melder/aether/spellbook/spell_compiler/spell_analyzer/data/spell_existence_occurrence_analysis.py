from dataclasses import dataclass
from typing import Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence


@dataclass(frozen=True, slots=True)
class SpellExistenceOccurrence:
    """
    One visible spell-id to existence row captured during the phase-8 spell walk.

    Subsystem Context:
        A row inside `SpellExistenceOccurrenceAnalysis`, captured during the Phase-8
        spell walk in the `spell_analyzer` package.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline. Value-only.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. One Phase-8 value row: spell_id + its Existence +
        has_disposal_methods. Frozen value object captured during the spell walk.
    """

    # Unannotated on purpose: annotated class vars can be misread as dataclass
    # fields on some Python versions; unannotated attrs never are.
    spell_id: str
    existence: Existence
    has_disposal_methods: bool


@dataclass(frozen=True, slots=True)
class SpellExistenceOccurrenceAnalysis:
    """
    Phase-8 existence-occurrence capture.

    Purpose:
        Hold both the raw spell-id/existence rows and the aggregate existence
        counts in one immutable payload with no live spell references.

    Subsystem Context:
        The aggregate of `SpellExistenceOccurrence` rows in the `spell_analyzer`
        package; carried on `SpellOccurrenceGraphAnalysis`.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline; feeds later planning
        without holding live spells.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-8 existence-occurrence payload: root_existence,
        total_spell_count, spell_existence_rows, existence_counts, and disposal counts.
        Immutable, no live spell refs.
    """

    # Unannotated on purpose: annotated class vars can be misread as dataclass fields.
    root_existence: Optional[Existence]
    total_spell_count: int
    spell_existence_rows: Tuple[SpellExistenceOccurrence, ...]
    existence_counts: Tuple[Tuple[Existence, int], ...]
    disposal_enabled_spell_count: int
    existence_disposal_counts: Tuple[Tuple[Tuple[Existence, bool], int], ...]
