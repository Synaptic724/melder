### src_architecture: metadata Updated  (-1 +1 lines)
- - Updated: 2026-10-19
+ - Updated: 2026-10-24

### src_architecture: indexing correction note  (-2 +1 lines)
- section used to paste those commands and cite the tooling's own specification).
- tooling, which does not ship with this document (corrected 2026-09-28: this
+ tooling, which does not ship with this document.

### src_architecture: citation recipe kept once, in src_components  (-39 +5 lines)
- # Cited source paths are relative to the SOURCE-TREE root, which is not
- # necessarily the directory you run this from. Walk up until `src/` appears, so
- # the check works from the documentation root or the repository root.
- CITE = re.compile(r"`?([a-z][A-Za-z0-9_/.]*\.py):(\d+)(?:\s*-\s*(\d+))?`?")
- EOF
- In-bounds is necessary, not sufficient. A range can sit inside the file and
- Run this after any pass that touches source or citations:
- The index tool checks this document's own structure. It CANNOT check the
- ```
- ```bash
- `path:line` citations in `EVIDENCE:` blocks, and those rot silently: the file
- a 693-line file (it had been decomposed into subpackages and the ranges were
- actually there - and when you cite a function, cite its `def` line, because a
- code. On 2026-08-02 an audit of the 81 citations across the two source documents
- continue
- docs = next(p for p in (pathlib.Path("system_docs"), pathlib.Path("."))
- f = root / m.group(1)
- for doc in docs.glob("src_*.md"):
- for i, line in enumerate(doc.read_text(encoding="utf-8").split("\n"), 1):
- for m in CITE.finditer(line):
- found SEVEN wrong - five pointing into `spell_compiler.py` at lines 1966-3787 of
- here = pathlib.Path.cwd().resolve()
- if doc.name.endswith("_index.md"):
- if list(p.glob("src_*.md")))
- if not f.exists():
- if s < 1 or e > n or s > e:
- import pathlib, re
- keeps existing, the citation keeps parsing, and it quietly points at the wrong
- n = len(f.read_bytes().decode("utf-8", "replace").splitlines())
- never remapped), and two that were in bounds but landed nowhere near the symbol
- print("MISSING", doc.name, i, m.group(0)); continue
- print("OUT OF BOUNDS", doc.name, i, m.group(0), "file has", n)
- python - <<'EOF'
- range that merely brushes past a definition reads as verified without being it.
- root = next((p for p in (here, *here.parents) if (p / "src").is_dir()), here)
- s = int(m.group(2)); e = int(m.group(3) or m.group(2))
- still contain none of what it is cited for, which is how two of the seven
- survived. For any citation you are relying on, open it and confirm the symbol is
- they were cited for. Nothing had reported any of it.
+ The index checks this document's structure, not the `path:line` citations in its `EVIDENCE:` blocks, and those rot
+ citation check - every cited file exists and every range lies inside it - is kept once, in src_components' Indexing
+ section, and covers this document too. In-bounds is necessary, not sufficient: open a citation you rely on, confirm
+ silently when code moves: the file keeps existing, the citation keeps parsing, and it points at the wrong code. The
+ the symbol is there, and cite a function by its `def` line.

### src_architecture: unknowns re-verification narrative  (-15 +3 lines)
- (`add_spell_into_spellindex` and `remove_spell_from_spellindex`, which are not
- 693-line file at lines 1966-3787.
- Spellbook methods and never were; `_get_conjure_hook_map`;
- The 2026-06-12 path/rename sweep that produced this list is COMPLETE. Its
- The second half of that was NOT TRUE, and an audit on 2026-08-02 disproved it:
- This block previously read "re-verified 2026-07-25: every source path cited in
- WHAT THE RE-VERIFICATION STAMP ACTUALLY COVERS - READ THIS BEFORE TRUSTING IT.
- `## Indexing`. Do not widen a future stamp beyond what was actually run.
- `_initialize_conduit_hooks`; `Meld._resolve_spell_for_live_creation_probe`),
- and nine `path:line` citations pointed at the wrong code, five of them into a
- five renamed or invented symbols were still being cited as live
- green path sweep says nothing about whether the symbols are real. Both are now
- index of every `class` and `def` in `src/`, citations via the recipe under
- step-by-step narration was removed as settled history; git carries it.
- this document resolves on disk and no renamed symbol survives as a live claim."
+ green path sweep says nothing about whether the symbols are real. Both were
+ index of every `class` and `def` in `src/`. Do not widen a future stamp beyond
+ what was actually run.

### src_architecture: glossary re-absorption note  (-6 +0 lines)
- 2026-08-01 recomposition on the reading that the Required Section Contract was a
- ORDER, and other sections are permitted and common. All 42 terms below were
- RE-ABSORBED 2026-08-02. This section was moved to the patch lane during the
- The 17 contract sections remain present and in contract order around it.
- verified against `src/` on re-absorption: every one resolves to a real class.
- whitelist. It is not - the instructions state it is a MINIMUM IN A FIXED RELATIVE

### src_architecture: boundary CORRECTED note  (-5 +0 lines)
- CORRECTED 2026-08-02: this document previously said the Conduit "delegates to
- not. That wording was inherited from the Conduit docstrings, which say the
- opposite correctly. The code settles it, and since 0.2.8249 all three Conduit docstrings say so.
- same thing and are also wrong - see `src/melder/aether/spellbook/spellbook.py:4042-4044`, which states the
- the owning Spellbook, WHICH ADMITS the change-control transaction". It does

### src_architecture: MutationResearch boundary bullet -> summary  (-80 +10 lines)
- "informational" with no custody/frame probes; POLYMORPHIC VERBS
- (2026-07-11 units-and-scales ruling): `module_view(...)` (the one-call
- (read-only candidate mock: AST analysis + would-be diff via
- (unified part-text diff between versions over RECORDED material only,
- - `Aether.mutation_research` as the access path to the hosted mutation root,
- 2026-07-11: `group_view` roster + behind drift, `group_diff_research`
- 34-command `research_*` family (14 record/organization/campaign incl.
- ADVERTISED via `list_supported_command_methods`, and
- DELETED; as of 2026-07-12 (patch
- EXPLICIT DB-storable node rows for both families at construction, and
- MutationResearchConfiguration.activate() CARRIES the recorded
- [2026-07-12]: the spell-grain reads themselves dispatch on node kind -
- `DiffEngine.diff_materials` + would-be radius; nothing executes, binds,
- `LaneType` development/experiment/production/test; join gate armed by
- `ViewSpell.describe_spell_research(...)` / `describe_spell_source(...)`
- `clear_active_campaign()` / `active_campaign` (ambient stamp carried by
- `create_configuration_builder()`, `configure(...)`, `activate(...)`,
- `create_diff_engine()`, and the foresight reads (2026-07-11 agent QoL
- `group_drift_view` custody drift narrowed to the footprint,
- `group_footprint_view` physical shadow + shared-module coupling,
- `group_history_view` the area's journal story, `compositions_of` the
- `join`, `archive`, `walk`/`history`/`heads`, `campaign_view`,
- `list_research_set_names()`, `describe_research_composition()`,
- `load_recorded_composition(...)`, `record_world_entry(...)`,
- `preview_candidate(...)`
- `recompose_group` [compositions = GroupedResearchNode, its OWN node
- `record_promotion(...)`, `residency_view(...)` (the query-time
- `research_preview` + 3 synthesis + 8 composition),
- `research_set(...)`, `create_research_set(...)`,
- `snapshot_network`/`restore_network`); the spellbook's bind,
- `source_drift_view()` (full drift report), the crystal-well reads
- active/parked/stored join), `set_active_campaign(...)` /
- agent verb surface (`register_spell`, `register_group`/
- and `part_diff(...)`
- annotate any visible spell with its research residency and recorded
- bind_inactive, and notch confirmation points auto-record
- campaign-pattern: the next fresh world entry mints the multi-parent
- capability rooms the twenty-one reads (seven record + eight foresight +
- carriers - synthetic and user-retained - and never the live disk;
- carrying its module-grain radius; diff material drinks BOTH recorded
- class-code inventory: every top-level part per module with full text)
- composition answers the group radius, diff_research routes two
- composition forward - the docking-loop law); the returned `ResearchSet` carries the
- compositions teach-grade; the emitted MutationResearchCrystal derives
- compositions through the members engine, code-grain verbs refuse
- configuration `lane_type_enforcement`], `attach`/`detach`,
- every runtime auto-record), `diff_research(...)`,
- foresight incl. the crystal-well module/part reads and the codegen-only
- instead bind the world root at init and expose it through borrowed
- kit): `source_view(...)` (recorded-first module text, live-disk fallback
- lane of group nodes is a subsystem's timeline], `create_lane` [typed via
- lane-evidenced version_moved pairing], `group_impact_view` union
- member radii + internal/outbound split + CLOSURE + adjacency,
- module + full preview; salvaged May lane), and the staged-ancestry mint
- module dossier: text labeled synthetic/user/live_disk, fingerprint,
- module source. The old `Conduit.get_mutation_research()` door is
- mutation dimension)
- mutation_research_accessor_doors_2026_07_12) Spellbook and Conduit
- node one-shot), and the composition reads (GroupedResearchNode ruling
- or records), `synthesize_candidate(...)` (surgical composition through
- path, deps both ways, exports, drift), `part_view(...)` (one named
- plus `MutationResearch.create_configuration()`,
- read-only `mutation_research` properties (frames still carry no
- residency), `module_graph_view(...)` (walkable module world),
- residency]; `residency_view` is kind-aware - compositions answer
- reverse lift [surfaced as `pinned_by_compositions` on spell
- roster-searches naming the carrying member, impact_view on a
- seam (`stage_ancestry`/`clear_staged_ancestry`/`staged_ancestry`,
- six composition), both
- source/parts/module_graph/module fan out per member, part_view
- strategies: source/structural/parts),
- surface is the Rift rooms (2026-07-11): codegen rooms carry the full
- the owned `StructuralSynthesizer`: donor parts splice into the base root
- the research_recent cold-landing read + 9
- through the MIRRORED GroupDiffEngine ["members" strategy:
- top-level part's text/span/carrying module), `parts_view(...)` (the
- type, purely informational, content-addressed over pinned members; a
- w/ drift marker), `impact_view(...)` (blast radius joined with research
- whole-version diffs offer the grain CHOICE via three registered
- world-entry/staged/promoted events while the root is active. The USER
+ (`create_configuration()`, `create_configuration_builder()`, `configure(...)`, `activate(...)`), the ResearchSet
+ - `Aether.mutation_research` as the access path to the hosted mutation root: its configuration lifecycle
+ `research_*` commands, advertised via `list_supported_command_methods`. Spellbook and Conduit expose the root
+ and notch confirmation points auto-record while the root is active. The user surface is the Rift rooms'
+ inventory is in src_components (Subcomponent: MutationResearch Root (ResearchSet Registry)).
+ of a ResearchSet (spells and compositions, lanes, joins, history, campaigns, network snapshots), the research
+ record (world entries, promotions, residency, campaigns, diffs), the foresight and crystal-well reads over
+ recorded source, candidate preview and synthesis, and the composition reads. The spellbook's bind, bind_inactive
+ registry (`research_set(...)`, `create_research_set(...)`, `list_research_set_names()`) and the agent verb surface
+ through borrowed read-only `mutation_research` properties; frames carry no mutation dimension. The full verb

### src_architecture: cleanup sequence re-absorption note  (-2 +1 lines)
- to report. Re-absorbed 2026-08-02 from the patch lane and extended from three
- types to seven; each `cleanup()` was verified present on the class named.
+ to report.

### src_architecture: runtime type names re-absorption note  (-2 +0 lines)
- Re-absorbed 2026-08-02 from the patch lane; every class below was verified to
- exist in `src/` and the enforcement citation was re-measured on the way in.

### src_architecture: runtime type names citation: patch-lane note out, range remeasured  (-2 +1 lines)
- - src/melder/aether/conduit/conduit.py:5599-5601 (the check and the raise -
- cited as :4342-4344 in the patch lane, which was off by one)
+ - src/melder/aether/conduit/conduit.py:5601-5603 (the check and the raise)

### src_architecture: extension points re-absorption note  (-1 +0 lines)
- Re-absorbed 2026-08-02 from the patch lane; every named seam verified present.

### src_architecture: invariant removed: Owner-store constants on the warm path (2026-10-03, 0.2.82  (-12 +0 lines)
- - Owner-store constants on the warm path (2026-10-03, 0.2.8221): a site plan's shared site of existence `unique` whose
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._owner_store_constant`
- `Spell._add_owned_conduit` - at conjure and, in dynamic posture, at ownership transfer - and a notch or a late
- and `SitePlanEmission._emit_shared_hit`.
- bind re-gates and recompiles the plan, so in an automatic world nothing repoints the store under a plan; a
- constant (`c{i}`, bound in the namespace at emission) instead of `spells[i]._owner_creations` on every creation;
- empty by cleanup is seen as before. An owned spell's owner store changes only through
- generation moves. Measured on the VM: -7..-17% of the plan on roots with `unique` providers (8-10 ns per site).
- provider Spell is owned by an automatic conduit and already has an owner store reads that store as a plan
- provider in a dynamic environment, one not yet owned, and every `meld.<store>` route keep the per-creation
- read. Plans are emitted at hydration from manifest rows (cold path and cache full hit alike), so no cache
- the hit read `c{i}._creations.get(sid{i})`, the miss call and the miss body are unchanged, so a store swapped

### src_architecture: invariant removed: Executor-cache world stamp (2026-10-03, 0.2.8220)  (-11 +0 lines)
- - Executor-cache world stamp (2026-10-03, 0.2.8220): the conduit creation-cache bundle records the world its executor
- EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`,
- `SpellbookCreationSystem._stage_spell_payloads_at_conjure_end` and
- `src/melder/utilities/caching_system/caching_system.py:CachingSystem.set_world_stamp`.
- byte-identical full hit; a world that only removed a spell recompiles once (the former surplus-id full hit is
- creation or a non-resolvable definition (ids the executor tier never counts, because they carry no payload)
- field) never matches, so the rule fails closed.
- payloads were staged in - the structural tier's world stamp (sorted pool ids, posture, sorted borrowed ids) - and
- recompiles phases 8-11 and re-stages the bundle, as a missing live spell does; a repeat world is still a
- retired). Generation 19 retires bundles without the field; "" (an empty store, a bundle written without the
- the executor tier admits a full hit only when the live world carries it. A world that differs only by an existing

### src_architecture: invariant removed: Annotation matching by address key (2026-10-03, 0.2.8218;  (-7 +0 lines)
- - Annotation matching by address key (2026-10-03, 0.2.8218; SUPERSEDED by the kind rule above at 0.2.8222): Phase 3
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:CompilerPhase3._matches_annotation` and `CompilerPhase3._build_candidate_index`.
- annotation's key against each spell's frame key and its type key - so a string category sharing a class's name
- bound bare satisfies a consumer annotated with its class; a binding resolves identically under a `TYPE_CHECKING`
- made its members providers of that class (the MelderOps "spectrum" collision). What survives: an existing object
- matched a constructor annotation to candidate spells by the lowercased name every spell address uses - the
- string and a runtime class object; ambiguity and Phase 4's one-address rule are unchanged.

### src_architecture: invariant removed: Lazy `instance_results` (2026-10-03, 0.2.8217)  (-5 +0 lines)
- - Lazy `instance_results` (2026-10-03, 0.2.8217): a dict-mode site plan builds a dict literal of exactly the values a
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_results_literal` and `SitePlanEmission._place`.
- generic construction reads, where that construction runs, and nothing on the warm path; misses take no dict
- parameter. Direct-mode plans are byte-identical; cache generation 17 retires the eager executors. Measured on
- the VM: -26..-32% of the plan on roots over existing objects.

### src_architecture: invariant removed: Many registration trim (2026-10-02, 0.2.8216)  (-11 +0 lines)
- - Many registration trim (2026-10-02, 0.2.8216): a disposal-bearing `many` creation registers into its scope store with
- EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations.register_many`,
- `Creations._append_many_locked` and
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_many`.
- a registration whose disposal declaration disagrees with the key's entries, a state the spell id already makes
- disposal_methods)` (explicit store-lock acquire/release); `add_many_creations` keeps its signature and refuses
- impossible. Disposal order, failure aggregation, the cleaned-store refusal and extract/restore rows are
- one list append; the Spell's disposal list is recorded once per key in a `ManyDisposalBucket` whose `entries` is
- plan -15..-34% and whole meld -7..-23% on transient roots with disposal; singletons unchanged.
- the live bucket itself. Emitted plans and executors call `Creations.register_many(spell_id, instance,
- unchanged; cache generation 16 retires executors emitted with the old keyword call. Measured on the VM:

### src_architecture: invariant removed: Injected dependencies resolve on their first direct meld (  (-15 +0 lines)
- - Injected dependencies resolve on their first direct meld (2026-09-30, 0.2.8215). A target-local resolution pass -
- EVIDENCE:
- Every meld door already reads that flag: the deferred lane runs the dependency's own full target pass (5-11)
- Phase 6 stamps every node of the target's scope valid, so a dependency first compiled inside the consumer's plan
- Verdicts, the Book validation flag, warm melds and the conduit-wide pass are unchanged, and no caller step is
- `SpellbookCreationSystem.run_resolution_phases_for_target_spell` and
- `src/melder/aether/conduit/meld/meld.py:Meld._ensure_runtime_resolution_ready`.
- `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.flag_dependencies_without_own_plan`,
- a consumer's first meld after a late bind - publishes root blueprints only to its target (2026-09-19) and its
- because it is not its Phase 5 root, checks its verdict, and the rebuild window publishes its context, so the
- direct meld returns the instance the consumer's plan stored (unique_per_conduit, unique) or a new one (many).
- needed.
- reads valid with no plan of its own. On success the pass therefore flags each such dependency the Book owns -
- resolvable, not an existing creation, with no phase-11 plan, no published CreationContext and no flag yet -
- with `resolution_required`, under the dependency's spell lock taken after the target's (the build-lock order).

### src_architecture: invariant removed: Per-frame spell worlds record and restore intact (2026-09-  (-23 +0 lines)
- - Per-frame spell worlds record and restore intact (2026-09-30, 0.2.8213-0.2.8214). Every Aether root twin carries
- EVIDENCE: `src/melder/aether/aether.py:Aether.process_wide_unique_spell_ids`,
- `RestoreEngine._book_bind_order` and
- `src/melder/aether/aether_configuration.py:AetherConfiguration.from_recorded_payload`,
- `src/melder/crystallizer/crystal_loader_system/load_admission.py:LoadAdmission._retarget_payloads`.
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._replay_aether_configuration`,
- `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.custody_key`,
- `src/melder/crystallizer/persistence/persistence_profile.py:PersistenceProfile.get_spell_crystal`,
- binds one spell id in two frames. Spell custody is keyed by the spell id's uniqueness scope: the bare spell id
- fires from a restore; it refuses before anything is built when the live regime is process-wide and the record
- frame. RecordVersion 4.0.0 fences the new keys from older readers; 3.x records stay readable (their keys are
- installs it while the live regime can still change - no configuration installed, no frame born - so the frames
- keys and `describe_spell_crystals()` keys are custody keys; removal and activity address one frame's copy, and a
- lookup by a bare spell id without a frame answers its lowest key. Restore replays custody per Book: bind order,
- process-wide keys). Recording still changes no runtime behaviour.
- so a class bound in two frames keeps one crystal per frame. Journal entries, checkpoint and formation payload
- stage 1 files a shortfall naming both regimes and rebuilds under the live one, so the sealed-regime guard never
- stage 5 births seal it. When the live regime is already fixed (a configured Aether or a live frame) and differs,
- the granting conduit's Book) are per Book, and a formation retarget re-keys frame-scoped keys for its target
- the member-index lookup and recorded-to-live spell translation (selections, staged anchors, contract grants by
- the spell-id regime in force (`process_wide_unique_spell_ids`, read from `Aether.process_wide_unique_spell_ids`;
- the utility system's logger re-emission reads it only from an initialized, uncleaned Aether), and restore stage 1
- under process-wide ids (default worlds keep their record shape) and `"<spell_id>@<frame>"` under per-frame ids,

### src_architecture: invariant removed: Shared document-view initialization (2026-09-28)  (-5 +0 lines)
- - Shared document-view initialization (2026-09-28): a non-None section tuple signals a complete index,
- EVIDENCE: `src/melder/utilities/ai_native_support_tools/system_document_view.py:SystemDocumentView._index`.
- publish one completed reference. This runtime ordering is independent of build-time asset integrity.
- so its key map is published first. Concurrent first reads may build equivalent immutable indexes;
- warm reads stay lock-free and failed map construction is retryable. Payload and adjacency loads each

### src_architecture: invariant removed: Compiler pool reads (2026-09-26)  (-9 +0 lines)
- - Compiler pool reads (2026-09-26): a compiler pass never iterates the live `Spellbook._spell_id_pool`; it
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:CompilerPhase5`.
- Phase 9 contract and runtime processors raised RuntimeError, which surfaced as PhaseExecutionError).
- Spellbook lock and passes run without it at meld time, so a concurrent bind used to abort revalidation. Phase 5
- iterates a copy taken in one call (Phases 3, 4, 5, 6 frame-wide and the Phase-8 walk). Pool writers hold the
- link sever, uncontract or unbind): every Phase 8/9 lookup that misses raises KeyError naming the spell id, and
- revalidation. No lock was added. A meld-time pass can therefore lose a spell between its phases (a concurrent
- sees only ids with a registered SpellSystemState, which leaves a half-registered bind to its own
- the target pass records it as a visibility failure, so the meld raises SpellbookValidationError (0.2.8227; the

### src_architecture: invariant removed: Override key-set plans and the site-plan runtime (2026-09-  (-14 +0 lines)
- - Override key-set plans and the site-plan runtime (2026-09-26): each hydrated root of the many_only and
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:SitePlanOverrideRuntime`
- The normal plan's per-conduit or SpellSpace root is built under its door's guard instead (Door-held first
- after. A shared site is read lock-free where it is placed and built in an out-of-line miss that builds its
- and `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission`.
- builds only the sites the unsupplied parameters demand, so a supplied dependency and everything only it needs
- builds, 0.2.73).
- children first and then takes its slot guard, so a plan never holds one build lock across another site's
- constructor and a stored shared site's children are not rebuilt. Operands depend on the key set only; supplied
- generalized families owns one `SitePlanOverrideRuntime`. Its normal plan (the empty key set) is the family's
- inner no-overrides executor; an override meld runs the plan compiled for its payload's key tuple, which
- is never constructed. Plans are compiled once per key set under the runtime's compile lock and read lock-free
- receiving code binds that position to that name. Key errors keep their texts and are not cached.
- values are never inspected beyond the equal-rank conflict guard. Operands go positionally only where the

### src_architecture: invariant removed: Deterministic codegen signatures and live contract overrid  (-12 +0 lines)
- - Deterministic codegen signatures and live contract override operands (2026-09-26): the compiler's
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:CodegenSignature`
- and `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:CodegenCreationSchemaHelpers.resolve_contract_override_ref`.
- are a hash surface: a `SpellContract`/`SpellMap` `override` value (renamed from `spell_override`; any
- executor signatures agree across interpreter processes without a generation bump. Persisted phase-11 rows
- hashes the pool-invariant rows once per pass. Override melds read the same resolved rows through the
- instances as address-free tuples and leaves every other value's bytes unchanged, so the creation cache's
- key-set plans (2026-09-26).
- object is allowed) is written as itself only when it is a scalar, otherwise as a value-only reference to
- phase-side and phase-11 facades delegate to; the freeze rule renders callables and default-`repr`
- signature serializer, hasher and freezer are one stdlib-only leaf (`CodegenSignature`) that both the
- the consumer's descriptor that the no-overrides hydration resolves to the live object at meld. Phase 8

### src_architecture: invariant removed: Structural snapshot (2026-09-26)  (-11 +0 lines)
- - Structural snapshot (2026-09-26): the conduit cache bundle (generation 15) carries, beside every executor
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:StructuralSnapshot`
- and `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._prepare_spellbook_for_conjure`.
- behave identically after a replay; rows carry no index ULID, so a crystallizer restore still hits.
- book's pool ids, posture and borrowed ids, and marked replayable only when no pool object or spellframe
- capture at conjure end refreshes the record from durable state without rewriting an unchanged file. Every
- invalidation event writes through the registry, so bind, notch, removal, contract grant and transfer
- keyed by the spell id plus the (module, qualname) of the types its sockets match on, stamped with the
- overrides `__eq__`. A later conjure whose owned spells ALL hit replays those results through the same
- payload, a value-only record of the spell's phase 3-4 results (dependencies, topology sockets, verdict)
- registry helpers phases 3-4 use and skips phases 1-4; every other case runs the phases unchanged, and the

### src_architecture: invariant removed: Process-stable spell ids and complete cache bundles (2026-  (-8 +0 lines)
- - Process-stable spell ids and complete cache bundles (2026-09-26): bind fingerprint inputs contain no
- EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile` (until 0.2.8257) and
- `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._stage_spell_payloads_at_conjure_end`.
- memory address - repr, parameter-default, signature and init_signature text are hashed address-free and
- outside the live pool.
- own compile and drops non-live ids (generation 12), so a full hit never hydrates a plan naming a spell id
- processes; display reprs are unchanged. A non-full-hit conjure rebuilds the conduit cache bundle from its
- untruncated - so every spell, callables and default-repr instances included, keeps one id across

### src_architecture: invariant removed: Door-held first builds (2026-09-26, 0.2.73)  (-14 +0 lines)
- - Door-held first builds (2026-09-26, 0.2.73): a CreationContext door holds its root's build lock from its
- Build-once, purge waiting for an in-flight build, the cleaned-store refusal, lock order and the hook
- Child sites, override key-set plans and a runtime built without a door route keep their guards too.
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_miss`,
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:SitePlanOverrideRuntime._compile_normal_plan`
- and `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:_build_site_plan_runtime`.
- at link and upgrade, cluster stores are re-resolved per call, and unique doors hold the Spell lock.
- attribute the door read (`_conduit_creations` or `_spellspace_creations`, each assigned once per Meld),
- children are built, so a same-thread nested meld that published it meanwhile is returned. Other roots
- keep their guard because the plan cannot prove it names the door's lock: lineage stores are repointed
- lanes' created flag are unchanged; a first build takes each build lock once.
- recheck until the executor returns. For a unique_per_conduit or unique_per_spell_space root the normal
- site plan it calls takes no guard of its own for the root: the plan reads the root's store from the Meld
- so the guard is the door's, and a second take only re-entered it. The root still rechecks after its

### src_architecture: invariant removed: Creation-cache release compatibility (2026-09-24)  (-9 +0 lines)
- - Creation-cache release compatibility (2026-09-24): generation 9 stores the canonical Melder
- EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem` and
- Python cache-tag agreement. A missing, malformed or different release produces the existing cold
- The stored release survives normalization and emission. No version check enters ordinary meld,
- `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`.
- and Crystallizer RecordVersion and durable records are unaffected.
- cache before individual payloads are exposed. Normal conjure rebuilds and emits the fresh envelope;
- release in each conduit .meldercache envelope. Admission requires exact release, format-generation and
- subsequent matching runs can reuse it. Old generation-8 readers reject generation 9 on downgrade.

### src_architecture: invariant removed: Dynamic named recording stores detached ancestor values in  (-9 +0 lines)
- - Dynamic named recording stores detached ancestor values inside each surviving named twin.
- Conduit-only tombstones retire scopes without removing their shared Book; sealed history is
- EVIDENCE: `src/melder/crystallizer/crystal_analysis/conduit_hierarchy.py:ConduitHierarchy`,
- IDs and no saved application objects. Schema major 3 fences root-only readers. Live restore requires
- `src/melder/aether/spellbook/spellbook.py:Spellbook._conjure_logic`.
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._replay_one_book`,
- caller quiescence of ordinary scope cycles. Public frame setup and normal conjure still emit the
- immutable. Both replay drivers use the common per-Book root/parent-first reconstruction with fresh
- owning Book and settled frame twins even when rich configuration was already locked.

### src_architecture: invariant removed: Nexus named lifecycle replaces existing payloads and clear  (-6 +0 lines)
- - Nexus named lifecycle replaces existing payloads and clears names/parents into pooled records
- EVIDENCE: `src/melder/nexus/frame_descriptor_manager.py:FrameDescriptorManager._publish_conduit_record`,
- `src/melder/nexus/rift/command_system/command_system.py:CommandSystem._get_conduit_by_name_locked`.
- before idle publication. Same-ID named reuse keeps compiled membership; new/deleted IDs retain
- changed live names. Anonymous cycles remain local, and no in-command Rift refresh is introduced.
- explicit Rift refresh. Capability/codegen getters resolve the published authorized ID and reject

### src_architecture: invariant removed: Pooled hook ownership (2026-09-22)  (-5 +0 lines)
- - Pooled hook ownership (2026-09-22): normal roots own stable Conduit/Meld baseline dictionaries
- Other normal roots and frozen configuration remain independent. Callback objects are borrowed.
- copied from configuration, including empty dictionaries. Explicit shared updates publish only
- through normal roots and preserve dictionary identity; inheritors see new contents without a tree
- walk. Local lifecycle event lists shadow shared events; local Meld maps are isolated copies.

### src_architecture: invariant removed: Pool return completes creation disposal before clearing lo  (-5 +0 lines)
- - Pool return completes creation disposal before clearing local lifecycle hooks, restoring temporary
- Meld references and publishing the scope as idle. Both manual and managed SpellSpaces, including
- prewarmed shells, follow this ordering. A Space marks a borrowed owner-local map as temporary even
- when its modified flag is set; baseline-only acquisition needs no map copy or reset lock.
- without registering callbacks itself. Acquisition selects the immediate owner's current local map

### src_architecture: invariant removed: Hook setters/register methods validate full batches and us  (-9 +0 lines)
- - Hook setters/register methods validate full batches and use existing writer locks. Ordinary Meld
- EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._initialize_hook_baselines`,
- Shared updates keep existing per-event visibility, not a whole-operation snapshot guarantee.
- `Conduit._prepare_for_pool`, `Conduit.prewarm_spellspaces`,
- `src/melder/aether/conduit/meld/meld.py:Meld._reset_pooled_meld_hooks` and
- `src/melder/aether/conduit/spell_space/spell_space_pool.py:SpellSpacePool.prepare_object`.
- and lock only for restoration; diagnostic hooks_modified reads use the existing locks. Active Spaces
- execution adds no new flag check, lock, version poll or hierarchy scan. Return paths check a bool
- retain their selected source when an owner switches local/shared maps until their next acquisition.

### src_architecture: invariant removed: Bind lifecycle hooks (2026-09-22)  (-8 +0 lines)
- - Bind lifecycle hooks (2026-09-22): Book and normal-Conduit add_bind_hooks append ordered
- Bind owns immutable callback tuples seeded once from the selected configuration. Runtime updates
- Callbacks run outside Bind's construction lock, within existing transaction admission. Return
- EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.capture_hooks` and
- `src/melder/aether/spellbook/spellbook.py:Spellbook.add_bind_hooks`.
- pre/activation/post callback sequences; clear_bind_hooks removes all stages for future binds.
- remain Book-local after configuration freeze; an in-flight bind retains its captured stages.
- values are ignored. Post is registration completion, not an outer-transaction commit callback.

### src_architecture: invariant removed: Pre receives the supplied reference; activation/post recei  (-9 +0 lines)
- - Pre receives the supplied reference; activation/post receive the actual Spell. Native identity
- Book teardown explicitly cleans Bind and releases callback references without disposing callbacks.
- EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic`,
- Recording carries bind:pre/bind:activation/bind:post presence in complete Book twins; full restore
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:SpellbookConfiguration.freeze`.
- `src/melder/aether/spellbook/spellbook.py:Spellbook._emit_bind_hook_presence` and
- framework is introduced. Existing application-object creation hooks still execute during Meld.
- remains established before activation and no automatic rehashing or published-state mutation
- reports missing callback code and live graft uses receiving-Book hooks. No callback serialization.

### src_architecture: invariant removed: Graduation configuration and hook ownership (2026-09-22)  (-5 +0 lines)
- - Graduation configuration and hook ownership (2026-09-22): every graduated root owns a new empty
- Book. Omitted local configuration means fresh defaults. With frame-wide sharing enabled, the Book
- adopts the canonical frozen frame configuration and rejects a different supplied object. Sharing
- canonical shared configuration; the frame owns it. The setting is frame-local, not process-wide.
- policy does not share Book registries, definitions or cleanup. Individual Books never retire the

### src_architecture: invariant removed: Old Book-specific configured hooks, runtime Bind changes a  (-9 +0 lines)
- - Old Book-specific configured hooks, runtime Bind changes and lesser/Space Conduit/Meld overlays
- Conduit/Meld events use configured defaults with exact Book event-list precedence; local runtime
- EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.upgrade_to_normal`,
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:SpellbookConfiguration`.
- `src/melder/aether/spellbook/spellbook.py:Spellbook._conjure_existing_conduit`,
- are discarded during successful graduation. Selected configuration defaults may deliberately seed
- callbacks again. Bind captures immutable seed tuples once and owns later add/clear independently.
- mutation APIs preserve configuration-owned lists. Callback objects are borrowed, never cloned or
- serialized. Configuration setters freeze; runtime hook APIs remain the mutation surface.

### src_architecture: invariant removed: Scoped creation purge (2026-09-21)  (-16 +0 lines)
- - Scoped creation purge (2026-09-21): Conduit and SpellSpace expose instance shortcuts and normal
- ConduitMeld/SpellSpaceMeld doors enforce scope authority. Creations alone owns
- EVIDENCE: `src/melder/aether/conduit/meld/meld.py:Meld._resolve_purge_spell`,
- Meld selectors. Shared discovery inspects an instance's class before existing lookup; concrete
- Spell lock before the store lock; the other slotted modes take the store's slot guard before
- `src/melder/aether/conduit/creations/creations.py:Creations.purge`.
- `src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld.purge`,
- `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld.purge`,
- after detachment and lock release. Definitions, contexts and scope objects remain usable.
- it (2026-09-25); many takes only the store lock. Disposal occurs
- purge_all=True removes all retained target entries; False requires the supplied instance and
- recovery is added. Purge changes no existing meld hot path or compiler-cache policy.
- removes only its entry. An absent entry returns zero. No reverse discovery index or qualifier
- retirement locks, paired live/disposal-map removal and existing disposal helpers. Space purge
- stays local. Conduit many/per-conduit removal stays local; unique, lineage and cluster require
- the spell owner, lineage root and elected leader respectively. Unique retirement takes the

### src_architecture: invariant removed: Non-resolvable definitions keep descriptive local topology  (-5 +0 lines)
- - Non-resolvable definitions keep descriptive local topology but are excluded from Phase-5 executable
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:CompilerPhase3`.
- signature position/kind; those IDs never expand the constructor DAG. Both planner variants retain
- snapshots and Phase8-11 planning. OVERRIDE_REQUIRED sockets retain selected reference IDs and actual
- the required-input values. Defaulted parameters keep PLAIN semantics and ordinary Python values.

### src_architecture: invariant removed: Nexus binds capability and selected dependency/reference/d  (-6 +0 lines)
- - Nexus binds capability and selected dependency/reference/direct-base links into the existing
- EVIDENCE: `src/melder/nexus/frame_descriptor_manager.py:FrameDescriptorManager._build_published_relationships`
- and `src/melder/nexus/rift/frame_viewer/view_spell.py:ViewSpell.describe_spell_relationships`.
- binding-payload section. ViewSpell/FrameViewer relationship navigation filters both endpoints
- external changes still require the normal Rift projection refresh. Source/history remains in MR.
- through current ACL visibility. Late Phase3 compilation republishes through the existing book sink;

### src_architecture: invariant removed: SpellCrystal records the native capability.  (-7 +0 lines)
- - SpellCrystal records the native capability. Active/staged restore and fresh/merge graft forward
- EVIDENCE: `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.describe`,
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py:GraftRunner._bind_selected`,
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._bind_one_active`,
- `src/melder/crystallizer/persistence/record_version.py:RecordVersion`.
- it through normal bind verbs; absent legacy fields default to True. Record schema major 2 prevents
- older readers from silently discarding False. Graph links rebuild from restored bindings and selections.

### src_architecture: invariant removed: Selector-sensitive required inputs reuse the existing fram  (-5 +0 lines)
- - Selector-sensitive required inputs reuse the existing frame-key watcher. A successful structural
- EVIDENCE: `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates._extract_collection_frame_keys`
- and `src/melder/aether/conduit/meld/meld.py:Meld._ensure_lineage_resolvable`.
- rerun gates the prior conduit-local resolution verdict, so the existing Phase5-11 rebuild replaces
- stale executors after provider selection changes. No alternate cache lifecycle is introduced.

### src_architecture: invariant removed: Phase-5 dependency visibility is broader than canonical ar  (-5 +0 lines)
- - Phase-5 dependency visibility is broader than canonical artifact publication. Conduit-wide
- Borrowed and unselected dependency Spells retain their executable artifacts and creation contexts.
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:CompilerPhase5`.
- The complete visible graph remains available for validation and consumer compilation.
- resolution publishes to the book's owned Spells; local resolution publishes only to its target.

### src_architecture: invariant condensed: per-conduit verdicts  (-14 +8 lines)
- (`ConduitResolutionState.forget_spell`), with no RiskManager callback - lineage membership in the risk model is
- Lock order stays registry -> conduit state; a dropped conduit is popped under that lock before it is cleaned, so
- `SpellSystemStates._forget_resolution_verdicts_locked` for the removed current spell id (reason
- `cleaned_up_spell`) and `register_index` calls it for `selected_spell_id` (reason `register_or_rebind`); each
- alive in its scope: for `many` the replacement builds anew; for a slotted existence (`unique_per_conduit` and kin)
- as against any stored shared instance (owner ruling 2026-10-03).
- content-stable, so a rebind of the same class at the same address after `cleanup_spell` mints the same id for a
- id that `register_index` publishes starts with none. `unregister_index` calls
- it keeps its id-keyed slot, the replacement's first meld there returns it, and an override against it is refused
- new Spell with no compiler artifact and a structural state that late binding makes valid eagerly; before 0.2.8219
- owner-scoped and `RiskManager.register_spell` recomputes it from the live verdict on the rebind. Spell ids are
- the dead definition's `valid` was read as current, phases 5-11 were skipped and the context builder raised.
- the helper never visits a cleaned state. The surviving product of a removed definition is deliberately left
- visits every live conduit state under the registry lock and pops the id's spell-level and root-level verdict
+ A spell_id is the object's code, so a rebind of the same class after `cleanup_spell` mints the same spell_id for a
+ State). The surviving product of a removed definition is deliberately left alive in its scope: for `many` the
+ id that `register_index` publishes starts with none.
+ instance (owner ruling 2026-10-03).
+ new Spell; without the retirement the removed definition's `valid` verdict would be read as current. The
+ replacement builds anew; for a slotted existence (`unique_per_conduit` and kin) it keeps its id-keyed slot, the
+ replacement's first meld there returns it, and an override against it is refused as against any stored shared
+ retirement and its lock order are in src_components (Subcomponents: SpellSystemStates Registry, Conduit Resolution

### src_architecture: invariant history trim 1  (-3 +1 lines)
- a mixed-case descriptor name gets a new spell id once, because the bind fingerprint hashes default reprs.
- construction; the Phase-4 warning SPELLMAP_BINDING_NAME_NOT_NORMALIZED is retired; the structural snapshot
- records the normalized name, so its rows and every cache format are unchanged. A consumer whose default carries
+ construction.

### src_architecture: invariant history trim 2  (-2 +1 lines)
- recorded name as a category and file a `spell_crystal` shortfall. Cache generation 20 retires bundles captured
- under the name matcher.
+ recorded name as a category and file a `spell_crystal` shortfall.

### src_architecture: invariant history trim 3  (-2 +1 lines)
- (values by reference; it never freezes or validates). The Aether record carried only the logger half of its
- configuration until 0.2.8213; it now carries the regime too (next invariant).
+ (values by reference; it never freezes or validates).

### src_architecture: invariant history trim 4  (-5 +2 lines)
- 2026-09-27). A pooled lesser handle is not checked on `Conduit.meld`, the hottest door: using a scope
- acquisition clears it, and a released space refuses meld and purge. The flag's two writes per cycle are
- after cleanup stays a caller contract violation there.
- call when none is open), so a scope cycle costs no more than before on 3.14t and the GIL build (measured
- paid back on the same path (inline managed exit and stack push, one idle-deque read, no SpellSpace sweep
+ `Conduit.meld`, the hottest door: using a scope after cleanup stays a caller contract violation there.
+ acquisition clears it, and a released space refuses meld and purge. A pooled lesser handle is not checked on

### src_architecture: invariant history trim 5  (-6 +3 lines)
- annotated with a `TYPE_CHECKING`-only type keeps one spell id across processes. The class binding
- evaluates once its `TYPE_CHECKING` imports are bound, enforced by a unit guard.
- fingerprint (affected classes changed id once when this landed; until 0.2.8257 - the spell_id now
- profile reads class-level annotations the same way, so a field typed with such a name counts in the
- reads an annotate function's code, never an annotation's value). Every annotation in `src/melder`
- source text, never a ForwardRef owner or a memory address. Bind fingerprints hash that text, so a class
+ annotations the same way. Every annotation in `src/melder` evaluates once its `TYPE_CHECKING` imports are
+ bound, enforced by a unit guard.
+ source text, never a ForwardRef owner or a memory address. The class binding profile reads class-level

### src_architecture: invariant history trim 6  (-3 +1 lines)
- Purge takes the same build lock before the store lock. Cache generation 10 rejects executors emitted
- cannot form a wait cycle; the former store-held builds deadlocked against unique builders and purge.
- with the previous locking. Warm meld paths take no lock, unchanged.
+ cannot form a wait cycle. Purge takes the same build lock before the store lock. Warm meld paths take no lock.

### src_architecture: invariant history trim 7  (-2 +1 lines)
- True preserves the existing v4-binding fingerprint; False uses a separate hash domain (until 0.2.8257;
- resolvable is a binding-manifest field since 0.2.8258 and no part of the spell_id). Application
+ Since 0.2.8258 resolvable is a binding-manifest field and no part of the spell_id. Application

### src_architecture: invariant history trim 8  (-1 +1 lines)
- never refuses these parameters. Cache generation 11 retires executors emitted before this wiring.
+ never refuses these parameters.

### src_architecture: invariant history trim 9  (-3 +1 lines)
- EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
- defaults retain existing DI inference. The compiled-cache semantic version advances to 8 so the
- existing mismatch check automatically rejects plans using the former precedence.
+ defaults retain existing DI inference.

### src_architecture: invariant history trim 10  (-2 +1 lines)
- 2026-10-01: this said teardown was identity-checked). The explicit reset
- its `cleanup()` returns at the `_cleaned` check before that reset (corrected
+ its `cleanup()` returns at the `_cleaned` check before that reset. The explicit reset

### src_architecture: invariant history trim 11  (-2 +1 lines)
- max_transaction_wait_time_in_seconds (recounted 2026-09-27; this said twelve,
- with six disable flags) - and then calls
+ max_transaction_wait_time_in_seconds - and then calls

### src_architecture: invariant history trim 12  (-2 +1 lines)
- check - a leased space melds whether or not it is the top of its thread's stack (corrected 2026-09-27:
- this line claimed an active-spellspace rule the source never had).
+ check - a leased space melds whether or not it is the top of its thread's stack.

### src_architecture: invariants: pointer to src_components  (-0 +12 lines)
+ (Normal and Lesser) and Component: Spellbook Core (Binding and Conjure); custody keys, per-frame record replay,
+ - Component mechanics recorded here before 0.2.8228 live in their src_components entries, not here: the
+ And ACL Managers; the document-view key map in Component: Packaged Hardcopy Documents And Public Helper Exports.
+ Component: SpellCompiler and Validation Pipeline; `many` registration, slot guards and purge in Component:
+ Creations and SpellSpace and Component: Meld Resolution Runtime, which also carries the injected-dependency flag
+ Module-World Surfaces; the named-record lifecycle and published capability links in Component: Nexus Descriptor
+ and pooled Meld hooks; hook baselines, pool return, bind-hook stages and graduation in Component: Conduit Runtime
+ creation-cache envelope (generations 9, 12, 15 and 19 - release admission, complete bundles, the structural
+ key-set plan runtime, door-held roots, lazy `instance_results`, owner-store constants, deterministic codegen
+ named-scope recording and the native-capability record in Component: Crystallizer Root, Persistence Record, And
+ signatures, compiler pool reads, Phase-5 publication, OVERRIDE_REQUIRED sockets, the selector watcher) in
+ snapshot, the executor world stamp) in Component: Spellbook Core (Binding and Conjure); site-plan emission (the

### src_architecture: failure-mode history trim 1  (-2 +1 lines)
- the class was accepted and matched by name as a label, so a same-named single annotation resolved its members.
- typing.Protocol." (0.2.8222, Breaking). Any other non-string, non-class object is refused the same way. Before,
+ typing.Protocol." (0.2.8222, Breaking). Any other non-string, non-class object is refused the same way.

### src_architecture: failure-mode history trim 2  (-2 +1 lines)
- and the remedy (install it before the first frame, or keep the sealed value). Before 0.2.8209 the
- configuration was installed and reported while the old regime stayed in force.
+ and the remedy (install it before the first frame, or keep the sealed value).

### src_architecture: failure-mode history trim 3  (-3 +1 lines)
- 0.2.8214 one frame's copy of a class bound in two frames was lost at record time while the restore reported
- complete.
- its mirror (0.2.8213). Before 0.2.8213 such worlds restored under process-wide ids with no report, and before
+ its mirror (0.2.8213).

### src_architecture: failure-mode history trim 4  (-2 +1 lines)
- Nexus's policy was replaced, unfrozen, under existing Rifts.
- RuntimeError "Cannot reconfigure Nexus while it is active. Deactivate it first." (0.2.8210). Before, a live
+ RuntimeError "Cannot reconfigure Nexus while it is active. Deactivate it first." (0.2.8210).

### src_architecture: failure-mode history trim 5  (-2 +1 lines)
- "not found" while its frame's Cloud returned it.
- (0.2.79). Before 0.2.79 `Aether.get_conduit_by_name` answered over roots only, so a live named lesser raised
+ (0.2.79).

### src_architecture: failure-mode history trim 6  (-6 +4 lines)
- conduit-verdict refusal printed "(none recorded)" and every message carried 64-character spell ids. A
- conjure aborted with PhaseExecutionError "DagNode cannot depend on itself". A spell that only needs a cycle is
- constructor that takes its own class is refused the same way (SELF_DEPENDENCY, naming the parameter); before,
- member.
- named as its consumer ("cannot be built: it needs 'Y' ... 'X' itself is not part of that cycle"), not as a
- warnings are only counted, and Melder's own consistency codes are marked [internal] to report. Before, a
+ cycle"), not as a member.
+ needs a cycle is named as its consumer ("cannot be built: it needs 'Y' ... 'X' itself is not part of that
+ that takes its own class is refused the same way (SELF_DEPENDENCY, naming the parameter). A spell that only
+ warnings are only counted, and Melder's own consistency codes are marked [internal] to report. A constructor

### src_architecture: failure-mode history trim 7  (-3 +1 lines)
- into the idle shell and the next lease was served what it built, and a lesser cleaned inside its own
- managed SpellSpace made that block's exit raise "stack corruption".
- or destroyed inside its own block leaves the stack without error. Before 0.2.8203 a kept handle melded
+ or destroyed inside its own block leaves the stack without error.

### src_architecture: failure-mode history trim 8  (-3 +1 lines)
- first failure ended its disposal and the original exception was dropped, and before 0.2.8203 conduit
- paths only logged these groups.
- per failing disposal method, chained from what that method raised (0.2.80); before 0.2.80 an object's
+ per failing disposal method, chained from what that method raised (0.2.80).

### src_architecture: failure mode removed: A warm creation cache no longer replays an executor compil  (-6 +0 lines)
- - A warm creation cache no longer replays an executor compiled in another world (fixed in 0.2.8220): a world that
- EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`.
- differs only by an existing creation or a non-resolvable definition used to be a full hit, so a consumer's
- executor compiled without a provider raised TypeError ("missing 1 required positional argument") at its first
- manifest references unknown spell_id"); both worlds now recompile and resolve as a cold cache does.
- meld after the provider was bound, and a plan naming a removed provider raised RuntimeError ("generalized

### src_architecture: failure mode removed: A definition melded, removed with `cleanup_spell` and boun  (-8 +0 lines)
- - A definition melded, removed with `cleanup_spell` and bound again at the same address (same class, spellframe and
- EVIDENCE: `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates.unregister_index`
- The replacement is resolved again per conduit on its first meld there; the two sequences that skip the first meld
- and `tests/integration/melder/aether/conduit/test_rebind_after_first_meld_integration.py`.
- exists." in the scopes that resolved the first definition (fixed in 0.2.8219; the builder's guard is unchanged).
- it is granted again; consumers of the removed definition rebuild against the next binding at that address.
- name) no longer fails its next meld with RuntimeError "Cannot build CreationContext before spell_codegen_creation
- were never affected. A peer that resolved the removed definition through a contract melds the replacement once

### src_architecture: failure mode removed: `with conduit:` no longer holds the conduit lock (Breaking  (-3 +0 lines)
- - `with conduit:` no longer holds the conduit lock (Breaking, 0.2.8203): code that used it as a lock now
- disposes the scope at block exit. `Cleanable.using_cleanup()` and `async_using_cleanup()` let cleanup
- errors propagate (0.2.8203; they used to be swallowed).

### src_architecture: failure mode rewritten: A meld that races a link sever, an uncontract or an unbind  (-6 +3 lines)
- - A meld that races a link sever, an uncontract or an unbind of a spell its resolution pass is planning no
- 0.2.8227): it raises SpellbookValidationError, as a meld starting a moment later does, and the next meld
- from the spell lookup." or "... SpellRuntimeProcessorStrategy could not resolve spell_id ..."; fixed in
- longer fails with PhaseExecutionError ("Phase 'injection_plan_local' ... Occurrence spell could not be resolved
- raising "Cannot build CreationContext before spell_codegen_creation exists."
- resolves against the current links and contracts. After an uncontract the old failure also left the next meld
+ - A meld that races a link sever, an uncontract or an unbind of a spell its resolution pass is planning raises
+ SpellbookValidationError, as a meld starting a moment later does, and the next meld resolves against the current
+ links and contracts (0.2.8227).

### src_architecture: failure mode rewritten: A spell bound on a live dynamic root after conjure and fir  (-4 +3 lines)
- - A spell bound on a live dynamic root after conjure and first built as a consumer's dependency no longer fails its
- first direct meld with RuntimeError "Cannot build CreationContext before spell_codegen_creation exists." (fixed
- for the conduit (a visibility failure), the meld raises SpellbookValidationError and the flag stays set.
- in 0.2.8215; the builder's guard is unchanged). If that dependency's own full target pass leaves it unresolved
+ - A spell bound on a live dynamic root after conjure and first built as a consumer's dependency, whose own full
+ SpellbookValidationError, and its flag stays set (0.2.8215).
+ target pass leaves it unresolved for the conduit (a visibility failure), makes its first direct meld raise

### src_architecture: failure mode rewritten: A dynamic conjure refused by the active-Crystallizer confi  (-3 +2 lines)
- (0.2.8211). Before, the frame was left frozen dynamic, so every later conjure there - automatic ones included -
- - A dynamic conjure refused by the active-Crystallizer configuration discipline no longer settles its frame
- inherited dynamic and was refused too.
+ (0.2.8211).
+ - A dynamic conjure refused by the active-Crystallizer configuration discipline does not settle its frame

### src_architecture: failure mode rewritten: A SpellMap default naming its provider's binding name or s  (-4 +2 lines)
- "SpellMap default could not be resolved" (fixed in 0.2.8226): the descriptor kept the lowercased name and
- - A SpellMap default naming its provider's binding name or string category in another case no longer raises
- Phase 3 compared it with the bound spell's raw one. A non-string `binding_name` on either descriptor raises
- TypeError (it was an AttributeError from `.lower()`).
+ - A non-string `binding_name` on a SpellMap or SpellContract raises TypeError (0.2.8226); a SpellMap default matches
+ its provider's binding name and string category in any case.

### src_architecture: promoted patch decisions intro  (-17 +4 lines)
- 2026-07-07 and 2026-07-12, then moved to the recomposition patch lane on
- 2026-08-01 under the reading that the Required Section Contract was a whitelist.
- BEFORE RE-ABSORPTION, not restored on faith: all 16 classes they name exist in
- It is not - it is a minimum in a fixed relative order - so they are back.
- TEXT RATHER THAN CONTRADICT IT - `BootMediator` is absent exactly because the
- The four sections below were promoted out of COMPLETED patch lanes between
- They are owner-ruled architecture decisions, not narrative, which is why they
- `LoadAdmission`, `RestoreEngine`, `ImpactEngine`, `CrystallizerBootstrap`,
- `RecordVersion`, `LoadGate`, `UserSourceIntegrityStrategy` among them), 10 of
- `refuse_on_blockers` is a keyword parameter on `RestoreEngine`, not a method,
- `src/` (`PersistenceSystem`, `AssetManagementSystem`, `CrystalLoaderSystem`,
- belong in the canonical document rather than in a lane nobody reads. VERIFIED
- custody keys (0.2.8214). The cache folder remains.
- the 11 verbs they name are real `def`s, and THE TWO APPARENT MISSES CONFIRM THE
- to "2.0.0" for non-resolvable policy, "3.0.0" for named lesser topology and "4.0.0" for frame-scoped
- topology section records it was renamed to `LoadAdmission` on 2026-07-11, and
- which is what that section calls it. At that verification, RecordVersion was "1.0.0"; it advanced
+ 2026-07-07 and 2026-07-12. When they were promoted RecordVersion was "1.0.0"; it advanced to "2.0.0" for
+ The four sections below are owner-ruled architecture decisions promoted from completed patch lanes between
+ by minor additions to "4.1.0" (0.2.8222), "4.2.0" (0.2.8242) and "4.3.0" (0.2.8258). The cache folder remains.
+ non-resolvable policy, "3.0.0" for named lesser topology and "4.0.0" for frame-scoped custody keys (0.2.8214), then

### src_architecture: persistence topology artifact path  (-3 +1 lines)
- across the crystallizer test tree validates it.
- artifacts/2026-07-09_crystallizer_philosophy_v3.md). Owner-run 614/614
- the V3 subsystem model (canonical anchor:
+ the V3 subsystem model.

### src_architecture: C1 intro moved to the top  (-9 +4 lines)
- DIRECTORY, which cannot carry a line range. It was EXPANDED into its 8 real
- One previous entry - `src/melder/mutation_research/research_set/` - was a
- Ranges are MEASURED, never estimated: `start_line`/`end_line` are the file's own
- `note` is descriptive text carried forward from the previous revision. The five
- below resolved on that pass.
- contract fields are the contract; the note is additional.
- extent and `loc` is its line count, read from disk at `verified_at`. Every path
- modules rather than given a plausible number, per the contract's rule that an
- unverified range stays UNKNOWN instead of being invented.
+ Ranges are MEASURED, never estimated: `start_line`/`end_line` are the file's own extent and `loc` is its line count,
+ Summary, not in its note.
+ description of the file beside the five contract fields; what changed in a file is recorded in the Context / Handoff
+ read from disk at `verified_at`. A directory is never an entry; it is expanded into its modules. `note` is a short

### src_architecture: C1 notes: descriptions only  (-159 +53 lines)
- (0.2.8224); describes candidates through `find_spell_by_spell_id` (0.2.8253).
- (0.2.8236); `transfer_spell_ownership` defaults to `move_creations=True` (0.2.8239) and documents the handover
- (0.2.8240); `managed_spell_meld` (0.2.8245) and the managed options on its bind facades (0.2.8242);
- (0.2.8242).
- (0.2.8248); `_resolve_spell`, `_deps_resolvable_on_target` and `_transfer_owned_dependencies` take the
- (0.2.8253).
- (0.2.8254).
- (0.2.8256).
- (0.2.8257); `_spell_index_unless_cleaned` lists the root's teardown among its readers (0.2.8259).
- (0.2.8266).
- (`non_resolvable_index_ids`, 0.2.8247); records a binding key per lineage, marks everything downstream of a
- (directory description carried forward) the formal research record: ResearchSet facade, ResearchLane, ResearchNode, TransitionEntry, ResearchJournal, ResidenceRegistry, NetworkVersioner. NOTE: this text described the DIRECTORY entry `src/melder/mutation_research/research_set/`, which was expanded into the eight modules below because a directory cannot carry a line range.
- 0.2.8250); `get_spell_by_id` renamed `get_spell_by_spell_id` and exact, `get_spell_permissions` per version,
- Book (0.2.8213-0.2.8214); hydrates Protocol frames or degrades them to categories with a shortfall (0.2.8222);
- Builds and carries the binding manifest and `binding_hash` (0.2.8258); its spell_id docstrings say code digest
- Its docstrings say a receiving policy moves the binding hash, not the spell_id (0.2.8258).
- Its spell_id docstrings say the object's code (0.2.8257).
- Records the binding hash (RecordVersion 4.3.0, 0.2.8258).
- Reports each binding a restore rebuilt differently (`binding_changes`, 0.2.8258).
- SpellContract consumers (`_mark_contract_dependents_dirty`), bind and `_apply_notch` record the binding key,
- The cache-state docstring names the binding hash in the world stamp (0.2.8258).
- The duplicate-id refusals name the one-object rule and `inspect_spell`'s stage 3 is an exact lookup (0.2.8257);
- The spell-id regime's comment says a spell_id is the object's code (0.2.8257).
- The spell_id is `SpellCodeDigest.spell_id(target)`; `sha256_profile` and its helpers are removed and
- The verdict-retirement docstring says a rebind of the same class mints its code's id (0.2.8257).
- `_apply_notch` no longer journals (0.2.8262). `_destroy_spell_index` drops a route only when it routes its
- `_apply_remove_from_index` registers the index it mints with the frame as `bind` registers its new one, and the
- `_emit_cache_file_if_required` returns the save's bool and leaves its flag cleared after a refused save (0.2.8266).
- `_is_selected_unless_cleaned`, the release registry's selected-version probe (0.2.8244); `update` and
- `_remove_contracted_spell` removes the copy of the spell_id it is given, matched by the copy's own
- `_resolve_transfer_spell` takes the explicit index step (0.2.8253). `cleanup_spell` releases the version
- `_spell_index_unless_cleaned`, the cleanup-safe index read (0.2.8229); a direct `cleanup()` removes the spell
- `adopt_children` (0.2.8238); the managed pool map, `ensure_managed_quantity`, `discard_managed_quantity`, pools
- `emit()` is best-effort: a bool, a per-writer temp file, a Windows-only rename retry, one WARNING per bundle
- `emit_cache_file` returns False for a refused save (0.2.8266).
- `find_contracted_spell` and `inspect_spell` take no conduit lock (0.2.8232); builds its SpellSpacePool and a
- `has_spell` say a spell_id names its own spell, not the head (0.2.8253).
- `notch_spell` names its target by `spell_id=` or `spell=` and checks it before and inside its transaction,
- `process_wide_unique_spell_ids` says a second bind of the same object is refused (0.2.8257).
- `register_conduit` refreshes once (0.2.8247).
- `register_index` (0.2.8247); `_migrate_inactive_members` documents the conjure stamp of pre-conjure staged versions
- `spell_id_inspector(spell)` takes the target alone (0.2.8257).
- abandon, adopt, destroy and cleanup (0.2.8243); `_rebind_spell` gives a same-spell_id rebind the new settings
- above 20 idle run the elastic band (0.2.8234).
- active only while the frame's lineage registry tracks it as its index's current version (0.2.8259).
- and `_apply_notch` marks everything downstream of the notched lineage (0.2.8250);
- and `add_to_spell_index` / `remove_from_spell_index` take `spell_id=` too (0.2.8249); after a notch every
- and `get_spell_by_source_id` meld only the named version through `_meld_live_spell_from_records_locked`,
- and the catch-up of stale dependencies before a plan compiles (0.2.8250).
- answers its own spell, no index read (0.2.8253); `cleanup_and_remove_spell` refuses the active member of an
- authority (0.2.8237).
- between its decision and its disposal (0.2.8261). `_notch_spell` checks a version it makes active and, when
- bind_inactive take the four `managed_spell_*` options (0.2.8242); bind and `_apply_notch` pass the selected
- by the notch entry (0.2.8262).
- cleaned first, the `managed` row (0.2.8243-0.2.8246); `ensure_managed_quantity` rebinds a found pool after the
- cleaned under its lock and `_has_spell_unless_cleaned` is the cleanup-safe probe (0.2.8230);
- composition emission; the old conduit/frame facades are GONE, 2026-07-11); residency calls a version
- conjure holds since conjure stamps them (0.2.8248); the five contracted-map mutators mark their key's
- conjure stamps the versions parked before it (`define_conduit_into_spells`, 0.2.8248).
- cross-frame sweeps read (0.2.8231); builds `ReleaseManagedSpell` last and cleans it after the frames (0.2.8244).
- dependencies it compiled without a plan of their own (0.2.8215); the executor-cache full hit requires
- explicit index step from a spell_id (0.2.8253).
- frame teardown logs the cloud's cluster disposal failures (0.2.8237).
- from every contract of the Book's root conduit before the disposal and sends the index destroy with no
- generation 22, "managed_settings_leave_spell_id" (0.2.8254). Generation 23, "binding_manifest_keys" (0.2.8258).
- held (0.2.8232); `cleanup_and_remove_spell` re-checks a Book torn down while it waits (0.2.8233); bind and
- index steps among them (0.2.8253); `cleanup`'s Raises names the multi-member refusal and its remedies
- index that holds parked versions and `_dispose_spell`'s refusal names the same remedies (0.2.8256).
- is refused with nothing moved (0.2.8262).
- its spell maps under the Book lock (0.2.8230); `cleanup_spell` decides through `_dispose_spell` and contracted
- key to the destroyed index and releases only the departing member's claim, by spell_id (0.2.8263).
- kinds - leasing and fresh, the inline pop, the reserve-first miss, the lease return (0.2.8245); the missing-pool
- linked peer's parked copy of the incoming version is made active again (`_activate_borrowed_spell`,
- lock, the listing resolved through the Book (0.2.8231); the version grant's docstring says what a notch does
- lookups answer by key (0.2.8231); overlapping disposals refuse and `inspect_spell` asks the frames with no lock
- managed options (RecordVersion 4.2.0, 0.2.8242), settings a replayed bind passes, not identity (0.2.8254).
- managed options (`_normalize_managed_options`, 0.2.8242), which the fingerprint leaves out since 0.2.8254.
- managed version's pool (0.2.8242-0.2.8243); `_spell_index_unless_cleaned` names its readers, the explicit
- member id (0.2.8261). `notch_spell`'s docstring and comments say a version that fails its structural check
- membership index (0.2.8236), `delete_cluster` raises disposal failures after deleting (0.2.8237).
- message without the pre-conjure staging cause (0.2.8248).
- notch (`mark_dependents_for_revalidation`) and walks on from every contract mark (0.2.8250).
- note: Phase-4 SpellContract presence check, the recheck a marked consumer's next meld runs; walks snapshots of
- note: Phase-4 refusal of a single typed parameter with several providers; names every candidate's address
- note: SpellContract descriptor; keeps binding_name as written (0.2.8226).
- note: SpellMap descriptor; keeps binding_name as written (0.2.8226).
- note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind publishes
- note: `ManagedSpellMode`: elastic, limited_quantity, queue (0.2.8242); a setting, not identity (0.2.8254).
- note: `SpellbookValidationError`; a gating Phase-4 warning (`GATING_WARNING_CODES`) is shown as a spell's
- note: a member root's facade over the cluster's team store; the elected leader's id is the purge
- note: bind-signature CARRIER for one spell version; delegates module-world analysis to crystal_analysis and carries
- note: binding pipeline; classifies the spellframe kind and refuses concrete-class frames (0.2.8222); normalizes the
- note: change control; the structural commit validator's docstring says a notched member reaches it checked
- note: cluster auto-sharing; the ordered leave (0.2.8236) and the team store the cluster owns (0.2.8237).
- note: conduit lifecycle and meld facade; `cleanup_spell` emits the index destroy the Book reports (0.2.8231);
- note: conjure and target-local resolution orchestration; a successful target pass flags the owned
- note: contracts and lineage; owner-side emissions under the ward lock, contract reads under the contract
- note: deferred module scan and `scan_bind` metadata replay; bind()'s target options, own-declaration eligibility and
- note: dynamic conduit registry; explicit leaves take the cluster's ordered exit, cluster lookups read the
- note: existence modes; `managed_spell_quantity`, the seventh member (0.2.8241).
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: expanded from the directory entry `src/melder/mutation_research/research_set/`
- note: fluent binding adapter; `as_managed_spell_quantity` (0.2.8242).
- note: global singleton, frame registry and the noncreating frame lookups (0.2.8208); the published frame view the
- note: hosted mutation-research root owned by Aether (ResearchSet registry +
- note: instance registry; `ManyDisposalBucket` and `register_many` (0.2.8216); `HolderDisposalEntry` and
- note: key-set plan lowering: site graph from steps, placement, emission, call shape; an automatic world's `unique`
- note: lineage flags; `non_resolvable`, the capability flag (0.2.8247).
- note: lineage registry; retires a spell id's per-conduit verdicts on unregister and on register (0.2.8219);
- note: lineage state; `update_flags`, `has_flag` and `_republish_validity` (0.2.8247).
- note: meld orchestration; the live probes' managed-pool answer (0.2.8243); the per-meld contract scan retired
- note: one leased managed object and its pool; releases once, `with` releases on exit (0.2.8244).
- note: ownership transfer; moves by default and disposes nothing (0.2.8239); the owner stamp follows the lineage both
- note: per-frame state and control plane; cleanup-safe probes, the frame lock kept after cleanup (0.2.8231);
- note: phase 4 validation; registers `AmbiguousProviderStrategy` after the required-holes strategy (0.2.8224).
- note: release-bound creation-cache admission, the envelope's world stamp and atomic persistence;
- note: risk gating; the Book flag leaves out lineages flagged `non_resolvable` (one subset test) and
- note: root-owned lesser pool; a miss records pressure and a return above 20 idle runs the elastic band (0.2.8234).
- note: runtime warnings, version metadata; the four managed-spell root exports (0.2.8244).
- note: shared room-local command surface; `get_spell_by_id` renamed `get_spell_by_spell_id` (command name,
- note: spell metadata and hooks; carries `spellframe_kind` and `implemented_protocols` (0.2.8222);
- note: spell-index graft driver; the same frame hydration as the restore engine (0.2.8222); replays the managed
- note: spellspace pool; release sets and acquisition clears the lease flag; misses record pressure and returns
- note: stable index that categorizes/targets spells and holds the active selected spell; `has_spell` re-checks
- note: staged restore driver; stage 1 installs or reports the recorded spell-id regime, stage 6 replays custody per
- note: static command posture; treats a managed spell like `many` (0.2.8243); `get_spell_by_spell_id` (renamed)
- note: static-room viewer overlay; treats a managed spell like `many` (0.2.8243).
- note: the managed pool: an `AbstractElasticPool` of one managed version's idle objects, its count, reserve, put_back,
- one bind per object per scan (0.2.8228); `scan_bind` takes the managed options, 28 reserved metadata keys
- options (0.2.8242); calls `find_spell_by_spell_id`, its adoption TRIAGE comment corrected (0.2.8253).
- outside the spell lock, under its removal lock (0.2.8233); the four managed fields; `_add_owned_conduit` ensures a
- per-contract release of a disposed version (0.2.8261).
- raw-access label, advertised list), `get_spell_by_source_id` exact through `_get_spell_by_record_locked`
- reason (0.2.8250); the keyword-only `preface`, one line placed before the report (0.2.8262).
- replays the managed options through bind (0.2.8242); calls `find_spell_by_spell_id` (0.2.8253).
- root's ConduitPool elastic, baseline 20 / max 256 (0.2.8234); a root's teardown leaves its cluster first
- root's teardown unregisters the indexes that hold only parked versions (0.2.8259). `_cleanup_spells` retires
- site's store (0.2.8235) and its miss records them with the holder (`adopt_children`, 0.2.8238); the managed site
- sites read their owner store as a plan constant (0.2.8221); a shared site's `many` children register in that
- spell_id (0.2.8251); `find_spell_by_id` renamed `find_spell_by_spell_id` and exact - a parked spell_id
- store lock (0.2.8254).
- the Book's parked versions and cleans the indexes only they hold (0.2.8260). `cleanup_spell` goes
- the check fails, puts the structure back before it raises (`_check_notched_version`, `_revert_refused_notch`);
- the contracted maps and names a lost provider's contract and remedy (0.2.8250).
- the grant check and the outbound listing resolve exactly (0.2.8253). `_emit_spell_disposed`, the
- the recorded world stamp (0.2.8220); the book-wide factories and the cleanup pass walk snapshots (0.2.8230);
- the result (moved + slimmed, 2026-07-10); records the frame kind and Protocol coordinates (0.2.8222); records the
- through the root conduit once conjured, and `_dispose_spell` runs the caller's `release_contracts`
- to its copy (0.2.8250); the dependency walks and the transfer's spell_id handle take the explicit index step,
- version's `resolvable` to `register_index` (0.2.8247); `bind_inactive`'s comment on versions parked before
- ways (`_restamp`, 0.2.8246); the flip and its rollback pass the moved version's `resolvable` to
- which the index path shares (0.2.8253).
- writes `SpellState.non_resolvable` from the registration's capability and publishes the flagged lineages
+ note: Phase-4 SpellContract presence check, the recheck a marked consumer's next meld runs.
+ note: Phase-4 refusal of a single typed parameter with several providers.
+ note: SpellContract descriptor.
+ note: SpellMap descriptor.
+ note: Spellbook core and conjure pipeline.
+ note: `GroupedResearchNode`, the composition node of the formal research record.
+ note: `ManagedSpellMode`: elastic, limited_quantity, queue (0.2.8242).
+ note: `NetworkVersioner`, part of the formal research record.
+ note: `ResearchJournal`, part of the formal research record.
+ note: `ResearchLane` with `LaneState` and `LaneType`, part of the formal research record.
+ note: `ResearchNode`, part of the formal research record.
+ note: `ResearchSet`, the facade of the formal research record.
+ note: `ResidenceRegistry`, part of the formal research record.
+ note: `SpellbookValidationError`.
+ note: `TransitionEntry` with `TransitionAct`, part of the formal research record.
+ note: a member root's facade over the cluster's team store.
+ note: bind-signature CARRIER for one spell version.
+ note: binding pipeline.
+ note: change control.
+ note: cluster auto-sharing.
+ note: conduit lifecycle and meld facade.
+ note: conjure and target-local resolution orchestration.
+ note: contracts and lineage.
+ note: deferred module scan and `scan_bind` metadata replay.
+ note: dynamic conduit registry.
+ note: existence modes.
+ note: fluent binding adapter.
+ note: global singleton, frame registry and the noncreating frame lookups (0.2.8208).
+ note: hosted mutation-research root owned by Aether (ResearchSet registry + composition emission).
+ note: instance registry.
+ note: key-set plan lowering: site graph from steps, placement, emission, call shape.
+ note: lineage flags.
+ note: lineage registry.
+ note: lineage state.
+ note: meld orchestration.
+ note: one leased managed object and its pool.
+ note: ownership transfer.
+ note: per-frame state and control plane.
+ note: phase 4 validation.
+ note: release-bound creation-cache admission, the envelope's world stamp and atomic persistence.
+ note: risk gating.
+ note: root-owned lesser pool.
+ note: runtime warnings, version metadata.
+ note: shared room-local command surface.
+ note: spell metadata and hooks.
+ note: spell-index graft driver.
+ note: spellspace pool.
+ note: stable index that categorizes/targets spells and holds the active selected spell.
+ note: staged restore driver.
+ note: static command posture.
+ note: static-room viewer overlay.
+ note: the managed pool: an `AbstractElasticPool` of one managed version's idle objects, its count, reserve,
+ put_back, abandon, adopt, destroy and cleanup (0.2.8243).

### src_architecture: C1 ranges remeasured from disk  (-174 +174 lines)
- end_line: 1880
- end_line: 2121
- end_line: 2223
- end_line: 652
- end_line: 7907
- loc: 1880
- loc: 2121
- loc: 2223
- loc: 652
- loc: 7907
- verified_at: 2026-08-01T19:12:00Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T13:00:45Z
- verified_at: 2026-08-02T16:30:22Z
- verified_at: 2026-08-02T16:30:22Z
- verified_at: 2026-08-02T16:30:22Z
- verified_at: 2026-08-02T16:30:22Z
- verified_at: 2026-09-19T23:13:57Z
- verified_at: 2026-09-19T23:13:57Z
- verified_at: 2026-09-23T11:33:20Z
- verified_at: 2026-09-23T11:33:20Z
- verified_at: 2026-09-23T11:33:20Z
- verified_at: 2026-09-23T11:33:20Z
- verified_at: 2026-09-23T12:28:41Z
- verified_at: 2026-09-25T23:40:00Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T20:10:34Z
- verified_at: 2026-09-26T21:40:00Z
- verified_at: 2026-09-26T22:18:53Z
- verified_at: 2026-09-27T23:41:28Z
- verified_at: 2026-09-27T23:41:28Z
- verified_at: 2026-09-28T08:22:09Z
- verified_at: 2026-09-28T09:42:05Z
- verified_at: 2026-09-30T00:28:01Z
- verified_at: 2026-09-30T00:28:01Z
- verified_at: 2026-09-30T00:28:01Z
- verified_at: 2026-09-30T18:28:00Z
- verified_at: 2026-09-30T18:28:00Z
- verified_at: 2026-09-30T18:28:00Z
- verified_at: 2026-10-01T10:18:17Z
- verified_at: 2026-10-01T10:18:17Z
- verified_at: 2026-10-04T11:45:00Z
- verified_at: 2026-10-04T17:15:00Z
- verified_at: 2026-10-04T21:25:43Z
- verified_at: 2026-10-04T21:25:43Z
- verified_at: 2026-10-12T20:34:01Z
- verified_at: 2026-10-12T20:34:01Z
- verified_at: 2026-10-12T20:34:01Z
- verified_at: 2026-10-14T23:59:35Z
- verified_at: 2026-10-14T23:59:35Z
- verified_at: 2026-10-14T23:59:35Z
- verified_at: 2026-10-14T23:59:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-15T21:20:35Z
- verified_at: 2026-10-16T01:12:19Z
- verified_at: 2026-10-16T01:12:19Z
- verified_at: 2026-10-16T01:12:19Z
- verified_at: 2026-10-16T11:03:50Z
- verified_at: 2026-10-16T16:48:16Z
- verified_at: 2026-10-17T23:03:04Z
- verified_at: 2026-10-17T23:03:04Z
- verified_at: 2026-10-17T23:03:04Z
- verified_at: 2026-10-17T23:03:04Z
- verified_at: 2026-10-18T01:42:03Z
- verified_at: 2026-10-18T01:42:03Z
- verified_at: 2026-10-18T01:42:03Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-18T20:24:47Z
- verified_at: 2026-10-19T00:01:11Z
- verified_at: 2026-10-19T12:09:01Z
- verified_at: 2026-10-19T13:16:16Z
- verified_at: 2026-10-19T13:16:16Z
- verified_at: 2026-10-19T13:16:16Z
- verified_at: 2026-10-19T23:18:53Z
- verified_at: 2026-10-24T20:54:46Z
- verified_at: 2026-10-24T20:54:46Z
- verified_at: 2026-10-24T20:54:46Z
+ end_line: 1680
+ end_line: 2105
+ end_line: 2225
+ end_line: 651
+ end_line: 7909
+ loc: 1680
+ loc: 2105
+ loc: 2225
+ loc: 651
+ loc: 7909
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z
+ verified_at: 2026-10-24T21:44:16Z

### src_architecture: C1 carried-forward non-path note  (-2 +0 lines)
- - Registration refusal itself lives in `src/melder/aether/spellbook/bind/bind.py`
- Non-path notes carried forward from the previous revision:

### src_architecture: ordered disposal diagram history  (-5 +3 lines)
- (0.2.8258).
- existing live IDs; since then the order is a binding-manifest field, so a receiving book's order
- keeps the spell_id, moves the binding hash and is reported in the restore's `binding_changes`
- policy source. Receiving-book order wins on replay. Until 0.2.8257 the order was part of the
- spell_id and the loader followed changed binding IDs without rewriting the original record or
+ `binding_changes` (0.2.8258).
+ policy source. Receiving-book order wins on replay. The order is a binding-manifest field, so a
+ receiving book's order keeps the spell_id, moves the binding hash and is reported in the restore's

### src_architecture: handoff: new entry, recent log kept, older history out  (-319 +26 lines)
- "<spell_id>@<frame>" under per-frame ids, so a class bound in two frames keeps both copies, and restore replays
- ### Carried forward from the previous revision (2026-07-25)
- ("Cannot build CreationContext before spell_codegen_creation exists") and using a context cleaned under
- (`component_material_for_migration.md`) of patch lane `system_doc_recompose_2026_08_01`.
- (`contract_violation`, `mutation_candidate`, `mutation_quarantined`, `mutation_failed`).
- (the R-A covenant). See Persistence & Restore Architecture.
- - 34 non-contract H2 sections were MOVED, NOT DELETED, to the migration file
- - ALL 134 C1 RANGES WERE OFF BY ONE and are now REMEASURED. The previous pass
- - Conjure follows settle-then-inherit: the conduit inherits the world's mode rather than
- - Internal-bind refusal is one module-level function over a committed manifest, exact
- - Join re-verified by strict parse rather than assumed: 134 cited paths, 0
- - Melder is framed as a Dependency Graph Runtime; DI-style binding and resolution are a
- - Scored 85/100 (band B) against
- - Scored 89.5/100 (band B), up from 85.
- - Structural mutation is admitted through one moded scope-acquisition gate. See
- - The Aether singleton invariant now names the double-checked `__new__` guard
- - The crystallizer is a passive sink; recording never changes runtime behaviour
- - The four posture-gated operations - linking, severing, ownership transfer and
- - `## C1 Code Map (Core Only)` was REBUILT with the contract's five fields per
- - `## Data Flows and Sequences` MOVED UP to its contract position, ahead of
- - `## Indexing` was ADDED; it did not exist.
- - `## Table of Contents` was REMOVED. The generated index replaces it; a
- 2026-09-19 registration/compiler foundation: native policy, compatible True identities, False-only
- 2026-09-21 purge supports instance shortcuts and explicit selectors through existing lookup.
- 2026-09-22 Bind stages are Book-owned and independently adjustable through Book/normal-Conduit
- 2026-09-22 graduation uses a separate private Spellbook conjure route for the existing prepared
- 2026-09-22 pooled hook contracts are promoted. Temporary hook references are retired before idle
- 2026-09-23 named lesser contracts are promoted. Cloud discovery stays separate from root ownership;
- 2026-09-24 creation-cache generation 9 adds exact Melder release admission. Release changes,
- 2026-09-25 boot and conjure sequences corrected from source: `Aether.__init__` builds six hosted
- 2026-09-25 creation build locks moved from the store lock to per-slot guards (unique keeps its Spell
- 2026-09-26 TYPE_CHECKING annotation reflection: Melder's readers of signatures and annotations no longer
- 2026-09-26 caller-supplied containers: a constructor parameter typed as a dict, set or tuple of user classes,
- 2026-09-26 class binding-profile annotations: a class whose field annotations name a `TYPE_CHECKING`-only type
- 2026-09-26 compiler pool reads (0.2.72): compiler passes iterate a copy of the spell pool instead of the live
- 2026-09-26 conjure validation report: a refused conjure now tells the user which spells failed, why and how to
- 2026-09-26 conjure validation warnings: `Spellbook.conjure(validation_warnings=False)` is an opt-in for
- 2026-09-26 cycle consumers: the conjure report tells a spell that only needs a dependency cycle which of its
- 2026-09-26 deterministic signatures and live contract operands (tranche T1 of the IR epic): one signature
- 2026-09-26 door-held first builds (0.2.73): the normal site plan of a per-conduit or SpellSpace root no longer
- 2026-09-26 override site-plan lane: override melds of the many_only and generalized families run one compiled
- 2026-09-26 process-stable spell ids: function, method, lambda, partial, callable-instance and default-repr
- 2026-09-26 self-referencing constructors: a constructor taking its own class is refused by the readable conjure
- 2026-09-26 shared context rebuild windows (the September 5 design, finished): concurrent first melds of a
- 2026-09-26 structural snapshot: a warm conjure over an unchanged book replays the phase 3-4 results recorded in
- 2026-09-26 unresolved inputs: a single typed constructor parameter that no registered spell provides no
- 2026-09-27 conduit lookup coverage (0.2.79): Aether's eight root-only lookups carry `*_root_*` names;
- 2026-09-27 disposal failures (0.2.80): one failing disposal method no longer stops an object's teardown;
- 2026-09-27 meld entry cache by name and class: the meld sequence names the second door registry that
- 2026-09-27 scope exits (0.2.8203): `with conduit:` disposes the scope instead of holding the conduit lock, and
- 2026-09-28 document-view race: publishing sections before the key map allowed a concurrent first lookup
- 2026-09-28 portability: `## Indexing` no longer pastes the index tool's commands or cites the tooling's
- 2026-09-28 qualified same-name registrations: conjure accepts repeated class names at distinct canonical
- 2026-09-30 injected dependencies (0.2.8215): a spell bound after conjure and first built as a consumer's
- 2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214): the Aether record carries the spell-id regime and restore
- 2026-09-30 root configuration guards (0.2.8209-0.2.8212): Aether refuses a spell-id regime other than the one its
- 2026-10-01 citation audit (documentation only): the internal-bind call is
- 2026-10-01 frame lookups and read accessors (0.2.8208, documented now): the boundary list, the operational
- 2026-10-02 many registration trim (0.2.8216): a disposal-bearing `many` creation registers with one append and the
- 2026-10-03 executor-cache world stamp (0.2.8220): the creation-cache bundle records the world its executors were
- 2026-10-03 lazy instance_results (0.2.8217) and annotation matching by address key (0.2.8218): a dict-mode site plan
- 2026-10-03 owner-store constants (0.2.8221): a `unique` site whose provider is owned by an automatic conduit reads its
- 2026-10-03 rebind after first meld (0.2.8219): a definition melded, removed and bound again at the same address
- 2026-10-04 ambiguous providers reported, not thrown (0.2.8224): two or more providers for one single annotation refuse
- 2026-10-04 annotation matching by kind (0.2.8222): a spellframe is a string category or a Protocol contract, a
- 2026-10-04 cache suffix (0.2.8223): Melder's cache bundles are named `.meldercache` (they were `.melc`):
- 2026-10-04 descriptor binding names (0.2.8226): SpellMap and SpellContract keep `binding_name` as written, as Bind
- 2026-10-04 live unlink race (0.2.8227): a meld racing a link sever, uncontract or unbind of a spell its pass is
- Concrete Meld doors retain scope authority; Creations retains lock/removal/disposal. Default
- Conduit. Normal configuration selection, initial Bind seeds and default Conduit/Meld events apply;
- Contract of its authoring instructions. It now carries exactly the 17
- Contracts, Policies, and Permissions plus the components doc's admission plane.
- DECISIONS CURRENTLY IN FORCE, and the sections that carry them:
- DEPTH PASS (2026-08-02): `## Operational Invariants` and `## Failure Modes and
- Direct runtime admission refuses False before validation, hooks, construction or reuse; its warm
- Error Paths` were deepened where they asserted a rule without the mechanism that
- False definitions; selector changes use existing structural and resolution revalidation mechanisms.
- It is blocked by design: those producers belong to the MutationResearch runtime-seam
- MutationResearch runtime-seam slice.
- NOTE ON THIS SECTION: it previously held a 20-entry changelog of edits made TO this
- Nexus frame creation, crystallizer restore and upgrade_to_normal keep the default.
- OPEN: one unknown remains - producer call sites for the advanced `SpellState` flags
- Ordinary meld and persisted world-record compatibility are unchanged.
- PATCH LANE CLOSED (2026-08-02). The recomposition lane went 1,887 -> 644 lines
- Phases 1-7 run on every conjure. The component map now documents the codegen IR export seams the
- Protocol admission and OVERRIDE_REQUIRED compiler metadata are implemented. Executable roots exclude
- RETIRED artifacts; the replacement is `src_graph.md` + `src_graph_index.md`, built
- STATE: This document describes the Melder core as it stands on 2026-07-25, after the
- SUBSET capability, not the whole model. See Architecture Summary.
- Scope objects, definitions and compiled contexts remain reusable. Discovery performs no construction.
- The component map carries the mechanics; the graph still needs regenerating for the new leaf module.
- The component map details the lifecycle and shared replay units; application ownership is unchanged.
- The document is 21 H2 sections with all 17 contract sections still in order.
- The graph pass follows. `src_graph.json` and `readable_src_graph.json` are the
- The other suspect citations here read true when opened: the Spellbook comment at
- The root-guards entry's "still open" item below is closed.
- The src_components binding and configuration entries detail stage ordering, cleanup and recording.
- They are component-level deep dives - per-subsystem Responsibilities sections,
- This is the prior handoff summary, PRESERVED VERBATIM. The recomposition above
- VOLATILE AREAS, most likely to drift first: the guard/manifest surface (it moved twice
- WHAT CHANGED (2026-08-01): this document was RECOMPOSED to the Required Section
- WHAT CHANGED (2026-08-02): CONFORMED to the revised
- WHAT REMAINS UNKNOWN: the entries in `## Unknowns` are unchanged and still
- WHERE THE NEXT READER SHOULD START: the `src_components.md` pass. The migration
- `## Operational Invariants`. It previously sat after `## Failure Modes`.
- `Conduit.enter_lesser_conduit()` makes a lesser for such a block. Every scope exit - SpellSpace managed exit
- `design_engineer/policies/system_document_quality_rubric.md`. The weak
- `get_conduit_by_name` now answers over a frame's named scopes and `get_conduit_by_id` over every live conduit,
- `get_frame` / `list_frame_names`, which never create a frame, and the five read accessors; the component map
- `splitlines()` and a fresh `verified_at`.
- `src/melder/aether/spellbook/bind/bind.py:657`, in `Bind._bind_logic` (cited as 404); the bind-guard
- `src/melder/aether/spellbook/spellbook.py:3816` and `check_system_state` at 1253-1292. Citations
- address collisions. Address ownership, discovery capability and class-object lookup are unchanged.
- address key, so existing objects resolve by their class and `TYPE_CHECKING` strings and class objects agree. The
- addresses. Phase 4 uses the registration/Meld key normalizer and retains DUPLICATE_SPELL_NAME for actual
- against source first; everything kept out carries a written reason in the lane.
- also made consumer melds fail on a full hit after a provider's id changed. Both fixed; cache generation 12.
- and `Extension Points` sections, and an extended `### Sequence: Cleanup` that
- and cause. Whole Book twins carry presence markers only; replay reports missing executable callbacks.
- and its index is stale with it.
- and manual cleanup, lesser pool return, permanent teardown - finishes when a disposal method fails and then
- and no block in it is undecided. Into this document came four promoted patch
- and post receive the actual Spell at distinct publication boundaries; callback errors preserve phase
- and the staging write. The former "surplus cached id still full-hits" contract is retired (one recompile).
- and, more importantly, the IDENTITY-CHECKED teardown: singleton bookkeeping is
- any such spell a book never reached a cache full hit and its bundle grew every run. A pre-existing defect
- are emitted from rows at hydration. The operational invariants and the code map carry it; the component map
- authoring instructions. One defect class was found here, and it was
- beginners. When True, conjure logs every Phase-4 validation warning once, grouped by code, at WARNING
- blocked by design - the advanced `SpellState` flag producers belong to the
- builds a literal per generic construction and nothing on the warm path; Phase 3 matches annotations by the
- by the graph generation tooling.
- caller input; the guard's container error and its Any mismatch with Phase 1 are removed.
- cannot unseat the live one.
- carries the eligible-site rule and the emitted shape.
- carries the per-component contracts and the README's spellframe and DI sections state the rule for users.
- carries the per-component contracts. The line citations the 0.2.8208 insertions moved, and the stale
- carries the per-method contract.
- carries the two verbs, their call sites and the corrected registry verb names. The surviving product of a removed
- carries the wording.
- citations into aether.py, point at their code again. The Aether singleton invariant now says what teardown
- class annotation to its type, a Protocol annotation to its recorded implementers (plus the descriptive
- classifies the creation cache before the conduit phases, skipping only phases 8-11 on a full hit.
- cleanup sequence, the operational invariants, the failure modes and the code map carry it; the component map
- cleared only when `Aether._instance is self`, so cleaning a stale instance
- compiler already carries (a dormant, signed phase 2-5 export and consumed phase-11 step rows).
- compiler, runtime and watcher detail; the failure-path wiring is interim until the override build plan.
- component map carries the Creations details and corrects the Meld concurrency entry.
- composition vocabulary. Re-verify those against source before relying on them.
- concrete class is refused at bind (Breaking), the binding records its kind and Protocol, and Phase 3 resolves a
- contract sections, in contract order, and nothing else.
- contracts. Still open: the Aether record does not carry the spell-id regime, so a world recorded under per-frame
- criterion is Mirror agreement, 2/5: `tests_architecture.md` is 13 days stale
- custody per Book; RecordVersion 4.0.0. The boundary list, the glossary, the operational invariants, the failure
- decision blocks under `## Promoted Patch Decisions`, the `Runtime Type Names`
- definition stays alive by ruling; a slotted replacement meets it in its slot.
- definition), a `TYPE_CHECKING` string to a type or contract and never a category, and `list[...]` to the group
- definitions/verdicts and runtime hook overlays do not cross. Shared frame configuration intentionally
- degrade to a category with a shortfall; cache generation 20. The operational invariants (the 0.2.8218 entry is
- deliberate, bounded, and recorded here rather than left to be discovered.
- dependencies leads there and that it is not part of the cycle, instead of calling it a member. The component map
- dependency melds directly afterwards - a successful target-local pass flags the owned dependencies it compiled
- detail.
- dict, so a concurrent bind no longer aborts meld-time revalidation; the operational invariants carry the rule.
- dirty-root loop has no shipped caller. The component map carries the detail.
- disk, never estimated. One entry was a DIRECTORY and was expanded into its 8
- document, plus a 2026-07-07 marker recording that its tail had been lost to a mid-write
- documented as ending at 261; it ends at 260. `loc` was inflated by one on
- does, and Phase 3 resolves a SpellMap default by the normalized binding and string-frame keys bind and meld use,
- does: it resets unconditionally, and only a failed construction checks identity. Citations into other files
- emitted line.
- enforces it or the failure it prevents.
- entries can only be minted after successful admission of an immutable True version. Supplied values
- entry - `path`, `start_line`, `end_line`, `loc`, `verified_at` - measured from
- errors propagate. The boundary list, the lesser, SpellSpace and cleanup sequences, the operational
- evaluable. External default-format reads of Melder's API are documented under Failure Modes.
- every declared method runs and every failure reaches the caller chained from its original exception. The
- every entry. 131 of 134 were wrong - the three that were right are the files
- evidence now covers the whole verdict gate (242-263) and the two cache-classifying methods (616-721).
- existing ACLs; crystal capture, active/staged replay and graft retain the per-version bool. Record
- existing locks are taken for changed state. Graduation installs independent root baselines on all
- explicit refresh for membership changes. Public configured-Book conjure records both owner and frame.
- facades. Immutable per-bind capture preserves stage consistency through runtime updates. Activation
- file above is its input. UNTIL THAT PASS LANDS, the component-level material it
- first frame sealed while frames exist; an active Nexus refuses another configuration (restore stage 4 deactivates
- first melds and purge; cache generation 10 retires executors emitted with the old locking. The
- fix it, by name; reasons from the conduit verdict are no longer dropped, warnings are counted rather than
- fragments; they were unwrapped on the way out.
- frame-before-book boot ordering is recorded there as the consequence it is.
- gate admission before attachment; later publication errors retain caller-owned normal cleanup.
- hand-maintained contents list is a second addressing surface that drifts.
- handles regeneration. The component map describes the envelope's ownership and write boundaries.
- headings WRAPPED ACROSS TWO PHYSICAL LINES, which produces one-line index
- hoisted to once per pass (-34% conjure at 300 spells, owner-run), and `SpellContract`/`SpellMap` `override`
- holds is in NEITHER canonical document. That is a real coverage gap; it is
- ids restores under process-wide ids. The code map's `aether.py` extent also now counts the 0.2.8208 frame lookups.
- in one day on 2026-07-25), the crystallizer subsystem split, and the MutationResearch
- instance spells used to get a new id per process because the fingerprint hashed "at 0x..." repr text; with
- instructions name as an anti-pattern in THIS document. Four of them had
- internal-bind guard replacement and the package-wide sweep that accompanied it. Every
- into the tooling, so the packaged copy names nothing its reader cannot resolve. The 2026-09-27 "still
- invariant carry the new name.
- invariants (the stale active-spellspace line corrected), the failure modes, a diagram and the code map carry
- invariants, the failure modes and the code map carry it, the component map carries the envelope field, the rule
- invariants, the failure modes, a Frame Lookups diagram and the code map carry `Aether.find_frame` /
- invariants, the failure modes, the code map and the sources carry it; the component map carries the
- invisible to every structural check in the Quality Gate.
- isolation and breaking the promise `automatic` posture makes. The
- it carries - which is the more valuable half of a handoff summary.
- it first); a dynamic conjure refused by the recorded-world configuration discipline no longer settles its frame;
- it; the component map carries the mechanics. Citations into spellbook.py were remeasured on the way (several
- it; the component map carries the per-method contracts. Still open: this document's `## Indexing` section
- key's disposal list is recorded once (`ManyDisposalBucket`, `Creations.register_many`, explicit lock calls); the
- leaf with both facades delegating (bytes unchanged for previously deterministic inputs), phase 8's pool digest
- lesser-to-normal upgrade - are now stated AS ONE SET with their shared
- lessers included; one frame resolver makes a non-string frame a TypeError; `ConduitCloud.list_conduits()`
- level; the default logs nothing, replacing the 0.2.54 per-conjure INFO line about unresolved inputs.
- listed, and Melder-internal consistency codes are flagged as bugs to report. `*args: Any` / `**kwargs: Any`
- lists named scopes. The boundary list, the operational invariants, the failure modes, the diagrams and the code
- live updates; local changes remain isolated. Only pool boundaries inspect restoration flags, and
- lock). The store lock is now a leaf, removing the store/Spell lock-order deadlock between concurrent
- longer fails conjure. It compiles as an UNRESOLVED_INPUT socket, the constructing meld supplies it by
- lost all of them from its binding profile, so its spell id ignored those fields. They are now kept as source
- major 2 rejects old readers safely. Existing eager branch construction and version rules are unchanged.
- manifest holds 619 entries at 0.2.8215 (cited as 582) and is 641 lines; the conjure sequence's
- map carry it; the component map carries the lookup contract and the snapshot ward walk.
- map carry it; the component map carries the mechanics.
- marked superseded), the failure modes, the code map and the information sources carry it; the component map
- match, no MRO inheritance. See Entrypoints and Runtime Guardrails.
- measured `end_line` as the length of `text.split(newline)`, which counts a
- measured unchanged within noise. The component map carries the mechanics.
- melds again - `unregister_index` and `register_index` retire the spell id's per-conduit resolution verdicts, so the
- modes, the record-version lines and the code map carry it; the component map carries the per-surface contracts.
- names maintenance tool paths, which a reader outside the repository cannot resolve (pre-existing).
- names retire before reuse. Crystallizer retains named structure plus necessary unnamed ancestry,
- never prior creations. Nexus preserves existing-ID projections through named pool cycles and retains
- no longer break a spell. The component map carries the layout rules.
- noise rather than a pattern. Every entry now carries a range measured with
- non-resolvable definition) recompiles instead of replaying a stale executor; the conjure sequence, the operational
- non-string name; SPELLMAP_BINDING_NAME_NOT_NORMALIZED retired; no cache generation moves. The operational
- now covers seven types rather than three. Everything re-absorbed was verified
- object by identity in-process and after a cross-process cache full hit. The same-day emission gate is retired.
- objects are unaffected. Cache generation 11 retires older executors. The component map carries the
- open" item below is closed.
- operational invariants and the code map carry it, the component map carries the record, its readers and the
- operational invariants carry the rule, the change-control sequence carries the survey note that the CCM
- operational invariants, the code map and the component map carry both; the README's DI section names the rule.
- operational invariants, the failure modes and the code map carry it; the component map carries the per-root
- or dict[str, Any], used to break conjure at Phase 4 although Melder never injects it. It is now a REQUIRED_HOLE
- override / single-provider remedies) instead of a Phase-3 RuntimeError; Phase 3 records an `AMBIGUOUS_INPUT`
- override, and a missing value raises UnresolvedInputError (a MeldExecutionError exported at the package
- owner ruling; no cache generation moves (a broken spell never plans). The failure modes, the code map and the
- owner store as a plan constant bound at emission instead of `spells[i]._owner_creations` per creation; dynamic
- per-descriptor rule.
- per-path overlay, the override-targeting surface and the old emitters are retired, so conjure no longer grows
- per-strategy rule.
- phantom line after the file's final newline. `src/melder/__init__.py` was
- plan per override key set that never builds a supplied dependency; normal melds of those families run the same
- planning raises SpellbookValidationError instead of PhaseExecutionError - the Phase 9 contract and runtime
- policing the caller's flag. See Operational Invariants.
- processors now report a pool miss as KeyError naming the spell, which the target pass already records as a
- profiles, `Package.describe` and ProtocolCrafter, and made such class spell ids differ per process. Readers
- providers, unowned ones and the `meld.<store>` routes keep the read, and no cache generation moves because plans
- publication, including manual/managed Spaces and prewarming. Root-shared maps retain identity for
- purge_all=True retires the target's entries; False requires an instance and removes only its entry.
- raise NameError on names unbound at runtime - which had broken late binding in dynamic worlds, detailed
- raises the failures as one ExceptionGroup; a lesser's pool return disposes its descendants first; a second
- rationale, because reading them as four unrelated rules invites fixing one in
- re-takes the root's build lock that its door already holds, so each first build takes that lock once; the meld
- real modules rather than given a plausible range.
- replaced it, and replacing it would have silently destroyed the decision record
- replacement is resolved again by each conduit instead of inheriting the dead definition's `valid`. The meld-time
- report (SELF_DEPENDENCY, naming the parameter) instead of aborting in the compiler. The component map carries the
- reseeds configured defaults and remains frame-owned. Public rollback restores lesser topology and
- retained runtime doors. Broader callback standardization remains a separate, deferred design.
- root) from that object's constructor-failure path only. A later matching bind re-resolves it; stored
- root. The meld-time validation sequence, the operational invariants, the failure modes and the code map carry
- roots eagerly in a fixed order (MutationResearch included, per the 2026-08-03 ruling), and conjure
- runtime's normal plan, and unresolved inputs are decided before construction in every family. The Phase-5
- sequence and the operational invariants carry the rule, and the component map carries the emission detail.
- serves `meld("Name")` and `meld(spell=Cls)` warm; the component map carries the mechanics.
- shared dynamic spell failed in two ways - building a context from the gap between Phase 5 and Phase 11
- slice, which is deliberately deferred. See Unknowns and Open Questions.
- so a capitalized binding name no longer fails with "SpellMap default could not be resolved"; TypeError for a
- socket, a new Phase-4 strategy refuses it, the watcher and the cycle strategy learn the kind. No warning path by
- soft cleanup does nothing; a released SpellSpace refuses meld and purge; `using_cleanup()` lets cleanup
- source path cited here was verified to resolve on that date, and no renamed or removed
- sources carry it; the component map carries the socket, the strategy and the message shape.
- specification, and the handoff lines below name the recomposition patch lane by its id instead of a path
- stage 1 installs it, or reports or refuses when the live regime is already fixed; spell custody is keyed
- staged in and a full hit requires it, so a world that only added or removed an existing creation (or a
- state-and-next-steps summary the template specifies; the edit history lives in git.
- symbol survives as a live claim.
- text; affected classes get a new id once. The component map carries the detail.
- that happen to lack a trailing newline, which is why the error looked like
- the Book is always independent and empty. Retained creations keep disposal responsibility, but old
- the audit heuristic could not tie to a symbol were not opened.
- the conduit cache bundle instead of running phases 1-4; the conjure sequence, the pipeline diagram and the
- the consumer through the readable conjure report (`AMBIGUOUS_PROVIDER`, every candidate's address, the SpellMap /
- the first run after upgrading compiles cold once. The bind-guard guardrail and the release-compatibility
- the four root configurations expose `get_configuration_dictionary()`. The boundary list, the boot sequence, the
- the glossary, pipeline narratives, and four promoted-patch blocks - which the
- the kind names; the crystal records the kind (RecordVersion 4.1.0) and the loaders re-import the Protocol or
- the per-conduit creation caches and the build-asset caches. Nothing reads or deletes a `.melc` file, so
- their ticket across the context read and execution; the two tests skipped in September run again. Warm melds
- them. Rebuilds now freeze and drain the spell-index gate before replacing the plan, and dynamic melds hold
- to receive None. The map now precedes the readiness marker, preserving deferred loading and lock-free reads.
- truncation predating recoverable git history. Both were replaced on 2026-07-25 with the
- unresolved against `src_graph_index.md`.
- unstamped legacy input and other existing incompatibilities cold-reset at load; normal conjure
- use FORWARDREF or the `SignatureReflection` helper; an annotation integrity guard keeps `src/melder`
- use existing execution and normal Python errors. Nexus publishes/navigates typed references under
- validation sequence, the operational invariants, the failure modes and the code map carry it; the component map
- values riding as live meld operands - rows carry refs, never object values, and the provider receives the
- visibility failure. The failure modes and the compiler pool-read invariant carry it; the component map carries the
- were already 2-14 lines stale).
- were not audited in this pass.
- with logical paths. The meld sequence, the operational invariants, the failure modes, the diagrams and the code
- without a plan of their own, and the deferred lane runs a full target pass for a spell that is not its Phase 5
+ (Entrypoints and Runtime Guardrails).
+ (Operational Invariants).
+ (Read This First), the Architecture Summary, then src_components by component name.
+ - Conjure follows settle-then-inherit: the conduit inherits the world's mode rather than policing the caller's flag
+ - Internal-bind refusal is one module-level function over a committed manifest, exact match, no MRO inheritance
+ - Melder is framed as a Dependency Graph Runtime; DI-style binding and resolution are a SUBSET capability, not the
+ - Structural mutation is admitted through one moded scope-acquisition gate (src_components, Component: Transaction
+ - The crystallizer is a passive sink; recording never changes runtime behaviour (Persistence & Restore
+ 2026-10-24 src_architecture to its authoring spec (documentation only; EPIC-2026-10-24-src_architecture_to_spec, the
+ Admission Plane (Scope Acquisition)).
+ Architecture).
+ DECISIONS IN FORCE, carried from the 2026-07-25 summary; the section named carries each one:
+ OLDER HISTORY: the entries for 0.2.8227 and earlier (2026-07-25 to 2026-10-04), with the record of the 2026-08-01
+ Operational Invariants, and that period's fixed-defect and correction history left Failure Modes and the other
+ Root (ResearchSet Registry)); C1 notes keep their descriptions, not per-version changes; the citation check is kept
+ `release_docs/0.2.8227.md`. The 2026-08-01 recomposition's migration file (patch lane
+ and 2026-08-02 recompositions, were removed on 2026-10-24. They are in git history - commit 3bedd65bb holds this
+ document as it stood before the trim - and the changes from 0.2.8202 to 0.2.8227 are in the release note
+ entries from 0.2.8228 on, the release-note boundary. Still unknown: see Unknowns. Where to start: What Melder Is
+ git history only.
+ once, in src_components' Indexing; three paths into the documentation tooling are gone. This change log keeps the
+ owner's ask): component mechanics recorded here before 0.2.8228 - cache envelope generations, site-plan emission,
+ sections; the MutationResearch interface inventory moved verbatim to src_components (Subcomponent: MutationResearch
+ store and slot locks, hook maps, recording keys - now live only in their src_components entries, named at the end of
+ system_doc_recompose_2026_08_01) was deleted in commit 0fddab923; what src_components did not absorb from it is in
+ whole model (Architecture Summary; What Melder Is (Read This First) since 2026-10-15).

### src_components: metadata Updated  (-1 +1 lines)
- - Updated: 2026-10-19
+ - Updated: 2026-10-24

### src_components: MutationResearch boundary inventory moved in  (-0 +82 lines)
+ "informational" with no custody/frame probes; POLYMORPHIC VERBS
+ (2026-07-11 units-and-scales ruling): `module_view(...)` (the one-call
+ (read-only candidate mock: AST analysis + would-be diff via
+ (unified part-text diff between versions over RECORDED material only,
+ - Boundary inventory, moved verbatim from src_architecture (System Boundary and External Interfaces) on 2026-10-24;
+ - `Aether.mutation_research` as the access path to the hosted mutation root,
+ 2026-07-11: `group_view` roster + behind drift, `group_diff_research`
+ 34-command `research_*` family (14 record/organization/campaign incl.
+ ADVERTISED via `list_supported_command_methods`, and
+ DELETED; as of 2026-07-12 (patch
+ EXPLICIT DB-storable node rows for both families at construction, and
+ MutationResearchConfiguration.activate() CARRIES the recorded
+ [2026-07-12]: the spell-grain reads themselves dispatch on node kind -
+ `DiffEngine.diff_materials` + would-be radius; nothing executes, binds,
+ `LaneType` development/experiment/production/test; join gate armed by
+ `ViewSpell.describe_spell_research(...)` / `describe_spell_source(...)`
+ `clear_active_campaign()` / `active_campaign` (ambient stamp carried by
+ `create_configuration_builder()`, `configure(...)`, `activate(...)`,
+ `create_diff_engine()`, and the foresight reads (2026-07-11 agent QoL
+ `group_drift_view` custody drift narrowed to the footprint,
+ `group_footprint_view` physical shadow + shared-module coupling,
+ `group_history_view` the area's journal story, `compositions_of` the
+ `join`, `archive`, `walk`/`history`/`heads`, `campaign_view`,
+ `list_research_set_names()`, `describe_research_composition()`,
+ `load_recorded_composition(...)`, `record_world_entry(...)`,
+ `preview_candidate(...)`
+ `recompose_group` [compositions = GroupedResearchNode, its OWN node
+ `record_promotion(...)`, `residency_view(...)` (the query-time
+ `research_preview` + 3 synthesis + 8 composition),
+ `research_set(...)`, `create_research_set(...)`,
+ `snapshot_network`/`restore_network`); the spellbook's bind,
+ `source_drift_view()` (full drift report), the crystal-well reads
+ active/parked/stored join), `set_active_campaign(...)` /
+ agent verb surface (`register_spell`, `register_group`/
+ and `part_diff(...)`
+ annotate any visible spell with its research residency and recorded
+ bind_inactive, and notch confirmation points auto-record
+ campaign-pattern: the next fresh world entry mints the multi-parent
+ capability rooms the twenty-one reads (seven record + eight foresight +
+ carriers - synthetic and user-retained - and never the live disk;
+ carrying its module-grain radius; diff material drinks BOTH recorded
+ class-code inventory: every top-level part per module with full text)
+ composition answers the group radius, diff_research routes two
+ composition forward - the docking-loop law); the returned `ResearchSet` carries the
+ compositions teach-grade; the emitted MutationResearchCrystal derives
+ compositions through the members engine, code-grain verbs refuse
+ configuration `lane_type_enforcement`], `attach`/`detach`,
+ every runtime auto-record), `diff_research(...)`,
+ foresight incl. the crystal-well module/part reads and the codegen-only
+ instead bind the world root at init and expose it through borrowed
+ kit): `source_view(...)` (recorded-first module text, live-disk fallback
+ lane of group nodes is a subsystem's timeline], `create_lane` [typed via
+ lane-evidenced version_moved pairing], `group_impact_view` union
+ member radii + internal/outbound split + CLOSURE + adjacency,
+ module + full preview; salvaged May lane), and the staged-ancestry mint
+ module dossier: text labeled synthetic/user/live_disk, fingerprint,
+ module source. The old `Conduit.get_mutation_research()` door is
+ mutation dimension)
+ mutation_research_accessor_doors_2026_07_12) Spellbook and Conduit
+ node one-shot), and the composition reads (GroupedResearchNode ruling
+ or records), `synthesize_candidate(...)` (surgical composition through
+ path, deps both ways, exports, drift), `part_view(...)` (one named
+ plus `MutationResearch.create_configuration()`,
+ read-only `mutation_research` properties (frames still carry no
+ residency), `module_graph_view(...)` (walkable module world),
+ residency]; `residency_view` is kind-aware - compositions answer
+ reverse lift [surfaced as `pinned_by_compositions` on spell
+ roster-searches naming the carrying member, impact_view on a
+ seam (`stage_ancestry`/`clear_staged_ancestry`/`staged_ancestry`,
+ six composition), both
+ source/parts/module_graph/module fan out per member, part_view
+ src_architecture keeps a summary:
+ strategies: source/structural/parts),
+ surface is the Rift rooms (2026-07-11): codegen rooms carry the full
+ the owned `StructuralSynthesizer`: donor parts splice into the base root
+ the research_recent cold-landing read + 9
+ through the MIRRORED GroupDiffEngine ["members" strategy:
+ top-level part's text/span/carrying module), `parts_view(...)` (the
+ type, purely informational, content-addressed over pinned members; a
+ w/ drift marker), `impact_view(...)` (blast radius joined with research
+ whole-version diffs offer the grain CHOICE via three registered
+ world-entry/staged/promoted events while the root is active. The USER

### src_components: handoff: new entry  (-0 +7 lines)
+ 2026-10-24 src_architecture to its authoring spec (documentation only; EPIC-2026-10-24-src_architecture_to_spec):
+ MutationResearch boundary inventory moved verbatim from src_architecture's System Boundary and External Interfaces,
+ Subcomponent: MutationResearch Root (ResearchSet Registry) carries, at the end of its Contract/Interface list, the
+ component contract changed. Verify next: that src_components pass.
+ its Operational Invariants, the entries here that carry them, so those entries are now the only record of them. No
+ two. src_architecture no longer repeats the component mechanics it recorded before 0.2.8228 and names, at the end of
+ which keeps a summary; the inventory overlaps the entry's own list until the epic's src_components pass folds the
