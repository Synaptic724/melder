# Capability Room Manual Runtime Access Architecture Patch

## Objective
Implement the first real capability room cut as broad manual runtime access
without codegen.

## Non-Goals
- No codegen work.
- No capability viewer redesign.
- No handle/proxy system.

## Changed Components
- `CapabilityCommandSystem`
- `CapabilityRiftSpace`

## Boundary Contract
- capability behaves like dynamic-style manual runtime access
- capability does not override frame truth
- dynamic-only lower-runtime operations still fail on automatic frames
- capability still does not imply codegen

## Migration Order
1. relax capability command runtime gating
2. update focused tests
