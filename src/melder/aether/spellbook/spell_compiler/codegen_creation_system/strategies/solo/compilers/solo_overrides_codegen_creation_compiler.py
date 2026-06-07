from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence


def compile_solo_overrides_codegen_creation_executor(
        *,
        spell: Any,
        resolve_route_key: str,
) -> Callable[..., Any]:
    """
    Compile the solo overrides executor for one root spell.

    Purpose:
        Build the spell-static root-only override executor for the solo family
        without depending on generalized step-plan or override-targeting
        machinery.

    Contract:
        - Consumes only root positional overrides and root keyword overrides.
        - Produces the standard
          `(caller_creations, overrides, caller_creations_lock_held)` executor
          shape expected by `CreationContext`.
        - Registration semantics remain truthful to the route family's
          underlying `Existence`.
    """
    def execute(
            caller_creations: Any,
            overrides: Optional[Dict[str, Any]],
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
        )
        keyword_overrides, positional_overrides = _split_override_payload(
            overrides
        )
        instance = _invoke_spell_target_with_overrides(
            spell=spell,
            keyword_overrides=keyword_overrides,
            positional_overrides=positional_overrides,
        )
        _register_solo_instance(
            spell=spell,
            instance=instance,
            creations=creations,
        )
        return instance

    return execute


def _resolve_creations_for_route(
        *,
        spell: Any,
        resolve_route_key: str,
        caller_creations: Any,
) -> Any:
    """
    Resolve the target creations store for the solo root override route.
    """
    if resolve_route_key in (
            "many",
            "unique_per_conduit",
            "spellspace",
    ):
        return caller_creations
    return spell._owner_creations


def _split_override_payload(
        overrides: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
    """
    Split root keyword overrides from optional root positional overrides.
    """
    if not overrides:
        return {}, None
    raw_args = overrides.get("__args__")
    if raw_args is None:
        return dict(overrides), None
    if isinstance(raw_args, tuple):
        positional_overrides = raw_args
    elif isinstance(raw_args, list):
        positional_overrides = tuple(raw_args)
    else:
        raise RuntimeError("__args__ override must be a list or tuple.")
    if len(overrides) == 1:
        return {}, positional_overrides
    keyword_overrides: Dict[str, Any] = {}
    for param_name, value in overrides.items():
        if param_name == "__args__":
            continue
        keyword_overrides[param_name] = value
    return keyword_overrides, positional_overrides


def _invoke_spell_target_with_overrides(
        *,
        spell: Any,
        keyword_overrides: Dict[str, Any],
        positional_overrides: Optional[Sequence[Any]],
) -> Any:
    """
    Invoke the solo root call target with root-only override payloads.
    """
    call_target = spell.spell
    if positional_overrides is not None:
        if keyword_overrides:
            return call_target(*positional_overrides, **keyword_overrides)
        return call_target(*positional_overrides)
    if keyword_overrides:
        return call_target(**keyword_overrides)
    return call_target()


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
