# Component Tests

Purpose:
Define the component test tier for this repository.

Definition:
Component tests exercise a small, real slice of the system (core objects and
their direct wiring) while stubbing or mocking external collaborators. They
sit between unit and integration tests and focus on internal contracts that
are hard to assert via pure unit tests but do not require full end-to-end
execution.

Guidelines:
- Use real core objects for the behavior under test.
- Stub external boundaries (scanners, validators, I/O, schedulers) as needed.
- Keep tests deterministic and self-contained.
- Prefer contract-level assertions over fragile implementation checks.
