# career_selection

Purpose
- Enforce the general-first onboarding order and explicit career selection.
- Treat skills as capability artifacts (not ad-hoc prompts) with progressive disclosure.
- Use the selected career to scope the rest of onboarding.

When to use
- At the start of every onboarding session (before any career-specific skills).
- When the user changes the agent’s responsibilities mid-session.

Required behavior
- Always read the shared baseline first:
  - onboarding/agent/general/SKILLS.md
- Ask the user which career to activate.
- Use explicit prompt language, for example:
  - "Which career should this agent use: developer, analyst, or project_manager? If you
    don't have a preference, I will default to developer."
- Valid careers: developer, analyst, project_manager.
- If the user has no preference, default to developer and state the default explicitly.
- After selection, read:
  - onboarding/agent/careers/<career>/SKILLS.md
- Use the career choice to determine which examples to open in
  onboarding/agent/careers/<career>/examples/.

Onboarding command usage
- After the career is chosen, create the agent profile:
  - python context_compass/system/ai_restricted/agent_management/agent_onboarding_start.py \
    --repo-root . --agent-id <agent_id> --agent-role <career>
- If defaulting to developer, you may omit --agent-role and state the default in the
  onboarding response.

Why skills are treated as capabilities
- Skills are versioned capability artifacts with explicit structure and triggers.
- The baseline skills exist to reduce ambiguity and enforce consistent workflows.
- Progressive disclosure prevents bloating context with unused documentation.

References
- context_compass/onboarding/agent/SKILLS.md
- context_compass/onboarding/user/README.md
