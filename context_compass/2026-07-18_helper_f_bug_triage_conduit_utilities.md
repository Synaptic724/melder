# Full-context bug triage - conduit_binding_meld (remaining 22) + utilities_sync_ownership (47)

- Author: helper_f, 2026-07-18T20:05:00Z, on owner directive ("read the bugs and exclude
  shit that is pointless") after the BUG-072 reclassification.
- Method: ALL fourteen audit reports for both epics read in one context, cross-referenced
  against each other and against the architecture read during Stories 01-03 of the aether
  epic and Story 02 of this epic (conduit.py, conduit_ward.py, spellbook seams, creations,
  meld front doors, door compiler, counter_switch, load_gate, cleanable law).
- Verdicts: KEEP (fix; verify line refs against current source first, per standing task),
  VERIFY-FIRST (mechanism plausible but a named premise must be proven through the real
  architecture before any edit), RECLASSIFY-PROPOSED (evidence says not a defect; owner
  acceptance required per EXIT_GATE). Every verdict is provisional to the microcycle's
  re-verification at story start - this triage sets the ORDER and the TRAPS, it does not
  replace per-bug FACT notes.

## Headline findings from cross-report reading

1. THE AUDIT WAVES DISAGREE. The synchronization-residual appendix (BUG-263-265) is the
   only wave that read every synchronization primitive TOGETHER WITH its real callers, and
   it explicitly lists as "excluded documented/existing behavior": terminal CreationGate
   reopen + post-clean failures, per-gate drain timeout semantics, LoadGate cleanup/acquire,
   SafeGuard timeout reuse, SyncWeakRef hashing, and scheduler sentinel cleanup. Earlier,
   narrower waves filed exactly those behaviors as BUG-156, BUG-157, BUG-230, BUG-092,
   BUG-090, and BUG-091. Six findings are therefore INTERNALLY CONTESTED by the audit
   itself - the 250k-context wave agents could not see each other. All six are downgraded
   to VERIFY-FIRST / RECLASSIFY-PROPOSED below and none may be "fixed" without an owner
   ruling on which wave is right.
2. INJECTION IS FINE FOR ROLLBACK BUGS, FATAL FOR PREMISE BUGS. Refined law after BUG-072:
   a rollback/atomicity finding legitimately uses fault injection - rollback must be
   correct for ANY failure of a genuinely fallible step (IO, persistence, emission, risk
   registration). A finding is premise-invalid only when its repro BYPASSES architectural
   guards (direct private-seam invocation, hand-built collaborators, inputs the real path
   cannot deliver). Each verdict below tags which case applies.
3. FAMILY CONSOLIDATION. Many findings are one design defect wearing several bug ids.
   Fixing the family root first shrinks the list honestly: pool-lifecycle family
   (076 -> 008/009), snapshot/alias-detachment family (083/096/098/179 - one deep-detach
   pattern), activation-atomicity family (081/099/240/241 - one install-then-validate
   inversion), transfer-rollback family (180-187 + 010/186), teardown-vs-in-flight family
   (263/271/273 + contested 154/230 - the CounterSwitch/LoadGate retained-surface law).

## conduit_binding_meld - remaining 22

### Story 01 (BUG-008-012) - helper_f - all KEEP
- BUG-008 KEEP. Double cleanup returning a pooled lesser twice violates the Cleanable
  contract's own idempotence law (cleanup() MUST be idempotent - documented repo-wide).
  Public surface. Fix likely belongs partly in the 076 family base.
- BUG-009 KEEP. Same law, SpellSpace pool. Same family.
- BUG-010 KEEP (verify custody contract). Transfer with move_creations=False extracts
  disposables for rollback then neither restores nor disposes on success - a leak
  whichever way the flag is documented. Injection-free repro. Family: 180-187/186.
- BUG-011 KEEP. Cache transfer read/write/delete under three independent critical
  sections; newest-write loss confirmed with a deterministic pause. 3.14t law makes
  shared-utility TOCTOU first-class. Same file as 093 - fix together.
- BUG-012 KEEP. bind.py flattens the ordered disposal list into a frozenset; runtime
  runs exactly ONE method (first iterated). Hash-seed-dependent lifecycle is real.
  ALSO NOTE (not in audit): `_attempt_cleanup` returns after the FIRST attempt success
  OR failure, so the "ordered fallback" loop can never fall back - owner should rule
  on intended semantics (ordered-first-only vs try-until-success) before the fix.

### Story 03 (BUG-154-157) - helper_f - the contested-gate story
- BUG-154 VERIFY-FIRST (premise). The audit itself concedes managed spaces are
  "intentionally outside the ordinary registry", and reset_for_pool_unlocked documents
  caller-guaranteed thread confinement as REQUIRED. Permanent cleanup while another
  thread is mid-scope may be a caller-sequencing violation by design (CounterSwitch
  ruling family), OR the gate/drain machinery is supposed to hold teardown until scopes
  exit. Must trace the real gate-ticket path around scope entry before any fix; likely
  owner ruling.
- BUG-155 KEEP (verify vs current source). Constructor-rollback gap (gate registered
  before fallible steps, no unregister on failure) - BUG-002-class, injection-for-
  rollback acceptable. Note the gates were reworked by the mediator-strategies lane
  after 07-12; line refs may be stale.
- BUG-156 VERIFY-FIRST (contested). Residual wave accepts terminal-gate reopen behavior
  as documented; gates-pools wave calls it a bug. Terminal-absorbing IS the repo's own
  law elsewhere (LoadGate terminal-open). Re-read the CURRENT creation_gate (post
  ticket-first rework) and escalate the wave conflict to the owner with the source.
- BUG-157 RECLASSIFY-PROPOSED or 1-line fix. Residual wave: "per-gate drain timeout
  semantics" documented. Fix is a trivial min(interval, remaining) if the owner wants
  it; not worth a story slot otherwise. Low severity.

### Story 04 (BUG-110-113) - helper_f2 - triage handed over via mailbox
- BUG-110 KEEP (verify one thing). Bind commits maps before fallible registration/risk/
  research/persistence steps with no undo - BUG-004/005-class, and those were real.
  Injection acceptable IF at least one mid-bind step is genuinely fallible in production
  (persistence/risk emission almost certainly is) - confirm one real failure lane, then fix.
- BUG-111 KEEP. Parked spells are locally owned and dropped uncleaned - direct violation
  of the "we clean everything, deterministically" core law. No injection involved.
- BUG-112 VERIFY-FIRST (premise - BUG-072-pattern alert). Repro invokes PRIVATE
  `_apply_notch` directly with a foreign-index spell. The public notch path runs through
  the mediator notch strategy - if the public path already validates membership, this is
  a non-defensive internal seam working as designed -> reclassify. Only if the public
  path delivers a foreign spell is it real.
- BUG-113 VERIFY-FIRST (premise). A caller-constructed rogue SpellIndex must actually be
  deliverable through the PUBLIC add-to-index surface for this to count. If the real path
  resolves the target index from the registry, premise fails -> reclassify.

### Story 05 (BUG-175-179) - helper_f - all KEEP, strongest High cluster
- BUG-175 KEEP. Standalone grant destroyed by index unlink - provenance loss through
  public flows only, no injection. Real contract violation.
- BUG-176 KEEP. Publish-before-validate ghost subscription - BUG-004 commit-order class,
  public flows.
- BUG-177 KEEP - TOP PRIORITY of the epic's remainder. The ORDINARY two-member unlink
  self-corrupts and raises with zero fault injection. Highest-confidence finding in the
  whole set.
- BUG-178 KEEP (verify vocabulary). Audit quotes the documented policy vocabulary
  (block_all, inbound_only, outbound_only) against confirmed public flows. Read
  policies.py's docstrings first; if the vocabulary reads as quoted, enforcement gaps
  are real.
- BUG-179 KEEP (verify docstring). Snapshot "claims detached-copy semantics" - confirm
  the claim in source, then it's the snapshot/alias family (one deep-detach sweep with
  083/096/098).

