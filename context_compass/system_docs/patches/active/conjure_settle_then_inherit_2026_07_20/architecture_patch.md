# Architecture Patch: conjure settle-then-inherit (world-mode inheritance)

Lane: conjure_settle_then_inherit_2026_07_20. Owner-ruled 2026-07-20.

## Law
The conduit inherits the WORLD's (aetheric frame's) mode. Conjure stops
policing: the flag-vs-posture mismatch throw is DELETED. Conjure remains the
settlement point for unset configuration - on an UNSETTLED world (frame
posture still the unfrozen birth default), conjure(dynamic=True) SETTLES the
world dynamic through the canonical bind_frame_configuration lifecycle (first
bind freezes). On a SETTLED world (posture frozen/explicit - "set in the
configuration is also correct"), every conjure inherits; the flag is ignored;
dynamic-only operations (link/sever/transfer/upgrade/clusters) fail at their
OWN gates with their own errors, on purpose.

## Changes
1. Spellbook._settle_or_inherit_conjure_mode(dynamic) -> bool (new, before
   conjure): settlement on unfrozen posture + dynamic ask; else inherit;
   missing posture defers to check_system_state's honest refusal. conjure()
   threads the EFFECTIVE mode down the whole chain (creation system _dynamic,
   blueprint dynamic_mode/automatic_mode where the conduit's state is born,
   _conjure_dynamic_hint, crystallizer config-discipline guard, cloud
   registration).
2. check_system_state: automatic-mismatch throw removed (structurally
   impossible - it receives effective mode); missing-posture refusal and the
   non-dynamic policy gate RETAINED (real constraints, correctly owned).
3. Back-compat: every existing conjure(dynamic=True) callsite works - fresh
   worlds settle, postured worlds inherit harmlessly. Nexus/restore callsites
   land in the settled-world case (frames posture before books).
4. Tests: test_conjure_settle_or_inherit.py (4 rows: settle, plain-static +
   own-gate failure, frozen-automatic ignores flag + own-gate failure,
   frozen-dynamic plain-conjure inherits). UX: _dynamic_world helper collapses
   to a plain book (no private seams); refusal probe flipped to settlement.

## Rollback
Restore the check_system_state block + drop the helper; probes flip back.
