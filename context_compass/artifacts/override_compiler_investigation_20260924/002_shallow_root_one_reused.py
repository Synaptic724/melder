def _overrides_codegen_creation_executor(
        meld,
        override_map,
        root_positional_override,
        *,
        steps=steps,
        step_spells=step_spells,
        step_spell_ids=step_spell_ids,
        step_has_disposal_methods=step_has_disposal_methods,
        step_disposal_methods=step_disposal_methods,
        step_override_targets=step_override_targets,
        step_has_targeted_overrides=step_has_targeted_overrides,
        step_override_target_counts=step_override_target_counts,
        step_is_existing_unique_creation=step_is_existing_unique_creation,
        step_is_callable_spell=step_is_callable_spell,
        step_instance_keys=step_instance_keys,
        root_instance_key=root_instance_key,
        root_spell_id=root_spell_id,
        any_overrides_present=any_overrides_present,
        _EMPTY_OVERRIDE_VALUES=_EMPTY_OVERRIDE_VALUES,
        _MISSING=_MISSING,
        _get_existing_creation=_get_existing_creation,
        _register_spell_instance_prebound=_register_spell_instance_prebound,
        _raise_override_on_existing_instance=_raise_override_on_existing_instance,
        Sequence=Sequence,
        MeldExecutionError=MeldExecutionError,
    ):
    instance_results = {}
    plan_step_0 = steps[0]
    spell_0 = step_spells[0]
    creations_0 = meld._spellspace_creations
    if creations_0 is None:
        creations_0 = meld._conduit_creations
    try:
        instance_0 = plan_step_0.spell.spell()
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=plan_step_0.spell.spell_index.selected_spell_id,
            spell_name=plan_step_0.spell.spell_name,
            message=("Error invoking spell '" + plan_step_0.spell.spell_name + "'."),
            inner=exc,
        ) from exc
    instance_results[step_instance_keys[0]] = instance_0
    plan_step_1 = steps[1]
    spell_1 = step_spells[1]
    creations_1 = meld._spellspace_creations
    if creations_1 is None:
        creations_1 = meld._conduit_creations
    try:
        instance_1 = plan_step_1.spell.spell()
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=plan_step_1.spell.spell_index.selected_spell_id,
            spell_name=plan_step_1.spell.spell_name,
            message=("Error invoking spell '" + plan_step_1.spell.spell_name + "'."),
            inner=exc,
        ) from exc
    instance_results[step_instance_keys[1]] = instance_1
    plan_step_2 = steps[2]
    spell_2 = step_spells[2]
    override_targets_2 = step_override_targets[2]
    creations_2 = meld._spellspace_creations
    if creations_2 is None:
        creations_2 = meld._conduit_creations
    single_override_socket_2 = override_targets_2[0]
    single_override_value_2 = override_map[single_override_socket_2]
    kwargs_2 = {}
    if single_override_socket_2.param_name != 'a':
        try:
            kwargs_2['a'] = instance_results[('7411d94f69dc39fe1302f2e06ca31412fa5d94db5b2453d7274cb4eb751fc361', 1)]
        except KeyError as exc:
            raise MeldExecutionError(
                spell_id=spell_id_2,
                spell_name=spell_id_2,
                node_id=spell_id_2,
                param_name='a',
                message=("Dependency " + '7411d94f69dc39fe1302f2e06ca31412fa5d94db5b2453d7274cb4eb751fc361' + " missing while building args for '" + spell_id_2 + "'."),
            ) from exc
    if single_override_socket_2.param_name != 'b':
        try:
            kwargs_2['b'] = instance_results[('ffe04a5ff92a37b4b4cad14f356f042089e20cae757acd46ff3e3ff79b73cbee', 2)]
        except KeyError as exc:
            raise MeldExecutionError(
                spell_id=spell_id_2,
                spell_name=spell_id_2,
                node_id=spell_id_2,
                param_name='b',
                message=("Dependency " + 'ffe04a5ff92a37b4b4cad14f356f042089e20cae757acd46ff3e3ff79b73cbee' + " missing while building args for '" + spell_id_2 + "'."),
            ) from exc
    kwargs_2[single_override_socket_2.param_name] = single_override_value_2
    try:
        instance_2 = plan_step_2.spell.spell(**kwargs_2)
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=plan_step_2.spell.spell_index.selected_spell_id,
            spell_name=plan_step_2.spell.spell_name,
            message=("Error invoking spell '" + plan_step_2.spell.spell_name + "'."),
            inner=exc,
        ) from exc
    instance_results[step_instance_keys[2]] = instance_2
    if root_instance_key not in instance_results:
        raise MeldExecutionError(
            spell_id=root_instance_key[0],
            spell_name=root_instance_key[0],
            message=(
                "Overrides codegen creation executor did not produce the root "
                f"instance '{root_instance_key[0]}'."
            ),
        )
    return instance_results[root_instance_key]
