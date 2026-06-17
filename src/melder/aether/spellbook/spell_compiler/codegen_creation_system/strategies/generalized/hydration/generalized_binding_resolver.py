"""
Binding resolvers for the generalized codegen-creation family.

A binding resolver is the single seam where executor hydration touches live
runtime state. Everything else the hydrator consumes is manifest data.

Two resolvers exist because the same hydrator serves two callers:

  - `PlanBindingResolver` backs the live phase-11 path, resolving spells from
    the lane plans and runtime shape already in hand.
  - `SpellbookBindingResolver` backs the cache-load path, resolving spells
    from the live Spellbook pool and the phase-5 root blueprint.

Ownership:
    Resolvers REFERENCE plan/model/spell state; they own nothing. The caller
    that constructs a resolver owns it for the duration of one hydration pass
    and calls `cleanup()` when that pass completes.
"""

from typing import Any, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class PlanBindingResolver(Cleanable):
    """
    Live phase-11 binding resolver over plan/model truth.

    Contract:
        - Resolves spells from the runtime-shape records first, then from lane
          plan steps.
        - Resolves the path registry from analyzer graph-shape truth; `None`
          is a valid result and downstream override compilation tolerates it.

    Lifecycle / Cleanup:
        - Owned by the phase-11 step that builds it, for one apply pass.
        - `cleanup()` is idempotent and deletes the reference maps; the spells
          and registry are referenced, never owned.
    """

    __slots__ = Cleanable.__slots__ + [
        "_records_by_spell_id",
        "_spells_by_id",
        "_path_registry",
    ]

    def __init__(
            self,
            *,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
    ) -> None:
        """
        Build one live resolver from phase-9 model and phase-10 plan truth.
        """
        super().__init__()
        runtime_shape = spell_codegen_model.spell_runtime_shape
        if runtime_shape is None:
            self._records_by_spell_id: Dict[str, Any] = {}
        else:
            self._records_by_spell_id = runtime_shape.records_by_spell_id

        spells_by_id: Dict[str, Any] = {}
        for lane_plan in (
                spell_codegen_plan.no_overrides_plan,
                spell_codegen_plan.overrides_plan,
        ):
            if lane_plan is None:
                continue
            for step in lane_plan.steps:
                spell_id = step.spell.spell_index.selected_spell_id
                if spell_id not in spells_by_id:
                    spells_by_id[spell_id] = step.spell
        self._spells_by_id = spells_by_id

        graph_shape = spell_codegen_model.graph_shape
        self._path_registry = (
            None if graph_shape is None else graph_shape.path_registry
        )

    def cleanup(self) -> None:
        """
        Deterministically release this resolver's reference surface.

        Contract:
            - Idempotent. Referenced state only; no child cleanup runs.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._records_by_spell_id
        del self._spells_by_id
        del self._path_registry

    def resolve_spell(self, spell_id: str) -> Any:
        """
        Return one live spell for the supplied current spell id.
        """
        self.check_cleaned()
        record = self._records_by_spell_id.get(spell_id)
        if record is not None:
            return record.spell
        spell = self._spells_by_id.get(spell_id)
        if spell is None:
            raise RuntimeError(
                "PlanBindingResolver could not resolve spell_id "
                f"'{spell_id}' from plan or runtime-shape truth."
            )
        return spell

    def resolve_path_registry(self) -> Optional[Any]:
        """
        Return the phase-5 path registry, or `None` when unavailable.
        """
        self.check_cleaned()
        return self._path_registry


class SpellbookBindingResolver(Cleanable):
    """
    Cache-load binding resolver over the live Spellbook surface.

    Contract:
        - Resolves spells from the owning Spellbook's spell-id pool.
        - Resolves the path registry from the live phase-5 root blueprint,
          which conjure builds and `reset_phase_artifacts` preserves.
        - Raises with a clear message when prerequisites are not live, because
          a hydration without phases 1-7 is a sequencing bug.

    Lifecycle / Cleanup:
        - Owned by the hydration pass that builds it (lazy-door first meld or
          eager codec load).
        - `cleanup()` is idempotent and deletes the spell reference; the spell
          is referenced, never owned.
    """

    __slots__ = Cleanable.__slots__ + [
        "_spell",
    ]

    def __init__(
            self,
            *,
            spell: Any,
    ) -> None:
        """
        Build one cache-load resolver bound to the spell being hydrated.
        """
        super().__init__()
        self._spell = spell

    def cleanup(self) -> None:
        """
        Deterministically release this resolver's reference surface.

        Contract:
            - Idempotent. Referenced state only; no child cleanup runs.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spell

    def resolve_spell(self, spell_id: str) -> Any:
        """
        Return one live spell from the owning Spellbook pool.
        """
        self.check_cleaned()
        spellbook = self._spell._spellbook
        if spellbook is None:
            raise RuntimeError("Spell has no owning Spellbook surface.")
        resolved_spell = spellbook._spell_id_pool.get(spell_id)
        if resolved_spell is None:
            raise RuntimeError(
                "generalized manifest references unknown spell_id "
                f"'{spell_id}'."
            )
        return resolved_spell

    def resolve_path_registry(self) -> Optional[Any]:
        """
        Return the live phase-5 path registry for override specialization.
        """
        self.check_cleaned()
        artifact = self._spell._compiler_artifact
        if artifact is None:
            raise RuntimeError(
                "Spell has no compiler artifact for manifest hydration."
            )
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "Manifest hydration requires a live phase-5 root blueprint "
                f"(spell_id={self._spell.spell_id})."
            )
        return root_blueprint.path_registry
