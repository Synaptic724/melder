# new_skills

## Why this folder exists

Staging area for skills authored here that are intended to be PORTED into the
`context_compass` repo proper. Keeping them in one folder makes the port a directory
copy instead of a scavenger hunt across `agent_onboarding/`.

Nothing in this folder is wired into a `SKILLS.MD` chain yet. These documents are
therefore NOT active skills - they are drafts with a settled contract, readable by any
agent who needs them but not yet part of any role's required readset.

## Contents

- `system_doc_index_generation.md` - how to CRAFT a line-range index over a large
  system document.
- `system_doc_index_usage.md` - how to CONSUME one: verify it, then slice only the
  ranges you need.

Read the generation skill first. The usage skill depends on its schema.

## Porting checklist

When these move into `context_compass` proper:

- [ ] Place under `agent_onboarding/default/engineer/skills/` (both are
      engineer-layer concerns, not general-layer).
- [ ] Add both paths to `agent_onboarding/default/engineer/SKILLS.MD`.
- [ ] Decide the tier: the USAGE skill is a strong candidate for **required baseline**
      (it is how an agent should read the big docs at all), while the GENERATION skill
      is naturally **on-demand**, triggered when an indexed document changes.
- [ ] Remove this folder once the port is verified.
