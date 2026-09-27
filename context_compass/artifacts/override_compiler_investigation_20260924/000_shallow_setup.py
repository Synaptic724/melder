t0 = transient_targets[0]
t1 = transient_targets[1]
t2 = transient_targets[2]
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
        v2 = t2(v0, v1)
    except Exception as exc:
        step_spell = steps[2].spell
        raise MeldExecutionError(
            spell_id=step_spell.spell_index.selected_spell_id,
            spell_name=step_spell.spell_name,
            message=f"Error invoking spell '{step_spell.spell_name}'.",
            inner=exc,
        ) from exc
    return v2
