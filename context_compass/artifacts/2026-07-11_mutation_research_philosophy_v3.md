# MutationResearch Philosophy V3 - The Built Model (2026-07-11)

STATUS: Canonical. Describes the SHIPPED system (owner-run green on 3.14t), not an
aspiration. Supersedes 2026-07-01 V2 and the 2026-05-09 May set wherever they
conflict; their identity layer (research graph of candidate runtime futures; NOT
git) is inherited, their machinery is replaced by what exists below.

## What MR Is
MutationResearch is the FORMAL DECLARATION RECORD of research over the live spell
world. Spells live their runtime lives elsewhere (spellbooks, conduits, custody);
MR answers exactly three questions: what have we formally declared as research,
where does it sit in the network of candidate futures, and how did it come to be.
It is drawn from git and is deliberately not git: commits are FULL OBJECTS
(binding-signature SHA256), diffs are derived read features, and there is no
checkout, no rollback, no merge, and no rebase - returning to an old version is a
new bind; combining content is composition in the codegen workshop re-entering as
a multi-parent declaration.

## The Objects (src/melder/mutation_research/)
- MutationResearch (root, Aether-hosted singleton): ResearchSet registry with a
  guaranteed `default` set; configuration lifecycle; the package's ONLY
  crystallizer touchpoint; diff facade; runtime-seam facades.
- research_set/ResearchSet: the agent-facing network. Verbs: register_spell,
  create_lane (optionally anchored), attach/detach (ancestry only), join
  (divergence-aware finisher), archive, walk/history/heads, campaign_view,
  snapshot_network/restore_network, describe_composition/from_payload,
  record_world_entry/record_promotion (runtime seams).
- ResearchLane: one object's line of versions; open -> joined | archived
  (terminal for the container); ordered full-object records; one ancestry anchor.
- ResearchNode: immutable reference-based record - spell_id (which IS the
  custody SpellCrystal id), module_source_sha256, parent ancestry, author/reason/campaign.
  Never pins source; custody owns the bytes under the same key.
- TransitionEntry + TransitionAct: immutable forward-only events. Vocabulary:
  lane_created, registered, staged, promoted, attached, detached, joined,
  archived, restored. No rollback acts exist by design.
- ResearchJournal: set-level monotonic append-only log; SURVIVES network restore;
  bounded describe window for the record; rebuilt journals continue minting
  without sequence reuse.
- ResidenceRegistry: SINGLE RESIDENCE - one SHA lives in exactly ONE lane
  network-wide, permanently (through archive). Identical content rebinds to the
  same SHA; the collision is the rediscovery signal naming the holding lane.
  No release verb exists.
- NetworkVersioner: version control of the ORGANIZATION itself - objects are
  indestructible, arrangement is what mistakes damage. Content-addressed
  (canonical-JSON SHA256) full snapshots, dedupe, bounded FIFO ring.
- diff/: derived reads over custody material via an injected resolver.
  DiffEngine (OCP registry) with two defaults: `source` (per-module unified
  diffs where text exists both sides; honest fingerprint-only verdicts where
  not) and `structural` (the reasoning layer: AST shapes - per-callable
  signature/docstring/body aspect flags, class add/remove/change, loud parse
  errors, honest text_unavailable bucket).

## The Verbs and Their Laws
- register_spell: the world-entry declaration. Default lane when none named (no
  orphan binds, no history holes). Parents must already be declared.
- join(lane, into, collapse, force): the finisher. Clean = anchored on the
  receiver with the receiver's tip AT the anchor (fast-forward analog); anything
  else is divergent and demands force=True (explicit supersede) - reconciliation
  by content is a codegen-workshop job, never a join feature. collapse moves the
  tip only, leaving the line readable in the joined container. Residence
  transfers with moved records; the source is terminal.
- archive: dead ends leave the active view; residence stays; snapshots restore
  views that contained them. The default lane never archives.
- restore_network: organization rewinds to a content address; the journal only
  ever grows (the restore itself journals forward as `restored`).
- Reads: walk (one line + its ancestry hop), history (one identity: holder,
  record, every touching event), heads (open-lane tips), campaign_view (stamped
  work gathered across lanes), diff_research (source/structural).

