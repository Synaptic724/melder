# EPIC-2026-07-19-oce-aether-conduit

- Completed: 2026-07-19T21:40:00Z
- Summary: All 30 classes under `src/melder/aether/conduit/**` raised to 3+ canonical
  docstring headers with subsystem and system context; guards 30/30 with both MRO cases
  (`Meld`, `Creations`) adjudicated as redundant-not-defective. No behaviour changes.
  Owner 3.14t pytest OUTSTANDING.

- Status: done_pending_owner_run
- Created: 2026-07-19T17:45:00Z
- Updated: 2026-07-19T17:45:00Z
- Owner: cowork
- Agent Name: melder_0
- Parent: tickets/epics/2026-07-19_object_contract_enrichment_program_epic.md

## Problem / Opportunity
The conduit subsystem is the RESOLUTION RUNTIME - the layer a user actually touches after
`conjure(...)`. It carries 30 classes, of which 27 have two or fewer canonical docstring
headers and 11 have ZERO. These are the objects a user holds in their hands (`Conduit`,
`SpellSpace`, `Policies`, `Permissions`, `ConduitCluster`), yet they are the least
documented tier in the package. That is backwards for a public library.

## Context (why now, relationship to architecture)
Conduit sits at layer 4 of the runtime: Aether -> AethericFrame -> Spellbook -> CONDUIT ->
Meld -> Creations. `Spellbook.conjure(...)` produces exactly one Conduit; every instance the
user resolves comes through `Conduit.meld(...)` -> `Meld` -> `CreationContext` ->
`Creations`. Contract/policy/permission semantics for cross-conduit sharing live in
`ConduitWard`. Evidence: `system_docs/src_architecture.md` (Conduit Lifecycle,
Resolution and Meld Pipeline, Existence and Scoping Model).

## MRP alignment
MRP, not MVP: the contract text must be right the first time because docstrings ARE the API
for a public library. Partial or guessed contracts are worse than none - they get trusted.

