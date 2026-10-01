# Codegen strategy certification (VM, CPython 3.14.7t, GIL disabled; tree 0.2.8214; GC disabled during timing,
# many buckets drained between variants). Plan-direct ns per creation; the reference row is the whole meld by name.

## Run 2 (2026-09-30T19:03Z)

| shape | variant | ns per creation (plan direct) | vs plain | py calls | C calls |
| --- | --- | ---: | ---: | ---: | ---: |
| worker | plain | 350 |  | 4 | 9 |
| worker | S1 trim registration | 183 | -48% | 3 | 5 |
| worker | S2b unique captures | 286 | -18% | 4 | 8 |
| worker | S4 single-door prologue | 291 | -17% | 4 | 9 |
| worker | S5 batched registration | 112 | -68% | 2 | 2 |
| worker | S6 thread-affine append | 126 | -64% | 2 | 3 |
| worker | ALL (S8+S4+S2a+S2b+S1) | 165 | -53% | 3 | 4 |
| worker | ALL+S5 (S5 for S1) | 97 | -72% | 2 | 1 |
| worker | reference: conduit.meld("Worker") | 483 | | | |
| context_root | plain | 596 |  | 4 | 13 |
| context_root | S1 trim registration | 466 | -22% | 3 | 9 |
| context_root | S2a existing constants | 520 | -13% | 4 | 9 |
| context_root | S2b unique captures | 598 | +0% | 4 | 12 |
| context_root | S4 single-door prologue | 576 | -3% | 4 | 13 |
| context_root | S5 batched registration | 389 | -35% | 2 | 6 |
| context_root | S6 thread-affine append | 410 | -31% | 2 | 7 |
| context_root | S8 lazy instance_results | 492 | -17% | 4 | 13 |
| context_root | ALL (S8+S4+S2a+S2b+S1) | 226 | -62% | 3 | 4 |
| context_root | ALL+S5 (S5 for S1) | 160 | -73% | 2 | 1 |
| context_root | reference: conduit.meld("ContextRoot") | 776 | | | |
| wide8_unique | plain | 581 |  | 4 | 16 |
| wide8_unique | S1 trim registration | 444 | -24% | 3 | 12 |
| wide8_unique | S2b unique captures | 506 | -13% | 4 | 8 |
| wide8_unique | S4 single-door prologue | 581 | +0% | 4 | 16 |
| wide8_unique | S5 batched registration | 395 | -32% | 2 | 9 |
| wide8_unique | S6 thread-affine append | 389 | -33% | 2 | 10 |
| wide8_unique | ALL (S8+S4+S2a+S2b+S1) | 327 | -44% | 3 | 4 |
| wide8_unique | ALL+S5 (S5 for S1) | 251 | -57% | 2 | 1 |
| wide8_unique | reference: conduit.meld("Wide8Unique") | 808 | | | |
| wide8_existing | plain | 781 |  | 4 | 16 |
| wide8_existing | S1 trim registration | 714 | -9% | 3 | 12 |
| wide8_existing | S2a existing constants | 645 | -17% | 4 | 8 |
| wide8_existing | S4 single-door prologue | 843 | +8% | 4 | 16 |
| wide8_existing | S5 batched registration | 594 | -24% | 2 | 9 |
| wide8_existing | S6 thread-affine append | 603 | -23% | 2 | 10 |
| wide8_existing | S8 lazy instance_results | 660 | -15% | 4 | 16 |
| wide8_existing | ALL (S8+S4+S2a+S2b+S1) | 271 | -65% | 3 | 4 |
| wide8_existing | ALL+S5 (S5 for S1) | 195 | -75% | 2 | 1 |
| wide8_existing | reference: conduit.meld("Wide8Existing") | 1004 | | | |
| chain8_transient | plain | 710 |  | 11 | 9 |
| chain8_transient | S1 trim registration | 448 | -37% | 10 | 5 |
| chain8_transient | S2b unique captures | 643 | -9% | 11 | 8 |
| chain8_transient | S4 single-door prologue | 662 | -7% | 11 | 9 |
| chain8_transient | S5 batched registration | 360 | -49% | 9 | 2 |
| chain8_transient | S6 thread-affine append | 388 | -45% | 9 | 3 |
| chain8_transient | ALL (S8+S4+S2a+S2b+S1) | 424 | -40% | 10 | 4 |
| chain8_transient | ALL+S5 (S5 for S1) | 351 | -51% | 9 | 1 |
| chain8_transient | reference: conduit.meld("Chain8") | 780 | | | |

