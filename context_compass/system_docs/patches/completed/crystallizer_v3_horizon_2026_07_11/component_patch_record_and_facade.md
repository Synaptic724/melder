# Component Patch: persistence record + Crystallizer facade (S1)

- Patch ID: crystallizer_v3_horizon_2026_07_11
- Story: STORY-2026-07-11-load-scope-maturity

## PersistenceProfile (record)
Before: compose_frame_subtree/compose_conduit_subtree raise
NotImplementedError, promising a "tree-view composer" for the restore
engine story.
After: both methods DELETED (owner ruling folded into S1). The promised
capability shipped as capture_formation_slice (the formation capture
composer consumed by PersistenceSystem.capture_formation_record); grep
proves zero code callers. A NOTE comment at the deletion site records the
absorption so the knowledge survives.

## Crystallizer facade
Before: restore_formation(formation_name, profile_name=None).
After: restore_formation(formation_name, profile_name=None, *,
target_frame_name=None, skip_existing=False) - byte-compatible for every
existing call; new kwargs thread through the loader untouched. Docstring
gains the host-admission contract (refusal class + skip semantics +
"host" admission key).

## Validation Expectations
- Existing formation round-trip tests pass unchanged (defaults).
- New facade test: kwargs thread to the loader (behavioral, via a live
  collision scenario at the integration tier).
- Owner runs 3.14t; "Not run." until then.
