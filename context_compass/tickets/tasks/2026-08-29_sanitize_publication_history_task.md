# Task: Sanitize Melder publication history locally

## Metadata
- Task ID: TASK-2026-08-29-sanitize-publication-history
- Story: none
- Status: in_progress
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-29T22:22:13Z
- Updated: 2026-08-29T23:42:57Z

## Objective
Rewrite the local `melder_private` Git history to remove the owner-approved
private data and legacy/output path families while preserving canonical source,
tickets, authorship, chronology, and current uncommitted work.

## Ticket Contract
- ENTRY_GATE: Owner approved the targeted sanitation plan and explicitly selected
  `<local-path>\PycharmProjects\melder_private` as the local rewrite target.
- EXECUTION_BOUNDARY: Local repository, verified local backup, temporary tooling,
  and ContextCompass tracking only. No commit, remote mutation, push, or PyPI action.
- DEPENDENCIES: The audit and removal plan in
  `tickets/tasks/2026-08-29_private_to_public_deployment_pipeline_discovery_task.md`.
- EXIT_GATE: Backups verify; forbidden historical paths/text are absent; tickets
  and source outside the manifest remain equivalent; Gitleaks is clean; the working
  tree is restored without forbidden files.
- FAILURE_ESCALATION: Stop before rewriting on backup failure. Stop after rewriting
  on unexpected source/ticket loss, failed Git integrity, secret finding, or
  unrecoverable working-tree conflict.

## Scope Boundaries
- In scope:
  - verified Git bundle plus tracked/untracked working-tree recovery material
  - exact history path removal and local-path text replacement
  - narrow GTM/persona history sanitation
  - post-rewrite Git, path, blob, secret, and tree-equivalence validation
- Out of scope:
  - `git commit`
  - pushing, changing remotes, changing repository visibility, or publishing
  - broad ticket removal or clean-slate history
  - copied competitor-source removal because audit proved it was never committed

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: The owner approved local execution with no commit or remote
  mutation.

## Steps / Checklist
- [x] Capture and verify branch/ref inventory.
- [x] Create and verify full Git bundle backup.
- [x] Capture tracked working-tree binary patch and untracked non-ignored files.
- [x] Stash current work to make the rewrite safe.
- [x] Install verified temporary `git-filter-repo` tooling.
- [x] Generate the exact removal and text-replacement manifests.
- [x] Rewrite all local history and restore allowed uncommitted work.
- [x] Prove forbidden paths and private text are absent.
- [x] Prove source/ticket preservation outside the approved manifest.
- [x] Rerun Gitleaks and large-blob inventory.
- [ ] Run Git integrity, build-asset, packaging, and supported test checks.
- [ ] Report local state and recovery locations; do not commit or push.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      execution.

## Deliverables
- Sanitized local Git history and working tree.
- Verified recovery bundle and working-tree recovery material.
- Exact removal/replacement manifests and validation evidence.

## Files / Paths Impacted
- Local `.git` object graph and refs under the approved repository.
- Owner-approved private/output paths throughout history.
- `context_compass/attention_board.md`
- This task and the discovery task.

## Validation
- Supported test tiers: pass (`10,959 passed`, exit code 0).
- Wheel/sdist build, member scan, and isolated install smoke: pass.
- Full Git fsck after immediate prune: pass; zero unreachable objects.
- Required:
  - `git fsck --full`
  - forbidden-path and forbidden-text history scans
  - Gitleaks full-history scan
  - source/ticket equivalence checks outside the manifest
  - build assets, supported tests, wheel/sdist build, and archive inspection

## Risks / Rollback Notes
- History rewriting changes commit hashes. Original hashes remain recoverable from
  the verified backup bundle.
- Dirty working-tree state can be lost if not captured. Binary patch and untracked
  archive verification are mandatory before any rewrite.
- Broad filters can remove legitimate tickets/source. Use exact path families and
  compare pre/post inventories before acceptance.

## Applicable Anti-Patterns
- [ ] No rewrite before backup verification.
- [ ] No `git reset --hard` or destructive checkout.
- [ ] No `git push --mirror`.
- [ ] No broad ContextCompass or ticket deletion.
- [ ] No generic large-blob stripping that would remove intentional build assets.
- [ ] No commit, remote mutation, push, or publication.
- [ ] No status transition without evidence-backed transition reason.
- [ ] No closure without acceptance confirmation and board sync.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed
- [ ] Notes quality maintained
- [ ] Applicable anti-pattern checks are clear or escalated
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - local history sanitation
  - backup and recovery
  - publication-boundary validation
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence.

## Notes