### Story 06 (BUG-271-273) - helper_f2 - all KEEP
- BUG-271 KEEP. Bind cleanup del-posture breaks retained decorators/in-flight binds with
  raw AttributeError - EXACTLY the BUG-007/CounterSwitch family we already fixed under
  the retained-terminal-surface law; same medicine (retain surfaces, re-check cleaned,
  raise the documented RuntimeError).
- BUG-272 KEEP. is_alive()/get() two-step on SyncWeakRef leaks ReferenceError instead of
  the documented RuntimeError - single atomic resolve + translate. Small, real.
- BUG-273 KEEP. Spellbook cleanup doesn't serialize with admitted binds - teardown-vs-
  in-flight family; align with the admission/lock law rather than ad-hoc guards.

### Story 07 (BUG-270) - helper_f - KEEP
- BUG-270 KEEP. Status probe hardcodes the owner-conduit many store while the emitted
  creation lane deliberately registers in the innermost SpellSpace - reproduced through
  a REAL dynamic Spellbook end-to-end (the audit's best-verified finding methodically).
  Also fix the two focused tests the audit says preserve the mismatch.

## utilities_sync_ownership - 47

### Story 01 (BUG-074-077) - KEEP x4
- BUG-074 KEEP (verify docstring claims set semantics). Duplicate identities in a "set".
- BUG-075 KEEP (verify callback contract). Replacement path skips the documented
  removal-callback lane.
- BUG-076 KEEP - family ROOT for 008/009. Pool accepts release/acquire after terminal
  cleanup; violates check_cleaned law at the base class, and both conduit/spellspace
  pools inherit the hole. Fix here first, then 008/009 shrink.
- BUG-077 KEEP. Eagerly-evaluated fallback argument - two-line fix, real.

### Story 02 (BUG-078, 090-093) - the contested-sync story
- BUG-078 KEEP. Explicit one-to-one contract in source; claim/update break it. Real.
- BUG-090 RECLASSIFY-PROPOSED (contested + reachability). Residual wave excluded
  SyncWeakRef hashing as documented/existing after reading ALL callers; hash-instability
  only bites if something keys tables by the wrapper - verify no caller does, then
  propose exclude (or accept a cheap stable-hash-cache as hardening if owner wants).
- BUG-091 VERIFY-FIRST (contested). Scheduler sentinel drain excluded by the residual
  wave as documented; the 5s-straggler scenario is still uncomfortable for teardown
  hygiene. Owner ruling with both waves on the table.
- BUG-092 RECLASSIFY-PROPOSED (contested + dead mode). The audit ITSELF notes internal
  call sites construct one-shot guards, so the broken reusable mode has no production
  reach; residual wave excluded it. Either delete/forbid the reusable mode or fix it as
  hardening - owner call, not silent fixing.
- BUG-093 KEEP (verify the integrity contract wording). Validate decodability at load so
  the cold-cache regeneration lane runs; same file as BUG-011 - one caching_system pass.

### Story 03 (BUG-079-084) - KEEP x6 (configuration correctness cluster)
- BUG-079 KEEP. required-token gate admits None==None - classic, High, cheap.
- BUG-080 KEEP. First-bind posture copy omits two public fields - field-sweep fix + a
  completeness regression that iterates ALL posture fields so the next added field
  cannot silently drop.
- BUG-081 KEEP (family: activation-atomicity). Reconfigure-after-active swaps without
  activate/reject.
- BUG-082 KEEP. `..` traversal escapes the documented cache root - containment check.
- BUG-083 KEEP (family: snapshot/alias). Shallow-copied frozen metadata.
- BUG-084 KEEP. Property path bypasses fluent validation - converge validation in
  freeze/finalize.

### Story 04 (BUG-094-101) - KEEP x8 (ownership/immutability cluster)
- 094 KEEP (consumed-before-accepted ownership inversion). 095 KEEP (finalized ACL
  exposes live ruleset). 096 KEEP (crystal twins shallow-detach - snapshot/alias family;
  crystallizer files -> coordinate with helper_0's lane before editing). 097 KEEP
  (validation requires the handler streaming actually uses + honest bool typing).
  098 KEEP (frozen config live list alias). 099 KEEP (enable() installs before
  validating - BUG-278 validate-before-publish class we already fixed on Aether; same
  shape on Nexus). 100 KEEP (verify the one-shot contract wording first). 101 KEEP
  (freeze-before-validate makes rejected drafts unrecoverable).

### Story 05 (BUG-180-187) - KEEP x8, one coherent transfer-rollback campaign
All eight are the same discipline failure inside transfer_of_ownership.py: mutations
before guards, rollbacks that delete pre-existing state, side maps never updated
(_spell_ids, cluster shared_spells), child commits outside the transaction, intent
recorded before preflight. BUG-004/005 proved this class real in this codebase.
Injection-for-rollback is acceptable throughout. Plan as ONE story-level rework of the
transfer transaction (preflight-everything -> reversible detach -> commit-last), with
per-bug regression tests, rather than eight patches. Verify all line refs first - the
transfer file is large and may have moved since the snapshot.

### Story 06 (BUG-230-236) - restore/load cluster - COORDINATE with helper_0
- BUG-230 VERIFY-FIRST (contested). LoadGate cleanup/acquire excluded by the residual
  wave; mechanism (cleaned-yet-held) is nasty if real. Our own LoadGate reading: acquire
  re-checks under the condition, cleanup marks under the condition - the audited window
  needs re-verification against CURRENT source before belief.
- BUG-231/232/233/234 KEEP. Restore rollback abandoning root config, cleaning hosted
  Nexus/MutationResearch while Aether still points at them, and leaving replayed
  clusters registered - all-or-nothing replay is the engine's own documented contract.
  FILES ARE CRYSTALLIZER'S: DECISION note + helper_0 coordination required before edits.
- BUG-235 KEEP (verify one-shot contract). BUG-236 KEEP-cheap or defer (Low, diagnostic
  completeness only).

### Story 07 (BUG-237-242) - KEEP x6 (bootstrap/host-identity cluster)
- BUG-237 KEEP - HIGH VALUE. Spellbook._aether class-level snapshot defeats Aether's
  documented safe reinitialization; production rebootstrap is broken and the test
  fixtures MASK it (they patch the cache manually - our own conftest reading confirms
  this). Fix + un-mask the fixtures.
- BUG-238 KEEP (crystallizer host-identity on retry - coordinate with helper_0).
- BUG-239 KEEP (verify vs current spellbook ctor). Ghost identity on failed construction.
- BUG-240 KEEP (activation-atomicity family; utility mutations without rollback -
  touches the utility system we just hardened, so verify against OUR new code first).
- BUG-241 KEEP (crystallizer activation flag ordering - coordinate with helper_0).
- BUG-242 KEEP (verify preferred remedy). Conjure commits then passive publication
  raises; BUG-182's precedent suggests CONTAINMENT (commit stands, report the incident)
  over rollback - owner preference wanted before implementation.

### Story 08 (BUG-263-265) - KEEP x3 (the residual wave's own findings, caller-evidenced)
- BUG-263 KEEP. Controller cleanup vs in-flight lookup with a REACHABLE production
  interleave named (lineage facade + DevOps cleanup). Retained-surface/re-check law.
- BUG-264 KEEP. Missing set_running_or_notify_cancel - textbook Future state defect.
- BUG-265 KEEP. Cancelled empty phase reported as success - check-order fix.

## Tally

- KEEP: 60 of 69 (12 conduit/helper_f + 5 conduit/helper_f2 + 43 utilities), every one
  still subject to per-bug source re-verification at story start; ~7 of them carry a
  named VERIFY item inside the fix work; 8 touch crystallizer files and need helper_0
  coordination; ~20 collapse into 5 design families, which is where the real effort goes.
- VERIFY-FIRST (premise/contested - no edits before the named proof or ruling): 154,
  156, 230, 091, 112, 113.
- RECLASSIFY-PROPOSED (owner acceptance turns them into documented exclusions): 157,
  090, 092 - plus 072 already ruled this session.
- Contested-by-the-audit-itself, needing an explicit owner ruling on which wave is
  authoritative: 090, 091, 092, 156, 157, 230.

## Standing laws applied to everything above

1. Reachability law (BUG-072 lesson): premise proven through the real architecture path
   before any fix; direct private-seam repros are not evidence.
2. Injection distinction: injection to trigger a genuinely fallible step = valid rollback
   evidence; injection/bypass to DELIVER an impossible input = invalid premise.
3. Family-first: fix the design root (pool base, deep-detach, validate-before-publish,
   transfer transaction) and let member bugs become regression tests, not patches.
4. Cross-lane respect: crystallizer-file bugs coordinate with helper_0; Stories 04/06 of
   the conduit epic belong to helper_f2 and this triage is advisory to them.

## FINAL VERDICTS - source-verified sweep (2026-07-18T20:50:00Z, owner-directed)

The report-level triage above was then verified against LIVE SOURCE with callers. Changes:

STRIPPED (6, owner acceptance = this directive; evidence in source):
- BUG-090 EXCLUDED. `SyncWeakRef.__hash__`'s docstring DOCUMENTS the id-fallback by design
  ("Returns id(self) to keep the wrapper usable in sets/dicts"); the sole production user
  (spellbinder) holds one wrapper as an attribute, never as a table key. Documented
  behavior, zero reach.
- BUG-092 EXCLUDED. `one_time_use=False` has ZERO callers in src/ - the broken reusable
  mode is dead code. Candidate for mode deletion in a later hygiene pass.
- BUG-154 EXCLUDED. Managed scopes are intentionally outside the registry, thread
  confinement is a documented caller contract, and the owner's 2026-07-12 ruling (live in
  admit_ticket's docstring) declares teardown-vs-racing-use "lifecycle misuse, loud by
  contract". Cross-thread permanent-cleanup racing an active scope is that misuse class.
- BUG-156 EXCLUDED. Same owner ruling: post-terminal open()/close() pokes on a gate that
  production discards after terminal closure are lifecycle misuse; making terminal state
  absorbing would be defensive-guard sprawl against declared-loud misuse.
- BUG-157 EXCLUDED. Residual wave: interval-quantized drain timeout is documented
  semantics. Low. (A min(interval, remaining) one-liner remains available as a freebie.)
- BUG-091 EXCLUDED. Residual wave excluded scheduler sentinel drain as documented after
  reading all callers; stragglers are daemon workers (process-bounded). Owner may
  override.

UPGRADED TO KEEP after tracing (previously suspect):
- BUG-112 KEEP - REAL. The public path Conduit.notch_spell -> Spellbook._notch_spell
  passes the CALLER-supplied (spell_index, spell) pair to _apply_notch with no membership
  validation at any layer (mediator claims scopes, not membership). The audit's private-
  seam repro was lazy, but the public surface delivers the same unvalidated input. Fix:
  membership gate in _apply_notch (it is the model seam both paths share).
- BUG-113 KEEP - REAL. The ownership gate exists in source and validates the WRONG
  property (`selected_spell_id in _spell_ids` instead of registry identity of the index
  object). A real guard checking the wrong thing is a defect, not a premise problem.
- BUG-230 KEEP - REAL vs current source. acquire()'s cleaned check happens before the
  condition; cleanup's tombstones publish under it; an acquirer blocked on the condition
  during cleanup completes the hold on a cleaned gate. Fix: re-check `_cleaned` inside
  the condition (the wait_for_passage tombstone-re-check pattern already in the file).
- BUG-076 KEEP - REAL and worse than filed: acquire/release carry NO terminal handling,
  so post-cleanup use SILENTLY corrupts (resurrection) instead of failing loud - a direct
  violation of the loud-by-contract posture. Family root for 008/009.
- BUG-012 KEEP - confirmed: bind.py flattens configured disposal order into frozenset().
- BUG-077 KEEP - confirmed: eager nested-getattr fallback in IDBuilder.compose.
- BUG-178 KEEP - confirmed: Policies enum docstring states exactly the vocabulary the
  audit tested against (block_all / inbound_only / outbound_only direction rules).

FINAL COUNT: 63 KEEP / 6 STRIPPED (plus BUG-072 reclassified earlier this session).
Owner directive 2026-07-18: helper_f proceeds across ALL stories of both epics regardless
of prior agent partition; helper_f2 notified to sync before touching Stories 04/06.
