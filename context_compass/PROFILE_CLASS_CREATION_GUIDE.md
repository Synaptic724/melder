Please get Codex to read this to help you make a class; this guide uses tokens and is not in normal skill paths except `new`.

# Profile Class Creation Guide

## Why this file exists
- This is a user-facing playbook for building and assigning profile classes.
- It is intentionally large and explicit so you can hand it to Codex during
  first-time onboarding.
- It is not meant to be loaded by every profile path.

## What context_compass is
- A code-development workflow system.
- A durable context system for AI-assisted engineering.
- A structure that keeps planning, execution, and handoff consistent.

## What it supports
- Any programming language.
- Codex-first workflows.
- Other AI agents, as long as they obey the same policy contracts.

## Recommended execution mode
- Use Codex with Extra High reasoning in this repository.
- Other reasoning modes are not yet validated here.

## Core concepts

### 1) Profile class
- A class/profile is a curated read path for behavior and skills.
- Profiles are route targets resolved by `router.roles.*` to `SKILLS.MD`.

### 2) Inheritance
- Parent profile docs load first.
- Child profile docs load last.
- Child profile `SKILLS.MD` should add deltas, not duplicate parent paths.

### 3) Default class
- This is the profile loaded after onboarding.
- For code work, `engineer` is the recommended default.

### 4) User-defined class
- A custom profile you create under `agent_onboarding/user_defined/`.
- Usually extends `engineer`.

## Current baseline classes
- `new`
  - first-time onboarding and class selection.
- `general`
  - system behavior, ticketing, process controls.
- `engineer`
  - code-development specializations and creation mechanics.
- `user_defined/*`
  - personal or team overlays.

## Where to configure classes
- `context_compass/config/context_compass_config.yaml`

Key areas in that file:
- `profiles.active_profile`
- `profiles.available_profiles`
- `profiles.user_defined_profiles`
- `profiles.onboarding.*`
- `router.roles.*`
- `router.profile_readme_policy.*`
- `SKILLS.MD` header inheritance:
  - `INHERITS_SKILLS_FROM: <skills_path|none>`

## Class creation checklist
- [ ] Choose class name.
- [ ] Create onboarding folder structure.
- [ ] Create profile `SKILLS.MD` file.
- [ ] Add class to config.
- [ ] Define `SKILLS.MD` inheritance header.
- [ ] Validate `SKILLS.MD` paths and overlap rules.
- [ ] Assign active/default class.

## Step-by-step: create a new class

### Step 1: Choose a class name
Example:
- `data_engineer`
- `frontend_engineer`
- `security_engineer`

Naming rules:
- lower_snake_case
- avoid spaces
- keep it short and descriptive

### Step 2: Create folder skeleton
Create this structure:

```text
context_compass/
  agent_onboarding/
    user_defined/
      <profile_name>/
        profile_overrides.md
        policies/
          <profile_name>_policy_overrides.md
        behavioral_guidelines/
          <profile_name>_behavior_overrides.md
        skills/
          <profile_name>_skill_overrides.md
```

You can add subfolders under `skills/` as needed.

### Step 3: Create profile SKILLS file
Create:

```text
context_compass/agent_onboarding/user_defined/<profile_name>/SKILLS.MD
```

SKILLS.MD rules:
- one relative path per line
- no empty lines
- inheritance header required for inheriting profiles:
  - `INHERITS_SKILLS_FROM: <skills_path|none>`
- no duplicated parent paths from inherited `SKILLS.MD`

Example:

```text
INHERITS_SKILLS_FROM: agent_onboarding/default/engineer/SKILLS.MD
agent_onboarding/user_defined/data_engineer/profile_overrides.md
agent_onboarding/user_defined/data_engineer/policies/data_engineer_policy_overrides.md
agent_onboarding/user_defined/data_engineer/behavioral_guidelines/data_engineer_behavior_overrides.md
agent_onboarding/user_defined/data_engineer/skills/data_engineer_skill_overrides.md
```

### Step 4: Register class in config
Edit `context_compass/config/context_compass_config.yaml`.

Minimum required edits:

```yaml
profiles:
  available_profiles:
    - data_engineer
  user_defined_profiles:
    - data_engineer

router:
  roles:
    data_engineer: agent_onboarding/user_defined/data_engineer/SKILLS.MD
```

### Step 5: Set active/default class
Set active class:

```yaml
profiles:
  active_profile: data_engineer
```

If this class should be selectable after first-time onboarding, update:

