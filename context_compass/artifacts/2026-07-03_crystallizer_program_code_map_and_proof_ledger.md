# Crystallizer Program — Code Map & Proof Ledger (retrace reference)

## Metadata
- Artifact ID: ART-2026-07-03-crystallizer-program-code-map-and-proof-ledger
- Grounds: EPIC-2026-07-02-agent-object-persistence-loop (parent) and its 3 children:
  EPIC-2026-07-03-wire-crystallizer-into-melder (first cut),
  EPIC-2026-07-03-crystallizer-bootstrap-checkpoint (phase 2),
  EPIC-2026-07-03-crystallizer-persistence (phase 3).
- Status: active
- Agent Name: crystal_0
- Created: __TS__
- Purpose: enough file:line:symbol detail + probe/result ledger that an agent can retrace
  EVERY claim by reading the code at these locations and RE-RUNNING the listed probes.
  Line numbers are from reads this session (CPython 3.10 sandbox; runtime target 3.14t);
  a few marked (PRIOR) are from an earlier read - reconfirm the symbol, not necessarily the line.

## THIS IS WORLD-FIRST — read before anything else
This is NOT "using importlib" or a normal Python module trick. It is a world-first runtime: a
MANAGED LIVE-OBJECT MODULE WORLD where modules are pre-existing world objects SERVED to the import
protocol (finder + loader = a DOORWAY; our registry is the ENGINE). The code says so itself -
synthetic_module.py's class docstring calls SyntheticModule "the world-first runtime embodiment of
one managed software unit". What makes it world-first, concretely:
- modules are pre-existing managed objects the loader RETURNS (inversion), not created by the import system;
- REMOVAL/unseed exists - importlib NEVER removes, it caches forever; removal is OUR novel, hazardous surface;
- content-addressed callsign versioning + a canonical->active alias give COEXISTING versions + checkpoint history;
- seed/unseed tied to spell state, deterministic no-GIL cleanup, and whole-Aether snapshot/restore.
Do NOT reason about this by analogy to normal Python import behavior - you will get it wrong. Read the
"frame" sections of the design docs, then this ledger.

## How to retrace
1. Read the Code Map locations below (they are the ground truth).
2. Re-run each probe in the Proof Ledger; expect the stated result.
3. Cross-check the per-epic grounding: each requirement points at code + a probe.

## 1. CODE MAP (file : line : symbol -> what it is ; BUILT | GAP)

### Crystallizer policy root — `src/melder/crystallizer/crystallizer.py` (full read)
- class Crystallizer : ~16  -> Aether-hosted singleton; starts DISABLED. BUILT.
- configure() : 229 ; activate() : 259 (validates config) ; deactivate() : 290. BUILT.
- create_spell_crystal(spell) : 301-321 -> ONLY crystal constructor; requires activated;
  builds `SpellCrystal(spell, user_source_root_paths=self._configuration.user_source_root_paths)`. BUILT.
- _require_activated() : 338. BUILT.
- NO module registry / alias / footprint here (policy+state root only). GAP for M8/first-cut.

### Host wiring — `src/melder/aether/aether.py`
- import Crystallizer : 14 ; "hosts ... Crystallizer" doc : 46. BUILT.
- `self._crystallizer = Crystallizer(aether=self)` : 119 -> Aether OWNS it, independent of Nexus. BUILT.
- cleanup: `self._crystallizer.cleanup()` 164-165 ; `del self._crystallizer` 179. BUILT.
- Reach path for bind: `Spellbook._aether` -> `._crystallizer`.

### SpellCrystal (the module "twin") — `src/melder/crystallizer/spell_crystal.py`
- __init__ : 86. BUILT.
- _module_to_path : slot 72, init 148, populated 1249, returned 550 + in describe 1412. BUILT (partial footprint).
- reads sys.modules : root 905, deps 1335. BUILT.
- describe() : 1375 (returns module_to_path 1412) -> the twin-emit pattern today. BUILT.
- AST (PRIOR read): _extract_import_targets_from_ast ~1088 ; _walk_module_dependencies ~1273 ;
  _classify_module_target ~950 (synthetic_module|user_source|site_package|unknown). BUILT.
- GAP: no callsign, no created-sys.modules-keys footprint, no `exports`.

### The loader machine — `src/melder/crystallizer/synthetic_module.py` (full read this session)
- _SyntheticModuleImportLoader : 14 ; create_module -> create_module_for_spec (returns PRE-EXISTING) ;
  exec_module -> exec_registered_module. BUILT.
