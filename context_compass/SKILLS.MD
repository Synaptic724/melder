# SKILLS.md - Context Compass Ticketing System

## Purpose
This document defines how to create deep, descriptive GitHub-style tickets for epics, stories, and tasks in `epics/`, `stories/`, and `tasks/`.
The goal is durable, high-context planning that survives compaction and handoffs.

## Onboarding Docs (Required)
Follow the onboarding standards in:
- `agent_onboarding/agent/general/README.md`
- `agent_onboarding/agent/engineer/README.md`
These are mandatory alongside the local rules in this folder.
Certification must include the execution environment (`active` or `inactive`); git commands are active-only.

## Ticket Types (Use Templates)
- Epic: big project or cross-cutting initiative with multiple stories.
- Story: medium scope, user- or system-facing slice that can stand alone or live under an epic.
- Task: small, single deliverable that can stand alone.

Templates live in:
- `templates/epic_template.md`
- `templates/story_template.md`
- `templates/task_template.md`

## File Locations and Naming
- Epics: `epics/`
- Stories: `stories/`
- Tasks: `tasks/`

Naming convention (date-first, descriptive):
- `YYYY-MM-DD_<slug>_epic.md`
- `YYYY-MM-DD_<slug>_story.md`
- `YYYY-MM-DD_<slug>_task.md`

## Deep Descriptive Model (Required)
Each ticket must be specific, evidence-based, and durable. Avoid vague goals.

Required elements (use the template sections):
- Problem / Opportunity: concrete pain or measurable opportunity.
- Context: why now, and how this relates to current architecture.
- MRP Alignment: explain the holistic core being built.
- Goals / Non-Goals: what success is, and what is explicitly out.
- Scope Boundaries: in-scope vs out-of-scope details.
- Requirements: functional and non-functional expectations.
- Acceptance Criteria: observable outcomes that define done.
- Risks / Mitigations: realistic failure modes and defenses.
- Validation Plan: how correctness will be verified.
- Decision Log: record key decisions and rationale.
- Notes: active findings with `path:start_line-end_line` evidence pointers during execution.
- Context / Handoff Summary: current state + next steps for future context.

Ticket microcycle requirement:
- While executing any ticket, run a strict loop:
  `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
- Each meaningful finding must be documented immediately before further investigation.
- UNKNOWN is the default claim state until evidence promotes it to FACT.
- Evidence pointers in notes must include both start and end lines (`path:start-end`); use the same value for single-line evidence (`path:77-77`).

## Task Tracking Model (Required)
Use checkboxes and keep status in sync.

Epic requirements:
- Milestones are mandatory and use `- [ ]` checkboxes.
- Include tasks like: "Complete story <STORY-ID>" for every required story.
- Keep "Stories" and "Tasks" sections current.

Story requirements:
- Include a task checklist with explicit task IDs.
- Every acceptance criterion must be testable or observable.

Task requirements:
- Include a step-by-step checklist and a done checklist.
- Record validation status explicitly ("Not run" if not run).

## Ticket Closure (Required)
Before moving any ticket to its completed folder:
- Walk through what was delivered.
- Ask the user to confirm the acceptance criteria are met.
- Close the ticket only after explicit confirmation.

## GitHub-Style Formatting Rules
- Title line is required and outcome-focused.
- Metadata is a short bullet list at the top.
- Use short paragraphs and bullet lists for scanability.
- Link epic <-> story <-> task by ID in metadata and checklists.

## Architecture and Components Documentation (Required)
Use the C4 mapping and component templates to preserve system understanding.

Docs and templates:
- `architecture/README.md`
- `architecture/src_architecture.md`
- `architecture/tests_architecture.md`
- `components/README.md`
- `components/src_components.md`
- `components/tests_components.md`

Rules:
- Keep C4 architecture in `architecture/` and C3/C2/C1 detail in `components/`.
- Maintain both ASCII and Mermaid diagrams for readability.
- Record information sources, invariants, and lifecycle/cleanup notes.
- Update these docs when architecture or component boundaries change.
- Before major work, review these docs to re-orient and update them using the information-gathering steps in the README files.

## Context Compaction / Handoff
Before any context compaction or major handoff:
- Re-open `attention_board.md` and confirm active routing rows match ticket truth.
- Update the "Context / Handoff Summary" section of active tickets.
- Review `AGENTS.MD`, `WORKFLOW.md`, and `CONTEXT_COMPACTION.md`.
- Re-read `agent_onboarding/agent/general/README.md` and `agent_onboarding/agent/engineer/README.md`.
- Ensure open questions and next steps are captured in the tickets.

## Policy Extensions (Required Skills)
These policy modules extend the core rules and must be followed:
- `agent_onboarding/agent/general/skills/agent_stance.md` - team stance, tone, and professional baseline.
- `EXECUTION_CONTRACT.md` - subordinate execution contract, mission-intent execution model, and conflict/strategy protocol.
- `agent_onboarding/agent/general/skills/mrp_policy.md` - MRP-only strategy with MLP for UI contexts.
- `agent_onboarding/agent/general/skills/context_gold.md` - context-first ritual and compaction re-entry.
- `agent_onboarding/agent/general/skills/documentation_standards.md` - deep, non-handwavy documentation rules.
- `agent_onboarding/agent/general/skills/active_documentation.md` - mandatory active-ticket notes with evidence anchors.
- `agent_onboarding/agent/general/skills/context_window_budget.md` - strict microcycle scope control and meaningful-finding note gates.

## DO NOT ASSUME / Unknowns Gate
Rule: No Unverified Claims.
Any statement that is not directly supported by evidence must be treated as UNKNOWN.

Evidence means at least one of:
- A specific source file reference (preferred: file + symbol/method/class name).
- A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be explicitly labeled UNKNOWN (or added to an Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:
- Mark it UNKNOWN.
- Identify the most likely evidence target (file + symbol).
- Investigate, then update the doc (or leave it UNKNOWN).

