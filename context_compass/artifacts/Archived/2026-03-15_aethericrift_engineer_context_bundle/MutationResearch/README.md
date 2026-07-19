# MutationResearch Foundations

## Purpose
This directory is the active planning workspace for mutation research.
It complements the AethericRift codegen guardrails model and defines how
structural runtime change is governed.

## Core Stance
- Guardrailed codegen is default.
- Mutation is explicit, gated, and auditable.
- Safe lane and mutation lane are separate execution paths.
- Promotion to stable lineage is always explicit.
- AR `StaticRiftSpace` remains the lower-risk operational surface.
- MR begins when a change crosses from workspace-local work into canonical
  evolution of durable runtime structure.

## Boundary Alignment
- Melder: runtime substrate, mutation mechanics, lifecycle truth.
- AethericRift: capability surface, ACL intersection, call routing.
- CommandOps: long-running orchestration, missions, coordination.

## Start Here
1. `MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md`
2. `MutationResearch/WORKING_MODEL.md`
3. `MutationResearch/systems/lane_contract.md`
4. `MutationResearch/systems/mutation_lifecycle.md`
5. `MutationResearch/systems/control_plane_gates.md`
6. `MutationResearch/systems/community_enterprise_topology.md`
7. `MutationResearch/systems/codegen_bridge.md`
8. `MutationResearch/systems/open_questions.md`
