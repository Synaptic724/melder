# Component Patch: Resolved sockets and compiler propagation

<!-- BEGIN ENTRY: OVERRIDE_REQUIRED local topology and plan input -->
## Before and After
Before, every annotation/SpellMap match becomes an executable dependency and Phase 3 derives socket
kind from declaration alone. After, a selected False definition creates OVERRIDE_REQUIRED with empty
target_spell_ids and descriptive referenced_spell_ids. False roots describe their own declarations
without attempting provider resolution or generating constructor edges.

## Records and Ownership
- SpellSocketDescriptor appends referenced_spell_ids (tuple[str, ...]) and parameter_kind (optional
  inspect-parameter kind name). Phase 3 obtains position/kind from the real Phase-1 parameters.
- Phase-1/2 objects remain untouched. SpellSystemStates continues owning the local topology.
- SpellInjectionParamSource carries reference IDs, position and kind for override_required entries.
- SpellInjectionInstanceSpec derives required_override_params: tuple rows of
  (parameter name, position, kind name, reference-ID tuple). Values only, with no supplied live object.
- Generalized and standalone many-only steps retain the same value rows across both plan variants.
  Model/plan cleanup releases their existing owned containers; no application ownership is added.

## Selection and Validation
Apply capability after scan/index matching, not inside the candidate index. Explicit descriptor
selection keeps cardinality. Required override sockets keep dependency_key for revalidation while
reference IDs never enter the construction DAG. Keep normal PLAIN and SpellContract kinds.
Phase-4 required-input diagnostics borrow local topology. Binding cycles exclude False roots and
OVERRIDE_REQUIRED sockets instead of rebuilding their construction edges from declarations.
DI shape, variadic and provider-presence rules must not make a descriptive root unregistrable;
profile shape, existing-object policy and explicit descriptor integrity remain checked.

## Executable Root Boundary
Phase-5 snapshot/index/blueprints represent executable entries only. Local topology/registration
stores keep False entries for discovery. Do not build fallback blueprints for False entries.
Existing artifact publication scope is unchanged. Empty executable worlds remain valid.

## Downstream Propagation
Phase 8 signatures include socket kind, references, position/kind and collection/optional flags.
Phase 9 reads durable topology to emit override_required rows even with no occurrence dependencies.
Both generalized dual/single builders and standalone many-only builders preserve required value rows.
Optional override metadata stripping cannot remove required-input obligations.

## Validation
Prove per-socket reference identity and zero executable edges, ordinary provider precedence,
default/Optional/collection distinctions, descriptive-cycle success versus real-cycle failure,
False-root exclusion, retained blueprint socket addresses, and every planner variant's value rows.
S4 supplies execution and compiled-cache tests; S6 supplies record replay tests.
<!-- END ENTRY: OVERRIDE_REQUIRED local topology and plan input -->
