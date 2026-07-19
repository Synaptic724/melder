# Component Patch: StaticCommandSystem

## Before
- Static spell failure reasons were implicit and path-dependent.

## After
- Static command exposes one explicit spell status/explain helper.

## Contract
- The helper reports whether a spell is:
  - published
  - command-enabled
  - live
  - supported by static existence policy
  - available for static fetch
  - and why/why not
