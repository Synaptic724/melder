# Epic: Design Crystallizer Asset Provenance Layer

## Metadata
- Epic ID: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-04-26T09:56:44Z
- Updated: 2026-04-26T11:39:24Z
- Updated: 2026-04-26T21:11:04Z
- Updated: 2026-04-27T00:13:04Z
- Updated: 2026-05-03T11:48:32Z
- Updated: 2026-05-03T14:53:56Z
- Updated: 2026-05-03T16:22:08Z
- Updated: 2026-05-03T15:54:59Z
- Updated: 2026-05-03T17:13:48Z
- Target Window: 2026-Q2
- Related Program/Initiative: Post-AethericRift asset/provenance and mutation foundation

## Problem / Opportunity
The next big subsystem is not more AR runtime invention. It is the bridge
between runtime registration and durable mutation work.

Melder already knows how to:
- bind live references and existing objects
- keep spells and lineage alive in the runtime
- let agents work through the live object world

But runtime registration is not the same thing as source truth.
The stack now needs one explicit layer that can answer:
- what source thing is this?
- where did it come from?
- what is the smallest honest mutation unit?
- what can be treated as first-class mutable and what cannot?
- what durable source/provenance data should be cached for later mutation work?

That layer is Crystallizer.

## MRP Alignment (Most Reasonable Product)
The MRP is not "solve every mutation edge case."
The MRP is:
- a coherent asset/provenance layer
- minimal durable records for source truth
- a bridge from Bind/Spell into Crystallizer
- enough structure that MutationResearch can build on top of it

## Ticket Contract
- ENTRY_GATE: AR runtime is usable enough that the next step is object/asset
  management rather than another foundational runtime pass.
- EXECUTION_BOUNDARY: design the Crystallizer asset/provenance layer, not full
  MutationResearch execution.
- DEPENDENCIES:
  - `src/melder/crystallizer/`
  - `src/melder/spellbook/bind/bind.py`
  - `src/melder/spellbook/spell.py`
  - `src/melder/spellbook/spellbook.py`
  - codegen runtime and transaction surfaces
- EXIT_GATE: the Crystallizer role, core records, origin taxonomy, and
  bind-to-crystallizer handoff are explicit enough to stage implementation
  stories/tasks without guessing.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the design proves that
  Crystallizer cannot stay separate from Bind/Spell without breaking the public
  Melder boundary.

## Goals (Outcomes)
- Define Crystallizer as the asset/provenance layer, not the runtime layer.
- Keep `Bind / Spell / Conduit` focused on runtime registration and lineage.
- Define the minimum durable records Crystallizer should own.
- Define the origin taxonomy and mutation-scope taxonomy.
- Define the bind-to-crystallizer handoff.
- Define how MutationResearch will sit on top of Crystallizer later.

## Non-Goals (Explicit Exclusions)
- Full MutationResearch execution design.
- Complete recursive source-ingestion for every dependency edge.
- Forcing all provenance storage into `Spell` or `Bind`.
- Solving process-restart replay fully in this epic.

## Scope Boundaries
- In scope:
  - source/provenance cache design
  - asset identity and version records
  - mutation-scope classification
  - dependency-envelope boundaries
  - bind/crystallizer linking strategy
- Out of scope:
  - full proprietary packaging/licensing details
  - broad AR/runtime redesign
  - implementing every mutation policy branch

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly identified object/asset management as
  the next step before MutationResearch, and the prior discussion produced a
  coherent Crystallizer direction that now needs to become a tracked ticket.

## Success Metrics
- Crystallizer has one explicit subsystem ticket that other work can route
  through.
- The source-of-truth split between runtime and provenance is explicit.
- The minimum data model is concrete enough to start implementation.

## Requirements (Functional + Non-Functional)
- Functional:
  - define what Crystallizer owns
  - define what `Spell` and `Bind` should and should not own
  - define origin kinds and mutation-scope kinds
  - define the minimal records needed for durable assetization
  - define the main crystallization flows
