# Component material migrated out of src_architecture.md

Extracted 2026-08-01 during the recomposition of `src_architecture.md` to its
Required Section Contract. These are component-level deep dives, which that
contract names as an anti-pattern in the architecture document.

NOTHING HERE IS DELETED. This file is the INPUT to the `src_components.md` pass.
Until that pass lands this material is absent from both canonical documents - a
deliberate, bounded, recorded gap.

Four headings arrived wrapped across two physical lines (which produces one-line
index fragments) and were unwrapped here.

## Table of Contents

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. Reason:

The generated `*_index.md` replaced it. A hand-maintained contents list is a
SECOND ADDRESSING SURFACE, and the two drift the moment a section moves - the
index is rebuilt from the document, the contents list is not.

This is a decision, not an oversight. Do not re-absorb it without first
retiring the authority named above.

## Documentation Quality Standard

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. Reason:

Superseded by
`agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md`,
which scores the same concern with weighted criteria and a refusal threshold. A
local restatement of a quality bar competes with the policy that owns it.

This is a decision, not an oversight. Do not re-absorb it without first
retiring the authority named above.

## Source Coverage and Evidence

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. Two independent reasons, both
measured rather than asserted:
1. ITS EVIDENCE HALF IS ROTTED. Two of its seven citations are out of bounds
   against current source - `spell_compiler.py:L131-L2383` in a 693-line file and
   `creation_context.py:L109-L814` in a 309-line file. Same decomposition rot as
   the other stale citations found on 2026-08-02. It also uses an `L131-L2383`
   format that no other citation in these documents uses, so nothing checking
   `path:line` would even see it.
2. ITS COVERAGE HALF IS SUPERSEDED. `## Information Sources` carries 110 entries
   in `src_architecture.md` and 170 in `src_components.md`, all resolving. This
   block is a non-exhaustive prose restatement of the same thing, and it cites
   DIRECTORIES (`crystal_loader_system/`, `crystal_analysis/`, `crystals/**`) -
   the exact pattern the current instructions forbid because a directory can
   never resolve against a graph keyed by source file.
Re-absorb only if someone first re-measures the seven ranges and converts the
coverage list to resolvable file paths. Neither is worth doing while
`## Information Sources` already answers the question correctly.

## Glossary and Core Terms

RE-ABSORBED into `context_compass/system_docs/src_architecture.md` on
2026-08-02, ahead of `## System Boundary and External Interfaces`. The body was
removed from this file deliberately: two copies of a glossary drift, and the
canonical document is the one that gets maintained. All 42 terms were verified
against `src/` before re-absorption. Nothing was lost - see that section.

## Spellbook Root Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 9 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Aether Global Singleton Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 12 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Aether Utility System Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 9 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Crystallizer Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 19 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Aetheric Frame Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 13 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Aetheric Mediator Plane Responsibilities (BUILT, NOT WIRED)

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 107 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Nexus and Rift Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 192 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Conduit Lifecycle (Normal and Lesser)

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 19 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Binding and Registration Pipeline

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 13 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Spell Examination Profile Responsibilities

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 8 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Resolution Styles and DI Shapes

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 34 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## DI Resolution Contract (Spec)

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 42 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## SpellCompiler and Validation Pipeline

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02, VERIFIED STALE TWIN.
Of its 34 lines, 24 are already in the canonical documents and the 10 that are
not ARE PRECISELY THE DEFECTS FIXED ON 2026-08-02: the `_capture_phase8_11_...`
name that carries a spurious leading underscore, and the six-citation evidence
block pointing into `spell_compiler.py` at lines 1966-3787 of a 693-line file,
plus `change_control_manager.py:1403-1475` and `meld.py:502-532`, neither of
which contains the symbol it was cited for.
Re-absorbing this would re-import every one of those. The corrected version
lives in `src_components.md`; this is the copy the corrections were made against.

## Resolution and Meld Pipeline

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 50 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Contracts, Policies, and Permissions

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 19 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Existence and Scoping Model

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 16 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Logging and Observability

