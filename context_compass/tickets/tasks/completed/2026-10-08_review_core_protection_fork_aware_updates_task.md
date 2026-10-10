# Task: Review core protection and fork-aware selective updates

## Metadata
- Task ID: TASK-2026-10-08-review_core_protection_fork_aware_updates
- Task type: REVIEW / design decision, not implementation
- Story: none (standalone owner-requested review)
- Status: done
- Owner: claude (assigned by the owner 2026-10-10; review and investigation only)
- Agent Name: melder_1 (review from 2026-10-10), dot (investigation and ticket preparation)
- Priority: p2
- Created: 2026-10-08T20:45:00Z
- Updated: 2026-10-10T13:44:41Z

- Completed: 2026-10-10T13:44:41Z
- Summary: Review handed back and accepted by the owner (2026-10-10): F1-F6 verified at 66939dfe8, the
  governed-evolution contract (C1-C6) with the D1-D8 mapping, a characterization suite holding D-10 and D-11
  under strict xfail, and three defects (D-10, D-11, D-20) kept open in backlog tickets of their own. No source
  changed; nothing committed or pushed. Evidence: artifacts/core_protection_review_20261010/.

## Objective
Review a default read-only core policy and a deliberate, lineage-preserving fork workflow for
Melder/MelderOps evolution, with agent-selected upstream changes handled by a custom research-branch
updater using ordinary package tooling where appropriate. Decide boundaries and acceptance tests
before changing implementation or architecture.

This is not a proposal to fork pip. Installation location alone is not the intended protection.
The Phase 1 baseline scope is unaffected. This ticket does not amend the architecture automatically.

## Owner Direction and Review Status
The owner requested a ticket covering this discussion, placed beside the earlier scan-bind ticket.
The design direction to review is:
- Agents can read the core; core-changing operations are denied by default through the applicable ACL.
- Deliberate core evolution means creating a fork and retaining its lineage.
- An agent selects which upstream changes to take into that fork through a custom research-branch
  updater, rather than treating every upstream release as an automatic replacement.
- Use pip's existing controls where useful; do not fork pip or reduce the design to installation paths.
These are requirements for this review, not claims that the proposed system is already implemented.
Source: owner conversation, ticket request Sentinel_7735a734e1308191ab903636993a377e and preceding discussion.

## Context / Source Baseline
- Repository: https://github.com/Synaptic724/melder
- Branch: codex_features2
- Reviewed SHA: 66939dfe84e41e51f41f4bc4461ad1690907e909
- Remote branch HEAD matched this SHA during the 2026-10-08 investigation.
- Checkout: /workspace/shared/melder-scan-bind-20261008
- Companion ticket: 2026-10-08_restore_scan_bind_option_parity_task.md in this directory.
- Review uses context_compass/templates/task_template.md; onboarding was explicitly waived for this
  investigation/ticket request. No standing onboarding-policy change is implied.

## Ticket Contract
- ENTRY_GATE: Assign a reviewer, read the evidence and latest notes, and add an active board row before
  commencing the review. Obtain owner decisions where flagged. Implementation requires a separate
  explicit authorization and approved scope; this ticket authorizes neither deployment nor publication.
- EXECUTION_BOUNDARY: Review discovery/classification, existing guarded binding, applicable command/ACL
  surfaces, mutation-research lineage, and package update boundaries. Produce decisions and a bounded
  follow-on implementation plan. Current work only creates this ticket and its downloadable copy.
- DEPENDENCIES: Pinned source baseline; owner-defined core boundary; actual Phase 1 baseline and
  architecture documents must be identified during review before proposing amendments.
- EXIT_GATE: Owner accepts the boundary matrix, lineage/update design, open decisions, and proposed
  verification plan. Any implementation work is routed to separately approved tasks.
- FAILURE_ESCALATION: Record DECISION_REQUEST for ambiguous core/fork/branch meaning; CONFLICT for
  incompatible existing runtime contracts; BLOCKER for unavailable enforcement or provenance. Do not
  substitute path heuristics for authorization or claim an unverified end-to-end protection.

## Scope Boundaries
- In scope now: preserve source findings, owner direction, options, risks, and review acceptance criteria.
- In scope for later review: distinguish existing mechanisms from missing ones; decide exact enforcement
  and lineage requirements; evaluate a selective updater without building or invoking it.
- Out of scope: source fixes, permission changes, package installs/upgrades, creating actual forks,
  activating research lanes, changing Phase 1, automatically editing architecture, commits, pushes,
  PRs, issue publication, or a broad security audit.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-10T13:44:41Z) the owner accepted the review and its direction (Note 25); the hand-back
  carries the tested revision, environment, results, D1-D8 disposition and follow-ups, and D-10, D-11 and D-20
  stay open in backlog tickets of their own (Notes 26-29). No implementation, commit or push.
- previous: in_progress -> review (2026-10-10T12:36:19Z) the governed-evolution contract (C1-C6), the D1-D8
  mapping and the commit grouping are written (Notes 18-23), with a third defect found (D-20, Note 20);
  specification only - no src, ACL or configuration change, no commit or push.
- previous: review -> in_progress (2026-10-10T12:06:36Z) the owner asked for the review to become a concrete
  governed-evolution contract before any implementation (Note 17); specification only - no implementation,
  commit or push.
- previous: in_progress -> review (2026-10-10T11:52:03Z) the review deliverables are in place (Notes 7-15):
  F1-F6 verified with two codegen gaps found, the D3 probe reproduced, the regression suite the owner asked
  for (GIL off), the boundary matrix, the D1-D8 decision request and the verification plan.
- previous: ready -> in_progress (2026-10-10T11:03:11Z) scan_bind_option_parity reached review, which was
  this lane's start condition (Note 5). Review only: verify the findings, run the D3 probe, write the
  decision request.
- previous: draft -> ready (2026-10-10T08:41:57Z) the owner added this ticket to the board, assigned it to
  melder_1 and directed "go ahead and investigate the findings and fix them" (chat, 2026-10-10); for this
  review ticket that authorizes the investigation, and the core-protection design waits on D1-D8.
- previous: draft -> draft (2026-10-08) New review proposal recorded at owner request; no review
  acceptance or implementation authorization exists. Passing baseline tests do not complete the
  proposed design.

## Confirmed Findings

### F1. Crystallizer normally stops recursive analysis at installed dependencies
CrystallizerConfiguration defaults site_package_dependency_descent to False and threads it through
SpellCrystal into CrystalAnalyzer. The walk still records site-package modules as leaves, including
paths; it skips their source fact extraction and interior dependencies. Setting the knob True restores
the interior walk. Raw internal analyzer/SpellCrystal construction retains True for compatibility.
This is an analysis-depth policy, not removal from Python's import path or a filesystem sandbox.
Evidence: E1-E3.

### F2. Default cwd classification can encompass a local virtual environment
Default user_source_root_paths is resolved cwd. The strategy chain tries synthetic, then user_source,
then site_package, then unknown, returning the first match. User-source matching is resolved path
containment without a .venv exclusion. A .venv inside cwd can therefore win user-source classification
and descend even when site_package_dependency_descent=False.
Verified nonmutating probe in this checkout: installed pytest under .venv/lib/python3.14t/site-packages
classified user_source with descends=True for cwd roots; narrowing roots to cwd/src produced
site_package with descends=False. This is not evidence that all deployments use such roots.
Evidence: E4-E6; reproduction below.

### F3. Discovery is rooted in a bound object's module, not a general directory search
SpellCrystal resolves the target module through sys.modules/inspect and the analyzer resolves paths
through a live __file__ or importlib.util.find_spec. Source imports drive graph traversal. Configured
user roots classify ownership; they do not add sys.path entries or grant access. Explicitly supplying a
root module/path to the internal analyzer does not turn classification into an authorization mechanism.
Evidence: E7-E8.

### F4. Recorded leaf source can remain visible through MutationResearch
source_view restricts a requested module to the crystal's module_targets. It then uses retained text
or reads the recorded module_to_path from disk. This fallback has no site-package-kind exclusion.
Thus descent-off does not mean that recorded installed-module source is unreadable. This is a read
behavior, not proof that a mutation is authorized or that arbitrary files can be selected by source_view.
Evidence: E9-E10. Preserve useful read access in the proposed core policy.

### F5. Existing internal binding guard is a separate boundary
Bind.assert_allowed rejects exact (module, qualname) entries in INTERNAL_MANIFEST as registration
targets. It explicitly distinguishes registration from use and does not walk inheritance. This is not
an installed-package write lock or proof of the proposed MelderOps ACL policy. Review how this existing
guard should coexist with deliberate core-fork evolution; do not assume it should be bypassed.
Evidence: E11.

### F6. Native research lanes exist and are not Git branches
The current ResearchSet.create_lane can anchor a new empty lane to a specified existing node, recording
ancestry without copying/moving content. ResearchLane describes full-object version records and states
that membership has zero runtime footprint; runtime residency is independent. Treat the owner's
“research branch” as potentially this Melder-native concept. Do not silently translate it into a Git
branch. Mapping native lanes, source-control forks, and distribution artifacts is an open design decision.
Evidence: E12-E13.

## Boundary Matrix to Decide
1. Discovery/read: Crystallizer analysis depth, source classification, source_view, descriptors, and
   dependency inspection. Reads should remain available subject to existing access rules.
2. Supported runtime object mutation: identify the actual authorized commands and ACL checks involved
   in introducing/selecting/activating core-derived candidate objects. A research-lane edit alone does
   not activate code. Define deny-by-default core changes and explicit fork authority at those seams.
3. Source edits: direct changes to repository or installed .py files are external filesystem actions.
   A Melder ACL cannot be assumed to stop a separate shell/editor/process with write permissions.
   State the threat model and OS/process boundary if protecting against such writers is required.
4. Installed distribution updates: pip or another installer changes environment contents. Treat this
   as a separately authorized update operation; a runtime ACL alone does not constrain the installer.
5. Fork lineage: distinguish parent source revision, native anchor/node identities, local adaptations,
   chosen upstream changes, produced artifact digest, and currently running version. Decide which
   identities are mandatory and how drift or missing lineage prevents promotion.

## Boundary Matrix (review result, melder_1, 2026-10-10)
Each row: what is possible today, who enforces it, what is unprotected, and the evidence. Verified against
66939dfe8 (these files unchanged in the working tree); tests named here are the suite of Notes 12-13.

1. Discovery and read
   - Today: the Crystallizer classifies each walked module synthetic -> user_source -> site_package ->
     unknown, first match; the default user root is the working directory and descent is off, so a `.venv`
     inside the working directory is user source - walked, fingerprinted, and retained when retention is
     on. MutationResearch reads any module of a recorded world, recorded text first, else the live disk,
     with no kind check (installed leaves included); a module outside the recorded world is an honest miss.
     Capability rooms carry the research reads and codegen rooms the whole research family; both pass room
     type and RiftGate admission only, never a frame ACL.
   - Enforcement owner: none. Classification is analysis policy, not authorization.
   - Unprotected: codegen `open(...)` reads any file the process can read, under every profile (Note 10).
   - Evidence: Notes 7-10; tests: custody characterization, recorded leaf source read.
2. Supported runtime mutation
   - Today: registering a `melder.*` class is refused by exact `(module, qualname)` match - registration
     only; subclasses and identities under another package name pass. The command system enforces the
     frame's compiled command ACL on its direct frame, conduit and spell fetch paths, and the codegen
     profiles declare rules for topology verbs (link, unlink, create lesser, transfer) and for spell
     invoke and attribute writes. Research organization (lanes, join, synthesize) runs in codegen rooms
     without a frame ACL and has zero runtime footprint: no lane act changes a selection.
   - Enforcement owner: Bind's guard with the committed manifest; the Nexus frame ACL compiled surfaces;
     the Conduit transaction verbs for selection changes.
   - Unprotected or UNKNOWN: how far the codegen profile's conduit and spell rules reach inside executed
     code, whether safe codegen reaches selection-changing verbs (bind, notch, add to or remove from an
     index) through its namespace objects, and whether materialize_codegen can publish a SyntheticModule
     under a `melder.*` name were not probed.
   - Evidence: Notes 9 and 11; tests: registration guard identity, research lane isolation.
3. Source writes (repository or installed `.py` files)
   - Today: Melder enforces nothing. Agent code writes files through `open` under every codegen profile,
     safe included; through pathlib under hybrid, permissive and full_access; through os, shutil and
     subprocess under permissive and full_access; and hybrid's denied roots load through `__import__`.
     Out-of-process writers (a shell, an editor) are outside any Melder ACL by nature.
   - Enforcement owner: none in Melder; only the process's OS file permissions.
   - Unprotected: all of it.
   - Evidence: Notes 10-11; tests: codegen core boundary (two strict xfails).
4. Installed distribution updates
   - Today: pip and other installers are outside Melder. In process, subprocess is importable under
     permissive and full_access and through `__import__` under hybrid and precision, so agent code can run
     an installer.
   - Enforcement owner: none in Melder; environment permissions.
   - Unprotected: all of it.
   - Evidence: Notes 10-11.
5. Fork lineage
   - Today: native lanes record ancestry (anchor lane id and node identity); the journal is forward-only
     with no merge, rebase or checkout; nodes are keyed by binding SHA256; crystals carry user-source
     fingerprints and site-package distribution provenance (identity, never text). Nothing records a git
     revision, a fork base, selected upstream changes or a produced artifact digest, and the guard keys on
     names, so a renamed fork is invisible to it.
   - Enforcement owner: MutationResearch (native lineage) and the Crystallizer (custody identity); nothing
     for source control or packages.
   - Evidence: Note 9; tests: research lane isolation, registration guard identity.

## Proposed Workflow for Review (Not Implemented)
- Identify the protected core by an explicit ownership/identity policy; use installation location as
  supporting evidence only. Decide treatment of editable installs, vendored code, subclasses, and plugins.