- Non-functional:
  - keep `Bind` shallow relative to deep provenance extraction
  - support workspace, wheel, codegen, runtime-only, and opaque-reference cases
  - remain pragmatic about dependency depth

## Constraints / Assumptions
- `Spell` should link to Crystallizer, not become Crystallizer.
- Codegen source provenance is not reliably recoverable from object references
  alone, so codegen-origin assets need explicit capture.
- For file-backed imports, the mutation unit is often the module, not just the
  symbol.
- External imports should be dependency edges by default, not recursively
  crystallized source.

## Core Design Thesis
Crystallizer should be the asset/provenance layer, not the runtime layer.

That means:
- `Bind / Spell / Conduit`
  - runtime registration
  - live object/reference handling
  - spell identity and lineage
- `Crystallizer`
  - source/provenance cache
  - asset identity
  - mutation scope classification
  - dependency envelope
  - durable source handles
- `MutationResearch`
  - consumes crystallized assets + spell/runtime lineage
  - plans and executes mutation

## Asset Taxonomy
Primary asset kinds:
- `workspace_asset`
- `wheel_asset`
- `codegen_asset`

Outlier / boundary kinds:
- `runtime_only_reference`
- `opaque_external_reference`

## What Crystallizer Should Own
1. **Asset identity**
- `asset_id`
- stable key for “what source thing is this?”

2. **Origin/provenance**
- workspace file
- wheel/site-packages file
- codegen runtime source
- runtime-only object
- opaque external reference

3. **Authoritative source unit**
- symbol
- module
- reference-only
- runtime-only

4. **Cached source payload**
- raw source text
- maybe AST later
- maybe normalized IR later
- source hash

5. **Dependency envelope**
- local sibling dependencies
- external imports
- stop-depth rules

## Core Records
**CrystallizedAsset**
- `asset_id`
- `origin_kind`
- `authoritative_unit_kind`
- `module_name`
- `qualname`
- `display_name`
- `source_hash`
- `mutable_status`

**CrystallizedAssetVersion**
- `asset_version_id`
- `asset_id`
- `source_text`
- maybe `ast_blob`
- `created_at`
- `created_from`
- `transaction_id`

**BindingLink**
- `spell_id`
- `spell_index_id`
- `asset_id`
- `binding_kind`
- `binding_mode`

**DependencyEdge**
- `asset_id`
- `target_kind`
- `target_name`
- `relation`
- `depth`

## The Most Important Design Rule
Crystallizer should answer:

**“What is the smallest honest mutation unit?”**

Not:
- what object did I click on

But:
- what unit can I actually mutate safely?

Default rules:
- `symbol_scope`
  - only if clearly self-contained
- `module_scope`
  - default for most file-backed things
- `external imports`
  - references only, do not recursively ingest by default

## Main Flows
### 1. File-backed import bind
- bind sees class/function from real module
- binding profile captures module/file/line-ish info
- Crystallizer reads file
- decides symbol vs module mutation scope
- stores asset
- returns `asset_id`
- `Spell` stores only `crystallizer_asset_id`

### 2. Codegen bind
- codegen event/transaction exists
- bind sees object reference
- Crystallizer intercepts transaction metadata
- stores code string + source hash + synthetic module identity
- returns `asset_id`
- `Spell` links to it

### 3. Existing object bind
- bind sees live instance
- Crystallizer may only store shallow provenance
- likely classify as `runtime_only` or `reference_only`
- not first-class mutable by default unless recoverable source exists

### 4. DB/system hydrate
- Crystallizer loads asset/version from DB
- reconstructs source-backed or codegen-backed thing
- bind registers runtime object/reference
- spell links back to same `asset_id`

## What Spell Should Store
Very little.

Probably just:
- `crystallizer_asset_id`
- maybe `origin_kind`
- maybe `source_hash`

Do **not** put the full source blob on `Spell`.

