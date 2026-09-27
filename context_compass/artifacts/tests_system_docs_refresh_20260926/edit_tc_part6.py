from typing import Dict

# New C2 entries inserted immediately before the heading given as the key.
INSERT_BEFORE_6: Dict[str, str] = {
"### Subcomponent: Aether Component Cluster\n": """### Subcomponent: Package Root Unit Cluster
Parent Component: Unit Test Suite
Purpose:
- cover what `import melder` publishes and pins: the root surface, the metadata
  modules, the internal registration guard, the annotation guard and the packaged
  system documents
Protects:
- every `__all__` name resolving on the root to the concrete-path object (identity,
  not equality), user-held surfaces and catchable errors reaching the root, and
  internal depths such as `ConduitWard` staying off it
- one version truth: `__version__` is the metadata literal, generated build assets
  are stamped for it, and `py.typed` ships beside the package
- internal classes refused by bind through the manifest (the test sets up its own
  world; see `### Flow: Runtime-Heavy Singleton Reset`)
- the system-document views: construction imports nothing deferred, slices are
  exact, refusal never reads as empty, graph walks terminate on cycles, and search,
  impact and cite stay index-shaped
Key Files (C1):
- `tests/unit/melder/test_package_public_surface.py`
- `tests/unit/melder/test_package_version_metadata.py`
- `tests/unit/melder/test_package_author_metadata.py`
- `tests/unit/melder/test_package_description_metadata.py`
- `tests/unit/melder/test_package_license_metadata.py`
- `tests/unit/melder/test_melder_registration_guard.py`
- `tests/unit/melder/test_annotation_integrity.py`
- `tests/unit/melder/test_system_documents.py`
- `tests/unit/melder/test_system_document_view.py`

### Subcomponent: Build Assets Unit Cluster
Parent Component: Unit Test Suite
Purpose:
- cover the build-time asset runner and its builders (agent metadata, system
  documents) without importing `melder`
Protects:
- refusal above all: `--check` fails on a version change, a hand-edited artifact,
  a missing artifact, a schema drift or an empty asset root, reports every stale
  asset, and propagates its exit code
- byte-deterministic rendering, and source fingerprints that ignore checkout line
  endings
- the system-documents builder transcribing the source index rather than
  re-deriving ranges, refusing an index without its proof, and catching a one-byte
  edit by digest
Key Files (C1):
- `tests/unit/melder/build_assets/test_build_asset_runner.py`
- `tests/unit/melder/build_assets/test_system_documents_builder.py`
- `tests/unit/melder/build_assets/test_agent_metadata_builder.py`

### Subcomponent: Utilities Unit Cluster
Parent Component: Unit Test Suite
Purpose:
- cover the utility layer class by class: synchronization primitives, weak and
  pooled data structures, custom exceptions, helpers, the logger adapter, the
  caching system and the agent text reader
Protects:
- gate semantics the runtime depends on: creation gate and controller state and
  drains; load-gate holder rules (one labelled holder, the holder passes free,
  foreign threads wait); phase-scheduler failure semantics (fail-fast, timeout,
  cancellation); latches and switches
- exception texts users read, above all the conjure validation report layout
  (`test_spellbook_validation_error.py`)
- `SignatureReflection` output for `TYPE_CHECKING`-only names; creation-cache
  persistence round trips; exact line accounting in the agent text reader
Key Files (C1):
- `tests/unit/melder/utilities/synchronization/test_creation_gate.py`
- `tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py`
- `tests/unit/melder/utilities/synchronization/test_load_gate.py`
- `tests/unit/melder/utilities/synchronization/test_phase_scheduler.py`
- `tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py`
- `tests/unit/melder/utilities/helpers/test_signature_reflection.py`
- `tests/unit/melder/utilities/test_caching_system.py`
- `tests/unit/melder/utilities/ai_native_support_tools/test_agent_text_reader.py`
- `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`

### Subcomponent: Repository Tooling Unit Cluster
Parent Component: Unit Test Suite
Purpose:
- cover tooling that is not `melder`: the CI scripts under `.github/scripts/`, the
  LLM support bundle builder and the architecture-docs tool; each is loaded by path
  (or from its own package) and never boots Melder
Protects:
- fail-closed CI policy: forged or stage-skipping routes refused, every mandatory
  job required, publication only for the live candidate with a resolved release
  tag, and the runtime guard checking actual free threading
- candidate and source qualification: identical trees across merge SHAs, no fallback
  to an older green run, bounded waits and API reads, immutable uploads
- distribution contents (wheel and sdist members, versions, the PEP 561 marker) and
  reproducible sdist normalization; workflow wiring checked on parsed YAML
- the LLM bundle builder's deterministic build/check lifecycle and explicit
  opt-in for untracked files; the architecture-docs tool's manifest, link, anchor
  and render-hash checks
Key Files (C1):
- `tests/unit/github_workflows/conftest.py`
- `tests/unit/github_workflows/test_ci_policy.py`
- `tests/unit/github_workflows/test_workflow_contracts.py`
- `tests/unit/github_workflows/test_candidate_publication.py`
- `tests/unit/github_workflows/test_source_qualification.py`
- `tests/unit/github_workflows/test_python_runtime_matrix.py`
- `tests/unit/github_workflows/test_distributions.py`
- `tests/unit/github_workflows/test_checkout_identity.py`
- `tests/unit/github_workflows/test_sdist_normalization.py`
- `tests/unit/llm_support/test_builder.py`
- `tests/unit/architecture_and_design/test_architecture_docs_tool.py`

""",
"### Subcomponent: Aether Integration Cluster\n": """### Subcomponent: Utilities Component Cluster
Parent Component: Component Test Suite
Purpose:
- validate synchronization pieces composed with real collaborators and the agent
  text reader against the real packaged documents
Protects:
- a creation-gate controller drain waiting for tickets in flight; the load gate
  and phase scheduler composed so a parallel restore runs behind held load
  authority; the scheduler's inter-phase guarantees
- the text reader's line accounting on real documents, not generated fixtures
Key Files (C1):
- `tests/component/melder/utilities/synchronization/test_creation_gate_component.py`
- `tests/component/melder/utilities/synchronization/test_load_gate_scheduler_cohort_component.py`
- `tests/component/melder/utilities/synchronization/test_phase_scheduler_pipeline_component.py`
- `tests/component/melder/utilities/test_agent_text_reader_component.py`

""",
"### Subcomponent: Mock Spellbook Fixtures\n": """### Subcomponent: Conduit Integration Cluster
Parent Component: Integration Runtime Suite
Purpose:
- validate conduits through the real meld front door: lineage, clusters,
  SpellSpaces, links, contracts, lifecycle and teardown
Protects:
- existence semantics across lineages, clusters and SpellSpaces (including scope
  ordering and structural resolution alignment), and SpellSpace isolation across
  threads
- link and contract transactions (a standalone add admits its own transaction;
  clearing a contract keeps the link), ownership transfer end to end, and
  automatic-mode refusal of dynamic APIs
- teardown: idempotent cleanup that blocks meld, and dependents disposed before
  their dependencies
Key Files (C1):
- `tests/integration/melder/conduit/test_conduit_integration_concurrency.py`
- `tests/integration/melder/conduit/test_conduit_integration_lifecycle.py`
- `tests/integration/melder/conduit/test_conduit_integration_links_contracts.py`
- `tests/integration/melder/conduit/test_conduit_integration_existence.py`
- `tests/integration/melder/conduit/test_conduit_integration_scope_resolution_alignment.py`
- `tests/integration/melder/conduit/test_conduit_integration_spellspace_scope_safety.py`
- `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`
- `tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py`
- `tests/integration/melder/conduit/test_ordered_disposal_runtime.py`

### Subcomponent: Multithreading Integration Cluster
Parent Component: Integration Runtime Suite
Purpose:
- run real threads against real runtime stacks and shared documents
Protects:
- link, bind and contract churn under concurrent meld workers, with orchestrated
  mutation lanes and mid-run cleanup
- the meld lock order: shapes that deadlocked while doors held the store lock now
  complete, each in its own child interpreter with a timeout backstop
- thread-safe first loads, private cursors and consistent search, walk and impact
  results on the packaged system documents and the agent text reader
Key Files (C1):
- `tests/integration/melder/multithreading/test_multithreading_link_bind_contract_features.py`
- `tests/integration/melder/multithreading/test_multithreading_spell_system_states.py`
- `tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py`
- `tests/integration/melder/multithreading/test_multithreading_system_document_view.py`
- `tests/integration/melder/multithreading/test_multithreading_agent_text_reader.py`

### Subcomponent: Live Sim Integration Cluster
Parent Component: Integration Runtime Suite
Purpose:
- bootstrap a small application the way a user would, in automatic and dynamic
  mode, and meld its root
Protects:
- automatic bootstrap resolving the application with interface-typed
  dependencies; dynamic bootstrap contracting owner dependencies into linked
  conduits before the application resolves
Key Files (C1):
- `tests/integration/melder/live_sim/bootstrap.py`
- `tests/integration/melder/live_sim/conftest.py`
- `tests/integration/melder/live_sim/test_live_sim_automatic.py`
- `tests/integration/melder/live_sim/test_live_sim_dynamic.py`

""",
}
