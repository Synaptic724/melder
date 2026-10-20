# Task: Restore scan_bind option parity and specify discovery edge cases

## Metadata
- Task ID: TASK-2026-10-08-restore_scan_bind_option_parity
- Story: none (standalone task; owner-requested investigation and ticket)
- Status: done
- Owner: claude (assigned by the owner 2026-10-10; implementation authorized)
- Agent Name: melder_1 (implementation from 2026-10-10), dot (investigation and ticket preparation)
- Priority: p2
- Created: 2026-10-08T16:52:00Z
- Updated: 2026-10-10T13:44:41Z

- Completed: 2026-10-10T13:44:41Z
- Summary: Landed 2026-10-10 (melder_1), notched 0.2.8228: scan_bind takes bind()'s target options (resolvable,
  per-target disposal_method_names, keyword metadata) and replays them through Spellbook.bind; only an object's
  own declaration makes it a target, bound once per scan (Breaking for undecorated subclasses and instances of a
  decorated class). Release note section: "`scan_bind` takes every option `bind` takes, and registers only what a
  module declares". 64 new tests red/green with the GIL off; the whole tests/ tree green on the hand-back tree;
  patch docs promoted and archived. Accepted by the owner; Windows tiers, hosted CI and the commits are the owner's.

## Objective
Bring the deferred scan declaration surface into deliberate alignment with normal Spellbook.bind,
without duplicating the binding pipeline or silently changing module-discovery policy.
This is an investigated implementation proposal. Creating this ticket does not authorize implementation.
The owner authorized implementation on 2026-10-10 (State Transition Event; Note 5).

## Problem / Opportunity
scan_bind ultimately calls Spellbook.bind, so shared arguments receive the current binding behavior.
However, its public signature and frozen metadata cannot express three supported direct-bind inputs:
resolvable, disposal_method_names, and arbitrary application metadata kwargs. This is a present API
coverage gap. Bounded history confirms resolvable was added to direct bind without a matching scan
option; the other gaps and discovery behaviors predate the recent changes (see History below).

Two additional discovery behaviors deserve explicit decisions: undecorated subclasses inherit scan
metadata, and multiple module names referring to one decorated object cause duplicate registration.

## Context / Source Baseline
- Repository: https://github.com/Synaptic724/melder
- Branch: codex_features2 (the verified branch matching the owner's "codex feature2")
- Source commit: 66939dfe84e41e51f41f4bc4461ad1690907e909
- Source version installed for checks: 0.2.8227
- Fresh checkout: /workspace/shared/melder-scan-bind-20261008
- Baseline remote HEAD was rechecked after the first investigation and matched this commit.
- The scan lane captures declaration metadata at decoration time and replays it into the owning
  Spellbook later. Shared registration must remain owned by Spellbook.bind and Bind._bind_logic.

### History (bounded source verification)
- A read-only fetch deepened the clone by 80 commits; it remains a shallow repository.
- Spellbook.bind gained resolvable in commit
  63ef620e36071027e9d022937406aefbc3ccb41b (2026-09-19). The patch adds the signature
  parameter, documents it, and forwards it to core binding.
- scan.py at the oldest fetched boundary,
  574cfa2a8480c2c6a2292c87b767c2943b8cb23d (2026-08-02), is byte-identical to reviewed HEAD.
  SHA-256 for both copies: 11b883cfa26bd12d33caa158a5fa89968c4ebe4ce8e47e690ae488f5b1839638.
- This verifies the resolvable adapter omission across the September addition. The missing disposal/
  metadata surface and inherited/alias discovery already existed in the August snapshot.
- The history boundary is not an introduction commit. No older origin date is claimed.
- Commit evidence:
  https://github.com/Synaptic724/melder/commit/63ef620e36071027e9d022937406aefbc3ccb41b
- Earlier scanner snapshot:
  https://github.com/Synaptic724/melder/blob/574cfa2a8480c2c6a2292c87b767c2943b8cb23d/src/melder/aether/spellbook/bind/scan.py

### MRP alignment
Supports the existing explicit declaration, single binding pipeline, lifecycle ownership, and
inspectable registration model. No new roadmap milestone or MRP identifier is claimed or required.

## Ticket Contract
- ENTRY_GATE: Owner approves implementation scope and discovery decisions below; assign an implementer,
  move this draft to ready/in_progress, and add an attention_board active row before implementation.
  Latest notes and the pinned baseline must be read. The owner explicitly waived onboarding for this
  investigation/ticket-preparation request; no broader policy change is implied.
- EXECUTION_BOUNDARY: Proposed implementation is limited to bind/scan.py, focused scan and binding parity
  tests, and directly corresponding public documentation. Any change to core binding, transaction
  semantics, discovery recursion, or repository publication needs a separate explicit decision.
- DEPENDENCIES: Current normal Spellbook.bind behavior at the pinned SHA; no parent story or new runtime
  dependency. Preserve Book-owned registration hooks and configured disposal policy.
- EXIT_GATE: Acceptance tests below pass on supported free-threaded Python; intentional differences are
  documented; affected aggregate checks pass or have explicit limitations; owner accepts the result.
- FAILURE_ESCALATION: Record DECISION_REQUEST for inheritance, alias, default, or metadata ownership
  ambiguity. Record CONFLICT if existing tests require incompatible behavior. Do not resolve a policy
  conflict by silently broadening registration, copying arbitrary objects, or changing transactions.

## Scope Boundaries
- In scope for this request: source investigation, safe reproductions, evidence, and this ticket.
- Proposed later scope: add supported declaration options and forwarding; pin parity with tests;
  settle the two discovery decisions; document retained differences.
- Out of scope: implementation now, code commits, pushes, PRs, GitHub issue publication, changing
  binding identity rules, replacing protocol validation, recursive scanning, or whole-system redesign.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-10T13:44:41Z) the owner accepted the work and asked for the tickets to be turned in
  (Note 20); the final verification holds on the hand-back tree (Note 21), the evidence pack is written, the patch
  folder is archived and the boards are synced. No commit or push (owner).
- previous: in_progress -> review (2026-10-10T09:50:28Z) implemented and validated inside the approved scope
  (Notes 9-18): scan.py,
  tests red then green with the GIL off, the Spellbook.scan docstring and the README example, the system
  documents and their indexes, the graph, notch 0.2.8228 and the running release note. The asset and
  llm_support rebuild follows as the last step. The owner's acceptance, the Windows tiers and the hosted
  runs remain.
- previous: draft -> in_progress (2026-10-10T08:35:00Z) the owner added this ticket to the board, assigned it to
  melder_1 and directed: "go ahead and investigate the findings and fix them" (chat, 2026-10-10). That
  approves the proposed option scope and the proposed F5/F6 discovery policies (Note 5).
