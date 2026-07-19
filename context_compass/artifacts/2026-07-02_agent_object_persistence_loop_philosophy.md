# Agent Object-Persistence Loop Philosophy (Codegen -> SynthModule -> Bind -> Crystal)

## Metadata
- Artifact ID: ART-2026-07-02-agent-object-persistence-loop-philosophy
- Parent Epic: EPIC-2026-07-02-agent-object-persistence-loop
- Status: active
- Agent Name: crystal_0
- Created: 2026-07-02T22:01:20Z
- Updated: 2026-07-02T23:03:09Z
- Refined: 2026-07-02T23:03:09Z - dynamic-mode in-memory loading model + frame
  correction (owner, memory-recovered); see the "Refinement 2026-07-02" section.
- Consolidates (does NOT supersede): the crystallizer + mutation + AR-codegen
  philosophy set (referenced in "Canon Map" below). Where this doc and a
  canonical V2 doc disagree, the V2 doc wins; this doc is a comprehensive
  session-capture, not a new authority layer.

## Purpose (read first; written to survive compaction)
This artifact captures, redundantly and comprehensively, the understanding
retraced in the 2026-07-02 crystal_0 session about ONE loop:

    codegen (source) -> materialize as SyntheticModule -> bind(the class)
    -> SpellCrystal (source custody) -> reuse by later codegen / restore later

plus the exact importlib mechanics that make it real, the physical<->synthetic
interop limits that were PROVEN by experiment, and the lifecycle discipline
(seed/unseed) required to run it safely. It exists because the owner is
retracing a large system from memory and compaction is imminent; everything
important is stated explicitly here so the thread is not lost.

Frame (corrected 2026-07-02; see the Refinement section): we do NOT "take over
importlib". We built our own loader + registry; the import protocol is only the doorway.
The machine is the `SyntheticModule` registry of live, pre-existing world objects.

## North Star (recap)
A container ships a project plus a small bootstrap. On start, crystals unfold
into synthetic modules, conduit world slices rebuild, config restores - the
whole checkpointed application is simply UP. Agents then work at Nexus
workstations building new objects, and every build comes with an impact map.
Crystallizer = the save/restore + source-custody spine. MutationResearch = the
git-for-live-objects + blast-radius change engine. Melder = the live object
world both operate on (already built and tested).

## Refinement 2026-07-02 (owner, memory-recovered) — Dynamic-Mode In-Memory Loading Is Step One
This section is the freshest layer; it REFINES the frame and several sections below.

FRAME CORRECTION (supersedes the "importlib takeover / own its state" wording used
elsewhere in this doc). The machine is the `SyntheticModule` class and its class-level
registry of LIVE module objects (`synthetic_module.py`) - the code itself calls it the
"world-first runtime embodiment of one managed software unit". Modules PRE-EXIST as
managed world objects and are SERVED to the import protocol, not created by it. The
import protocol (a finder on `sys.meta_path` + a `Loader` subclass) is only the DOORWAY
so a plain `import X` / `importlib.reload` resolves onto the world object: the loader
creates nothing and executes nothing itself - `create_module` returns the pre-existing
object, `exec_module` delegates back to `module.execute_source()`. "We plug into the
import protocol" is NOT "we depend on importlib's behavior." This is world-first; do not
reason about it by analogy to normal Python.

STEP ONE (this epic) = in-memory load/unload management tied to spell state:
- Bind creates a SpellCrystal. The crystal is the loader's HANDLE for every module
  related to it. Crystal creation is DISTINCT from module loading.
- Spell ACTIVE -> the loader turns it on and loads the module plus its
  dependencies/requirements (register -> publish -> execute, in dependency order).
- Spell INACTIVE -> not loaded / unloaded and unwound (unpublish -> detach -> unregister);
  the crystal is RETAINED.
- COLLISION MANAGEMENT falls out of this: because the loader controls the load PHASES,
  only active spells' modules occupy `sys.modules` at once; inactive names stay free.

