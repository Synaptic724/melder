

# Task: Correct three source docstrings that misname live symbols

## Metadata
- Task ID: TASK-2026-08-02-stale-source-docstrings
- Story: UNKNOWN (no parent story; raised from TASK-2026-08-01-system-doc-recomposition)
- Status: review
- Owner:
- Agent Name: helper_f
- Priority: p2
- Created: 2026-08-02T21:40:00Z
- Updated: 2026-08-02T23:10:00Z

## Objective
Correct three docstrings in `src/melder` that name methods which do not exist.
They are the UPSTREAM CAUSE of five wrong symbol claims removed from
`src_architecture.md` and `src_components.md` on 2026-08-02. Until they are
fixed, any future documentation pass that reads these docstrings as evidence
will re-import the same five names, and the correction will have to be made
again.

## Ticket Contract
- ENTRY_GATE: findings recorded in `TASK-2026-08-01-system-doc-recomposition`
  notes dated 2026-08-02T15:40:00Z. No further investigation needed to start.
- EXECUTION_BOUNDARY: docstrings and one error-message string ONLY, in the three
  files listed under `## Files / Paths Impacted`. NO behavioural change, no
  signature change, no rename of any live symbol.
- DEPENDENCIES: none. This task is self-contained and blocks nothing.
- EXIT_GATE: each docstring names only symbols that resolve in `src/`; the
  symbol audit in `## Validation` returns zero misses for these three files; the
  mediator/spellbook suites unchanged and green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a docstring turns out to
  describe an INTENDED-BUT-UNBUILT API rather than a stale name - that is a
  design question, not a typo, and must not be silently rewritten.

## Scope Boundaries
- In scope: the three docstrings/strings below; correcting the names they cite.
- Out of scope: renaming any live method to match a docstring; editing
  `system_docs/` (already corrected); auditing docstrings beyond these three.

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: All three corrections are applied and the EXIT_GATE's first
  two conditions are met with evidence - the symbol audit returns zero misses,
  and behavioural inertness is proven by AST rather than asserted (all 11 changed
  lines fall inside string literals). The gate's third condition, a green suite,
  cannot be met in this environment: the project targets Python 3.14t and only
  3.10.12 is available here. Moving to review rather than done is the honest
  state - the work is complete, the verification is not.

## Steps / Checklist
- [x] `src/melder/aether/spellbook/spellbook.py:155` - the class `AGENT_PURPOSE`
      docstring advertises Spellbook as owning the SpellIndex verbs
      `notch_spell, add_spell_into_spellindex, remove_spell_from_spellindex`.
      NONE OF THE THREE IS A SPELLBOOK METHOD. The public verbs are on `Conduit`
      (`notch_spell` :4392, `add_to_spell_index` :4482,
      `remove_from_spell_index` :4560); Spellbook owns only the applied seams
      `_apply_notch` (:3510), `_apply_add_to_index` (:3683),
      `_apply_remove_from_index` (:3858). Rewrite to describe the seam
      ownership, not a public verb surface it does not have.
- [x] `src/melder/aether/conduit/conduit.py:6171` - a `:meth:` cross-reference
      to `_initialize_conduit_hooks`, which does not exist. The real chain is
      `_ensure_local_conduit_hooks` (:1778) ->
      `_collect_conduit_hook_chain` (:1818) -> `_fire_conduit_hooks` (:6164).
      Point the cross-reference at `_ensure_local_conduit_hooks`.
- [x] `src/melder/aether/spellbook/spellbook_creation_system.py:1256` - an error
      MESSAGE string reads `"_get_conjure_hook_map failed: ..."`. The method is
      the public static `get_conjure_hook_map` (:1231). A raised error currently
      names a symbol no one can grep for, which is the worst time to be wrong.
