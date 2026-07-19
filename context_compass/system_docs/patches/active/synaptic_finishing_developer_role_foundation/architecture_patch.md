# Architecture Patch: Synaptic Finishing Developer Role Foundation

## Patch Scope and Non-Goals
Scope:
- add a new user-defined role named `synaptic_finishing_developer`
- register the role in config and top-level role routing
- make the role inherit `engineer`
- make `src_architecture.md`, `src_components.md`, `graph_details_document.md`,
  and `readable_src_graph.json` mandatory baseline reads for the role
- add a dedicated documentation skill family and a dedicated testing skill
  family for finishing work
- add a dedicated finishing-role example pack and make those examples mandatory
  baseline reads for the role

Non-goals:
- changing `profiles.active_profile`
- rewriting the shared `engineer` or `qa_engineer` role semantics
- changing runtime source behavior in `src/melder/**`

## Changed-Components Matrix
| Component | Current gap | Required delta |
|---|---|---|
| config profile registry | no `synaptic_finishing_developer` entry | add profile lists, readme policy entry, allowed-post-onboarding entry, and role map |
| top-level role map | custom role not explicitly discoverable | add explicit role name and path-map entry |
| user-defined finishing role | does not exist | add folder, `SKILLS.MD`, and role-local docs |
| documentation skill surface | only generic/current synaptic documentation skills exist | add deeper finishing-specific documentation skills |
| testing skill surface | no finishing-role-specific unit/component/integration guidance exists | add deeper finishing-specific testing skills |
| example surface | only borrowed synaptic examples exist | add dedicated finishing-role examples and list them in baseline role reads |

## Interface and Boundary Deltas
- The new role MUST remain a user-defined overlay under
  `agent_onboarding/user_defined/`.
- The new role MUST inherit from `agent_onboarding/default/engineer/SKILLS.MD`.
- The new role MUST directly list the mandatory system docs in its active skill
  set instead of relying on `engineer` on-demand triggers.
- The new role MUST keep its mission narrow:
  public-library docstrings, comments, and tests.

## Cross-Component Invariants
- Shared engineer behavior stays parent-first and unchanged.
- The new role does not become the default active profile automatically.
- Documentation and testing skills stay separate families under the new role.
- Dedicated finishing-role examples stay part of the role baseline and do not
  rely on the old synaptic example files.
- The new role encodes slow, deep, multi-turn execution rather than one-shot
  completion posture.

## Migration/Rollout Order
1. create epic/story/task workflow state
2. create patch docs
3. register the new role in config and top-level role map
4. create the role skeleton and `SKILLS.MD`
5. author documentation skills
6. author testing skills
7. author dedicated finishing-role examples and add them to the role baseline
8. sync board and artifact state
9. reread the role chain and summarize final behavior

## Rollback Strategy
- If the role design starts requiring shared baseline edits, stop and keep the
  implementation inside a user-defined overlay only.
- If explicit top-level role registration proves redundant, preserve config
  registration and the user-defined folder while removing only the extra
  top-level listing.

## Validation Expectations and Evidence Plan
- config contains the new profile in all required lists and role map
- top-level `SKILLS.md` explicitly lists the new role
- new role `SKILLS.MD` inherits from `engineer`
- new role `SKILLS.MD` includes the mandatory system docs and both new skill
  families
- new role `SKILLS.MD` includes the dedicated example files as mandatory reads
- created docs reread cleanly and describe the intended role behavior

## Ticket Coverage Map
- epic:
  - `tickets/epics/2026-04-25_build_synaptic_finishing_developer_role_epic.md`
- investigation:
  - `tickets/stories/2026-04-25_investigate_synaptic_finishing_developer_inputs_story.md`
  - `tickets/tasks/2026-04-25_investigate_role_creation_and_finishing_skill_surface_task.md`
- implementation:
  - `tickets/stories/2026-04-25_implement_synaptic_finishing_developer_role_story.md`
  - `tickets/tasks/2026-04-25_register_synaptic_finishing_developer_role_task.md`
  - `tickets/tasks/2026-04-25_author_synaptic_finishing_documentation_skills_task.md`
  - `tickets/tasks/2026-04-25_author_synaptic_finishing_testing_skills_task.md`
  - `tickets/tasks/2026-04-25_author_synaptic_finishing_examples_task.md`

## Unknowns and Decision Requests
- UNKNOWN: whether the role should later absorb QA-story planning docs by
  reference or remain strictly finishing-local
