# Bootstrap Design Detail — Crystal-Twin Snapshots + restore_aether (full context)

## Metadata
- Artifact ID: ART-2026-07-03-bootstrap-design-detail
- Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Parent: EPIC-2026-07-02-agent-object-persistence-loop
- Status: active ; Agent: crystal_0 ; Created: 2026-07-03
- Companions: first-cut design detail, the program code-map/proof-ledger, and the loop philosophy.

## Purpose
The restore layer: snapshot + restore a WHOLE running Aether from a small manifest. Structure-first;
instances re-meld. Sits ABOVE the first cut (consumes crystals) and RIDES the persistence epic (store/load).

## Crystal-twin family (B1)
- A crystal per structural unit, mirroring the runtime OWNERSHIP TREE:
  AethericCrystal (root/system) composes AethericFrameCrystal(s) compose ConduitCrystal(s) compose
  SpellCrystal(s) (+ the module/synthetic crystals underneath).
- Each is a PURE-DATA serializable MIRROR ("twin") - no behavior, no live instances, no locks.
- SpellCrystal already IS the spell/module twin (spell_crystal.py); `describe()` (1375) is basically
  the twin-emit today. The new siblings extend that pattern UPWARD.
- Symmetric per type: `to_crystal()` (emit twin from live object) + `restore()` (rebuild live from twin).

## snapshot_aether / restore_aether (B2, B3) - symmetric pair
- `snapshot_aether("name")`: walk the LIVE tree top-down, emit the composed twin, hand to persistence.
- `restore_aether("name")` / `restore_aether("name", version=<callsign>)`: walk the STORED twin, rebuild
  the live tree in DEPENDENCY ORDER: configs -> frames -> Nexus -> conduits (conjure) -> bindings -> links.
- Restore rebuilds STRUCTURE (the registration graph), NOT live instances - instances re-meld at runtime
  on demand. This is the mission's "save structure + explicit state, rebuild live runtime". A checkpoint
  is a save-state of the registration graph, not a memory dump of objects.
- Better name than initialize_system: restore_aether says exactly what it does; snapshot_aether mirrors it.

## Two inputs, one restore engine
- Same reconstruction path consumes EITHER an AUTHORED bootstrap file (hand-declared bindings + configs
  + topology, infra-as-code) OR a CHECKPOINT snapshot (the system captures ITSELF into the same manifest
  shape). Checkpoint just auto-generates the manifest from the live world.

## Snapshot-over-time = content-addressing (B4)
- Each AethericCrystal snapshot is content-addressed (callsign-style SHA) -> immutable, versioned,
  dedup'd checkpoint HISTORY for free. restore_aether(name) = latest ; (name, version=<callsign>) = exact
  historical checkpoint. Proof: the callsign store probe (coexist/dedup/versioned, 3/3).

## Synth vs non-synth is a LEAF concern (B5)
- Only the module-crystals at the bottom differ: synth records callsign + source -> restore SEEDS via
  the loader (codegen lane only) ; non-synth records physical module refs OR bytecode/fileless
  (crystallizer_v3 "fileless truth") -> restore imports/execs. The whole UPPER tree is identical either way.

## Two capture modes (B6)
- (a) LIVE-PUSH: live objects push their twin into an ACTIVE snapshot as they change (incremental).
- (b) METHOD-WALK: snapshot_aether captures at a point in time. (Default is an OPEN QUESTION.)

## Storage: file or DB
- Local file = self-contained bootstrap. DB = soft assignment + keys, so a kube container points at the
  DB and restore_aether pulls the whole world. Both ride the persistence adapter (the single db-write +
  load seam = persistence epic C6/P4).

## Alignment
- Realizes parent M3 (the loader chain bootstrap_manifest -> crystal_loader -> synthetic_module_loader
  -> bootstrap_loader) and generalizes V2's "conduit snapshots as the primary reload unit" to a full
  Aether tree. restore_aether = the bootstrap_loader realized; checkpoint = the snapshot side.

## Ownership hierarchy in code (for the walk)
- Aether hosts frames + Nexus + Crystallizer + MR. Conduits are created by conjure (SpellbookCreationSystem).
  Spells are bound into spellbooks/frames (spellbook.bind 4229). The twin walk mirrors this tree.

