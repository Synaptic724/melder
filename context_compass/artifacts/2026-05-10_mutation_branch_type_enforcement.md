# Mutation Branch Type Enforcement

## Metadata
- Artifact ID: ART-2026-05-10-mutation-branch-type-enforcement
- Parent Epic: EPIC-2026-05-03-general-open-questions
- Status: superseded (archived 2026-07-11; owner-directed salvage read done)
- Superseded by: the V3 model has lanes/join, no branch vocabulary. The
  salvageable core (optional TYPE enum + enforcement toggle) is recorded as
  "Lane TYPE classification" in
  artifacts/2026-07-11_mutation_research_philosophy_v3.md Open Directions.
- Created: 2026-05-10T09:19:43Z
- Updated: 2026-07-11T19:45:00Z

## Purpose
Capture one narrow MutationResearch design idea:
- branch names may remain freeform
- branch type classification may be optionally enforced
- the same branch-type classification should apply across spell mutation and
  module mutation

This artifact exists because branch naming and branch semantics should not stay
implicit once module versions, spell versions, and grouped mutation
transactions start sharing the same control surface.

## Core Thesis
Branch identity should be split into two fields:

- `branch_name`
  - freeform string
  - human or agent chosen
  - used for local naming and workflow references

- `branch_type`
  - optional enum classification
  - used for policy and validation
  - shared across spell mutation and module mutation

This gives the system:
- flexible names
- structured validation when desired
- a clean way to reason about grouped transactions

## Why This Exists
MutationResearch is increasingly managing:
- spell mutation branches
- module mutation branches
- grouped transactions across both

If these stay untyped forever, then the system has less leverage to detect:
- test-oriented mutation work happening inside production-oriented lanes
- development work being promoted with the wrong policy posture
- branch labels drifting apart between module and spell versions that are
  supposed to move together

The point is not to remove flexibility.
The point is to give the system an optional structured control surface.

## Configuration Item
Add one new mutation-configuration field:

- `branch_type_enforcement`

Behavior:
- `false`
  - no branch-type validation
  - branch names are plain strings
  - default branch name is `default`
  - branch type may be omitted entirely
- `true`
  - each mutation branch must carry a valid `branch_type`
  - branch names may still be custom strings
  - validation and alarms use the enum classification

So the enforcement toggle governs whether branch typing is:
- required
or
- optional

It does not govern whether branching exists at all.

## Branch Type Enum
The branch type classification can be a normal `Enum`.

Initial values:
- `development`
- `experiment`
- `production`
- `test`

This enum should be shared by:
- spell mutation branches
- module mutation branches

That keeps both layers under the same policy vocabulary.

## Default Behavior
When `branch_type_enforcement` is disabled:
- branch name defaults to `default`
- branch type is not required
- no enum-based validation or alarms are applied

When `branch_type_enforcement` is enabled:
- branch type is required
- branch name may still be custom
- the system validates behavior using the enum

This means users can choose:
- completely loose branch naming
or
- structured branch policy

## Naming Versus Classification
Branch names and branch types should not be conflated.

Examples:
- `branch_name = "experiment_0"`
  - `branch_type = experiment`
- `branch_name = "prod_hotfix_alpha"`
  - `branch_type = production`
- `branch_name = "qa_probe_7"`
  - `branch_type = test`

So:
- names are for local expression
- types are for policy meaning

This also means the system can remain flexible without giving up validation.

## Module And Spell Alignment
When a spell mutation is created from a module mutation context:
- the module branch type should provide the default branch type for the spell
  mutation
- grouped transactions should keep the module and spell branch type aligned
  unless there is an explicit widening or reassignment decision

This is the key behavioral rule:
- module branch classification drives the default mutation label for spell work
  derived from that module world
- the transaction makes that association authoritative

So the relationship is:
- module branch context provides the initial classification
- grouped mutation transactions keep the branch labels synchronized

## Group Transactions
This idea is most useful when grouped transactions exist.

In a grouped transaction:
- one or more module versions may advance
- one or more spell versions may advance
- the branch label set should stay coherent across all participants

That means the transaction should carry:
- `branch_name`
- `branch_type`

and should stamp those onto:
- module mutation records
- spell mutation records

This avoids silent divergence inside one branch movement.

## Validation Uses
With `branch_type_enforcement` enabled, the enum gives the system a way to
raise alarms or block invalid combinations.

Examples:
- creating a `test` mutation inside a `production` module branch
- trying to promote a `test`-typed branch directly into a production release
  lane
- mixing `production` and `experiment` branch types in one grouped
  transaction without an explicit override path

The important point is:
- this is policy support
- not an automatic hard prohibition on every possible workflow

The system can:
- raise alarms
- require explicit overrides
- block specific transitions

depending on policy later.

## Branch Type Is Optional Governance
This is not the same as saying all mutation work must be heavily structured.

The design should preserve two modes:

### Unstructured mode
- `branch_type_enforcement = false`
- branch name defaults to `default`
- enum classification is off

### Structured mode
- `branch_type_enforcement = true`
- branch type is required
- validation uses the enum

This keeps the system usable for:
- users who want lightweight mutation branches
- users who want stronger governance

## Production And Development Semantics
If users choose structured mode, the branch enum gives the system a stable way
to describe common environments or intentions without pretending that the name
alone is enough.

Examples:
- `production`
  - stable or promoted branch context
- `development`
  - normal ongoing implementation work
- `experiment`
  - exploratory or parallel future
- `test`
  - validation or synthetic verification work

This does not force the exact branch names.
It only gives the system a way to understand the intent class.

## Why This Should Be Shared Across Module And Spell Mutation
Module and spell mutation are too entangled to let their branch typing drift.

If modules and spells use separate classification systems:
- grouped transactions become harder to validate
- agent intent is harder to interpret
- branch policy becomes inconsistent

So the same enum should be reused in both places.

That gives us:
- one branch-type vocabulary
- one policy surface
- one validation language

## Recommended First Implementation Shape
The smallest honest shape is:

- `branch_type_enforcement: bool`
- `branch_name: str`
- `branch_type: Optional[BranchType]`

Rules:
- when enforcement is off:
  - `branch_name` defaults to `default`
  - `branch_type` may be `None`
- when enforcement is on:
  - `branch_type` must be a valid enum value
  - `branch_name` may be custom or system-generated

That is enough to start.

## Summary
In one sentence:

MutationResearch should support an optional `branch_type_enforcement`
configuration so branch names can stay flexible while module mutations and
spell mutations share one enum-based branch classification
(`development`, `experiment`, `production`, `test`) for grouped transaction
labeling, validation, and alarm policies, with `default` as the unstructured
fallback branch name when enforcement is off.
