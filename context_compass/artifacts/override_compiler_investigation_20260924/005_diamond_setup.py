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
        step_existences=step_existences,
        step_creations_target_kinds=step_creations_target_kinds,
        step_is_root=step_is_root,
        step_has_targeted_overrides=step_has_targeted_overrides,
        step_instance_keys=step_instance_keys,
        step_use_spell_lock_hints=step_use_spell_lock_hints,
        step_must_register_flags=step_must_register_flags,
        root_instance_key=root_instance_key,
        root_spell_id=root_spell_id,
        any_overrides_present=any_overrides_present,
        Existence=Existence,
        ManyOnlyCodegenPlanTargetKind=ManyOnlyCodegenPlanTargetKind,
        _construct_spell_instance_with_overrides=_construct_spell_instance_with_overrides,
        _get_existing_creation=_get_existing_creation,
        _register_spell_instance_prebound=_register_spell_instance_prebound,
        _raise_override_on_existing_instance=_raise_override_on_existing_instance,
        MeldExecutionError=MeldExecutionError,
    ):
    instance_results = {}
    plan_step_0 = steps[0]
    spell_0 = step_spells[0]
    spell_id_0 = step_spell_ids[0]
    has_disposal_methods_0 = step_has_disposal_methods[0]
    disposal_methods_0 = step_disposal_methods[0]
    existence_0 = step_existences[0]
    if existence_0 is Existence.many:
        creations_0 = meld._spellspace_creations
        if creations_0 is None:
            creations_0 = meld._conduit_creations
    elif existence_0 is Existence.unique_per_conduit:
        creations_0 = meld._conduit_creations
    elif existence_0 is Existence.unique_per_spell_space:
        creations_0 = meld._spellspace_creations
    elif existence_0 is Existence.unique_per_conduit_lineage:
        creations_0 = meld._root_creations
    elif existence_0 is Existence.unique_per_conduit_cluster:
        creations_0 = meld._cluster_creations.resolved_store()
    elif existence_0 is Existence.unique:
        creations_0 = spell_0._owner_creations
    else:
        raise RuntimeError(f"Unsupported existence '{existence_0}' for spell '{spell_0.spell_id}'.")
    override_targets_0 = step_override_targets[0]
    has_targeted_overrides_0 = step_has_targeted_overrides[0]
    is_root_step_0 = step_is_root[0]
    step_root_positional_override_0 = root_positional_override if is_root_step_0 else None
    must_register_0 = step_must_register_flags[0]
    if existence_0 is Existence.many:
        instance_0 = _construct_spell_instance_with_overrides(plan_step=plan_step_0, instance_results=instance_results, override_targets=override_targets_0, override_map=override_map, root_positional_override=step_root_positional_override_0)
        if must_register_0:
            with creations_0._lock:
                _register_spell_instance_prebound(spell_id=spell_id_0, instance=instance_0, creations=creations_0, existence=existence_0, has_disposal_methods=has_disposal_methods_0, disposal_methods=disposal_methods_0)
    elif existence_0 in (Existence.unique_per_conduit, Existence.unique_per_spell_space):
        instance_0 = _get_existing_creation(spell=spell_0, creations=creations_0, existence=existence_0)
        if instance_0 is not None:
            _raise_override_on_existing_instance(spell=spell_0, has_targeted_overrides=has_targeted_overrides_0, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with creations_0._lock:
                instance_0 = _get_existing_creation(spell=spell_0, creations=creations_0, existence=existence_0)
                if instance_0 is not None:
                    _raise_override_on_existing_instance(spell=spell_0, has_targeted_overrides=has_targeted_overrides_0, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_0 = _construct_spell_instance_with_overrides(plan_step=plan_step_0, instance_results=instance_results, override_targets=override_targets_0, override_map=override_map, root_positional_override=step_root_positional_override_0)
                    _register_spell_instance_prebound(spell_id=spell_id_0, instance=instance_0, creations=creations_0, existence=existence_0, has_disposal_methods=has_disposal_methods_0, disposal_methods=disposal_methods_0)
    else:
        use_spell_lock_0 = step_use_spell_lock_hints[0]
        if use_spell_lock_0:
            with spell_0._lock:
                with creations_0._lock:
                    instance_0 = _get_existing_creation(spell=spell_0, creations=creations_0, existence=existence_0)
                if instance_0 is not None:
                    _raise_override_on_existing_instance(spell=spell_0, has_targeted_overrides=has_targeted_overrides_0, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_0 = _construct_spell_instance_with_overrides(plan_step=plan_step_0, instance_results=instance_results, override_targets=override_targets_0, override_map=override_map, root_positional_override=step_root_positional_override_0)
                    with creations_0._lock:
                        _register_spell_instance_prebound(spell_id=spell_id_0, instance=instance_0, creations=creations_0, existence=existence_0, has_disposal_methods=has_disposal_methods_0, disposal_methods=disposal_methods_0)
        else:
            with creations_0._lock:
                instance_0 = _get_existing_creation(spell=spell_0, creations=creations_0, existence=existence_0)
                if instance_0 is not None:
                    _raise_override_on_existing_instance(spell=spell_0, has_targeted_overrides=has_targeted_overrides_0, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_0 = _construct_spell_instance_with_overrides(plan_step=plan_step_0, instance_results=instance_results, override_targets=override_targets_0, override_map=override_map, root_positional_override=step_root_positional_override_0)
                    _register_spell_instance_prebound(spell_id=spell_id_0, instance=instance_0, creations=creations_0, existence=existence_0, has_disposal_methods=has_disposal_methods_0, disposal_methods=disposal_methods_0)
    instance_results[step_instance_keys[0]] = instance_0
    plan_step_1 = steps[1]
    spell_1 = step_spells[1]
    spell_id_1 = step_spell_ids[1]
    has_disposal_methods_1 = step_has_disposal_methods[1]
    disposal_methods_1 = step_disposal_methods[1]
    existence_1 = step_existences[1]
    if existence_1 is Existence.many:
        creations_1 = meld._spellspace_creations
        if creations_1 is None:
            creations_1 = meld._conduit_creations
    elif existence_1 is Existence.unique_per_conduit:
        creations_1 = meld._conduit_creations
    elif existence_1 is Existence.unique_per_spell_space:
        creations_1 = meld._spellspace_creations
    elif existence_1 is Existence.unique_per_conduit_lineage:
        creations_1 = meld._root_creations
    elif existence_1 is Existence.unique_per_conduit_cluster:
        creations_1 = meld._cluster_creations.resolved_store()
    elif existence_1 is Existence.unique:
        creations_1 = spell_1._owner_creations
    else:
        raise RuntimeError(f"Unsupported existence '{existence_1}' for spell '{spell_1.spell_id}'.")
    override_targets_1 = step_override_targets[1]
    has_targeted_overrides_1 = step_has_targeted_overrides[1]
    is_root_step_1 = step_is_root[1]
    step_root_positional_override_1 = root_positional_override if is_root_step_1 else None
    must_register_1 = step_must_register_flags[1]
    if existence_1 is Existence.many:
        instance_1 = _construct_spell_instance_with_overrides(plan_step=plan_step_1, instance_results=instance_results, override_targets=override_targets_1, override_map=override_map, root_positional_override=step_root_positional_override_1)
        if must_register_1:
            with creations_1._lock:
                _register_spell_instance_prebound(spell_id=spell_id_1, instance=instance_1, creations=creations_1, existence=existence_1, has_disposal_methods=has_disposal_methods_1, disposal_methods=disposal_methods_1)
    elif existence_1 in (Existence.unique_per_conduit, Existence.unique_per_spell_space):
        instance_1 = _get_existing_creation(spell=spell_1, creations=creations_1, existence=existence_1)
        if instance_1 is not None:
            _raise_override_on_existing_instance(spell=spell_1, has_targeted_overrides=has_targeted_overrides_1, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with creations_1._lock:
                instance_1 = _get_existing_creation(spell=spell_1, creations=creations_1, existence=existence_1)
                if instance_1 is not None:
                    _raise_override_on_existing_instance(spell=spell_1, has_targeted_overrides=has_targeted_overrides_1, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_1 = _construct_spell_instance_with_overrides(plan_step=plan_step_1, instance_results=instance_results, override_targets=override_targets_1, override_map=override_map, root_positional_override=step_root_positional_override_1)
                    _register_spell_instance_prebound(spell_id=spell_id_1, instance=instance_1, creations=creations_1, existence=existence_1, has_disposal_methods=has_disposal_methods_1, disposal_methods=disposal_methods_1)
    else:
        use_spell_lock_1 = step_use_spell_lock_hints[1]
        if use_spell_lock_1:
            with spell_1._lock:
                with creations_1._lock:
                    instance_1 = _get_existing_creation(spell=spell_1, creations=creations_1, existence=existence_1)
                if instance_1 is not None:
                    _raise_override_on_existing_instance(spell=spell_1, has_targeted_overrides=has_targeted_overrides_1, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_1 = _construct_spell_instance_with_overrides(plan_step=plan_step_1, instance_results=instance_results, override_targets=override_targets_1, override_map=override_map, root_positional_override=step_root_positional_override_1)
                    with creations_1._lock:
                        _register_spell_instance_prebound(spell_id=spell_id_1, instance=instance_1, creations=creations_1, existence=existence_1, has_disposal_methods=has_disposal_methods_1, disposal_methods=disposal_methods_1)
        else:
            with creations_1._lock:
                instance_1 = _get_existing_creation(spell=spell_1, creations=creations_1, existence=existence_1)
                if instance_1 is not None:
                    _raise_override_on_existing_instance(spell=spell_1, has_targeted_overrides=has_targeted_overrides_1, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_1 = _construct_spell_instance_with_overrides(plan_step=plan_step_1, instance_results=instance_results, override_targets=override_targets_1, override_map=override_map, root_positional_override=step_root_positional_override_1)
                    _register_spell_instance_prebound(spell_id=spell_id_1, instance=instance_1, creations=creations_1, existence=existence_1, has_disposal_methods=has_disposal_methods_1, disposal_methods=disposal_methods_1)
    instance_results[step_instance_keys[1]] = instance_1
    plan_step_2 = steps[2]
    spell_2 = step_spells[2]
    spell_id_2 = step_spell_ids[2]
    has_disposal_methods_2 = step_has_disposal_methods[2]
    disposal_methods_2 = step_disposal_methods[2]
    existence_2 = step_existences[2]
    if existence_2 is Existence.many:
        creations_2 = meld._spellspace_creations
        if creations_2 is None:
            creations_2 = meld._conduit_creations
    elif existence_2 is Existence.unique_per_conduit:
        creations_2 = meld._conduit_creations
    elif existence_2 is Existence.unique_per_spell_space:
        creations_2 = meld._spellspace_creations
    elif existence_2 is Existence.unique_per_conduit_lineage:
        creations_2 = meld._root_creations
    elif existence_2 is Existence.unique_per_conduit_cluster:
        creations_2 = meld._cluster_creations.resolved_store()
    elif existence_2 is Existence.unique:
        creations_2 = spell_2._owner_creations
    else:
        raise RuntimeError(f"Unsupported existence '{existence_2}' for spell '{spell_2.spell_id}'.")
    override_targets_2 = step_override_targets[2]
    has_targeted_overrides_2 = step_has_targeted_overrides[2]
    is_root_step_2 = step_is_root[2]
    step_root_positional_override_2 = root_positional_override if is_root_step_2 else None
    must_register_2 = step_must_register_flags[2]
    if existence_2 is Existence.many:
        instance_2 = _construct_spell_instance_with_overrides(plan_step=plan_step_2, instance_results=instance_results, override_targets=override_targets_2, override_map=override_map, root_positional_override=step_root_positional_override_2)
        if must_register_2:
            with creations_2._lock:
                _register_spell_instance_prebound(spell_id=spell_id_2, instance=instance_2, creations=creations_2, existence=existence_2, has_disposal_methods=has_disposal_methods_2, disposal_methods=disposal_methods_2)
    elif existence_2 in (Existence.unique_per_conduit, Existence.unique_per_spell_space):
        instance_2 = _get_existing_creation(spell=spell_2, creations=creations_2, existence=existence_2)
        if instance_2 is not None:
            _raise_override_on_existing_instance(spell=spell_2, has_targeted_overrides=has_targeted_overrides_2, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with creations_2._lock:
                instance_2 = _get_existing_creation(spell=spell_2, creations=creations_2, existence=existence_2)
                if instance_2 is not None:
                    _raise_override_on_existing_instance(spell=spell_2, has_targeted_overrides=has_targeted_overrides_2, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_2 = _construct_spell_instance_with_overrides(plan_step=plan_step_2, instance_results=instance_results, override_targets=override_targets_2, override_map=override_map, root_positional_override=step_root_positional_override_2)
                    _register_spell_instance_prebound(spell_id=spell_id_2, instance=instance_2, creations=creations_2, existence=existence_2, has_disposal_methods=has_disposal_methods_2, disposal_methods=disposal_methods_2)
    else:
        use_spell_lock_2 = step_use_spell_lock_hints[2]
        if use_spell_lock_2:
            with spell_2._lock:
                with creations_2._lock:
                    instance_2 = _get_existing_creation(spell=spell_2, creations=creations_2, existence=existence_2)
                if instance_2 is not None:
                    _raise_override_on_existing_instance(spell=spell_2, has_targeted_overrides=has_targeted_overrides_2, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_2 = _construct_spell_instance_with_overrides(plan_step=plan_step_2, instance_results=instance_results, override_targets=override_targets_2, override_map=override_map, root_positional_override=step_root_positional_override_2)
                    with creations_2._lock:
                        _register_spell_instance_prebound(spell_id=spell_id_2, instance=instance_2, creations=creations_2, existence=existence_2, has_disposal_methods=has_disposal_methods_2, disposal_methods=disposal_methods_2)
        else:
            with creations_2._lock:
                instance_2 = _get_existing_creation(spell=spell_2, creations=creations_2, existence=existence_2)
                if instance_2 is not None:
                    _raise_override_on_existing_instance(spell=spell_2, has_targeted_overrides=has_targeted_overrides_2, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_2 = _construct_spell_instance_with_overrides(plan_step=plan_step_2, instance_results=instance_results, override_targets=override_targets_2, override_map=override_map, root_positional_override=step_root_positional_override_2)
                    _register_spell_instance_prebound(spell_id=spell_id_2, instance=instance_2, creations=creations_2, existence=existence_2, has_disposal_methods=has_disposal_methods_2, disposal_methods=disposal_methods_2)
    instance_results[step_instance_keys[2]] = instance_2
    plan_step_3 = steps[3]
    spell_3 = step_spells[3]
    spell_id_3 = step_spell_ids[3]
    has_disposal_methods_3 = step_has_disposal_methods[3]
    disposal_methods_3 = step_disposal_methods[3]
    existence_3 = step_existences[3]
    if existence_3 is Existence.many:
        creations_3 = meld._spellspace_creations
        if creations_3 is None:
            creations_3 = meld._conduit_creations
    elif existence_3 is Existence.unique_per_conduit:
        creations_3 = meld._conduit_creations
    elif existence_3 is Existence.unique_per_spell_space:
        creations_3 = meld._spellspace_creations
    elif existence_3 is Existence.unique_per_conduit_lineage:
        creations_3 = meld._root_creations
    elif existence_3 is Existence.unique_per_conduit_cluster:
        creations_3 = meld._cluster_creations.resolved_store()
    elif existence_3 is Existence.unique:
        creations_3 = spell_3._owner_creations
    else:
        raise RuntimeError(f"Unsupported existence '{existence_3}' for spell '{spell_3.spell_id}'.")
    override_targets_3 = step_override_targets[3]
    has_targeted_overrides_3 = step_has_targeted_overrides[3]
    is_root_step_3 = step_is_root[3]
    step_root_positional_override_3 = root_positional_override if is_root_step_3 else None
    must_register_3 = step_must_register_flags[3]
    if existence_3 is Existence.many:
        instance_3 = _construct_spell_instance_with_overrides(plan_step=plan_step_3, instance_results=instance_results, override_targets=override_targets_3, override_map=override_map, root_positional_override=step_root_positional_override_3)
        if must_register_3:
            with creations_3._lock:
                _register_spell_instance_prebound(spell_id=spell_id_3, instance=instance_3, creations=creations_3, existence=existence_3, has_disposal_methods=has_disposal_methods_3, disposal_methods=disposal_methods_3)
    elif existence_3 in (Existence.unique_per_conduit, Existence.unique_per_spell_space):
        instance_3 = _get_existing_creation(spell=spell_3, creations=creations_3, existence=existence_3)
        if instance_3 is not None:
            _raise_override_on_existing_instance(spell=spell_3, has_targeted_overrides=has_targeted_overrides_3, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with creations_3._lock:
                instance_3 = _get_existing_creation(spell=spell_3, creations=creations_3, existence=existence_3)
                if instance_3 is not None:
                    _raise_override_on_existing_instance(spell=spell_3, has_targeted_overrides=has_targeted_overrides_3, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_3 = _construct_spell_instance_with_overrides(plan_step=plan_step_3, instance_results=instance_results, override_targets=override_targets_3, override_map=override_map, root_positional_override=step_root_positional_override_3)
                    _register_spell_instance_prebound(spell_id=spell_id_3, instance=instance_3, creations=creations_3, existence=existence_3, has_disposal_methods=has_disposal_methods_3, disposal_methods=disposal_methods_3)
    else:
        use_spell_lock_3 = step_use_spell_lock_hints[3]
        if use_spell_lock_3:
            with spell_3._lock:
                with creations_3._lock:
                    instance_3 = _get_existing_creation(spell=spell_3, creations=creations_3, existence=existence_3)
                if instance_3 is not None:
                    _raise_override_on_existing_instance(spell=spell_3, has_targeted_overrides=has_targeted_overrides_3, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_3 = _construct_spell_instance_with_overrides(plan_step=plan_step_3, instance_results=instance_results, override_targets=override_targets_3, override_map=override_map, root_positional_override=step_root_positional_override_3)
                    with creations_3._lock:
                        _register_spell_instance_prebound(spell_id=spell_id_3, instance=instance_3, creations=creations_3, existence=existence_3, has_disposal_methods=has_disposal_methods_3, disposal_methods=disposal_methods_3)
        else:
            with creations_3._lock:
                instance_3 = _get_existing_creation(spell=spell_3, creations=creations_3, existence=existence_3)
                if instance_3 is not None:
                    _raise_override_on_existing_instance(spell=spell_3, has_targeted_overrides=has_targeted_overrides_3, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_3 = _construct_spell_instance_with_overrides(plan_step=plan_step_3, instance_results=instance_results, override_targets=override_targets_3, override_map=override_map, root_positional_override=step_root_positional_override_3)
                    _register_spell_instance_prebound(spell_id=spell_id_3, instance=instance_3, creations=creations_3, existence=existence_3, has_disposal_methods=has_disposal_methods_3, disposal_methods=disposal_methods_3)
    instance_results[step_instance_keys[3]] = instance_3
    plan_step_4 = steps[4]
    spell_4 = step_spells[4]
    spell_id_4 = step_spell_ids[4]
    has_disposal_methods_4 = step_has_disposal_methods[4]
    disposal_methods_4 = step_disposal_methods[4]
    existence_4 = step_existences[4]
    if existence_4 is Existence.many:
        creations_4 = meld._spellspace_creations
        if creations_4 is None:
            creations_4 = meld._conduit_creations
    elif existence_4 is Existence.unique_per_conduit:
        creations_4 = meld._conduit_creations
    elif existence_4 is Existence.unique_per_spell_space:
        creations_4 = meld._spellspace_creations
    elif existence_4 is Existence.unique_per_conduit_lineage:
        creations_4 = meld._root_creations
    elif existence_4 is Existence.unique_per_conduit_cluster:
        creations_4 = meld._cluster_creations.resolved_store()
    elif existence_4 is Existence.unique:
        creations_4 = spell_4._owner_creations
    else:
        raise RuntimeError(f"Unsupported existence '{existence_4}' for spell '{spell_4.spell_id}'.")
    override_targets_4 = step_override_targets[4]
    has_targeted_overrides_4 = step_has_targeted_overrides[4]
    is_root_step_4 = step_is_root[4]
    step_root_positional_override_4 = root_positional_override if is_root_step_4 else None
    must_register_4 = step_must_register_flags[4]
    if existence_4 is Existence.many:
        instance_4 = _construct_spell_instance_with_overrides(plan_step=plan_step_4, instance_results=instance_results, override_targets=override_targets_4, override_map=override_map, root_positional_override=step_root_positional_override_4)
        if must_register_4:
            with creations_4._lock:
                _register_spell_instance_prebound(spell_id=spell_id_4, instance=instance_4, creations=creations_4, existence=existence_4, has_disposal_methods=has_disposal_methods_4, disposal_methods=disposal_methods_4)
    elif existence_4 in (Existence.unique_per_conduit, Existence.unique_per_spell_space):
        instance_4 = _get_existing_creation(spell=spell_4, creations=creations_4, existence=existence_4)
        if instance_4 is not None:
            _raise_override_on_existing_instance(spell=spell_4, has_targeted_overrides=has_targeted_overrides_4, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
        else:
            with creations_4._lock:
                instance_4 = _get_existing_creation(spell=spell_4, creations=creations_4, existence=existence_4)
                if instance_4 is not None:
                    _raise_override_on_existing_instance(spell=spell_4, has_targeted_overrides=has_targeted_overrides_4, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_4 = _construct_spell_instance_with_overrides(plan_step=plan_step_4, instance_results=instance_results, override_targets=override_targets_4, override_map=override_map, root_positional_override=step_root_positional_override_4)
                    _register_spell_instance_prebound(spell_id=spell_id_4, instance=instance_4, creations=creations_4, existence=existence_4, has_disposal_methods=has_disposal_methods_4, disposal_methods=disposal_methods_4)
    else:
        use_spell_lock_4 = step_use_spell_lock_hints[4]
        if use_spell_lock_4:
            with spell_4._lock:
                with creations_4._lock:
                    instance_4 = _get_existing_creation(spell=spell_4, creations=creations_4, existence=existence_4)
                if instance_4 is not None:
                    _raise_override_on_existing_instance(spell=spell_4, has_targeted_overrides=has_targeted_overrides_4, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_4 = _construct_spell_instance_with_overrides(plan_step=plan_step_4, instance_results=instance_results, override_targets=override_targets_4, override_map=override_map, root_positional_override=step_root_positional_override_4)
                    with creations_4._lock:
                        _register_spell_instance_prebound(spell_id=spell_id_4, instance=instance_4, creations=creations_4, existence=existence_4, has_disposal_methods=has_disposal_methods_4, disposal_methods=disposal_methods_4)
        else:
            with creations_4._lock:
                instance_4 = _get_existing_creation(spell=spell_4, creations=creations_4, existence=existence_4)
                if instance_4 is not None:
                    _raise_override_on_existing_instance(spell=spell_4, has_targeted_overrides=has_targeted_overrides_4, any_overrides_present=any_overrides_present, root_spell_id=root_spell_id)
                else:
                    instance_4 = _construct_spell_instance_with_overrides(plan_step=plan_step_4, instance_results=instance_results, override_targets=override_targets_4, override_map=override_map, root_positional_override=step_root_positional_override_4)
                    _register_spell_instance_prebound(spell_id=spell_id_4, instance=instance_4, creations=creations_4, existence=existence_4, has_disposal_methods=has_disposal_methods_4, disposal_methods=disposal_methods_4)
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
