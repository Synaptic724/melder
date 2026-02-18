

# Artifact Board

Purpose
- Canonical index of active artifact associations.
- Track artifact lifecycle decisions that support ticket execution.
- Keep `attention_board.md` ticket-only and free of artifact pointers.

Scope rules
- `attention_board.md` routes tickets only; do not add artifact paths there.
- Tickets remain canonical memory; this board is an association index.
- Add rows only when a ticket has one or more active artifact files.
- Every artifact row must include a ticket path and retention decision.

Disposition values
- `delete_on_close`: remove artifact when ticket closes.
- `retain_as_reference`: keep artifact with explicit reason.
- `promote_to_documentation`: convert artifact into durable docs.

## Active Artifact Links
| ticket | artifact_path | artifact_type | status | disposition | next | updated_at | reread |
|---|---|---|---|---|---|---|---|
| `tickets/epics/2026-02-18_skill_gate_first_compaction_measurement_loop_epic.md` | `artifacts/2026-02-18_skill_gate_first_compaction_success_model.md` | planning_spec | active | retain_as_reference | keep linked through discovery and implementation planning | 2026-02-18T16:53:27Z | REQUIRED |

## Active Artifact Details
- DATETIME: 2026-02-18T16:53:27Z
  TYPE: FACT
  CLAIM: Artifact captures the requested skill-gate-first scored compaction
    loop and is linked to the new epic as planning source of truth.
  EVIDENCE:
  - artifacts/2026-02-18_skill_gate_first_compaction_success_model.md:1-136
  - tickets/epics/2026-02-18_skill_gate_first_compaction_measurement_loop_epic.md:156-160
  IMPACT: Discovery and upcoming implementation are now anchored to a durable
    artifact instead of transient chat context.
  NEXT: keep artifact linkage updated as discovery decisions solidify.
  REREAD: REQUIRED

## Recently Cleared Artifacts
| ticket | artifact_path | disposition | reason | closed_at |
|---|---|---|---|---|
| `tickets/tasks/completed/2026-02-16_artifact_board_and_store_contract_task_completed.md` | `artifacts/2026-02-16_artifact_protocol_discovery_snapshot.md` | delete_on_close | ticket closed; disposition applied and artifact removed from active set | 2026-02-17T12:01:56Z |