FULLY RE-ABSORBED - VERIFIED DUPLICATE, BODY REMOVED 2026-08-02.
Every line of this block is present verbatim in
`context_compass/system_docs/src_components.md` under
`#### Architecture narrative (folded in from src_architecture.md)` inside the
owning component entry. Measured, not assumed: 100% of its 14 non-blank
lines matched. The body was removed because two copies of a narrative drift
and only one of them is the document anyone maintains.

## Ownership, Lifecycle, and Cleanup

RE-ABSORBED 2026-08-02 into `src_architecture.md` at
`## Data Flows and Sequences` -> `### Sequence: Cleanup`. It EXTENDED that
listing from three types to seven (adding AetherUtilitySystem, Nexus, Rift and
Creations) and each `cleanup()` was verified present on the class named before
re-absorption. Body removed so the two cannot drift.

## Extension Points

RE-ABSORBED 2026-08-02 into `src_architecture.md` as its own H2, scoped as the
seams that CROSS components (per-component seams live in each `src_components.md`
entry). Every named seam verified present in `src/`. Body removed.

## C3 and C2 Cross-Reference

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. It was a two-line pointer to
`src_components.md`, and both canonical documents already cross-reference each
other in `## Information Sources` and their handoff summaries. A third pointer
living in a patch lane is not navigation, it is another thing to keep current.

## Runtime Type Names (Concrete, No Interface Layer)

RE-ABSORBED 2026-08-02 into `src_architecture.md` as its own H2. All six
concrete classes verified to exist; the enforcement citation was re-measured and
CORRECTED on the way in - the `isinstance` check and its raise are at
`conduit.py:4341-4343`, not :4342-4344 as recorded here. Body removed.

## Open Questions

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02, VERIFIED DUPLICATE. Every claim
here is already carried by `## Unknowns` in BOTH canonical documents: SpellContract
evidenced rather than unknown, the live mutation override overlay, and the four
`SpellState` producer flags still blocked on the MR runtime-seam slice with the
same two follow-up stories. Those entries were re-verified against source on
2026-08-02 - all four flags still have zero producer sites - so the canonical
copy is the current one and this was the stale twin.

## Persistence & Restore Architecture (promoted from patch restore_engine_2026_07_07 + successor lanes, 2026-07-07)

RE-ABSORBED 2026-08-02 into `src_architecture.md` under
`## Promoted Patch Decisions (re-absorbed 2026-08-02)`, verified first: every
class and verb named in these four blocks was checked against `src/`, and the
two that did not resolve turned out to CONFIRM the text (`BootMediator` was
renamed as documented; `refuse_on_blockers` is a parameter, as stated).
Body removed so the canonical copy is the only one.

## Persistence Subsystem Topology (promoted from patch crystallizer_decomposition_2026_07_09, 2026-07-10)

RE-ABSORBED 2026-08-02 into `src_architecture.md` under
`## Promoted Patch Decisions (re-absorbed 2026-08-02)`, verified first: every
class and verb named in these four blocks was checked against `src/`, and the
two that did not resolve turned out to CONFIRM the text (`BootMediator` was
renamed as documented; `refuse_on_blockers` is a parameter, as stated).
Body removed so the canonical copy is the only one.

## V3 Horizon Architecture (promoted 2026-07-12 from six patch dirs; owner-run full-tree green)

RE-ABSORBED 2026-08-02 into `src_architecture.md` under
`## Promoted Patch Decisions (re-absorbed 2026-08-02)`, verified first: every
class and verb named in these four blocks was checked against `src/`, and the
two that did not resolve turned out to CONFIRM the text (`BootMediator` was
renamed as documented; `refuse_on_blockers` is a parameter, as stated).
Body removed so the canonical copy is the only one.

## Three-Lane Tail (promoted 2026-07-11; owner-directed finish of the public_cloud_seams, source_drift_preflight, and spell_index_graft lanes)