DYNAMIC-MODE GATE (hard condition): bind->crystal is default-ON only when Nexus AND
MutationResearch are enabled - i.e. codegen/agent (dynamic) development. Without agents,
synthetic modules are not needed and this stays off. BOTH subsystems (synthetic-module
management AND MR) operate ONLY in dynamic mode. This REFINES V2 Duty 1's unconditional
"crystal at every bind, always" -> "crystal at every bind in dynamic mode". (The V2
crystallizer doc is another lane's artifact; reconcile it there, not here.)

AST'S ACTUAL JOB (narrowed): the AST analysis maps HOW a module's code populates
`sys.modules` and then the module `__dict__`, and it makes the reverse (UNWIND/unload)
possible. A module's dependencies and all requirements must be loaded too, so the loader
takes on much of the work importlib normally does (dependency resolution + ordering) and
MAY re-delegate to importlib's own methods where useful. The crystal's dependency map
drives both the load and the unwind.

MUTATION RESEARCH = a thin API over what already exists. MR relies on SpellCrystals
existing. Each spell has a unique SHA256 key. MR holds an IN-MEMORY representation DERIVED
FROM the crystallizer: derived objects mapped to those SHA256 keys that report active vs
inactive, which fork a version is on, diff two versions, and compute blast radius by
scanning impacted code - all by reusing the SAME dependency systems crystallizer already
uses. MR re-derives nothing; it is tools/an API over crystallizer's custody + graph.

OUT OF SCOPE FOR THIS FIRST STEP (separate later systems): checkpointing, bootstrapping,
and fast-loading the system + its configurations. The North Star above describes the
eventual unfold; that is context, NOT this epic's deliverable.

## The Core Loop (what was retraced)
1. An agent, working in the Nexus codegen room, produces source (a class/tool).
2. `codegen -> X -> synthetic_module`: `X` = PROMOTE the source to a
   `SyntheticModule` - retain the source text, give it a canonical module name,
   materialize it into `sys.modules`. This is the philosophy's "promoted
   bindable synthetic-module stream." The SyntheticModule is a NORMAL module:
   no conduit/melder machinery lives inside it; it is plain importable Python.
3. `bind(TheClass)`: you bind the CLASS that lives in the synthetic module -
   NOT the module (bind rejects modules/Protocols as concrete spells). Binding
   yields a `Spell` + `SpellIndex`.
4. `-> SpellCrystal`: per Crystallizer V2 Duty 1, bind should mint a
   `SpellCrystal` for the bound object (custody). The MODULE is the unit of
   custody/reference: the crystal is module-shaped (`module_name`, `exports`,
   `internal_dependency_names`, `external_import_names`, `authority_class`),
   capturing the FULL synthetic-module source, not just the class body.
5. Result trio: crystal = saved source truth; synthetic module = live
   embodiment; spell = runtime handle. That is "stored and saved."
6. A later codegen references the first unit either as a normal IMPORT
   (synthetic modules import each other by normal Python import syntax) or as a
   melder DI dependency at bind (keeps the edge in melder's graph so MR's impact
   engine can see it). A multi-unit saved system is a `SpellCrystalGraph`.

CRITICAL CURRENT-STATE FACT: bind -> crystal is NOT wired today. The only place
a `SpellCrystal` is constructed is `Crystallizer.create_spell_crystal(spell)`
(crystallizer.py ~318); `spellbook/` has ZERO references to "crystal". The
codegen room does NOT produce a synthetic module / bind / crystal - it validates
-> compiles -> execs into a sandboxed namespace -> emits a memory record, and
stops. So the loop is INTENT (now canon), not built wiring. The pieces
(SyntheticModule machinery, `create_spell_crystal`, codegen namespace + import
ACLs) all exist and are tested; the loop is a WIRING job across them.

## The Loader Machine - Exact Mechanism (comprehensive)
FRAME NOTE (see "Refinement 2026-07-02" above): the mechanics below are accurate, but
read them as OUR loader/registry machine with the import protocol as a doorway - NOT as
"taking over importlib". The finder/loader are the socket; the `SyntheticModule` registry
of live pre-existing world objects is the engine.

- A `_SyntheticModuleMetaPathFinder` is inserted at the FRONT of
  `sys.meta_path` (global; consulted on every import regardless of who imports).
- `find_spec(fullname)` -> `build_registered_spec`: looks the name up in a
  class-level registry `_registered_modules_by_name`, builds a spec via
  `spec_from_loader(name, loader, is_package=...)`, sets `spec.origin =
  module.__file__`. Not registered -> returns None -> Python falls through to
  the filesystem finders. For synthetic names, the filesystem is never consulted.
- INVERSION (the part that is NOT textbook importlib): the loader's
  `create_module(spec)` RETURNS THE PRE-EXISTING registered module object
  (`create_module_for_spec`), not a fresh `ModuleType`. The module pre-exists as
  a managed world object; importlib is bent back onto it. `exec_module` ->
  `exec_registered_module(name)` -> `module.execute_source()` (exec of the
  retained source into `module.__dict__`).
- `_attach_importlib_metadata` STAMPS onto the live module object:
  `module.__loader__ = <your loader>`, `module.__spec__ = <spec>`, plus
  `__package__`/`__path__`. This is the "something bound on the module object"
  that makes `importlib.reload` and submodule resolution route back through YOUR
  loader forever. The live object also carries `_spell_crystal_id` and
  `_binding_signature` - the bridges to durable crystal truth and the spell
  surface - bound right on the module.
- `materialize()` = the manual full path: register -> publish_to_sys_modules
  (BEFORE exec, so interdependent + circular graphs resolve naturally) ->
  execute_source -> _attach_importlib_metadata.

Physical and synthetic modules are the SAME under the hood: a module is a
`ModuleType` whose `__dict__` is populated by `exec(code_object, module.__dict__)`.
`exec` auto-injects `__builtins__`. The ONLY difference is where the code object
comes from: physical loads marshalled bytecode from `.pyc` (or compiles the
`.py`); synthetic compiles the retained source STRING at exec time. So it is
SOURCE at the custody layer, BYTECODE at the execution layer - deliberately both.
The bytecode layer is real elsewhere too: `SpellCodegenCreation` holds compiled
`code_object`s, the codegen-creation cache is marshal-safe, and
`executor_code_cache` dedupes/replays compiled code by hash.

## Physical <-> Synthetic Interop - PROVEN by experiment
Experiment: `tests/experimentation/physical_imports_synthetic_limits_probe.py`
(self-contained, pure-stdlib mirror of the production mechanism). Ran on the
3.10 sandbox; import semantics are identical on 3.14t (owner should re-run there).
NOTE: that probe file was mount-truncated during editing (the recurring
file-tool write fault); it needs a clean re-lay - tracked in the epic.

Results (6/7 green; the one red is a real, named, fixable limit):
- PROVEN: a PHYSICAL file-backed module CAN import a SYNTHETIC in-memory module,
  via the global front-of-`meta_path` finder. Who imports (physical vs
  synthetic) is irrelevant.
- PROVEN: a PHYSICAL PACKAGE can import a SYNTHETIC SUBMODULE, both ABSOLUTE
  (`from mixpkg.helper import H`) and RELATIVE (`from . import helper`). Key:
  materialize the synthetic child and `setattr` it onto the physical parent
  package.
- PROVEN: `sys.modules` precedence - it is checked BEFORE `meta_path`, so an
  already-loaded physical module of the same name WINS and the finder never
  runs. To resolve a colliding name synthetically you must evict the physical
  first.
- PROVEN: the HOT-SWAP boundary - a consumer that eagerly did
  `from provider import VALUE` keeps the OLD value after a synthetic swap; a
  fresh lazy `import provider` sees the NEW one. So "overwrite an existing
  module" is safe at bootstrap/rebuild boundaries, NOT as an invisible live
  swap. This matches the crystallizer_configuration "non-negotiable" boundary.
- PROVEN: reload of a physical module whose dep is synthetic works when the
  synthetic dep is re-exec'd in place (v1->v2 on the same live object).
- PROVEN: pickling a class defined in a synthetic module works IN-PROCESS (by
  qualname, e.g. `pmod.Widget`, resolved through the finder). Cross-process
  unpickling needs the finder + registry rebuilt - which is exactly what a
  crystal restore does.

## The inspect.getsource / linecache Limit - PROVEN + fix
`inspect.getsource` on a synthetic class FAILS with `OSError: could not get
source code`. The reason is NOT merely a missing loader hook. The real blocker:
`linecache.updatecache` short-circuits on angle-bracket filenames -
`if filename.startswith('<') and filename.endswith('>'): return []` - BEFORE it
ever consults the loader. Production `SyntheticModule.__init__` sets
`self.__file__ = "<synthetic:{0}>".format(module_name)` (line ~277), so it hits
exactly this. (Production loader also lacks `get_source`; it only has
`create_module` + `exec_module`.)

Two fixes, BOTH proven green by inline experiment:
- FIX B (clean, preferred): give synthetic modules a `__file__` that is NOT the
  `<...>` form - a normal-looking synthetic path (or `materialized_directory_path`
  when projected to a real file) - AND implement `get_source(fullname)` on the
  loader (`importlib.abc.InspectLoader`). Then linecache does `os.stat` (fails,
  not on disk) -> falls back to `__loader__.get_source(name)` -> source. This is
  how `zipimport` exposes source; `inspect.getsource`, tracebacks, `pdb` all work.
- FIX C (targeted): keep `<synthetic:...>` and seed
  `linecache.cache[__file__] = (size, None, lines, path)` at materialize.
  `getlines` checks the cache before the guard, so it bypasses it.

This does NOT affect MutationResearch - MR reads `source_text` off the object
directly, not via `inspect`. It only affects standard introspection tooling
(inspect/traceback/pdb/coverage).

## Lifecycle - Seed/Unseed Symmetric with Spell State
Owner's insight (correct): inactive modules must be unseeded. The lifecycle is
symmetric and must be tied to spell activation state:
- ACTIVATE / bind -> register in the synth registry -> publish to `sys.modules`
  -> attach to parent package -> (FIX B) non-`<>` `__file__` + `get_source`
  (and/or seed `linecache`).
- INACTIVE (notch parks the outgoing active spell) / cleanup -> unpublish from
  `sys.modules` -> detach from parent -> CLEAR the `linecache` entry ->
  unregister. Production `SyntheticModule.cleanup()` ALREADY does unpublish +
  unregister + detach-parent; the missing pieces are the `linecache` clear (the
  flip side of the getsource fix) and TYING the unseed to the notch/deactivate
  transition so a parked spell's module stops resolving.

PRECISION: "removed" means unseed from the LIVE import surface, NOT destroy. The
crystal (source truth) and the SpellIndex member are RETAINED so checkout /
reactivate stays cheap. You pull the module out of `sys.modules`/`linecache`,
you do not delete world truth.

CAVEAT that never goes away: the hot-swap boundary. Unseeding cannot reach code
that already eagerly captured the old object, so this coherence holds at
bind/rebuild/bootstrap boundaries - which is exactly why the philosophy pins
copy-mode to those boundaries and forbids invisible live swaps.

## The Mutation Wall Is Down (recovered memory)
The old blocker "couldn't make mutations due to spell_index" is FIXED. A
`SpellIndex` now holds a member SET plus one active `selected_spell_id`;
`bind_inactive` stages a candidate member (real SHA256 `spell_id`, unmeldable
until promoted); `notch` promotes it under a sealed change-control transaction.
`Spellbook._apply_notch` is a real implementation (spellbook.py 3063-3149): park
the outgoing active spell via `_deactivate_owned_spell` (+ tear down its
creation context to kill the warm door), promote the staged spell via
`_reactivate_owned_spell`, repoint the index via `SpellIndex.update`, re-gate so
meld recompiles lazily - all inside the held `notch` window. MR V2: "index
operations became real mediated transactions ... promotion is a solved runtime
mechanic." REMAINING SLICE (spellbook.py :3091): a notch on a SHARED index does
not yet fan out to cross-conduit contracted borrowers.

## The Codegen Room Today vs Intent
- Today: `CodegenSystem` (owned by `CodegenRiftSpace`, facade
  `CodegenCommandSystem`) = build transaction context -> validate (AST/import/
  builtin/name/attr/reflection/recursive policy strategies) -> build namespace
  (from room/runtime strategies) -> compile -> `exec` into namespace -> emit
  room-memory record. Import policy exists (`imports_enabled`,
  `allowed_import_module_roots`, `codegen_import_policy_strategy`) - THIS is the
  designed hook for synthetic-module names. It does NOT yet produce a synthetic
  module / bind / crystal.
- Residency ladder (AR Codegen Capability Surface doc): `transient ->
  sessional -> bound -> crystallized -> promoted`. Agent acts: Probe, Harness,
  Adapter, Challenger, Utility, Progenitor. "Turn a codegen into a class and
  save it" = the Progenitor act climbing the ladder.
- Safe lane vs mutation lane (Codegen-to-Mutation Bridge doc): one codegen
  entrypoint, AST policy first, then Route A (safe: approved capabilities,
  return results) vs Route B (mutation escalation: structural intent ->
  permissions -> mutation lane). Binding a genuinely new object = escalation.

## Canon Map (all philosophy documents; promote/reference)
Canonical (2026-07-01 V2; win on any conflict):
- `artifacts/2026-07-01_crystallizer_philosophy_v2.md` (Custody + Unfold; three
  duties: crystal-at-bind-always, save-time facts + unfold-order,
  MR-hydration/persistence via JSON adapter).
- `artifacts/2026-07-01_mutation_research_philosophy_v2.md` (Tool Model; MR =
  internal git + code-based blast-radius engine; kill list retires
  SpellMutationNode/CreationMutationNode, MutationConduit-as-gate-orchestrator,
  MutationFrame; versions are full objects).

Older / superseded-where-conflicting (valid background):
- `artifacts/2026-04-26_crystallizer_philosophy.md`
- `artifacts/2026-05-09_mutation_research_philosophy.md`

Supporting (NOT superseded; still govern):
- `artifacts/2026-04-26_ar_codegen_capability_surface_philosophy.md` (codegen =
  construction surface, residency ladder, agent acts, Melder/CommandOps split).
- `artifacts/crystallizer_configuration.md` (synthetic-module copy mode; hot-swap
  boundary is non-negotiable; bootstrap/rebuild/reload only).
- `artifacts/2026-05-02_file_to_memory_bridge_mechanic.md` (codegen->py,
  py->codegen->py, codegen-alone; file projection direction; "the bridge stands").
- `artifacts/IMPORTANT_CONSIDERATION.md` (governs world-merge; "still open");
  merge-model decision remains PARKED.
- `artifacts/2026-05-10_mutation_branch_type_enforcement.md` (optional
  branch_type_enforcement config policy on ResearchStream).
- `artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md`
  (pairs with AR codegen; lower-trust execution -> container/pod workers).

Archived bundle (`artifacts/Archived/2026-03-15_aethericrift_engineer_context_bundle/`
and `artifacts/Archived/2026-04-26_crystallizer_v1/v2/v3...`):
- `.../MutationResearch/systems/codegen_bridge.md` (safe/mutation lane routing).
- `.../utilized_ticket_artifacts/Codegen Interaction Model - Safe Lane and Mutation Lane.md`.
- `.../utilized_ticket_artifacts/Ticket - Workstation Codegen Guardrails and Capability Manifest.md`.
- `.../MutationResearch/WORKING_MODEL.md`.
- `Archived/2026-04-26_crystallizer_v2_synthetic_module_graph_and_requirements.md`
  (SpellCrystal V2 fields: module_name, exports, internal_dependency_names,
  external_import_names, authority_class; SpellCrystalGraph; RequirementsView;
  PersistenceTableContract; uv-first environment recovery).
- `Archived/2026-04-26_crystallizer_v1_spell_crystal_storage.md`,
  `Archived/2026-04-26_crystallizer_v3_bootstrap_recovery_and_fileless_truth.md`.
NOTE: these three archived docs were referenced but not fully re-read this
session; a follow-up read is queued in the epic.

## Built vs Gaps (actionable)
Built and GREEN (386 crystallizer unit+component+integration tests pass on
user-run 3.14t; probe scenarios green on 3.10):
- SyntheticModule machinery: finder/loader, create-returns-preexisting,
  publish/unpublish, register/unregister, parent attach/detach, materialize,
  reload_via_importlib, package shells, cycle-safe publish-before-exec.
- SpellCrystal captures root module identity + `module_to_direct_dependencies`
  + `_extract_import_targets_from_ast` (imports incl. relative + from-imports) +
  `_walk_module_dependencies` + module classification (synthetic/user_source/
  site_package/unknown) + `describe()`. That is 4 of 5 V2 record fields
  (missing: `exports`).
- Codegen room exec surface + validation strategies + import ACLs.

Gaps that close the loop:
- bind -> crystal AUTO-WIRE, gated to dynamic mode (Nexus + MR). Not wired; spellbook
  has 0 crystal refs.
- crystal `exports` capture + `SpellCrystalGraph` (multi-module saved systems).
- codegen-result -> SyntheticModule MATERIALIZE step (the `X`).
- Loader chain: `crystal_loader.py`, `synthetic_module_loader.py`,
  `bootstrap_loader.py` are all 0-line scaffolds; plus a `load_order` topological
  sort over the crystal's dep graph (the crystal has the edges; no sort yet).
- Introspection fix: non-`<>` `__file__` + `get_source` (FIX B) or linecache
  seed (FIX C); AND `linecache` CLEAR on unseed.
- Tie synthetic load/unload to spell activate/deactivate (notch) lifecycle.
- Persistence adapter contract: typed contract + JSON codec; CRUD verbs
  (create/read/update/delete over named datasets; a "transaction" = an ordered
  batch of CRUD ops applied atomically); first adapters SQLite mock + JSON file.
- MR tool: derived in-memory objects keyed by spell SHA256 (active/inactive, fork,
  diff, blast radius) over crystallizer's dependency systems; then the impact engine.

## Open Decisions (parked)
- MutationResearch merge/lane/head model (lane/head/merge-node/rebase vs additive
  time-based union). IMPORTANT_CONSIDERATION governs; still open. This is the
  parked DECISION_REQUEST on
  `tickets/tasks/2026-07-01_reframe_spellindex_in_crystallizer_mutation_philosophy_artifacts_task.md`.
- Module naming for `X` (agent-chosen vs derived from class/target). The name is
  both the import handle and the crystal's canonical module id.
- Default reference mode for a later codegen referencing a prior unit: normal
  IMPORT vs melder DI (lean DI-default to keep edges in melder's graph for MR).
- Adapter payload boundary: typed contract is canonical, JSON is the codec/
  portability option.

## Build Order (from V2 docs)
1. MutationResearch tool (composition + query API + orchestration + transaction
   emission).
2. Crystallizer build-out (crystal-at-bind in dynamic mode, save-time facts, adapter
   contract + SQLite/JSON adapters, MR hydration, then the loader chain).
   Crystallizer load half, concretely: `load_order` (topo sort) ->
   `synthetic_module_loader` -> `crystal_loader`/`bootstrap_loader`.
3. MR impact engine (needs 1 + 2).
4. Checkpoint / bootstrap / fastload + world-merge afterward (separate systems).

## Summary (one paragraph)
The system lets an agent turn a codegen into a durable, versioned, restorable object:
promote the source to a synthetic module, bind the class inside it (bind mints a crystal,
in dynamic mode, that captures the whole module as source custody), and reuse it later by
ordinary import or melder DI - all made possible by OUR loader machine (a `SyntheticModule`
registry of live pre-existing world objects; the import protocol is only the doorway - the
loader returns the pre-existing object and delegates execution back to it, with
`sys.modules` publish-before-exec and `__spec__`/`__loader__` + crystal id stamped on the
object). The crystal is the loader's handle: an ACTIVE spell loads its module + its
dependencies, an INACTIVE spell unloads/unwinds them (crystal retained), and controlling
those load phases is how name collisions stay manageable. Introspection
(`inspect.getsource`) is a knob on our own loader (non-`<>` `__file__` + `get_source`, or
seed linecache), not a Python limit we are subject to. Both this synthetic-module
machinery and MutationResearch run ONLY in dynamic mode (Nexus + MR enabled); MR is a thin
API of in-memory objects derived from crystallizer, keyed by each spell's SHA256, reusing
crystallizer's dependency systems. The mutation wall (spell_index) is down; the machinery
mostly exists; what remains is wiring: bind->crystal, the codegen->synthmodule materialize
step, the loader chain + load_order, the introspection fix, lifecycle tie-in to notch, the
persistence CRUD adapter, and the MR tool.  Checkpointing, bootstrapping, and fast-loading are separate later systems.
