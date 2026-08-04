# [Ticket] Workstation Codegen Guardrails and Capability Manifest

**Type:** Architecture / Philosophy Ticket

**Status:** Active Planning Context

**Labels:** `aetheric-rift`, `workstation`, `codegen`, `ast`, `capability-manifest`, `acl`, `imports`, `mutation-lane`, `safety`

---

## 1. Intent

Capture the concrete model for codegen-first workstation execution:

- Guardrails are on by default.
- Object access is capability-bound, not global-Python-bound.
- AST and symbol checks classify safe execution vs mutation routing.
- Import behavior is policy-governed and owned by session runtime context.

This ticket extends prior codegen lane decisions with the practical mechanics
needed for consistent implementation.

---

## 2. Core Decision Summary

1. Codegen is a first-class interaction style for workstation sessions.
2. Guardrails are default-on and deny-by-default.
3. Capability access is derived from ACL intersection, compiled as a session manifest.
4. AST validation checks language shape; symbol validation checks what objects are touched.
5. Runtime dispatch re-checks ACL and lifecycle on every operation.
6. Imports are optional, explicitly allowlisted, and owned by execution context.
7. Mutation-class operations route to mutation lane; they do not silently run in safe lane.

---

## 3. Core Objects

### 3.1 CapabilityManifest

Compiled per session from:

- Object ACL
- Domain ACL
- Profile ACL

It defines:

- Allowed symbols (alias -> object_ref).
- Allowed members per symbol (methods/attrs).
- Allowed operations per member (invoke/read/write/create/destroy/etc.).
- Allowed imports (if any).
- Policy profile (`strict`, `relaxed`, `unsafe`).

`CapabilityManifest` is the authoritative allowlist for codegen validation and runtime execution.

### 3.2 CodeBlock

Immutable executable submission unit:

- `block_id`
- `source`
- `source_hash`
- `manifest_id`
- `policy_hash`
- `created_by`
- `created_at`

Code is executed by `block_id`/`source_hash`, not by a mutable name.

### 3.3 ExecutionContext

Session-owned runtime map used for execution:

- Bound object handles from manifest.
- Optional approved module handles/import bindings.
- Controlled globals/locals surface.

No ambient/global process namespace is exposed by default.

---

## 4. Validation and Routing Pipeline

1. `register_codeblock(source, session_id)` -> compute hash and metadata.
2. Build or resolve active `CapabilityManifest` for the session.
3. Parse source into AST.
4. Apply AST node policy:
- Allow approved structural nodes (`If`, `For`, `Assign`, `Call`, etc.).
- Deny dangerous nodes (`Import` when not allowed, dynamic escapes, uncontrolled reflection).
5. Resolve symbols and member access against manifest:
- Every `Name`/`Attribute`/`Call` target must map to an approved symbol/member.
6. Classify lane:
- Safe lane if only approved operations over existing capabilities.
- Mutation lane if structural/new-object/graph-modifying patterns are requested.
7. Execute through governed dispatcher with per-call ACL/lifecycle re-check.
8. Emit audit events and incidents as needed.

---

## 5. Import Governance Model

Default stance:

- Prefer capability injection over Python import statements.

Optional import enablement:

- Profile + domain + object policy must allow imports.
- AST accepts only allowlisted import forms.
- Runtime importer enforces same allowlist.
- Dynamic import escapes are denied (`__import__`, importlib reflection paths not explicitly allowed).

Imports are runtime-context assets, not agent-owned ambient privileges.

---

## 6. Policy Tiers

### 6.1 Strict (Default)

- Deny-by-default.
- Minimal AST node set.
- No dynamic import/reflection escapes.
- Only explicitly exposed symbols/members allowed.

### 6.2 Relaxed

- Expanded AST and import allowlist for trusted lab profiles.
- Still manifest-bound and fully audited.

### 6.3 Unsafe

- Explicit opt-in only.
- Session-scoped and time-bounded.
- Elevated profile required.
- Mandatory incident/audit markers at enable/disable boundaries.

---

## 7. Mutation Research Tie-In

Codegen is not blocked by mutation research; it routes into it when needed.

Safe lane:

- Uses existing approved runtime capabilities.

Mutation lane:

- Add/remove/change/create operations.
- Mutation lock and control-plane gates apply.
- Validation + promote/rollback pipeline applies.

This preserves fast AI iteration while keeping structural change governed.

---

## 8. API-Style Operation Set (Conceptual)

- `register_codeblock(session_id, source) -> block_id, source_hash`
- `validate_codeblock(block_id) -> validation_report`
- `classify_codeblock(block_id) -> safe | mutation`
- `execute_codeblock(block_id, args?) -> result`
- `describe_manifest(session_id) -> capability_manifest`
- `set_policy_mode(session_id, strict|relaxed|unsafe)` (gated)

This operation set can be exposed by wrappers without changing Rift's core boundary.

---

## 9. Audit and Incident Requirements

Each run should emit:

- `session_id`, `domain_id`, `profile_id`
- `block_id`, `source_hash`
- `manifest_id`, `policy_hash`
- Lane classification
- Operation trace summary
- Deny reasons and incident links (if any)

No execution path should bypass observability.

---

## 10. Acceptance Criteria (Conceptual)

This ticket is accepted when the team agrees:

- Guardrailed codegen is the default workstation model.
- Capability manifests are the source of truth for what code may touch.
- AST policy and symbol policy are separate, both required checks.
- Import permissions are explicit and runtime-owned.
- Safe and mutation lanes are enforceably distinct.
- Execution identity (`block_id`/hash/policy/manifest) is auditable end-to-end.