- Keep normal core access read-only at applicable mutation surfaces.
- Require a deliberate fork operation for core evolution, with immutable parent identity and recorded
  lineage. Decide whether the fork is native research state, source-control state, or a linked pair.
- Let the agent inspect upstream deltas and propose/select particular changes for the fork. Define the
  authority needed to select, apply, test, promote, and install; these are separate transitions.
- Stage candidate changes against the recorded fork base. Detect conflicts and local modifications;
  retain rejected or deferred changes in an auditable decision record.
- Validate compatibility and ownership/ACL invariants before runtime promotion or package installation.
- Record accepted upstream identities and resulting artifact/runtime identities. Define rollback and
  recovery without silently replacing the fork with an upstream package.
- If arbitrary source hunks or runtime objects are selected, pip does not perform that merge. The custom
  updater must produce a validated candidate artifact/state before ordinary installation or promotion.

## Existing pip Controls to Evaluate
These are available packaging options, not implemented Melder architecture or authorization gates.
Check the actual supported pip version during review; no packaging command was executed for this ticket.

- Pins and constraints can bound candidate versions; constraints do not themselves request installation.
  Review complete dependency coverage and separate build-dependency policy.
- An exact Git commit, a specific wheel, or a local checkout can identify the intended input. A mutable
  local checkout needs its own revision/dirty-state evidence; a branch name alone is not immutable.
- --dry-run with --report exposes a proposed install without installing. It is not a sandbox: resolution
  can fetch inputs and obtain metadata/build information. Review untrusted inputs in an appropriate
  isolated environment. A report is evidence, not a lockfile or an approval token.
- --upgrade-strategy=only-if-needed limits indirect dependency upgrades; it does not protect a directly
  requested package or preserve an independently modified fork.
- --no-deps skips dependency installation. It does not prove compatibility or protect the named package;
  review a complete compatible environment and validation such as pip check separately.
- Restrict approved artifact sources and verify hashes. Consider a controlled wheelhouse with --no-index
  and --find-links, and --require-hashes for pinned archive requirements. Hash mode is not directly
  interchangeable with VCS/local-directory requirements: build an identified wheel when that workflow
  needs artifact hashes. Integrity checks do not prove code is safe.

Official references checked 2026-10-08:
- https://pip.pypa.io/en/stable/cli/pip_install/
- https://pip.pypa.io/en/stable/topics/vcs-support/
- https://pip.pypa.io/en/stable/topics/secure-installs/
- https://pip.pypa.io/en/stable/topics/dependency-resolution/
- https://pip.pypa.io/en/latest/reference/installation-report/

## Open Decisions
- D1: Exact protected core: Melder kernel, MelderOps code, selected objects/subsystems, or a named set?
- D2: Which existing ACL/command surfaces enforce the default and which actions need new mediation?
  Inventory the supported paths before claiming a complete gate; do not assume direct Python access
  has the same boundary as an agent-facing command.
- D3: Is cwd/.venv precedence intentional? Should user roots be narrower, site roots win, or a declared
  override exist? Decide explicitly before changing classification or historical analysis behavior.
- D4: Define “fork” and “research branch” in native runtime, Git, and package terms, including translation
  rules, required lineage fields, identity validation, and persistence across restoration.
- D5: Who may create forks, select upstream changes, approve conflict resolutions, promote runtime state,
  and install artifacts? Decide grants and revocation without broadening read access into write authority.
- D6: What is the unit of a selective upgrade: package release, commit, source patch, object, or composition?
  What compatibility guarantees must remain true for mixed upstream/local versions?
- D7: How will source changes become runtime candidates/artifacts, and how are running processes migrated
  or restarted? Define safe rollback and treatment of persisted state/schema changes.
- D8: Which existing Phase 1 and architecture documents should later receive approved decisions? Record
  their identities during review; this ticket neither invents a baseline identifier nor expands scope.

## Decision Request D1-D8 (recommendations, melder_1, 2026-10-10)
One recommendation each; the owner decides. Nothing here is implemented.

- D1 protected core. Options: (a) the `melder` package as a distribution - every `melder.*` module of an
  identified artifact; (b) named subsystems; (c) per-object lists. Recommend (a), with MelderOps declaring
  its own core the same way, and the bind-guard manifest kept as the registration-level list. Location fails
  for editable and vendored installs and objects are too fine to audit; an artifact identity survives a
  fork and can be checked.
- D2 enforcing surfaces. Found: no existing surface denies a core change, and two codegen gaps contradict
  their profiles (Notes 10-11). Recommend, in order: (1) fix the gaps as their own tasks - deny `open` and
  the file-capable builtins under safe, and check `__import__` and other dynamic imports against the import
  policy whenever an allow or deny list exists; (2) list the protected core's top-level packages as denied
  import roots in every profile below full_access; (3) decide whether research reads pass the frame view
  ACL or are ungated by design; (4) treat in-process validation as defence in depth, not a boundary -
  protecting core files from agent code needs an OS boundary (a separate process, read-only mounts of the
  environment and the source tree).
- D3 root precedence. Options: (a) keep and document; (b) environment wins - user_source skips paths under
  the interpreter's site roots and `sys.prefix`; (c) a narrower default root such as `src/`; (d) an explicit
  exclude list. Recommend (b), documented: an environment's packages are never the user's source, yet today
  they are walked, fingerprinted and, with retention, recorded as user text under the defaults. Cost:
  existing records classify differently (fingerprint sets, drift reports), so it needs a record-version
  note, and the custody characterization tests move with it.
- D4 fork and research branch. Recommend: "research branch" means a native ResearchLane (ancestry only, no
  runtime footprint) and "fork" means a source-control fork; link them explicitly by recording on the lane
  (value-only metadata) the fork's repository identity, base revision and produced artifact digest; never
  turn a lane into a git branch implicitly. Required lineage fields: parent artifact (version plus digest or
  commit), fork base commit, local commits, selected upstream commits, produced artifact digest and the
  running selection (spell ids).
- D5 authority. Recommend separate grants: create a fork or lane (agent), propose upstream selections
  (agent), approve conflict resolutions (owner), promote a runtime selection to a production lane (owner),
  install an artifact (owner, out of band). Reads never imply any of them; each approval is journaled.
- D6 unit of a selective upgrade. Options: release, commit, source hunk, object, composition. Recommend the
  upstream commit, applied into the fork with ordinary git and rebuilt into a new artifact; objects and
  compositions stay the runtime and research units. Before promotion the fork's full test tiers pass and
  its records read under the current record version.
- D7 source to runtime. Recommend: build a wheel from the fork, verify its digest, install into a fresh
  environment rather than in place, and restart; carry runtime state through Crystallizer checkpoints
  (record-version gated); roll back by reinstalling the previous artifact and restoring its checkpoint. Live
  in-place replacement stays out of scope; SyntheticModule materialization remains an experiment lane.
- D8 documents. Found: no Phase 1 baseline document exists in this repository (Note 14). Recommend that the
  decisions land in src_architecture (the core definition, the codegen and ACL boundary invariants and their
  failure modes) and src_components (Crystallizer custody, codegen validation, MutationResearch lanes), with
  tests_components already carrying the suite; the owner names the Phase 1 document, probably MelderOps's,
  for the MelderOps half.

## Governed Evolution Contract (specification, melder_1, 2026-10-10; not implemented)
The owner's direction (Note 17), written as a contract. Governed evolution changes explicitly approved application
source only; installed dependencies, virtual environments, site-packages and native or binary extensions stay
outside the mutation scope and are used only through their supported interfaces. Each clause gives the
requirement, what exists today with its evidence, and the gap. MUST and MUST NOT bind a future implementation.
Nothing here is built, and building any of it needs a separately approved task.

Terms: an evolution scope is the owner-authored set of permitted roots and grants; a governed change is one
proposal carried through the permissions of C3; its change record is C4.2; the protected core is D1's answer.

### C1. Eligible application source (owner item 1)
- C1.1 Eligibility comes only from an owner-authored allowlist of permitted roots, held apart from Crystallizer
  custody roots. Custody classifies for analysis and grants nothing: it claims any path under a root - nested
  environments, native extensions, build output - and its default root is the working directory (Notes 18-19).
  An empty allowlist makes nothing eligible.
- C1.2 Each permitted-root entry records: the path, resolved strictly when the entry is created (it MUST exist and
  be a directory); the owning project or distribution identity (D1); the top-level import packages the root
  provides (for example `src/` provides `myapp`); its grants (C3); and the vendored or generated subtrees excluded
  inside it. A root is never inferred from the working directory, sys.path or the project layout.
- C1.3 A file is eligible for modification only when all of these hold: its strictly resolved path is under a
  permitted root, compared component-wise on resolved paths; no C2 exclusion matches any component; its suffix is
  `.py` (`.pyi` only if the owner adds it); its module name falls inside the root's declared packages; and it is
  not in the protected core (D1) unless the change runs in a fork scope (C3.7).
- C1.4 A module name is eligible for in-process generation only inside a generation namespace the owner declared,
  and never when it is already in sys.modules, sits under a protected core root, is a standard-library name
  (`sys.stdlib_module_names`) or is the top-level import name of an installed distribution
  (`importlib.metadata.packages_distributions()`). Today materialize_codegen accepts any identifier-legal name and
  replaces live modules (Note 20).
- C1.5 Location inside the project never establishes eligibility (owner item 1). The owner's checkout shows why:
  `.venv_new` sits at its root (Note 8), and custody would call that environment's packages user source.

### C2. Exclusions and path checks (owner item 2)
- C2.1 Excluded whatever the allowlist says, tested on every component of the strictly resolved path:
  - environments: any directory holding `pyvenv.cfg` or `conda-meta/`, and everything under it; the running
    interpreter's `sys.prefix`, `sys.base_prefix` and `sys.exec_prefix`; every site root
    (`site.getsitepackages()`, `site.getusersitepackages()`); any component named `site-packages` or
    `dist-packages`;
  - native and binary extensions: the suffixes in `importlib.machinery.EXTENSION_SUFFIXES` plus `.so`, `.pyd`,
    `.dylib` and `.dll`, and any module loaded by an extension loader;
  - generated and build output: `__pycache__/`, `*.pyc`, `build/`, `dist/`, `*.egg-info/`, `*.dist-info/`,
    `.eggs/`, Melder's runtime caches under `__melder_cache__/` (written inside the melder package, Note 20), the
    build-asset manifests and payloads under `_build_assets/`, the `llm_support/` bundles, and the scope's
    declared generated subtrees;
  - tool and VCS state: `.git/`, `.hg/`, `.tox/`, `.nox/`, `.mypy_cache/`, `.pytest_cache/`;
  - vendored third-party trees inside a root, by declaration (C1.2), because they cannot be detected reliably.
  Today nothing in Melder reads an environment marker, the interpreter prefixes or the extension suffixes
  (Note 18).
- C2.2 Resolution and comparison:
  - an existing target is resolved with `Path.resolve(strict=True)`; for a new file the parent is resolved
    strictly and the final component MUST be a plain name (no separator, no `..`);
  - containment is decided on resolved Path objects only, never on raw or lexical strings: lexical
    `is_relative_to` accepts `C:\proj\src\..\..\outside\x.py` as inside `C:\proj` (Note 19);
  - on Windows containment is case-insensitive, as WindowsPath already compares (Note 19); an alternate data
    stream (a `:` after the drive), a DOS device name or a UNC target the scope did not declare is refused.
- C2.3 Links: a file is refused for modification when any component between its permitted root and the file is
  a symlink, a junction or another reparse point, even when the target is also eligible, and when its
  `st_nlink` is above 1. In the probe a symlink inside a root resolved to an outside site-packages, and a hard
  link inside a root shared its inode with an installed module, so a write through it changed the installed file
  (Note 19).
- C2.4 The check happens at the write, not before it: open the parent directory, re-resolve, open the target
  without following links where the OS allows (`O_NOFOLLOW` on POSIX), confirm with `fstat` on that handle a
  regular file with `st_nlink == 1` and the device and inode seen at the check, write a temporary file in the same
  directory and `os.replace` it into place. Any mismatch aborts with nothing written. Analysis-time custody is
  never reused as this check (Note 18).

### C3. Permissions and the owner-controlled path (owner item 3)
Six permissions. None implies another, and reading never implies writing.
- C3.1 discover - enumerate modules, custody, dependency graphs and research records. Agents. Today research verbs
  pass no frame ACL (Note 9); whether research reads go through the view ACL is a D2 question.
- C3.2 read - read the source of eligible files, of the core and of recorded modules, installed leaves included
  (the owner's "agents can read the core"). Agents. Today codegen `open` reads any file the process can read
  (Note 10); that is defect D-10 under C6, not this permission.
- C3.3 modify - change an existing eligible file. An agent may only propose; applying to the shared tree needs an
  owner grant scoped to named roots. Today no Melder surface does this, and codegen `open` writes anywhere (D-10).
- C3.4 generate - create a new file in a declared generation directory under a permitted root, or a new in-process
  module in a declared generation namespace (C1.4). The agent proposes; the owner grants per directory or
  namespace; an existing name is always refused. Today ProtocolCrafter writes to any path, and materialize_codegen
  replaces existing modules (Note 20, defect D-20).
- C3.5 install - put a built artifact into an environment. Owner only, outside Melder (D5, D7); Melder performs no
  installs and holds no install grant. Today subprocess is reachable under permissive and full_access, and through
  `__import__` under hybrid and precision (Notes 10-11).
- C3.6 promote - make a validated change the one in force: a runtime selection (a notch into a production lane), a
  source merge into the protected branch, or an artifact install. Owner only.
- C3.7 Core evolution happens only in a fork scope (D4). The protected core is never eligible in the main scope;
  in a fork scope the fork's own tree is the eligible source, with its repository identity and base revision
  recorded, and the running process never hot-replaces a core module.
- C3.8 A governed change moves proposed -> validated -> approved -> applied -> promoted, with rejected and
  rolled_back as exits. Agents propose and validate in an isolated workspace (a worktree or a copy, never the live
  tree); the owner approves apply, promote and install. An approval is bound to the exact change digest, so a
  changed proposal needs a new approval. Every transition is journaled with actor, time, reason and digests.

### C4. Validation, change records, rollback and compatibility (owner item 4)
- C4.1 Validation before approval, all in the isolated workspace: C1-C2 eligibility of every touched path; every
  changed module compiles; the project's test tiers; a Crystallizer analysis of the candidate world (custody and
  the drift preflight); codegen-profile validation of generated code; for a core fork, the fork's full Melder
  tiers and a regenerated registration-guard manifest.
