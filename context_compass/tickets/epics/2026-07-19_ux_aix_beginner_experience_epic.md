# Epic: UX/AIX Beginner experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-beginner
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

## Objective
First-contact UX + the agent first-read: bind/conjure/meld, lifecycles, function and instance spells, named bindings, scan_bind, scopes, the error vocabulary, and the hardcopy self-documentation. Prove the root serves the first hour with zero deep-path imports.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/01_beginner/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/01_beginner/ examples + findings notes ONLY; init changes route to the init composition story.
- DEPENDENCIES: init composition story (the 66-name root is the surface under test);
  prior tiers' findings.
- EXIT_GATE: every example runs green on the owner's 3.14t; every discovered
  init-surface gap either landed on the init story or recorded as a rejected
  curation call with reasons; owner walkthrough of the tier.
- FAILURE_ESCALATION: DECISION_REQUEST on any gap whose fix would widen the public
  surface beyond the ConduitWard law.

## Noting Behavior
- MEASURE per authoring wave (examples written, surfaces exercised, gaps found).
- DECISION for every init-surface change the tier proposes.

## Notes
- DATETIME: 2026-07-19T13:14:00Z
  TYPE: MEASURE
  CLAIM: Owner tier-law correction applied + registration wave landed. (1) TIER LAW:
    beginner = STATIC conjure only, no dynamic, no Nexus, no MutationResearch - all 7
    offending conjure(dynamic=True, name=...) calls rewritten to book.conjure();
    tier is grep-verified dynamic-free. (2) claude.md renamed AGENTS.md per owner.
    (3) Registration wave: +7 examples (09-15), SpellBinder fluent API source-verified
    first (spellbinder.py:246-692: bind/with_existence/as_unique/as_many/
    as_unique_per_conduit(+cluster/lineage/spell_space)/with_permissions/
    under_spellframe/named/with_kwargs/with_pre_hook(s)/with_activation_hook(s)/
    with_post_hook(s)/finalize->str, ctor defaults existence=unique permissions=create).
    09 fluent basics + binder reuse, 10 the full chain incl. with_kwargs ctor
    injection + per-conduit frame policy, 11 hook trio (printed order = the runtime
    documentation), 12 strings-as-vocabulary (existence/permissions accept names),
    13 disposal_method_names teardown contract (staged prints: conduit vs book
    cleanup), 14 spellframe grouping ((frame, name) is the full address), 15 context-
    managed Spellbook with post-exit guard honesty. 15 examples total; compile green
    x15; md-only imports; 120-col clean. INIT FINDINGS: still zero gaps - the full
    registration vocabulary reaches beginner UX from md.* alone.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/10_spellbinder_full_chain.py:1-60
  - UX_and_AIX_experiences/01_beginner/13_disposal_contract.py:1-45
  - src/melder/aether/spellbook/spellbinder.py:246-692
  IMPACT: Registration UX ("how to register shit") is now covered end to end at the
    beginner tier: direct bind, fluent binder, decorator scan, strings, kwargs,
    hooks, disposal, frames, context management.
  NEXT: Owner 3.14t pass over the 15 scripts; three examples deliberately PRINT
    contracts the run will document (07 unregistered-meld, 11 hook firing points,
    13 disposal stage). Then tier 02.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T12:52:00Z
  TYPE: MEASURE
  CLAIM: Tier authored - 8 examples, every verb source-verified before writing
    (conjure(policy/dynamic/name) spellbook.py:5658, meld(spell/spell_name/
    binding_name/spellframe/spell_override) conduit.py:3594, scan(module)->list[str]
    :4877, Existence members existence.py:24-72, Permissions read/create/block
    :34-36). Coverage: 01 hello-meld, 02 unique-vs-many, 03 function+instance spells,
    04 binding_name disambiguation, 05 @scan_bind + module scan, 06 lesser-conduit
    scopes (unique_per_conduit), 07 catchable error family from root, 08 the AIX
    first-read (workflow-map docstring, version, four hardcopy docs, __all__).
    INIT-SURFACE FINDINGS: ZERO gaps at this tier - every beginner workflow completes
    from md.* alone; the 66-name root fully serves first-contact UX and the agent
    first-read. One honest unknown for the 3.14t run: whether melding an unregistered
    spell raises SpellbookValidationError vs returns None (07 handles both and PRINTS
    which - the run itself documents the contract).
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/01_hello_meld.py:1-40
  - UX_and_AIX_experiences/01_beginner/08_agent_first_read.py:1-40
  - src/melder/aether/spellbook/spellbook.py:5658-5664
  - src/melder/aether/conduit/conduit.py:3594-3602
  IMPACT: Beginner tier is authored evidence that the loaded init works at first
    contact; the tier's zero-gap result is itself a finding for the init story.
  NEXT: Owner: python UX_and_AIX_experiences/01_beginner/0N_*.py on 3.14t (or one
    loop); then iterate tier 02 (intermediate).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8


## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
