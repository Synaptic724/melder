# self_certification

Purpose
- Force a structured self-certification before any execution.

Canonical Contract (verbatim from context_compass/AGENTS.md)
Certification gate (mandatory)
- Complete skills/self_certification.md and wait for approval.
- Request approval using skills/user_approved_certification.md.
- Do not use tools or edit files until the user replies exactly: CERTIFY: APPROVED.
- After approval, run: python python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"
- Tools that mutate repo state must refuse to run unless the agent profile certification_state is CERTIFIED.

Rules
- Before any tool use or implementation, output a filled self-certification.
- Before requesting certification, read every skill listed in context_compass/SKILLS.md.
- Do not proceed until the user replies CERTIFY: APPROVED.
- If the user replies CERTIFY: CHANGES, update this document and re-request approval.
- While uncertified, only ask clarifying questions or revise this document.
- Do not write files, apply patches, or run tools before approval.
- Exception: context_compass/tools/onboarding_bundle.py may be run before certification to gather docs.

Required template (fill in every section)
```
Self-Certification

Task Understanding (My Words):
- ...

Inputs Provided:
- ...

Skills Read (all entries in context_compass/SKILLS.md):
- ...

Outputs Expected:
- ...

Constraints / Requirements:
- ...

Non-Goals:
- ...

Step-by-Step Execution Plan:
1) ...
2) ...

Assumptions:
- ...

Risks / Failure Modes:
- ...

Open Questions (if any):
- ...

Requirement-to-Plan Mapping Checklist:
- [ ] Requirement: ... -> Planned action: ...
- [ ] Requirement: ... -> Planned action: ...

Stop Condition:
- I will not proceed until the user replies CERTIFY: APPROVED.
```

References
- context_compass/schemas/certification_state.schema.json