- C4.2 The change record is value-only and journaled: change id, actor, permission and grant ids, scope id; per
  path the resolved path, its root, the SHA256 of the bytes before (or "absent") and after, and the prior bytes or
  a VCS reference that can restore them; the tree's base revision (commit plus a dirty flag); validation commands,
  results and digests; the approval (approver, time, approved digest); promotion events; the declared external
  effects (C4.5). Hashes come from the bytes at record time, never from the stat-guarded source cache, which
  served a stale hash after a same-size rewrite with the mtime restored (Note 19).
- C4.3 What can be rolled back (Note 21), and how:
  - eligible source files: from the record's prior bytes or VCS revision, written with the C2.4 discipline and
    verified by hash; a file changed since the record is a conflict and is never overwritten blindly;
  - a runtime selection: a notch back to the parked previous member - the selection only; whether instances built
    under the newer member are retired was not traced (UNKNOWN);
  - research organization: restore_network to the snapshot address captured in the record, while that address is
    still in the bounded retention ring;
  - a recorded world: restore of an earlier checkpoint into a fresh runtime, all-or-nothing per run, never an
    in-place revert of a live world;
  - environments: reinstall the previous artifact by digest - the owner, outside Melder;
  - in-process module replacement: no rollback exists (the original module is not restored, Note 20), which is
    why C1.4 forbids generating into an existing name.
- C4.4 Compatibility before promotion: the candidate's dependency set (distribution names, versions, artifact
  digests) against the target environment; the Crystallizer RecordVersion major of every record the change reads
  or writes; the public export surface of each changed module; the creation-cache generation. The dependency
  baseline comes from the environment (importlib.metadata or a lock file), because under the shipped default the
  record holds no distribution provenance for installed dependencies of user code (Note 19).
- C4.5 External effects that need separate handling, because no Melder rollback reaches them: writes through
  ExternalPersistenceManager callables to user stores; network calls; subprocesses; files outside the permitted
  roots; import-time side effects of changed modules; persisted formats (Crystallizer records and checkpoints,
  caches); objects built by changed code that outlive the change. Each change declares them; validation refuses an
  undeclared effect where it can detect one, and the rest are owner-accepted risks named in the record.

### C5. Regression cases (owner item 5)
Named for the symptom. PINNED means written and run (in this review, or existing and rerun green here);
SPECIFIED means written with the implementation. Characterizations pin today's behaviour, so the implementing
change updates them on purpose.
- Positive
  - P1 an owner-granted modify of an eligible .py file applies, and its record carries both hashes. SPECIFIED.
  - P2 a generate into a declared directory or namespace creates the file or module and records it. SPECIFIED.
  - P3 agents read core source and a recorded installed leaf with no write grant. PINNED in part:
    test_recorded_leaf_source_read_integration (an installed leaf read with descent off, from a safe room).
  - P4 a notch back to the parked previous member restores the selection. PINNED (existing, rerun green):
    test_spell_index_notch_lifecycle::test_notch_back_restores_original_active and
    test_index_lifecycle_and_depth_integration::test_lifecycle_notch_back_restores_and_melds_original.
  - P5 a research lane anchored to a running spell leaves the selection, residency and meld result alone. PINNED:
    test_research_lane_runtime_isolation_integration.
  - P6 a user subclass of an internal class registers normally. PINNED: test_internal_registration_identity.
- Negative
  - N1 a module of a nested environment under the project root is refused. SPECIFIED; today's user_source
    classification is PINNED by test_custody_boundary_characterization.
  - N2 a file under an interpreter site root, a `site-packages` or a `dist-packages` is refused. SPECIFIED.
  - N3 a native extension inside a permitted root is refused. SPECIFIED (Note 19 probe).
  - N4 paths in `build/`, `dist/`, `*.egg-info`, `__pycache__`, `__melder_cache__`, `_build_assets` and
    `llm_support` are refused. SPECIFIED.
  - N5 a symlink inside a root - to an outside site-packages, and to another file in the root - is refused.
    SPECIFIED (Note 19 probe).
  - N6 a hard-linked file (st_nlink 2) inside a root is refused and the installed file stays unchanged. SPECIFIED.
  - N7 a path lexically under the root that resolves outside it through `..` is refused. SPECIFIED.
  - N8 on Windows a case variant of an excluded path, a junction and an alternate data stream are refused.
    SPECIFIED (Windows tiers, owner-run).
  - N9 a target swapped for a symlink between the check and the write is refused with nothing written. SPECIFIED.
  - N10 a protected core module is refused outside a fork scope. SPECIFIED.
  - N11 materializing under an existing name - a core module, a stdlib module, an installed import name - is
    refused and leaves sys.modules unchanged. SPECIFIED; today this is defect D-20 (Note 20), not yet pinned.
  - N12 install and promote without their owner grants are refused, and a modify grant never allows either.
    SPECIFIED.
  - N13 codegen `open(..., "w")` under safe, and `__import__` of denied roots under hybrid and precision, are
    refused. PINNED as strict xfail (defects D-10 and D-11): they document the defects and protect nothing.
  - N14 a renamed core fork is not covered by the registration guard. PINNED (characterization):
    test_internal_registration_identity.
- Recovery
  - R1 a change that fails validation leaves the tree byte-identical (the before-hashes match) and is recorded
    rejected. SPECIFIED.
  - R2 a write failing partway through a multi-file apply restores the files already written from their prior
    bytes. SPECIFIED.
  - R3 rolling back an applied change restores every file and verifies its hash; a file edited since is reported
    as a conflict and left alone. SPECIFIED.
  - R4 a failed promotion leaves the previous selection active. SPECIFIED.
  - R5 a restore stage failure tears down everything that run built, newest first. PINNED (existing, rerun green):
    test_restore_report_safety::test_built_stack_teardown_runs_newest_first_and_survives_noise and
    test_crystallizer_restore_integration::test_wide_pool_chaos_tears_down_three_book_world.
  - R6 a failed or cleaned-up materialization leaves sys.modules as it found it. SPECIFIED; today the original
    module is removed (D-20).
  - R7 restore_network recovers the organization and keeps the journal, and a snapshot without the default lane
    leaves the live organization untouched. PINNED (existing, rerun green):
    test_research_set::test_restore_network_recovers_organization_and_keeps_history and
    test_research_set::test_restore_network_refuses_snapshot_without_default_lane.

### C6. Evolution scope is not security isolation (owner item 6)
- C6.1 C1-C5 define what a governed change may touch. They are not a security boundary. The codegen profiles, the
  import gate, the builtins filter, the registration guard and custody classification run in the same process as
  the code they police, so that code can get around them; they are policy and defence in depth.
- C6.2 Open defects, each a defect until it is fixed and its own test passes: D-10, `open` reads and writes files
  under every codegen profile, safe included (Note 10); D-11, `__import__` loads roots that hybrid and precision
  deny (Note 11); D-20, materialize_codegen replaces live core and dependency modules and cannot put them back
  (Note 20). The strict xfails for D-10 and D-11 document the defects and establish no protection. D-20 has no
  test yet; pinning it as a strict xfail is the owner's call.
- C6.3 Protection from agent code, if wanted, needs an OS boundary: agent code in a separate process or user, the
  environment and the core tree mounted read-only, only the permitted roots (or a copy of them) writable, and no
  network unless granted. Melder writes its runtime caches inside the melder package directory (Note 20), so a
  read-only environment needs those caches moved first. This is an owner decision under D2.
- C6.4 Wording rule: no ticket, document or test calls a C6.1 control protection. This review's own test-file
  title and its test-map lines are reworded to a characterization label in the same pass (Note 22).

## D1-D8 Mapping to the Contract (melder_1, 2026-10-10)
Each decision: the clauses it governs, what is still the owner's to decide, and the evidence that would accept it.
- D1 protected core
  - Clauses: C1.3, C1.4, C3.7; cases N10 and N14.
  - Owner decides: the recommendation (the `melder` distribution identified by version and digest, MelderOps
    declaring its own core the same way), and whether MelderOps's core list lives in this repository.
  - Acceptance: N10 passes, and N14 is updated to the chosen identity (a renamed fork covered, or recorded as out
    of scope).
- D2 enforcing surfaces
  - Clauses: C3 (each permission names its enforcing surface), C6.2 and C6.3.
  - Owner decides: whether D-10, D-11 and D-20 become their own tasks; whether the protected core's top-level
    packages are denied import roots below full_access; whether research reads pass the view ACL; whether an OS
    boundary is required, and where Melder's caches move if so.
  - Acceptance: the D-10 and D-11 strict xfails become passing regressions; N11 and N12 pass; an adopted OS
    boundary gets its own integration test.
- D3 root precedence
  - Clauses: C1.1 (custody grants nothing), C2.1 (environment markers), C4.4.
  - Refinement: the evolution scope no longer depends on D3 - eligibility is the allowlist plus C2, so D3 decides
    analysis only. The review now recommends option (b) extended by markers: user_source skips the interpreter's
    prefixes and site roots and any directory holding `pyvenv.cfg`, which also catches a foreign `.venv_new`.
  - Owner decides: (b) with markers or another option, and whether descent-off leaves should record distribution
    provenance (Note 19); either change needs a record-version note.
  - Acceptance: N1 for eligibility; the custody characterizations updated to the chosen rule.
- D4 fork and research branch
  - Clauses: C3.7, C3.8, C4.2 (base revision and artifact digest in the record).
  - Owner decides: "research branch = native lane, fork = source-control fork, linked by lane metadata" and the
    lineage fields listed in D4.
  - Acceptance: a fork keeps its lineage through restore; P5 stays green.
- D5 authority
  - Clauses: C3.1-C3.6 and C3.8.
  - Owner decides: who holds each grant, how a grant is revoked, and where approvals are journaled (the
    MutationResearch journal or a change-record store).
  - Acceptance: N12 passes, and an approval bound to one digest refuses a changed proposal.
- D6 unit of a selective upgrade
  - Clauses: C4.1, C4.2, C4.4.
  - Owner decides: the upstream commit as the unit, and the conflict policy (the owner resolves; never automatic).
  - Acceptance: an upstream selection leaves unselected and local work intact (to be specified with D4).
- D7 source to runtime
  - Clauses: C1.4 (no hot replacement), C4.3, C4.4, C4.5.
  - Owner decides: a wheel into a fresh environment plus a restart, and where the previous artifact and its
    checkpoint are kept for rollback.
  - Acceptance: R5 and R7 (existing, green), plus R1-R4 and R6 with the implementation.
- D8 documents
  - Clauses: all. On acceptance C1-C6 land as invariants and failure modes in src_architecture and as component
    contracts in src_components; tests_components already maps the suite.
  - Missing: the Phase 1 baseline. No document in this repository is one - the only Markdown naming a Phase 1
    baseline or scope is this ticket, and "Phase 1" elsewhere means the compiler's first phase (Note 14). The
    owner names it, probably a MelderOps or owner document, and says whether it changes.
  - Acceptance: the named Phase 1 document reviewed against C1-C6 (or recorded unchanged), and the two system
    documents updated in the implementing change.

## Commit Grouping (owner action; nothing committed)
Accepted work and the unresolved protection review go in separate commits.
- A, scan_bind_option_parity (0.2.8228): src/melder/aether/spellbook/bind/scan.py, src/melder/aether/spellbook/
  spellbook.py, src/melder/__version__.py, README.md, release_docs/next_version_release.md, its two tests
  (tests/unit/melder/spellbook/test_scan_bind_option_parity.py, tests/component/melder/spellbook/
  test_scan_bind_parity_component.py), src_architecture and src_components with their indexes, src_graph with its
  index and the scan descriptor, patches/active/scan_bind_option_parity_2026_10_10/, its ticket, the build assets,
  and llm_support's src and other bundles with their indexes.
- B, core_protection_review: the five review test files and this ticket - characterization and specification only.
- Shared, after both (or with B): tests_components.md and its index (both lanes' entries and shared counts),
  llm_support's tests bundle, its index and manifest.json, attention_board.md and artifact_board.md. Until these
  land, the tracked-only llm_support check reports the tests bundle stale.

## Hand-back (melder_1, 2026-10-10)
The owner accepted this review and its direction on 2026-10-10 (Note 25): governed evolution operates on explicitly
approved application source, and installed dependencies, virtual environments, site-packages and native or binary
extensions stay outside the mutation scope. The acceptance resolves none of the protection gaps and authorizes no
implementation, commit or public push. Evidence pack: `artifacts/core_protection_review_20261010/` (start at its
README); the scan_bind lane's pack is `artifacts/scan_bind_option_parity_20261010/`.

### Reviewed and tested revision
- HEAD 66939dfe84e41e51f41f4bc4461ad1690907e909 on codex_features2, plus the working-tree changes of this request's
  two lanes (scan_bind_option_parity at 0.2.8228 and this review). Every changed file is listed with its SHA256 in
  the packs' `file_manifest.md`, and the whole delta against HEAD in `tree/tree_delta.txt` (content compared with
  line endings normalized; about 1,750 tracked files differ from HEAD only in CRLF endings).
