from typing import Dict, List, Tuple

# Protects blocks inserted immediately before the first "Key Files (C1):" after each heading.
PROTECTS_5: Dict[str, str] = {
"### Subcomponent: Aether/Nexus/Rift Unit Cluster\n": """Protects:
- Nexus singleton and cold-start rules (a Nexus needs an Aether and publishes no
  singleton before one), Rift creation gated on an enabled Nexus and creation
  permission, projection refresh through the Rift gate barrier
- Rift constructor and frame-link guardrails, one primary space, idempotent cleanup
  that re-checks the cleaned flag under its lock; workstation binding and target
  guardrails; command-system lookups, and one room memory per top-level public call
""",
"### Subcomponent: Crystallizer Unit Cluster\n": """Protects:
- the crystallizer as an Aether-hosted singleton that refuses a first init without
  Aether and activates only with an activated configuration
- spell crystals recording unknown import targets instead of skipping them
- synthetic modules that materialize, import nested package graphs, re-execute
  updated source on reload, allow a benign import cycle and surface a bad one
""",
"### Subcomponent: MutationResearch Unit Cluster\n": """Protects:
- configuration defaults and a value-typed payload; a guaranteed default research
  set and unique set names; composition emission only while active
- activation that hydrates an untouched registry from the record and never
  clobbers live research; idempotent world-entry recording
""",
"### Subcomponent: Spellbook Runtime And Binding Unit Cluster\n": """Protects:
- bind refusals: modules, Protocols bound as spells, existing objects and callables
  without `unique` existence, unnamed lambdas; binding-profile hashing, including
  fingerprints with no memory address in them
- Spell hooks, mutation override and cleanup; SpellIndex hash/equality stability
  and its context manager; scan-bind of marked objects; configuration defaults,
  freeze and disposal priority; conjure cache-path classification and emission
""",
"### Subcomponent: Spellbook Compiler Unit Cluster\n": """Protects:
- the compiler system's owned surfaces and phase delegation; Phase 1 building once
  and honouring cancellation; the phase 2-5 codegen IR shape and deterministic
  signature hashing; the validation-strategy registry and Phase-6 validity gating
- key-set plan lowering (`test_site_plan_lowering.py`): demand, placement, guard
  order, call shape and unresolved inputs
- copied pool reads (`test_compiler_pool_snapshot_reads.py`): Phases 3, 5 and 6 and
  the Phase-8 walk survive a pool that grows while iterated, and Phase 5 skips an
  entry with no registered state (see `### Flow: Concurrent-Writer Stand-In`)
""",
"### Subcomponent: Aether Component Cluster\n": """Protects:
- the descriptor manager keeping frame, conduit and spell records coherent; one ACL
  container per descriptor creation flow, cleaned on frame detach even without
  managed-frame state; the extended viewer surface matrix
""",
"### Subcomponent: Crystallizer Component Cluster\n": """Protects:
- graph extraction (module targets, direct dependencies, kind mapping, paths)
  over real module graphs; the bench cases executing repeatably and leaving
  `sys.modules` and the meta path clean
""",
"### Subcomponent: MutationResearch Component Cluster\n": """Protects:
- the Aether-owned root reachable from a real conduit, its default set ready on a
  real Aether, and the configuration/activation matrix
""",
"### Subcomponent: Spellbook Runtime And Binding Component Cluster\n": """Protects:
- bind metadata, Protocol member enforcement and detailed profiles; configuration
  adoption and refusal against the frame; contracted-spell maps and peer
  collisions; SpellIndex version tracking; cache-gate posture stamps
- the conduit cache bundle rebuilt from each non-full-hit conjure, and spell ids
  that agree across two fresh interpreters
""",
"### Subcomponent: Spellbook Compiler Component Cluster\n": """Protects:
- phase 3-7 records through the compiler system and direct structural phases that
  match the system surfaces; real codegen processor and planner outputs;
  generalized-family discovery routing
- key-set plans through real conjures: a supplied dependency and its subtree are
  never built, three of five supplied parts build only the other two, positional
  payloads, collection members, stored shared sites
""",
"### Subcomponent: Aether Integration Cluster\n": """Protects:
- Rift frame viewers after passive publication; the extended viewer method matrix
  through both Nexus and Rift; the ACL chain provisioned on publish, advanced and
  rolled back after conjure, and removed on frame detach
""",
"### Subcomponent: Crystallizer Integration Cluster\n": """Protects:
- crystallization of really bound spells (root module name and kind, targets,
  direct dependencies, describe snapshot) and the synthetic-module cases through
  the hosted crystallizer
""",
"### Subcomponent: MutationResearch Integration Cluster\n": """Protects:
- one Aether-owned root shared across frames and returned by dynamic conduits;
  bound spell ids registering into the default set; dynamic binds auto-declaring
  research; the residency view joining live runtime; research lines surviving a
  composition round trip
""",
"### Subcomponent: Spellbook Integration Cluster\n": """Protects:
- configuration shared and locked across named frames; conjure registration and
  cleanup; scan-bind order and refusals (re-exports, duplicates, rescans); meld by
  id, name, class, Protocol or string spellframe, forward-reference type hints and
  collection DI; read-only public mappings; compiler phases followed by a meld
""",
}

EDITS_5: List[Tuple[str, str, int]] = [
("- `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py` (key-set plans, 2026-09-26)\n",
 "- `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py` (key-set plans, 2026-09-26)\n"
 "- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`\n", 1),
]