## Recommendation
If we keep v1 simple:
- Crystallizer owns:
  - source text
  - source hash
  - origin kind
  - module/qualname
  - scope classification
  - dependency edges
- Bind owns:
  - runtime registration
  - handoff to Crystallizer
  - storing returned `asset_id`
- MutationResearch owns:
  - mutation planning
  - runtime/source mutation mode
  - rollback/versioning decisions

## Milestones (Track Progress)
- [ ] Milestone 1: define asset/provenance boundary and minimal record set
- [ ] Milestone 2: define origin/scope/dependency classification rules
- [ ] Milestone 3: define bind-to-crystallizer handoff and next implementation stories

## Stories (Required to Complete)
- [ ] Story: define CrystallizedAsset and CrystallizedAssetVersion contracts
- [ ] Story: define bind/crystallizer handoff and spell-link contract
- [ ] Story: define mutation-scope and dependency-envelope policy

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: verify current bind/profile metadata is sufficient for first-pass file-backed assets
- [ ] Task: verify codegen-origin metadata requirements from the live transaction path
- [ ] Artifact: capture AR/codegen capability-surface philosophy and workflow model
- [ ] Task: stage the first implementation slice for `src/melder/crystallizer/`
- [ ] Task: scaffold the initial crystallizer package layout before component authoring

## Acceptance Criteria (Epic Done)
- Crystallizer’s role is explicit and separated cleanly from runtime registration.
- The minimum durable asset records are defined.
- The asset taxonomy and mutation-scope rules are explicit.
- The bind-to-crystallizer handoff is concrete enough to implement.

## Risks / Mitigations
- Risk: Crystallizer grows into a second runtime rather than an asset/provenance layer.
  Mitigation: keep runtime truth in `Spell`/Melder and source truth in Crystallizer.
- Risk: symbol/module boundaries get fuzzy.
  Mitigation: default to module scope when local dependency closure is unclear.
- Risk: dependency extraction widens too far.
  Mitigation: stop at external import edges by default.

## Applicable Anti-Patterns
- [ ] No provenance engine hidden inside `Bind`.
- [ ] No source blobs stored directly on `Spell`.
- [ ] No recursive dependency ingestion by default.

## Validation / Test Approach
- Design-only in this epic.
- Validation is coherence of the model and readiness for implementation slicing.

## Rollout / Adoption Plan
- First: crystallize the schema and flow
- Second: implement minimal Crystallizer storage/cache
- Third: wire bind handoff
- Fourth: let MutationResearch consume the new layer

## Open Questions
- When does symbol scope become unsafe enough to force module scope?
- What exact metadata should codegen-origin bind pass into Crystallizer?
- Should synthetic module identity be required for all codegen assets?