RE-ABSORBED 2026-08-02 into `src_architecture.md` under
`## Promoted Patch Decisions (re-absorbed 2026-08-02)`, verified first: every
class and verb named in these four blocks was checked against `src/`, and the
two that did not resolve turned out to CONFIRM the text (`BootMediator` was
renamed as documented; `refuse_on_blockers` is a parameter, as stated).
Body removed so the canonical copy is the only one.

# Material migrated out of src_components.md (2026-08-01)

Moved during the recomposition of `src_components.md` to its Required Section
Contract. Headings that arrived wrapped across two to five physical lines were
unwrapped. NOTHING HERE IS DELETED.

## Documentation Quality Standard

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. Reason:

Superseded by
`agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md`,
which scores the same concern with weighted criteria and a refusal threshold. A
local restatement of a quality bar competes with the policy that owns it.

This is a decision, not an oversight. Do not re-absorb it without first
retiring the authority named above.

## Table of Contents

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. Reason:

The generated `*_index.md` replaced it. A hand-maintained contents list is a
SECOND ADDRESSING SURFACE, and the two drift the moment a section moves - the
index is rebuilt from the document, the contents list is not.

This is a decision, not an oversight. Do not re-absorb it without first
retiring the authority named above.

## Component Template

KEPT OUT DELIBERATELY - BODY REMOVED 2026-08-02. Reason:

Superseded by the Component Entry Contract in
`src_components_instructions.md`. The skill is the single authority for which
fields a C3 entry carries; a template copy in a patch lane goes stale silently
and nothing checks it.

This is a decision, not an oversight. Do not re-absorb it without first
retiring the authority named above.

## Crystallizer Persistence & Restore (promoted from patch restore_engine_2026_07_07 + successor lanes, 2026-07-07)

RE-ABSORBED 2026-08-02 into `src_components.md` under
`## Promoted Patch Detail (re-absorbed 2026-08-02)`. Verified first: every
class and method name cited in these four blocks resolves in `src/` - zero
misses across 411 lines - and they carry no `path:line` citations, so no
line-range rot came with them. Body removed; the canonical copy is the one.

## Subsystem Decomposition (promoted from patch crystallizer_decomposition_2026_07_09, 2026-07-10)

RE-ABSORBED 2026-08-02 into `src_components.md` under
`## Promoted Patch Detail (re-absorbed 2026-08-02)`. Verified first: every
class and method name cited in these four blocks resolves in `src/` - zero
misses across 411 lines - and they carry no `path:line` citations, so no
line-range rot came with them. Body removed; the canonical copy is the one.

## V3 Horizon Iteration (promoted 2026-07-12 from six patch dirs: aether_lazy_frames_and_load_gate_2026_07_11, crystallizer_v3_horizon_2026_07_11, crystallizer_s2_user_source_ retention_2026_07_11, crystallizer_s3_impact_engine_2026_07_11, crystallizer_external_mesh_2026_07_12, mr_restore_build_stage_2026_07_11)

RE-ABSORBED 2026-08-02 into `src_components.md` under
`## Promoted Patch Detail (re-absorbed 2026-08-02)`. Verified first: every
class and method name cited in these four blocks resolves in `src/` - zero
misses across 411 lines - and they carry no `path:line` citations, so no
line-range rot came with them. Body removed; the canonical copy is the one.

## Three-Lane Tail (promoted 2026-07-11 from patch dirs public_cloud_seams_2026_07_12, source_drift_preflight_2026_07_12, spell_index_graft_2026_07_12; owner-directed finish)

RE-ABSORBED 2026-08-02 into `src_components.md` under
`## Promoted Patch Detail (re-absorbed 2026-08-02)`. Verified first: every
class and method name cited in these four blocks resolves in `src/` - zero
misses across 411 lines - and they carry no `path:line` citations, so no
line-range rot came with them. Body removed; the canonical copy is the one.

## Test surfaces evicted from src_components.md (2026-08-02)

Destination: `context_compass/system_docs/tests_components.md`.

