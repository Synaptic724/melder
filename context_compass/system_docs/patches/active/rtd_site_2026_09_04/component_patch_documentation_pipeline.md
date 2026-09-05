# Component Patch: Documentation Pipeline

## Purpose and Current Boundary
The repository has canonical public source material but no local Sphinx publication component.

## Before and After
Before: readers follow repository Markdown and scripts; advertised RTD configuration is absent locally.
After: one command assembles selected sources, creates navigable pages, runs Sphinx, and reports checks.

## Interface Deltas
- Inputs: validated navigation metadata, authored pages, selected source/diagram paths, version metadata.
- Outputs: generated source and HTML under docs/_build, with clear exit status and build logs.
- Errors: malformed metadata, duplicate IDs, missing inputs, path escape, and builder failures are explicit.
- Native Sphinx configuration uses its required module-level configuration interface; it is docs config,
  not a new Melder runtime global or import/export convention.

## State and Lifecycle
The pipeline owns generated directories only. Files are read with bounded ownership and handles close
after use. Existing source, virtual environments, Git metadata, and other agents' records are never cleaned.

## Failure Modes
Validate before staging. Missing/malformed sources stop with a useful path and reason. Sphinx nonzero
status propagates. Keep logs and generated output for diagnosis; never call a failed build published.

## Dependency and Ordering
Navigation/schema precedes output generation. Static version reading precedes Sphinx configuration.
Source selection and path validation precede generated-directory replacement. Sphinx consumes the result.

## Validation Expectations
Targeted checks cover containment, duplicate/missing IDs, parent ownership, source equality, and repeatable
output. Real Sphinx/browser checks prove behavior not captured by metadata-only checks.

## Unknowns
Exact import/docstring edge cases are measured in the first real build. Catalog and reference extensions
must preserve the pipeline interface and publication boundary.
