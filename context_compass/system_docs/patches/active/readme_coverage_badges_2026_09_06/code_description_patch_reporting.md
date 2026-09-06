# Code description: optional measurement, isolated upload

## Runner
Parse the existing required JUnit destination and an optional coverage XML destination.
Keep the original test argument list; append --cov=melder, --cov-branch and the requested XML output
only when opted in. Create its parent directory. Call pytest once and preserve its exit code.
Keep actual-process GIL verification before and after pytest, unchanged.

## Workflow
Each of the existing OS jobs opts in, retaining its coverage XML with a distinct run/attempt name.
After the full matrix succeeds, a short separate job downloads these artifacts without flattening
their directories and uploads the coverage-only directory with the repository CODECOV_TOKEN secret.
The reporting job is nonblocking and has no publishing environment or id-token permission.
Skip uploads on fork PRs and warn/skip when the secret is missing; test execution stays required.

## Non-goals and failure semantics
Do not rerun tests to obtain coverage, weaken test failures, alter source qualification records,
reuse a report from another run, introduce a threshold, or claim hosted completion from local tests.
