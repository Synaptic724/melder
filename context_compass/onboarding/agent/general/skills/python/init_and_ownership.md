# init_and_ownership

Purpose
- Keep initialization explicit and ownership clear.

Constructor / Initialization Requirements
When adding or modifying __init__ / initialization flows:
* Maintain explicit ownership: it must be clear what this object owns and what it only references.
* Initialize fields deterministically and explicitly.
* If an attribute is optional, initialize it to None (or a clear sentinel) and document that contract.

Rules
- Initialize all attributes deterministically in __init__.
- Optional fields must be set to None (or a sentinel) and documented.
- Document ownership: who cleans up what and when.
- Avoid hidden shared state; prefer instance ownership for resources.
- If a field is injected and not owned, document that contract explicitly.

Checklist
- Every field is initialized.
- Ownership and lifecycle are described in the docstring.
- Optional values are explicitly None.

Examples
- context_compass/onboarding/agent/general/examples/python/cleanup_patterns.py