## Decision Log
- 2026-04-26T09:56:44Z: Created as the next major subsystem ticket after AR stabilization, based on the user-approved design direction that Crystallizer should own source/provenance truth and MutationResearch should consume it.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-04-26_crystallizer_philosophy.md
  - artifacts/2026-04-26_ar_codegen_capability_surface_philosophy.md
  - artifacts/IMPORTANT_CONSIDERATION.md
  - artifacts/2026-05-02_file_to_memory_bridge_mechanic.md
  - artifacts/crystallizer_configuration.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-26T09:56:44Z
  TYPE: PLAN
  CLAIM: Crystallizer is the correct next subsystem because MutationResearch
    needs an asset/provenance foundation before durable mutation can stay
    coherent. The minimum viable next move is to define the asset taxonomy,
    minimal records, and bind/crystallizer handoff cleanly.
  EVIDENCE:
  - user_instruction: object/asset management should be solved before MutationResearch
  - prior_design_discussion: Crystallizer should own source/provenance truth while Spell keeps only a lightweight link
  IMPACT: The next concrete work should move from chat into a tracked
    Crystallizer design lane instead of staying implicit.
  NEXT: stage the first implementation-facing story around the core asset schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T10:11:59Z
  TYPE: FACT
  CLAIM: The subsystem now has a dedicated philosophy artifact. That artifact
    captures the source-truth/runtime-truth split, the five asset categories,
    the mutation-unit rule, and why `Spell` should link lightly to Crystallizer
    instead of owning full provenance payloads itself.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:1-200
  IMPACT: The Crystallizer lane now has a durable design artifact that can be
    reused when implementation stories start instead of forcing the philosophy
    to live only in transient chat.
  NEXT: stage the first implementation-facing story around the core asset schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-26T13:03:57Z
  TYPE: FACT
  CLAIM: A second retained artifact now captures the capability-first AR/codegen
    philosophy. It explains AR as a capability surface, codegen as a
    construction surface rather than a mutation-first system, the agent act
    taxonomy, residency levels, and the Melder vs CommandOps split.
  EVIDENCE:
  - artifacts/2026-04-26_ar_codegen_capability_surface_philosophy.md:1-414
  IMPACT: Later Crystallizer and workflow design can now inherit a durable
    capability-first model instead of collapsing immediately into mutation
    semantics.
  NEXT: use both retained philosophy artifacts when staging the first
    implementation-facing crystallizer stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T15:23:20Z
  TYPE: FACT
  CLAIM: The V1 storage story is now explicit. Crystallizer should return a
    stable `spell_crystal_id`, store one `SpellCrystal` record per id in a
    dict-backed store, and preserve the current string representation for the
    asset: raw codegen string for codegen-backed assets, full module string plus
    target metadata for file-backed assets.
  EVIDENCE:
  - artifacts/Archived/2026-04-26_crystallizer_v1_spell_crystal_storage.md:1-200
  IMPACT: Later implementation can start from one simple stable storage model
    instead of guessing at IDs, record shape, or whether file-backed assets
    should store full modules or only target snippets.
  NEXT: stage the first implementation-facing crystallizer story around the
    `SpellCrystal` record and the dict-backed store facade.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T15:23:20Z
  TYPE: FACT
  CLAIM: The V1 storage contract is now explicitly mode- and package-gated.
    Crystallizer is disabled in `automatic` mode, spells in that posture must
    not receive a `spell_crystal_id`, and the storage/facade path only exists
    when the optional Crystallizer class is present, which keeps the feature in
    the `melder_pro` layer instead of base Melder.
  EVIDENCE:
  - artifacts/Archived/2026-04-26_crystallizer_v1_spell_crystal_storage.md:49-80
  - artifacts/Archived/2026-04-26_crystallizer_v1_spell_crystal_storage.md:143-176
  IMPACT: Later implementation does not need to pretend that all spell
    postures or all package builds support crystallization. The availability
    boundary is explicit from the start.
  NEXT: preserve this gate when the first implementation-facing `SpellCrystal`
    and spell-facade stories are staged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T15:23:20Z
  TYPE: FACT
  CLAIM: The V2 storage direction is now explicit. Crystallizer should evolve
    from one-source-unit storage into a synthetic module graph and requirements
    view: AST import investigation, synthetic-module identity, internal graph
    edges, and a requirements view distinct from plain `pip freeze`.
  EVIDENCE:
  - artifacts/Archived/2026-04-26_crystallizer_v2_synthetic_module_graph_and_requirements.md:1-170
  IMPACT: Later implementation work can now distinguish clearly between:
    - Base V1 single-unit storage
    - V2 graph-aware synthetic module and requirements semantics
  NEXT: expand the V2 artifact later with concrete graph, restore, and
    requirements semantics once more of the dependency model is agreed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T18:44:49Z
  TYPE: FACT
  CLAIM: The dependency recovery policy is now explicit in the artifacts.
    `uv` is the preferred and fully supported dependency snapshot and recovery
    path, while `pip` remains an optional fallback only when the user provides
    an explicit subprocess script. Crystallizer still does not become a package
    manager, and default design no longer assumes storage of `site-packages`
    contents.
  EVIDENCE:
  - artifacts/Archived/2026-04-26_crystallizer_v2_synthetic_module_graph_and_requirements.md:210-257
  - artifacts/Archived/2026-04-26_crystallizer_v3_bootstrap_recovery_and_fileless_truth.md:74-92
  IMPACT: Later implementation can treat dependency recovery as an adapter-led
    bootstrap phase instead of an internal packaging subsystem.
  NEXT: preserve the `uv`-first and scripted-`pip` fallback rule in later
    bootstrap and restore stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T18:23:15Z
  TYPE: FACT
  CLAIM: The V3 direction is now explicit. Crystallizer should define boot and
    recovery semantics over crystallized software graphs: JSON package in/out,
    synthetic-module restoration, binding signatures, optional fileless
    application truth, and optional file materialization later.
  EVIDENCE:
  - artifacts/Archived/2026-04-26_crystallizer_v3_bootstrap_recovery_and_fileless_truth.md:1-200
  IMPACT: The crystallizer lane now has a durable statement of what comes after
    V1 storage and V2 graph semantics: how software actually comes back into a
    live world and becomes useful again.
  NEXT: later expand the V3 artifact with more explicit loader, activation, and
    package-shape semantics once more of the restore model is agreed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T17:22:21Z
  TYPE: DECISION
  CLAIM: Managed synthetic modules are now a validated core feature for the
    crystallizer lane. The green experiment proved that a synthetic package
    shell and submodule graph can be materialized as real module objects,
    inserted into `sys.modules` before execution, imported by later synthetic
    units through normal Python import syntax, and removed again
    deterministically.
  EVIDENCE:
  - tests/experimentation/synthetic_module_import_testbench.py:47-110
  - tests/experimentation/synthetic_module_import_testbench.py:113-187
  - tickets/tasks/2026-04-26_experiment_synthetic_module_import_task.md:1-170
  - validation_result: `python tests/experimentation/synthetic_module_import_testbench.py` -> `OK_SYNTHETIC_MODULE_IMPORT`
  IMPACT: Later implementation stories can treat synthetic-module import and
    recovery as a real design center instead of a speculative side path.
  NEXT: use this validated synthetic-module direction when expanding the V2
    artifact and when staging the first implementation-facing graph and
    recovery stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-27T00:13:04Z
  TYPE: DECISION
  CLAIM: The split crystallizer `V1`, `V2`, and `V3` artifact docs have been
    collapsed into one unified `crystallizer_philosophy` artifact. The lane now
    keeps one crystallizer philosophy artifact and one separate AR/codegen
    capability philosophy artifact instead of carrying version-labeled design
    files.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:1-241
  - artifact_board.md:17-28
  IMPACT: The crystallizer artifact lane is simpler and no longer needs
    separate version-doc maintenance for the same subsystem philosophy.
  NEXT: update future crystallizer philosophy changes in the unified artifact
    instead of spawning new V-numbered design docs by default.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:11:04Z
  TYPE: FACT
  CLAIM: The first filesystem scaffold for `src/melder/crystallizer/` is now
    staged. The package has the agreed concern-oriented directories
    (`configuration`, `crystal_analysis`, `asset_management`, and
    `crystal_loader`), the obsolete local `crystal_management/` and
    `mutation_research/` dirs are gone, and the package is ready for gradual
    component authoring.
  EVIDENCE:
  - src/melder/crystallizer/: filesystem inventory after scaffold
  - tickets/tasks/2026-04-26_scaffold_crystallizer_package_layout_task.md:1-94
  IMPACT: The crystallizer lane no longer needs more directory-shape debate
    before implementation slices start.
  NEXT: begin filling the first top-level components (`SpellCrystal`,
    `SyntheticModule`, `BindingSignature`, and `Crystallizer`) incrementally.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-02T10:12:13Z
  TYPE: FACT
  CLAIM: The file-backed bind -> in-memory software truth -> file projection
    mechanic is now captured in its own artifact. This makes the bridge between
    physical module authority and memory-first managed software truth explicit
    instead of leaving it only in chat.
  EVIDENCE:
  - artifacts/2026-05-02_file_to_memory_bridge_mechanic.md:1-87
  IMPACT: The crystallizer lane now has a retained reference for one of its
    most important concrete mechanics: turning file-backed software into
    in-memory managed truth and later projecting it back out again.
  NEXT: use this artifact when we work out the exact `SyntheticModule` /
    `SpellCrystal` mechanics and file-backed bind path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T16:10:43Z
  TYPE: DECISION
  CLAIM: The crystallizer philosophy artifact now carries the practical asset
    manager and bootstrap model. The current direction is: all files are
    assets, codegen first becomes `SyntheticModule`, `SpellCrystal` is created
    when code becomes bind-relevant, snapshots are the versioned capture unit,
    payloads are stored in uniform base64 + SHA256 form, and transactions are
    plain dataclass-style raw data payloads emitted for the host to persist and
    organize as it chooses.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:1-320
  - user_instruction: "go ahead and properly outline how the asset manager works what assets are how the bootstrap works and yes snapshotting too"
  IMPACT: The crystallizer lane now has a concrete baseline for asset mapping,
    snapshotting, bootstrap, and payload representation without drifting into
    fake git/history ownership.
  NEXT: use this asset/snapshot/bootstrap baseline when we later shape the
    concrete data classes and loader callbacks in `src/melder/crystallizer/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T16:43:11Z
  TYPE: DECISION
  CLAIM: The crystallizer lane now explicitly separates two codegen streams.
    Generic codegen remains a namespace-backed scratch/runtime path and is not
    bindable by default. Deliberate synthetic modules are the explicit module
    identity path: the agent chooses a name, collisions are checked, the module
    is published to `sys.modules`, and that module provenance becomes the safe
    bind path for generated code. `Crystallizer` should track the managed
    synthetic-module registry and the `Rift`/room references to those
    deliberate modules, while generic codegen remains lower-ceremony scratch
    work.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:1-420
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace.py:1-158
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py:1-90
  - user_instruction: "I think the general way we do this is the synthetic_module system is deliberate"
  IMPACT: The provenance and lifecycle model is now cleaner. Bind/recovery work
    can target deliberate synthetic modules without forcing every codegen act into
    heavy managed truth.
  NEXT: use this stream split when we later define the concrete deliberate
    module creation flow, collision policy, and bind provenance checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T19:35:40Z
  TYPE: DECISION
  CLAIM: Deliberate synthetic modules now carry an ACL/import-policy
    consequence. Their chosen module names should be tracked in a managed
    `synthetic_module_imports` set so codegen import policy can explicitly
    allow those names. Generic scratch namespace code should not expand import
    availability the same way.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:1-460
  - user_instruction: "we could keep a synthetic_module_imports set and it could describe all the imports that we have and we would just need to allow those in the ACLs"
  IMPACT: Deliberate module creation is no longer only about provenance and
    bind safety. It also affects the managed import surface exposed back into
    codegen.
  NEXT: use this when we later define the concrete module-registry and import
    policy handoff between Crystallizer and the codegen ACL surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T11:48:32Z
  TYPE: DECISION
  CLAIM: The canonical crystallizer philosophy artifact has been rewritten into
    the current world-first model. The artifact now treats namespace-backed
    codegen as the default, Rift-local synthetic modules as valid local world
    material, bind as the promotion boundary into durable world truth, conduit
    snapshots as the primary reload unit, spell crystals as retained
    module/activation records instead of live spell mirrors, and mutation
    manifests as conduit-owned snapshot payloads when MutationResearch is
    present.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:1-322
  - artifact_board.md:17-19
  IMPACT: The crystallizer lane now has one modern canonical philosophy file
    that matches the recent runtime, codegen, conduit-snapshot, and mutation
    discussions instead of carrying older conflicting assumptions.
  NEXT: use this artifact as the reference point when choosing the next
    implementation-facing crystallizer slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T14:53:56Z
  TYPE: FACT
  CLAIM: A new focused artifact now captures the mutation-specific open
    question around forks, non-active versions, linkability, meldability,
    spellbook/contract updates, and why the current runtime does not yet prove
    that `mutation_fork` is cleanly solved. This keeps the lane from burying
    that concern inside broader crystallizer philosophy.
  EVIDENCE:
  - artifacts/IMPORTANT_CONSIDERATION.md:1-176
  - artifact_board.md:17-20
  IMPACT: The crystallizer lane now has one dedicated investigation artifact
    for mutation semantics instead of forcing those questions to live only in
    transient chat or overloaded notes.
  NEXT: use this artifact when mutation, conduit-snapshot, and spell-crystal
    semantics need to be revisited together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T15:54:59Z
  TYPE: DECISION
  CLAIM: The crystallizer philosophy now carries the newer environment-package
    boundary explicitly. `uv.lock` is treated as an environment/package
    asset/reference layer, not as something Crystallizer manages directly.
    Users/operators own broad site-package installation and any custom pip/uv
    loader behavior, while the internal Crystallizer loader validates the
    environment, throws when required package/module prerequisites are missing,
    and then rebuilds the world from crystals, assets, conduit snapshots, and
    optional mutation manifests.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:145-306
  - user_instruction: "uv.lock is more like a snaptool"
  - user_instruction: "the user just has to install the wide range of site-packages they want to use and we validate and throw if its missing something"
  IMPACT: The crystallizer lane now has a cleaner boundary between
    package-environment truth and world/module truth, which keeps Crystallizer
    out of package-manager ownership while still supporting bootstrap
    validation.
  NEXT: use this boundary when later defining site-package-backed crystals and
    the internal loader checks in more concrete detail.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T16:22:08Z
  TYPE: DECISION
  CLAIM: The artifact lane now states the operator boundary more explicitly.
    `uv.lock` is treated as an environment/package asset reference, users own
    broad site-package installation, custom package-install conduits or scripts
    remain allowed outside the core Crystallizer build, and the internal loader
    validates and throws instead of trying to directly own pip/uv controls.
  EVIDENCE:
  - artifacts/2026-04-26_crystallizer_philosophy.md:208-259
  - artifacts/2026-05-02_file_to_memory_bridge_mechanic.md:187-201
  - user_instruction: "the user just has to install the wide range of site-packages they want to use and we validate and throw if its missing something"
  IMPACT: The bootstrap/environment story is now clearer: environment truth is
    operator-provided and validated, while world/module truth is loader-owned
    and rebuilt from assets, crystals, snapshots, and manifests.
  NEXT: keep this boundary intact when later defining site-package-backed
    crystals and pod bootstrap behavior in more detail.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T17:13:48Z
  TYPE: DECISION
  CLAIM: The lane now has a dedicated crystallizer-configuration artifact for
    the optional synthetic-module copy mode. It defines the feature as an
    explicit bootstrap/reload-boundary mode, captures root reference targets
    and physical path targets, preserves canonical import names during
    registration into `sys.modules`, and ties the feature directly to snapshot
    byte-copy/rebuild workflows rather than to transparent live swapping.
  EVIDENCE:
  - artifacts/crystallizer_configuration.md:1-131
  - artifact_board.md:17-21
  - user_instruction: "make sure you make an artifact called crystallizer configuration"
  IMPACT: The crystallizer lane now has one feature-specific artifact for
    synthetic-module copy mode instead of forcing that configuration surface to
    live only inside the broader philosophy file.
  NEXT: use this artifact when we later decide what the actual crystallizer
    configuration object and eligibility rules should be in code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and subsystem boundaries.
- Add notes when asset taxonomy, boundary rules, or handoff contracts change.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic owns the design of Crystallizer as the asset/provenance bridge layer
between runtime registration and later MutationResearch work.