## The Runtime Seams (live wiring, not aspiration)
The spellbook's confirmation points auto-record while the MR root is ACTIVE:
- bind (dynamic posture) -> registered; bind_inactive -> staged; notch (the real
  _apply_notch swap) -> promoted (journal-only: promotion changes what is LIVE,
  never which lane holds a version; unknown incoming ids get world-entry
  catch-up).
Laws: the bind path PEEKS the root without constructing it; research bookkeeping
never gates a bind (rediscovery is an atomic quiet no-op); the record carries no
active flags - runtime residency (active/parked/stored) is a query-time join.

## Persistence (the twin loop, closed end to end)
- EMIT: every mutating verb re-emits the MutationResearchCrystal (replace-on-emit)
  through the normal sink: activated flag + configuration_payload + composition
  (organization, bounded journal window, undo-ring payloads). Lane records have
  ZERO runtime footprint; bytes live in custody; the twin is thin bookkeeping.
- RECORD: the twin rides checkpoints -> local cache -> user DB like every twin.
- HYDRATE (normal boot): a VIRGIN root (untouched default set only) rebuilds from
  the active profile's recorded twin at activate(); live research is never
  clobbered; hydrate_from_record=False opts out.
- RELOAD (restore): the engine's MR BUILD stage (melder_0,
  EPIC-2026-07-11-mutation-research-restore-build-stage) rebuilds from FOLDED
  truth: config reload verb -> configure -> activate(hydrate_from_record=False)
  -> load_recorded_composition; later-wins state replay; honest shortfalls for
  pre-Phase-B and cleaned-state payloads.
- The undo ring rides the composition (owner dial 2026-07-11), so organizational
  mistake-recovery survives pod death. The journal window stays bounded at the
  twin (owner precedent: "lanes + recent logs"); full history lives across the
  checkpoint sequence.

## What MR Is Not (inherited, still binding)
Not git with different names. Not a runtime activation system (SpellIndex holds
the one selected spell; MR holds no active flags). Not a gate system (the
mediator/notch plane owns admission). Not a storage system (crystallizer owns
bytes). Not conduit- or frame-scoped (they carry no mutation dimension).

## Open Directions (recorded, not promised)
- SpellState advanced-flag producers (mutation_candidate etc.) - a future slice
  over these same seams.
- Borrower fan-out recording when the cross-conduit notch slice lands.
- Impact/blast-radius promotion policy - reads melder_0's impact engine (V3
  horizon S3) plus this record; promotion POLICY was always the May end-game.
- module_source_sha256 at auto-registration stays None (custody carries module truth under
  the same key; per-bind describe() cost buys no information).
- SALVAGED from the archived May lanes (owner-directed read-before-archive,
  2026-07-11; sources: artifacts/2026-05-10_mutation_branch_type_enforcement.md
  + artifacts/2026-05-09_mutation_research_philosophy.md):
  - Lane TYPE classification - optional enum vocabulary
    (development/experiment/production/test) on lanes with an optional
    enforcement toggle; join/campaign policy could then warn or require force
    when types mix (e.g. experiment -> production). Names stay freeform; the
    type is the policy word. The old artifact's config key
    (branch_type_enforcement) maps cleanly onto lane vocabulary.
  - Surgical synthesis - the diff family shipped the structured REPORT half of
    the May "surgical mutation" flow; the unbuilt half is selection +
    synthesis: pick structural parts (methods/attrs/docstrings) from two
    version records and mint a NEW multi-parent node from the selection.
    Multi-parent nodes already express composition; the synthesizer is the
    missing verb.
  - Runtime recomposition - the May end-state verb
    (recompose a live object onto a selected candidate future's structural
    shape). Everything below it now exists (records, custody, diff, notch);
    recomposition is the step beyond notch where a selected future becomes
    live structure rather than a re-selection.

## Where the Truth Lives
Code: src/melder/mutation_research/** (+ spellbook seam hooks, crystallizer read
facade). Tests: tests/{unit,component,integration}/melder/mutation_research/**.
Design record: tickets/tasks/2026-07-05_wire_mutation_research_git_system_
investigation_task.md (the convergence trail) + tickets/stories/2026-07-11_build_
mr_research_set_core_story.md (the build trail). Docs: src_architecture.md /
src_components.md MR sections; graph nodes under melder.mutation_research.*.
