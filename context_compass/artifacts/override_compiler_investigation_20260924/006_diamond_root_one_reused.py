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
    creations_2 = meld._spellspace_creations
    if creations_2 is None:
        creations_2 = meld._conduit_creations
    kwargs_2 = {}
    try:
        kwargs_2['leaf'] = instance_results[('2dcf16c444f1a46881ed2408f67e886f3992061cc04cf5fafc9e47804a8e9ae8', 4)]
    except KeyError as exc:
        raise MeldExecutionError(
            spell_id=spell_id_2,
            spell_name=spell_id_2,
            node_id=spell_id_2,
            param_name='leaf',
            message=("Dependency " + '2dcf16c444f1a46881ed2408f67e886f3992061cc04cf5fafc9e47804a8e9ae8' + " missing while building args for '" + spell_id_2 + "'."),
        ) from exc
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
    plan_step_3 = steps[3]
    spell_3 = step_spells[3]
    creations_3 = meld._spellspace_creations
    if creations_3 is None:
        creations_3 = meld._conduit_creations
    kwargs_3 = {}
    try:
        kwargs_3['leaf'] = instance_results[('2dcf16c444f1a46881ed2408f67e886f3992061cc04cf5fafc9e47804a8e9ae8', 3)]
    except KeyError as exc:
        raise MeldExecutionError(
            spell_id=spell_id_3,
            spell_name=spell_id_3,
            node_id=spell_id_3,
            param_name='leaf',
            message=("Dependency " + '2dcf16c444f1a46881ed2408f67e886f3992061cc04cf5fafc9e47804a8e9ae8' + " missing while building args for '" + spell_id_3 + "'."),
        ) from exc
    try:
        instance_3 = plan_step_3.spell.spell(**kwargs_3)
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=plan_step_3.spell.spell_index.selected_spell_id,
            spell_name=plan_step_3.spell.spell_name,
            message=("Error invoking spell '" + plan_step_3.spell.spell_name + "'."),
            inner=exc,
        ) from exc
    instance_results[step_instance_keys[3]] = instance_3
    plan_step_4 = steps[4]
    spell_4 = step_spells[4]
    override_targets_4 = step_override_targets[4]
    creations_4 = meld._spellspace_creations
    if creations_4 is None:
        creations_4 = meld._conduit_creations
    single_override_socket_4 = override_targets_4[0]
    single_override_value_4 = override_map[single_override_socket_4]
    kwargs_4 = {}
    if single_override_socket_4.param_name != 'left':
        try:
            kwargs_4['left'] = instance_results[('33c98225ce6391f724ed4e28e9b20411d8f9334a38be968e2a269a20d325d09b', 1)]
        except KeyError as exc:
            raise MeldExecutionError(
                spell_id=spell_id_4,
                spell_name=spell_id_4,
                node_id=spell_id_4,
                param_name='left',
                message=("Dependency " + '33c98225ce6391f724ed4e28e9b20411d8f9334a38be968e2a269a20d325d09b' + " missing while building args for '" + spell_id_4 + "'."),
            ) from exc
    if single_override_socket_4.param_name != 'right':
        try:
            kwargs_4['right'] = instance_results[('15971b934fe49fb823e0c678e24a168df12c35fe4478670068d3e1a01a96d27b', 2)]
        except KeyError as exc:
            raise MeldExecutionError(
                spell_id=spell_id_4,
                spell_name=spell_id_4,
                node_id=spell_id_4,
                param_name='right',
                message=("Dependency " + '15971b934fe49fb823e0c678e24a168df12c35fe4478670068d3e1a01a96d27b' + " missing while building args for '" + spell_id_4 + "'."),
            ) from exc
    kwargs_4[single_override_socket_4.param_name] = single_override_value_4
    try:
        instance_4 = plan_step_4.spell.spell(**kwargs_4)
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=plan_step_4.spell.spell_index.selected_spell_id,
            spell_name=plan_step_4.spell.spell_name,
            message=("Error invoking spell '" + plan_step_4.spell.spell_name + "'."),
            inner=exc,
        ) from exc
    instance_results[step_instance_keys[4]] = instance_4
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