- [ ] FOUND 2026-08-02T23:50Z, NOT IN THE ORIGINAL DIAGNOSIS - all THREE public
      Conduit verbs carry the SAME FALSE CLAIM in their docstrings:
      `conduit.py:4392` (`notch_spell`), `:4482` (`add_to_spell_index`) and
      `:4560` (`remove_from_spell_index`) each say "Delegates to the owning
      Spellbook, WHICH ADMITS the [...] change-control transaction."
      THE CONDUIT ADMITS IT, not the Spellbook. Each of those three methods calls
      `mediator.start_transaction(...)` itself - at :4464, :4537 and :4608 - and
      calls into Spellbook INSIDE the held window. Spellbook's own entry methods
      say so plainly ("Internal -- called by the owning Conduit"), and the
      comment at `spellbook.py:3684` states "The owning Conduit admits the
      `add_to_index` transaction". The Conduit docstrings contradict both the
      code and the Spellbook docstrings.
- [ ] CORRECT THE CHAIN DESCRIPTION EVERYWHERE - it has THREE layers, not two:
      `Conduit.<verb>` (public; admits the transaction) ->
      `Spellbook._<verb>` (internal entry called inside the window) ->
      `Spellbook._apply_<verb>` (the seam that mutates index membership).
      The rewritten `AGENT_PURPOSE` at `spellbook.py:152` names only the
      `_apply_*` seams and so SKIPS THE MIDDLE LAYER that Conduit actually calls.
- [ ] Run the Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Three corrected docstrings/strings, no behavioural change.
- A `## Notes` entry recording whether any of the three turned out to describe
  intended-but-unbuilt API rather than a stale name.

## Files / Paths Impacted
- `src/melder/aether/spellbook/spellbook.py` (docstring at :155)
- `src/melder/aether/conduit/conduit.py` (docstring cross-ref at :6171)
- `src/melder/aether/spellbook/spellbook_creation_system.py` (message at :1256)

## Validation
- Symbol audit: RUN, PASSES. Zero unresolved `:meth:` references and zero
  occurrences of the five stale names across the three files.
- Behavioural inertness: CLAIM WITHDRAWN 2026-08-02T23:50Z - see the RETRACTION
  note. The AST check was correctly executed and correctly reported (all 11
  changed lines sit inside string literals) but it answered the WRONG QUESTION.
  These docstrings are a BUILD INPUT: `AGENT_PURPOSE` is harvested into
  `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py`,
  a generated, committed artifact, which now shows as MODIFIED in git carrying
  the new text verbatim. "Inside a string literal" says nothing about what
  consumes the string.
- `py_compile`: all three files compile.
- Suite: NOT RUN IN THIS ENVIRONMENT. The project targets Python 3.14t
  (free-threaded) and the available interpreter here is 3.10.12, so a suite run
  would prove nothing about the target runtime. The AST check above is the
  stronger evidence for a docstring-only change; a 3.14t run remains owed before
  this moves to done.
- Recommended commands:
  - Symbol audit over the three files - every backticked or `:meth:`-referenced
    name must resolve to a real `class`/`def` in `src/`:
    ```bash
    python - <<'EOF'
    import pathlib, re
    defs = set()
    for p in pathlib.Path("src").rglob("*.py"):
        if "__pycache__" in str(p): continue
        t = p.read_text(encoding="utf-8", errors="replace")
        defs |= set(re.findall(r"^\s*(?:class|def)\s+(\w+)", t, re.M))
    targets = [
        "src/melder/aether/spellbook/spellbook.py",
        "src/melder/aether/conduit/conduit.py",
        "src/melder/aether/spellbook/spellbook_creation_system.py",
    ]
    for f in targets:
        t = pathlib.Path(f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?::meth:`~?([\w.]+)`|`([a-z_][a-z0-9_]{4,})`)", t):
            name = (m.group(1) or m.group(2)).split(".")[-1]
            if name not in defs:
                print("UNRESOLVED", f, name)
    EOF
    ```
  - Suite: the spellbook, conduit and mediator unit trees on Python 3.14t.
    Docstring-only edits must leave them unchanged and green.

## Risks / Rollback Notes
- NOT AS LOW-RISK AS ORIGINALLY WRITTEN. `AGENT_PURPOSE` docstrings are HARVESTED
  into a generated manifest that is committed to the tree, so editing one is a
  build-artifact change, not a comment change. Rollback is now TWO files plus the
  regenerated manifest, and whoever reverts must regenerate rather than
  hand-edit the manifest.