## Open questions
- Capture-mode default (live-push vs method-walk). Restore atomicity (all-or-nothing vs partial/resumable).
- Where twin-emit lives (`to_crystal()` on each live type vs a visitor in crystallizer).

## The onion / bootstrap paradox — resolved (the snapshot FLATTENS the onion)
Concern: to capture, crystallizer reads FRAME config (derive-mode-from-frame) - so must you configure
the frame/spellbook BEFORE crystallizer? And crystallizer has its OWN config too. The dependency runs
in OPPOSITE directions for the two paths:

- FORWARD (build fresh / capture): configure Aether -> frame -> spellbook -> conjure -> bind; crystallizer
  captures as you go, reading the frame's mode at bind. Onion OUTSIDE-IN. This is how a snapshot is MADE.
- RESTORE (use the bootstrap): the snapshot IS the whole onion FLATTENED into a manifest - the
  AethericCrystal twin tree CONTAINS every config (frame config incl. rift_enabled/ai_native/system_state,
  spellbook config, conduit config, spell perms, AND the Nexus/MR state, since Aether hosts them).
  So crystallizer does NOT need frames to pre-exist - it CREATES them from the twin data. Onion INSIDE-OUT.

=> To RESTORE you hand-configure exactly ONE thing: Crystallizer's own config (store/DB location,
   user_source_root_paths, remove_inactive_synthmodules) + the bootstrap name. That is the irreducible
   SEED (a bootloader). Everything else lives IN the manifest and is restored BY crystallizer.

Restore order (dissolves the onion):
1. Configure + activate CRYSTALLIZER (its own config; point at the store). <- the ONLY hand-config.
2. crystallizer.restore_aether("name") reads the manifest.
3. If the snapshot is DYNAMIC: crystallizer first restores Nexus + MR from the manifest (honoring
   "synthetic => dynamic" from the activation rules).
4. Then creates FRAMES (with captured config/mode) -> SPELLBOOKS -> conjures CONDUITS -> BINDINGS -> LINKS.

Reconciliation: "crystallizer derives mode from the frame" is a FORWARD-path truth (frame exists ->
crystallizer reads it). On RESTORE crystallizer WRITES the frame (creates it with the captured mode).
Two phases, no contradiction. The kube container's job = configure crystallizer, point at the DB,
call restore_aether; the onion reassembles itself.

## EMIT / OBSERVER MODEL (owner direction) — the onion fully dissolved
Invert control: structural units EMIT to crystallizer (PUSH); crystallizer NEVER reaches in (no PULL).
Crystallizer = a passive EMISSION SINK / observer of the live object world.

- Enable crystallizer (store pointer + policy = the whole config). A sink is now listening.
- Each unit EMITS its own twin + lifecycle events when it comes into being / changes:
  - AethericFrame -> emits its config INCLUDING mode (rift_enabled/ai_native/system_state) at finalize.
  - Conduit -> emits its twin at conjure. Spellbook -> emits its config. Spell -> bind EMITS the SpellCrystal.
  - Links -> emit their edges. (MR already emits transaction data - existing V2 pattern; extend emit to ALL.)
- Crystallizer RECORDS the composed twin tree + persists it. It "just knows what's configured" because
  everything SELF-REPORTS. No ordering, no reach-in, no onion - a unit emits WHEN IT EXISTS; crystallizer
  only has to be listening.

Consequences:
- Bootstrap is OPEN-ENDED: any node is a unit -> restore_conduit(id) / restore_frame(name) /
  restore_aether(name) are the SAME operation at different subtrees of the twin tree.
- "derive mode from the frame" becomes "the frame EMITS its mode" (no pull). Per-frame perms ride the emit.
- bind reframed: bind EMITS the spell; crystallizer records/acts only if active; the emit is a cheap
  NO-OP when crystallizer is off -> bind stays byte-identical (the constraint we needed).
- crystallizer config stays MINIMAL (store + remove_inactive_synthmodules); it never needs topology
  in advance - the topology reports itself.

Seams to wire (emit-points): frame-config finalize ; conjure ; bind ; link (+ MR's existing emit).
This RESHAPES the epics: first-cut C5 (bind hook) -> "bind emits" ; bootstrap B6 (capture mode) ->
emit-primary / live-push ; bootstrap B1 (twin family) -> emit-produced. Method-walk snapshot becomes a
SECONDARY/reconciliation path, not the primary one.