## Run 3 with the captured plain bodies (2026-09-30T19:05Z)

| shape | variant | ns per creation (plan direct) | vs plain | py calls | C calls |
| --- | --- | ---: | ---: | ---: | ---: |

```
# worker
def _miss0(meld, c0):
    with spells[0]._lock:
        v0 = c0._creations.get(sid0)
        if v0 is None:
            try:
                v0 = t0()
            except Exception as exc:
                _raise_meld_construction_error(spells[0], exc)
            c0.add_creation(sid0, v0, has_disposal_methods=True, disposal_methods=dm0)
        return v0
def _site_plan_executor(meld):
    many_store = meld._spellspace_creations
    if many_store is None:
        many_store = meld._conduit_creations
    c0 = spells[0]._owner_creations
    v0 = c0._creations.get(sid0)
    if v0 is None:
        v0 = _miss0(meld, c0)
    try:
        v1 = t1(v0)
    except Exception as exc:
        _raise_meld_construction_error(spells[1], exc)
    many_store.add_many_creations(sid1, v1, has_disposal_methods=True, disposal_methods=dm1)
    return v1

```
| worker | plain | 348 |  | 4 | 9 |
| worker | S1 trim registration | 187 | -46% | 3 | 5 |
| worker | S2b unique captures | 294 | -15% | 4 | 8 |
| worker | S4 single-door prologue | 295 | -15% | 4 | 9 |
| worker | S5 batched registration | 115 | -67% | 2 | 2 |
| worker | S6 thread-affine append | 124 | -64% | 2 | 3 |
| worker | ALL (S8+S4+S2a+S2b+S1) | 172 | -50% | 3 | 4 |
| worker | ALL+S5 (S5 for S1) | 96 | -72% | 2 | 1 |
| worker | reference: conduit.meld("Worker") | 480 | | | |

```
# context_root
def _miss0(meld, c0, instance_results):
    with spells[0]._lock:
        v0 = c0._creations.get(sid0)
        if v0 is None:
            v0 = _construct_spell_instance(plan_step=st0, instance_results=instance_results)
            c0._creations[sid0] = v0
        return v0
def _miss1(meld, c1, instance_results):
    with spells[1]._lock:
        v1 = c1._creations.get(sid1)
        if v1 is None:
            v1 = _construct_spell_instance(plan_step=st1, instance_results=instance_results)
            c1._creations[sid1] = v1
        return v1
def _miss2(meld, c2, instance_results):
    with spells[2]._lock:
        v2 = c2._creations.get(sid2)
        if v2 is None:
            try:
                v2 = t2()
            except Exception as exc:
                _raise_meld_construction_error(spells[2], exc)
            c2.add_creation(sid2, v2, has_disposal_methods=True, disposal_methods=dm2)
        return v2
def _miss3(meld, c3, instance_results):
    with spells[3]._lock:
        v3 = c3._creations.get(sid3)
        if v3 is None:
            v3 = _construct_spell_instance(plan_step=st3, instance_results=instance_results)
            c3._creations[sid3] = v3
        return v3
def _miss4(meld, c4, instance_results):
    with spells[4]._lock:
        v4 = c4._creations.get(sid4)
        if v4 is None:
            v4 = _construct_spell_instance(plan_step=st4, instance_results=instance_results)
            c4._creations[sid4] = v4
        return v4
def _site_plan_executor(meld):
    many_store = meld._spellspace_creations
    if many_store is None:
        many_store = meld._conduit_creations
    instance_results = {}
    c0 = spells[0]._owner_creations
    v0 = c0._creations.get(sid0)
    if v0 is None:
        v0 = _miss0(meld, c0, instance_results)
    instance_results[key0] = v0
    c1 = spells[1]._owner_creations
    v1 = c1._creations.get(sid1)
    if v1 is None:
        v1 = _miss1(meld, c1, instance_results)
    instance_results[key1] = v1
    c2 = spells[2]._owner_creations
    v2 = c2._creations.get(sid2)
    if v2 is None:
        v2 = _miss2(meld, c2, instance_results)
    instance_results[key2] = v2
    c3 = spells[3]._owner_creations
    v3 = c3._creations.get(sid3)
    if v3 is None:
        v3 = _miss3(meld, c3, instance_results)
    instance_results[key3] = v3
    c4 = spells[4]._owner_creations
    v4 = c4._creations.get(sid4)
    if v4 is None:
        v4 = _miss4(meld, c4, instance_results)
    instance_results[key4] = v4
    try:
        v5 = t5(v0, v4, v1, v3, v2)
    except Exception as exc:
        _raise_meld_construction_error(spells[5], exc)
    many_store.add_many_creations(sid5, v5, has_disposal_methods=True, disposal_methods=dm5)
    instance_results[key5] = v5
    return v5

```
| context_root | plain | 596 |  | 4 | 13 |
| context_root | S1 trim registration | 461 | -23% | 3 | 9 |
| context_root | S2a existing constants | 526 | -12% | 4 | 9 |
| context_root | S2b unique captures | 599 | +0% | 4 | 12 |
| context_root | S4 single-door prologue | 627 | +5% | 4 | 13 |
| context_root | S5 batched registration | 390 | -35% | 2 | 6 |
| context_root | S6 thread-affine append | 418 | -30% | 2 | 7 |
| context_root | S8 lazy instance_results | 447 | -25% | 4 | 13 |
| context_root | ALL (S8+S4+S2a+S2b+S1) | 228 | -62% | 3 | 4 |
| context_root | ALL+S5 (S5 for S1) | 164 | -72% | 2 | 1 |
| context_root | reference: conduit.meld("ContextRoot") | 788 | | | |

