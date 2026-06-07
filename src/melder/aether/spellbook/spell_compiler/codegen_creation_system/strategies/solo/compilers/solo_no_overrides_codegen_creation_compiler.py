from typing import Any, Callable, Optional, Sequence

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
        - Registration semantics remain truthful to the route family's
          underlying `Existence`.
    """
    if resolve_route_key == "many" and fast_transient_no_overrides_enabled:
        def execute() -> Any:
            return _invoke_spell_target(spell)

        return execute

    def execute(
            caller_creations: Any,
            owner_creations: Any = None,
            caller_creations_lock_held: bool = False,
    ) -> Any:
        _ = caller_creations_lock_held
        if resolve_route_key == "existing_creation":
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell.spell_id})."
                )
            return instance

        creations = _resolve_creations_for_route(
            spell=spell,
            resolve_route_key=resolve_route_key,
            caller_creations=caller_creations,
            owner_creations=owner_creations,
        )
        instance = _invoke_spell_target(spell)
        _register_solo_instance(
            spell=spell,
            instance=instance,
            creations=creations,
        )
        return instance

    return execute


def _invoke_spell_target(
        spell: Any,
) -> Any:
    """
    Invoke the solo root call target with no dependency inputs.
    """
    call_target = spell.spell
    return call_target()


def _resolve_creations_for_route(
        *,
        spell: Any,
        resolve_route_key: str,
        caller_creations: Any,
        owner_creations: Any,
) -> Any:
    """
    Resolve the target creations store for the solo root route.
    """
    if resolve_route_key in (
            "many",
            "unique_per_conduit",
            "spellspace",
    ):
        return caller_creations
    return spell._owner_creations or owner_creations


def _register_solo_instance(
        *,
        spell: Any,
        instance: Any,
        creations: Any,
) -> None:
    """
    Register one solo root instance according to its `Existence`.
    """
    existence = spell.existence
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
            Existence.unique_per_spell_space,
    ):
        creations.add_creation(
            spell.spell_id,
            instance,
            has_disposal_methods=spell.has_disposal_methods,
            disposal_methods=_normalize_disposal_methods(
                spell.disposal_method_names
            ),
        )
        return

    if existence is Existence.many:
        if not spell.has_disposal_methods:
            return
        creations.add_many_creations(
            spell.spell_id,
            instance,
            has_disposal_methods=True,
            disposal_methods=_normalize_disposal_methods(
                spell.disposal_method_names
            ),
        )
        return

def _normalize_disposal_methods(
        disposal_method_names: Sequence[str],
) -> Optional[Sequence[str]]:
    """
    Normalize spell-owned disposal metadata for creations registration.
    """
    if not disposal_method_names:
        return None
    return tuple(disposal_method_names)
