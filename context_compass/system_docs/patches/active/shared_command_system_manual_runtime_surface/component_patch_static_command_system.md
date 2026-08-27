# Component Patch: StaticCommandSystem

## Before
- static specialized spell runtime retrieval and spell explainability
- no explicit deny layer existed for newly added shared topology-mutation
  command methods

## After
- static keeps the shared command vocabulary visible
- unsafe topology-mutation methods are explicitly denied in
  `StaticCommandSystem`

## Contract
- static still allows query, describe, and live-only retrieval behavior
- static denies:
  - `create_lesser_conduit(...)`
  - `create_cluster(...)`
  - `delete_cluster(...)`
  - `join_cluster(...)`
  - `leave_cluster(...)`
  - `link(...)`
  - `sever_link(...)`
- the deny path is explicit and room-owned rather than hidden behind missing
  methods
