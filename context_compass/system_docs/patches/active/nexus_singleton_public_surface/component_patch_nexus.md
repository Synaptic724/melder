# component_patch_nexus

## Component purpose and boundary in current architecture
`Nexus` is the public singleton root for Rift-domain work. It owns Rift
registry/config/lifecycle state and hides `Aether` from normal public use.

## Before/after behavior summary
- Before:
  The public AR model was still built around `Aether` facade methods and a
  hosted `AethericRiftSystem`.
- After:
  `Nexus` is the public root, while `Aether` privately hosts the inert Nexus
  singleton and remains hidden substrate only.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  Nexus configuration, Rift creation requests, direct Rift lookup/removal
  requests
- Outputs:
  configured/enabled Nexus state plus live `Rift` objects
- Error semantics:
  unconfigured or disabled Nexus operations fail fast with explicit runtime
  errors

## State and lifecycle deltas
- Singleton
- Exists at boot but starts unconfigured and disabled
- Owns:
  - Nexus configuration
  - configured/enabled flags
  - Rift registry/id-name indexes
  - frame-name assignment metadata/policy
- Does not own:
  - actual `AethericFrame` objects
  - live substrate operations against Aether

## Failure mode deltas
- Leaving Aether-facing Rift facade methods active would split the public root
  and reintroduce god-object pressure
- Letting Nexus target Aether directly for operational frame access would blur
  the domain boundary and create circular coupling

## Dependency and ordering constraints
- `Aether` privately creates/hosts the inert Nexus singleton at boot
- Public `Nexus()` must return the hosted singleton rather than creating a
  second one
- `Rift` creation depends on Nexus being configured and enabled

## Validation expectations
- `Nexus` is the only intended public entrypoint for Rift-domain work
- `Aether` no longer publicly facades Rift creation/configuration methods
- Nexus remains substrate-agnostic beyond private hosting/bootstrap

## Unknowns and open decisions
- Exact private helper names used for Aether-hosted Nexus construction