- previous: draft -> draft (2026-10-08) new investigated backlog proposal. No implementation
  authorization or acceptance has been given. The existing successful baseline tests do not make the
  proposed fix done.

## Findings and Requirements

### F1: Missing resolvable option (confirmed API gap)
Normal bind accepts resolvable=True and supports False. scan_bind rejects the keyword at the call
boundary. Consequently a Protocol target cannot be declared as a non-resolvable definition through
scan_bind, though it can through direct bind. A Protocol used as spellframe still receives current
contract validation through the shared bind pipeline.
- Proposed requirement: expose resolvable=True, store it, and forward it without truthiness coercion.
- Preserve strict bool checking in normal binding; do not invent decorator-specific protocol rules.
- Evidence: src/melder/aether/spellbook/bind/scan.py:108-155
- Evidence: src/melder/aether/spellbook/spellbook.py:5176-5187
- Evidence: src/melder/aether/spellbook/bind/bind.py:663-683

### F2: Missing per-binding disposal names (confirmed API gap)
scan_bind rejects disposal_method_names. Book-wide configured names still apply at scan time because
Spellbook.bind supplies them. Per-target disposal candidates cannot be captured by the decorator.
- Proposed requirement: expose disposal_method_names=None and capture caller-supplied sequence values
  defensively, preserving order. Replay through normal bind so Book overlap/priority rules stay central.
- Preserve the distinction between omitted/empty per-target names and disabling Book-wide disposal;
  an empty per-target group must not disable Book configuration.
- Evidence: src/melder/aether/spellbook/spellbook.py:5317-5324
- Evidence: src/melder/aether/spellbook/bind/bind.py:704-747

### F3: Missing application metadata kwargs (confirmed API gap)
Normal bind passes non-hook kwargs into Spell construction; scan_bind has no **kwargs channel.
scan_bind(..., custom_tag="audit") raises TypeError before metadata can be attached.
- Proposed requirement: capture and forward application metadata while preserving reserved native
  arguments and the three hook keys. Define shallow snapshot/reference semantics explicitly.
- Do not deep-copy arbitrary application objects or claim that frozen outer metadata freezes nested
  values. Preserve metadata identity where normal bind does, unless the owner specifies otherwise.
- Evidence: src/melder/aether/spellbook/spellbook.py:5325-5330
- Evidence: src/melder/aether/spellbook/bind/scan.py:117-155

### F4: Intentional differences to retain unless explicitly changed
- existence is required on both surfaces; permissions is required by scan_bind but defaults to create
  on normal bind. The scan requirement is documented and covered by existing tests.
- scan_bind returns the original decorated object and does not register at import time.
- Only an explicitly supplied module is scanned; no recursive package traversal or imports occur.
- Re-exports are rejected by the object's __module__ check.
- Scan hook inputs accept None/list/tuple, validate callables early, and snapshot lists as tuples;
  normal bind receives hook kwargs at bind time. This is deliberate decorator-time validation.
- Each found target uses the same bind normalization, existence constraints, Protocol-spellframe
  checks, guarded-target checks, collision handling, registration hooks, and runtime registration.
- Scanning is a multi-target operation. Before conjure it does not open its own outer transaction;
  post-conjure it participates in or opens a bind transaction. Do not promise universal scan atomicity.
- Evidence: src/melder/aether/spellbook/bind/scan.py:18-51
- Evidence: src/melder/aether/spellbook/bind/scan.py:145-232
- Evidence: src/melder/aether/spellbook/bind/scan.py:335-370
- Evidence: src/melder/aether/spellbook/spellbook.py:3621-3644
- Evidence: src/melder/aether/spellbook/spellbook.py:5473-5546

### F5: Inherited metadata (confirmed behavior; policy decision pending)
The scanner uses getattr(obj, "__melder_scan_bind__", None). An undecorated Child inheriting from a
same-module decorated Parent is therefore registered, even though Child.__dict__ has no scan metadata.
- Proposed policy: only explicit own-object metadata makes a target eligible. Confirm with owner.
- An explicitly decorated subclass should remain eligible using its own declaration.
- Do not label this a newly introduced regression: introduction history has not been established.
- Evidence: src/melder/aether/spellbook/bind/scan.py:342-345

### F6: Same-object aliases (confirmed behavior; policy decision pending)
The scanner visits every module dictionary entry without deduplicating object identity. A decorated
Thing and Alias = Thing cause a second bind attempt and a collision. Before conjure, the first binding
remains registered after the exception (observed count: 1).
- Proposed policy: bind each eligible object once per scan, by identity, preserving first occurrence.
- Retain errors for genuinely distinct targets with colliding binding keys and for later rescans.
- Do not silently make this task a transaction-rollback redesign. Pin and document failure boundaries.
- Evidence: src/melder/aether/spellbook/bind/scan.py:339-368
- Evidence: src/melder/aether/spellbook/spellbook.py:5333-5348

## Reproductions
Run in a disposable checkout with Melder installed, Python 3.14+ free-threaded, and repository root
available on PYTHONPATH. The helper below is an existing test fixture helper, not a proposed public API.

```python
import types
import melder as md
from typing import Protocol
from tests.unit.melder.spellbook.test_scan_bind import _make_spellbook

for option, value in (("resolvable", False), ("disposal_method_names", ["close"]),
                      ("custom_tag", "audit")):
    try:
        md.scan_bind(existence="unique", permissions="create", **{option: value})
    except TypeError as error:
        print(option, error)  # Each is an unexpected keyword argument.

class Contract(Protocol):
    def act(self): ...
book = _make_spellbook()
try:
    sid = book.bind(spell=Contract, existence="unique", resolvable=False)
    assert book.find_spell_by_id(sid).resolvable is False
finally:
    book.cleanup()

module = types.ModuleType("probe_inherited")
exec("from melder import scan_bind\n"
     "@scan_bind(existence='unique', permissions='create')\n"
     "class Parent: pass\nclass Child(Parent): pass", module.__dict__)
book = _make_spellbook()
try:
    assert "__melder_scan_bind__" not in module.Child.__dict__
    ids = book.scan(module)
    assert [book.find_spell_by_id(sid).spell.__name__ for sid in ids] == ["Parent", "Child"]
finally:
    book.cleanup()

module = types.ModuleType("probe_alias")
exec("from melder import scan_bind\n"
     "@scan_bind(existence='unique', permissions='create')\n"
     "class Thing: pass\nAlias = Thing", module.__dict__)
book = _make_spellbook()
try:
    try:
        book.scan(module)
    except RuntimeError as error:
        assert "Spell ID collision" in str(error)
        assert len(book.spells) == 1
    else:
        raise AssertionError("Expected alias duplicate binding failure at baseline")
finally:
    book.cleanup()
```

