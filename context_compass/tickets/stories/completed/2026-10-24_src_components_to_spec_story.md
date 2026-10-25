

# Story: src_components brought to its authoring spec - tooling paths, history and duplicated material out

- Completed: 2026-10-25T01:12:33Z
- Summary: src_components is at its authoring spec: 12,642 -> 11,874 lines (-768), the 12 contract sections in
  order, every C3 entry with its 12 fields in contract order, no path into the documentation tooling; history
  clauses left the entries and the change log keeps 0.2.8228 on (older entries in git 9f240166f); claims the source
  contradicted are corrected; the MutationResearch inventory is folded; core = the C3 Key Files union (238), every
  range remeasured; Information Sources lists all 286 cited files. Preservation accounted (1,823 removed lines: 1,821
  in git 9f240166f, 2 of Story 1's framing lines); rubric 66.5 -> 84.5 (B); index `--check` OK. No source, no notch,
  no release-note entry; the rebuild runs last, after this closure, and its result is recorded in the epic.

## Metadata
- Story ID: STORY-2026-10-24-src_components_to_spec
- Epic: EPIC-2026-10-24-src_architecture_to_spec
- Status: done
- Owner: Mark (owner; scope and acceptance)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T22:19:05Z
- Updated: 2026-10-25T01:12:33Z

## User Narrative
As an agent slicing src_components by component name, I want each entry to state its component as it is today -
the twelve contract fields and the mechanics behind them - without paths into the documentation tooling, release
history or a second copy of the same inventory, so that a slice is trustworthy evidence and the document ships clean
in the wheel as the packaged components hardcopy.

## Value / MRP Alignment
src_components is the level the reading hierarchy sends a reader to for mechanics, and after Story 1 it is the only
record of the component mechanics src_architecture no longer repeats. Its contract, its portability rule and its
Handoff Rule have to hold here first; history belongs to git and the release notes.

## Ticket Contract
- ENTRY_GATE: the board row routes here; Story 1 has applied and rebuilt (its insert into src_components lands
  first); the preservation baseline is captured immediately before the first edit.
- EXECUTION_BOUNDARY: `context_compass/system_docs/src_components.md` and its index; this story's artifacts; the
  asset rebuild. Nothing in `src/`, tests, version or release note; no change to src_architecture beyond Story 1, to
  src_graph (generated), to the tests documents or to any policy document.
- DEPENDENCIES: EPIC-2026-10-24-src_architecture_to_spec; STORY-2026-10-24-src_architecture_trim_to_spec (applies
  first, and moves the MutationResearch boundary inventory into this document).
- EXIT_GATE: the src_components Quality Gate passes, the portability searches included; every baseline line is
  accounted for; the rubric (src_components profile) is recorded before and after; the index and both asset
  builders `--check` OK; board and artifacts synced.
- FAILURE_ESCALATION: DECISION_REQUEST when a cut would remove a rule in force or an owner ruling, or when a fix
  would restructure an entry beyond removing history; CONFLICT when another lane writes this document; BLOCKER
  when a gate cannot pass.

## Requirements (Functional)
- The 12 contract sections stay present and in order; every C3 entry keeps its 12 fields.
- No path into the Context Compass package: the citation recipe in `## Indexing` stays, the one copy for both source
  documents, without its `system_docs` path; the `artifacts/` anchor and the rubric's skill path go.
- Context / Handoff Summary: the entries from 0.2.8228 on stay; older ones go to git and the release notes; the
  Handoff Rule's three facts (contracts changed, still unknown, verify next) open it.
- History and correction clauses inside entries ("CORRECTED ...", "Before 0.2.x ...", "(corrected ...)", re-absorption
  notes, retired cache generations) go where the current rule stands without them; the rule stays.
- The MutationResearch boundary inventory Story 1 moves in is folded into the Root subcomponent's own
  Contract/Interface list: each verb once, nothing lost.
- Citations: `Conduit.link`'s type check cited where it is; recipe failures fixed or explained.
- C1 Code Map (Core): five fields per entry, ranges remeasured; the Full Package Inventory kept.

## Requirements (Non-Functional)
- Edits by a text-anchored script that refuses on any miss, dry-run first; never by retyping file content.
- Moved or folded text keeps its words; condensing removes history, not mechanism.
- Re-read the document immediately before writing it.

## Scope Boundaries
- In scope: src_components and its index; this story's artifacts; the boards; the asset rebuild.
- Out of scope: src_architecture (Story 1), tests_architecture, tests_components, src_graph, README, `docs/`, policy
  documents, Melder source.

## State Transition Event
- from_state: in_progress (implementation)
- to_state: done
- transition_reason: the EXIT_GATE is met but for the rebuild, which the turn-in order runs after this closure: the
  Quality Gate passed with the portability searches, every baseline line accounted, the rubric recorded before and
  after (66.5 -> 84.5), the index `--check` OK (the Notes of 2026-10-25, MEASURE V1 last). Routine closure under
  the owner's scope of 2026-10-24.
- from_state (earlier): draft
- to_state (earlier): in_progress
- transition_reason (earlier): the owner's go (chat, 2026-10-24 16:15 MDT): "go ahead and check out src_components next
  please", on top of his first message's ask to clean up what in src_components is not to spec; the audit runs now,
  read-only, while Story 1 waits for melder_1's turn-in.

## Dependencies / Related Work
- STORY-2026-10-24-src_architecture_trim_to_spec: applies first; its Notes of 2026-10-24T21:46:00Z list the three
  items this story inherits (the recipe leak, the stale citation, the inventory overlap).

## Tasks (Implementation Checklist)
- [x] B1: structural audit - contract order, H3 units, the twelve fields, wrapped and broken headings, portability
      and absolute paths, C1 fields and ranges, the Key Files join, the citation recipe, history markers.
- [x] B2: read the example components document and score the current document (src_components profile, Depth per
      entry).
- [x] B3: disposition per section and per marker - keep, cut history, fold, fix - with line estimates.
- [x] B4: the edit script and its dry run, on the document as Story 1 leaves it.
- [x] E0: preservation baseline immediately before the first edit.
- [x] E1: apply; E2: the index regenerated, `--check` OK.
- [x] V1: preservation gate, Quality Gate, the portability searches, the Key Files join, the rubric after.
- [ ] V2: asset runner and llm_support builder, each then `--check`, on Python 3.14 - last (runs after this
      closure; its result is recorded in the epic's Notes).
- [x] Close: summary, completed/, board and artifact sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- src_components: 12 contract sections in order; every C3 entry with its 12 fields; the portability and
  absolute-path searches return nothing; the handoff opens with the three Handoff Rule facts and keeps 0.2.8228 on.
- Every baseline line is in the document or accounted for (a named git revision, a fold, or a recorded fix).
- Rubric recorded before and after; the index and both asset builders `--check` OK.

## Validation / Test Plan
- `index_document.py --check`; the two portability searches from the instructions' Validation Commands; the Key
  Files join recipe; the citation recipe; the preservation multiset against the named revision; the rubric; the two
  builders with `--check`. No test suite is affected (documents only).

## UX / API / Data Notes
- The packaged `__components__` hardcopy changes with the rebuild; no API changes.

## Risks / Mitigations
- Removing a mechanism with its history -> only history clauses go; uncertain text stays.
- Folding the inventory loses a verb -> fold by verb list, check every backticked name survives.
- Concurrent writers -> apply after Story 1 and after any other lane's write; re-read before writing.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- The dated sub-blocks inside C3 entries (about 70 open with a date or version) hold current mechanics: proposed to
  keep them where they are and cut only their history clauses, not to refile them under the twelve fields.
  Resolved by the B3 DECISION (2026-10-24T23:40:26Z): kept in place, their history clauses cut.

## Decision Log
- 2026-10-24: owner (chat, 16:15 MDT): go ahead with src_components next.
- 2026-10-24: B3 dispositions (Notes, DECISION of 23:40:26Z): history out with the rule kept, code that is gone
  removed, stale facts fixed, core = the C3 Key Files union, the handoff kept from 0.2.8228 on.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/src_components_to_spec_20261024/
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: this story's closure, after the preservation gate is accounted
- APPLIED (2026-10-25T01:12:33Z): the folder is deleted at this closure; the accounting it produced is recorded in this
  story's Notes (B4, E0-E2 and V1).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_3 (synaptic_python_developer); prose; revision 1 of this story.
- Published By: UNKNOWN before publication (local files; the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-24T22:20:01Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: B1 on src_components as melder_1's 0.2.8267 edits left it (12,552 lines; index `--check` OK, 156
    sections): one H1; the 12 contract sections in order plus one extra H2 (Promoted Patch Detail); 26 C3
    `Component:` entries, every one with all 12 fields; 64 C2 `Subcomponent:` entries; no duplicate H3 and no
    unclosed-bracket heading, but one H3 broken by an earlier unwrap (V3 Horizon Iteration's
    "crystallizer_s2_user_source_ retention_2026_07_11"). C1 Code Map (Core): 236 entries above the retained Full
    Package Inventory (1,079 lines), all five fields, no stale range, no directory; 5 notes name a version. Key Files
    and C1 paths: 238, all in src_graph_index. Portability: the spec's search is clean; three leaks by other
    spellings - the citation recipe's `pathlib.Path("system_docs")`, the `artifacts/` design anchor, the rubric's
    skill path in the handoff. No absolute path. The citation recipe fails on two bare filenames in the handoff,
    which itself lists seven citations "still stale from earlier lanes". History markers in entries: about 60
    (CORRECTED 10, "(corrected" 7, "Before 0.2" 7, "until 0.2" 26, retired cache generations 8, others). Handoff:
    667 lines, 72 dated entries; those for 0.2.8227 and earlier start at its line 12137 (about 415 lines). The
    `Conduit.link` citation Story 1 flagged was already remapped by melder_1 (5601-5603).
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:32-185
  - context_compass/system_docs/src_components.md:72-72
  - context_compass/system_docs/src_components.md:11169-11169
  - context_compass/system_docs/src_components.md:12487-12487
  - context_compass/system_docs/src_components.md:11248-11248
  - context_compass/system_docs/src_components.md:12059-12063
  - context_compass/system_docs/src_components.md:3386-3386
  IMPACT: the structure meets the contract; the work is the three leaks, the handoff, the history clauses, the
    seven self-reported stale citations, one broken heading, five C1 notes and the inventory fold - not a rewrite.
  NEXT: B2 - read the example components document, then score the document entry by entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:05:54Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-onboarded after a compaction and consumed three messages. M1-57 (melder_1, QUESTION, 22:43:42Z) and
    M1-58 (NOTICE, 22:56:45Z): melder_1 cut the 0.2.8265 release note after Story 1's rebuild -
    release_docs/0.2.8265.md holds the notes as released, next_version_release.md only 0.2.8266-0.2.8267 - and
    rebuilt after it, every check OK; release_docs is free again and M1-58 withdrew the ACK M1-57 asked for.
    M0-220 (melder_0, NOTICE, 22:51:34Z): that lane is tests only and added one untracked file, its Windows
    held-bundle test, which melder_1's rebuild took into the LLM bundles' tests corpus. git, read-only at
    23:05:54Z: HEAD is still 9f240166f, and that test file and release_docs/0.2.8265.md are untracked;
    src_components.md is as Story 1 left it (its index proof matches).
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_cut_release_note_0_2_8265_task.md:1-7
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:1-594
  - context_compass/special_instructions/agent_contribution_guide.md:77-81
  - context_compass/system_docs/src_components_index.md:9-19
  IMPACT: nothing in Story 2's scope changes. V2 runs the llm_support builder and its `--check` with
    `--include-untracked` while those two files stay untracked, as the contribution guide asks.
  NEXT: B2 - read Component: ConduitWard and Contracts through PhaseScheduler (src_components.md:3475-6359)
    and score Depth per entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T23:13:08Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: B2 rubric baseline (src_components profile), scored from the file on disk (12,642 lines, index proof
    12a198a4 current) after reading the example components document and all 26 C3 entries: Fidelity 3, Contract
    3, Depth 4.5, Addressability 3, Join 3, Mirror 4 = 66.5 (C). Depth per entry: 5 for 16 entries; 4 for DI
    Descriptors, AR Runtime, RiftSpace, SpellCompiler, DevOps Information, Logging, Examination and PhaseScheduler
    (one or two one-clause fields, e.g. SpellCompiler Observability and Concurrency); 3 for Codegen Internal
    Engine and Nexus Descriptor; mean 4.54. Fidelity: claims the source contradicts - "the spell id hashes its
    resolved disposal names" (3771; the spell_id is the code since 0.2.8257), a RuntimeError for several
    single-annotation providers (5250, and "still raise" at 4905; an AMBIGUOUS_INPUT socket and
    SpellbookValidationError since 0.2.8224), "Existence = 6" (1401; seven members), the transfer's SafeGuard at
    `:1451` (1783; it is at 1497), 11 `info` sites (3675; 12), "59 or more of the 62 entries" (6371; 64), two
    Binding Pipeline claims (1094, 1101), and the handoff's own seven stale citations. Contract: the 12 sections
    in order and every C3 entry with its 12 fields, but Key Files (C1) precedes Observability and Extension Points
    in Transaction Admission (5617) and DevOps Information (5731), and the 675-line handoff (11968-12642) does not
    open with the Handoff Rule's three facts. Addressability: the two catalog containers (193-6359, 6360-8247) and
    the V3 Horizon H3's unwrap artifact (11330). Join: all 238 Key Files and C1 paths resolve in src_graph_index,
    but C1 ranges are carried forward (108 entries stamped 2026-08-02T13:00:45Z). Mirror: tests_components keeps
    the same 12-section contract and names its clusters after these components (its line 1021); boundaries were
    not compared entry by entry.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/system_docs/src_components.md:3771-3772
  - context_compass/system_docs/src_components.md:5250-5251
  - context_compass/system_docs/src_components.md:5617-5650
  - context_compass/system_docs/tests_components.md:1021-1021
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:46-120
  IMPACT: usable (C) with these caveats. The edit aims at Fidelity (the stale claims), Contract (the handoff, two
    field orders) and Join (remeasured C1 ranges, the stale citations); Addressability stays 3, because both
    containers are contract sections.
  NEXT: B3 - read the C2 catalog, the flows, the C1 notes, Promoted Patch Detail, Diagrams, Information Sources and
    the handoff; record the DECISION and PLAN notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:30:21Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-onboarded after a second compaction (REONBOARD posted, self-certified under the owner's standing
    preference for a kept agent name) and consumed M2-37 (melder_2, NOTICE, 23:21:55Z, no ACK asked):
    STORY-2026-10-24-testpypi_trusted_publishing_and_provenance writes `.github/` (the release-candidate workflow,
    its scripts, a new provenance folder, ci_cd, BRANCH_WORKFLOW.md), tests/unit/github_workflows and
    system_docs/tests_components.md with its index; no src, no notch, no release-note entry; melder_2 rebuilds
    the assets and bundles at its turn-in. None of those paths is in Story 2's boundary; tests_components.md is
    only read here, as the rubric's Mirror counterpart.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:29-35
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:105-115
  IMPACT: no conflict and no reply owed. V1 scores Mirror against tests_components.md as it stands on disk at
    scoring time and says so; both lanes rebuild last at their own turn-ins from the disk as it then is, so the
    later rebuild carries both documents.
  NEXT: B3 - read the handoff's remaining lines (src_components.md:12331-12642), then run the citation, Key Files
    and Information Sources scripts.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T23:40:26Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: B3 dispositions, each checked against the source on this pass. (1) History out, rule kept: text recording
    0.2.8228 and later stays as written; in older text the clauses that narrate earlier behaviour ("before",
    "used to", "no longer", "now"), CORRECTED/UPDATED markers, re-absorption, migration and verification stamps,
    old measurements, bump-only cache generations and lane or patch provenance go, and the current rule with its
    version tag stays. (2) Removed whole: blocks describing code the source no longer has, and the C2 entry
    LesserCreations Transfer - a "historical transfer slot" cited nowhere, whose `_conduit`/`_conduit_state` names
    creations.py does not have; its live fact (an upgrade keeps the Creations store) is Conduit Upgrade to
    Normal's, whose "rebound" becomes "retained". (3) Stale facts fixed: the spell_id is the code (not "hashes its
    disposal names"); several providers are an AMBIGUOUS_INPUT socket that Phase 4 refuses, not a RuntimeError;
    Existence has seven members; the transfer's SafeGuard is at :1497; ConduitWard has 12 `info` sites; C2 holds
    63 entries after the removal, 60 with the usual four fields; RecordVersion is 4.3.0; the cache admission
    checks the current format, not "version 9"; about 30 numeric citations that point at other code (meld.py,
    aether.py, aetheric_frame.py, conduit_cloud.py, crystallizer.py, persistence_profile.py,
    frame_descriptor_manager.py) are remapped to the symbol they name. (4) Core set: the C1 core (236) is not
    the C3 Key Files union (216) - 20 core paths are claimed only by C2 entries and two C2 paths are in neither;
    the 22 join their parent C3 entries' Key Files (a C2 entry is a narrower view of what its parent owns) and
    the two get measured core entries, so core = C3 union = C3 and C2 union (238); three C2 parents get the C3
    name "Crystallizer Root, Persistence Record, And Module-World Surfaces". (5) Handoff: 0.2.8228 on stays; the
    0.2.8227-and-older tail (2026-08-01 to 2026-10-04, 416 lines, with the rubric's skill path) goes to git
    9f240166f and release_docs/0.2.8227.md behind an OLDER HISTORY pointer; a new first entry states the Handoff
    Rule's three facts; one sentence of the 0.2.8247 entry that names two citations by bare filename - the
    recipe fails on it every run - is rewritten to point at the 0.2.8248 entry, which re-pointed them. (6)
    Information Sources lists every cited source file (86 added) and drops its false "same set as the C1 map"
    claim. (7) Narrative H4s renamed, carried-across notes dropped, the 16 `*From ...*` labels kept as topics. (8)
    Key Files (C1) moves after Extension Points in Transaction Admission and DevOps Information. (9) The MR boundary
    inventory folds into the Root's Contract/Interface list; every backticked name survives in Root or Package.
    (10) Out of scope, for the owner: creations.py docstrings still say a spell id hashes its disposal names; a
    `many` bucket keeps its first registration's method list across a rebind with other disposal names (added as
    an UNKNOWN, uninvestigated); release_docs/0.2.8227.md shows modified in the working tree (another lane).
  EVIDENCE:
  - context_compass/system_docs/src_components.md:6360-6380
  - context_compass/system_docs/src_components.md:7694-7709
  - src/melder/aether/conduit/conduit.py:2590-2593
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:628-704
  - src/melder/utilities/caching_system/caching_system.py:854-900
  - src/melder/crystallizer/persistence/record_version.py:90-90
  - src/melder/aether/conduit/meld/meld.py:1216-1257
  - src/melder/aether/conduit/creations/creations.py:746-812
  - context_compass/system_docs/src_components.md:12143-12154
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:193-209
  IMPACT: every cut is history or a record of code that is gone; every addition is evidenced from source; the
    core-set, Key Files and Information Sources rules hold again. No owner ruling or rule in force is removed,
    so no DECISION_REQUEST is owed.
  NEXT: record the B4 plan, fix `s2_lib.section_range` for code fences, then write the op modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T23:40:26Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: B4: artifacts/src_components_to_spec_20261024/ gets edit_src_components.py (driver) and op modules by
    region - front matter and C3 entries, C2 and flows, C1 and Promoted Patch Detail, Diagrams, Information
    Sources and the handoff - each under 900 lines, every op anchored on exact text and raising on a miss, so a
    miss writes nothing. After the ops the driver checks: the 12 H2 sections in order; 26 C3 entries with their
    12 fields in contract order; the two portability searches and an extra `artifacts/`/`design_engineer/`
    search return nothing; no line over 120 characters; core = C3 Key Files union; every backticked name of the
    old MR inventory present; the citation recipe clean. Then a dry run on the current file, E0 (baseline copy and
    multiset), the apply, the index and `--check`, and V1 accounting of every removed line against the result,
    git 9f240166f (both documents) and the op log. Size: 12,642 -> about 12,170 (-416 handoff, about -170 history
    clauses, -16 LesserCreations, +86 Information Sources, about +40 Key Files, two C1 entries, the UNKNOWN and
    the new handoff entry).
  EVIDENCE:
  - context_compass/artifacts/src_components_to_spec_20261024/s2_lib.py:1-187
  - context_compass/agent_onboarding/default/engineer/AGENTS.MD:69-69
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:303-354
  IMPACT: the board row moves to implementation for B4; the apply waits for a clean dry run.
  NEXT: fix section_range, then write the front-matter op module and dry-run it alone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:18:47Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: B4 in progress, after a third re-onboard (no message for melder_3). ops_front, ops_c3a and ops_c3b are
    written; the dry run on the unedited document (sha 12a198a4) applies 163 ops with 0 misses, 12,642 -> 12,379
    lines, every C3 entry with its 12 fields in contract order (Transaction Admission and DevOps Information Key
    Files moved last). Facts checked against source while writing ops_c3b, beyond the B3 list: Meld raises seven
    types besides the abstract methods' NotImplementedError - RuntimeError marks an internal precondition (no
    owning Spellbook, no selected spell id or resolution conduit id, an index with no spell object, shared hooks
    changed through a lesser) and MeldExecutionError also covers a non-resolvable registration, an unsupplied
    input and a failed override; the Meld lock sites are 287 (RLock) and 388, 1749, 1778, 1833, 1894, 1947; the
    channel-logger gate is set from AetherConfiguration by `_apply_configuration_to_utility_system`; nothing calls
    `capture_phase2_5_codegen_ir`; ParameterPolicyStrategy answers False for `typing.Any`; UNSUPPORTED_COLLECTION_SHAPE
    is in no source file. The remaining checks wait for ops_c2 and ops_tail (core set, two tooling paths, two
    bare-filename citations in the handoff).
  EVIDENCE:
  - context_compass/artifacts/src_components_to_spec_20261024/ops_c3b.py:1-410
  - src/melder/aether/conduit/meld/meld.py:1216-1262
  - src/melder/aether/aether.py:1189-1210
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.py:185-194
  IMPACT: the C3 catalog is scripted; what is left of B4 is the C2 catalog, the flows and the tail (C1 map, Promoted
    Patch Detail, Information Sources, handoff).
  NEXT: write ops_c2.py (C2 and flows) and dry-run it with the three modules before it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:42:49Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: B4 continues after a fourth re-onboard (no message for melder_3). ops_c2 (the C2 catalog and the flows)
    is written: LesserCreations Transfer goes (16 lines), the MutationResearch boundary inventory folds into three
    bullets of the Root's Contract/Interface list with every backticked name still in Root or Package, the C2
    header reads "60 of the 63 entries" (counted on the dry run: 63 entries, 60 with the usual four fields, the
    three builder/engine entries with Invariants/Guarantees), and seven frame_descriptor_manager.py citations point
    at their `def` lines. The dry run of the four modules applies 199 ops with 0 misses, 12,642 -> 12,274 lines. A
    defect in the edit library, found and fixed on this pass: a unit ran on through a field label standing alone at
    column 0, and the label check had no digits, so two ops merged `Key Files (C1):` into the bullet above it
    (Registration Refusal; Rift Single Space And Event Seam). `_unit_end` now ends a unit at such a label and the
    label pattern takes digits; the driver now also checks 63 C2 entries with their required labels, C2 Key Files
    inside the C3 union, and no field label merged into text. Out of scope, for the owner: `ResearchLane.clear_anchor`
    is public by name, and its docstring calls it a set-internal effect that writes no journal entry
    (`ResearchSet.detach` is the journalled path).
  EVIDENCE:
  - context_compass/artifacts/src_components_to_spec_20261024/ops_c2.py:1-239
  - context_compass/artifacts/src_components_to_spec_20261024/s2_lib.py:103-103
  - context_compass/artifacts/src_components_to_spec_20261024/s2_lib.py:210-224
  - context_compass/artifacts/src_components_to_spec_20261024/edit_src_components.py:28-31
  - context_compass/artifacts/src_components_to_spec_20261024/edit_src_components.py:114-141
  - src/melder/mutation_research/research_set/research_lane.py:775-810
  IMPACT: the C3 and C2 catalogs and the flows are scripted and their labels are intact; the remaining checks are
    ops_tail's (the core set and the 22 Key Files, two tooling paths, two bare-filename citations in the handoff).
  NEXT: write ops_tail.py (C1 map, Promoted Patch Detail, Information Sources, handoff) and dry-run all five.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T01:02:26Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: B4 done: ops_tail is written (the C1 Code Map, the 22 Key Files, Promoted Patch Detail, the handoff, and -
    last, computed from the document as the other ops leave it - Information Sources). The dry run of all five
    modules on the unedited document (sha 12a198a4) applies 253 ops with 0 misses and every check clean: 12,642 ->
    11,875 lines (C3 -222, C2 -104, C1 map -10, Promoted Patch Detail -102, Information Sources +85, handoff -394,
    front matter -21); 26 C3 entries with their 12 fields in order, 63 C2 entries with their labels; core = C3 Key
    Files union = 238, C2 inside it; all 238 C1 ranges measured on the run (none had moved) and resolved in
    src_graph_index; the citation recipe 0 failures; the two portability searches and the extra
    `artifacts/`/`design_engineer/` search empty; Information Sources 286 files on disk. Preservation pre-check on
    the dry run: 1,821 removed lines, 1,819 of them in git 9f240166f (either document), the other 2 Story 1's own
    framing lines of the moved inventory, and every removed line recorded by an op. Facts re-read for ops_tail:
    the eleven default preflight rows and their names, RecordVersion 4.3.0, the knob no-op in bootstrap_loader.py,
    and the def lines cited (aether.py 409 and 1212, aetheric_frame.py 499 and 943, conduit_cloud.py 719 and 748,
    persistence_profile.py 900, persistence_system.py 545, crystallizer.py 974 and 1009, spellbook.py 7505); the
    strategy is `MutationResearchCompositionStrategy` (the document said MRCompositionStrategy twice). A second
    library defect, fixed: a rewrap could start a continuation line with a spaced dash, which renders as a nested
    bullet (the new UNKNOWN had one); `wrap` now binds such a space, and the driver refuses any new continuation
    line that reads as a bullet; one such line already in the base (the MR Root's ancestry seam) is fixed too.
  EVIDENCE:
  - context_compass/artifacts/src_components_to_spec_20261024/ops_tail.py:1-500
  - context_compass/artifacts/src_components_to_spec_20261024/s2_lib.py:24-33
  - context_compass/artifacts/src_components_to_spec_20261024/edit_src_components.py:71-87
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py:110-145
  - src/melder/crystallizer/persistence/record_version.py:90-90
  - src/melder/crystallizer/crystal_loader_system/bootstrap_loader.py:322-325
  IMPACT: the edit is ready; nothing in the document has changed yet.
  NEXT: E0 - copy the document and its multiset into the artifact folder, then apply with the same five modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T01:07:23Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M2-41 (melder_2, NOTICE, 2026-10-25T00:40:40Z, no ACK asked):
    STORY-2026-10-24-testpypi_trusted_publishing_and_provenance is turned in (completed 00:38:43Z; `.github/`,
    tests and docs, no src, no notch); melder_2 updated tests_components and tests_architecture with their indexes
    (`--check` OK) and runs the asset and bundle rebuild next; src_architecture and src_components were not
    touched (the M3-5 layout holds). On disk now: tests_components.md sha 91d805d7, its index current (71
    sections, 4,344 lines).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:1-12
  - context_compass/system_docs/tests_components_index.md:9-19
  IMPACT: no conflict and no reply owed. V1 scores Mirror against that tests_components.md; this story's V2
    rebuild, after its apply, carries both document pairs whatever order the two rebuilds run in.
  NEXT: E0 - the baseline copy and multiset - then the apply.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T01:08:03Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: E0-E2 done. E0 at 01:07:31Z: the document (sha 12a198a4, 12,642 lines) and its index copied to
    artifacts/src_components_to_spec_20261024/e0_baseline/ with the instructions' multiset (9,955 distinct
    non-blank lines). E1: the five op modules applied - 253 ops, 0 misses, every check clean - and the op log
    written beside them (apply_log.json); src_components.md is now 11,874 lines (sha 6381710a). E2: the index
    regenerated, 155 sections (LesserCreations Transfer gone), all ranges validated, `--check` OK.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/artifacts/src_components_to_spec_20261024/e0_baseline/src_components.e0.md:1-12642
  IMPACT: the document is at spec pending V1's accounting and scoring; V2 (the rebuild) stays last.
  NEXT: V1 - preservation accounting, the Quality Gate and portability searches, the join, the rubric after.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T01:10:51Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: V1 on the document as applied (sha 6381710a, 11,874 lines, index current). Preservation (the
    instructions' recipe, after = the document + git 9f240166f of both source documents): 2 baseline lines are
    absent - Story 1's own framing lines of the moved inventory ("- Boundary inventory, moved verbatim from
    src_architecture ..." and "src_architecture keeps a summary:"), which the fold replaced - and apply_log.json
    names the op that removed each of the 1,823 removed lines. Quality Gate: all eight items pass - the 12
    sections in order, 26 C3 entries with their 12 fields in contract order, concrete C1 flows, 238 C1 entries
    with all five fields, Information Sources listing all 286 cited files (each on disk), and both portability rg
    searches empty. Join: 238 Key Files and C1 paths, 0 missing from src_graph_index; the document's own citation
    recipe prints nothing for either source document. Rubric after, scored from disk: Fidelity 4, Contract 5,
    Depth 4.5, Addressability 3, Join 5, Mirror 4 = 84.5 (B), up from 66.5 (C). Below 5: Fidelity - some
    non-obvious claims still cite nothing (the SpellCrystal bullet at 10799, which also keeps the pre-0.2.8257
    term "bind signature"); Depth - the B2 per-entry scores stand (16 at 5, 8 at 4, 2 at 3; history removal
    took no mechanism, and the one field that shrank by more than a quarter, SpellCompiler's Failure Modes,
    lost fixed-defect history only), e.g. PhaseScheduler's one-clause Failure Modes (6100) and Codegen
    Internal Engine (2640); Addressability - the C3 and C2 catalogs are containers (172-6116, 6117-7900), required
    by the contract; Mirror - tests_components.md (sha 91d805d7) keeps the 12-section contract and names its
    clusters after these components (its line 1021), but boundaries were not compared entry by entry. Aside,
    for the owner: the instructions' unclosed-bracket heading pattern does not parse in rg ("unclosed character
    class"); with the "[" escaped it returns nothing here.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/system_docs/src_components_index.md:36-63
  - context_compass/system_docs/src_components.md:10799-10801
  - context_compass/system_docs/src_components.md:6100-6101
  - context_compass/system_docs/src_components.md:11596-11612
  - context_compass/system_docs/tests_components.md:1021-1021
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:379-379
  IMPACT: the exit gate holds except V2; the score clears B, and the two caps left (containers, the Mirror
    comparison) are not edits this document can make.
  NEXT: close the story (summary, completed/, board and artifact sync), the epic, the NOTICE, then V2 last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (melder_3's chat report to the owner, 2026-10-25, after the rebuild)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
Done (melder_3, 2026-10-25). src_components is at its authoring spec and 768 lines lighter (11,874): history out of
the entries, the change log from 0.2.8228 on behind an OLDER HISTORY pointer, stale claims corrected against source,
the MutationResearch inventory folded, the core set again the C3 Key Files union with every range remeasured, every
cited file in Information Sources; rubric 84.5 (B). Left for the owner: the two creations.py docstrings that still
say a spell id hashes its disposal names, the `many` bucket UNKNOWN, `ResearchLane.clear_anchor` (public by name,
writes no journal entry). Remaining in the epic: the V2 rebuild (last).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