## Ticket Contract
- ENTRY_GATE: parent program epic active; conduit survey complete with per-class
  guard + docstring-rank measurement recorded below.
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/**` ONLY. No edits to spellbook, aether
  root, nexus, or crystallizer. No behaviour changes - docstrings, comments, and guard
  sentinels only.
- DEPENDENCIES: THE OBJECT CONTRACT + THE MRO LAW + THE CHUNKING LAW from the parent epic;
  the mandatory 4-check codemod validation set recorded in the parent epic RISK note.
- EXIT_GATE: 30/30 classes at 3+ canonical headers; guard classification complete and
  justified; py_compile clean; 0 trapped lines; 0 unresolvable imports; 0 duplicate
  sentinels; 0 whitespace-only diff files; owner 3.14t pytest green.
- FAILURE_ESCALATION: any behaviour-changing find (a guard that must be REMOVED, a
  doc-code contradiction) becomes a DECISION_REQUEST note; do not self-apply.

## Goals / Non-goals
Goals:
- Rank 4+ class docstrings on all 30 classes with Subsystem Context and System Context.
- Correct guard classification on every class, with the reasoning recorded.
- Public-method docstrings raised to Rank 4 where they are thin.
Non-goals:
- No behaviour changes. No renames. No API shape changes.
- Not touching `spell_compiler` (owner ruled it out of scope: "the goal is user facing assets").

## Scope boundaries
IN: conduit.py, conduit_cluster.py, conduit_pool.py, conduit_state/, conduit_ward/**,
creations/**, meld/**, spell_space/**.
OUT: everything else under `src/melder`.

## Requirements
Functional:
- Every class carries the canonical headers appropriate to its kind.
- Every guard decision is one of the three classifications (BASE CLASS / USER-BINDABLE /
  MELDER KERNEL) and says WHY in its `Registration:` section.
Non-functional:
- No `# noqa`, no `type: ignore`, no PEP 604 unions, no wildcard imports, no
  `from __future__ import annotations` (`skills/python/banned_patterns.md:57-71`).
- Never delete a comment or docstring; update stale ones instead
  (`skills/python/comments.md:17-19`).

## Acceptance criteria
- [ ] 30/30 classes at 3+ canonical headers.
- [ ] Guard classification complete: currently 26 guarded / 4 unguarded.
- [ ] MRO-law audit clean or every exception justified in writing.
- [ ] Validation set passes (compile, trapped-line, import-resolution, whitespace).
- [ ] Owner 3.14t pytest green.

## Risks / Mitigations
- RISK: the codemod line-ending hazard recorded in the parent epic. MITIGATION: the
  mandatory 4-check set; `splitlines(keepends=True)` only.
- RISK: documenting a contract that the code does not actually honour. MITIGATION: read the
  implementation and verify each behavioural claim against source before writing it.

## Validation plan
py_compile over the package; AST audits for guards, duplicates, trapped lines, and import
resolution; `git diff --ignore-all-space` file-count parity. Owner runs pytest on 3.14t -
the sandbox is 3.10 and cannot execute this package.

## Decision Log
- 2026-07-19: conduit chosen as the next child epic after crystallizer, on the parent epic's
  user-facing-first ordering.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: survey complete; classification rulings evidenced; implementation starts.

## Milestones
- [x] M1 survey (30 classes measured for guard + docstring rank)
- [x] M2 MRO adjudication for `Meld` and `Creations`
- [x] M3 guard the 4 unguarded kernel classes (30/30 guarded)
- [x] M4 docstring enrichment, ward/contract tranche (9/9)
- [x] M5 docstring enrichment, meld/creations tranche (10/10)
- [x] M6 docstring enrichment, conduit/spellspace tranche (11/11)
- [~] M7 validation: 5-check set PASSES; owner 3.14t pytest OUTSTANDING

## Applicable Anti-Patterns
- Documenting from naming rather than implementation (Unknowns Gate).
- Sweeping a guard sentinel across a base class without the MRO check.
- Claiming tests ran when they did not.

## Artifact Links (Optional)
None.

## Context Management
CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Epic-level: cross-tranche direction, classification rulings, and tranche order.

## Notes

- TYPE: MEASURE
  DATETIME: 2026-07-19T17:45:00Z
  AGENT: melder_0
  CLAIM: Conduit survey baseline. 30 classes: 26 guarded, 4 unguarded, 27 thin
    (<=2 canonical headers) and 11 with ZERO headers. The zero-header set is exactly the
    user-facing vocabulary: `Policies`, `Permissions`, `Contract`, `Detail`, `IndexDetail`,
    `DetailReason`, `ContractTypes`, `TransferOfOwnership`, `ConduitWard`, `Meld`,
    `SpellOverrider`. The four unguarded are `CreationContextBuilder`,
    `CreationContextFactory`, `SpellSpaceThreadState`, `_SpellSpaceLocal`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1-39
  - src/melder/aether/conduit/meld/meld.py:42-88
  IMPACT: The least-documented tier of the package is the tier users touch most.
  NEXT: Guard the four kernel classes, then enrich by tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: DECISION
  DATETIME: 2026-07-19T17:45:00Z
  AGENT: melder_0
  CLAIM: MRO-LAW ADJUDICATION for conduit - `Meld` and `Creations` are guarded AND are
    bases, but this is REDUNDANT, NOT A DEFECT, so both sentinels STAY.
    `Meld(Cleanable, ABC)` is the base of `ConduitMeld` and `SpellSpaceMeld`;
    `Creations(Cleanable)` is the base of `ConduitCreations` only (`ClusterCreations`
    extends `Cleanable` directly, NOT `Creations` - the survey's "BASE of 1" is correct).
    Every one of those subclasses is melder-internal and is constructed ONLY inside
    `conduit.py`. A repo-wide grep for injection parameters (`meld:`/`creations:`/
    `*_class`/`*_factory` kwargs) returns no user seam - the only hits are an unrelated
    `fast_has_existing_creations` bool in the codegen lane plan. So the inherited sentinel
    can never reach a USER class, and the MRO law is not violated.
    CONTRAST with `PersistenceAnalysisStrategy` (crystallizer): that base IS user-extensible
    because `PersistenceAnalyzer.__init__` accepts an injectable `strategies` list, which is
    exactly why it remains an open DECISION_REQUEST and this one does not.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:276-304
  - src/melder/aether/conduit/meld/meld.py:42-42
  - src/melder/aether/conduit/creations/creations.py:10-10
  - src/melder/aether/conduit/creations/cluster_creations.py:10-10
  IMPACT: Establishes the general rule - a guarded base is a defect ONLY where a user
    injection seam exists. Guard-base + all-internal-subclasses is merely redundant.
  NEXT: Apply the same injection-seam test to the remaining repo-wide MRO risk list
    (`RiftSpace`, `CommandSystem`, `Creations`, `FrameViewer`) in their own child epics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- TYPE: MEASURE
  DATETIME: 2026-07-19T18:10:00Z
  AGENT: melder_0
  CLAIM: M3 COMPLETE + M4 partial. Guards: 30/30 (added `CreationContextBuilder`,
    `CreationContextFactory`, `SpellSpaceThreadState`, `_SpellSpaceLocal`; `_SpellSpaceLocal`
    guarded for consistency with the existing private-class precedent `_Specificity`).
    Docstrings: 7/30 at 3+ canonical headers, up from 3. The four ward enums
    (`Policies`, `Permissions`, `ContractTypes`, `DetailReason`) were enriched ADDITIVELY -
    they already carried strong prose and `comments.md:17-19` forbids stripping it, so the
    canonical sections were appended rather than the narrative rewritten.
  VALIDATION: 4-check set PASSES - py_compile ALL CLEAN, 0 trapped lines, 0 duplicate
    sentinels, and 7 real changed files vs 19 pre-existing whitespace-churned files in the
    subtree (that churn is the owner-pending aether/nexus issue, NOT this pass; verified by
    writing only 3 files in the guard codemod).
    Not run: pytest (needs 3.14t; sandbox is 3.10).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/policies/policies.py:1-70
  - src/melder/aether/conduit/conduit_ward/permissions/permissions.py:1-64
  IMPACT: The user-facing ward vocabulary now explains WHY each value behaves as it does,
    not just what it is - e.g. `Policies.whitelist_all` is documented as the only mode that
    can override a per-spell `Permissions.block`, making it the widest authority in the
    conduit layer.
  NEXT: M4 remainder - `Contract`, `Detail`, `IndexDetail`, `ConduitWard`,
    `TransferOfOwnership` (5 classes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: RAISE
  DATETIME: 2026-07-19T18:10:00Z
  AGENT: melder_0
  CLAIM: MY OWN CRYSTALLIZER RULING IS INCONSISTENT WITH CODEBASE PRECEDENT. I left
    `RecordedUnitState` UNGUARDED under a "value vocabulary" rationale, but conduit shows the
    established convention is the opposite: `Policies` and `Permissions` are guarded AND are
    the most user-facing enums in the package - users pass them by value into `conjure(...)`
    and `bind(...)` constantly. Guarding an enum never blocks passing it as a value; it only
    blocks binding the CLASS as a spell. So "user-facing" was never a reason to leave an enum
    unguarded, and my rationale was wrong.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/policies/policies.py:38-38
  - src/melder/aether/conduit/conduit_ward/permissions/permissions.py:33-33
  IMPACT: Low blast radius (`RecordedUnitState` is internal-only, so nothing is broken), but
    the classification rule in the parent epic should say enums are guarded like any other
    kernel class, and the three unguarded crystallizer entries should be re-adjudicated on
    the injection-seam test rather than on a "value vocabulary" category.
  NEXT: Owner ruling - fold `RecordedUnitState` into the guarded set for consistency, or keep
    the value-vocabulary carve-out and document it as deliberate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- TYPE: DECISION_REQUEST
  DATETIME: 2026-07-19T18:35:00Z
  AGENT: melder_0
  CLAIM: 186 PEP 604 UNION ANNOTATIONS EXIST IN `src/melder`, in direct violation of this
    repo's own overlay policy. `skills/python/banned_patterns.md:61,71` and
    `skills/python/typing.md:24-25` both state "Never use PEP 604 union syntax (A | B,
    T | None); use Optional/Union". Concentration: aether 164, utilities 20,
    crystallizer 1, nexus 1. Found while reading `details.py`, where
    `sources: Set[str] | None = None` sits on line 54 even though `Optional` is ALREADY
    imported on line 8 - so the fix there is a pure one-token swap with no import churn.
    PRE-EXISTING: not introduced by any codemod of mine (I have never written an
    annotation in this repo).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/details.py:54-54
  - src/melder/aether/conduit/conduit.py:167-170
  - src/melder/aether/aether.py:435-435
  IMPACT: Free-threaded 3.14t runs these fine, so this is a policy/consistency defect, not
    a runtime one. But it is exactly the class of thing the overlay exists to prevent, and
    it is in the public library surface.
  WHY NOT SELF-APPLIED: 186 sites across many files is a REPO-WIDE SWEEP, which
    `general/AGENTS.MD:158` lists as an explicit Stop Condition requiring confirmation, and
    `synaptic_policy_overrides.md:12-13` forbids edits or scope expansion without explicit
    user confirmation. Untouched pending ruling.
  NEXT: Owner ruling - (a) authorize an AST codemod sweep under the mandatory 4-check
    validation set, (b) fix only within each OCE child epic's boundary as those land, or
    (c) accept as-is and relax the overlay rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: FACT
  DATETIME: 2026-07-19T18:35:00Z
  AGENT: melder_0
  CLAIM: MOJIBAKE (double-encoded UTF-8) IN 12 DOCSTRING/COMMENT LINES ACROSS 6 FILES.
    Verified PRE-EXISTING: HEAD and worktree carry identical counts per file
    (contract.py 1/1, conduit.py 1/1, meld.py 3/3), and none of these files were written
    by me this session. The worst case is `conduit.py:5637`, where the sequence has been
    re-encoded through several save cycles ("conduit" followed by ~60 characters of
    accumulated escape debris where a single apostrophe belongs); `contract.py:79` is one
    round ("wards<debris> detail maps"). `compiler_phase_5.py:564` shows a c-cedilla in
    "facade" corrupted the same way, and `meld.py:775,785` show right-arrows corrupted in
    live comments.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5637-5637
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:79-79
  - src/melder/aether/conduit/meld/meld.py:775-785
  IMPACT: Docstrings ARE the API for a public library (`policy_skills.md:121-123`), so this
    is user-visible garbage in shipped help text. It also corroborates the encoding-hygiene
    problem already recorded in the parent epic (34 BOM files, 13 mixed CRLF+LF files) -
    same root cause family: files round-tripping through a mis-configured editor encoding.
  NEXT: Repairable deterministically - the corrupted sequences decode back to a small set
    of characters (right single quote, en dash, right arrow, c-cedilla). Bundle with the
    PEP 604 ruling since both are cross-cutting text sweeps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: MEASURE
  DATETIME: 2026-07-19T18:55:00Z
  AGENT: melder_0
  CLAIM: M4 at 7/9. Docstrings 10/30 at 3+ canonical headers (was 3 at epic open).
    `Contract`, `Detail`, and `IndexDetail` enriched additively. The load-bearing fact
    recovered while reading: a `Contract` owns FOUR maps, not two - each ward keeps a
    `Detail` map keyed by spell_id AND an `IndexDetail` map keyed by index_id. `Detail`
    captures a spell_id at grant time (a point-in-time answer); `IndexDetail` subscribes to
    a `SpellIndex` so the borrower follows the lineage HEAD. That split is what lets a notch
    repoint an index's active member WITHOUT renegotiating any contract - the alternative
    would make version movement O(peers) and would race with in-flight resolution.
    Also documented: `Detail.sources` is justification reference-counting, which is what
    makes dependency-linked rollback correct - a lineage pulled in by several roots is
    retired only when the last justifying root departs, so unlinking one root cannot revoke
    a lineage another still needs.
  VALIDATION: 4-check set PASSES - compile ALL CLEAN, 0 trapped lines, 0 duplicate
    sentinels, 9 real changed files vs 17 pre-existing churn files. Comment/docstring
    preservation verified per `comments.md:17-19`: 0 files lost comments or docstrings.
    Not run: pytest (needs 3.14t; sandbox is 3.10).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:20-90
  - src/melder/aether/conduit/conduit_ward/contract/details.py:193-212
  IMPACT: The contract layer now explains WHY it is shaped the way it is, not just what
    the fields hold - the version-snapshot vs lineage-subscription split was previously
    discoverable only by reading both classes side by side.
  NEXT: `ConduitWard` (3702L) and `TransferOfOwnership` (1942L) close M4; both are large
    enough to need chunked reads under `codex.read_loc_max`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: MEASURE
  DATETIME: 2026-07-19T19:40:00Z
  AGENT: melder_0
  CLAIM: Docstrings 19/30 at 3+ canonical headers (from 3 at epic open). Landed this pass:
    `SpellMap`, `SpellContract`, `Meld`, `ConduitMeld`, `SpellSpaceMeld`, `Creations`,
    `ConduitCreations`, `Conduit`, `ConduitState`. All ADDITIVE - these classes already
    carried strong prose and examples, so canonical sections were appended rather than the
    narrative rewritten (`comments.md:17-19`).
    Two contract facts recovered by reading rather than inferring:
    (1) `ConduitMeld` REFUSES `requires_spellspace_request` spells instead of fabricating
    scope, because inventing request-local scope would hand back an instance whose lifetime
    silently disagrees with its declared Existence - a refusal is cheaper than a wrong
    lifetime. (2) `SpellSpaceMeld` deliberately holds BOTH the spellspace store and the
    owner-conduit store: a request-scoped instance must die with the spellspace while a
    `unique_per_conduit` dependency resolved during that request must outlive it. One store
    would collapse that and turn conduit-lived services into per-request garbage.
    Also documented the guarded-base rationale INLINE on `Meld` and `Creations` so a future
    auditor does not "fix" the MRO law by removing a sentinel that is correct.
  VALIDATION: compile ALL CLEAN, 0 trapped lines, 30/30 guards, 0 comment/docstring loss.
    Not run: pytest (needs 3.14t; sandbox is 3.10).
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:42-135
  - src/melder/aether/conduit/creations/creations.py:10-75
  IMPACT: The resolution runtime now explains WHERE each `Existence` mode stores its
    instances and why the two meld doors exist at all - previously only derivable by
    reading both doors plus the store family side by side.
  NEXT: 11 thin remain - `ConduitWard` (3702L) and `TransferOfOwnership` (1942L) are the
    two large ones; the rest are small internals.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: MEASURE
  DATETIME: 2026-07-19T19:40:00Z
  AGENT: melder_0
  CLAIM: MOJIBAKE REPAIR COMPLETE (owner-directed). 12 double-encoded UTF-8 lines across
    6 files repaired; residual scan over all of `src/melder` returns 0. Recovered characters
    were right single quote, em/en dash, set-union, c-cedilla, and rightwards arrow.
    Three lines resisted the automated cp1252->utf8 round-trip and were fixed by hand to
    ASCII (`'` and `->`): `conduit.py:5637` (corrupted through several save cycles - roughly
    60 characters of accumulated escape debris where one apostrophe belonged) and
    `meld.py:775,785`. ASCII was chosen over restoring the original glyphs so the same
    editor-encoding round-trip cannot silently re-corrupt them.
    Root-cause note: the automated pass initially missed those three because the mojibake
    for U+2020 contains U+00A0, and Python's `\s` matches NBSP - so a `[^\s]*` run-matcher
    truncates mid-sequence. Any future text-repair codemod must not use `\s` boundaries.
  VALIDATION: 0 residual mojibake, py_compile ALL CLEAN across `src/melder`,
    0 comment/docstring loss. Not run: pytest.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5637-5637
  - src/melder/aether/conduit/meld/meld.py:775-785
  IMPACT: Shipped help text no longer contains encoding garbage. Docstrings are the API for
    a public library, so this was user-visible.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- TYPE: MEASURE
  DATETIME: 2026-07-19T20:55:00Z
  AGENT: melder_0
  CLAIM: oce-aether-conduit DOCSTRING WORK COMPLETE. 30/30 classes at 3+ canonical headers
    (3 at epic open); average class docstring 57 lines; guards 30/30. Final tranche:
    `ConduitWard`, `TransferOfOwnership`, `ConduitCluster`, `CreationContext`,
    `CreationContextBuilder`, `CreationContextFactory`, `SpellOverrider`, `_Specificity`,
    `SpellSpacePool`, `SpellSpaceThreadState`, `_SpellSpaceLocal`.
    Highest-value contract facts recovered by reading implementation:
    - `ConduitWard` uses SORTED LOCK ORDERING between wards on contract creation; without
      it two conduits linking each other simultaneously deadlock. Its two-phase sever
      (detach -> destroy, with reattach as undo) exists so a mid-sever failure cannot leave
      one ward believing a contract is gone while its peer still holds it - asymmetric
      contract state is the worst failure available to that class.
    - `TransferOfOwnership` deliberately leaves impacted state DIRTY rather than repairing
      the graph, because it cannot know which consumers are mid-resolution; meld-time lazy
      revalidation rebuilds under the per-spell lock.
    - `CreationContext` executor slots are SELF-REPLACING (cold door hot-swapped in place
      on first execution), which is precisely why `Meld`'s fast-door registry stores the
      CONTEXT and re-reads the executor per hit instead of caching the executor.
    - `CreationContextFactory` is lock-free ON PURPOSE: context construction is idempotent,
      the spell's slot is the single point of truth, and locking would serialize every
      distinct spell's cold path across all cores under 3.14t.
    - `_SpellSpaceLocal` initializes eagerly so the owner can use direct attribute access,
      because `banned_patterns.md:8-18` forbids defensive getattr on owned attributes.
  VALIDATION: full 5-check set PASSES - compile ALL CLEAN, 0 trapped lines, 0 unbound
    `_mrg`, 0 duplicate sentinels, 0 comment/docstring loss.
    Not run: pytest (needs 3.14t; sandbox is 3.10). OWNER RERUN REQUIRED before closure,
    especially the gauntlet that caught the `_mrg` regression.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:55-138
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-120
  IMPACT: The resolution runtime is now self-explaining end to end - a reader can follow
    conjure -> conduit -> meld door -> creation context -> creations store and find the
    reasoning, not just the mechanics, at each hop.
  NEXT: Owner 3.14t run. Then oce-aether-aetheric-frame (60) or oce-nexus-rift (53).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Child epic of the OCE program covering `src/melder/aether/conduit/**` (30 classes).
Survey and MRO adjudication are complete and recorded above. Remaining work is guarding four
internal kernel classes and raising 27 thin docstrings to Rank 4+ in three tranches.
The conduit MRO cases are RESOLVED (redundant, not defective); the crystallizer
`PersistenceAnalysisStrategy` case remains open and belongs to the parent epic.
