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

## MEASURE - 2026-07-20 01:36 UTC - owner run exposed call-time NameError (FIXED)
Owner component-test run died at spellbook.py:6006: NameError AethericFrameConfiguration
inside _settle_or_inherit_conjure_mode (plain conjure on an unconfigured world - the
settlement path constructs the class at runtime). Root cause: the class was imported
ONLY under `if TYPE_CHECKING:` - my grep import check matched that type-only line, and
compile() cannot catch a NameError that resolves at call time.
FIX (EVIDENCE spellbook.py:19-21): module-level runtime import of
AethericFrameConfiguration added beside the SystemState import; the redundant
TYPE_CHECKING duplicate (old :51) DELETED so grep matches exactly one truth.
Cycle-safe: aetheric_frame_configuration.py imports guard/system_state/cleanable/
crystallizer/aetheric_frame_crystal/helpers/safeguard - none execute spellbook.py.
compile green, CRLF preserved. LESSON: import checks must distinguish runtime blocks
from TYPE_CHECKING blocks; any helper that CONSTRUCTS a class needs a runtime import.
Status: awaiting owner rerun (component tests + test_conjure_settle_or_inherit.py + full suite).

## MEASURE - 2026-07-20 01:44 UTC - owner run 2 exposed flag bulldozing in the settle path (FIXED)
15 component reds (conduit transactions, conduit cloud, spellbook post-conjure gates): every
disable_* flag staged on the UNFROZEN retained posture before conjure stopped firing -
DID NOT RAISE "disabled", or execution ran past the dead gate into deeper errors.
Root cause (EVIDENCE aetheric_frame.py:645-698): bind_frame_configuration's unfrozen branch
copies ALL attempted values over the canonical posture when handed a DIFFERENT object. My
settlement constructed a FRESH AethericFrameConfiguration carrying only mode/ai_native/rift,
so its default-False disable flags bulldozed the staged truth at freeze time.
FIX (EVIDENCE spellbook.py:6004-6017): settle the RETAINED frame-owned posture object ITSELF -
with_system_state(dynamic) in place when needed, then rebind the SAME object; same-object bind
skips the copy branch and goes straight to freeze, preserving every staged flag. This is
exactly how the pre-change settle point (_bind_aetheric_frame_configuration_to_aether,
spellbook.py:5647) always worked. The fresh-object constructor call is GONE, so the earlier
NameError class of failure is structurally impossible now. Downstream same-object rebind on
the frozen posture lands in the idempotent matches branch - no double-freeze hazard.
compile green, CRLF preserved. LESSON: settlement must never mint a parallel posture object;
the canonical object is the only safe carrier of pre-conjure staged state.
Status: awaiting owner rerun (the 15 reds + test_conjure_settle_or_inherit.py + full suite).

## MEASURE - 2026-07-20 01:59 UTC - stale old-law tests updated to the settled law (8 rows, 3 files)
Owner full-suite run after both fixes left exactly 8 reds - none regressions; ALL assert the
OLD law (the deleted mismatch police, or flag-forces-static on a dynamic world).
Updates, all law-faithful:
1. tests/unit/melder/spellbook/test_spellbook.py: the two direct mismatch-throw tests are now
   test_check_system_state_trusts_effective_dynamic_default_policy and
   test_check_system_state_dynamic_mode_admits_dynamic_policies (no-raise: the gate receives
   the EFFECTIVE mode); check_system_state matrix rows with automatic=False (= effective
   dynamic) flip expect_raises True->False - dynamic mode admits every policy.
2. tests/integration/.../test_spellbook_integration_public_errors.py: dynamic-only-policy
   refusal now runs on an AUTOMATIC world (on a dynamic world the conduit inherits dynamic
   and the policy is legal); the old dynamic-in-automatic refusal test was the SETTLEMENT
   case - rewritten as test_spellbook_conjure_dynamic_flag_cannot_override_settled_automatic_world
   (frozen automatic posture + dynamic=True + whitelist_all -> policy refusal proves inherit).
3. tests/integration/.../test_spell_index_op_guards.py: new _make_automatic_spellbook helper;
   the three A8 non-dynamic guard tests build on it (on the old dynamic world they either
   went red or passed for the WRONG reason - dynamic conduit, different guard firing).
INCIDENT, owned: my first edit pass on the public-errors file used a broken line matcher
(searched the pristine list while mutating a copy - matches landed shifted) and mangled the
file; the owner caught it mid-repair and the mangle got committed in 2fac50956. Worktree
repaired by full-region rewrite; sanity sweep (ast parse + stray/dup counts) now clean.
LESSON: edit scripts must search and mutate the SAME buffer; always ast-parse test files
post-edit, not just py_compile the happy path.
Status: awaiting owner rerun (the 8 + full suite). HEAD carries the mangled copy - next
commit of the repaired worktree supersedes it.
