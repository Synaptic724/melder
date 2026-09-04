# Architecture patch: branch CI and final release qualification

- Patch ID: branch_ci_release_2026_09_04
- Task: TASK-2026-09-04-implement-branch-ci-release-validation

## Scope and non-goals
Introduce enforceable CI before branch merges and reuse the same checks at publication. Runtime
architecture is unchanged. Do not publish a package or invent dated candidate metadata in this change.

## Changed-components matrix
| Component | Before | After |
| --- | --- | --- |
| CI validation | Independent asset workflows; runtime tests only during publication | Central CI calls reusable asset/runtime/package jobs and reports a fail-closed final status |
| Release publication | Prod check at start; inline tests and package code | Fresh shared checks/build plus repeated prod and distribution verification before upload |

## Interface and boundary deltas
- ci.yml owns PR/permanent-branch triggers. Asset workflows expose workflow_call and manual dispatch.
- Runtime and distribution verification become reusable workflows with read-only permissions.
- A stdlib policy CLI handles branch routing, result aggregation, hygiene, and release-head checks.
- Branch ruleset JSON names the final CI status; deployment must wait for that check to exist remotely.

## Cross-component invariants
- A required job must report success; cancellation/failure/unexpected skip must block merge-ready.
- PR source/base policy checks repository identity for permanent-branch promotion.
- Feature-to-dev runs all supported test tiers on both supported OSes and a free-threaded interpreter.
- Promotion/release checks verify the actual selected checkout; no untested alternate ref is accepted.
- Release validation is fresh for that publication run; artifacts come from that same successful run.
- Only the publication job receives the pypi environment; the final prod check follows environment approval.
- A prod change during validation refuses publication at the last head check.

## Rollout order
1. Implement helpers, reusable workflows, and caller together.
2. Validate failure semantics, supported local runtime, packaging, and asset consistency.
3. Deploy workflows and observe the real named CI check before activating rulesets.
4. Add automatic promotion and dated-candidate scheduling as subsequent configured work.

## Rollback
Restore caller and helper workflows together. Remove a newly required check before removing its
workflow, otherwise merges lock. Keep existing/final release prod checks and publication isolation.

## Validation plan
Behavior tests cover invalid routes, forged promotion heads, failed/skipped results, unsupported
runtime, stale prod, and malformed distributions. Parse/lint YAML with actual action semantics;
exercise packaged documents and the supported local test tiers. Report remote-only gaps explicitly.

## Ticket coverage
The implementation task owns all rows above. Its analysis predecessor supplies live settings and timing.

## Unknowns
GitHub-hosted execution of the new workflows and named-check availability require deployment.
Scheduled release date/version and promotion-App credentials were not supplied.
