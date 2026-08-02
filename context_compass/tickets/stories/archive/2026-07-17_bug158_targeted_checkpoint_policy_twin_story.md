# Story: BUG-158 - Targeted checkpoint emits its policy twin into the active profile

## Metadata
- Story ID: STORY-2026-07-17-bug158-targeted-checkpoint-policy-twin
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p1
- Severity: High
- Created: 2026-07-18T15:58:33Z
- Updated: 2026-07-18T15:58:33Z

## Root Cause (verified against current source)
Crystallizer.create_checkpoint(profile_name=X) (crystallizer.py:1466-1510) calls
self._emit_policy_twin() with NO target, then seals profile X. _emit_policy_twin
(crystallizer.py:439-490) records the CrystallizerCrystal policy twin via
PersistenceSystem.record(...), which routes unconditionally to the ACTIVE profile
(persistence_system.py:214-233 -> active_profile.record). So when X is not the active
profile, the policy twin lands in the active profile (e.g. default) while X's window is
empty: X shows an inverted/empty sequence range, zero journal entries, and no policy twin,
and the unrelated active profile receives stray journal traffic (audit BUG-158).

## Fix (root cause: thread the target through)
PersistenceSystem.record gains an optional profile_name (None = active) and resolves the
target profile under the system lock (mirroring create_checkpoint's resolution), so a caller
can record a twin into an explicitly named profile. Crystallizer._emit_policy_twin gains the
same optional profile_name and forwards it to record. create_checkpoint(profile_name=X) now
passes X to _emit_policy_twin so the policy twin is emitted into the profile being sealed. The
other two _emit_policy_twin call sites - activation (crystallizer.py:425) and the automatic
cadence seal (crystallizer.py:528) - target the active profile and correctly keep the default
(None) behavior. All changes are additive/backward-compatible (optional param defaults to active).

## Scope Boundaries
- In scope: crystallizer.py (_emit_policy_twin + create_checkpoint) and persistence_system.py
  (record) + a facade regression.
- Out of scope: the auto-checkpoint / activation emissions (already correct); other bugs.

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-158 against current source (policy twin routed to active, not target).
- [x] Add optional profile_name routing to PersistenceSystem.record.
- [x] Forward profile_name through _emit_policy_twin; pass the target from create_checkpoint.
- [x] Confirm activation and auto-cadence seals keep active-profile behavior (None default).
- [x] Add a facade regression (inactive 'named' profile checkpoint keeps default untouched).
- [ ] User runs the crystallizer suite on 3.14t and accepts.

## Acceptance Criteria
- create_checkpoint(profile_name=X) makes X self-describing (non-empty policy-twin window) and
  leaves the active profile's emission sequence unchanged; the crystallizer suite is green on 3.14t.

## Validation / Test Plan
- Re-verified against current source; py_compile OK on both changed modules.
- Facade regression added (test_crystallizer_profile_facades.py) reproducing the audit scenario:
  default active + inactive 'named', checkpoint 'named', assert named window non-empty/valid and
  describe_profile('default') unchanged before/after.
- Full pytest Not run in-container: the facade boots the whole Aether/Nexus/Crystallizer stack,
  which needs 3.14t. Agent test-run status: Not run under pytest; the user runs the suite on 3.14t.

## Risks / Mitigations
- Risk: record() signature change ripples to other callers. Mitigation: profile_name is optional
  and defaults to the prior active-profile behavior; existing callers are unaffected.
- Risk: recording into a non-active profile could surprise. Mitigation: it is explicit and only
  used by the profile-scoped seal path; the audit's expected behavior.

## Applicable Anti-Patterns
- [x] Reproduced/verified against source before fixing.
- [x] Root-cause (route to target), not a defensive guard.
- [ ] No closure before the user's suite run.

## Decision Log
- DATETIME: 2026-07-18T15:58:33Z
  TYPE: DECISION
  CLAIM: Fix by threading an optional profile_name through record + _emit_policy_twin (default active) rather than snapshotting/swapping the active profile around the seal, which would be racy and mutate global emission state.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
BUG-158 fixed: the policy twin now records into the profile being checkpointed (optional
profile_name routing on record + _emit_policy_twin), so a named checkpoint is self-describing and
the active profile is untouched. Status review, pending the user's 3.14t suite run.
