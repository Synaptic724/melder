# First-Cut Design Detail — Wire Crystallizer Into Melder (full context)

## Metadata
- Artifact ID: ART-2026-07-03-first-cut-design-detail
- Epic: EPIC-2026-07-03-wire-crystallizer-into-melder
- Parent: EPIC-2026-07-02-agent-object-persistence-loop
- Status: active ; Agent: crystal_0 ; Created: 2026-07-03
- Companions: 2026-07-02_agent_object_persistence_loop_philosophy.md (mechanism),
  2026-07-02_import_and_module_lifecycle_findings.md (evidence),
  2026-07-03_crystallizer_program_code_map_and_proof_ledger.md (code:line + probe ledger).

## Purpose
Everything needed to build the first cut from cold: wire crystallizer into melder, the
create_spell_crystal call path, the importlib seed/unseed actioning, the config knob, and bind
participation. Deliberately redundant for compaction survival.

## The frame (non-negotiable)
The machine is the `SyntheticModule` registry of live pre-existing world objects
(synthetic_module.py). The import protocol (finder at front of sys.meta_path + a Loader) is a
DOORWAY: our loader RETURNS the pre-existing object and delegates exec to it. We own our
registered names; importlib owns the rest. World-first; do not reason by analogy to normal Python.
Proof: numpy.__loader__ = SourceFileLoader (importlib's) while synthetics use OurLoader.

## Wiring reach (C1)
- Aether HOSTS Crystallizer: `aether.py:119` `self._crystallizer = Crystallizer(aether=self)`,
  same posture as Nexus, INDEPENDENT of Nexus.
- Spellbook reaches Aether (`Spellbook._aether`, spellbook.py:4342), so the reach path is
  bind -> Spellbook._aether -> ._crystallizer. Nothing new to plumb.

## create_spell_crystal call path (C2)
- crystallizer.py:301 `create_spell_crystal(spell)` is the ONLY crystal constructor; requires
  `activated`; builds `SpellCrystal(spell, user_source_root_paths=self._configuration.user_source_root_paths)`.
- It has ZERO callers today (grep). spellbook.py has ZERO `crystal` refs (grep). This is THE gap.
- The hook: inside `Spellbook.bind` (4229), after `new_spell = self._bind.bind(...)` (4331) and the
  local registration (`_lookup_spells`/`_spells`/`_register_owned_spell_id`, 4362-4364), gated on
  `crystallizer.activated`: call `create_spell_crystal(new_spell)` (+ seed). When crystallizer is
  OFF the bind path is byte-identical (gate skips) - satisfies "don't disturb bind when off".

## Seed / unseed actioning + timing (C3)
- SEED on activate/bind: register_in_import_registry (761) -> publish_to_sys_modules (723, BEFORE
  exec) -> execute_source (697). Publish-before-exec = cycle-safe (mirrors importlib).
- UNSEED on inactive/notch/deactivate: unpublish_from_sys_modules (741) or, deeper, cleanup (284).
- BRANCHES ON AUTHORITY: a PHYSICAL bind's module is already in sys.modules (importlib loaded it)
  -> crystal captures custody, NO seed. A SYNTHETIC/codegen bind -> seed via our loader. So
  `remove_inactive_synthmodules` scopes to SYNTHETIC modules only (physical aren't ours to remove).
- Three removal DEPTHS (proven): PUBLISHED -> UNPUBLISHED (drop sys.modules ref; captured refs still
  work - a ghost) -> CLEANED (clear namespace; even captured refs break). notch/inactive = UNPUBLISH
  (reversible, crystal retained); hard teardown = CLEANUP (clear namespace, del owned, logger last,
  clear linecache). Proof: G8 of the suite + captured-ref-survives-unpublish.

## The config knob (C4)
- `remove_inactive_synthmodules: bool` in crystallizer/configuration/crystallizer_configuration.py.
- Default FALSE = leave / insert-only (validated, lower hazard, content-addressed model). TRUE = remove.
- Only bites synthetic modules in the codegen lane.

## The activation footprint (R-E)
- Per activation, the crystal DOCUMENTS what it placed so it is exactly reversible:
  {callsign, created sys.modules keys, canonical alias, parent-package attrs set, file locations}.
- SpellCrystal already has `_module_to_path` (spell_crystal.py:148/1249) + reads sys.modules
  (905/1335) + describe() (1375) -> extend it with the callsign + created-keys footprint.
- Proof: footprint + insert-only probe 2/2.

## Content-addressed version store + alias (parent M8; adjacent)
- callsign `<canonical>__<hex12>` (identifier-safe; `@` breaks `import` statement). = content SHA256
  = module-version id = crystal's module-version SHA. Append-only; identical content DEDUPS; versions
  COEXIST (no collision).
- Canonical->active-callsign ALIAS (owner call: lives in the CRYSTALLIZER layer, not SpellIndex; a
  single crystal = one version, so the alias belongs to the Crystallizer/version-store level, and the
  finder READS it). `import svc` / `from svc import a` use canonical names; the SHA never appears in
  code. Version-pin (MR checkout) via `import <callsign>` or importlib.import_module(callsign).
- REMOVAL RELOCATED: not collision-driven teardown, but (a) repoint the alias on notch (invalidate
  the canonical sys.modules entry - the one bounded removal) + (b) evict COLD callsigns for memory
  (no live refs, safe boundary). Proof: callsign store 3/3, callsign-invisible 4/4.

## importlib is PLUGGED-IN, not reimplemented
- We are two hooks (finder + loader) inside importlib. Cycle handling, ImportError/ModuleNotFoundError,
  sys.modules, fromlist, relative imports are ALL importlib's - identical for synthetic + physical.
- Proof: importlib publishes to sys.modules BEFORE calling our exec_module; synthetic circular
  ImportError == physical (5/5 hybrid+mirror). CAVEAT: the manual `materialize` path replicates
  importlib's sequence ourselves -> a mirror we MAINTAIN (add an equivalence test, T-F7).

## Dependency taxonomy + two tiers (feeds crystal_analysis)
- WORLD-INTERNAL (we manage): synthetic->synthetic, synthetic->owned-physical, physical->synthetic.
- WORLD-EXTERNAL (importlib manages loading; we validate presence): ->site-package, ->stdlib.
- TWO SCOPES: load-time (top-level) = seed before exec + set load order + cycle handling ;
  deferred (in-method) = fire at CALL time, don't gate load, but gate call-time availability + unseed
  safety. A method built ONLY to break a cycle is a deferred edge kept OUT of load-order (else you
  recreate the cycle) but IN the reverse/unseed graph. Proof: G4 deferred 5/5, hybrid 5/5.
- `_classify_module_target` (spell_crystal ~950, PRIOR) already classifies authority; extend with
  SCOPE (load-time|deferred) + NAME-level from-import edges (`_extract_import_targets_from_ast` ~1088
  already returns the from-import map).

## External libraries
- Resolve FREE via importlib behind our finder; shared object (no dup). We track EDGES (name +
  site_package authority + best-effort version) for restore-time env validation; we NEVER own their
  code. A MISSING external -> ModuleNotFoundError at exec, and publish-before-exec leaves a
  HALF-PUBLISHED broken module -> restore must VALIDATE-BEFORE-ACTIVATE + ROLLBACK-ON-EXEC-FAILURE
  (unpublish+unregister). Proof: external-lib probe 5/5 (confirmed 3.14t).

## Physical -> synthetic (the hardest edge)
- Resolution free (global finder). Burden: SEED-BEFORE-IMPORT (finder installed + synth registered
  before the physical import fires; registered-only resolves lazily) -> must EAGER-SEED synth deps on
  activation since we don't control physical import timing. We CANNOT enumerate physical importers
  (importlib owns them) and a physical dep may be DEFERRED -> record physical->synthetic edges
  EXPLICITLY at analysis time; KEEP-RESIDENT while physical dependents are live. Proof: 4/4 + 4/4.

## from b import a
- Reaches INTO b: b must be exec'd (registered-only execs on demand); `a` resolves as attribute OR
  submodule (b must be a package). Two failures: b absent -> ModuleNotFoundError (seeding); `a` not
  in b -> ImportError "cannot import name" (CONTRACT - the impact-engine signal). Name-level edges.
  Relative `from . import a` needs __package__/__name__ (a bare codegen dict fails -> exec as a
  synthetic module w/ package context). Proof: G5 5/5.

## Introspection
- Physical-backed managed modules get getsource FREE (real __file__ on disk). Codegen-backed use
  `__file__="<synthetic:>"` (synthetic_module.py:277) which trips linecache's angle-bracket guard ->
  FIX B (loader get_source + non-`<>` __file__) or FIX C (seed linecache). Clear linecache on unseed.

## Concurrency (narrowed)
- importlib + module __dict__ + the import-driven path are ALREADY no-GIL-safe. Guard only OUR
  surface with RLocks: registry mutations, the manual materialize sequence, alias repoint, eviction.
  Add a no-GIL stress test (T-F6). Append-only + dedup make concurrent identical stores converge.

## Activation-gate / dependency model
- Nexus enable() requires an installed NexusConfiguration (nexus.py:540). Frame utilization
  (`_validate_target_frame_runtime_requirements` 2430): `rift_enabled=True` always for AR; CODEGEN
  additionally needs `ai_native_enabled=True` + `system_state==dynamic`; ai_native implies dynamic.
- SystemState (system_state.py): `automatic` (safe default) | `dynamic` (AI-native). Two values.
- Postures: automatic+rift_enabled (AR only, NO synth) ; automatic+ai_native (REJECTED) ;
  dynamic+rift_enabled+ai_native (codegen/synth unlocked).
- OWNER RULE: the CODEGEN LANE requires Crystallizer AND MR active. MR REQUIRES Nexus (dependency) +
  Crystallizer, and may be enabled ONLY under the codegen conditions. One-way: crystallizer standalone
  in automatic (physical/bytecode bootstrap) needs none of it; the codegen lane needs all three.
  Enforce in nexus.py:2430 (codegen path) + the MR enable path. Order: Crystallizer -> Nexus -> MR.

## Build order (C1-C6) + open questions
- C1 wiring map [done] ; C2 create_spell_crystal path ; C3 seed/unseed timing (authority-branched) ;
  C4 config knob (default FALSE) ; C5 bind participation (gated on activated) ; C6 name the single
  db-write + hydrate/load seam (design stub -> persistence epic).
- OPEN: alias placement (rec: dedicated version-store owned by Crystallizer) ; remove default (FALSE) ;
  does create_spell_crystal SEED or only capture custody (seed separate, per authority).

## Configuration Restrictions (the gate matrix)
Derived from HOW the flags are used in crystallizer.py + nexus.py this session. The config CLASSES
themselves (CrystallizerConfiguration, NexusConfiguration, AethericFrame/Spellbook frame config)
were NOT read - confirm exact field names / defaults / validation on the NEXT READ (listed below).

### CrystallizerConfiguration (crystallizer.py)
- Installed via `configure(config)` (229); CANNOT reconfigure while activated -> raises (252-254).
- `configuration.activated` must be True before `Crystallizer.activate()` -> else raises (283-285).
- `configuration.validate()` is called on activate (286); finalize / `frozen` pattern (as Nexus).
- `configuration.user_source_root_paths` -> consumed by create_spell_crystal (320).
- ADD (first cut, C4): `remove_inactive_synthmodules: bool` (default FALSE = leave / insert-only).

### NexusConfiguration (nexus.py)
- Must be installed BEFORE `enable()` -> else raises (564-565). `enable()` finalizes/freezes it (573-574).

### AethericFrame / Spellbook frame configuration (checked in nexus.py `_validate_target_frame_runtime_requirements` 2430)
- `rift_enabled: bool` -> required True for ANY AR/Rift attach (2463-2469).
- `ai_native_enabled: bool` -> required True for CODEGEN rift spaces (2471; rules 2444-2445).
- `system_state: SystemState {automatic | dynamic}` -> CODEGEN requires `dynamic` (2446-2447).
- HARD RESTRICTION: `ai_native_enabled` True => `system_state == dynamic`, else ValueError (2474-2478).

### The composed gate (what must be true for each capability)
- Crystallizer ACTIVE: CrystallizerConfiguration installed + `activated` + validated.
- Nexus ENABLED: NexusConfiguration installed (+ finalized on enable).
- AR/Rift on a frame: frame `rift_enabled=True`.
- CODEGEN / synthetic modules on a frame: `rift_enabled` + `ai_native_enabled` + `system_state=dynamic`.
- MR ENABLED: requires Nexus + Crystallizer + the codegen conditions above (MR requires Nexus).
- `automatic` posture: crystallizer STANDALONE (physical/bytecode bootstrap); NO synthetic, NO MR.

### NEXT READ (fresh session) to confirm exact fields/defaults/validation
- src/melder/crystallizer/configuration/crystallizer_configuration.py
- src/melder/nexus/configuration/nexus_configuration.py
- src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
- src/melder/aether/spellbook/configuration/spellbook_configuration.py

## Activation Rules (DEFINITIVE) — when Crystallizer / Bind / Nexus / MR turn on
Reconciles: automatic-can-coexist-with-Nexus; crystallizer-anytime-for-bootstrap; physical vs
synthetic bootstrap; synthetic requires dynamic.

### Four runtime modes
1. Plain Melder - nothing on (physical bind/conjure/meld; no custody/snapshots).
2. Crystallizer standalone - crystallizer active, frame `automatic`, no Nexus/MR. Custody +
   physical/bytecode bootstrap. Bind captures physical custody. NO synthetic modules.
3. Nexus AR (no codegen) - Nexus enabled, frame `automatic` + `rift_enabled`. Command/view only.
   No synthetic modules. Crystallizer optional (physical bootstrap if on).
4. Codegen lane ("synthetic-mod mode") - frame `dynamic` + `ai_native_enabled` + `rift_enabled`,
   Nexus enabled, Crystallizer active, MR active. Codegen produces synthetic modules; bind mints
   crystals; MR versions them. `remove_inactive_synthmodules` only bites here.

### Per-subsystem rules
- Crystallizer: activate ANYTIME (independent, no deps). OPTIONAL for standalone bootstrap; REQUIRED
  when the codegen lane is active.
- Bind participation: whenever `crystallizer.activated`, in ANY mode. Branches on authority - physical
  bind -> capture custody ; synthetic bind -> seed via loader (codegen lane only).
- Nexus: enable for AR. `automatic + rift_enabled` = command/view ; `dynamic + ai_native + rift_enabled`
  = codegen unlocked.
- MR: enable ONLY in the codegen lane; REQUIRES Nexus + Crystallizer + a `dynamic`+`ai_native` frame.
- Synthetic modules: exist ONLY in the codegen lane.

### Dependency DAG (one-way)
- Crystallizer <- nothing. Nexus <- nothing to enable (AR needs rift_enabled; codegen needs dynamic+ai_native).
- MR -> requires -> Nexus + Crystallizer + a codegen frame.
- Codegen lane -> requires -> Nexus + Crystallizer + MR + (dynamic+ai_native+rift_enabled).
- => enabling the codegen lane FORCES Crystallizer + MR on; enabling Crystallizer FORCES nothing.

### Bootstrap mode rule (content-determines-mode)
- PHYSICAL-only snapshot (source or bytecode/fileless) -> restorable in `automatic`, crystallizer
  standalone. No Nexus, no dynamic.
- Snapshot CONTAINS synthetic modules -> requires the CODEGEN LANE on restore (dynamic + Nexus +
  Crystallizer + MR), because live synthetic modules are dynamic-lane citizens and need MR to govern
  them. So: physical bootstrap = automatic ; synthetic bootstrap = dynamic.
- OPEN (defer): a read-only STATIC restore of synthetic modules in automatic (load, no mutation
  surface). Safe default for now: ANY synthetic content => dynamic.

### Activation order + enforcement
- Order: Crystallizer -> Nexus -> (frame config: rift_enabled/ai_native/system_state) -> MR.
- Enforce at: nexus.py:_validate_target_frame_runtime_requirements (2430) - extend to require
  crystallizer.activated + MR.activated on the codegen path ; the MR enable path (require
  Nexus+Crystallizer+dynamic+ai_native) ; crystallizer.activate (independent) ; bind (gated on
  crystallizer.activated, spellbook.py:4331/4364) ; restore_aether (snapshot content -> required mode).

## Where crystallizer confirms its mode: the AethericFrame (NOT the Spellbook)
- The mode/gate flags (rift_enabled, ai_native_enabled, system_state) are FRAME-level: nexus.py:2430
  reads `target_frame_configuration.{rift_enabled, ai_native_enabled, system_state}`. The Spellbook is
  only the BIND SURFACE - it knows its frame via `self._aetheric_frame_name` (spellbook.py:4338). So at
  bind, crystallizer resolves the spell's FRAME and reads THAT frame's config for the mode.
- TWO gate levels:
  - Subsystem-enabled (Aether singletons, GLOBAL): crystallizer.activated, Nexus enabled, MR enabled.
  - Per-FRAME mode (frame config, PER-LOCATION): automatic vs dynamic + ai_native + rift_enabled.
  Different frames in ONE Aether can be in DIFFERENT modes (frame A automatic/physical ; frame B
  dynamic/codegen). Enabled subsystems act PER-FRAME per that frame's mode. MR is "truly active" only
  for dynamic+ai_native frames (per-frame), even when globally enabled.
- The bind hook (conceptual): if crystallizer.activated: mode = frame_config_for(new_spell.frame) ;
  crystallizer.participate(new_spell, mode)  # physical=capture custody ; synthetic-seed only if the
  frame is in the codegen lane.

## Twin hierarchy == permission hierarchy (rationalize permissions BY LOCATION)
- AethericCrystal -> AethericFrameCrystal (frame config + MODE) -> ConduitCrystal (conduit config/perms)
  -> SpellCrystal (spell perms). Each twin captures ITS level's config/permissions.
- On restore, permissions are rationalized PER-LOCATION: the frame twin restores the mode, the conduit
  twin its perms, the spell twin its perms. Crystallizer reads mode from the FRAME level, conduit-scoped
  perms from the CONDUIT level, spell perms from the SPELL.
- Bootstrap GRANULARITY: conduit-scoped (ConduitCrystal + its spells = V2 primary reload unit) OR
  whole-Aether (AethericCrystal). Persistence stores the twins; restore only enables what each level's
  captured permissions allow ("persistence allows what can be used").

## Order-of-operations (what comes first)
- Crystallizer FIRST (base) - REQUIRED to get ANY custody/bootstrap/codegen feature.
- Then per-frame config sets the mode. Nexus enabled for AR frames. MR enabled for codegen frames.
- OPEN: whether a per-FRAME "crystallize" permission exists (a custody toggle per location, beyond the
  mode flags). rationalize-by-location hints yes; NOT evidenced yet - confirm when reading the frame
  config class (src/melder/aether/aetheric_frame/aetheric_frame_configuration.py).

## Nexus emission gating precedent (2026-07-04, evidence-backed) — the model for crystallizer emit
How the EXISTING nexus publish path decides whether to emit. This is the precedent to mirror (or
consciously diverge from) for the crystallizer emit.

- Emitter-side gate (the CALLER decides): spellbook/conduit check a cached boolean before every
  `self._nexus._publish_*` call: `if not self._nexus_publish_enabled: return`.
  EVIDENCE: spellbook.py:5006, 5033, 5053, 1121 ; conduit.py:728, 757, 781.
- Flag source is FRAME CONFIG, cached (not a live query): `_nexus_publish_enabled =
  frame_configuration is not None and frame_configuration.rift_enabled`
  (spellbook.py:_refresh_nexus_publish_enabled 4960-4964). The spellbook retains the frame-owned
  config object in `_aetheric_frame_configuration` (None at :443, bound at :4669) and reads
  `.rift_enabled` off it. Refreshed at conjure/bind; a None config reads as not-enabled.
- Receiver stays DUMB: nexus `_publish_frame_record` / `_publish_conduit_record` /
  `_publish_spell_record` / `_remove_spell_record` (nexus.py:979-1076) do NOT gate on `nexus._enabled`
  — they delegate straight to `_frame_descriptor_manager`. So the block is per-FRAME (rift_enabled),
  enforced at the emitter, NOT on the Nexus singleton's own enabled flag.
- Implication for crystallizer emit — two viable styles:
  (A) emitter-side cached flag like Nexus: host checks a cached crystallizer-enabled boolean before
      calling; the sink stays dumb; supports byte-identical-when-off if the check is cheap.
  (B) receiver-side no-op inside `crystallizer.emit()` (`if not activated: return`): centralizes the
      gate but always makes the call.
  Nexus proves style A; the sketched emit() was style B. DECISION pending (owner).
