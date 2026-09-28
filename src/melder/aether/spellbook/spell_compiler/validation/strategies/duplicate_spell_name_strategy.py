from typing import TYPE_CHECKING, Dict, List, Any, Optional, Tuple



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class DuplicateSpellNameStrategy(SpellValidationStrategy):
    """
    Detect spells that claim the same lookup address within the visible Spellbook
    (local + contracted).

    Registration and Meld identify a spell by its normalized ``(frame_key,
    binding_key)``. An explicit spellframe replaces the display name in that
    address; distinct frames or bindings therefore disambiguate same-named spells.

    Equal addresses are errors regardless of display name or resolution
    capability. Ordinary binding admission already prevents them; this strategy
    checks the same invariant over the visible validation pool.

    Contract:
    - Uses the visible spellbook spell pool as the source of truth.
    - Uses SpellInputUtils so case and default bindings match runtime lookup.
    - Permits shared display names when their canonical addresses differ.
    - Preserves the ``DUPLICATE_SPELL_NAME`` code for actual address collisions.
    - Emits validation issues only; it does not rename or partition spells.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family, keyed off the same
        `_spell_id_pool` the dangling/circular strategies read.

    System Context:
        Phase 4 (validation) of the conjure pipeline. It checks the same address
        identity used by binding admission and name/frame-based Meld resolution.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: collects visible spells by normalized lookup
        address (pass-cached) and emits DUPLICATE_SPELL_NAME for a shared address. Same-named
        spells at distinct addresses are valid. Advises changing the frame or binding.
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
                "Detects multiple visible spells that share a normalized lookup "
                "address (frame_key, binding_key)."
            ),
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Detect visible collisions at the canonical frame/binding address.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Uses the spellbook's visible spell pool to collect collisions.
        - Normalizes addresses with the same helper as registration and Meld.
        - Emits one `DUPLICATE_SPELL_NAME` issue when more than one visible
          spell claims the target address, including discoverable definitions.
        - Reuses a completed collision map only within the supplied validation
          pass; without a cache, each invocation examines a fresh pool copy.
        - Does not mutate registrations or their resolution capability.
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

        lookup_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spell.spellframe,
            spell_name=spell_name,
            binding_name=spell.binding_name,
        )

        # Pass-scoped memo: the address->collisions map derives only from
        # bind-transactional pool truth, so one build serves every spell in
        # the validation pass (mirrors the binding-graph memo). Without a
        # pass cache (deferred single-spell paths) the map is built fresh,
        # with the same address semantics as the shared-pass path.
        pass_cache = context.validation_pass_cache
        address_collisions: Optional[Dict[Tuple[str, str], List[Dict[str, Any]]]] = None
        if pass_cache is not None:
            address_collisions = pass_cache.get("duplicate_lookup_collisions")
        if address_collisions is None:
            address_collisions = {}
            # A copy: concurrent binds change the live pool under the Spellbook lock, not held here.
            for spell_id, other_spell in spellbook._spell_id_pool.copy().items():
                other_name = other_spell.spell_name
                if not other_name:
                    continue
                other_key = SpellInputUtils.make_spell_key_from_parts(
                    spellframe=other_spell.spellframe,
                    spell_name=other_name,
                    binding_name=other_spell.binding_name,
                )
                index = other_spell.spell_index
                address_collisions.setdefault(other_key, []).append(
                    {
                        "spell_index_id": index.id,
                        "spell_id": spell_id,
                        "spell_name": other_name,
                        "spellframe": other_spell.spellframe,
                        "binding_name": other_spell.binding_name,
                    }
                )
            if pass_cache is not None:
                pass_cache["duplicate_lookup_collisions"] = address_collisions

        collisions = address_collisions.get(lookup_key, [])

        # If this spell is the only one at that address, we're fine.
        if len(collisions) <= 1:
            return

        context.issues.append(
            SpellValidationIssue(
                severity="error",
                code="DUPLICATE_SPELL_NAME",
                message=(
                    "Multiple visible spells share the lookup address "
                    f"frame={lookup_key[0]!r}, binding={lookup_key[1]!r}. "
                    "Use a distinct spellframe or binding_name so that each "
                    "registration has a unique normalized address."
                ),
                details={
                    "spell_name": spell_name,
                    "lookup_key": lookup_key,
                    "collision_count": len(collisions),
                    "collisions": collisions,
                },
            )
        )
