# Governance and Structural Change

<!--
Audience: integrator, contributor
Depth: mid
Status: current
Verified against: Melder 0.1.2 / git 7b31be6d7665
Last verified: 2026-08-29
Diagram source: architecture_and_design/diagrams/source/governed_change_loop.mmd
Source anchors:
- src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py
- src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py
- tests/integration/melder/aether/test_aether_integration_change_control_transactions.py
-->

[Architecture and design home](../README.md)

## Reader Question

How can Melder change live structure without putting every resolution behind one global lock?

## Short Answer

Normal resolution and structural mutation use different control paths. `meld()` relies on
compiled artifacts plus validity and dirty-root gates. Structural writers enter the
frame-local transaction plane, declare the scopes they need, and commit or abort through a
family-specific strategy.

![Governed runtime change loop](../diagrams/rendered/governed_change_loop.svg)

[Editable diagram source](../diagrams/source/governed_change_loop.mmd)

## Writer Path

Transaction families include binding, linking, unlinking, cluster sharing, ownership
transfer, index membership changes, and active-member notching. Each family computes a
scope claim set; disjoint work can proceed independently while overlapping structural
work waits or refuses with blocking evidence.

## Reader Path

Resolution does not acquire writer transaction claims. Instead, structural commits mark
affected roots or lineages dirty/gated. A later meld checks that state and refuses or
re-runs the required compilation/validation path before execution.

## Why This Design Is Strong

- Mutation cost is paid by mutation, not by every reader.
- Scope claims express isolation more precisely than one container-wide mutex.
- Dirty-state propagation prevents a committed structural change from being treated as a
  valid old execution plan.
- Transaction-family strategies keep mutation-specific scope rules explicit.

## Tradeoffs

The control plane adds state machines, claim modes, strategy registries, and lock-order
constraints. That complexity purchases parallel disjoint writes and a fast steady-state
read path instead of serializing every operation through one lock.

## Where to Go Next

- [Preserve and evolve](../03_usage/preserve_and_evolve.md)
- [Runtime model](runtime_model.md)

Source entry points:

- [Transaction mediator](../../src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py)
- [Change-control manager](../../src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py)
- [Transaction integration](../../tests/integration/melder/aether/test_aether_integration_change_control_transactions.py)
