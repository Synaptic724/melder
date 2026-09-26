def __melder_executor_factory__(bindings):
    any_overrides_present = bindings['any_overrides_present']
    root_instance_key = bindings['root_instance_key']
    root_spell_id = bindings['root_spell_id']
    step_creations_target_kinds = bindings['step_creations_target_kinds']
    step_disposal_methods = bindings['step_disposal_methods']
    step_existences = bindings['step_existences']
    step_has_disposal_methods = bindings['step_has_disposal_methods']
    step_has_targeted_overrides = bindings['step_has_targeted_overrides']
    step_instance_keys = bindings['step_instance_keys']
    step_is_callable_spell = bindings['step_is_callable_spell']
    step_is_existing_unique_creation = bindings['step_is_existing_unique_creation']
    step_is_root = bindings['step_is_root']
    step_must_register_flags = bindings['step_must_register_flags']
    step_override_target_counts = bindings['step_override_target_counts']
    step_override_targets = bindings['step_override_targets']
    step_spell_ids = bindings['step_spell_ids']
    step_spells = bindings['step_spells']
    step_use_spell_lock_hints = bindings['step_use_spell_lock_hints']
    steps = bindings['steps']
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
            _raise_meld_construction_error(plan_step_0.spell, exc)
        instance_results[step_instance_keys[0]] = instance_0
        plan_step_1 = steps[1]
        spell_1 = step_spells[1]
        creations_1 = meld._spellspace_creations
        if creations_1 is None:
            creations_1 = meld._conduit_creations
        try:
            instance_1 = plan_step_1.spell.spell()
        except Exception as exc:
            _raise_meld_construction_error(plan_step_1.spell, exc)
        instance_results[step_instance_keys[1]] = instance_1
        plan_step_2 = steps[2]
        spell_2 = step_spells[2]
        spell_id_2 = step_spell_ids[2]
        has_disposal_methods_2 = step_has_disposal_methods[2]
        disposal_methods_2 = step_disposal_methods[2]
        has_targeted_overrides_2 = step_has_targeted_overrides[2]
        override_targets_2 = step_override_targets[2]
        creations_2 = meld._conduit_creations
        instance_2 = _get_existing_creation(spell=spell_2, creations=creations_2, existence=plan_step_2.existence)
        if instance_2 is not None:
            _raise_override_on_existing_instance(spell=spell_2, has_targeted_overrides=has_targeted_overrides_2, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with (creations_2._slot_guards.get(spell_id_2) or creations_2.slot_guard(spell_id_2)):
                instance_2 = _get_existing_creation(spell=spell_2, creations=creations_2, existence=plan_step_2.existence)
                if instance_2 is not None:
                    _raise_override_on_existing_instance(spell=spell_2, has_targeted_overrides=has_targeted_overrides_2, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    kwargs_2 = {}
                    try:
                        kwargs_2['x'] = instance_results[('717d2a681100681147188b4e7bc3c533439f63afe2e064aca445fcd5aa385876', 3)]
                    except KeyError as exc:
                        raise MeldExecutionError(
                            spell_id=spell_id_2,
                            spell_name=spell_id_2,
                            node_id=spell_id_2,
                            param_name='x',
                            message=("Dependency " + '717d2a681100681147188b4e7bc3c533439f63afe2e064aca445fcd5aa385876' + " missing while building args for '" + spell_id_2 + "'."),
                        ) from exc
                    try:
                        instance_2 = plan_step_2.spell.spell(**kwargs_2)
                    except Exception as exc:
                        _raise_meld_construction_error(plan_step_2.spell, exc, kwargs_2)
                    _register_spell_instance_prebound(spell_id=spell_id_2, instance=instance_2, creations=creations_2, existence=plan_step_2.existence, has_disposal_methods=has_disposal_methods_2, disposal_methods=disposal_methods_2)
        instance_results[step_instance_keys[2]] = instance_2
        plan_step_3 = steps[3]
        spell_3 = step_spells[3]
        override_targets_3 = step_override_targets[3]
        creations_3 = meld._spellspace_creations
        if creations_3 is None:
            creations_3 = meld._conduit_creations
        single_override_socket_3 = override_targets_3[0]
        single_override_value_3 = override_map[single_override_socket_3]
        kwargs_3 = {}
        if single_override_socket_3.param_name != 'a':
            try:
                kwargs_3['a'] = instance_results[('bed3e05909dbd9a2bf6894136ca08976141690041661ffe07f1e610acd39c723', 1)]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id_3,
                    spell_name=spell_id_3,
                    node_id=spell_id_3,
                    param_name='a',
                    message=("Dependency " + 'bed3e05909dbd9a2bf6894136ca08976141690041661ffe07f1e610acd39c723' + " missing while building args for '" + spell_id_3 + "'."),
                ) from exc
        if single_override_socket_3.param_name != 's':
            try:
                kwargs_3['s'] = instance_results[('fc042808e2f14bf98232bef8b300d45c4ebe468b43ad9053129388f51b1726b7', None)]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id_3,
                    spell_name=spell_id_3,
                    node_id=spell_id_3,
                    param_name='s',
                    message=("Dependency " + 'fc042808e2f14bf98232bef8b300d45c4ebe468b43ad9053129388f51b1726b7' + " missing while building args for '" + spell_id_3 + "'."),
                ) from exc
        kwargs_3[single_override_socket_3.param_name] = single_override_value_3
        try:
            instance_3 = plan_step_3.spell.spell(**kwargs_3)
        except Exception as exc:
            _raise_meld_construction_error(plan_step_3.spell, exc, kwargs_3)
        instance_results[step_instance_keys[3]] = instance_3
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
    return _overrides_codegen_creation_executor
