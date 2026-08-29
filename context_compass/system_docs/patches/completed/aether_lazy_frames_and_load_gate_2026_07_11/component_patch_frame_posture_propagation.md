# Component Patch: frame posture -> mediator wait-bound propagation

- Patch ID: aether_lazy_frames_and_load_gate_2026_07_11 (same seam; owner
  go 2026-07-11 after the DevOps-twin investigation)
- Ticket: STORY-2026-07-11-load-scope-maturity (investigation FACT note)

## Problem (source-verified)
AethericFrameCrystal twins the FULL dev-ops posture (describe_posture map
incl. max_transaction_wait_time_in_seconds); from_recorded_posture reloads
it; bind_frame_configuration copies it onto the frame's canonical posture
object. But the live TransactionMediator captures the wait bound ONCE at
frame construction (CCM ctor), and `mediator.configure()` - the update verb
built for exactly this - has ZERO callers. Restored/rebound wait bounds
never reach the mediator. Under lazy frames this is guaranteed at restore:
frames are born mid-replay with the default posture (30.0) BEFORE the
frames stage rebinds recorded truth. The disable_* gates are unaffected
(read live at verb time from the canonical posture object).

## Change
AethericFrame gains one private helper,
`_propagate_transaction_wait_posture(posture)`, that routes the canonical
posture's wait bound through the EXISTING public chain:
`dev_ops_manager.change_control_manager.transaction_mediator.configure(
max_transaction_wait_time_in_seconds=...)` (normal-verbs law; the reload
exception stays config-side). Called from BOTH posture-landing branches of
`bind_frame_configuration`: the adopt-new branch (after
freeze_frame_configuration returns) and the copy-into-existing branch
(after freeze). The idempotent-match and conflict-refusal branches change
nothing, so no propagation there.

## State/Failure Deltas
- None new: configure() validates >0 (recorded values already validated at
  posture construction). Propagating an unchanged value is a no-op set.

## Validation Expectations
- Integration (real frames): bind a posture carrying a non-default wait
  bound; assert the frame's mediator enforces it (describe/read the bound).
- Restore round-trips: recorded wait bound lands on the live mediator after
  the frames stage.
- Owner runs 3.14t; "Not run." until then.