```
# wide8_unique
def _miss0(meld, c0):
    with spells[0]._lock:
        v0 = c0._creations.get(sid0)
        if v0 is None:
            try:
                v0 = t0()
            except Exception as exc:
                _raise_meld_construction_error(spells[0], exc)
            c0._creations[sid0] = v0
        return v0
def _miss1(meld, c1):
    with spells[1]._lock:
        v1 = c1._creations.get(sid1)
        if v1 is None:
            try:
                v1 = t1()
            except Exception as exc:
                _raise_meld_construction_error(spells[1], exc)
            c1._creations[sid1] = v1
        return v1
def _miss2(meld, c2):
    with spells[2]._lock:
        v2 = c2._creations.get(sid2)
        if v2 is None:
            try:
                v2 = t2()
            except Exception as exc:
                _raise_meld_construction_error(spells[2], exc)
            c2._creations[sid2] = v2
        return v2
def _miss3(meld, c3):
    with spells[3]._lock:
        v3 = c3._creations.get(sid3)
        if v3 is None:
            try:
                v3 = t3()
            except Exception as exc:
                _raise_meld_construction_error(spells[3], exc)
            c3._creations[sid3] = v3
        return v3
def _miss4(meld, c4):
    with spells[4]._lock:
        v4 = c4._creations.get(sid4)
        if v4 is None:
            try:
                v4 = t4()
            except Exception as exc:
                _raise_meld_construction_error(spells[4], exc)
            c4._creations[sid4] = v4
        return v4
def _miss5(meld, c5):
    with spells[5]._lock:
        v5 = c5._creations.get(sid5)
        if v5 is None:
            try:
                v5 = t5()
            except Exception as exc:
                _raise_meld_construction_error(spells[5], exc)
            c5._creations[sid5] = v5
        return v5
def _miss6(meld, c6):
    with spells[6]._lock:
        v6 = c6._creations.get(sid6)
        if v6 is None:
            try:
                v6 = t6()
            except Exception as exc:
                _raise_meld_construction_error(spells[6], exc)
            c6._creations[sid6] = v6
        return v6
def _miss7(meld, c7):
    with spells[7]._lock:
        v7 = c7._creations.get(sid7)
        if v7 is None:
            try:
                v7 = t7()
            except Exception as exc:
                _raise_meld_construction_error(spells[7], exc)
            c7._creations[sid7] = v7
        return v7
def _site_plan_executor(meld):
    many_store = meld._spellspace_creations
    if many_store is None:
        many_store = meld._conduit_creations
    c0 = spells[0]._owner_creations
    v0 = c0._creations.get(sid0)
    if v0 is None:
        v0 = _miss0(meld, c0)
    c1 = spells[1]._owner_creations
    v1 = c1._creations.get(sid1)
    if v1 is None:
        v1 = _miss1(meld, c1)
    c2 = spells[2]._owner_creations
    v2 = c2._creations.get(sid2)
    if v2 is None:
        v2 = _miss2(meld, c2)
    c3 = spells[3]._owner_creations
    v3 = c3._creations.get(sid3)
    if v3 is None:
        v3 = _miss3(meld, c3)
    c4 = spells[4]._owner_creations
    v4 = c4._creations.get(sid4)
    if v4 is None:
        v4 = _miss4(meld, c4)
    c5 = spells[5]._owner_creations
    v5 = c5._creations.get(sid5)
    if v5 is None:
        v5 = _miss5(meld, c5)
    c6 = spells[6]._owner_creations
    v6 = c6._creations.get(sid6)
    if v6 is None:
        v6 = _miss6(meld, c6)
    c7 = spells[7]._owner_creations
    v7 = c7._creations.get(sid7)
    if v7 is None:
        v7 = _miss7(meld, c7)
    try:
        v8 = t8(v3, v7, v2, v0, v4, v6, v5, v1)
    except Exception as exc:
        _raise_meld_construction_error(spells[8], exc)
    many_store.add_many_creations(sid8, v8, has_disposal_methods=True, disposal_methods=dm8)
    return v8

```
| wide8_unique | plain | 576 |  | 4 | 16 |
| wide8_unique | S1 trim registration | 451 | -22% | 3 | 12 |
| wide8_unique | S2b unique captures | 514 | -11% | 4 | 8 |
| wide8_unique | S4 single-door prologue | 596 | +3% | 4 | 16 |
| wide8_unique | S5 batched registration | 372 | -35% | 2 | 9 |
| wide8_unique | S6 thread-affine append | 382 | -34% | 2 | 10 |
| wide8_unique | ALL (S8+S4+S2a+S2b+S1) | 327 | -43% | 3 | 4 |
| wide8_unique | ALL+S5 (S5 for S1) | 252 | -56% | 2 | 1 |
| wide8_unique | reference: conduit.meld("Wide8Unique") | 796 | | | |

