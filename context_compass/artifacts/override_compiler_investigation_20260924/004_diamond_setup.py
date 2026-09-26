t0 = transient_targets[0]
t1 = transient_targets[1]
t2 = transient_targets[2]
t3 = transient_targets[3]
t4 = transient_targets[4]
def _no_overrides_codegen_creation_executor(meld):
    try:
        v0 = t0()
    except Exception as exc:
        step_spell = steps[0].spell
        raise MeldExecutionError(
            spell_id=step_spell.spell_index.selected_spell_id,
            spell_name=step_spell.spell_name,
            message=f"Error invoking spell '{step_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v1 = t1()
    except Exception as exc:
        step_spell = steps[1].spell
        raise MeldExecutionError(
            spell_id=step_spell.spell_index.selected_spell_id,
            spell_name=step_spell.spell_name,
            message=f"Error invoking spell '{step_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v2 = t2(v1)
    except Exception as exc:
        step_spell = steps[2].spell
        raise MeldExecutionError(
            spell_id=step_spell.spell_index.selected_spell_id,
            spell_name=step_spell.spell_name,
            message=f"Error invoking spell '{step_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v3 = t3(v0)
    except Exception as exc:
        step_spell = steps[3].spell
        raise MeldExecutionError(
            spell_id=step_spell.spell_index.selected_spell_id,
            spell_name=step_spell.spell_name,
            message=f"Error invoking spell '{step_spell.spell_name}'.",
            inner=exc,
        ) from exc
    try:
        v4 = t4(v3, v2)
    except Exception as exc:
        step_spell = steps[4].spell
        raise MeldExecutionError(
            spell_id=step_spell.spell_index.selected_spell_id,
            spell_name=step_spell.spell_name,
            message=f"Error invoking spell '{step_spell.spell_name}'.",
            inner=exc,
        ) from exc
    return v4