- src/ and tests/ did not change after the final verification began (2026-10-10T12:53Z); later edits are in
  context_compass/ and in the generated assets, which the closing rebuild checks.
- Nothing is committed or pushed; the commits follow "Commit Grouping" above (owner).

### Environment
- The device VM on the owner's machine: Ubuntu 22.04.5 LTS, Linux 6.8.0; CPython 3.14.7 free-threading build run
  with `-X gil=0` (`sys._is_gil_enabled()` False); pytest 9.1.1; installed beside it: iniconfig 2.3.0, packaging
  26.3, pluggy 1.6.0, Pygments 2.21.0, PyYAML 6.0.3 (`env/`). Windows tiers and hosted CI: Not run (owner).

### Commands and results
- Every run: `python -X gil=0 -m pytest -q -p no:cacheprovider -rsxX <paths>` from the repository root, with
  PYTHONDONTWRITEBYTECODE=1, the pycache prefix and TMPDIR outside the repository (`runs/run_one.sh`).
- Whole tests/ tree: 13,639 passed, 32 skipped, 17 xfailed, 2 xpassed, 0 failed, in 16 runs that partition it
  (`runs/results_table.md`; the crystallizer integration folder ran in seven groups because one file exceeds the
  180 s call limit). Three more runs are subsets on the same tree: the focused scan set (409 passed), this review's
  suite and the unit spellbook folder (2343 passed).
- This review's suite (five files): 28 passed, 5 xfailed. The five xfails are strict and are the open defects: one for
  D-10 (`test_safe_profile_refuses_writing_files`) and four for D-11 (`test_hybrid_refuses_dynamic_imports_...`).
- Every other skip, xfail and xpass is pre-existing and unrelated, each with its reason in `runs/skips_xfails.md`:
  skipped - opt-in timing experiments (4), retired src_graph.json fixtures (23), a build-asset test that needs a
  fresh interpreter, a package-wrapping case and an empty interface parameter set (3), two SpellIndex.update cases
  (2); xfailed - seven package-helper cases (coroutine rejection, a call fallback), the process-wide spell-id graft
  conflict (3), the conjure-sweep preflight race (1), the live_sim automatic bootstrap (1); xpassed - the two
  non-strict fault-B markers.
- Probes rerun on this tree at 13:33Z reproduce every finding they back (Note 27; `probes/`).

