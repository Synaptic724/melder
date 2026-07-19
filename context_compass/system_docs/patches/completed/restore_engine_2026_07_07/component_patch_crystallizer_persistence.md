# Component Patch: crystallizer.persistence (restore_engine_2026_07_07)

## Metadata
- Patch ID: restore_engine_2026_07_07
- Component: src/melder/crystallizer/persistence/**
- Owner ticket: tickets/stories/2026-07-07_restore_engine_load_checkpoint_story.md
- Created: 2026-07-07T03:05:00Z

## Before / After Behavior

### PersistenceSystem.load_checkpoint
- BEFORE: validates the checkpoint id under lock, raises NotImplementedError.
- AFTER: validates the id under lock, resolves the target crystal's profile
  chain (all ledger crystals with the same profile_name and checkpoint_number
  <= target's, creation order), constructs one single-use RestoreEngine OUTSIDE
  the lock (replay drives public verbs that take their own locks; holding the
  system lock across replay would deadlock the emit path re-entering
  record(...)), delegates, returns None (facade returns the report).

### Crystallizer.load_checkpoint (facade)
- BEFORE: delegates and propagates NotImplementedError.
- AFTER: delegates to a new PersistenceSystem.restore_checkpoint(checkpoint_id)
  -> Dict (detached RestoreReport.describe()); keeps load_checkpoint name as
  the public verb. Activation still required (facade gate unchanged).

### SpellCrystal (capture-gap fields, additive)
- BEFORE: no disposal_method_names; no profile family.
- AFTER: `_disposal_method_names: List[str]` (sorted copy of the live spell's
  frozenset at emission) and `_profile_family: str` ("detailed" iff the
  attached profile object's type name is "SpellDetailedProfile", else
  "general"). Surfaced as properties + describe() keys
  `disposal_method_names` / `profile_family`; cleanup() dels extended.
  Rehydration tolerance: readers use .get(...) with [] / "general" defaults so
  pre-patch cached checkpoints keep restoring (absence noted as a shortfall).

### PersistenceProfile.capture_segment_since (third capture-gap fix)
- BEFORE: spell_crystal capture used the generic twin path - the payload
  carried NO custody-location signal, so staged members that never flipped
  (bind_inactive-born) were indistinguishable from actives in a checkpoint.
- AFTER: the spell_crystal branch annotates the detached payload with
  `custody_location` ("active"/"inactive") read from the live location maps
  at capture time. Fold routes on it; unannotated (pre-patch) payloads
  default active, matching their era's behavior.

### Replay-order correction (self-review round, 2026-07-07T04:40Z)
- The engine finalizes each rebuilt SpellbookConfiguration BEFORE any bind
  (the conjure configuration-discipline guard refuses recorded-lane worlds
  whose binds ran against a mutable configuration), binds actives
  PRE-conjure (bind self-admits; no explicit spellbook window needed),
  conjures, then stages members POST-conjure through Conduit.bind_inactive.

### RestoreEngine (NEW: restore_engine.py)
- Cleanable; __slots__ = Cleanable.__slots__ + owned fields; cleanup()
  DIRECTLY after __init__ (owner law); single-use (`restore()` raises on
  reuse); no module-level state (types + pure helpers only).
- Owned state: borrowed persistence-system reference (non-owning), fold maps,
  identity translation dict, built-unit stack (for rollback), report.
- Verbs:
  - restore(chain) -> RestoreReport: fold -> replay stages 1-9 -> report.
  - _fold_chain: per (kind, key) later-wins; tombstone kinds delete their
    targets (spellbook_removed sweeps by recorded parent edge; frame_removed
    sweeps frame-keyed kinds; contract/cluster/index/spell removals delete
    one key); spell_activity folds into the custody location decision.
  - _replay_* stage methods, each appending (unit, undo) onto the built stack.
  - _teardown_built: reverse-order cleanup of everything built; called from
    the except path; re-raises the original error (all-or-nothing).
- Failure semantics: first stage error -> teardown -> raise RuntimeError
  chaining the cause, message names the failed stage + last good stage.

### Chain-integrity verb + retention-safe numbering (task
### 2026-07-07_checkpoint_chain_integrity_verb_task, same patch lane)
- NEW read-only verb PersistenceSystem.verify_checkpoint_chain(profile_name
  =None -> active) + Crystallizer facade passthrough. Detached report:
  ledger bounds, dropped_prefix_count, empty_windows, break evidence rows
  (duplicate_checkpoint_number / checkpoint_number_gap /
  window_discontinuity / inverted_window), verdict intact |
  truncated_prefix | broken | empty. Full-dropout restarts are caught by
  the first retained window starting past sequence 1.
- BUG FIX (latent, found by the verb's duplicate check):
  _next_checkpoint_number minted numbers from the retained COUNT, which
  duplicates once FIFO dropout engages; now mints from the highest
  retained number + 1 (monotonic under retention).

### Owner-run triage #2 (2026-07-07): CAPTURE GAP #4 + contract direction
- PRODUCTION BUG (found by the round-trip suite; audit correction): the
  SpellbookCrystal NEVER emitted in any legal recorded world. The twin's
  only emission lives in SpellbookConfiguration.freeze(origin...), which
  early-returned for frozen configs - while the dynamic-mode bind guard
  FORCES configs frozen before the first bind, and the spellbook's
  conjure freeze short-circuited frozen configs without calling freeze.
  Net: finalize-first (the only legal bind lane) recorded no book twin;
  restores folded empty worlds and reported "complete" with zero builds.
  FIX both sides: freeze() now routes emission through
  _emit_spellbook_twin_when_recording on BOTH paths (fresh freeze +
  origin-carrying re-freeze), and _validate_and_freeze_configuration
  re-enters freeze with origin identity for pre-frozen configs. Emission
  fires exactly once per book (conjure is once-per-book).
- ENGINE FIX (contract direction): ward record truth is that a plain
  detail lives in the map of the side OWNING the lineage ("initiated"
  via link-time _grant; "received" via the borrow verb, which files
  under the owner per _check_spell_if_eligible). The live verb is
  borrower-called naming the owner. _replay_contracts now replays EVERY
  detail as borrower.add_spell_to_contract(conduit=owner) in a borrower-
  opened link window (was: initiated-only, owner-called - backwards).
  Label drift tolerance: replayed details re-record as "received".
- ENGINE FIX (config tolerance): replay loads the default property
  dictionary BEFORE overlaying recorded values, so pre-patch/lossy
  windows finalize on documented defaults instead of failing on missing
  required properties.
- TEST FIX: the round-trip contract test's record lane called the borrow
  verb owner-side; corrected to borrower-called.

### Owner-run triage #3 (2026-07-07): frames stage (REPLAY gap, not capture)
- The record was fine: AethericFrameCrystal captures the FULL frame posture
  (system_state/rift/ai_native + the describe_posture dev-ops surface) at
  the frame-configuration freeze with origin identity. The ENGINE folded
  "frame" twins and never replayed them - rebuilt frames kept the fresh-
  boot automatic default posture, and conjure's check_system_state (which
  reads the FRAME configuration, not the book's) refused every dynamic
  conjure.
- FIX: new stage 2 "frames" between aether_configuration and
  books_and_binds. _replay_frames builds the attempted posture from the
  twin payload (constructor-default fallbacks per key) and applies it via
  AethericFrame.bind_frame_configuration - the frame copies values into
  its own unfrozen default posture and freezes WITH origin identity, so
  the frame twin re-emits (rebuilt worlds re-record their frames).
  Fresh-boot idempotence and frozen-conflict tolerance ride the frame's
  own bind contract.
- Missing-twin fallback (pre-frame-emission windows): books on an
  unpostured frame posture it dynamic with ai_native/rift hints from the
  book's recorded configuration payload + a
  frame_twin_missing_postured_dynamic_from_book_hints shortfall (the
  record's hard gate only seals dynamic worlds).
- Seam note: engine uses Aether()._ensure_frame (documented deliberate
  private seam, same class as frame._conduit_cloud; public accessor
  follow-up tracked in the story).

### Owner correction (2026-07-07): RELOAD lanes, not defaults lanes
- Owner ruling: restore must NEVER rebuild configurations through the
  defaults/authoring lane - present-day defaults drift, and a defaults-
  first rebuild silently rewrites sealed history. Every configuration the
  engine rebuilds now has a dedicated RELOAD verb whose contract is:
  recorded values are the truth, backfill is explicit and per-key
  reported, nothing substitutes silently.
- NEW SpellbookConfiguration.load_recorded_dictionary(recorded) ->
  {"rejected": ["key: reason", ...], "backfilled": [key, ...]}: recorded
  keys route through set_property (registration + type checks); refusals
  (unknown keys, stringified-lossy values) come back as rejected;
  required keys the record lacks backfill via load_default_dictionary's
  populate-missing-only semantics and come back as backfilled.
- NEW AethericFrameConfiguration.from_recorded_posture(twin_payload) ->
  (unfrozen posture, missing_keys): system_state_name HARD-REQUIRED (the
  reload lane never guesses a frame state); every other absent key falls
  to the constructor default AND is returned for reporting.
- ENGINE rewired: books use load_recorded_dictionary (shortfalls
  config_property_not_replayable / config_property_backfilled_schema_
  default per key); frames stage uses from_recorded_posture (shortfall
  posture_key_backfilled_schema_default per key); _posture_frame reduced
  to bind-only; the missing-twin fallback remains an explicit AUTHORING
  construction (there is no record to reload) with its single tolerance
  shortfall. load_default_dictionary no longer appears in the engine.
- REFINEMENT (owner spec, post-green run): reload verbs LOAD AND FREEZE
  in one motion - a reloaded configuration/posture comes back SEALED
  (internal freeze, no origin identity, no twin emission; the spellbook
  conjure / frame bind freeze re-entries carry identity and emit). The
  engine's separate finalize call is gone; input payloads are documented
  as the JSON-safe cached-item shapes. Reload-lane unit tests updated to
  the sealed-on-return contract (6 tests).

### Owner directive (2026-07-07): reload lanes for ALL configs + the
### crystallizer's own twin
- EVERY configuration now carries a JSON-based load-and-freeze reload
  verb (MR excluded as too new): SpellbookConfiguration.
  load_recorded_dictionary + AethericFrameConfiguration.
  from_recorded_posture (prior sections) PLUS NEW AetherConfiguration.
  from_recorded_payload (knob reloads; callable presence flags report as
  code_participation; frozen-not-activated on return),
  NexusConfiguration.load_recorded_dictionary (defaults floor + recorded
  overwrite; enum member NAMES and collection lists convert back via
  _coerce_recorded_value; seals WITHOUT the enable emission), and
  CrystallizerConfiguration.load_recorded_dictionary (with_defaults floor
  + recorded overwrite; list->tuple source roots; plain seal).
- NEXUS record fidelity + emission seam: freeze's twin emission extracted
  to emit_configured_twin_when_recording (enum->name, collections->list
  branches added - tuples/enums no longer stringify lossily);
  Nexus.enable calls the seam for PRE-FROZEN (reloaded) configurations -
  same fix class as the spellbook conjure re-freeze.
- NEW CrystallizerCrystal twin (root-singleton semantics, journal kind
  "crystallizer", key "root"): self-emitted by Crystallizer.activate from
  the frozen configuration (scalar filter incl. collection form). Profile
  carries slot/record-branch/_resolve_twin route/cleanup; capture rides
  the generic twin path. The ENGINE folds it and reports
  crystallizer_policy_recorded_reload_is_boot_time_act (the live
  crystallizer driving a restore never swaps its own policy; boot code
  reloads it pre-activation).
- ENGINE stage 1 rewired to AetherConfiguration.from_recorded_payload +
  LATENT FIX: Aether.activate requires an ACTIVATED configuration; the
  engine now calls configuration.activate() (the emission moment) first -
  the old manual lane would have raised (masked: stage 1 never ran in the
  green suite's worlds).
- Follow-up flagged: a boot orchestration verb that reads the cache and
  reloads the crystallizer configuration before activation (kit/boot
  lane).

### Whole-system restore + canonical order (2026-07-07, owner directives)
- NEXUS RESTORE (stage): the nexus twin recorded but never replayed, and
  nexus_state fell through the fold silently. NEW fold branches (nexus /
  nexus_state later-wins / mutation_research+state stores) + engine stage
  _replay_nexus: config rebuilds via
  NexusConfiguration.load_recorded_dictionary (per-key shortfalls),
  enables via the public verb (pre-frozen emission seam re-records),
  final "disabled" replays enable-then-disable, final "cleaned" skips
  with report; rides _built_stack for all-or-nothing teardown.
  Integration test: nexus round trip across the boot boundary.
- AETHER ROOT CATCH-UP: the aether twin emitted only at
  AetherConfiguration.activate, which structurally precedes crystallizer
  activation (the aether hosts it) - normal boots never recorded the
  root (stage 1 never fired in green runs). Emission extracted to
  AetherConfiguration.emit_configured_twin_when_recording;
  Crystallizer.activate performs a targeted root catch-up emission once
  recording is live (single root emission, NOT a world walk). The
  utility system regenerates transitively: stage 1's Aether.activate
  runs _apply_configuration_to_utility_system. FOLLOW-UP: audit
  AetherUtilitySystem for configured surface beyond the aether config.
- CANONICAL ORDER (owner ruling): restore stages now mirror the boot
  order Aether|AetherUtilitySystem -> Crystallizer -> MR -> Nexus ->
  AethericFrame -> Spellbook -> Conduit|Ward. crystallizer_policy became
  its own report stage (extracted from the aether stage);
  mutation_research became an ordered honest-report stage (fold-time
  shortfalls moved to stores + stage). Every recorded kind folds to a
  build, a report, or a tombstone - nothing silent.

## State / Failure Deltas
- No new persistent state anywhere; the engine is transient.
- New error surface: RuntimeError("restore failed at stage ...") chaining the
  stage exception; KeyError for unknown checkpoint id (unchanged).

## Dependency / Ordering Notes
- Engine imports runtime types lazily INSIDE methods (Spellbook, Existence,
  Permissions enums) to respect the package-root import chain (3.14t-only
  runtime; compileall floor in the 3.10 sandbox).
- Contract re-grant runs inside `with conduit.transaction("link", ...)`
  windows (removal-family verbs REQUIRE an active window; adds self-admit).

## Validation Expectations
- Unit (tests/unit/melder/crystallizer/persistence/test_restore_engine.py):
  fold later-wins + tombstones; translation-map hygiene; shortfall
  classification (hook / replay_required / synthetic / lossy-config /
  pre-patch-absence); report shape; single-use + cleanup idempotence.
- Integration (tests/integration/melder/crystallizer/
  test_crystallizer_restore_integration.py): full seal -> Aether reset ->
  reload_cached_checkpoint -> load_checkpoint round trip (binds, staged+notch,
  links, contracts, clusters); injected mid-replay failure -> rollback leaves
  no frames/conduits behind.
- All "Not run." in-session; owner runs 3.14t.