## Steps / Checklist
- [x] Clone and verify exact branch and SHA; inspect both binding paths and relevant tests.
- [x] Run focused baseline tests and reproduce missing options and discovery edge cases.
- [x] Separate API gaps from intentional behavior and unproven historical-regression claims.
- [x] Owner approves option scope and explicitly settles inheritance/alias policy (2026-10-10; Note 5).
- [x] Assign implementer and activate board routing before implementation (melder_1, 2026-10-10).
- [x] Add failing regression/parity tests for the approved behavior (54 of 63 red on the old code; Note 11).
- [x] Implement only metadata capture/forwarding and approved discovery changes (scan.py only; Note 12).
- [x] Validate focused tests, affected broader checks, and public documentation (Notes 13-18).
- [x] Run Ticket Microcycle during approved execution:
      Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document.
- [x] Append meaningful findings in Notes before the next investigation tranche.

## Acceptance Criteria
Checked by melder_1 against the tests named in Notes 11-18; the owner confirms at turn-in.
- [x] scan_bind accepts and forwards resolvable, disposal_method_names, and application metadata.
- [x] Supported direct and scanned registrations agree on effective existence, permissions, frame,
  binding name, profile, resolvable policy, resolved disposal order, and application metadata.
- [x] Compare identity/fingerprints in isolated fixtures; do not bind the same fingerprint twice into
  one live registry and misinterpret the expected collision as a parity failure (each side its own Book).
- [x] A Protocol target with resolvable=False registers; the resolvable=True case still fails normally.
- [x] Non-bool resolvable values fail with the normal binding policy; invalid Protocol frames and
  incompatible existence/function combinations remain rejected.
- [x] Disposal cases cover omitted/empty/per-target names, Book overlap, configured priority,
  missing methods, duplicates, inherited callable names, and mutation of the original input list.
- [x] Metadata cases cover ordinary values, object identity, reserved keys, and caller-dictionary
  mutation. Metadata storage semantics are documented and do not leak into native policy fields.
- [x] Construction hooks retain order, copy discipline, and timing; Book registration pre/activation/
  post callbacks each run once per actual registration, including new options.
- [x] Discovery tests cover own metadata, undecorated and explicitly decorated subclasses, aliases,
  re-exports, corrupted metadata, distinct collisions, rescans, and module order.
- [x] Pre-conjure partial failure and post-conjure/outer-transaction boundaries are tested separately;
  the ticket does not claim atomicity beyond evidence or change it without approval.
- [x] Lifecycle coverage includes class scopes plus unique-only callable/existing-object rules.
- [x] Public signature/default documentation clearly records intentional permission/hook differences.
- [x] Existing focused tests and affected regression tiers pass with GIL disabled (VM; Windows tiers and
  hosted CI: Not run, owner).

## Deliverables
- This durable, downloadable investigation and implementation ticket.
- Later, only after approval: scoped patch, parity/discovery regression tests, and updated documentation.

## Files / Paths Impacted
- Investigation (dot, 2026-10-08): this ticket only; a byte-identical delivery copy is saved outside the checkout.
- Implementation (melder_1, 2026-10-10):
  - src/melder/aether/spellbook/bind/scan.py (the fix)
  - src/melder/aether/spellbook/spellbook.py (the Spellbook.scan docstring only)
  - src/melder/__version__.py (notch 0.2.8228)
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py (new)
  - tests/component/melder/spellbook/test_scan_bind_parity_component.py (new)
  - README.md (scan example and paragraph)
  - release_docs/next_version_release.md (opened for 0.2.8228)
  - context_compass/system_docs/src_components.md, src_architecture.md, tests_components.md and their
    indexes; src_graph.md, src_graph_index.md and the graph descriptors (scan.json authored prose)
  - context_compass/system_docs/patches/active/scan_bind_option_parity_2026_10_10/ (three patch docs, new)
  - generated build assets and llm_support bundles (rebuilt last)
- Turn-in (melder_1, 2026-10-10):
  - context_compass/system_docs/patches/active/scan_bind_option_parity_2026_10_10/ moved to patches/completed/
  - context_compass/artifacts/scan_bind_option_parity_20261010/ (evidence pack, new)
  - context_compass/attention_board.md and context_compass/artifact_board.md (closure sync)
- Proposed source: src/melder/aether/spellbook/bind/scan.py
- Proposed tests: tests/unit/melder/spellbook/test_scan_bind.py
- Proposed tests: tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py
- Proposed tests: tests/component/melder/spellbook/test_bind_lifecycle_hooks.py
- Proposed parity reference: tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py
- Proposed documentation: current scan/binding reference, selected by the approved implementer.

## Validation
Baseline: 345 passed in 2.66 seconds on CPython 3.14.8 free-threaded, Py_GIL_DISABLED=1,
sys._is_gil_enabled() == False. This was a focused run, not the whole repository suite.
Of these, 34 tests are the scan unit/integration files. Extra runtime probes confirmed F1-F3 and F5-F6.
No implementation changes exist, so proposed acceptance tests have not yet been implemented or run.

Environment preparation used the repository lock without modifying it:
```sh
UV_CACHE_DIR=/tmp/melder-uv-cache UV_PYTHON_INSTALL_DIR=/tmp/melder-python \
  uv sync --locked --python 3.14t --no-default-groups --group test
```
Exact focused command (output redirected only for collection):
```sh
.venv/bin/python -X gil=0 -m pytest -q \
  tests/unit/melder/spellbook/test_scan_bind.py \
  tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py \
  tests/component/melder/spellbook/test_bind_lifecycle_hooks.py \
  tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py \
  tests/unit/melder/spellbook/bind/test_bind.py
```
Probe invocation: PYTHONPATH=$PWD .venv/bin/python -X gil=0 /tmp/melder-scan-probes.py
Logs retained locally at /tmp/melder-scan-tests.log and /tmp/melder-scan-probes.log.
These temporary paths are convenience evidence; the reproducible recipe and measured results are
embedded here so the ticket does not depend on those files surviving.

Results (melder_1, 2026-10-10, CPython 3.14.7 free-threaded, -X gil=0, device VM): red run 54 failed / 9
passed on the old scan.py (Note 11); after the change the focused set is 409 passed (Note 18), the spellbook
unit tier, the conduit facade and the package public surface 2388 passed, the component spellbook tier 799
and the integration spellbook tier 613 (+2 skipped, 2 xpassed) in a delete-capable copy, and tests/unit/melder
8466 with two failures that need context_compass/system_docs and pass in the repository (Note 13). Windows
tiers and hosted CI: Not run (owner).

