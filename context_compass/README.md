# context_compass

Purpose
- Central control plane for planning, execution memory, and architecture context.
- Durable work state is ticket-first; board is routing-only.

Core operating model
- Active work lives in `epics/`, `stories/`, and `tasks/`.
- Detailed state belongs in active ticket `## Notes` with evidence ranges.
- `attention_board.md` routes to the active ticket and next action only.
- Closed work moves to matching `*/completed/` folders.

Primary docs
- `AGENTS.MD`: repository operating contract.
- `SKILLS.MD`: ticket depth and documentation strategy.
- `WORKFLOW.md`: ticket lifecycle and closure rules.
- `CONTEXT_COMPACTION.md`: compaction/handoff policy.
- `agent_onboarding/`: onboarding policy modules.
- `architecture/`: C4 architecture docs.
- `components/`: C3/C2/C1 component docs.

Policy anchors
- Unknowns gate: `agent_onboarding/agent/general/skills/unknowns_gate_reference.md`.
- Certification and environment gate (`active`/`inactive`): `AGENTS.MD` and
  `agent_onboarding/agent/general/skills/self_certification.md`.

Packaging model
- `core/`:
  - Reusable process mechanics.
- `profiles/`:
  - Repository-specific overlays.
- `config/context_compass_config.yaml`:
  - Ticket microcycle strict/relaxed policy switch.

Completed (legacy archive)
- 2026-01-17 - Melder DI resolution contract docs (see `completed/2026-01-17_melder_di_resolution_contract_docs_task_completed.md`).
- 2026-01-17 - Melder DI contract decision alignment (see `completed/2026-01-17_melder_di_contract_decisions_doc_alignment_task_completed.md`).
- 2026-01-17 - Melder scan bind module work (see `completed/2026-01-17_melder_scan_bind_module_task_completed.md`).
- 2026-01-18 - Melder src architecture doc (see `completed/2026-01-18_melder_src_architecture_doc_task_completed.md`).
- 2026-01-18 - Melder src components doc (see `completed/2026-01-18_melder_src_components_doc_task_completed.md`).