```
# wide8_existing
def _miss0(meld, c0, instance_results):
    with spells[0]._lock:
        v0 = c0._creations.get(sid0)
        if v0 is None:
            v0 = _construct_spell_instance(plan_step=st0, instance_results=instance_results)
            c0._creations[sid0] = v0
        return v0
def _miss1(meld, c1, instance_results):
    with spells[1]._lock:
        v1 = c1._creations.get(sid1)
        if v1 is None:
            v1 = _construct_spell_instance(plan_step=st1, instance_results=instance_results)
            c1._creations[sid1] = v1
        return v1
def _miss2(meld, c2, instance_results):
    with spells[2]._lock:
        v2 = c2._creations.get(sid2)
        if v2 is None:
            v2 = _construct_spell_instance(plan_step=st2, instance_results=instance_results)
            c2._creations[sid2] = v2
        return v2
def _miss3(meld, c3, instance_results):
    with spells[3]._lock:
        v3 = c3._creations.get(sid3)
        if v3 is None:
            v3 = _construct_spell_instance(plan_step=st3, instance_results=instance_results)
            c3._creations[sid3] = v3
        return v3
def _miss4(meld, c4, instance_results):
    with spells[4]._lock:
        v4 = c4._creations.get(sid4)
        if v4 is None:
            v4 = _construct_spell_instance(plan_step=st4, instance_results=instance_results)
            c4._creations[sid4] = v4
        return v4
def _miss5(meld, c5, instance_results):
    with spells[5]._lock:
        v5 = c5._creations.get(sid5)
        if v5 is None:
            v5 = _construct_spell_instance(plan_step=st5, instance_results=instance_results)
            c5._creations[sid5] = v5
        return v5
def _miss6(meld, c6, instance_results):
    with spells[6]._lock:
        v6 = c6._creations.get(sid6)
        if v6 is None:
            v6 = _construct_spell_instance(plan_step=st6, instance_results=instance_results)
            c6._creations[sid6] = v6
        return v6
def _miss7(meld, c7, instance_results):
    with spells[7]._lock:
        v7 = c7._creations.get(sid7)
        if v7 is None:
            v7 = _construct_spell_instance(plan_step=st7, instance_results=instance_results)
            c7._creations[sid7] = v7
        return v7
def _site_plan_executor(meld):
    many_store = meld._spellspace_creations
    if many_store is None:
        many_store = meld._conduit_creations
    instance_results = {}
    c0 = spells[0]._owner_creations
    v0 = c0._creations.get(sid0)
    if v0 is None:
        v0 = _miss0(meld, c0, instance_results)
    instance_results[key0] = v0
    c1 = spells[1]._owner_creations
    v1 = c1._creations.get(sid1)
    if v1 is None:
        v1 = _miss1(meld, c1, instance_results)
    instance_results[key1] = v1
    c2 = spells[2]._owner_creations
    v2 = c2._creations.get(sid2)
    if v2 is None:
        v2 = _miss2(meld, c2, instance_results)
    instance_results[key2] = v2
    c3 = spells[3]._owner_creations
    v3 = c3._creations.get(sid3)
    if v3 is None:
        v3 = _miss3(meld, c3, instance_results)
    instance_results[key3] = v3
    c4 = spells[4]._owner_creations
    v4 = c4._creations.get(sid4)
    if v4 is None:
        v4 = _miss4(meld, c4, instance_results)
    instance_results[key4] = v4
    c5 = spells[5]._owner_creations
    v5 = c5._creations.get(sid5)
    if v5 is None:
        v5 = _miss5(meld, c5, instance_results)
    instance_results[key5] = v5
    c6 = spells[6]._owner_creations
    v6 = c6._creations.get(sid6)
    if v6 is None:
        v6 = _miss6(meld, c6, instance_results)
    instance_results[key6] = v6
    c7 = spells[7]._owner_creations
    v7 = c7._creations.get(sid7)
    if v7 is None:
        v7 = _miss7(meld, c7, instance_results)
    instance_results[key7] = v7
    try:
        v8 = t8(v7, v4, v6, v1, v5, v3, v2, v0)
    except Exception as exc:
        _raise_meld_construction_error(spells[8], exc)
    many_store.add_many_creations(sid8, v8, has_disposal_methods=True, disposal_methods=dm8)
    instance_results[key8] = v8
    return v8

```
| wide8_existing | plain | 778 |  | 4 | 16 |
| wide8_existing | S1 trim registration | 668 | -14% | 3 | 12 |
| wide8_existing | S2a existing constants | 639 | -18% | 4 | 8 |
| wide8_existing | S4 single-door prologue | 807 | +4% | 4 | 16 |
| wide8_existing | S5 batched registration | 592 | -24% | 2 | 9 |
| wide8_existing | S6 thread-affine append | 586 | -25% | 2 | 10 |
| wide8_existing | S8 lazy instance_results | 634 | -18% | 4 | 16 |
| wide8_existing | ALL (S8+S4+S2a+S2b+S1) | 263 | -66% | 3 | 4 |
| wide8_existing | ALL+S5 (S5 for S1) | 190 | -76% | 2 | 1 |
| wide8_existing | reference: conduit.meld("Wide8Existing") | 1014 | | | |