Final verification for the turn-in (melder_1, 2026-10-10, Note 21): the focused set 409 passed and the whole
tests/ tree 13,639 passed, 32 skipped, 17 xfailed, 2 xpassed, 0 failed, GIL off; lane logs in
artifacts/scan_bind_option_parity_20261010/runs/, the full set in artifacts/core_protection_review_20261010/runs/.

## Risks / Rollback Notes
- Metadata passthrough can accidentally reinterpret reserved names or mutable values; test boundaries.
- Changing inherited/alias discovery may affect applications relying on current behavior; owner decides.
- Do not change shared validation or transaction internals merely to make the decorator convenient.
- No source rollback is needed for this investigation. Later rollback must preserve existing registrations
  and respect the normal lifecycle/transaction contract rather than mutating live registries manually.

## Decision Log
- Confirmed: preserve one normal bind pipeline and the currently documented explicit permissions rule.
- Proposed, not approved: expose all three missing option families.
- Pending: own-object-only metadata discovery and identity deduplication within one scan.
- Deferred: broader transaction semantics; not authorized by this ticket-preparation request.
- 2026-10-10: the owner directed the fix (Note 5): the three option families and both proposed discovery
  policies are approved; broader transaction semantics stay deferred.
- 2026-10-10 (melder_1): implementation shape per Note 9 - 24 reserved metadata keys refused at decoration,
  bare-string disposal groups refused, ScanBindMetadata an immutable slotted class instead of a dataclass,
  own-__dict__ eligibility, identity dedup per scan; scan non-atomicity documented, not changed.
- 2026-10-10 (melder_1, turn-in): the two raised items below are carried as P3 follow-ups in the core-protection
  review's Hand-back section; neither is fixed here.
- 2026-10-10 (melder_1): raised to the owner, not fixed (outside this ticket): a bare-string
  disposal_method_names on direct Spellbook.bind is iterated per character and silently matches nothing;
  Spellbook.scan builds a Scan helper and never calls its cleanup().

## Applicable Anti-Patterns
- [x] Baseline findings distinguish FACT from policy proposals and UNKNOWN history.
- [x] No implementation, commit, push, or publication was inferred from a ticket request.
- [x] No status transition without evidence-backed reason and owner-approved scope.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Investigation and baseline validation recorded
- [x] Ticket deliverable produced with self-contained reproductions
- [x] Implementation steps complete and checked off
- [x] Approved regression tests pass and documentation is updated
- [x] Applicable anti-pattern checks are clear or escalated
- [x] Acceptance criteria reviewed with user and confirmed (owner, 2026-10-10; Note 20)
- [x] Board sync completed when implementation is activated or closed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true (patch docs and the turn-in evidence pack; the investigation evidence stays embedded here)
- ARTIFACT_PATHS:
  - system_docs/patches/completed/scan_bind_option_parity_2026_10_10/architecture_patch.md
  - system_docs/patches/completed/scan_bind_option_parity_2026_10_10/component_patch_scan_bind.md
  - system_docs/patches/completed/scan_bind_option_parity_2026_10_10/code_description_patch_scan_module.md
  - artifacts/scan_bind_option_parity_20261010/
- DISPOSITION: promote_to_documentation for the patch docs (promoted into src_components and src_architecture at
  landing, Note 15; the folder moved to system_docs/patches/completed/ at turn-in); retain_as_reference for the
  evidence pack (diffs, file manifest with SHA256, lane logs)
- CLEANUP_TRIGGER: applied at turn-in (2026-10-10T13:44:41Z).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: scan declaration parity and explicit discovery semantics
- IF_UNKNOWN: ask owner before implementation decisions

## Noting Behavior
- Append tactical findings with concrete evidence and one next action.
- Correct factual errors explicitly; do not rewrite uncertain history into a regression claim.

