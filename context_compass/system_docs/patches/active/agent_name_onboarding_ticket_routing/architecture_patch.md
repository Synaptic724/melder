# Architecture Patch: Agent Name Onboarding Ticket Routing

## Patch Scope and Non-Goals
Scope:
- require agent naming on every onboarding/re-onboarding certification cycle
- carry `AGENT_NAME` into attestation
- add `Agent Name` metadata to ticket templates/docs
- add `agent_name` to the attention board schema
- allow multiple assigned names in one field

Non-goals:
- changing the approval token `CERTIFY: APPROVED`
- changing `artifact_board.md` unless later required
- broad legacy ticket migration

## Changed-Components Matrix
| Component | Current gap | Required delta |
|---|---|---|
| onboarding/certification docs | no mandatory name capture | require `AGENT_NAME` on every cycle and in attestation |
| ticket templates/docs | no assigned-name field | add `Agent Name` metadata and multi-agent semantics |
| attention board docs/live schema | no name field beyond `owner` | add `agent_name` while keeping `owner` |

## Interface and Boundary Deltas
- Keep `owner` as executor/runtime owner.
- Add `agent_name` as assigned user-facing identity.
- Use `AGENT_NAME:` in attestation/certification flows.
- Allow multiple names as a comma-separated list inside `Agent Name` /
  `agent_name`.

## Cross-Component Invariants
- Certification still requires `CERTIFY: APPROVED`.
- Every onboarding/re-onboarding cycle asks for a name.
- Ticket metadata and board schema use consistent identity semantics.

## Migration/Rollout Order
1. create workflow state
2. create patch docs
3. update onboarding/certification identity flow
4. update ticket/template/board identity flow
5. reread changed docs and summarize final behavior

## Rollback Strategy
- If board retrofitting becomes too risky, keep the schema docs and templates,
  then add the live board change separately.

## Validation Expectations and Evidence Plan
- changed docs reread cleanly
- templates show `Agent Name`
- attention board shows `agent_name`
- attestation/certification docs show `AGENT_NAME`

## Ticket Coverage Map
- epic:
  - `tickets/epics/2026-04-25_add_agent_name_to_onboarding_and_ticket_routing_epic.md`
- investigation:
  - `tickets/stories/2026-04-25_investigate_agent_name_onboarding_ticket_routing_story.md`
  - `tickets/tasks/2026-04-25_investigate_current_agent_identity_touchpoints_task.md`
- implementation:
  - `tickets/stories/2026-04-25_implement_agent_name_onboarding_ticket_routing_story.md`
  - `tickets/tasks/2026-04-25_implement_agent_name_attestation_and_certification_task.md`
  - `tickets/tasks/2026-04-25_implement_agent_name_ticket_template_and_board_schema_task.md`

## Unknowns and Decision Requests
- UNKNOWN: whether `artifact_board.md` should later mirror the new identity field
