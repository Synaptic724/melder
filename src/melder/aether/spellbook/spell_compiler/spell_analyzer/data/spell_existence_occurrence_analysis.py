from dataclasses import dataclass
from typing import Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence


@dataclass(frozen=True, slots=True)
class SpellExistenceOccurrence:
    """
    One visible spell-id to existence row captured during the phase-8 spell walk.
    """

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
    """

    root_existence: Optional[Existence]
    total_spell_count: int
    spell_existence_rows: Tuple[SpellExistenceOccurrence, ...]
    existence_counts: Tuple[Tuple[Existence, int], ...]
    disposal_enabled_spell_count: int
    existence_disposal_counts: Tuple[Tuple[Tuple[Existence, bool], int], ...]
