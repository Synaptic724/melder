from typing import Any, Callable, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence


def compile_solo_no_overrides_codegen_creation_executor(
        *,
        spell: Any,
        resolve_route_key: str,
        fast_transient_no_overrides_enabled: bool,
) -> Callable[..., Any]:
    """
    Compile the solo no-overrides executor for one root spell.

    Purpose:
        Build the spell-static root-only executor for the solo family without
        depending on generalized lane-step machinery.

    Contract:
        - Produces a zero-arg executor only for the transient-many fast path.
        - Produces the standard
          `(caller_creations, owner_creations, caller_creations_lock_held)`
          executor shape for all other solo routes.
        - Specializes route, existence, and disposal posture at compile time so
          hot calls do not keep re-deciding static branch state.
    """
    call_target = spell.spell
    spell_id = spell.spell_id
    has_disposal_methods = spell.has_disposal_methods
    disposal_methods = _normalize_disposal_methods(
        spell.disposal_method_names
    )

    if resolve_route_key == "many":
        if fast_transient_no_overrides_enabled:
            return call_target

        if has_disposal_methods:
            def execute_many_with_disposal(
                    caller_creations: Any,
                    owner_creations: Any = None,
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                add_many_creations = caller_creations.add_many_creations
                instance = call_target()
                add_many_creations(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_many_with_disposal

        def execute_many_no_disposal(
                caller_creations: Any,
                owner_creations: Any = None,
                caller_creations_lock_held: bool = False,
        ) -> Any:
            return call_target()

        return execute_many_no_disposal

    if resolve_route_key in (
            "unique_per_conduit",
            "spellspace",
    ):
        if has_disposal_methods:
            def execute_caller_owned_with_disposal(
                    caller_creations: Any,
                    owner_creations: Any = None,
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                add_creation = caller_creations.add_creation
                instance = call_target()
                add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_caller_owned_with_disposal

        def execute_caller_owned(
                caller_creations: Any,
                owner_creations: Any = None,
                caller_creations_lock_held: bool = False,
        ) -> Any:
            add_creation = caller_creations.add_creation
            instance = call_target()
            add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_caller_owned

    if resolve_route_key == "existing_creation":
        def execute_existing_creation(
                caller_creations: Any,
                owner_creations: Any = None,
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell_id})."
                )
            return instance

        return execute_existing_creation

    prebound_owner_creations = spell._owner_creations
    if prebound_owner_creations is not None:
        if has_disposal_methods:
            add_creation = prebound_owner_creations.add_creation

            def execute_shared_with_disposal(
                    caller_creations: Any,
                    owner_creations: Any = None,
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = call_target()
                add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_shared_with_disposal

        add_creation = prebound_owner_creations.add_creation

        def execute_shared(
                caller_creations: Any,
                owner_creations: Any = None,
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = call_target()
            add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_shared

    if has_disposal_methods:
        def execute_fallback_shared_with_disposal(
                caller_creations: Any,
                owner_creations: Any = None,
                caller_creations_lock_held: bool = False,
        ) -> Any:
            add_creation = owner_creations.add_creation
            instance = call_target()
            add_creation(
                spell_id,
                instance,
                has_disposal_methods=True,
                disposal_methods=disposal_methods,
            )
            return instance

        return execute_fallback_shared_with_disposal

    def execute_fallback_shared(
            caller_creations: Any,
            owner_creations: Any = None,
            caller_creations_lock_held: bool = False,
    ) -> Any:
        add_creation = owner_creations.add_creation
        instance = call_target()
        add_creation(
            spell_id,
            instance,
        )
        return instance

    return execute_fallback_shared


def _normalize_disposal_methods(
        disposal_method_names: Sequence[str],
) -> Optional[Tuple[str, ...]]:
    """
    Normalize spell-owned disposal metadata for creations registration.
    """
    if not disposal_method_names:
        return None
    return tuple(disposal_method_names)
