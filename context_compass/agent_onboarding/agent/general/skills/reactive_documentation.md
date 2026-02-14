# reactive_documentation

Purpose
- Keep compaction-proof breadcrumbs while work is in flight.
- Capture broad findings quickly without losing source truth.
- Preserve momentum by recording only what must be re-read later.

When to use
- Any investigation, debugging pass, architecture revalidation, or broad repo trace.
- Immediately after discovering a core claim that could be lost after compaction.

Core stance
- Do not dump raw transcript sludge as durable memory.
- Do not over-structure notes into heavy ceremony.
- Use targeted, broad claims plus exact evidence pointers.
- Start from UNKNOWN and promote to FACT only with evidence.

Canonical storage
- Tickets are first-class memory:
  - `Notes` for in-flight findings captured during execution.
  - `Decision Log` for accepted facts and decisions.
  - `Unknowns` for unresolved or blocked claims.
  - `Context / Handoff Summary` for current state and next actions.
- `attention_board.md` is routing-only state, not detailed finding storage.
- Avoid creating side memory stores unless explicitly requested.

Reactive capture protocol (mandatory)
1) Classify claim type:
   - `FACT`: verified directly in source.
   - `UNKNOWN`: not yet verified or ambiguous.
   - `HYPOTHESIS`: explicit idea/opinion awaiting evidence.
   - `DECISION`: explicit direction and rationale.
   - `PLAN`: concrete next implementation slice.
   - `MEASURE`: validation/profiling result.
   - `RISK`: risk that needs mitigation follow-up.
2) Record one broad claim line:
   - 1-2 sentences, general and scannable.
3) Attach evidence pointers:
   - `path/to/file.py:line` (preferred), plus symbol when useful.
4) Mark re-read priority:
   - `REQUIRED`: must reopen on next session.
   - `HELPFUL`: context only.
5) Add compaction usefulness score:
   - `SCORE_0_TO_10` (improve notes below 8 before proceeding).
6) Record one concrete next action:
   - single step that moves verification or implementation forward.

Entry template
- `TYPE`: FACT | UNKNOWN | HYPOTHESIS | DECISION | PLAN | MEASURE | RISK
- `CLAIM`: <broad finding>
- `EVIDENCE`: <path:line>, <path:line>
- `REREAD`: REQUIRED | HELPFUL
- `SCORE_0_TO_10`: <0-10>
- `NEXT`: <single concrete step>

Quality bar
- Prefer targeted claims over narrative replay.
- Every durable claim needs `file:line` evidence.
- No evidence means mark it `UNKNOWN`.
- Keep entries append-only when possible.

Anti-patterns
- Long logs with no evidence.
- Broad assertions with no file pointers.
- Rewriting history instead of adding incremental updates.
- Treating speculative reasoning as fact.
- Implementing directly from UNKNOWN/HYPOTHESIS without evidence-backed promotion.

Re-entry checklist
- Open active ticket handoff summary first.
- Re-open entries marked `REREAD: REQUIRED`.
- Resume from the most recent `NEXT` action.

References
- `agent_onboarding/agent/general/skills/memory_management.md`
- `agent_onboarding/agent/general/skills/active_documentation.md`
- `agent_onboarding/agent/general/skills/compaction_requirements.md`
- `WORKFLOW.md`
- `SKILLS.MD`
