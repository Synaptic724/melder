from typing import Any, Callable, Dict, Optional, Sequence, Tuple


def compile_solo_overrides_codegen_creation_executor(
        *,
        spell: Any,
        solo_emit_key: str,
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
        - Specializes route and disposal posture at compile time so hot calls
          do not keep paying generic route and registration helper dispatch.
    """
    call_target = spell.spell
    spell_id = spell.spell_id
    has_disposal_methods = spell.has_disposal_methods
    disposal_methods = _normalize_disposal_methods(
        spell.disposal_method_names
    )

    if solo_emit_key == "many":
        if has_disposal_methods:
            def execute_many_with_disposal(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                caller_creations.add_many_creations(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_many_with_disposal

        def execute_many_no_disposal(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> Any:
            return _invoke_with_overrides(
                call_target=call_target,
                overrides=overrides,
            )

        return execute_many_no_disposal

    if solo_emit_key == "unique_per_conduit":
        if has_disposal_methods:
            def execute_unique_per_conduit_with_disposal(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                caller_creations.add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_unique_per_conduit_with_disposal

        def execute_unique_per_conduit(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = _invoke_with_overrides(
                call_target=call_target,
                overrides=overrides,
            )
            caller_creations.add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_unique_per_conduit

    if solo_emit_key == "unique_per_spell_space":
        if has_disposal_methods:
            def execute_unique_per_spell_space_with_disposal(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                caller_creations.add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_unique_per_spell_space_with_disposal

        def execute_unique_per_spell_space(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = _invoke_with_overrides(
                call_target=call_target,
                overrides=overrides,
            )
            caller_creations.add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_unique_per_spell_space

    if solo_emit_key == "existing_creation":
        def execute_existing_creation(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
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

    if solo_emit_key == "unique":
        prebound_owner_creations = spell._owner_creations
        if prebound_owner_creations is not None:
            if has_disposal_methods:
                def execute_unique_prebound_with_disposal(
                        caller_creations: Any,
                        overrides: Optional[Dict[str, Any]],
                        caller_creations_lock_held: bool = False,
                ) -> Any:
                    instance = _invoke_with_overrides(
                        call_target=call_target,
                        overrides=overrides,
                    )
                    prebound_owner_creations.add_creation(
                        spell_id,
                        instance,
                        has_disposal_methods=True,
                        disposal_methods=disposal_methods,
                    )
                    return instance

                return execute_unique_prebound_with_disposal

            def execute_unique_prebound(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                prebound_owner_creations.add_creation(
                    spell_id,
                    instance,
                )
                return instance

            return execute_unique_prebound

        if has_disposal_methods:
            def execute_unique_dynamic_with_disposal(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                dynamic_owner_creations = spell._owner_creations
                dynamic_owner_creations.add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_unique_dynamic_with_disposal

        def execute_unique_dynamic(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = _invoke_with_overrides(
                call_target=call_target,
                overrides=overrides,
            )
            dynamic_owner_creations = spell._owner_creations
            dynamic_owner_creations.add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_unique_dynamic

    if solo_emit_key == "unique_per_conduit_cluster":
        prebound_owner_creations = spell._owner_creations
        if prebound_owner_creations is not None:
            if has_disposal_methods:
                def execute_cluster_prebound_with_disposal(
                        caller_creations: Any,
                        overrides: Optional[Dict[str, Any]],
                        caller_creations_lock_held: bool = False,
                ) -> Any:
                    instance = _invoke_with_overrides(
                        call_target=call_target,
                        overrides=overrides,
                    )
                    prebound_owner_creations.add_creation(
                        spell_id,
                        instance,
                        has_disposal_methods=True,
                        disposal_methods=disposal_methods,
                    )
                    return instance

                return execute_cluster_prebound_with_disposal

            def execute_cluster_prebound(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                prebound_owner_creations.add_creation(
                    spell_id,
                    instance,
                )
                return instance

            return execute_cluster_prebound

        if has_disposal_methods:
            def execute_cluster_dynamic_with_disposal(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                dynamic_owner_creations = spell._owner_creations
                dynamic_owner_creations.add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_cluster_dynamic_with_disposal

        def execute_cluster_dynamic(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = _invoke_with_overrides(
                call_target=call_target,
                overrides=overrides,
            )
            dynamic_owner_creations = spell._owner_creations
            dynamic_owner_creations.add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_cluster_dynamic

    if solo_emit_key == "unique_per_conduit_lineage":
        prebound_owner_creations = spell._owner_creations
        if prebound_owner_creations is not None:
            if has_disposal_methods:
                def execute_lineage_prebound_with_disposal(
                        caller_creations: Any,
                        overrides: Optional[Dict[str, Any]],
                        caller_creations_lock_held: bool = False,
                ) -> Any:
                    instance = _invoke_with_overrides(
                        call_target=call_target,
                        overrides=overrides,
                    )
                    prebound_owner_creations.add_creation(
                        spell_id,
                        instance,
                        has_disposal_methods=True,
                        disposal_methods=disposal_methods,
                    )
                    return instance

                return execute_lineage_prebound_with_disposal

            def execute_lineage_prebound(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                prebound_owner_creations.add_creation(
                    spell_id,
                    instance,
                )
                return instance

            return execute_lineage_prebound

        if has_disposal_methods:
            def execute_lineage_dynamic_with_disposal(
                    caller_creations: Any,
                    overrides: Optional[Dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                instance = _invoke_with_overrides(
                    call_target=call_target,
                    overrides=overrides,
                )
                dynamic_owner_creations = spell._owner_creations
                dynamic_owner_creations.add_creation(
                    spell_id,
                    instance,
                    has_disposal_methods=True,
                    disposal_methods=disposal_methods,
                )
                return instance

            return execute_lineage_dynamic_with_disposal

        def execute_lineage_dynamic(
                caller_creations: Any,
                overrides: Optional[Dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> Any:
            instance = _invoke_with_overrides(
                call_target=call_target,
                overrides=overrides,
            )
            dynamic_owner_creations = spell._owner_creations
            dynamic_owner_creations.add_creation(
                spell_id,
                instance,
            )
            return instance

        return execute_lineage_dynamic

    raise RuntimeError(
        f"Unsupported solo overrides emit key: {solo_emit_key}"
    )


def _invoke_with_overrides(
        *,
        call_target: Any,
        overrides: Optional[Dict[str, Any]],
) -> Any:
    """
    Invoke the solo root call target with root-only override payloads.
    """
    if not overrides:
        return call_target()

    raw_args = overrides.get("__args__")
    if raw_args is None:
        return call_target(**overrides)

    if isinstance(raw_args, tuple):
        positional_overrides = raw_args
    elif isinstance(raw_args, list):
        positional_overrides = tuple(raw_args)
    else:
        raise RuntimeError("__args__ override must be a list or tuple.")

    if len(overrides) == 1:
        return call_target(*positional_overrides)

    keyword_overrides: Dict[str, Any] = {}
    for param_name, value in overrides.items():
        if param_name == "__args__":
            continue
        keyword_overrides[param_name] = value
    return call_target(*positional_overrides, **keyword_overrides)


def _normalize_disposal_methods(
        disposal_method_names: Sequence[str],
) -> Optional[Tuple[str, ...]]:
    """
    Normalize spell-owned disposal metadata for creations registration.
    """
    if not disposal_method_names:
        return None
    return tuple(disposal_method_names)
