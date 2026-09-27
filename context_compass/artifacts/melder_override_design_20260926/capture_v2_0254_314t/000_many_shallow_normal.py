t0 = transient_targets[0]
t1 = transient_targets[1]
t2 = transient_targets[2]
def _no_overrides_codegen_creation_executor(meld):
    try:
        v0 = t0()
    except Exception as exc:
        _raise_meld_construction_error(steps[0].spell, exc, (), 0)
    try:
        v1 = t1()
    except Exception as exc:
        _raise_meld_construction_error(steps[1].spell, exc, (), 0)
    try:
        v2 = t2(v0, v1)
    except Exception as exc:
        _raise_meld_construction_error(steps[2].spell, exc, (), 2)
    return v2
