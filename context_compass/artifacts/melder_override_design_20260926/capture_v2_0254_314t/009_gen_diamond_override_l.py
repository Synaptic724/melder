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
        spell_id_0 = step_spell_ids[0]
        has_disposal_methods_0 = step_has_disposal_methods[0]
        disposal_methods_0 = step_disposal_methods[0]
        has_targeted_overrides_0 = step_has_targeted_overrides[0]
        override_targets_0 = step_override_targets[0]
        creations_0 = meld._conduit_creations
        instance_0 = _get_existing_creation(spell=spell_0, creations=creations_0, existence=plan_step_0.existence)
        if instance_0 is not None:
            _raise_override_on_existing_instance(spell=spell_0, has_targeted_overrides=has_targeted_overrides_0, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with (creations_0._slot_guards.get(spell_id_0) or creations_0.slot_guard(spell_id_0)):
                instance_0 = _get_existing_creation(spell=spell_0, creations=creations_0, existence=plan_step_0.existence)
                if instance_0 is not None:
                    _raise_override_on_existing_instance(spell=spell_0, has_targeted_overrides=has_targeted_overrides_0, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    try:
                        instance_0 = plan_step_0.spell.spell()
                    except Exception as exc:
                        _raise_meld_construction_error(plan_step_0.spell, exc)
                    _register_spell_instance_prebound(spell_id=spell_id_0, instance=instance_0, creations=creations_0, existence=plan_step_0.existence, has_disposal_methods=has_disposal_methods_0, disposal_methods=disposal_methods_0)
        instance_results[step_instance_keys[0]] = instance_0
        plan_step_1 = steps[1]
        spell_1 = step_spells[1]
        creations_1 = meld._spellspace_creations
        if creations_1 is None:
            creations_1 = meld._conduit_creations
        kwargs_1 = {}
        try:
            kwargs_1['s'] = instance_results[('02c4873fd1cec8da098d21ed0c29806a090efd5189458c91b34767000d4fb8f5', None)]
        except KeyError as exc:
            raise MeldExecutionError(
                spell_id=spell_id_1,
                spell_name=spell_id_1,
                node_id=spell_id_1,
                param_name='s',
                message=("Dependency " + '02c4873fd1cec8da098d21ed0c29806a090efd5189458c91b34767000d4fb8f5' + " missing while building args for '" + spell_id_1 + "'."),
            ) from exc
        try:
            instance_1 = plan_step_1.spell.spell(**kwargs_1)
        except Exception as exc:
            _raise_meld_construction_error(plan_step_1.spell, exc, kwargs_1)
        instance_results[step_instance_keys[1]] = instance_1
        plan_step_2 = steps[2]
        spell_2 = step_spells[2]
        creations_2 = meld._spellspace_creations
        if creations_2 is None:
            creations_2 = meld._conduit_creations
        kwargs_2 = {}
        try:
            kwargs_2['s'] = instance_results[('02c4873fd1cec8da098d21ed0c29806a090efd5189458c91b34767000d4fb8f5', None)]
        except KeyError as exc:
            raise MeldExecutionError(
                spell_id=spell_id_2,
                spell_name=spell_id_2,
                node_id=spell_id_2,
                param_name='s',
                message=("Dependency " + '02c4873fd1cec8da098d21ed0c29806a090efd5189458c91b34767000d4fb8f5' + " missing while building args for '" + spell_id_2 + "'."),
            ) from exc
        try:
            instance_2 = plan_step_2.spell.spell(**kwargs_2)
        except Exception as exc:
            _raise_meld_construction_error(plan_step_2.spell, exc, kwargs_2)
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
        if single_override_socket_3.param_name != 'l':
            try:
                kwargs_3['l'] = instance_results[('d846125bb6fc6940bf775bb09e18462e16585ccf44454a3b12a1a127334fe4c0', 1)]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id_3,
                    spell_name=spell_id_3,
                    node_id=spell_id_3,
                    param_name='l',
                    message=("Dependency " + 'd846125bb6fc6940bf775bb09e18462e16585ccf44454a3b12a1a127334fe4c0' + " missing while building args for '" + spell_id_3 + "'."),
                ) from exc
        if single_override_socket_3.param_name != 'r':
            try:
                kwargs_3['r'] = instance_results[('186b3b7b71a74e6ba96dd386d80e63c016c51ebfe0ac254849b78fdc91279cd1', 2)]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id_3,
                    spell_name=spell_id_3,
                    node_id=spell_id_3,
                    param_name='r',
                    message=("Dependency " + '186b3b7b71a74e6ba96dd386d80e63c016c51ebfe0ac254849b78fdc91279cd1' + " missing while building args for '" + spell_id_3 + "'."),
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
