# Architecture Patch: Melder documentation publication system

- Patch ID: rtd_site_2026_09_04
- Owner: codex_2
- Status: ready for scoped implementation

## Scope and Non-goals
Add a documentation-only publication layer over canonical README, example, architecture, and public
API sources. The four reader levels are Beginner, Intermediate, Advanced, Expert. Runtime behavior,
runtime dependencies, and other agents' changes are outside this patch.

## Changed Components
| Component | Before | After |
| --- | --- | --- |
| Documentation pipeline | No checked-in Sphinx/RTD build | Deterministic public-source assembly and local/CI/RTD HTML build |

## Interface and Boundary Deltas
- docs/tools/build_docs.py exposes prepare, build, and check operations with explicit output paths.
- docs/navigation.toml defines the ordered page/level hierarchy; generated contents uses the same data.
- Canonical source stays in its existing directories. Only selected public inputs enter generated output.
- Sphinx runs with docs/conf.py over docs/_build/source; output is generated and ignored by Git.
- Later catalog/reference tasks extend the same pipeline instead of adding an independent publisher.

## Cross-component Invariants
- Four exact learning levels; complete contents and prominent example routes.
- One canonical source per prose/script/diagram; no hand-maintained executable copies.
- Source preparation must validate input paths and IDs before touching generated output.
- Recursive cleanup is allowed only for resolved generated subdirectories beneath docs/_build.
- Package imports used by autodoc occur only during its build; version lookup itself is static.
- No runtime API/typing changes just to satisfy documentation tooling.
- User/agent coordination records are excluded from published source selection.

## Migration and Rollout
1. Establish isolated dependencies and public-source/navigation schema.
2. Add local foundation and representative real content; verify a strict build.
3. Extend through the existing catalog/curriculum/reference tasks with evidence after each tranche.
4. Add CI/RTD configuration and offline outputs, then verify hosted setup within authorized scope.

## Rollback
Revert the new docs/config/workflow files as a unit. Canonical example/runtime/architecture sources
remain usable. Remove only this pipeline's verified generated output; never delete source directories.

## Validation and Evidence Plan
Test path containment, duplicate/missing page IDs, deterministic ordering, complete navigation, and
source fidelity. Build real HTML and inspect a lesson, API, diagram, and mobile/keyboard navigation.

## Ticket Coverage
- Epic: EPIC-2026-09-04-readthedocs-documentation
- S1: TASK-2026-09-04-rtd-site-foundation (initial pipeline and representative build)
- S2-S7: catalog, curriculum, and reference tasks extend declared public inputs.
- S8-S9: CI/offline, hosted project, quality, and launch tasks verify publication behavior.

## Unknowns
Actual API docstring/annotation rendering is pending the first build. Resolve build failures from
evidence, without silently weakening runtime contracts or suppressing unrelated warnings.