- _SyntheticModuleMetaPathFinder : 80 ; find_spec -> build_registered_spec. BUILT.
- class SyntheticModule : 117 ; registry `_registered_modules_by_name` 159 ; `_load_order` 160. BUILT.
- __init__ 164 ; `__file__ = "<synthetic:{0}>"` 277 (the getsource/linecache trip). BUILT.
- cleanup 284 ; execute_source 697 (exec; publish-before-exec) ; publish_to_sys_modules 723 ;
  unpublish_from_sys_modules 741 ; register_in_import_registry 761 ; materialize 819 ;
  install_import_hook 1062 ; build_registered_spec 1098 ; _attach_importlib_metadata 1142 ;
  create_module_for_spec 1175 ; exec_registered_module 1204 ; describe 1298. BUILT.
- GAP: production loader has NO get_source (introspection fix / M1).

### Bind seam — `src/melder/aether/spellbook/spellbook.py`
- bind() : 4229 ; opens "bind" transaction : 4303. BUILT.
- `new_spell = self._bind.bind(...)` : 4331 (spell created; has spell_id + spell_index). BUILT.
- collision check `Spellbook._aether._check_for_spell` : 4342. BUILT.
- register into `_lookup_spells`/`_spells`/`_register_owned_spell_id` : 4362-4364. BUILT.
- GAP: ZERO "crystal" refs in spellbook (grep); `create_spell_crystal` has ZERO callers (grep).
  HOOK: after 4364, gated on `crystallizer.activated` -> `create_spell_crystal(new_spell)` + seed.

### Mode gates — `src/melder/nexus/nexus.py`
- class Nexus : 60 ; __init__ 136 ; starts disabled `_enabled=False` : 195. BUILT.
- enable() : 540 -> REQUIRES an installed NexusConfiguration (raises ~564-565), finalizes/freezes
  config 573-574, sets enabled 575. BUILT.
- _validate_target_frame_runtime_requirements() : 2430 -> the FRAME/spellbook conditions:
  rules docstring 2441-2449 ; `rift_enabled` required 2463-2469 ; `ai_native_enabled` 2471 ;
  `system_state` 2472 ; ai_native implies dynamic (raise) 2474-2478. BUILT.

### SystemState — `src/melder/aether/spellbook/configuration/system_state.py`
- enum: `automatic` 24 (safe managed default), `dynamic` 25 (permissive/AI-native). Two values only. BUILT.

## 2. PROOF LEDGER (probe -> result -> key assertions proven)

### Persisted (tests/experimentation/), re-runnable
- `import_lifecycle_management_suite.py` -> 22/22 green.
  G3 physical->synthetic seed/unseed ; G4 load-time vs deferred (in-method) ; G5 `from b import a`
  in exec'd code ; G6 physical-method->synthetic ; G7 circular-dep publish-before-exec ;
  G8 removal depth (unpublish vs cleanup).
- `synthetic_module_external_library_probe.py` -> 5/5 green, CONFIRMED on user 3.14t.
  Stdlib+site-package resolve free + shared object ; AST classify {stdlib,synthetic,site_package,missing} ;
  missing external -> ModuleNotFoundError with half-published=True ; unseed leaves external loaded.
- `owned_physical_synthetic_relationship_probe.py` -> 6/6 green.
  Owned physical served by OUR loader (real __file__) ; imports a synthetic dep ; imports a
  site-package via importlib ; reverse edge (synthetic imports the owned-physical) ; getsource works.

### Persisted 2026-07-03 (T-F8 DONE) - the former inline probes, now on disk + re-runnable
- `content_addressed_version_store_probe.py` -> 6/6 (coexist by callsign + dedup + `import`/`from`
  invisible + repoint-without-removal + version-pin by callsign).
- `importlib_mirror_and_cycle_breaker_probe.py` -> 5/5 (hybrid scope-split + deferred cycle-breaker;
  importlib publishes-before-exec; synthetic circular ImportError == physical).
- `activation_footprint_insert_only_probe.py` -> 2/2 (insert-only deactivate; footprint =
  callsign + sys.modules key + canonical alias + file).
Original inline assertions (now covered by the three files above):
- content-addressed callsign store -> 3/3: two versions coexist by callsign (no collision) ;
  identical content dedups ; repoint canonical alias WITHOUT removing either version.
- callsign invisible to import site -> 4/4: `import svc` / `from svc import a` use canonical names,
  no SHA ; repoint picks up v2 unchanged ; version-pin via `import <callsign>` AND
  importlib.import_module(callsign). CAVEAT: `@` breaks the import statement -> identifier-safe `__` separator.
