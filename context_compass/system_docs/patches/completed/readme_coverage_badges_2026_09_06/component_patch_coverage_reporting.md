# Component patch: runtime coverage and badge delivery

## Before and after
Before: the runtime runner writes only JUnit; README has no CI or coverage badge.
After: an optional XML argument enables pytest-cov over Melder, preserving all original pytest inputs.
The three existing matrix legs opt in and retain separate coverage artifacts for this run/attempt.

## Reporting boundary
A contents-read-only checkout and artifact download occur in the reporting job. The owner selected
an explicit repository secret, CODECOV_TOKEN, instead of OIDC. Callers forward only that secret;
the credential check and upload steps receive it. No publishing credentials or environments are used.
Downloads select this run/attempt's coverage artifact names, never unrelated reports or JUnit files.
Require all three nonempty coverage XMLs before upload; missing artifact delivery cannot publish a
partial matrix as the current full result.

## State and failures
Failed runtime tests still fail qualification. Reporting is skipped on failed matrices and fork PRs.
Missing token emits a setup warning and skips reporting. Report upload/delivery failures are visible
but do not change test or package correctness gates. No tokenless or OIDC fallback is attempted.
Configuration disables Codecov statuses/comments; it remains a report and badge service only.

## Publication semantics
Normal branch/PR detection stays with Codecov. An authorized final-release event supplies prod as its
branch because its tag has already been verified against current prod by the existing release gate.
No coverage number is claimed before Codecov ingests a real report.

## Validation mapping
Runner behavior -> focused Python tests. Workflow permission/artifact/failure contracts -> parsed YAML.
Service setup and badge lifetime -> branch guide and owner-hosted verification.
