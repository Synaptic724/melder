from typing import TYPE_CHECKING, Dict, List, Any, Optional



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class DuplicateSpellNameStrategy(SpellValidationStrategy):
    """
    Detect spells that share the same ``spell_name`` within the visible Spellbook
    (local + contracted).

    Now that `meld(...)` can resolve by ``spell_name`` / simple string, having
    multiple visible spells with the same name makes name-based resolution
    ambiguous and unsafe.

    This strategy treats such overlaps as **errors** and instructs the user to
    disambiguate via spellframe and/or binding_name.

    Contract:
    - Uses the visible spellbook spell pool as the source of truth.
    - Treats duplicate visible `spell_name` values as a hard ambiguity for
      name-based resolution.
    - Emits validation issues only; it does not rename or partition spells.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the duplicate-spell-name strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="duplicate_spell_name",
            description=(
                "Detects multiple visible spells that share the same spell_name, "
                "which would make name-based resolution via meld(spell_name=...) "
                "ambiguous."
            ),
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Detect ambiguous visible spell-name collisions.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Uses the spellbook's visible spell pool to collect collisions.
        - Emits one `DUPLICATE_SPELL_NAME` issue when more than one visible
          spell shares the same name.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        spellbook = context.spellbook

        # If we don't have a spell or a spellbook, we can't do any global checks.
        if spell is None or spellbook is None:
            return

        spell_name = spell.spell_name
        if not spell_name:
            # Nothing to check if this spell has no name.
            return

        # Pass-scoped memo: the name->collisions map derives only from
        # bind-transactional pool truth, so one build serves every spell in
        # the validation pass (mirrors the binding-graph memo). Without a
        # pass cache (deferred single-spell paths) the map is built fresh,
        # matching the previous per-spell scan byte-for-byte.
        pass_cache = context.validation_pass_cache
        name_collisions: Optional[Dict[str, List[Dict[str, Any]]]] = None
        if pass_cache is not None:
            name_collisions = pass_cache.get("duplicate_name_collisions")
        if name_collisions is None:
            name_collisions = {}
            for spell_id, other_spell in spellbook._spell_id_pool.items():
                other_name = other_spell.spell_name
                if not other_name:
                    continue
                index = other_spell.spell_index
                name_collisions.setdefault(other_name, []).append(
                    {
                        "spell_index_id": index.id,
                        "spell_id": spell_id,
                        "spellframe": other_spell.spellframe,
                        "binding_name": other_spell.binding_name,
                    }
                )
            if pass_cache is not None:
                pass_cache["duplicate_name_collisions"] = name_collisions

        collisions = name_collisions.get(spell_name, [])

        # If this spell is the only one with that name, we're fine.
        if len(collisions) <= 1:
            return

        context.issues.append(
            SpellValidationIssue(
                severity="error",
                code="DUPLICATE_SPELL_NAME",
                message=(
                    f"Multiple visible spells share the name {spell_name!r}. "
                    "Name-based resolution via meld(spell_name=...) would be "
                    "ambiguous. Disambiguate by using a spellframe (Protocol/"
                    "string frame key) and/or a binding_name so that each "
                    "resolution path is uniquely identifiable."
                ),
                details={
                    "spell_name": spell_name,
                    "collision_count": len(collisions),
                    "collisions": collisions,
                },
            )
        )