`src_components_instructions.md` now states that `Key Files (C1)` cites
in-scope SOURCE paths only, because the graph is built from the source tree
and a test path is a guaranteed miss against it, not a near miss. The two
citations below were the only test paths in the source-side document and
were the only two unresolved entries in the 167-path join. They are removed
from `src_components.md` and recorded here verbatim; they are not deleted,
and until `tests_components.md` is recomposed they live in neither canonical
document.

Removed from `Key Files (C1)` of `Subcomponent: DevOps Change Control
Manager (Transaction Ownership)`:

- `tests/unit/melder/aether/dev_ops/change_control_manager/test_scope_acquisition.py`

Removed from `Key Files (C1)` of `Subcomponent: DevOps Information
Strategies`:

- `tests/unit/melder/aether/dev_ops/test_devops_information_strategies.py`

Removed from `## C1 Code Map (Core)`, measured ranges retained so the
test-side recomposition does not have to remeasure:

- path: `tests/unit/melder/aether/dev_ops/change_control_manager/test_scope_acquisition.py`
  start_line: 1
  end_line: 662
  loc: 662
  verified_at: 2026-08-01T20:05:00Z
- path: `tests/unit/melder/aether/dev_ops/test_devops_information_strategies.py`
  start_line: 1
  end_line: 541
  loc: 541
  verified_at: 2026-08-01T20:05:00Z

Both paths remain cited in `## Information Sources` of `src_components.md`.
That is deliberate: they were read as evidence during the build, and
Information Sources records what was consulted rather than what the
component claims as its own.


## Measured C1 records evicted from `src_components.md` Core (2026-08-02)

Destination: back into `## C1 Code Map (Core)` if and only if a component ever
claims one of these in its `Key Files (C1)` list.

`src_components_instructions.md` defines Core as the DEDUPLICATED UNION OF EVERY
`Key Files (C1)` LIST, so membership is decided by a component's own claim and
nothing else. These 40 `nexus/acl/**` modules are the ACL profile, validator and
configuration depth, and the Frame ACL entries state explicitly that they are
NOT key files of those components. They were therefore not Core, and Core had
been carrying them anyway.

The modules themselves remain catalogued with purpose text in
`### Full Package Inventory (exhaustive, retained)` in `src_components.md`. That
inventory carries no line ranges, which is why the measured records are kept
here - a later pass promoting any of these to core should not have to remeasure.
Ranges re-measured from disk at eviction; whole-file, so `start_line: 1`.

