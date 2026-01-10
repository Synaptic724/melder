# certification

Purpose
- Provide onboarding-owned facades for certification tooling.
- Keep onboarding entrypoints thin and delegated to ai_restricted tools.

Scripts
- python_certified.py -> context_compass/system/ai_restricted/agent_management/python_certified.py

Usage
- Finalize certification after approval:
  `python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"`

Notes
- Requires explicit approval token before running.
- Certification checks are enforced by the delegated tool.