```yaml
profiles:
  onboarding:
    allowed_post_onboarding_profiles:
      - general
      - engineer
      - data_engineer
```

### Step 6: Validate class wiring
Run checks:

```powershell
rg -n "data_engineer" context_compass/config/context_compass_config.yaml
Get-Content context_compass/agent_onboarding/user_defined/data_engineer/SKILLS.MD
```

Validate `SKILLS.MD` path existence (manual method):
- open each path listed in the class `SKILLS.MD`
- confirm files exist and are readable

Validate overlap discipline:
- compare child `SKILLS.MD` lines against parent `SKILLS.MD` lines
- remove duplicates from child `SKILLS.MD`
- confirm child `SKILLS.MD` starts with inheritance header:
  - `INHERITS_SKILLS_FROM: <parent_skills_path>`

## Recommended class design patterns

### Pattern A: Strict overlay
- Keep default behavior in `general` + `engineer`.
- Put only preferences and deltas in user-defined class.

### Pattern B: Domain overlay
- Add domain-specific workflows (data, UI, infra).
- Keep shared code-quality rules inherited from `engineer`.

### Pattern C: Team policy overlay
- Add team conventions, review gates, and naming rules.
- Keep system mechanics unchanged.

## Anti-patterns to avoid
- Duplicating entire parent `SKILLS.MD` path lists in child classes.
- Putting shared system rules in user-defined profiles.
- Mixing onboarding docs into non-`new` flow without role intent.
- Setting `active_profile` to a class not in `available_profiles`.
- Forgetting to register `router.roles.<profile>`.

## Profile file templates

### profile_overrides.md

```markdown
# <profile_name> profile_overrides

Purpose
- Define user/team-specific profile behavior deltas.

Scope
- Applies only when active profile is `<profile_name>`.

Rules
- Keep this profile as a delta layer over `engineer`.
- Do not duplicate inherited baseline docs.
```

### policy override template

```markdown
# <profile_name>_policy_overrides

Purpose
- Add policy deltas for this profile.

Policy
- <rule 1>
- <rule 2>
```

### behavior override template

```markdown
# <profile_name>_behavior_overrides

Purpose
- Define behavior and communication deltas for this profile.

Behavior
- <behavior 1>
- <behavior 2>
```

### skill override template

```markdown
# <profile_name>_skill_overrides

Purpose
- Define skills specific to this profile.

Skills
- <skill 1>
- <skill 2>
```

## How onboarding transitions should work

### First-time entry
- Route into `new`.
- Explain system + profiles + config.
- Ask user to select steady-state default class.

### Post-onboarding entry
- Route directly to selected default class path order.
- If class inherits `engineer`, `SKILLS.MD` headers resolve
  `general` then `engineer` then custom.

## Recommended default class choice
- For code development, default to `engineer`.
- Use user-defined classes when you need preference/domain overlays.

## Fast operator checklist
- [ ] I know the class name I want.
- [ ] I created class folder + files under `user_defined`.
- [ ] I created `SKILLS.MD` under `agent_onboarding/user_defined/<profile_name>/`.
- [ ] I updated config profile lists and router role registration.
- [ ] I added the `SKILLS.MD` inheritance header.
- [ ] I set `active_profile` to target class.
- [ ] I validated `SKILLS.MD` paths and overlap contract.

## Troubleshooting

### Class does not load
Check:
- class exists in `profiles.available_profiles`
- role exists under `router.roles`
- class `SKILLS.MD` path is correct and readable

### Wrong docs load order
Check:
- `SKILLS.MD` inheritance header:
  - `INHERITS_SKILLS_FROM: <skills_path|none>`
- parent-first ordering resolved from `SKILLS.MD` inheritance headers
- path entries not duplicated across parent/child `SKILLS.MD` files

### Behavior looks unchanged
Check:
- active profile is what you think it is
- class docs are actually listed in class `SKILLS.MD`
- class docs contain real deltas, not empty placeholders

## File index
- `context_compass/config/context_compass_config.yaml`
- `context_compass/SKILLS.md`
- `context_compass/agent_onboarding/default/new/SKILLS.MD`
- `context_compass/agent_onboarding/default/general/SKILLS.MD`
- `context_compass/agent_onboarding/default/engineer/SKILLS.MD`
- `context_compass/agent_onboarding/user_defined/<profile_name>/SKILLS.MD`
- `context_compass/agent_onboarding/user_defined/`

## Final note
- Use this guide through `new` onboarding when creating a class.
- Keep class changes explicit, additive, and validated before switching
  defaults.