```
# chain8_transient
def _miss0(meld, c0):
    with spells[0]._lock:
        v0 = c0._creations.get(sid0)
        if v0 is None:
            try:
                v0 = t0()
            except Exception as exc:
                _raise_meld_construction_error(spells[0], exc)
            c0._creations[sid0] = v0
        return v0
def _site_plan_executor(meld):
    many_store = meld._spellspace_creations
    if many_store is None:
        many_store = meld._conduit_creations
    c0 = spells[0]._owner_creations
    v0 = c0._creations.get(sid0)
    if v0 is None:
        v0 = _miss0(meld, c0)
    try:
        v1 = t1(v0)
    except Exception as exc:
        _raise_meld_construction_error(spells[1], exc)
    try:
        v2 = t2(v1)
    except Exception as exc:
        _raise_meld_construction_error(spells[2], exc)
    try:
        v3 = t3(v2)
    except Exception as exc:
        _raise_meld_construction_error(spells[3], exc)
    try:
        v4 = t4(v3)
    except Exception as exc:
        _raise_meld_construction_error(spells[4], exc)
    try:
        v5 = t5(v4)
    except Exception as exc:
        _raise_meld_construction_error(spells[5], exc)
    try:
        v6 = t6(v5)
    except Exception as exc:
        _raise_meld_construction_error(spells[6], exc)
    try:
        v7 = t7(v6)
    except Exception as exc:
        _raise_meld_construction_error(spells[7], exc)
    try:
        v8 = t8(v7)
    except Exception as exc:
        _raise_meld_construction_error(spells[8], exc)
    many_store.add_many_creations(sid8, v8, has_disposal_methods=True, disposal_methods=dm8)
    return v8

```
| chain8_transient | plain | 707 |  | 11 | 9 |
| chain8_transient | S1 trim registration | 452 | -36% | 10 | 5 |
| chain8_transient | S2b unique captures | 605 | -14% | 11 | 8 |
| chain8_transient | S4 single-door prologue | 595 | -16% | 11 | 9 |
| chain8_transient | S5 batched registration | 364 | -49% | 9 | 2 |
| chain8_transient | S6 thread-affine append | 440 | -38% | 9 | 3 |
| chain8_transient | ALL (S8+S4+S2a+S2b+S1) | 428 | -40% | 10 | 4 |
| chain8_transient | ALL+S5 (S5 for S1) | 360 | -49% | 9 | 1 |
| chain8_transient | reference: conduit.meld("Chain8") | 777 | | | |
