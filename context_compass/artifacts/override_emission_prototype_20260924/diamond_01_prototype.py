def _prototype_executor(meld, override_map, root_positional_override):
    try:
        v0 = _prototype_target_0()
    except Exception as exc:
        error_spell = _prototype_spell_0
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v1 = _prototype_target_1()
    except Exception as exc:
        error_spell = _prototype_spell_1
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v2 = _prototype_target_2(v1)
    except Exception as exc:
        error_spell = _prototype_spell_2
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v3 = _prototype_target_3(v0)
    except Exception as exc:
        error_spell = _prototype_spell_3
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    o4_0 = override_map[_prototype_socket_4_0]
    o4_1 = override_map[_prototype_socket_4_1]
    try:
        v4 = _prototype_target_4(o4_0, o4_1)
    except Exception as exc:
        error_spell = _prototype_spell_4
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    return v4
