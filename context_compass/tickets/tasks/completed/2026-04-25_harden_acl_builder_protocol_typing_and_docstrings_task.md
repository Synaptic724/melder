# Task: Harden ACL Builder Protocol Typing And Docstrings
- Completed: 2026-04-26T09:56:44Z
- Summary: Closed after the ACL builder family protocol/docstring hardening
  landed and the focused validation rings stayed green.

## Metadata
- Task ID: TASK-2026-04-25-harden-acl-builder-protocol-typing-and-docstrings
- Story: STORY-2026-04-25-harden-acl-builder-protocol-typing-and-docstrings
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:08:57Z
- Updated: 2026-04-26T09:56:44Z

## Objective
Harden the ACL builder family so borrowed collaborators and borrowed typed ACL
configurations use the interface layer instead of concrete imports, and rewrite
the builder docstrings to the public-library contract standard.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this hardening pass.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/interfaces.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py`
  - directly affected focused builder tests
- DEPENDENCIES:
  - `codex/context_compass/system_docs/patches/active/acl_builder_protocol_and_docstring_hardening/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/acl_builder_protocol_and_docstring_hardening/component_patch_interfaces.md`
  - `codex/context_compass/system_docs/patches/active/acl_builder_protocol_and_docstring_hardening/component_patch_acl_builders.md`
- EXIT_GATE: the builder family uses protocols for borrowed collaborators and
  borrowed configs, the docstrings are upgraded, and the focused builder ring
  is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a correct protocol boundary
  requires widening beyond the builder family.

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/acl_builder_protocol_and_docstring_hardening/architecture_patch.md`
  - `system_docs/patches/active/acl_builder_protocol_and_docstring_hardening/component_patch_interfaces.md`
  - `system_docs/patches/active/acl_builder_protocol_and_docstring_hardening/component_patch_acl_builders.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicit supersession

## Notes
- DATETIME: 2026-04-25T20:08:57Z
  TYPE: FACT
  CLAIM: The existing interface layer is incomplete for the builder family.
    `IFrameACLContainer` is currently missing methods that `FrameACLBuilder`
    already calls, the typed configuration protocols are incomplete, and there
    is no builder protocol for the family-specific builders to depend on.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2760-2898
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:57-583
  IMPACT: This is not just a docstring pass. The hardening has to patch
    `interfaces.py` and the builders together.
  NEXT: add the missing protocols and then migrate the builder family off
    borrowed concrete types.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:19:53Z
  TYPE: FACT
  CLAIM: The builder hardening pass is landed. `interfaces.py` now exposes the
    missing typed ACL configuration protocols and a dedicated builder protocol,
    the generic builder uses those interfaces for borrowed draft/config typing,
    and the family builders no longer import the generic builder class as a
    borrowed collaborator. The family builder files also now carry full
    convenience-method docstrings instead of sparse or missing prose.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2790-3077
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-604
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-546
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-590
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-525
  IMPACT: The ACL builder family now matches the repo's protocol-first and
    public-library docstring expectations much more honestly.
  NEXT: return the slice for review and let the user inspect the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:19:53Z
  TYPE: MEASURE
  CLAIM: The focused and broader ACL-builder hardening rings are green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> `30 passed, 2 warnings`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile_builder.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> `37 passed, 2 warnings`
  IMPACT: The hardening pass is stable enough to move to review immediately.
  NEXT: wait for user review feedback on the builder family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:24:01Z
  TYPE: FACT
  CLAIM: One real protocol gap remains after the first hardening pass. The
    family-specific builders still do not have their own builder protocols, so
    the generic builder cannot return family-builder interface types cleanly
    and the public signatures still expose concrete family builders in places
    where the code only borrows them.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2790-3077
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:200-274
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-546
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-590
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-525
  IMPACT: The hardening pass is not done until the family-builder protocols
    exist and the builder signatures return those interfaces instead of the
    concrete family types.
  NEXT: add `IFrameACLViewBuilder`, `IFrameACLCommandBuilder`, and
    `IFrameACLCodegenBuilder`, then update the generic/family builder
    signatures to use them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:28:38Z
  TYPE: FACT
  CLAIM: The remaining family-builder protocol gap is now closed. The interface
    layer now includes `IFrameACLViewBuilder`,
    `IFrameACLCommandBuilder`, and `IFrameACLCodegenBuilder`; the generic
    builder now returns those interface types from `begin_*_change(...)`; and
    all three family builders inherit their protocol beside `Cleanable`.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2870-3103
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-604
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-546
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-590
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-525
  IMPACT: The public builder signatures now expose shape contracts instead of
    borrowed concrete builder classes, which is the correct protocol-first
    boundary for this subsystem.
  NEXT: return the hardening slice for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:28:38Z
  TYPE: MEASURE
  CLAIM: The post-protocol-conversion builder rings are green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> `30 passed, 2 warnings`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile_builder.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> `37 passed, 2 warnings`
  IMPACT: The protocol-first builder hardening is stable enough to inspect now.
  NEXT: wait for user review feedback on the builder family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
