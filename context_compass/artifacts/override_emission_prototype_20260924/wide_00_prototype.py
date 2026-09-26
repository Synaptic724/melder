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
        v2 = _prototype_target_2()
    except Exception as exc:
        error_spell = _prototype_spell_2
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v3 = _prototype_target_3()
    except Exception as exc:
        error_spell = _prototype_spell_3
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v4 = _prototype_target_4()
    except Exception as exc:
        error_spell = _prototype_spell_4
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v5 = _prototype_target_5()
    except Exception as exc:
        error_spell = _prototype_spell_5
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v6 = _prototype_target_6()
    except Exception as exc:
        error_spell = _prototype_spell_6
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v7 = _prototype_target_7()
    except Exception as exc:
        error_spell = _prototype_spell_7
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    o8_0 = override_map[_prototype_socket_8_0]
    try:
        v8 = _prototype_target_8(o8_0, v3, v2, v5, v1, v6, v7, v4)
    except Exception as exc:
        error_spell = _prototype_spell_8
        raise MeldExecutionError(
            spell_id=error_spell.spell_index.selected_spell_id,
            spell_name=error_spell.spell_name,
            message=f"Error invoking spell '{error_spell.spell_name}'.",
            inner=exc,
        ) from exc
    return v8
