def __melder_executor_factory__(bindings):
    root_instance_key = bindings['root_instance_key']
    step_contract_values = bindings['step_contract_values']
    step_dep_keys = bindings['step_dep_keys']
    step_disposal_methods = bindings['step_disposal_methods']
    step_existences = bindings['step_existences']
    step_instance_keys = bindings['step_instance_keys']
    step_owner_creations = bindings['step_owner_creations']
    step_positional_args = bindings['step_positional_args']
    step_spell_ids = bindings['step_spell_ids']
    step_spells = bindings['step_spells']
    step_targets = bindings['step_targets']
    steps = bindings['steps']
    target_0 = step_targets[0]
    spell_0 = step_spells[0]
    spell_id_0 = step_spell_ids[0]
    target_1 = step_targets[1]
    spell_1 = step_spells[1]
    target_2 = step_targets[2]
    spell_2 = step_spells[2]
    target_3 = step_targets[3]
    spell_3 = step_spells[3]
    def _no_overrides_codegen_creation_executor(meld):
        creations_0 = meld._conduit_creations
        instance_0 = creations_0._creations.get(spell_id_0)
        if instance_0 is None:
            with (creations_0._slot_guards.get(spell_id_0) or creations_0.slot_guard(spell_id_0)):
                instance_0 = creations_0._creations.get(spell_id_0)
                if instance_0 is None:
                    try:
                        instance_0 = target_0()
                    except Exception as exc:
                        _raise_meld_construction_error(spell_0, exc)
                    creations_0._creations[spell_id_0] = instance_0
        try:
            instance_1 = target_1(
                s=instance_0,
            )
        except Exception as exc:
            _raise_meld_construction_error(spell_1, exc)
        try:
            instance_2 = target_2(
                s=instance_0,
            )
        except Exception as exc:
            _raise_meld_construction_error(spell_2, exc)
        try:
            instance_3 = target_3(
                l=instance_2,
                r=instance_1,
            )
        except Exception as exc:
            _raise_meld_construction_error(spell_3, exc)
        return instance_3
    return _no_overrides_codegen_creation_executor