- path: `src/melder/nexus/acl/builder/frame_acl_codegen_builder.py`
  start_line: 1
  end_line: 650
  loc: 650
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/builder/frame_acl_command_builder.py`
  start_line: 1
  end_line: 585
  loc: 585
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/builder/frame_acl_view_builder.py`
  start_line: 1
  end_line: 696
  loc: 696
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/frame_acl_codegen_configuration.py`
  start_line: 1
  end_line: 681
  loc: 681
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/frame_acl_command_configuration.py`
  start_line: 1
  end_line: 710
  loc: 710
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/frame_acl_view_configuration.py`
  start_line: 1
  end_line: 871
  loc: 871
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py`
  start_line: 1
  end_line: 841
  loc: 841
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile.py`
  start_line: 1
  end_line: 314
  loc: 314
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile_builder.py`
  start_line: 1
  end_line: 213
  loc: 213
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/full_access_profile.py`
  start_line: 1
  end_line: 172
  loc: 172
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/hybrid_profile.py`
  start_line: 1
  end_line: 152
  loc: 152
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/permissive_profile.py`
  start_line: 1
  end_line: 128
  loc: 128
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/precision.py`
  start_line: 1
  end_line: 144
  loc: 144
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py`
  start_line: 1
  end_line: 125
  loc: 125
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py`
  start_line: 1
  end_line: 99
  loc: 99
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/command/frame_acl_command_profile.py`
  start_line: 1
  end_line: 348
  loc: 348
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/command/frame_acl_command_profile_builder.py`
  start_line: 1
  end_line: 204
  loc: 204
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/command/hybrid_profile.py`
  start_line: 1
  end_line: 96
  loc: 96
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/command/permissive_profile.py`
  start_line: 1
  end_line: 95
  loc: 95
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/command/precision.py`
  start_line: 1
  end_line: 93
  loc: 93
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/command/safe_profile.py`
  start_line: 1
  end_line: 96
  loc: 96
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/frame_acl_profile.py`
  start_line: 1
  end_line: 227
  loc: 227
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/rules/frame_acl_rule.py`
  start_line: 1
  end_line: 262
  loc: 262
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/rules/frame_acl_ruleset.py`
  start_line: 1
  end_line: 297
  loc: 297
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/view/frame_acl_view_profile.py`
  start_line: 1
  end_line: 465
  loc: 465
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/view/frame_acl_view_profile_builder.py`
  start_line: 1
  end_line: 204
  loc: 204
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/view/hybrid_profile.py`
  start_line: 1
  end_line: 105
  loc: 105
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/view/permissive_profile.py`
  start_line: 1
  end_line: 103
  loc: 103
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/view/precision.py`
  start_line: 1
  end_line: 98
  loc: 98
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/configurations/profiles/view/safe_profile.py`
  start_line: 1
  end_line: 112
  loc: 112
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/compatibility/frame_acl_set_compatibility_report.py`
  start_line: 1
  end_line: 242
  loc: 242
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/compatibility/frame_acl_set_compatibility_validator.py`
  start_line: 1
  end_line: 636
  loc: 636
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/frame_acl_validator.py`
  start_line: 1
  end_line: 1493
  loc: 1493
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/codegen/precision_strategy.py`
  start_line: 1
  end_line: 24
  loc: 24
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/codegen/safe_strategy.py`
  start_line: 1
  end_line: 120
  loc: 120
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/command/precision_strategy.py`
  start_line: 1
  end_line: 21
  loc: 21
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/command/safe_strategy.py`
  start_line: 1
  end_line: 49
  loc: 49
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/common.py`
  start_line: 1
  end_line: 47
  loc: 47
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/view/precision_strategy.py`
  start_line: 1
  end_line: 23
  loc: 23
  verified_at: 2026-08-02T14:29:36Z
- path: `src/melder/nexus/acl/validator/profiles/view/safe_strategy.py`
  start_line: 1
  end_line: 71
  loc: 71
  verified_at: 2026-08-02T14:29:36Z

# Material migrated out of tests_architecture.md (2026-08-02)

Moved during the test-architecture recomposition, NOT deleted. Both sections are
superseded by a named authority, exactly as their source-side twins were:

## Table of Contents

KEPT OUT - superseded by the generated `tests_architecture_index.md` - a hand-maintained contents list is a
second addressing surface and the two drift the moment a section moves.

Body retained below verbatim so nothing is lost:

```
- Scope and Intent
- Documentation Quality Standard
- DO NOT ASSUME / Unknowns Gate
- Unknowns
- Source Coverage and Evidence
- C4 Architecture Summary
- External Interfaces and Entry Points
- Core Responsibilities
- Data Flows and Lifecycle
- Invariants and Guarantees
- C3 Components Overview
- C2 Subcomponents Overview
- C1 Code Map (Key Paths)
- Diagrams
- Information Sources
- Open Questions
- Context / Handoff Summary
```

## Documentation Quality Standard

KEPT OUT - superseded by `agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md`,
which scores the same concern with weighted criteria and a refusal threshold.

Body retained below verbatim so nothing is lost:

```
This document is durable context and must stand on its own.

Rules:
- No handwaving. Every claim is grounded in source evidence or marked as unknown.
- Test entrypoints and runtime reset flow are explicit.
- Tier boundaries are described in terms of what is actually in the repo.
- Shared harnesses and support layers are named directly.
- Evidence list is updated when new files are used.
```

