# Public configured-Book recording repair

## Observed Failure
The new public-only expert lesson configures frame posture through Spellbook.configure_aether_frame
before binding/conjure. That call locks configuration before _conjure_dynamic_hint is known. Normal
conjure's preparation skips locked configuration entirely, so no origin-bearing Book twin is emitted.
The recorded named lessers and spell custody then refer to a missing Book; restore preflight refuses.

## Bounded Repair
Mirror the already-delivered existing-conduit route in ordinary Spellbook._conjure_logic: after
single-conjure and integrity checks, re-enter _validate_and_freeze_configuration when the Book is
already locked. Frozen configuration values are unchanged; its existing origin-aware emitter now
receives the effective dynamic hint and current Book identity. Bind the frame posture as the normal
unlocked preparation does: configure_aether_frame freezes only the rich configuration. Otherwise
the record lacks the frame twin and replay loses Rift policy through its legacy fallback. Unlocked
preparation stays unchanged.

## Invariants and Validation
No new recording sweep, synthetic twin, compiler path or pool/Meld work. Inactive/automatic emission
gates stay in the configuration emitter. Prove public frame-configuration capture and both replay
drivers, including frame-wide configuration. The new expert lesson must restore successfully without
deep imports or weakening its assertion. Existing graduation recording remains unchanged.