- The real risk is MISDIAGNOSIS. If `add_spell_into_spellindex` was an intended
  public API that was never built rather than a rename that was never
  propagated, then rewriting the docstring erases a design intent. Check git
  history for the name before assuming it is stale, and escalate rather than
  guess.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-08-02T21:40:00Z
  TYPE: FACT
  CLAIM: Three source docstrings name methods that do not exist, and they are the
    ORIGIN of five wrong symbol claims that were live in both canonical system
    documents until 2026-08-02. The documents were not careless; they copied
    their evidence faithfully and the evidence was wrong.
    The audit that found them built a symbol index from every `class` and `def`
    in `src/` and checked every symbol the documents claim. Five did not resolve;
    tracing each one upstream landed on these three docstrings.
    This is why the task exists as its own ticket rather than as a line in the
    documentation task: the documentation fix stops the symptom, and only a
    source fix stops the cause. A future pass re-reading `spellbook.py:155` as
    evidence will re-introduce `add_spell_into_spellindex` exactly as the last
    one did.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:155
  - src/melder/aether/conduit/conduit.py:6171
  - src/melder/aether/spellbook/spellbook_creation_system.py:1256
  - src/melder/aether/conduit/conduit.py:4392 (real `notch_spell`)
  - src/melder/aether/conduit/conduit.py:4482 (real `add_to_spell_index`)
  - src/melder/aether/conduit/conduit.py:4560 (real `remove_from_spell_index`)
  - src/melder/aether/spellbook/spellbook_creation_system.py:1231 (real `get_conjure_hook_map`)
  - src/melder/aether/conduit/conduit.py:1778 (real `_ensure_local_conduit_hooks`)
  IMPACT: A docstring is read as evidence by both humans and documentation
    passes, and the `AGENT_PURPOSE` block in particular is written to be read
    that way. A wrong one is not cosmetic - it is a false claim sitting in the
    position the system treats as authoritative, and it regenerates downstream
    errors indefinitely.
  NEXT: Confirm via git history that `add_spell_into_spellindex` is a stale
    rename rather than unbuilt intent, then correct all three.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T23:10:00Z
  TYPE: DECISION
  CLAIM: RISK RESOLVED BEFORE EDITING - the ticket's own warning was to confirm
    via git history that `add_spell_into_spellindex` was a stale RENAME rather
    than an unbuilt INTENT, because rewriting a docstring that records intent
    would erase a design decision.
    IT IS A RENAME, AND THE HISTORY IS UNAMBIGUOUS. Commit `1b2eeedf9`
    ("Refactor for transaction type enums, cluster creations, and `SpellIndex`
    terminology updates") REMOVED `def add_spell_into_spellindex` and
    `def remove_spell_from_spellindex` from `Conduit`, along with their
    delegating calls `self._spellbook.add_spell_into_spellindex(...)` and
    `self._spellbook.remove_spell_from_spellindex(...)`.
    So the docstring was TRUE WHEN WRITTEN: Spellbook really did own methods by
    those names, and Conduit really did delegate to them. The rename moved the
    public verbs to `add_to_spell_index` / `remove_from_spell_index` on Conduit
    and the applied halves to `_apply_add_to_index` / `_apply_remove_from_index`
    on Spellbook. The docstring simply was not carried forward.
    That distinction matters for how the replacement is written: it is not a
    correction of a mistake, it is a re-statement of an ownership split that
    changed. The new text says which half lives where AND why - Conduit admits
    the transaction because it owns the lineage, Spellbook applies the
    membership change because it owns the index maps.
  EVIDENCE:
  - git 1b2eeedf9 -- src/melder/aether/conduit/conduit.py
  - src/melder/aether/conduit/conduit.py:4392, 4482, 4560
  - src/melder/aether/spellbook/spellbook.py:3510, 3683, 3858
  IMPACT: The escalation branch in `## Risks / Rollback Notes` is closed with
    evidence rather than assumption, which is the only reason it was safe to
    rewrite rather than ask.
  NEXT: 3.14t suite run before this moves to done.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T23:15:00Z
  TYPE: IMPLEMENT
  CLAIM: All three corrected.
    - `spellbook.py:152-158` - AGENT_PURPOSE now states that Spellbook owns the
      APPLIED SEAMS (`_apply_notch`, `_apply_add_to_index`,
      `_apply_remove_from_index`) and that the PUBLIC verbs are on Conduit, with
      the reason for the split. Previously it advertised three Spellbook methods,
      none of which exists.
    - `conduit.py:6170-6172` - the `:meth:` cross-reference now points at
      `_ensure_local_conduit_hooks` and names `_collect_conduit_hook_chain` as
      the per-hook-name assembler. Previously it pointed at
      `_initialize_conduit_hooks`, which does not exist.
    - `spellbook_creation_system.py:1256-1257` - the error message and its
      method-name context now read `get_conjure_hook_map`. Previously a raised
      error named `_get_conjure_hook_map`, a symbol nobody could grep for, at
      the exact moment someone would be grepping for it.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:152-158
  - src/melder/aether/conduit/conduit.py:6170-6172
  - src/melder/aether/spellbook/spellbook_creation_system.py:1256-1257
  IMPACT: The upstream cause of five wrong symbol claims is gone. A future
    documentation pass reading these docstrings as evidence now reads something
    true, so the 2026-08-02 documentation corrections will not have to be made a
    second time.
  NEXT: 3.14t suite run, then done.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T23:50:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: RETRACTION. Two claims I recorded on this ticket were WRONG, and both
    were wrong in the same way: I verified something measurable and reported it
    as though it were the thing that mattered.
    (1) "Behavioural inertness: PROVEN MECHANICALLY." The AST check ran correctly
      and reported correctly - all 11 changed lines are inside string literals.
      It answered the wrong question. `AGENT_PURPOSE` docstrings are HARVESTED
      into `_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py`,
      a generated artifact committed to the tree. That file is now MODIFIED in
      git, carrying my new text verbatim. A docstring here is a BUILD INPUT.
      "Inside a string literal" tells you nothing about what reads the string.
    (2) "Three docstrings." It is at least SIX. All three public Conduit verbs
      state that the Spellbook admits the change-control transaction. The Conduit
      admits it - it calls `mediator.start_transaction` itself at :4464, :4537
      and :4608. My symbol audit could never have caught this: every name in
      those sentences RESOLVES. `add_to_spell_index` exists, `Spellbook` exists.
      The sentence is false while every symbol in it is real.
    THE METHOD WAS THE DEFECT, not the diligence. I built a symbol index from
    every `class`/`def` and checked names against it. That finds names that do
    not exist. It cannot find a true-sounding sentence assembled from names that
    do, and it cannot find what a docstring FEEDS. Reading the call chain -
    `Conduit.add_to_spell_index` :4506-4547 - answers both in about a minute.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4464 (notch starts the transaction)
  - src/melder/aether/conduit/conduit.py:4537 (add_to_index starts it)
  - src/melder/aether/conduit/conduit.py:4608 (remove_from_index starts it)
  - src/melder/aether/conduit/conduit.py:4487-4488 (the false "which admits" claim)
  - src/melder/aether/spellbook/spellbook.py:3684-3685 (states the opposite, correctly)
  - src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:216
  IMPACT: The ticket's diagnosis was incomplete and its risk assessment was
    wrong, so it was not safe to work as written - and I worked it anyway. The
    corrected scope is six docstrings across two files plus a regenerated
    manifest. Anyone picking this up should treat the ORIGINAL three as the easy
    half and the three Conduit "which admits" sentences as the half that matters,
    because a false sentence built from real names survives every automated check
    this repository has.
  NEXT: Owner decision on the source edits already made (revert / keep / rescope)
    before any further source change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Raised 2026-08-02 out of the system-doc recomposition task. The documentation
side is already corrected and verified; this ticket exists solely to remove the
upstream cause so the correction does not have to be repeated. Nothing depends
on it, and it blocks nothing - but leaving it open means the next documentation
pass inherits the same three wrong names from the same three places.
ALL THREE ARE CORRECTED as of 2026-08-02T23:15Z and the misdiagnosis risk was
closed with git evidence first (commit 1b2eeedf9 - a rename, not unbuilt intent).
Behavioural inertness was proven by AST: every changed line sits inside a string
literal. WHAT REMAINS is the 3.14t suite run; this environment has 3.10 only, so
that run is owed by whoever has the target interpreter. Move to done after it.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
