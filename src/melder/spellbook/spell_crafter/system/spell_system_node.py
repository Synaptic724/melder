from __future__ import annotations
from typing import Dict, Iterable, Mapping, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellSystemNode(Cleanable):
    """
    Internal

    Version-id keyed system view of a single spell for Phases 5–7.

    This does *not* replace SpellSystemStates (which is lineage/DevOps centric).
    Instead, it gives Phase 5+ a small, version-centric node type to hang
    structural metadata on:

        * spell_id     – version id (SpellIndex.current).
        * lineage_id   – lineage ULID (SpellIndex.id).
        * dependencies – direct dependency spell_ids (version ids).
        * existence    – lifecycle / policy hint (optional).
        * spell_type   – logical spell role (optional).
        * conduit_id   – owning conduit (optional).
        * ward_id      – owning ward (optional).
        * is_root      – whether this spell is considered a root for the frame.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_spell_id",
        "_lineage_id",
        "_dependencies",
        "existence",
        "spell_type",
        "conduit_id",
        "ward_id",
        "is_root",
    ]

    def __init__(
            self,
            spell_id: str,
            lineage_id: str,
            *,
            dependencies: Optional[Iterable[str]] = None,
            existence: Optional[Existence] = None,
            spell_type: Optional[SpellType] = None,
            conduit_id: Optional[str] = None,
            ward_id: Optional[str] = None,
            is_root: bool = False,
    ) -> None:
        super().__init__()

        if spell_id is None:
            raise ValueError("spell_id must not be None.")
        if lineage_id is None:
            raise ValueError("lineage_id must not be None.")

        self._spell_id: str = spell_id
        self._lineage_id: str = lineage_id
        self._dependencies: set[str] = set(dependencies or ())

        # Optional metadata – callers are free to ignore these.
        self.existence: Optional[Existence] = existence
        self.spell_type: Optional[SpellType] = spell_type
        self.conduit_id: Optional[str] = conduit_id
        self.ward_id: Optional[str] = ward_id
        self.is_root: bool = is_root

    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down this node.

        Behaviour:
            * Idempotent.
            * Drops the dependency set and metadata references.
        """
        if self._cleaned:
            return

        self._cleaned = True

        self._dependencies.clear()
        self._dependencies = None

        self.existence = None
        self.spell_type = None
        self.conduit_id = None
        self.ward_id = None
        self.is_root = False

        self._spell_id = None
        self._lineage_id = None

    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def spell_id(self) -> str:
        self.check_cleaned()
        return self._spell_id

    @property
    def lineage_id(self) -> str:
        self.check_cleaned()
        return self._lineage_id

    @property
    def dependencies(self) -> set[str]:
        """
        Snapshot of direct dependency version ids for this spell.
        """
        self.check_cleaned()
        return set(self._dependencies)

    # ------------------------------------------------------------------ #
    # Mutators                                                           #
    # ------------------------------------------------------------------ #

    def add_dependency(self, spell_id: str) -> None:
        """
        Add a single direct dependency.
        """
        self.check_cleaned()
        if spell_id is None:
            raise ValueError("spell_id must not be None.")
        self._dependencies.add(spell_id)

    def add_dependencies(self, spell_ids: Iterable[str]) -> None:
        """
        Union in multiple direct dependencies.
        """
        self.check_cleaned()
        if spell_ids is None:
            raise ValueError("spell_ids must not be None.")
        for dep in spell_ids:
            if dep is None:
                continue
            self._dependencies.add(dep)
