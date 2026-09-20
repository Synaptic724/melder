# Control Flow Patch: Selected-target refusal

<!-- BEGIN ENTRY: Admission ordering and warm-entry proof -->
1. Preserve existing ID/name/frame selection, its cache and its errors.
2. Read the selected Spell's native _resolvable bool.
3. False: raise the common structured error carrying spell_id and spell_name. Do not normalize
   overrides, run hooks or validation, return a stored object, build a context or mint a warm door.
4. True: continue the pre-existing request-scope, validity, override, reuse and execution flow.

The warm door is eligible only after step 4 succeeds. Its captured Spell has immutable True capability;
False bindings have a different identity. Existing epoch/context guards handle invalidation. There is
no second capability cache and no flag mutation API. A test that mutates private _resolvable would
test an unsupported object state rather than a legitimate version transition.

Repeat False calls through both ID and normalized lookup to prove cached input resolution does not
bypass admission. Exercise True warm behavior through the existing fast-door regression suite.
Observational lookup/status remains separate from resolution. Required-input constructor enforcement
and executor/cache hydration remain the next S4 task.
<!-- END ENTRY: Admission ordering and warm-entry proof -->