## Notes
- DATETIME: 2026-10-08T16:36:07Z
  TYPE: FACT
  CLAIM: The three missing option families are verified at the pinned SHA; supported scan inputs
    delegate to normal binding. The scan decorator is a partial adapter, not an alternate binder.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/scan.py:108-155
  - src/melder/aether/spellbook/bind/scan.py:359-368
  - src/melder/aether/spellbook/spellbook.py:5176-5187
  - src/melder/aether/spellbook/spellbook.py:5307-5330
  IMPACT: Fix capture/forwarding and test parity instead of duplicating validation.
  NEXT: Obtain approval for the missing-option scope and metadata ownership semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-08T16:36:07Z
  TYPE: MEASURE
  CLAIM: 345 focused tests passed; independent runtime probes reproduced inherited subclass discovery,
    alias collision with one surviving pre-conjure registration, and keyword rejections.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_scan_bind.py
  - tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py
  - src/melder/aether/spellbook/bind/scan.py:339-368
  IMPACT: Existing green tests do not cover full direct-bind option parity or settle discovery policy.
  NEXT: Add approved failing regression tests before implementing a fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-08T16:52:00Z
  TYPE: FACT
  CLAIM: A completed April profile-rebuild ticket explicitly recorded scan profile parity as an outcome.
    This supports preserving the one-pipeline design, but does not prove all future options were promised
    or establish when the present gaps and discovery behaviors originated.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md:142-158
  IMPACT: Avoid calling these newly introduced regressions without commit evidence.
  NEXT: Check bounded recent history and retain uncertainty if introduction remains unproven.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-08T16:56:00Z
  TYPE: FACT
  CLAIM: Bounded history proves direct bind gained resolvable on September 19 while scan.py stayed
    byte-identical to the August 2 snapshot. The new option was not propagated into the scan adapter.
    Existing discovery edge cases are older behaviors, with their first introduction still unknown.
  EVIDENCE:
  - git:63ef620e36071027e9d022937406aefbc3ccb41b:src/melder/aether/spellbook/spellbook.py
  - git:574cfa2a8480c2c6a2292c87b767c2943b8cb23d:src/melder/aether/spellbook/bind/scan.py
  - src/melder/aether/spellbook/bind/scan.py:108-155
  - src/melder/aether/spellbook/bind/scan.py:339-368
  IMPACT: Prioritize confirmed adapter option drift; treat discovery changes as explicit policy work.
  NEXT: Owner reviews the proposed option scope and discovery decisions before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:40:31Z
  TYPE: DECISION
  CLAIM: The owner added this ticket on 2026-10-10, assigned it to melder_1 and directed "go ahead and
    investigate the findings and fix them" (chat). That approves the proposed scope as written: scan_bind
    gains resolvable=True, disposal_method_names=None and application-metadata **kwargs, all forwarded
    through normal Spellbook.bind; F5 eligibility is own-object metadata only (an explicitly decorated
    subclass stays eligible); F6 binds each eligible object once per scan by identity, first occurrence
    wins, while distinct colliding targets and rescans still raise. The F4 differences stay; transaction
    and atomicity semantics stay out of scope. Board routing added (scan_bind_option_parity).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_restore_scan_bind_option_parity_task.md:92-159
  - context_compass/tickets/tasks/2026-10-08_restore_scan_bind_option_parity_task.md:229-250
  - context_compass/attention_board.md:181-182
  IMPACT: Implementation is authorized but still gated: the change alters a public signature and the
    scan eligibility policy, so patch docs come before code, and failing tests before the fix.
  NEXT: Read src/melder/aether/spellbook/bind/scan.py in full and verify F1-F6 at 66939dfe8.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:49:27Z
  TYPE: FACT
  CLAIM: F1-F6 hold at 66939dfe8 (working tree equals HEAD apart from CRLF) and every evidence range in
    this ticket lands on the logic it cites. Read in full: scan.py, Spellbook.bind/scan, the bind-window
    check, Bind.bind/_bind_logic and Spell.__init__. The forwarding chain the fix must feed is:
    Spellbook.bind passes resolvable and per-target disposal names to Bind and every non-hook kwarg on
    to Spell(**kwargs), which stores a fresh dict as spell.metadata; metadata is not fingerprinted. Keys
    that collide on that chain are reserved: spell, self, aetheric_frame,
    configured_disposal_method_names, enforce_priority_disposal_methods, _lifecycle_hooks (Bind.bind) and
    spell_index, spell_name, spell_type, spell_id, existing_object, spellbook, spellframe_kind,
    implemented_protocols (Spell). Root cause of F5: scan.py:343 uses getattr, which also resolves class
    attributes through instances, metaclass attributes and __getattr__ fallbacks.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/scan.py:54-142
  - src/melder/aether/spellbook/bind/scan.py:145-236
  - src/melder/aether/spellbook/bind/scan.py:320-370
  - src/melder/aether/spellbook/spellbook.py:5176-5188
  - src/melder/aether/spellbook/spellbook.py:5291-5350
  - src/melder/aether/spellbook/spellbook.py:5473-5546
  - src/melder/aether/spellbook/spellbook.py:3621-3644
  - src/melder/aether/spellbook/bind/bind.py:455-569
  - src/melder/aether/spellbook/bind/bind.py:658-807
  - src/melder/aether/spellbook/spell.py:301-321
  - src/melder/aether/spellbook/spell.py:461-465
  IMPACT: The fix is capture and forwarding inside scan.py only; Spellbook, Bind and Spell stay as they
    are. Reserved keys must be refused at decoration, or they fail later at scan time mid-module.
  NEXT: Record the baseline probe results, including two failures the ticket did not list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:49:37Z
  TYPE: MEASURE
  CLAIM: Baseline probes (CPython 3.14.7 free-threaded, -X gil=0, Melder 0.2.8227 from this tree, scratch
    scripts outside the repository) confirm F1-F3 (TypeError: unexpected keyword), direct Protocol bind
    with resolvable=False, F5 (Parent and undecorated Child both bound) and F6 (Spell ID collision, one
    spell left). Two more failures share F5's getattr root cause: a module-level instance of a decorated
    class makes the scan fail ("Binding signature already active in this frame", one spell left), and
    any module object with a permissive __getattr__ aborts the scan ("scan_bind metadata ... invalid or
    corrupted", nothing bound). Direct bind facts: reserved kwargs raise "got multiple values" from
    Bind.bind() or Spell(); spell.metadata is a fresh dict with value identity kept, and Spell cleanup
    clears that dict in place; a bare-string disposal_method_names is iterated per character and
    silently matches nothing (out of scope, raised to the owner).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/scan.py:342-357
  - src/melder/aether/spellbook/spell.py:605-633
  - src/melder/aether/spellbook/bind/bind.py:707-725
  - src/melder/aether/spellbook/bind/bind.py:784-807
  IMPACT: The own-object rule also fixes the instance and __getattr__ failures, so tests must cover them.
    The stored scan metadata must never be the dict handed to bind, or one spell's cleanup would empty
    the decorator's copy for later scans.
  NEXT: Read the scan integration tests, the scan mock modules and the resolvable parity reference.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:51:08Z
  TYPE: FACT
  CLAIM: Existing coverage is module-only scanning, re-exports, distinct-target collisions, rescans and
    reimports, module order, lambdas (unique only), corrupted metadata, functools.wraps stacking,
    post-conjure conduit and spellbook scans, Nexus records and one hook dispatch per scanned
    registration. Nothing covers the three options, inherited or instance metadata, aliases, metadata
    storage or disposal/resolvable parity. functools.wraps copies the wrapped __dict__, so the
    own-object rule keeps the wraps case bindable. A failed scan is atomic in no mode: a probe with two
    targets sharing one binding key leaves the first registered pre-conjure, post-conjure in scan's own
    window and post-conjure inside an outer spellbook or conduit bind window. A bind window's end does
    not undo registrations, so Spellbook.scan's docstring ("commits or rolls back with that outer
    window", "atomic in isolation") is wrong and gets corrected, not the behaviour (ticket scope).
  EVIDENCE:
  - tests/unit/melder/spellbook/test_scan_bind.py:71-333
  - tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py:66-522
  - tests/component/melder/spellbook/test_bind_lifecycle_hooks.py:326-366
  - tests/mocks/spellbook/scan_bind_module_wrapped.py:1-123
  - src/melder/aether/spellbook/spellbook.py:4394-4473
  - src/melder/aether/spellbook/spellbook.py:5483-5498
  IMPACT: The new tests cover the gaps and pin the non-atomic boundary in all three modes; the scan
    docstring stops promising a rollback the code does not perform.
  NEXT: Record the design decisions and the patch-gate plan before any test or code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:55:07Z
  TYPE: DECISION
  CLAIM: Implementation shape, inside the approved scope. (1) scan_bind gains resolvable=True,
    disposal_method_names=None and **spell_metadata; resolvable is stored as given and checked by Bind at
    scan time (no coercion, no decorator rule); disposal names must be a list or tuple of str and are
    kept as a tuple (a bare string, which direct bind iterates per character, is refused like a bad
    hook list); metadata keys that collide on the bind chain (24 names, a class constant guarded by a
    signature test) raise TypeError at decoration; metadata is a read-only shallow snapshot, values by
    identity, handed to bind as fresh dict entries. (2) ScanBindMetadata stops being a dataclass: it
    would now hold arbitrary application objects, which the profile's value-only dataclass rule
    forbids (it already held callables and Protocol classes). It becomes an immutable slotted class
    with the same keyword constructor and attribute names; it owns nothing, so it has no cleanup.
    Internal type, constructed only in scan.py. (3) Discovery reads only the object's own __dict__
    (fixes F5, module-level instances and __getattr__ proxies); each object binds once per scan, keyed
    by id() with a strong reference held for the scan; aliases add no spell id. (4) Docs: the
    Spellbook.scan rollback claim is corrected; the README scan example, which raises TypeError because
    it omits the required permissions, gets permissions="create" (F4 keeps permissions required).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/scan.py:54-142
  - src/melder/aether/spellbook/bind/bind.py:707-725
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:257-286
  - README.md:550-588
  IMPACT: Every behaviour change stays in scan.py; Spellbook, Bind and Spell are untouched.
  NEXT: Write patch docs scan_bind_option_parity_2026_10_10 and link them before tests or code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:56:42Z
  TYPE: PLAN
  CLAIM: Patch gate met: scan_bind_option_parity_2026_10_10 (architecture, component, code-description)
    is written, linked in Artifact Links and on artifact_board.md, and was consumed in that order.
    Mapping (patch section -> implementation -> validation): Interface deltas -> scan_bind parameters,
    disposal and metadata helpers, ScanBindMetadata slots and to_bind_kwargs -> unit decoration and
    parity tests. Invariants "own declaration" and "one registration per object" -> scan_module own
    __dict__ lookup and id() dedup -> unit discovery tests (subclass, instance, proxy, alias, wraps,
    re-export, corrupted, collision, rescan). Invariant "reserved keys" -> class constant plus
    decoration check -> signature-derived drift test. State and failure deltas -> no runtime change ->
    component boundary tests (pre-conjure, post-conjure own and outer window) and the Spellbook.scan
    docstring fix. Validation expectations -> new unit and component files, then the existing scan,
    bind, hook and resolvable tiers with GIL off. Unknowns in the patch docs: none open.
  EVIDENCE:
  - context_compass/system_docs/patches/active/scan_bind_option_parity_2026_10_10/architecture_patch.md:1-56
  - context_compass/system_docs/patches/active/scan_bind_option_parity_2026_10_10/component_patch_scan_bind.md:1-39
  - context_compass/system_docs/patches/active/scan_bind_option_parity_2026_10_10/code_description_patch_scan_module.md:1-32
  - context_compass/artifact_board.md:95-97
  IMPACT: Implementation may start; tests first, and they must fail on the current scan.py.
  NEXT: Write tests/unit/melder/spellbook/test_scan_bind_option_parity.py and run it red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T09:04:24Z
  TYPE: MEASURE
  CLAIM: Red run on the unchanged scan.py (3.14.7t, -X gil=0): the two new files collect 63 tests;
    54 fail and 9 pass. The 9 that pass pin behaviour that must not change: native-policy parity, the
    omitted disposal group under both Book priorities, Bind's refusal of a Protocol left resolvable,
    and the five failure-boundary modes (the first registration survives a failed scan pre-conjure,
    in scan's own Book or conduit window, and inside an outer Book or conduit window). Two tests passed
    for the wrong reason on the first run (TypeError text and the alias collision) and were tightened
    to match the intended messages before this count.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:1-728
  - tests/component/melder/spellbook/test_scan_bind_parity_component.py:1-201
  IMPACT: Every new contract is red on the old code for the intended reason; green after the change
    proves the fix rather than the tests.
  NEXT: Implement scan.py (signature, ScanBindMetadata, own-dict discovery, identity dedup) and rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T09:09:25Z
  TYPE: FACT
  CLAIM: scan.py implements the plan (Note 9): scan_bind takes resolvable, disposal_method_names and
    **spell_metadata; two pure helpers validate and snapshot the disposal group and the metadata
    (reserved keys refused, names sorted in the error); ScanBindMetadata is an immutable slotted class
    with the dataclass's keyword constructor and attribute names plus resolvable,
    disposal_method_names, spell_metadata (read-only mapping over a private copy), a 24-name
    RESERVED_SPELL_METADATA_KEYS constant, __setattr__/__delattr__ guards and a values-free repr;
    to_bind_kwargs adds the metadata entries; Scan._own_scan_bind_metadata reads only the object's own
    __dict__ and scan_module binds each object once per scan by id() while holding it. Spellbook, Bind
    and Spell are unchanged. All removed lines are PEP 604 annotations rewritten as Union/Optional, the
    dataclass import/decorator, the getattr lookup and docstring sentences extended in place.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/scan.py:53-134
  - src/melder/aether/spellbook/bind/scan.py:137-401
  - src/melder/aether/spellbook/bind/scan.py:405-541
  - src/melder/aether/spellbook/bind/scan.py:544-752
  IMPACT: The fix is contained in one module; existing readers of the payload see the same attributes.
  NEXT: Run the scan, bind, hook and resolvable tiers plus the new files with GIL off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T09:20:33Z
  TYPE: MEASURE
  CLAIM: Green with the GIL disabled (CPython 3.14.7t, -X gil=0). The ticket's focused set plus the two
    new files: 408 passed (345 baseline + 63 new). In the repository: tests/unit/melder/spellbook, the
    conduit facade and the package public surface 2388 passed. tests/component/melder/spellbook in
    the repository: 760 passed, 39 failed, every failure a PermissionError from shutil.rmtree on the
    delete-refusing connected folder (cache fixtures under src/melder/tests); in a delete-capable copy
    of src and tests on the VM the same tier is 799 passed. tests/integration/melder/spellbook in the
    copy: 613 passed, 2 skipped, 2 xpassed. tests/unit/melder in the copy: 8466 passed, 2 failed in
    test_system_documents_builder only because the copy has no context_compass/system_docs; that file
    passes 60/60 in the repository. Runs use PYTHONPYCACHEPREFIX outside the repository, because
    stale Windows-compiled pytest .pyc files make one inspector test read source from C:\ paths.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/scan.py:544-752
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:1-729
  - tests/component/melder/spellbook/test_scan_bind_parity_component.py:1-201
  IMPACT: No regression in the scan, bind, hook, resolvable, spellbook or unit tiers; the only red runs
    are environmental and pass where deletes work. Windows tiers and hosted CI: Not run (owner).
  NEXT: Correct the Spellbook.scan docstring and the README example, then update the system documents.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T09:21:51Z
  TYPE: FACT
  CLAIM: Public documentation corrected. The Spellbook.scan docstring no longer promises that a scan
    commits or rolls back with its bind window; it states that ending a window unregisters nothing,
    so targets bound before a failure stay registered (same line count, so no spellbook.py citation
    moves). The README "Declarative Binding by Module" example now passes permissions="create" on both
    decorators - without it the example raised TypeError (missing required keyword-only argument) -
    and a short paragraph states that scan_bind takes bind()'s target options and that subclasses and
    instances of a decorated class are not registered. The README example runs: scan, conjure and
    meld("MetricsHub") succeed. README.md keeps its mixed CRLF/LF endings (new lines use CRLF like
    their neighbours). The API reference page is generated from the scan_bind docstring at docs build.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5483-5504
  - README.md:552-597
  - docs/maintaining.md:121-131
  IMPACT: Users see the real contract; the docs CI build renders the new scan_bind docstring.
  NEXT: Read the src_components and src_architecture authoring instructions, then update both documents.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T09:36:41Z
  TYPE: FACT
  CLAIM: System documents updated for 0.2.8228 and all three indexes regenerated (--check OK). src_components:
    Scan-Bind Module Scanner rewritten from scan.py as read (signature, decoration checks, own-__dict__
    eligibility, once-per-object dedup, slotted ScanBindMetadata, to_bind_kwargs, non-atomic failure), a
    scan flow under C1 flows, the Spellbook Core responsibility line, scan.py extent 373 -> 755 and spellbook.py
    re-verified, handoff entry. src_architecture: boundary bullet, a "Scan declarations" invariant, three
    failure-mode entries (Breaking subclass/instance change, decoration TypeErrors, non-atomic scans), C1 map,
    handoff. tests_components: both new files in their spellbook clusters (Protects + Key Files), three C1
    entries - the third is test_contract_mutation_during_meld_resolution_integration.py, which my 0.2.8227 lane
    listed as a key file without a code-map entry - core set 209 (the stated 206 matched the map, not the
    207-path union), tier and tree counts recounted from disk (784 test modules; nine counts were stale from
    earlier lanes). Content Preservation Gate: every baseline line survives except deliberate in-place updates
    (Metadata dates, two remeasured extents, verified_at stamps, the architecture scan.py note extended, the
    recounted numbers). Portability and absolute-path checks clean, no wrapped headings, new lines <= 120
    chars. Rubric not re-scored (incremental pass; precedent of the 2026-10-01 citation audit).
  EVIDENCE:
  - context_compass/system_docs/src_components.md:5434-5492
  - context_compass/system_docs/src_components.md:7134-7152
  - context_compass/system_docs/src_architecture.md:420-424
  - context_compass/system_docs/src_architecture.md:922-937
  - context_compass/system_docs/src_architecture.md:1548-1568
  - context_compass/system_docs/tests_components.md:951-989
  - context_compass/system_docs/tests_components.md:1188-1218
  - src/melder/aether/spellbook/bind/scan.py:544-752
  IMPACT: Readers of the packaged documents see the new scan contract and the Breaking change; the test map
    follows the source map and no longer misses the 0.2.8227 regression.
  NEXT: Regenerate the graph (extract_graph.py --strict on 3.14, then assemble_graph.py) and fix any stale
    authored prose on the scan.py descriptor.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T09:43:52Z
  TYPE: FACT
  CLAIM: Graph regenerated on CPython 3.14.7 (extract_graph.py --strict: 587 descriptors, 1217 nodes, skipped
    0; assemble_graph.py and its --check: 587 sections, all ranges verified, no package paths in the
    document). The scan.py descriptor's authored prose now matches the source as read: ScanBindMetadata carries
    the new options, holds metadata as a read-only shallow copy handed out fresh per bind, and is a slotted
    class, not a dataclass; Scan reads only an object's own __dict__ and binds each object once per scan. The
    three scan nodes were re-accepted after that read (graph_walker --accept). Content changes against HEAD:
    scan.json, spellbook.json (docstring edit; its Spellbook nodes were already SEMANTICS_STALE before this
    change and are left unaccepted - the class was not re-read) and the eight build-asset payload descriptors,
    which lag the assets by one rebuild as they did at HEAD. The census of 138 stale nodes is pre-existing.
  EVIDENCE:
  - context_compass/system_docs/src_graph.md:5945-6006
  - context_compass/system_docs/src_graph_index.md:161-161
  - src/melder/aether/spellbook/bind/scan.py:137-401
  - src/melder/aether/spellbook/bind/scan.py:544-752
  IMPACT: Graph slices for scan.py describe the new behaviour; nothing in the graph claims a frozen dataclass.
  NEXT: Read src/melder/__version__.py and release_docs/next_version_release.md, then notch to 0.2.8228.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T09:47:44Z
  TYPE: FACT
  CLAIM: Notched 0.2.8227 -> 0.2.8228 and opened the running release note (it was empty: the owner staged
    the 0.2.8227 note's rename to release_docs/0.2.8227.md after tagging 0.2.8227 on release merge 81c61b91,
    so the frozen window is over and this is the first notch after the publish; PyPI was not checked - the
    fetch is disallowed). The note's example runs (scan, conjure, meld, the per-target close() at cleanup,
    the bare-string and reserved-key refusals). Checking the acceptance criteria against the tests found one
    gap: no test scans a directly decorated module-level instance, so "unique-only existing-object rules" on
    the scan path is unpinned. Such an instance carries its own declaration, so it is a target, and Bind's
    rule ("Existing-object spells must use Existence.unique") must apply on the scan path too.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-47
  - src/melder/aether/spellbook/bind/bind.py:1121-1136
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:543-566
  IMPACT: Without the test the acceptance criterion would be claimed on evidence that does not exist.
  NEXT: Add the existing-object discovery test to the unit file, run it, then the post-notch tiers.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T09:49:42Z
  TYPE: MEASURE
  CLAIM: The existing-object gap is closed: a directly decorated module-level instance carries its own
    declaration, scans as a unique existing object with its metadata (Spell.spell is the instance, not its
    class), and the same declaration with existence="many" is refused by Bind ("Existing-object spells must
    use Existence.unique") with nothing registered. It pins behaviour that did not change (old getattr
    discovery also found the instance), so it is coverage, not a red/green regression. Focused set after the
    notch, GIL off (CPython 3.14.7t): 409 passed (the ticket's five baseline files plus the two new files).
    tests_components now lists the unit file at 768 lines and names the existing-object case.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:625-662
  - src/melder/aether/spellbook/bind/bind.py:1121-1136
  - context_compass/system_docs/tests_components.md:951-989
  IMPACT: Every acceptance criterion now has a test or a documented source citation behind it.
  NEXT: Move the ticket to review (checklists, transition, handoff), sync the board and the notch notice,
    then rebuild the assets and the llm_support bundles last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T11:02:22Z
  TYPE: MEASURE
  CLAIM: Rebuilt last, on CPython 3.14.7t. _build_asset_runner.py wrote the three asset families at
    v0.2.8228 (bind guard 622 entries, unchanged; agent documentation 462; system documents 4) and --check
    prints three OK lines. The first attempt stopped at the payload step because the connected folder
    refused the builder's unlink of the three system-document payload modules; the owner granted delete
    permission for the folder this session and the rerun recreated them. llm_support/_builder.py
    --include-untracked rebuilt src, tests and other; --check --include-untracked prints three OK lines.
    The tracked-only --check reports tests STALE until the two new test files are added to git (the
    owner's git add). After the rebuild, GIL off: package version, public surface, registration guard,
    build_assets and llm_support tests 163 passed and 1 skipped; system documents, document view and
    package metadata 115 passed; annotation integrity and architecture_and_design 28 passed.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_build_asset_runner.py:380-399
  - llm_support/_builder.py:860-880
  IMPACT: Assets, bundles and the version agree at 0.2.8228; the lane is ready for the owner's review.
  NEXT: Owner: git add -A, commit, push, Windows tiers and hosted CI, then accept or redirect.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T13:24:32Z
  TYPE: DECISION
  CLAIM: The owner accepted the work of this request and asked for the tickets to be turned in (chat
    2026-10-10: "I accept review, everything is good, and make sure to turn in your tickets"; then "finalize and
    hand back the review tickets and supporting evidence", with diffs, revision, environment and test results).
    Turn-in for this lane: final verification on the hand-back tree, an evidence pack at
    artifacts/scan_bind_option_parity_20261010/ (diffs, file manifest with SHA256, logs), the patch folder
    archived to system_docs/patches/completed/ (its decisions were promoted into src_architecture and
    src_components at landing, Note 15), the closure summary naming notch 0.2.8228 and the release-note section,
    the move to tickets/tasks/completed/, the board and artifact-board sync, and the rebuild last. Not
    authorized: commits or a push; the two items raised in the Decision Log stay open as follow-ups.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_restore_scan_bind_option_parity_task.md:323-335
  - context_compass/attention_board.md:181-181
  IMPACT: The lane closes with its evidence kept beside it; nothing about the protection review rides on it.
  NEXT: Record the final verification for this lane, then write its evidence pack.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T13:24:32Z
  TYPE: MEASURE
  CLAIM: Final verification on the hand-back tree (GIL off, CPython 3.14.7t, pytest 9.1.1, HEAD 66939dfe8 plus
    this request's working-tree changes): the focused scan set 409 passed (the five baseline files and the two
    new ones); tests/unit 9020 passed, 3 skipped, 7 xfailed; component spellbook 799 passed - in the repository
    now that deletes are allowed, where Note 13 saw 39 PermissionErrors; integration spellbook 613 passed,
    2 skipped, 2 xpassed; the rest of the tree green as well (13,639 passed, 0 failed across tests/). Every skip,
    xfail and xpass outside the core-protection suite is pre-existing. Windows tiers and hosted CI: Not run
    (owner).
  EVIDENCE:
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:1-768
  - tests/component/melder/spellbook/test_scan_bind_parity_component.py:1-201
  - src/melder/aether/spellbook/bind/scan.py:544-752
  IMPACT: The landing holds on the final tree; turn-in can proceed.
  NEXT: Write the evidence pack, then archive the patch folder and close the ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T14:05:31Z
  TYPE: MEASURE
  CLAIM: Turned in. The patch folder moved to system_docs/patches/completed/scan_bind_option_parity_2026_10_10/ (its
    decisions were promoted at landing, Note 15); this ticket moved to tickets/tasks/completed/; the board lost the
    active row and its details and gained a closed anchor; artifact_board.md cleared the three patch rows and recorded
    the archived folder (promote_to_documentation) and the evidence pack artifacts/scan_bind_option_parity_20261010/
    (retain_as_reference: lane diffs against HEAD, a file manifest with SHA256 of the final bytes, lane logs). Rebuilt
    last: the asset and llm_support checks print OK and no generated file changed bytes; after the rebuild the focused
    set is 409 passed with the GIL off. Notched 0.2.8228; release note section "`scan_bind` takes every option `bind`
    takes, and registers only what a module declares". Nothing committed or pushed.
  EVIDENCE:
  - context_compass/artifacts/scan_bind_option_parity_20261010/README.md:1-28
  - context_compass/artifacts/scan_bind_option_parity_20261010/runs/v15_scan_focused_post.txt:1-10
  - context_compass/artifacts/scan_bind_option_parity_20261010/file_manifest.md:1-41
  - release_docs/next_version_release.md:1-47
  IMPACT: The lane is closed with its evidence beside it; the commits, Windows tiers and hosted CI are the owner's.
  NEXT: none in this ticket; the two raised items are P3 follow-ups in the core-protection review's Hand-back.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
DONE (melder_1, 2026-10-10T13:44:41Z). Accepted by the owner and turned in: landed at 0.2.8228 (release note
section "`scan_bind` takes every option `bind` takes, and registers only what a module declares"), patch docs
promoted and archived, evidence pack at artifacts/scan_bind_option_parity_20261010/. Owner-owed: the commits
(Commit Grouping A in the core-protection review ticket), Windows tiers and hosted CI. The two raised items stay
open as P3 follow-ups.

REVIEW (melder_1, 2026-10-10). Landed at 0.2.8228 inside the approved scope: scan_bind takes resolvable,
per-target disposal_method_names and keyword metadata with bind's defaults and replays them through
Spellbook.bind; reserved metadata keys and bare-string disposal groups are refused at decoration;
ScanBindMetadata is an immutable slotted class whose metadata is a read-only shallow copy handed out fresh
per bind; only an object's own __dict__ declaration makes it a target (Breaking for undecorated subclasses;
instances and proxies no longer break a scan) and each object binds once per scan (aliases no longer
collide). Scans stay non-atomic; the Spellbook.scan docstring now says so. Tests: 64 new (unit + component),
red/green recorded, broader tiers green with the GIL off. Docs: README example fixed, system documents,
graph, patch docs (promote at turn-in), running release note. Owner: commit (git add -A for the two new test
files and the patch folder), push, run the Windows tiers and hosted CI, accept or redirect; then the patch
folder moves to patches/completed/ and the ticket closes. Raised, not fixed: the two items in the Decision Log.
Assets and llm_support bundles are rebuilt at 0.2.8228 with every check OK (Note 19); the tracked-only
llm_support check passes once the two new test files are added to git.

Earlier summary (dot, 2026-10-08, draft stage):
The latest verified codex_features2 baseline uses normal binding internally but scan_bind cannot express
resolvable, per-target disposal names, or arbitrary metadata. Existing validation and registration are
shared. Preserve documented differences unless explicitly changed. Decide subclass/alias behavior before
implementation. Focused baseline tests pass; reproductions expose gaps not covered by those tests.
This is a draft implementation ticket, with no implementation or remote publication authorized.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
- Download copy: /workspace/shared/melder-tickets/2026-10-08_restore_scan_bind_option_parity_task.md
- Stable source links use the full commit above; example:
  https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/aether/spellbook/bind/scan.py#L145-L155
<!-- END USER-DEFINED: project_fields -->