- hybrid cycle-breaker + importlib-mirror -> 5/5: AST splits load-time vs deferred ; a deferred
  cycle-breaker keeps both loading ; forcing it load-time reintroduces the partial-init cycle ;
  importlib publishes to sys.modules BEFORE calling our exec_module ; synthetic circular ImportError
  is byte-identical to physical ("cannot import name 'X'").
- footprint + insert-only deactivate -> 2/2: v2 active via canonical, v1 NOT removed + reimportable
  by callsign ; footprint per activation = {callsign, sys.modules key, canonical alias, file}.
- (folded into the suite) physical->synthetic mgmt 4/4 ; deferred 5/5 ; from-import 5/5 ;
  physical-method->synthetic 4/4 ; circular-dep 4/4.

## 3. PER-EPIC GROUNDING

### First cut (EPIC-2026-07-03-wire-crystallizer-into-melder)
- Wire reach: aether.py:119 (host) -> Spellbook._aether._crystallizer ; bind seam spellbook.py:4331/4364.
- create_spell_crystal path: crystallizer.py:301 (0 callers today -> add the caller at the bind hook).
- Seed/unseed: synthetic_module.py materialize 819 / publish 723 / unpublish 741 / cleanup 284.
- Config knob remove_inactive_synthmodules: crystallizer/configuration/crystallizer_configuration.py (add).
- Gate: crystallizer.activated (crystallizer.py:338) ; codegen-lane requires it + MR (nexus.py:2430 extend).
- Proof: the suite (G3/G8), footprint+insert-only (2/2), callsign store (3/3).

### Bootstrap (EPIC-2026-07-03-crystallizer-bootstrap-checkpoint)
- SpellCrystal twin exists (spell_crystal.py describe 1375) -> extend upward to
  ConduitCrystal/AethericFrameCrystal/AethericCrystal.
- Reconstruction order: configs -> frames -> Nexus -> conduits(conjure) -> bindings -> links.
- Snapshot versioning = content-addressed (same mechanism as the callsign store proof, 3/3).
- Proof: callsign store (coexist/dedup/versioned) + footprint (what a twin records).

### Persistence (EPIC-2026-07-03-crystallizer-persistence)
- Contract per Crystallizer V2 (artifacts/2026-07-01_crystallizer_philosophy_v2.md Duty 3):
  JSON in/out, CRUD, transactions = ordered plain-data batches, host owns storage.
- MutationResearchCrystal per MR V2 (artifacts/2026-07-01_mutation_research_philosophy_v2.md):
  ResearchStream + VersionRecord + heads + index associations.
- Scaffold dirs (0-byte, from prior survey): crystallizer/crystal_loader/, /asset_management/.
- Proof: design contract (no runtime probe yet) - validated by the V2 canon + the external-lib
  probe's "track edges, validate at restore" finding.

## 4. KEY MECHANISM SNIPPETS (minimal; full code in the probe files)
- Loader inversion (create_module returns the pre-existing object):
    def create_module(self, spec): return _REG[spec.name]      # NOT a fresh ModuleType
- Publish-before-exec (cycle-safe; mirrors importlib):
    sys.modules[name] = module ; exec(compile(src, module.__file__, "exec"), module.__dict__)
- Finder declines non-owned names (importlib owns the rest):
    def find_spec(self, name, ...): m = _REG.get(name) ; return None if m is None else spec
- Content-addressed callsign + canonical alias:
    callsign = "%s__%s" % (canonical, sha256(source)[:12])     # identifier-safe
    find_spec: key = ACTIVE.get(fullname, fullname)            # canonical -> active callsign
- Bind hook (first cut), conceptual, after spellbook.py:4364:
    if aether._crystallizer.activated: aether._crystallizer.create_spell_crystal(new_spell)  # + seed

## 5. RETRACE CHECKLIST
- [ ] Open each Code Map file at the cited line; confirm the symbol + BUILT/GAP.
- [ ] Run all 6 persisted probes on 3.14t: import_lifecycle_management_suite (22/22),
  synthetic_module_external_library_probe (5/5), owned_physical_synthetic_relationship_probe
  (6/6), content_addressed_version_store_probe (6/6), importlib_mirror_and_cycle_breaker_probe
  (5/5), activation_footprint_insert_only_probe (2/2).
- [ ] (T-F8 done) all former-inline probes are now standalone files - just run them.
- [ ] Confirm the two gaps: spellbook has 0 crystal refs; create_spell_crystal has 0 callers.