### Diffs
- This review: `diffs/review_authored.diff` (the five test files against HEAD) and
  `diffs/tests_components_review_part.diff` (the review's part of the test map). The scan_bind lane's diffs are in
  its own pack. Generated files are listed with hashes, not diffed.

### D1-D8 disposition
The direction is accepted; every decision below still needs the owner's word, and nothing in it is implemented.
- D1 protected core: recommended - the `melder` distribution by version and digest, MelderOps declaring its own.
  Open: confirm, and say where MelderOps's list lives.
- D2 enforcing surfaces: the three defects are routed to their own tickets (below). Open: the core's packages as
  denied import roots below full_access; research reads through the view ACL or not; an OS boundary, and if so
  where Melder's caches move.
- D3 root precedence: now an analysis question only (eligibility is the allowlist plus C2). Open: option (b) with
  environment markers, provenance for descent-off leaves, the record-version note either change needs.
- D4 fork and research branch: recommended - lane = native ResearchLane, fork = source-control fork, linked by lane
  metadata. Open: confirm the lineage fields.
- D5 authority: open - who holds each grant, revocation, where approvals are journaled.
- D6 unit of a selective upgrade: open - the upstream commit as the unit, conflicts resolved by the owner.
- D7 source to runtime: open - a wheel into a fresh environment plus a restart, and where the previous artifact and
  its checkpoint are kept for rollback.
- D8 documents: open - the Phase 1 baseline is missing (next subsection); on implementation C1-C6 land in
  src_architecture and src_components.

### Gaps kept open
Each is a defect until its own test passes on a fixed tree; none is resolved by this hand-back.
- D-10, file access: `open()` reads and writes any file under every codegen profile, safe included (Note 10).
  Pinned by one strict xfail. Ticket: `tickets/tasks/backlog/2026-10-10_deny_file_access_under_safe_codegen_task.md`.
- D-11, dynamic import: `__import__` loads roots hybrid, precision and permissive deny or leave out (Note 11). Pinned
  by four strict xfails. Ticket: `tickets/tasks/backlog/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md`.
- D-20, hot replacement (the further gap, with its own reproducer, impact and evidence): `materialize_codegen` replaces
  live core, stdlib and dependency modules and cannot restore them (Note 20). Reproducer only, no test pin. Ticket:
  `tickets/tasks/backlog/2026-10-10_refuse_materializing_over_live_modules_task.md`.

### Proposed implementation follow-ups
Priority, then the evidence that accepts it. Each needs its own approved task.
- P1 D-10: safe refuses `open` at validation and at run time; the strict xfail passes without its marker; every
  profile's file posture is pinned.
- P1 D-11: the four strict xfails pass without their marker; `__import__('melder')` is refused below full_access;
  allowed imports are unaffected.
- P1 D-20: N11 and R6 pass; generation only inside the declared namespace.
- P2 Eligibility checker (C1-C2: permitted roots, exclusions, strict resolution, link refusal, write-time recheck):
  N1-N9 pass (N8 on the Windows tiers) and P1-P2 pass.
- P2 Change record, write discipline and file rollback (C3.8, C4.2, C4.3): R1-R3 pass, and an approval bound to one
  digest refuses a changed proposal.
- P2 The contract and the open defects in the system documents (src_architecture invariants and failure modes,
  src_components contracts): reviewed by the owner, with no C6.1 control called protection.
- P3 D3 custody markers and descent-off provenance, with a record-version note: N1 for custody, and the custody
  characterizations updated on purpose.
- P3 C3 grants (D5): N12 passes and P3 stays green.
- P3 OS boundary and cache relocation (C6.3), only if the owner adopts it: its own integration test.
- P3 The two items scan_bind raised: a bare-string `disposal_method_names` on direct `Spellbook.bind` is iterated per
  character, and `Spellbook.scan` never cleans its Scan helper; one symptom-named regression each.
- Owner decision: name the Phase 1 baseline (D8).

### Missing baseline material
- The Phase 1 baseline (D8): no document in this repository is one; "Phase 1" here means the compiler's first phase
  (Note 14). Probably a MelderOps or owner document - UNKNOWN until the owner names it.
- A dependency-version baseline for C4.4: under the shipped default the record holds no distribution provenance for
  installed dependencies of user code (Note 18), so it must come from the environment or a lock file.
- Windows tiers and hosted CI for this tree (owner-run).
- Whether a notch back retires instances built under the newer member: UNKNOWN (Note 21).

## Proposed Verification Plan (review deliverable)
- The contract's case list (C5) supersedes this plan in detail; it is kept as the review's first plan.
- In place (Notes 12-13): characterization tests for F1-F6 and the codegen import gate, and strict xfails
  for the two codegen gaps; mutants show each family fails when its behaviour moves.
- After the decisions (proposed, not written):
  - D2 fixes: the two strict xfails become ordinary regressions; per-profile cases for `open`, `io.open`,
    `os.open` and pathlib writes; `importlib.import_module` and `sys.modules[...]` reach-arounds.
  - D2 inventory: safe codegen cannot bind, notch, add to or remove from an index, or materialize a module
    under the core package name.
  - D3: custody cases for a nested `.venv`, an editable install (a path finder outside site-packages), a
    vendored package inside the user root, an explicit override, descent on and off and unknown modules,
    updated to the chosen rule.
  - D4-D5: a fork keeps its lineage through restore; an upstream selection leaves unselected and local work
    intact; promotion and installation refuse without their own grant.
  - External limits: a test documents that an out-of-process writer is not stopped by any Melder ACL.

## Acceptance Criteria for Review
- [x] Produce an evidence-backed matrix separating discovery/read, supported runtime mutation, source
      writes, and installed-package updates, including enforcement owner and unprotected external paths.
- [x] Confirm the default core-read/deny-core-change policy and explicit deliberate-fork workflow with owner.
      (Direction accepted by the owner on 2026-10-10, Note 25; nothing implemented.)
- [x] Settle D1-D8 or name their blockers and owners; do not label assumptions implemented facts.
      (Named: the Hand-back's D1-D8 disposition lists each remaining owner decision.)
- [x] Specify native research-lane vs Git-fork mapping and lineage sufficient to identify parent, local
      modifications, selected upstream changes, produced artifacts, and runtime selection.
      (Proposed in D4; the owner accepts or redirects.)
- [ ] Define selective-updater inputs, conflict behavior, allowed sources, dependency strategy, approval
      transitions, validation, rollback, and audit record; do not propose a fork of pip.
      (Partly: C3.8 and C4 now specify approval transitions, validation, change records, rollback and the
      audit record; inputs, conflicts, sources and dependency strategy still wait on D1, D4 and D6.)
      Not fully met; the owner accepted it as is (Note 25), and the rest is routed to D1, D4 and D6 (Hand-back).
- [x] Propose tests for external site packages, nested .venv, explicit user-root overrides, editable and
      vendored installs, installed root objects, descent on/off, leaf source reads, and unknown modules.
      (Verification plan; the current behaviour of nested .venv, src-only roots, descent, leaf reads and
      unknown modules is already pinned by the suite, Notes 12-13.)
- [x] Propose tests that authorized reads still work, forbidden supported core mutations fail, forks retain
      lineage, selective upgrades preserve unselected/local work, and promotion/install require their own
      authority. Specify external filesystem/install limitations honestly rather than claiming ACL coverage.
- [x] Keep existing Phase 1 scope intact; route only accepted architectural changes and implementation
      into separately approved follow-on work.
- [x] Turn the owner's direction into a concrete governed-evolution contract - eligibility, exclusions and
      path checks, separate permissions, change records and rollback, regression cases, isolation kept
      separate - and map D1-D8 to it (owner request, Note 17; Notes 18-23 and the sections above).

## Steps / Checklist
- [x] Inspect pinned code and verify discovery defaults and ownership precedence.
- [x] Run focused baseline tests and nonmutating classification probe.
- [x] Verify native research-lane nomenclature and check official pip option documentation.
- [x] Prepare this review ticket beside the earlier ticket and a byte-identical downloadable copy.
- [x] Assign reviewer and activate board routing for review (melder_1, 2026-10-10).
- [x] Review boundary matrix, open decisions, and proposed workflow with owner (accepted 2026-10-10, Note 25).
- [x] Record accepted decisions, remaining blockers, and bounded follow-on implementation tasks (Hand-back;
      D-10, D-11 and D-20 as draft backlog tickets, Note 29).
- [x] Use the ticket microcycle during execution; implementation remains outside this review scope.
- [x] Add the regression suite the owner asked for (2026-10-10; tests only, Notes 12-13).
- [x] Write the governed-evolution contract, the D1-D8 mapping and the commit grouping (Notes 17-23).
- [x] Hand back the ticket and its evidence: final verification, evidence pack, defect tickets, Hand-back section
      (Notes 25-29).

## Deliverables
- This self-contained review ticket with source evidence and proposed acceptance criteria.
- Later: accepted decision record and bounded implementation/test plan, only after review.
- Hand-back (2026-10-10): the Hand-back section of this ticket, the evidence pack
  artifacts/core_protection_review_20261010/ and three draft defect tickets in tickets/tasks/backlog/.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md
- Download copy: /workspace/shared/melder-tickets/2026-10-08_review_core_protection_fork_aware_updates_task.md
- Existing scan-bind ticket and runtime source files remain unchanged.
- Regression suite (melder_1, 2026-10-10; tests only, owner's request):
  - tests/unit/melder/crystallizer/crystal_analysis/test_custody_boundary_characterization.py (new)
  - tests/unit/melder/spellbook/bind/test_internal_registration_identity.py (new)
  - tests/integration/melder/crystallizer/test_recorded_leaf_source_read_integration.py (new)
  - tests/integration/melder/mutation_research/test_research_lane_runtime_isolation_integration.py (new)
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py (new)
  - context_compass/system_docs/tests_components.md and its index
  - llm_support bundles and build assets rebuilt last (no notch: no source change)
- Contract pass (melder_1, 2026-10-10; specification only):
  - this ticket (contract, D1-D8 mapping, commit grouping, Notes 18-23)
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py (module docstring only)
  - context_compass/system_docs/tests_components.md (three lines reworded, one code-map entry remeasured)
    and its index
  - llm_support bundles and build assets rebuilt last (no notch: no source change)
- Hand-back (melder_1, 2026-10-10):
  - context_compass/artifacts/core_protection_review_20261010/ (evidence pack, new)
  - context_compass/tickets/tasks/backlog/2026-10-10_deny_file_access_under_safe_codegen_task.md (new)
  - context_compass/tickets/tasks/backlog/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md (new)
  - context_compass/tickets/tasks/backlog/2026-10-10_refuse_materializing_over_live_modules_task.md (new)
  - context_compass/attention_board.md and context_compass/artifact_board.md (closure sync)
  - build assets and llm_support bundles rebuilt last

## Validation
Review suite (melder_1, 2026-10-10, CPython 3.14.7 free-threaded, -X gil=0, device VM): the five new files
28 passed and 5 xfailed (strict, each failing on its own assertion); mutants in a scratch copy fail the
intended tests and turn the xfails into XPASS(strict); neighbouring tiers green (Note 13). Windows tiers and
hosted CI: Not run (owner).

Contract pass (melder_1, 2026-10-10, CPython 3.14.7t, -X gil=0): the five review files 28 passed, 5 xfailed
after the docstring rewording; six existing tests named as pins (P4, R5, R7) 6 passed in the /tmp scratch
copy; the probes of Notes 19-20 ran in /tmp only. Windows tiers and hosted CI: Not run (owner).

Final verification for the hand-back (melder_1, 2026-10-10, Note 26): the whole tests/ tree on the final tree,
GIL off - 13,639 passed, 32 skipped, 17 xfailed, 2 xpassed, 0 failed; the commands, logs, junit XML and every
skip and xfail reason are in artifacts/core_protection_review_20261010/runs/. Windows tiers and hosted CI: Not
run (owner).

Observed baseline only: 7 passed, 14 deselected in 0.31 seconds, CPython 3.14 free-threaded.
This is not a whole-suite pass or validation of the proposed ACL/updater design.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -X gil=0 -m pytest -q -p no:cacheprovider \
  tests/unit/melder/crystallizer/test_crystallizer_configuration_analysis_knobs.py \
  tests/unit/melder/crystallizer/crystal_analysis/test_crystal_analyzer.py \
  -k 'descent or site_package'
```

Nonmutating classification probe (private analyzer seam used only as investigation evidence):
```python
from pathlib import Path
import pytest
from melder.crystallizer.crystal_analysis.crystal_analyzer import CrystalAnalyzer
root = Path.cwd().resolve()
package_path = Path(pytest.__file__).resolve()
for roots in [(root,), (root / 'src',)]:
    analyzer = CrystalAnalyzer(
        user_source_root_paths=roots,
        site_package_root_paths=CrystalAnalyzer.resolve_site_package_root_paths(),
        site_package_dependency_descent=False,
    )
    try:
        custody = analyzer._match_custody(
            module_name='pytest', module_obj=pytest, module_path=package_path,
        )
        print(roots, custody.kind, analyzer._custody_descends(custody))
    finally:
        analyzer.cleanup()
```
Run with PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -X gil=0 from a checkout
whose .venv contains pytest. Measured output: cwd -> user_source/True; cwd/src -> site_package/False.
Source-view behavior was traced in code, not exercised as an end-to-end ACL test. All new acceptance
checks above are planned and remain unimplemented/unrun.

## Evidence Index
All repository links below are pinned to the reviewed SHA.
- E1: [Configuration default](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/configuration/crystallizer_configuration.py#L382-L404)
- E2: [Descent policy and walk](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/crystal_analysis/crystal_analyzer.py#L740-L865)
- E3: [Facade wiring](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/crystallizer.py#L1708-L1718)
- E4: [Default cwd root](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/configuration/crystallizer_configuration.py#L798-L831)
- E5: [Custody order](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/crystal_analysis/crystal_analyzer.py#L260-L278)
- E6: [User-source containment](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/crystal_analysis/custody/user_source_custody_strategy.py#L141-L148)
- E7: [Object-root analysis](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/crystals/spell_crystal.py#L342-L375)
- E8: [Path resolution](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/crystallizer/crystal_analysis/crystal_analyzer.py#L1363-L1425)
- E9: [Recorded source-view targets](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/mutation_research/mutation_research.py#L1957-L1970)
- E10: [Live source fallback](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/mutation_research/mutation_research.py#L2013-L2042)
- E11: [Internal registration guard](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/aether/spellbook/bind/bind.py#L64-L107)
- E12: [Lane anchoring contract](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/mutation_research/research_set/research_set.py#L974-L1010)
- E13: [Native lane/runtime distinction](https://github.com/Synaptic724/melder/blob/66939dfe84e41e51f41f4bc4461ad1690907e909/src/melder/mutation_research/research_set/research_lane.py#L153-L195)

## Risks / Rollback Notes
- Confusing read/discovery policy with write authority produces false protection claims.
- Broad cwd roots, editable installs, and vendored modules defeat location-only ownership assumptions.
- Selective upstream changes can violate compatibility despite individually valid package pins.
- Unrecorded fork ancestry makes later updates and rollback ambiguous.
- No runtime/source rollback is needed for this ticket-only work. A future updater must define rollback
  separately for runtime state, source tree, installed environment, and persisted data.

## Applicable Anti-Patterns
- [x] Separate verified behavior from proposals and open questions.
- [x] Do not infer implementation, package updates, or publication from a review-ticket request.
- [x] No status transition without evidence-backed reason.
- [x] No implementation from UNKNOWN/HYPOTHESIS or closure without owner acceptance and board sync.

## Done Checklist
- [x] Ticket preparation completed and baseline evidence recorded.
- [x] Existing ticket preserved; downloadable copy prepared.
- [x] Review steps and deliverables complete.
- [x] Open decisions resolved or explicitly routed (Hand-back: D1-D8 disposition, defect tickets).
- [x] Validation limitations and planned checks accepted (owner, 2026-10-10).
- [x] Applicable anti-patterns clear and notes quality maintained.
- [x] Acceptance criteria reviewed with owner and confirmed (Note 25).
- [x] Board sync completed for accepted review and successor routing.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true (the hand-back evidence pack, 2026-10-10; earlier evidence stays embedded here)
- ARTIFACT_PATHS:
  - artifacts/core_protection_review_20261010/
- DISPOSITION: retain_as_reference (the three defect tickets point at its probes)
- CLEANUP_TRIGGER: none; retained with this completed ticket and its successor defect tickets.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: core read-only defaults, fork lineage, selective updates, discovery versus authorization
- IF_UNKNOWN: ask owner before implementation or architecture changes

## Noting Behavior
Record tactical findings with evidence and one next action. Keep policy proposals labeled. Correct factual
errors explicitly; do not silently convert analysis behavior into an authorization guarantee.

## Notes
- DATETIME: 2026-10-08T20:37:15Z
  TYPE: MEASURE
  CLAIM: Seven focused tests passed; a nonmutating probe verified cwd/.venv user-source precedence and
    the different result with src-only roots.
  EVIDENCE:
  - E1-E6 and the embedded Validation reproduction
  IMPACT: The default descent policy is real but not a universal site-package exclusion.
  NEXT: Decide intended overlap semantics during review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-08T20:45:00Z
  TYPE: FACT
  CLAIM: Source-view fallback reads recorded module paths; native lanes record ancestry separately from
    runtime residency. Neither fact establishes the proposed core mutation policy.
  EVIDENCE:
  - E9-E13
  IMPACT: Review must keep source visibility, research organization, and mutation authority distinct.
  NEXT: Identify exact supported mutation enforcement surfaces and fork representation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-08T20:45:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner requests review of read-allowed/read-only core defaults, deliberate forks, lineage, and
    agent-selected research-branch updates using ordinary pip where useful, without forking pip or
    expanding Phase 1 automatically.
  EVIDENCE:
  - Owner conversation and ticket request Sentinel_7735a734e1308191ab903636993a377e
  IMPACT: Capture this direction without asserting an implemented ACL/updater or amending architecture.
  NEXT: Resolve D1-D8 with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T08:41:57Z
  TYPE: FACT
  CLAIM: This ticket was reconstructed, not copied. The owner's pasted original (prepared by dot) was
    lost at a context compaction before it was written; the content here comes from melder_1's
    compaction summary of it. Priority, exact wording, commands and E1-E13 beyond the listed ranges are
    missing, so every finding stays UNKNOWN until re-verified against source.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:13-21
  IMPACT: The findings are leads, not facts; the owner can re-paste the original to restore it.
  NEXT: Ask the owner once whether to re-paste the original; continue verification regardless.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T08:41:57Z
  TYPE: DECISION
  CLAIM: Assigned to melder_1 by the owner on 2026-10-10 ("go ahead and investigate the findings and fix
    them"). For this review that means: verify F1-F6, run the D3 probe, and write the D1-D8 decision
    request. Nothing in the core-protection design is implemented without the owner's answers. Order:
    scan_bind_option_parity first (implementation), this lane once that one reaches review.
  EVIDENCE:
  - context_compass/attention_board.md:181-182
  IMPACT: Keeps one implementation lane active at a time; this lane changes no source.
  NEXT: When scan_bind reaches review, read crystallizer_configuration.py:382-404 and 798-831 for F1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T11:03:11Z
  TYPE: FACT
  CLAIM: The owner's original text (prepared by dot) reached this session again in full on 2026-10-10,
    so the ticket now carries it verbatim, superseding the reconstruction that Note 4 describes (Note 4's
    evidence range pointed at the reconstruction's provenance section, which no longer exists). Changes
    to the original: Metadata (status, owner, agent name, updated), the State Transition Event and the
    assignment checklist item; dot's three notes are kept as written, the two melder_1 notes follow them.
    The original's findings F1-F6, the boundary matrix, D1-D8 and E1-E13 are now the review's input; each
    finding is still re-verified against the current source before it is relied on.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:1-120
  IMPACT: The review works from the owner's actual ticket, including its acceptance criteria and evidence
    index, instead of a summary.
  NEXT: Verify F1 against crystallizer_configuration.py (E1, E4), crystal_analyzer.py (E2) and the facade
    wiring (E3), reading the full functions behind each range.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:07:13Z
  TYPE: FACT
  CLAIM: F1, F2 (code half) and F3 hold at 66939dfe8 (these files are unchanged in the working tree).
    F1: the configuration getter defaults site_package_dependency_descent to False; the facade threads it
    with the user roots into SpellCrystal; _custody_descends stops only site_package custody when it is
    off, and the walk then records the module as a leaf (path, kind, distribution provenance, no source
    read, no dependencies); the raw analyzer and SpellCrystal default to True. F2: with_defaults() (the
    builder and the bootstrap loader's default path too) sets user_source_root_paths to the resolved cwd,
    and SpellCrystal falls back to cwd when no roots are passed; the chain is synthetic -> user_source ->
    site_package -> unknown, first match wins; user_source matching is plain is_relative_to over the user
    roots with no site-packages or .venv exclusion, and user_source always descends. Two consequences the
    ticket does not state: a .venv module classified user_source also gets a SHA256 custody fingerprint
    (site packages make no claim), so it enters drift checks, and with retain_user_sources=True its text
    is retained in the record. F3: SpellCrystal takes the root module from sys.modules or
    inspect.getmodule and its path from resolve_module_path (synthetic path, else __file__, else find_spec
    origin); dependencies come from source imports; the roots only classify - with_user_source_root_paths
    never touches sys.path or reads the roots.
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:382-404
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:788-832
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:994-1020
  - src/melder/crystallizer/crystallizer.py:1708-1719
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:260-290
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:499-570
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:740-927
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:1283-1321
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:1361-1425
  - src/melder/crystallizer/crystal_analysis/custody/user_source_custody_strategy.py:109-148
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:124-190
  - src/melder/crystallizer/crystals/spell_crystal.py:153-161
  - src/melder/crystallizer/crystals/spell_crystal.py:255-377
  IMPACT: D3 is wider than descent: a nested .venv also changes what the record fingerprints and retains.
  NEXT: Re-run the D3 probe in scratch space with a .venv inside the working directory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:08:16Z
  TYPE: MEASURE
  CLAIM: The D3 probe reproduces F2 on CPython 3.14.7t in VM scratch space (nothing in the repository was
    touched): a project dir with a .venv inside it (no pip), a package probe_pkg in that venv's
    site-packages importing probe_dep, and src/app_mod.py importing probe_pkg, analyzed through
    CrystalAnalyzer.analyze_spell_root from the venv's interpreter. User roots = cwd, descent off:
    probe_pkg and probe_dep classify user_source, the walk descends into probe_dep, and both get SHA256
    custody fingerprints. Roots = cwd/src, descent off: probe_pkg is a site_package leaf, probe_dep is never
    walked, no fingerprints. Roots = cwd/src, descent on: both are walked as site_package, still no
    fingerprints. The descent knob therefore never sees a nested .venv when the user root contains it.
    The owner's checkout has such a directory (.venv_new at the repository root), so running Melder from
    there under with_defaults() would classify that environment's packages as user source.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:576-618
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:740-927
  - src/melder/crystallizer/crystal_analysis/custody/user_source_custody_strategy.py:119-148
  IMPACT: D3 needs an owner decision; it is not an analysis-depth detail but a custody boundary question.
  NEXT: Verify F4 by reading MutationResearch.source_view and its live-disk fallback in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:21:30Z
  TYPE: FACT
  CLAIM: F4, F5 and F6 hold at 66939dfe8, and the supported command surface is inventoried. F4: source_view
    takes a module only from the crystal's module_targets, answers from recorded carriers (synthetic, then
    retained user text), else reads module_to_path from the live disk with no kind check; record_module puts
    every walked module, site-package leaves included, into module_targets and module_to_path, so with
    descent off a recorded installed leaf is still readable (drift only where a fingerprint exists; the read
    needs an active crystallizer). F5: assert_allowed is an exact (module, qualname) lookup at registration
    only; the builder AST-scans the source tree and names every module "melder.<path>", so a fork under
    another top-level package name is not guarded at all, and a class added to a melder-named fork is
    guarded only after the asset rebuild regenerates the committed manifest. F6: create_lane anchors by
    recording the anchor lane id and node identity; the new lane starts empty and nothing is copied; lanes
    have zero runtime footprint and the journal's acts have no merge, rebase or checkout. Command surface:
    the frame ACL is enforced on direct frame/conduit/spell fetches; every research_* verb (reads and the
    codegen room's create_lane/join/synthesize) enters _entered_command_action with frame_name=None, which
    is RiftGate admission plus memory only, so research commands are gated by room type, not by any frame
    ACL. Codegen execute builds its namespace from the frame's compiled codegen ACL (no projection: imports
    off); import roots are an allowlist when non-empty plus a denylist; safe has imports off, precision and
    hybrid allow stdlib lists (hybrid adds pathlib, inspect, csv, time), permissive adds os, shutil,
    subprocess, sys, importlib, io, socket and tempfile and allows dynamic access, mutation, reflection and
    dunder access, full_access has no allowlist; no profile names melder in a deny list. __builtins__ is the
    full builtins dict minus the profile's denylist, and no denylist contains open.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1819-1897
  - src/melder/mutation_research/mutation_research.py:1899-2049
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py:283-310
  - src/melder/aether/spellbook/bind/bind.py:35-108
  - src/melder/_build_assets/_bind_guard/_builder.py:169-250
  - src/melder/mutation_research/research_set/research_set.py:974-1080
  - src/melder/mutation_research/research_set/research_lane.py:144-212
  - src/melder/mutation_research/research_set/transition_entry.py:15-36
  - src/melder/nexus/rift/command_system/command_system.py:20-77
  - src/melder/nexus/rift/command_system/command_system.py:1051-1112
  - src/melder/nexus/rift/command_system/capability_command_system.py:1298-1323
  - src/melder/nexus/rift/command_system/codegen_command_system.py:669-737
  - src/melder/nexus/rift/command_system/codegen_command_system.py:1061-1098
  - src/melder/nexus/rift/codegen_system/codegen_system.py:295-342
  - src/melder/nexus/rift/codegen_system/codegen_system.py:404-475
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:89-195
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:82-109
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:1-99
  - src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:56-125
  - src/melder/nexus/acl/configurations/profiles/codegen/permissive_profile.py:100-128
  IMPACT: D2 so far: no existing ACL denies a core change as such. Recorded core source is readable through
    research commands; source writes and installs are reachable from permissive and full_access codegen.
    Whether safe or hybrid validation stops open(...).write(...) is UNKNOWN: open is in the namespace, and
    the validator's AST, name-resolution and attribute strategies are not yet read.
  NEXT: Read the codegen validator strategies, then probe open(...) under the safe and hybrid configurations
    in VM scratch space (no repository file written).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:26:37Z
  TYPE: MEASURE
  CLAIM: Agent code run through the codegen room can read and write files under every codegen profile,
    safe included. Probe on CPython 3.14.7t (-X gil=0) in a VM scratch copy of the tree, using the setup
    of the integration matrix (Nexus, codegen Rift, frame "ops", begin_codegen_change().use_profile(...),
    create_frame_link, then command_system.execute_codegen): "handle = open(<scratch path>, 'w');
    handle.write('x')" is accepted and writes the file under safe, hybrid, hybrid+precision, permissive and
    full_access; "open(<core file>).read()" returns all 64109 characters of bind.py under all five;
    pathlib writes pass under hybrid, permissive and full_access and are refused only by the import gate
    (safe: imports off; precision: pathlib not allowlisted). "import melder" is refused by the import
    allowlist under safe, hybrid, precision and permissive and accepted under full_access; "import
    subprocess" is accepted under permissive and full_access. Cause in source: __builtins__ is the full
    builtins dict minus the denylist, no profile denies open, and no validator strategy looks at open
    calls or at non-dunder method calls. The safe profile's own contract says it "denies ... writes, and
    dangerous capability escalation", which the runtime does not do for the filesystem.
  EVIDENCE:
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:19-36
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:82-109
  - src/melder/nexus/acl/frame_acl_compiler.py:600-630
  - src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:10-48
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:83-99
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_attribute_access_strategy.py:87-128
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:85-127
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:99-149
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py:87-138
  IMPACT: The proposed "agents read the core; core changes denied by default" does not hold today for
    source files: any codegen room can rewrite core .py files the process can write. This is a CONFLICT
    with the safe profile's documented posture, it is a pre-existing behaviour, and it is the first input
    to D2. Nothing was changed; the probe wrote only to VM scratch.
  NEXT: Probe whether __import__("subprocess") bypasses the import denylist under hybrid (the import gate
    reads only import statements and hybrid does not deny __import__).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T11:27:09Z
  TYPE: MEASURE
  CLAIM: Under hybrid and hybrid+precision, a __import__ call bypasses the codegen import gate. Same probe
    setup as Note 10: "loaded = __import__('<module>'); result = str(loaded)" is accepted and returns the
    module for subprocess, socket, importlib and melder under hybrid, hybrid+precision and permissive -
    the first three are exactly the roots hybrid's deny list names. Only safe refuses it ("Builtin
    '__import__' is not allowed"), because the compiler adds __import__ to the denied builtins only when
    imports are disabled. The import strategy inspects import statements only; the builtin strategy
    denies only listed names; hybrid's and precision's builtin deny lists omit __import__; the name and
    attribute strategies allow a non-denied builtin Name. So hybrid's and precision's import allowlists and
    deny lists constrain import statements, not imports.
  EVIDENCE:
  - src/melder/nexus/acl/frame_acl_compiler.py:600-630
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:73-99
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:89-195
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:85-127
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:244-265
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:39-60
  IMPACT: A second CONFLICT for D2: the hybrid and precision postures promise no subprocess, socket or
    importlib and do not enforce it; with Note 10, an agent in a hybrid room can import subprocess and
    run pip or edit installed core files. The existing matrix tests only import statements, which is
    why neither gap shows in the suite. Pre-existing behaviour; nothing changed.
  NEXT: Write the characterization regression suite (custody, descent, source_view, bind guard, lanes,
    codegen gate) and run it with the GIL off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T11:32:45Z
  TYPE: PLAN
  CLAIM: Regression suite for this review (owner, chat 2026-10-10: "make sure you put a regression test suite
    just incase"). Tests only; no source, configuration or ACL change. Characterization tests pin what the
    code does today, so a change made after D1-D8 has to update them on purpose; the two contract gaps
    (Notes 10-11) are written as the documented contract under xfail(strict=True), so the suite stays green
    now and fails loudly when someone fixes a gap without removing its marker. Five new files:
    (1) unit crystallizer/crystal_analysis/test_custody_boundary_characterization.py - nested .venv under the
    user root is user_source, walked and fingerprinted with descent off or on; a src-only root makes it a
    site-package leaf (walked as site_package only with descent on, never fingerprinted); retention keeps
    the nested venv's text only in the first case; user roots never extend sys.path; with_defaults() uses
    cwd and descent off. (2) unit spellbook/bind/test_internal_registration_identity.py - a user subclass
    of an internal class registers, an instance of one is refused, the guard keys on the (module,
    qualname) strings (a forked "melder_fork" identity passes, a user class claiming a melder identity is
    refused), every manifest module is rooted at melder. (3) integration crystallizer/
    test_recorded_leaf_source_read_integration.py - with descent off a recorded site-package leaf is still
    read from the live disk by source_view and by a codegen room's research_source under the safe profile,
    while its unwalked interior answers unknown_module. (4) integration mutation_research/
    test_research_lane_runtime_isolation_integration.py - an anchored lane starts empty and leaves the
    live selection, residency and meld result unchanged. (5) integration aether/
    test_codegen_core_boundary_integration.py - import melder is refused except under full_access, hybrid
    refuses import statements of its denied roots, and the strict xfails: safe refuses open(..., "w"),
    hybrid and precision refuse __import__ of denied roots. Then tests_components.md (preservation baseline
    first), the ticket, and the llm_support and asset rebuilds with their checks.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:204-219
  - tests/unit/melder/crystallizer/crystal_analysis/test_crystal_analyzer.py:601-702
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:19-60
  - tests/integration/melder/aether/test_non_resolvable_graph_replay.py:58-117
  - tests/integration/melder/mutation_research/test_mutation_research_root_integration.py:138-171
  - tests/unit/melder/test_melder_registration_guard.py:22-69
  IMPACT: Every finding F1-F6 plus the two codegen gaps gets a test that fails if the behaviour moves; no
    existing test is edited.
  NEXT: Write file (1) and run it with the GIL off in the repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:44:18Z
  TYPE: MEASURE
  CLAIM: The regression suite of Note 12 is written and green with the GIL off (CPython 3.14.7t, -X gil=0):
    in the repository the five new files run 28 passed and 5 xfailed (custody 9, guard identity 5, leaf
    source read 2, lane isolation 1, codegen boundary 11 + 5 strict xfails). Each strict xfail fails on its
    own assertion ("assert True is False" on accepted) under --runxfail, and the markers carry
    raises=AssertionError, so a setup error cannot pass for the known gap. Mutants in a VM scratch copy,
    each restored after its run, show the tests bite: user_source refusing site-packages paths (a "site
    roots win" D3 change) fails 4 custody tests; a guard that walks the MRO fails the subclass test;
    source_view skipping site-package leaves fails both leaf tests; denying open under safe and __import__
    under hybrid/precision turns all 5 xfails into XPASS(strict) failures while the 11 characterizations
    still pass. Neighbouring tiers in the copy: unit crystallizer, spellbook/bind, registration guard and
    mutation_research 1158 passed; integration crystallizer and mutation_research 340 passed, 3 xfailed
    (pre-existing); integration aether 785 passed, 5 xfailed (the new ones). One earlier aether run failed
    57 tests with OSError because the VM's shared /sessions disk had 0 bytes free (other sessions); I
    removed my own pytest temp dirs and pycache, moved the scratch copy to /tmp, and the rerun was green.
  EVIDENCE:
  - tests/unit/melder/crystallizer/crystal_analysis/test_custody_boundary_characterization.py:1-345
  - tests/unit/melder/spellbook/bind/test_internal_registration_identity.py:1-141
  - tests/integration/melder/crystallizer/test_recorded_leaf_source_read_integration.py:1-221
  - tests/integration/melder/mutation_research/test_research_lane_runtime_isolation_integration.py:1-115
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:1-203
  IMPACT: F1-F6 and both codegen gaps are now pinned; a D1-D8 change has to touch these tests on purpose,
    and closing either gap is reported by the suite. No existing test or source file was changed.
  NEXT: Update tests_components.md for the five files (preservation baseline first), then write the boundary
    matrix and the D1-D8 decision request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:49:49Z
  TYPE: FACT
  CLAIM: tests_components records the suite: each new file joins its cluster's key files with a Protects line
    (Crystallizer Unit, Spellbook Runtime And Binding Unit, Aether Integration, Crystallizer Integration and
    MutationResearch Integration clusters), the five code-map entries are measured from disk, the core set is
    214 paths (the union and the map agree), the tier and tree counts they change are recounted (789 test
    modules: unit 476 of 479 .py, integration 157 of 164; trees unit crystallizer 47, unit spellbook 146,
    integration aether 44, crystallizer 17, mutation_research 3), and a handoff entry is added. The
    preservation multiset loses only the recounted lines; the index is regenerated and --check is OK (2915
    lines); the portability and absolute-path greps are empty and every cited path exists. tests_architecture
    states no count that moved. Separately, D8's "Phase 1 baseline" is not a document in this repository: the
    only *.md naming a Phase 1 baseline or scope is this ticket, and "Phase 1" elsewhere is the compiler's
    first phase - so it is probably a MelderOps or owner document (UNKNOWN).
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:914-942
  - context_compass/system_docs/tests_components.md:957-1001
  - context_compass/system_docs/tests_components.md:1271-1345
  - context_compass/system_docs/tests_components_index.md:1-25
  IMPACT: The test map follows the suite, so the review's protections are findable from the packaged documents;
    D8 needs the owner to name the Phase 1 document.
  NEXT: Write the boundary matrix and the D1-D8 decision request with one recommendation each.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T11:52:21Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner decisions D1-D8, with the review's recommendations (full text in "Decision Request D1-D8"):
    D1 the protected core is the `melder` package as an identified distribution, MelderOps declaring its own,
    the guard manifest kept as the registration list; D2 fix the two codegen gaps first as their own tasks,
    then deny the core's top-level packages as import roots below full_access, decide whether research reads
    pass the view ACL, and use an OS boundary (separate process, read-only mounts) for real file protection;
    D3 the environment wins - user_source skips the interpreter's site roots and sys.prefix - with a
    record-version note; D4 research branch = native lane, fork = source-control fork, linked by lane
    metadata (repository, base revision, artifact digest); D5 separate grants, owner-only promotion to
    production and installation, every approval journaled; D6 the upstream commit is the selection unit;
    D7 wheel from the fork into a fresh environment, restart, Crystallizer checkpoints for state, rollback by
    reinstall plus restore; D8 decisions land in src_architecture and src_components, and the owner names the
    Phase 1 document, which is not in this repository.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:147-200
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:262-321
  IMPACT: No core-protection code, configuration or ACL change happens until the owner answers; the two codegen
    gaps are recorded defects either way, and their strict xfails report the fix when it lands.
  NEXT: Owner answers D1-D8 or redirects; meanwhile rebuild llm_support and the assets with their checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T11:56:39Z
  TYPE: MEASURE
  CLAIM: Rebuilt last, on CPython 3.14.7t, with no notch (no source changed): _build_asset_runner.py wrote the
    three asset families at v0.2.8228 (bind guard 622, agent documentation 462, system documents 4) and --check
    prints three OK lines; llm_support/_builder.py --include-untracked rewrote the tests bundle (src and other
    unchanged) and --check --include-untracked prints three OK lines. The tracked-only --check reports tests
    STALE until the owner adds the new test files to git (these five and the two from scan_bind). After the
    rebuild, GIL off: version, public surface, registration guard, build_assets, llm_support and system-document
    tests 272 passed, 1 skipped; the five review files 28 passed, 5 xfailed. No .git/index.lock was left.
  EVIDENCE:
  - src/melder/_build_assets/_build_asset_runner.py:380-399
  - llm_support/_builder.py:860-880
  IMPACT: Assets and bundles are current with the suite and the test map; the lane waits only on the owner.
  NEXT: Owner: answer D1-D8 or redirect, git add the five test files, commit and push; Windows tiers and
    hosted CI are the owner's.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T12:06:36Z
  TYPE: DECISION
  CLAIM: Owner direction (chat 2026-10-10, addressed to melder_1): the recommendations match the intended
    direction - Melder's governed evolution operates on explicitly approved application source, while installed
    dependencies, virtual environments, site-packages and native/binary extensions stay outside the mutation
    scope (still imported and used through supported interfaces, never rewritten or hot-mutated). Before any
    implementation the review becomes a concrete contract: (1) eligible source by explicit permitted roots and
    ownership/configuration rules - location inside a project never establishes eligibility; (2) exclusions for
    nested environments, installed packages, generated/build artifacts and native extensions, with resolved-path
    and symlink checks against escape; (3) discovery, reading, modification, generation, installation and
    promotion as separate permissions, with an owner-controlled approval and promotion path; (4) validation,
    change records, rollback and compatibility, naming what can and cannot be rolled back; (5) positive and
    negative regression cases (legitimate changes, excluded dependencies, nested environments, escape attempts,
    failed-change recovery); (6) evolution scope kept separate from security isolation - profile filtering is
    not an OS sandbox, Notes 10-11 stay defects until fixed and verified, and expected failures document them
    without establishing protection; (7) D1-D8 mapped one by one to the contract, the remaining decisions and
    the acceptance evidence, with the missing Phase 1 baseline identified rather than assumed. Not approval to
    implement the recommendations, commit or push; unrelated accepted work stays separate from unresolved
    protection claims.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:262-321
  IMPACT: The lane reopens for a specification pass only: the contract is written into this ticket; no source,
    configuration, ACL or test-behaviour change, no commit or push.
  NEXT: Read how custody normalizes roots and module paths (symlinks, case, hard links) and how native
    extensions and generated files classify today, as evidence for contract items 1-2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T12:20:15Z
  TYPE: FACT
  CLAIM: Custody classifies on symlink-resolved paths at analysis time and on nothing else, so it cannot serve as
    evolution eligibility. (1) Roots: the configuration and the analyzer resolve each root with non-strict
    Path.resolve() (a missing root is accepted), dedupe by Path equality and fall back to the working directory;
    nothing checks whether a root contains or sits inside an environment. (2) Module paths: __file__ or the
    find_spec origin is resolve()d, and the strategies re-resolve best-effort (raw path on error), so a module is
    classified by its link target. No file in src/melder reads pyvenv.cfg, sys.prefix or base_prefix,
    EXTENSION_SUFFIXES, st_nlink, lstat or is_symlink. (3) user_source claims ANY path under a root - native
    extensions, generated and build files, a nested environment - and reads text only from .py/.pyi, so a native
    extension under a user root is user_source with no text, no fingerprint and no binary identity. (4)
    site_package claims a path under a site root or any resolved path whose text contains "site-packages" or
    "dist-packages". (5) A dependency that does not descend (site_package with descent off, unknown always) is
    recorded as a leaf and never popped, and distribution provenance and binary identity are harvested only for
    popped nodes: under the shipped default an installed dependency of user code records path, kind and extension
    but no distribution provenance, and no dependency records a binary identity (the walk-level provenance test
    runs the raw analyzer, descent on). (6) The physical-source cache reuses a fingerprint while (mtime_ns, size)
    is unchanged, so a same-size rewrite inside one mtime tick keeps the old hash until the stat moves.
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:1059-1097
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:499-570
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:770-927
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:1005-1054
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:1361-1425
  - src/melder/crystallizer/crystal_analysis/custody/source_custody_strategy.py:250-307
  - src/melder/crystallizer/crystal_analysis/custody/user_source_custody_strategy.py:119-148
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:124-156
  - src/melder/crystallizer/crystal_analysis/custody/binary_unknown_custody_strategy.py:175-236
  - src/melder/crystallizer/crystal_analysis/physical_source_cache.py:99-198
  - tests/unit/melder/crystallizer/crystal_analysis/test_distribution_provenance.py:118-161
  IMPACT: Contract items 1-2 need their own permitted-root list checked on resolved paths, explicit exclusions
    (environment markers, site roots, extension suffixes, generated trees), a link check at the write site and
    change records that hash bytes afresh; item 4 cannot lean on recorded distribution provenance under the default.
  NEXT: Probe in /tmp scratch: a symlink into site-packages inside a root, a hard link, a .so under a root, a
    foreign venv (pyvenv.cfg) outside the roots, Windows case handling, and provenance for a descent-off leaf.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T12:22:22Z
  TYPE: MEASURE
  CLAIM: The scratch probe confirms Note 18 on CPython 3.14.7t (-X gil=0; analyzer run from the /tmp scratch copy of
    src, data under /tmp/cc_probe_t2/world, nothing in the repository touched). User root = the project, descent
    off: a symlink inside the root to a package in an outside site-packages classifies site_package (by target); a
    symlink outside the root to a file inside it classifies user_source; a hard link inside the root to an installed
    module classifies user_source while its other name classifies site_package - one inode, st_nlink 2 - and a
    write through the root name changed the installed file; a stdlib .so copied into the root, a nested venv with
    pyvenv.cfg and a build/ file inside the root all classify user_source; a foreign venv outside the root
    classifies site_package in its site-packages and unknown elsewhere; a missing root is accepted. Walk level: the
    .so under the root is user_source with no fingerprint and no binary identity. An installed dependency of user
    code (pytest, user root src/) records a distribution-provenance row with descent on and none with descent off.
    The physical-source cache served the old hash after a same-size rewrite with the mtime restored, while a fresh
    read hashed the new text. Pure paths: Windows containment ignores case (C:\Users\Mark vs c:\users\mark), POSIX
    does not, and is_relative_to is lexical - "C:\proj\src\..\..\outside\x.py" reads as inside "C:\proj".
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:770-927
  - src/melder/crystallizer/crystal_analysis/custody/user_source_custody_strategy.py:119-148
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:124-156
  - src/melder/crystallizer/crystal_analysis/physical_source_cache.py:99-198
  IMPACT: Eligibility must be decided on strictly resolved paths, refuse links (symlinked components and
    st_nlink > 1) for modification, exclude environments by marker rather than by name, and hash bytes directly at
    record time; a lexical or name-based check would admit an escape, and the default record cannot serve as the
    dependency-version baseline for compatibility checks.
  NEXT: Read the code that writes files today (ProtocolCrafter writers, materialize_codegen and SyntheticModule
    physical files, the crystallizer and creation caches, the build assets) and the restore all-or-nothing path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T12:26:16Z
  TYPE: MEASURE
  CLAIM: A third gap beside Notes 10-11: the codegen room hot-replaces modules of the running process, core and
    dependencies alike, under every profile that accepts the module's code. materialize_codegen is an advertised
    codegen command gated by RiftGate admission and static validation of the code only; module_name is checked for
    identifier legality, nothing else. SyntheticModule.publish_to_sys_modules assigns sys.modules[name]
    unconditionally and sets the parent package attribute, and execute_source runs the text with the interpreter's
    full builtins (validation is static only). Probe (/tmp scratch copy, process-local, CPython 3.14.7t -X gil=0),
    under safe and hybrid alike: "Bind = None" materialized as melder.aether.spellbook.bind.bind replaced the core
    module (import_module and the parent attribute return the SyntheticModule); a new melder.injected_probe joined
    the melder package; stdlib csv was replaced; the installed name pytest was shadowed (import pytest gives the
    SyntheticModule). A materialize over an existing name whose exec fails, and cleanup of a successful replacement,
    both leave the name absent from sys.modules - the original module is not restored. Separately, the only Melder
    code that writes source files is ProtocolCrafter (write_protocol_module_from_source_file and
    write_joined_protocol_module overwrite <dir>/<name>.py; add_/remove_protocol_..._interface_file rewrite a given
    file in place): any path, no root, link or eligibility check, non-atomic, no record or backup. Melder's own
    caches are written atomically (temp file then replace) under the melder PACKAGE root - inside site-packages
    when installed - never relative to the working directory.
  EVIDENCE:
  - src/melder/nexus/rift/command_system/codegen_command_system.py:100-103
  - src/melder/nexus/rift/command_system/codegen_command_system.py:739-888
  - src/melder/crystallizer/synthetic_module.py:859-975
  - src/melder/crystallizer/synthetic_module.py:1047-1094
  - src/melder/crystallizer/synthetic_module.py:1189-1259
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:327-381
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:432-558
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:2411-2437
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:111-175
  - src/melder/utilities/caching_system/caching_system.py:860-892
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1676-1742
  IMPACT: The owner's "dependencies are never hot-mutated" and "core changes denied by default" do not hold for
    in-process modules today; generation must be its own permission with a target-namespace policy that refuses
    existing names, protected roots and installed import names, and recovery must restore the prior module object.
    A read-only environment mount (D2 item 4) would also block Melder's own caches unless they move.
  NEXT: Read the restore all-or-nothing path and the checkpoint/journal surfaces for what can be rolled back, then
    write the contract and the D1-D8 mapping into the ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T12:27:24Z
  TYPE: FACT
  CLAIM: What Melder can roll back today, for contract item 4. (a) A recorded world: a checkpoint-chain restore
    replays through public verbs with fresh identities and is all-or-nothing within one run - preflight blockers
    refuse before anything is built, and a stage failure tears down every unit that run built, newest first and
    best-effort per unit, then raises with the cause chained; it builds a new world beside or after the old one and
    never reverts a live world in place, and synthetic modules already in sys.modules are skipped, not replaced.
    (b) Research organization: restore_network validates the snapshot, then swaps lanes and residence wholesale;
    the journal is forward-only (the restore is journaled as an event) and snapshots age out of a bounded ring
    (KeyError). (c) Selection: a notch runs in a transaction, parks the outgoing member and promotes a parked one,
    journals the promotion forward and re-gates the index so the next meld recompiles; the outgoing member stays
    parked, so a second notch re-selects it; borrowers' contracted maps are not fanned out. Not rolled back by
    Melder: source files (no versioning; ProtocolCrafter overwrites in place), installed packages, hot-replaced
    modules (Note 20), external effects (remote stores reached through ExternalPersistenceManager, network,
    processes, files outside any root), and objects already built - whether a notch back retires instances made
    under the newer member was not traced (UNKNOWN).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:396-405
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:666-786
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2907-2987
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:3047-3069
  - src/melder/mutation_research/research_set/research_set.py:2224-2251
  - src/melder/mutation_research/research_set/research_set.py:2323-2400
  - src/melder/aether/spellbook/spellbook.py:3701-3841
  - src/melder/crystallizer/synthetic_module.py:951-975
  IMPACT: The contract's rollback clause can promise selection reversal (notch back), research-organization
    restore and restore of a recorded world into a fresh runtime; source and environment rollback belong to git
    and the installer, and the change record must say so per change.
  NEXT: Write the Governed Evolution Contract (items 1-7) and the D1-D8 mapping into this ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T12:31:47Z
  TYPE: DECISION
  CLAIM: Write the governed-evolution contract (C1-C6, one clause set per owner item 1-6) and the D1-D8 mapping
    (item 7) into this ticket as two new sections before the verification plan, citing Notes 18-21. Per item 6,
    also reword this review's own deliverables so nothing reads as protection: the codegen test file's title
    ("Codegen room boundary around Melder's core") and its three tests_components lines ("the codegen room's
    boundary around the core", "codegen core boundary") become a characterization label; assertions, markers and
    every other file stay as they are. D-20 (Note 20) is recorded in the contract and not pinned by a new test -
    that is the owner's call. Six existing tests named as pins for P4, R5 and R7 were run green in the /tmp
    scratch copy (GIL off, 6 passed). Then regenerate the tests_components index under the preservation gate, rerun
    the five review files, and rebuild llm_support and the assets last with their checks. No src, ACL,
    configuration or test-behaviour change; no commit or push.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:853-879
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:1-19
  - context_compass/system_docs/tests_components.md:1289-1299
  - context_compass/system_docs/tests_components.md:2772-2776
  IMPACT: The owner gets the contract asked for, and the review's wording matches its own rule that expected
    failures and characterizations establish no protection.
  NEXT: Insert the two sections into the ticket and check line lengths and the section order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T12:35:37Z
  TYPE: MEASURE
  CLAIM: The contract pass is written and checked. This ticket now carries "Governed Evolution Contract" (C1-C6:
    eligibility by an owner-authored allowlist of permitted roots, exclusions and write-time path checks, six
    separate permissions with an owner-controlled lifecycle, validation, change records, rollback and
    compatibility, 27 symptom-named cases, and the scope-versus-isolation rule with defects D-10, D-11 and D-20),
    "D1-D8 Mapping to the Contract" (clauses, remaining owner decisions and acceptance evidence per decision; D3
    narrowed to analysis and D8's Phase 1 baseline named as missing) and "Commit Grouping" (scan_bind's accepted
    work, this review, and the shared generated surfaces in separate commits). Per item 6 the codegen test file's
    title now reads "What the codegen room's profiles stop around Melder's core today" with a "characterization,
    not protection" paragraph, and its three tests_components lines say characterization; the preservation
    multiset shows exactly those 10 lines replaced by 11, the code-map entry is remeasured (206 lines), the index
    is regenerated and --check prints OK (66 sections, 2916 lines), and the portability grep is empty. GIL off in
    the repository: the five review files 28 passed, 5 xfailed. No src, ACL or configuration change.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:310-569
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:1-23
  - context_compass/system_docs/tests_components.md:1289-1300
  - context_compass/system_docs/tests_components.md:2201-2206
  - context_compass/system_docs/tests_components.md:2773-2777
  IMPACT: The owner can review a concrete contract with every claim tied to a note; the review's own wording no
    longer reads as protection.
  NEXT: Update this ticket's checklists, handoff summary and state (review), sync the board row, then rebuild
    llm_support and the assets last with their checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T12:39:53Z
  TYPE: MEASURE
  CLAIM: Rebuilt last, CPython 3.14.7t, no notch (no source change): _build_asset_runner.py wrote the three asset
    families at v0.2.8228 (agent documentation 462, bind guard 622, system documents 4) and --check prints three
    OK lines; llm_support/_builder.py --include-untracked rewrote the tests bundle and manifest.json (src and
    other unchanged) and --check --include-untracked prints three OK lines. GIL off afterwards: llm_support,
    build_assets, system-document and registration-guard tests 255 passed, 1 skipped. The ticket moved to review
    and the board row to review/handoff; no .git/index.lock was left. Owner-owed: review of the contract and the
    D1-D8 answers, routing of D-10, D-11 and D-20, the commits per "Commit Grouping", Windows tiers and hosted CI
    (Not run).
  EVIDENCE:
  - src/melder/_build_assets/_build_asset_runner.py:380-399
  - llm_support/_builder.py:860-880
  - context_compass/attention_board.md:182-182
  IMPACT: Assets and bundles are current with the reworded test file; the lane waits on the owner only.
  NEXT: Owner reviews the contract (C1-C6) and the D1-D8 mapping, answers or redirects.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T12:53:01Z
  TYPE: DECISION
  CLAIM: The owner accepted the review and its direction (chat 2026-10-10: "I accept the review and the agreed
    direction: governed evolution should operate on explicitly approved application source, with installed
    dependencies, virtual environments, site-packages and native/binary extensions outside the mutation scope";
    earlier the same turn: "I accept review, everything is good, and make sure to turn in your tickets"). Asked:
    finalize and hand back the tickets and evidence - the reviewed and tested revision and environment, diffs, test
    commands and results with skips and expected failures, the D1-D8 disposition, remaining decisions and the
    missing baseline; keep the filesystem-access and dynamic-import gaps open until fixed and verified; document
    any further gap separately with reproducer, impact and evidence; keep the contract; list implementation
    follow-ups with priorities and acceptance criteria. Not resolved by this: the protection gaps. Not authorized:
    the proposed implementation changes, commits or a public push. Plan, in order: rerun the verification set on
    the final tree with skip and xfail reasons; write the evidence pack (artifacts/core_protection_review_20261010/)
    and one per lane for scan_bind; open three backlog defect tickets (D-10, D-11, D-20, the last with its own
    reproducer); write the hand-back section here; turn in this ticket and the scan_bind ticket of the same request
    (board and artifact-board sync, scan_bind's patch folder archived); rebuild assets and llm_support last. The
    eleven older melder_1 review tickets are not part of this request and stay open.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:310-569
  - context_compass/attention_board.md:181-182
  IMPACT: The review closes with its defects still open in tickets of their own, so the next bounded work can be
    assigned from them without reading this ticket's history.
  NEXT: Run the final verification set on the final tree in the background and collect the logs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T13:24:15Z
  TYPE: MEASURE
  CLAIM: Final verification on the hand-back tree, the whole tests/ tree with the GIL off (CPython 3.14.7
    free-threading build, -X gil=0, sys._is_gil_enabled() False; pytest 9.1.1; Ubuntu 22.04.5 VM on the owner's
    machine; repository at HEAD 66939dfe8 on codex_features2 plus 40 modified and 12 untracked files, all from
    this request's two lanes - 1747 more tracked files differ from HEAD only in line endings). 13,639 passed,
    32 skipped, 17 xfailed, 2 xpassed, 0 failed: tests/unit 9020 passed, 3 skipped, 7 xfailed; component
    spellbook 799; component aether, crystallizer, mutation_research and utilities 1502 passed, 23 skipped,
    1 xfailed; integration spellbook 613 passed, 2 skipped, 2 xpassed; integration crystallizer 273 passed,
    3 xfailed (seven groups - one file exceeds the 180 s call limit); integration mutation_research 67;
    integration aether 785 passed, 5 xfailed; integration conduit 275; live_sim and multithreading 55 passed,
    1 xfailed; experimentation 250 passed, 4 skipped. The focused scan set is 409 passed and the review suite 28
    passed, 5 xfailed. The 5 review xfails are the strict D-10/D-11 markers; every other skip, xfail and xpass
    is pre-existing and unrelated (opt-in timing experiments, retired src_graph.json fixtures, the
    process-wide spell-id graft conflict, package-helper coroutine cases, two non-strict fault-B xpasses).
    Windows tiers and hosted CI: Not run (owner).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-08_review_core_protection_fork_aware_updates_task.md:310-569
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:1-23
  IMPACT: The hand-back states one tested tree, by HEAD plus a per-file SHA256 manifest, with no failing test
    in any tier.
  NEXT: Write the evidence packs (logs, diffs, manifests, probes) under context_compass/artifacts/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T13:35:11Z
  TYPE: MEASURE
  CLAIM: Evidence packs written beside the tickets: artifacts/core_protection_review_20261010/ (environment, the 19
    completed run logs with their junit XML, the results and skip/xfail tables, the node-id splits, both lanes'
    diffs, the probes with their outputs, the diff tool) and artifacts/scan_bind_option_parity_20261010/ (its diffs
    and four lane logs). Logs are stored as .txt because the repository ignores *.log; the VM home reads as ~; the
    two crystallizer runs killed at the 180 s call limit are not kept (their split reruns are). Every probe was rerun
    from the scratch copy of this tree (13:33Z, CPython 3.14.7t, -X gil=0) and reproduces its note: D-10, open()
    writes under all five profiles and reads all 64109 characters of bind.py (Note 10); D-11, __import__ of
    subprocess, socket, importlib and melder is accepted under hybrid, hybrid+precision and permissive and refused
    only under safe (Note 11); D-20, a core module, a new melder.* name, a stdlib module and an installed name are
    materialized under safe and hybrid, and a failed materialize or a cleanup leaves the name absent (Note 20); the
    custody, provenance, stat-cache and path results of Note 19; the nested-.venv classification of Note 8. The file
    manifests, the tree delta and the READMEs are written last, after the turn-in moves and the rebuild, so their
    hashes describe the final tree.
  EVIDENCE:
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe_output.txt:1-28
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe2_output.txt:1-19
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize_output.txt:1-11
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_materialize_fail_output.txt:1-6
  - context_compass/artifacts/core_protection_review_20261010/probes/probe_custody_output.txt:1-23
  - context_compass/artifacts/core_protection_review_20261010/probes/d3_probe_output.txt:1-9
  IMPACT: Each open defect has a runnable reproducer with recorded output in the repository for its own ticket.
  NEXT: Re-read the codegen builtins, import and validation sources behind D-10 and D-11, then draft their tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T13:37:02Z
  TYPE: FACT
  CLAIM: The source behind the three open defects, re-read at 66939dfe8 (these files are unchanged in the working
    tree) before their tickets are written. D-10: the safe deny list (SAFE_DENIED_BUILTIN_NAMES, which hybrid and
    precision reuse) does not name open; the runtime __builtins__ is vars(builtins) minus that list; the builtin
    strategy refuses only a call whose callee is a denied Name, and name resolution admits every builtin not denied
    - so open() passes the static and the runtime gate under every profile, against safe's documented "denies ...
    writes". D-11: the compiler adds __import__ to the denied builtins only when imports are disabled; the import
    strategy inspects Import and ImportFrom statements only; the reflection strategy catches importlib.import_module
    and reload only as attribute calls on a Name - so hybrid's and precision's allow and deny roots bind import
    statements, not imports. D-20: materialize_codegen validates the code and checks module_name for dotted-identifier
    legality only; publish_to_sys_modules assigns sys.modules[name] unconditionally and attaches the parent package
    attribute; execute_source execs with the module dict as globals and no filtered __builtins__; cleanup removes only
    its own object and never restores what it displaced, and the command's failure path calls that cleanup.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:73-99
  - src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:10-48
  - src/melder/nexus/acl/frame_acl_compiler.py:600-630
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:82-109
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:85-127
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:89-171
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:99-149
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_reflection_policy_strategy.py:148-220
  - src/melder/nexus/rift/command_system/codegen_command_system.py:739-888
  - src/melder/crystallizer/synthetic_module.py:462-531
  - src/melder/crystallizer/synthetic_module.py:901-949
  - src/melder/crystallizer/synthetic_module.py:1047-1094
  IMPACT: Each defect ticket can name the exact seam a fix changes and the test that proves it, without this ticket.
  NEXT: Write the three draft backlog tickets (D-10, D-11, D-20) from the task template.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T13:41:22Z
  TYPE: FACT
  CLAIM: The three open defects now have draft tickets of their own in tickets/tasks/backlog/, each with symptom,
    reproducer, cause, impact, ticket contract, the owner questions that gate it, symptom-named acceptance criteria
    and an opening note: D-10 deny_file_access_under_safe_codegen (open() under safe; whether hybrid and precision
    deny it too is the owner's call, because they share safe's deny list), D-11
    enforce_import_policy_on_dynamic_imports (__import__ under hybrid, precision and permissive; static refusal of
    the name, a runtime import guard, or both), D-20 refuse_materializing_over_live_modules (a generation namespace
    the owner declares, refusal of existing, protected, stdlib and installed names, exits that leave sys.modules as
    found, and the room's builtins for materialized code). All three are p1, draft, owner-held and unassigned; each
    reproducer is registered on artifact_board.md as a backlog row pointing into this review's evidence pack. Nothing
    in src changed; D-10 and D-11 stay pinned by their strict xfails, D-20 by its reproducer only.
  EVIDENCE:
  - context_compass/tickets/tasks/backlog/2026-10-10_deny_file_access_under_safe_codegen_task.md:1-170
  - context_compass/tickets/tasks/backlog/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:1-176
  - context_compass/tickets/tasks/backlog/2026-10-10_refuse_materializing_over_live_modules_task.md:1-190
  - context_compass/artifact_board.md:98-100
  IMPACT: The next bounded work can be assigned from these tickets without reading this review's history.
  NEXT: Write the hand-back section of this ticket (revision, environment, results, D1-D8 disposition, follow-ups).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T14:05:31Z
  TYPE: MEASURE
  CLAIM: Turned in. This ticket and scan_bind_option_parity moved to tickets/tasks/completed/; the board lost both
    active rows and their details and gained two closed anchors (the two oldest dropped, cap 12); artifact_board.md
    cleared scan_bind's three patch rows and recorded the archived patch folder and both evidence packs, beside the
    three backlog reproducer rows of Note 29. Rebuilt last on CPython 3.14.7t: _build_asset_runner.py wrote the three
    families at v0.2.8228 and --check prints three OK lines; llm_support/_builder.py --include-untracked reports all
    bundles unchanged and --check --include-untracked three OK lines (the tracked-only check stays STALE for tests
    until the owner adds the new test files); all 46 generated files kept their bytes. After the rebuild, GIL off:
    llm_support, build_assets, registration guard, public surface, version and system-document tests 291 passed and 1
    skipped; this review's suite 28 passed and 5 xfailed (D-10, D-11); the scan focused set 409 passed. The packs'
    file manifests and tree/tree_delta.txt were regenerated last: 40 modified files, the owner's staged
    release_docs/0.2.8227.md, and untracked tests, tickets, patch docs and the two packs; 1747 files differ from HEAD
    only in line endings. No .git/index.lock left; nothing committed or pushed.
  EVIDENCE:
  - context_compass/artifacts/core_protection_review_20261010/README.md:1-93
  - context_compass/artifacts/core_protection_review_20261010/runs/v13_post_rebuild.txt:1-11
  - context_compass/artifacts/core_protection_review_20261010/tree/tree_delta.txt:1-27
  - context_compass/attention_board.md:183-199
  - context_compass/artifact_board.md:95-106
  IMPACT: The hand-back is complete: tickets closed, evidence in the repository, defects open in their own tickets.
  NEXT: none in this ticket; the owner assigns D-10, D-11 and D-20 and answers D1-D8 in their own lanes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
DONE (melder_1, 2026-10-10T13:44:41Z). The owner accepted the review and its direction (Note 25): governed
evolution changes explicitly approved application source only. The Hand-back section carries the tested revision,
environment, results, D1-D8 disposition, open gaps and prioritized follow-ups; the evidence pack is
artifacts/core_protection_review_20261010/. D-10, D-11 and D-20 stay OPEN in their own backlog tickets until
fixed and verified. Nothing in src/ changed; nothing committed or pushed (owner).

REVIEW (melder_1, 2026-10-10). F1-F6 hold at 66939dfe8 (Notes 7-9). Three defects go beyond the original
findings: `open` reads and writes files under every codegen profile (D-10, Note 10), `__import__` loads the
roots hybrid and precision deny (D-11, Note 11), and materialize_codegen replaces live core and dependency
modules with no way back (D-20, Note 20) - so no existing surface denies a core change today. The
regression suite pins F1-F6 and holds D-10 and D-11 under strict xfail (Notes 12-14); D-20 is not pinned.
At the owner's request (Note 17) the review is now a contract: "Governed Evolution Contract" C1-C6, "D1-D8
Mapping to the Contract" and "Commit Grouping" (sections above; Notes 18-23). Owner: review the contract
and answer or redirect D1-D8; route D-10, D-11 and D-20 if wanted; commit per the grouping. Nothing in src/,
configuration or ACLs changed; the only non-ticket edits of this pass are the codegen test file's docstring
and its tests_components lines.

The shipped Crystallizer default stops recursion at site-package leaves, but user-root precedence can
include nested .venv packages, and recorded source can remain readable. These are discovery/read
behaviors, not core write authorization. Review an explicit read-only core policy plus intentional
lineage-preserving forks and selective upstream updates. Native research lanes are real; their mapping
to Git and package artifacts is undecided. Keep runtime mutation, file edits, and installation separate.
Only this review ticket has been created; implementation and architecture changes need later approval.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
- Review category: future design; Phase 1 baseline unaffected.
- Companion: 2026-10-08_restore_scan_bind_option_parity_task.md
- Publication: none; no commit, push, PR, or external issue created.
<!-- END USER-DEFINED: project_fields -->
