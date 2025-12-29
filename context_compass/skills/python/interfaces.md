# interfaces

Purpose
- Choose Protocol, ABC, or concrete types deliberately.

Rules
- Use Protocol for structural typing when multiple implementations are expected.
- Use ABC for shared behavior and explicit inheritance requirements.
- Use concrete types when there is a single stable implementation.
- Document the interface contract in the docstring, not just the type hints.
- Avoid widening types without a concrete compatibility reason.

Example
- Protocol: "Supports .acquire() and .release()" without forcing inheritance.
- ABC: "BaseLogger" enforcing cleanup and level setting.

Examples
- context_compass/examples/python/protocols_and_abc.py