- DATETIME: 2026-08-29T23:42:57Z
  TYPE: MEASURE
  CLAIM: The disposable bare probe cloned successfully from the second bundle,
    contains every expected head/remote/stash plus both identical Codex tree
    refs, and passes full strict fsck before filtering. The active repository
    has not undergone the binary-aware rewrite.
  EVIDENCE:
  - `<external-recovery>/binary_rewrite_probe.git`
  IMPACT: Callback behavior can now be proven against the exact current ref
    graph without risking the working repository.
  NEXT: Delete only the probe's two noncommit tree refs, run the callback, and
    require zero decoded path blobs plus preserved commit/file counts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:42:04Z
  TYPE: FACT
  CLAIM: The pinned filter tool confirms ordinary `--replace-text` deliberately
    skips blobs with NUL bytes in the first 8 KiB, explaining the miss. Its
    blob callback receives mutable `blob.data`, so a BOM/encoding-preserving
    callback is the supported repair seam. Two newly created Codex turn-diff
    refs are identical tree objects, not commits; filter-repo cannot rewrite
    them and they must not remain as unsanitized reachability anchors.
  EVIDENCE:
  - `<external-tool>/git_filter_repo.py:603-626`
  - `<external-tool>/git_filter_repo.py:3811-3830`
  - `.git`
  IMPACT: The disposable probe and active rewrite must delete only those two
    noncommit harness refs after their verified bundle/worktree backup, then run
    the callback across commit refs.
  NEXT: Create a bare probe from the second bundle, delete its two tree refs,
    run the callback, and compare every ref/tree/blob invariant.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:39:56Z
  TYPE: MEASURE
  CLAIM: The second pre-repair recovery set verifies. Its all-ref bundle is
    36,904,809 bytes with SHA-256
    `c394fc318f042afc4a6136721949a42b43adfad6ab55093bc366325c44ae9bc4`;
    the binary worktree patch is 323,418 bytes with SHA-256
    `dba5509e884291d1f8799e49afa574f22f8ce637483d51eced27a66c2156d5cd`;
    all three untracked files were copied and hash-verified.
  EVIDENCE:
  - `<external-recovery>/post_prune_pre_binary_rewrite_all_refs.bundle`
  - `<external-recovery>/post_prune_pre_binary_rewrite_worktree.patch`
  - `<external-recovery>/post_prune_pre_binary_rewrite_untracked`
  IMPACT: The exact post-first-rewrite refs and current dirty state are recoverable
    independently before the binary-aware rewrite.
  NEXT: Inspect the two newly captured Codex turn-diff refs and the pinned
    filter-repo blob-callback contract before creating the disposable probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:38:54Z
  TYPE: FACT
  CLAIM: All 82 matching blobs map to 81 known ContextCompass paths: preserved
    February pytest/profile artifacts, the two current typecheck artifacts, and
    one sanitation-task blob held by stash. Prod/dev/preprod and
    codex_features2 each reach 81 matching blobs; test reaches none. Every match
    is an actual user-home path, not a secret-pattern or filename false positive.
  EVIDENCE:
  - `artifacts/`
  - `tickets/tasks/2026-08-29_sanitize_publication_history_task.md`
  - `.git`
  IMPACT: A global content callback constrained by the decoded user-home regex is
    safer than enumerating 81 filenames and preserves every artifact. It will
    replace workspace prefixes with `<repo-root>` and other home prefixes with
    `<local-path>` while retaining encoding and BOM.
  NEXT: Create a second verified all-ref/worktree recovery set, then prove the
    callback on a disposable clone before touching the active repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:37:34Z
  TYPE: BLOCKER
  CLAIM: Correction to the path-limited scope: a binary-aware scan of all
    29,792 reachable blobs finds 82 blobs with actual user-home prefixes, not
    only the two current artifact blobs. Most are UTF-16 report revisions and
    three are UTF-8. The preflight transform round-trips every encoding, keeps
    line counts stable, and preserves JSON validity where applicable.
  EVIDENCE:
  - `.git`
  IMPACT: Repair remains content-only, but it must target every matching blob
    across reachable history rather than two filenames. Path/ref mapping is
    required before rewrite approval can be considered satisfied.
  NEXT: Map all 82 blob identities to repository paths, version counts, and
    containing ref families; confirm none is a secret/non-path false positive.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:35:32Z
  TYPE: FACT
  CLAIM: Path-limited history enumeration finds exactly one reachable blob for
    each affected artifact, each introduced by one commit. The typecheck blob
    contains 74 user-home/workspace prefixes; the DevOps JSON blob contains 19.
    Both are UTF-16 and no alternate revisions exist for either path.
  EVIDENCE:
  - `artifacts/spellbook_typecheck_report.txt:1-253`
  - `artifacts/dev_ops_typecheck_scan.json:1-848`
  IMPACT: The repair surface is two blobs and 93 decoded prefix substitutions;
    no file deletion, general artifact rewrite, or source change is warranted.
  NEXT: Scan every reachable blob binary-aware to prove there are no other
    UTF-16/local-path misses, then validate the transform in memory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:34:32Z
  TYPE: FACT
  CLAIM: Both missed artifacts are UTF-16LE with BOM and approximately half of
    their bytes are NULs. Git's binary detection therefore skipped them under
    `git grep -I`, and filter-repo's ordinary text replacements did not match the
    interleaved byte representation. Git attributes declare text/LF but do not
    transcode the committed UTF-16 content.
  EVIDENCE:
  - `artifacts/spellbook_typecheck_report.txt:1-253`
  - `artifacts/dev_ops_typecheck_scan.json:1-848`
  IMPACT: The repair must decode and re-encode UTF-16LE with BOM while replacing
    only the machine-local prefixes; generic ASCII replacement is insufficient.
  NEXT: Enumerate every distinct reachable blob for both paths and count all
    decoded user-home/workspace occurrences before defining the callback.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:33:44Z
  TYPE: BLOCKER
  CLAIM: Correction to the preceding ref-clean note: each artifact's worktree,
    index, and HEAD blob hash is identical and both index flags are normal.
    `git grep -I` silently excluded these binary-detected blobs, so the earlier
    ref scan did not test them. Machine-local paths remain in reachable history.
  EVIDENCE:
  - `artifacts/spellbook_typecheck_report.txt`
  - `artifacts/dev_ops_typecheck_scan.json`
  - `.git`
  IMPACT: Final publication safety requires a third, path-limited binary-aware
    history rewrite. Deleting either artifact is not justified.
  NEXT: Identify encoding, NUL/BOM shape, affected blob count, and ref coverage;
    then construct a byte-preserving replacement callback for only these files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:33:03Z
  TYPE: FACT
  CLAIM: Correction to the preceding blocker: every head, remote-tracking ref,
    and live stash is clean for the IDE-workspace marker, and exact history
    search finds zero commits containing the artifact prefix. The two tracked
    artifact files therefore differ only in the filesystem while Git status
    suppresses them; reachable rewritten history is clean.
  EVIDENCE:
  - `.git`
  - `artifacts/spellbook_typecheck_report.txt`
  - `artifacts/dev_ops_typecheck_scan.json`
  IMPACT: No third history rewrite is needed. The remaining work is to identify
    the index flag/stat mechanism hiding these working copies and reconcile them
    without losing other content.
  NEXT: Inspect index flags and compare worktree versus HEAD blob identities for
    the two artifacts before applying any file repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:32:01Z
  TYPE: BLOCKER
  CLAIM: The current path scan finds 74 machine-path lines in the tracked
    spellbook typecheck artifact, 19 in the tracked DevOps scan artifact, and
    16 historical/path-evidence lines in this untracked task. Both artifact
    files match current HEAD, so this is reachable-history residue rather than
    only a dirty-worktree restoration issue.
  EVIDENCE:
  - `artifacts/spellbook_typecheck_report.txt:1-253`
  - `artifacts/dev_ops_typecheck_scan.json:1-848`
  - `tickets/tasks/2026-08-29_sanitize_publication_history_task.md`
  IMPACT: The earlier path-clean conclusion is incomplete for at least the
    current branch; final publication safety is blocked until affected refs and
    replacement-rule coverage are identified.
  NEXT: Scan HEAD, every branch, remote-tracking refs, and stash for the exact
    two tracked artifact path forms before selecting the narrow rewrite repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:30:27Z
  TYPE: BLOCKER
  CLAIM: The current untracked sanitation tickets were restored after the
    history rewrite and may still contain machine-layout placeholders; one new
    recovery-evidence line also briefly used an absolute local path. That line
    is corrected to `<external-recovery>`, but the full worktree still requires
    a targeted path scan before publication safety can be claimed.
  EVIDENCE:
  - `tickets/tasks/2026-08-29_sanitize_publication_history_task.md`
  IMPACT: Reachable Git history remains clean, but uncommitted files are part of
    the future public tree and must meet the same path-redaction gate.
  NEXT: Scan every non-ignored current-worktree file for local path forms and
    replace only verified machine-layout residues with neutral placeholders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:28:43Z
  TYPE: MEASURE
  CLAIM: Approved local reflog expiry and immediate garbage collection completed.
    Full strict fsck passes, unreachable-object count is zero, live stash ref
    remains `32b42abcca699ab52e7c438e7229f0853f8598fa`, and packed history is
    36.83 MiB with zero loose or garbage objects.
  EVIDENCE:
  - `.git`
  IMPACT: Removed private/unreachable history is no longer retained by local
    reflogs or loose objects; rollback remains in the external verified bundle.
  NEXT: Rerun final forbidden-path/text, build-asset, ref, status, and remote
    configuration scans against the pruned repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:27:52Z
  TYPE: FACT
  CLAIM: Both unreachable commits are the worktree/index pair of one July 1
    stash entry and modify only `.gitignore`. Their root-anchored `MANIFEST`,
    sealed-skill, competitor, and cache-ignore intent is present and further
    refined in current HEAD. No ref contains either commit; current `refs/stash`
    remains the rewritten pre-publication sanitation stash.
  EVIDENCE:
  - `.gitignore:25-31`
  - `.gitignore:189-226`
  - `.git`
  IMPACT: Expiring the old stash reflog entry and pruning its unreachable object
    pair removes no unique source, ticket, configuration intent, or live stash.
  NEXT: Expire all local reflogs and run immediate local Git garbage collection,
    then require zero unreachable objects and a successful full fsck.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:26:49Z
  TYPE: FACT
  CLAIM: The external all-ref recovery bundle still verifies as complete at
    53,449,164 bytes with SHA-256
    `bb0124e23210065696500adbd9fe9e36459ef7ecb1cdda2153ae13cf189fd27c`.
    Current rewritten branch and stash refs are intact. Pre-prune fsck finds two
    unreachable commits (`80f63ebe...` and `cf365805...`) plus their trees/blobs;
    the reflogs contain two unique commits.
  EVIDENCE:
  - `<external-recovery>/melder_private_all_refs.bundle`
  - `.git`
  IMPACT: Rollback remains independently available, but both unreachable commits
    must be inspected before the approved prune boundary removes them.
  NEXT: Read both unreachable commit identities and diffs plus the reflog entries,
    then classify whether either contains unique user work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:25:59Z
  TYPE: MEASURE
  CLAIM: All five verified validation-generated roots were removed and each
    exact absolute path now reports absent. No source, durable build asset,
    ticket, stash, or external recovery path was targeted.
  EVIDENCE:
  - `.publication_validation_dist`
  - `.publication_validation_extract`
  - `.publication_validation_install`
  - `.pytest_sanitization_tmp`
  - `src/melder.egg-info`
  IMPACT: The working tree no longer carries package/test validation output.
    The removed archives are reproducible from the recorded build command and
    hashes; they were never committed or published.
  NEXT: Inventory reflogs and unreachable objects, then run the approved local
    reflog-expiry and garbage-collection boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:25:27Z
  TYPE: FACT
  CLAIM: Cleanup targets are resolved and proven inside the repository. The
    three `.publication_validation_*` roots were created during this validation
    pass and contain 2,268 files totaling about 62.5 MB; the failed pytest root
    is empty; `src/melder.egg-info` was created by the build with four files.
    Root `build/` is already absent. None of the five present roots is tracked.
  EVIDENCE:
  - `.publication_validation_dist`
  - `.publication_validation_extract`
  - `.publication_validation_install`
  - `.pytest_sanitization_tmp`
  - `src/melder.egg-info`
  IMPACT: These exact validation-generated roots can be removed without touching
    source, restored user work, durable build assets, or recovery material.
  NEXT: Remove only the five verified present roots and prove each is absent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:24:48Z
  TYPE: MEASURE
  CLAIM: The corrected isolated-wheel smoke passes. It imports version 0.1.2
    from the validation target, verifies all four packaged documents, exposes
    46 architecture and 136 component sections, walks a 1,224-node/1,452-edge
    graph, and retains 452 agent-documentation entries plus 628 bind-guard entries.
  EVIDENCE:
  - `.publication_validation_install/melder/__init__.py`
  - `src/melder/utilities/ai_native_support_tools/system_document_view.py:260-289`
  IMPACT: The built wheel installs and its runtime plus durable documentation
    assets function independently of the source checkout.
  NEXT: Inventory and remove only validation-generated directories, then expire
    rewritten reflogs, prune unreachable objects, and run final integrity scans.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:23:59Z
  TYPE: BLOCKER
  CLAIM: The first installed-wheel smoke reached the packaged graph and passed
    all preceding import, version, document-integrity, and asset-count assertions,
    then failed because the validation script guessed a `Node.source_path`
    attribute that the public `Node` record does not expose. This is a smoke-test
    assertion defect, not a wheel failure.
  EVIDENCE:
  - `src/melder/utilities/ai_native_support_tools/system_document_view.py:1040-1063`
  IMPACT: Installed-wheel validation remains incomplete until the real `Node`
    record schema is read and the assertion is rerun against its public field.
  NEXT: Read the `Node` record definition, correct only the smoke assertion, and
    rerun the isolated installed-wheel test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:22:37Z
  TYPE: MEASURE
  CLAIM: Offline pip installation of the built wheel into the dedicated local
    validation target completed successfully with no dependency or index access.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pip install --no-deps --no-index --no-compile --target .publication_validation_install .publication_validation_dist/melder-0.1.2-py3-none-any.whl`
  IMPACT: Wheel layout and installation metadata are consumable by pip on the
    supported Python 3.14 interpreter.
  NEXT: Import exclusively from the validation target and verify version,
    document integrity, entry counts, and graph access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:22:02Z
  TYPE: RISK
  CLAIM: The 32 packaged tooling references split cleanly: 18 are required or
    harmless source provenance in wrapper/builder/manifest module text; 14 are
    inside the public architecture/components document bodies. Those 14 are
    non-secret indexing commands or historical patch-lane pointers to paths not
    shipped in the wheel, so they are dead process text for installed users and
    violate the system-document output contract.
  EVIDENCE:
  - `src/melder/_build_assets/_system_documents/_builder.py:1-220`
  - `context_compass/system_docs/src_architecture.md:33-115`
  - `context_compass/system_docs/src_components.md:22-107`
  - `context_compass/system_docs/src_components.md:8246-8370`
  IMPACT: This is a pre-existing public-document polish defect, not private-data
    exposure and not justification to remove any build asset. Correcting it needs
    a separately confirmed authored-doc edit plus deterministic regeneration.
  NEXT: Complete installed-wheel smoke and final repository integrity validation;
    report the 14 dead process references as a pre-release follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:20:05Z
  TYPE: MEASURE
  CLAIM: Root-aware inspection passes for both release formats. The wheel has
    599 unique safe members; the sdist has 768. Both have zero unexpected roots,
    forbidden root lanes, unsafe paths, cache/database/profile-output extensions,
    or private-content matches. All seven required build assets are present.
  EVIDENCE:
  - `.publication_validation_dist/melder-0.1.2-py3-none-any.whl`
  - `.publication_validation_dist/melder-0.1.2.tar.gz`
  IMPACT: The built distributions do not contain the removed private lanes or
    machine-local/GTM content. Their SHA-256 hashes are recorded by the validation
    output for reproducibility.
  NEXT: Classify the 32 non-private ContextCompass/tool-path references before
    treating archive-content review as complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:20:05Z
  TYPE: UNKNOWN
  CLAIM: Extracted archive text contains 32 references to ContextCompass or its
    system-document tooling. Initial samples span shipped builder provenance,
    source-path metadata, and authored payload instructions. They are not private
    content, but their intended public-release status is not yet classified.
  EVIDENCE:
  - `.publication_validation_extract/wheel/melder/_build_assets/_system_documents/_builder.py`
  - `.publication_validation_extract/wheel/melder/_build_assets/_system_documents/payloads/src_architecture_payload.py`
  IMPACT: Publication safety passes, but documentation polish may still carry an
    internal-tooling leak prohibited by the system-document authoring contract.
  NEXT: Map all 32 matches to source files and distinguish required build logic
    from process references embedded in public document payloads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:18:14Z
  TYPE: MEASURE
  CLAIM: Valid escalated archive inspection finds 599 unique wheel members and
    768 unique sdist members. Every wheel member is under `melder/` or dist-info,
    and all seven required durable asset manifests/payloads are present. The
    initial forbidden-name predicate overmatched legitimate runtime directories
    named `profiles` and `artifacts`; its 39/54 hit counts are not publication
    findings. The sdist's two other root results are directory entries only.
  EVIDENCE:
  - `.publication_validation_dist/melder-0.1.2-py3-none-any.whl`
  - `.publication_validation_dist/melder-0.1.2.tar.gz`
  IMPACT: Archive structure and durable build-asset inclusion pass. Sensitive
    path checks must be root-aware so valid product modules are not misclassified.
  NEXT: Apply root-aware member predicates, extract both archives, and scan all
    text content for private path and publication-boundary terms.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:17:21Z
  TYPE: BLOCKER
  CLAIM: The sandbox cannot reopen either archive created by the unsandboxed
    build: ZIP, tar, and SHA-256 reads all return access denied. The summary
    values printed after those exceptions are invalid and must not be used.
  EVIDENCE:
  - `.publication_validation_dist/melder-0.1.2-py3-none-any.whl`
  - `.publication_validation_dist/melder-0.1.2.tar.gz`
  IMPACT: Archive membership and hashes remain unverified until the read-only
    inspection runs with the same escalated filesystem access as the build.
  NEXT: Rerun archive member, metadata, asset-presence, and hash inspection with
    escalated filesystem access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:16:15Z
  TYPE: MEASURE
  CLAIM: The unsandboxed local setuptools build completed with exit code 0 and
    produced `melder-0.1.2.tar.gz` plus `melder-0.1.2-py3-none-any.whl` without
    contacting or publishing to a package index.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m build --no-isolation --outdir .publication_validation_dist`
  IMPACT: Both release archive formats exist for exact member inspection. The
    sandbox build blocker is cleared.
  NEXT: Enumerate both archives, verify their metadata and durable build assets,
    and reject forbidden/private member families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:15:34Z
  TYPE: BLOCKER
  CLAIM: The local no-isolation package build reached the setuptools backend but
    failed before archive creation because the sandbox denied writes to build's
    global temporary hook directory. This is the same Windows temp ACL boundary
    already proven by pytest, not a packaging configuration failure.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m build --no-isolation --outdir .publication_validation_dist`
  IMPACT: Archive validation requires one unsandboxed build invocation; no source
    or packaging configuration change is justified.
  NEXT: Rerun the identical local build with escalated filesystem access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:15:04Z
  TYPE: FACT
  CLAIM: Packaging uses `setuptools.build_meta`; wheel discovery is explicitly
    rooted at `src`, includes only `melder*`, and excludes repository support
    lanes. No `MANIFEST.in`, `setup.cfg`, or `setup.py` exists, so source-archive
    composition must be proven from the built archive rather than inferred.
  EVIDENCE:
  - `pyproject.toml:1-3`
  - `pyproject.toml:131-173`
  IMPACT: The wheel boundary is explicit, while the sdist boundary remains a
    validation question until its member list is inspected.
  NEXT: Build wheel and sdist locally without publication, then reject any
    private, generated-result, cache, or competitor-source member.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T23:14:18Z
  TYPE: MEASURE
  CLAIM: The unsandboxed supported-tier run completed successfully with
    10,959 passes, 28 skips, 15 expected failures, one unexpected pass, and
    exit code 0 in 201.62 seconds. A trailing unawaited-coroutine warning did
    not change the pytest result.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pytest -q tests/unit tests/component tests/integration`
  IMPACT: The sandbox ACL blocker is cleared and the sanitized repository passes
    all supported unit, component, and integration tiers.
  NEXT: Build wheel and source archives in an isolated output directory and
    inspect their contents before final Git cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:58:53Z
  TYPE: BLOCKER
  CLAIM: A second unchanged supported-tier run with repository-local
    `--basetemp` is also ACL-blocked. The sandbox creates the directory but
    denies enumeration to pytest and even denies `Get-Acl`; pytest crashes in
    tmp-path setup/session cleanup. This proves path selection is not the cause.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pytest -q --basetemp=.pytest_sanitization_tmp tests/unit tests/component tests/integration`
  - `.pytest_sanitization_tmp`
  IMPACT: Supported-tier validation requires one unsandboxed run. No source or
    test fixture change is justified.
  NEXT: Run the exact three tiers with escalated filesystem access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:56:04Z
  TYPE: MEASURE
  CLAIM: The first supported-tier run produced 10,775 passes, 27 skips,
    15 xfails, one xpass, and 185 setup errors. The error traces share one
    external cause: pytest cannot scan the sandbox-blocked global temp root
    `<local-path>\AppData\Local\Temp\pytest-of-Mark`. No test assertion
    failure was reported.
  EVIDENCE:
  - `.venv_new/Scripts/python.exe -m pytest -q tests/unit tests/component tests/integration`
  IMPACT: The result does not evidence a code or sanitation regression. Rerun
    unchanged tests with a repository-local writable `--basetemp`.
  NEXT: Run the same three tiers with `--basetemp=.pytest_sanitization_tmp`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:52:34Z
  TYPE: MEASURE
  CLAIM: Owner-approved build-asset regeneration and `--check` pass for all
    three assets. Exact diff inspection confirms only two
    `SOURCE_SHA256` lines changed. Agent documentation remains 452 entries,
    bind guard remains 628 entries, and system documents remain four entries.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:20-27`
  - `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:15-22`
  IMPACT: No asset, entry, or runtime source was removed or semantically changed.
  NEXT: Run the supported unit/component/integration test tiers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:49:39Z
  TYPE: FACT
  CLAIM: Build-asset validation reports source-fingerprint mismatches for
    `_agent_documentation` and `_bind_guard`; `_system_documents` is
    current. The untouched recovery clone at original prod fails identically, and
    the sanitized prod source tree is 600/600 files with zero changed blobs.
  EVIDENCE:
  - `src/melder/_build_assets/_build_asset_runner.py:268-350`
  - `git -C <backup-recovery-probe> diff prod -- src/melder`
  - `git -C . diff <original-prod>..prod -- src/melder`
  IMPACT: This is a pre-existing raw-byte fingerprint mismatch, not evidence that
    the manifest entries or semantics are stale. Refreshing it changes only the
    two stamped `SOURCE_SHA256` values and does not alter runtime source.
  NEXT: Regenerate all durable build assets deterministically and require a clean
    `--check`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:51:55Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner clarified that deterministic regeneration is approved; the
    objection was concern that the agent-documentation or bind-guard assets were
    being removed. They are not removed. The verified diff changes only two
    fingerprint strings while preserving 452 and 628 entries respectively.
  EVIDENCE:
  - `src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py:20-26`
  - `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:15-21`
  IMPACT: Reapply the fingerprint refresh, verify the two-line-only diff, and
    continue validation. Do not characterize the asset content as stale.
  NEXT: Regenerate, check, and inspect the exact diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:48:12Z
  TYPE: MEASURE
  CLAIM: Post-rewrite Gitleaks scanned 141.23 MB across 2,056 commits and
    reports only the previously verified false positive: a historical
    `self.<attribute>` assignment with no string literal or quotes. No verified
    secret remains. Large-blob inventory has 31 blobs at or above 500 KB and zero
    forbidden database/profile/result/snapshot families.
  EVIDENCE:
  - `git -C . log -p -U0 --full-history --all`
  - `git -C . rev-list --objects --all`
  - `git -C . cat-file --batch-check`
  IMPACT: Secret and binary-history gates pass. Remaining large blobs are
    intentional ContextCompass question/system maps and Melder generated system
    document assets.
  NEXT: Validate build assets and repair only deterministic staleness caused by
    approved text redaction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:48:12Z
  TYPE: MEASURE
  CLAIM: Rewritten history retains 2,107 prod commits and all three prod authors.
    `git fsck --full --no-reflogs` exits successfully with one unreachable
    dangling commit; it will be removed by final reflog expiry/GC after all
    recovery checks. Packed history is 37.03 MiB, down from 63.34 MiB.
  EVIDENCE:
  - `git -C . fsck --full --no-reflogs`
  - `git -C . rev-list prod --count`
  - `git -C . count-objects -vH`
  IMPACT: Useful engineering history and authorship are preserved while obsolete
    private/output history is removed.
  NEXT: Run build-asset checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:46:34Z
  TYPE: MEASURE
  CLAIM: The narrow second text pass completed and all publication-text gates
    now pass across history, commit/tag messages, and the prod tree: zero Mark
    home paths, zero `PycharmProjects` workspace prefixes, zero GTM document
    names/terms, zero retired private-package names, and zero exact private
    instruction headings. Generic `Missions` component and `Mission Recall`
    policy headings were verified unrelated and retained.
  EVIDENCE:
  - `git -C . log --all --regexp-ignore-case -G <forbidden-patterns>`
  - `git -C . grep -I -E -i <forbidden-patterns> prod`
  - `git -C . log --all --format=%H%x09%s%x09%b`
  IMPACT: The residual machine-layout blocker is resolved without removing any
    additional path, ticket, or runtime source file.
  NEXT: Rerun Gitleaks and Git integrity, then validate build assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:42:35Z
  TYPE: BLOCKER
  CLAIM: Forbidden-path and commit-message validation passed, but the first text
    rule was case-sensitive and replaced only the username prefix. Historical
    tickets still contain lowercase-drive and neutral-prefix forms such as
    `<local-path>/PycharmProjects/melder_private`. This is machine-layout
    residue, not a credential.
  EVIDENCE:
  - `git -C . grep -I -n -E -i PycharmProjects prod`
  - `git -C . log --all --regexp-ignore-case -G PycharmProjects`
  IMPACT: The text-sanitization exit gate is not yet met. A narrow second
    replacement pass is required; no further path/ticket removal is justified.
  NEXT: Collapse explicit Mark/PycharmProjects and existing neutral-prefix
    workspace forms to `<local-workspace>`, then rerun all text scans.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:41:01Z
  TYPE: MEASURE
  CLAIM: All 46 removal rules have zero matches across 9,450 reachable unique
    paths. Rewritten `prod` has 4,284 files versus 4,453 before: exactly 169
    approved current-tip removals, zero additions, and 45 content replacements.
    The 45 modified survivors are 44 ContextCompass prose/artifact files and one
    build-asset test; no runtime source file changed.
  EVIDENCE:
  - `git -C . rev-list --objects --all`
  - `git -C . ls-tree -r prod`
  - `git -C <backup-recovery-probe> ls-tree -r prod`
  IMPACT: The rewrite removed only approved current content and applied only the
    planned local-path/GTM redactions. Canonical Melder runtime source is
    byte-identical at the prod tip.
  NEXT: Prove forbidden text absence, rerun Gitleaks, and run Git integrity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:38:57Z
  TYPE: MEASURE
  CLAIM: The approved local rewrite completed over 2,279 commits/refs and
    repacked successfully. New local heads are
    `codex_features2=a67be58b02db2a3df65ae3eca0b71047a5e1463a` and
    `prod/dev/preprod=5708a852e7707a1fd4e3bbb91b489b6a34f15246`.
    The three skipped Codex tree refs were deleted after backup; every sampled
    forbidden path family now has zero reachable objects.
  EVIDENCE:
  - `git -C . for-each-ref refs/heads refs/stash`
  - `git -C . rev-list --objects --all`
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/filter_manifests/remove_paths.txt`
  IMPACT: Private SQLite storage, named strategy/persona files, legacy agent
    trees, profiles, experiments, and raw benchmark result histories are no
    longer reachable from local refs.
  NEXT: Complete forbidden-text, equivalence, secret, integrity, build, test, and
    package validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:38:57Z
  TYPE: FACT
  CLAIM: Allowed dirty state is restored without a commit. The tracked recovery
    patch restored the workflow deletion, attention/mailbox edits, and 101
    pre-existing patch-document EOL deltas. The two audit tasks and profiling
    results ignore file were restored from the rewritten stash and verify against
    their stash blobs after Git clean filtering. The 22 generated result files
    remain in the external backup hold and are intentionally absent.
  EVIDENCE:
  - `git -C . status --short --branch`
  - `git -C . stash show --include-untracked stash@{0}`
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/generated_results_hold`
  IMPACT: The rewrite preserved substantive uncommitted work while completing the
    approved profile/result removal.
  NEXT: Validate the rewritten repository before any owner handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:31:08Z
  TYPE: BLOCKER
  CLAIM: The first stash attempt wrote nothing and failed with
    `could not write index`. There is no `.git/index.lock`, the index is
    writable, and the only Git process is this repository's long-running built-in
    fsmonitor daemon. `core.fsmonitor=true` is the remaining evidenced index
    writer/extension candidate.
  EVIDENCE:
  - `.git/index`
  - `.git/config:1-12`
  IMPACT: Do not rewrite while the working tree cannot be stashed. Stop the
    built-in daemon through Git, disable its index extension temporarily, and
    require a successful stash plus clean status.
  NEXT: Stop fsmonitor, set `core.fsmonitor=false`, clear the fsmonitor index
    extension, and retry the stash.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:30:01Z
  TYPE: FACT
  CLAIM: Pinned `git-filter-repo` 2.47.0 is installed only in the external
    backup directory and verified by version/hash. The removal manifest has 46
    rules, every rule matches historical paths, and text/message manifests have
    seven and nine replacement rules. `--analyze` completed over 2,276 commits,
    19,867 filenames, and approximately 1.09 GB unpacked blob history.
  EVIDENCE:
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/filter_manifests/remove_paths.txt`
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/filter_manifests/replace_text.txt`
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/filter_manifests/replace_messages.txt`
  - `.git/filter-repo/analysis/README:1-20`
  IMPACT: The rewrite is deterministic and bounded to approved paths/text. No
    manifest rule is dead or guessed.
  NEXT: Stash the verified dirty state, prove the repository is clean, then run
    the single local rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:26:05Z
  TYPE: MEASURE
  CLAIM: Recovery material is verified. The all-ref bundle is 53,449,164 bytes,
    passes `git bundle verify`, and recreates original `prod`
    `660359fb97b0da1bdc94b540f7e1f04844b6b4cd`. The tracked binary patch is
    468,532 bytes; all three untracked files were copied and hash-verified.
    A long-path-enabled recovery checkout succeeds. Its 101 dirty files are the
    same known CRLF/LF-only patch-document delta, not missing data.
  EVIDENCE:
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/SHA256SUMS.txt`
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/refs_before.txt`
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/status_before.txt`
  IMPACT: The destructive entry gate is satisfied. Original Git objects and dirty
    working state can be recovered independently.
  NEXT: Generate exact filter manifests, stash the working tree, install temporary
    tooling, and run the local rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:24:59Z
  TYPE: RISK
  CLAIM: The Git bundle passed `git bundle verify`, but the first recovery
    probe clone failed during checkout because the new clone did not inherit
    `core.longpaths=true`. Melder has legitimate paths beyond the default
    Windows checkout limit. No rewrite has started.
  EVIDENCE:
  - `<local-path>/PycharmProjects/melder_private_sanitization_backup_20260829T222319Z/melder_private_all_refs.bundle`
  IMPACT: Recovery must be reproven with a no-checkout clone, long paths enabled,
    and an explicit checkout before the entry gate can open.
  NEXT: Remove only the failed probe, clone without checkout, enable long paths,
    checkout `prod`, run `git fsck --full`, and verify the original prod SHA.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:23:19Z
  TYPE: FACT
  CLAIM: The approved target is dirty and carries user state that must survive
    rewriting: one staged workflow deletion, staged profile deletions, many tracked
    ContextCompass patch-document modifications, two untracked audit tasks, one
    untracked profiling-results ignore file, and a pre-existing stash ref.
  EVIDENCE:
  - `git -C . status --short --branch`
  - `git -C . ls-files --others --exclude-standard`
  - `git -C . for-each-ref refs/stash`
  IMPACT: History rewriting cannot start until both committed history and dirty
    working state have independently verified recovery material.
  NEXT: Create a full Git bundle, binary worktree patch, and untracked-file archive
    outside the repository, then verify each.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
History, security, and build-asset validation pass. Both sandboxed supported-tier
runs are ACL-blocked regardless of temp location; run once with escalated filesystem
access, then continue with package and final garbage-collection validation. No commit,
push, remote mutation, visibility change, or PyPI publication is authorized.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
