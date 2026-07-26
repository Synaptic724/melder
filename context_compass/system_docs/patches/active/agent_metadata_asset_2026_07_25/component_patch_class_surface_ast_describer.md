

# Component Patch: ClassSurfaceAstDescriber reads the generated asset

## Metadata
- Patch ID: agent_metadata_asset_2026_07_25
- Component: `src/melder/utilities/helpers/class_surface_ast_describer.py`
- Ticket: TASK-2026-07-25-agent-metadata-build-asset
- Owner: melder_0
- Status: active
- Created: 2026-07-25T20:55:00Z

## Scope
The three sites that resolve agent metadata off live classes, and only those:

| Site | Current source |
|---|---|
| `_get_ast_helper_access` :669 | `type(obj).__dict__.get("__ast_helper_access__")` |
| `_get_agent_purpose` :710 | `type(obj).__dict__.get("__agent_purpose__")` |
| `_describe_inherited_agent_purposes` :745 | `base.__dict__.get("__agent_purpose__")` over `inspect.getmro(...)[1:]` |

## BLOCKER FOUND WHILE AUTHORING THIS PATCH

`_get_ast_helper_access` (:683) accepts only:

    if access_level not in {"public", "private"}:
        raise ValueError(...)

The live census of the codebase is:

    "internal"  325 classes
    "public"     79 classes
    "private"     0 classes

So the describer REFUSES the most common value in the codebase, and accepts a value
no class actually uses. Describing any of those 325 classes raises `ValueError` today.

This is a pre-existing latent defect, NOT introduced by this patch, and it is a hard
blocker on the repoint: migrating faithfully would preserve `internal` and the
describer would keep rejecting it. Two readings, and they need an OWNER RULING:

- (A) The describer's validation is stale. `internal` is legitimate - it is what 80% of
  marked classes declare - and the allowed set should be
  `{public, internal, private}`. Most likely, given the data.
- (B) `internal` was never valid and 325 classes are mis-marked. Then this is a data
  migration, not a relocation, and its scope is far larger than this patch.

Until ruled, `AgentMetadataPolicy.VALID_ACCESS` deliberately accepts `internal` so the
harvest stays FAITHFUL to source. The mismatch is recorded rather than silently
normalised - normalising it would destroy the evidence that the defect exists.

## SECOND FINDING: the inheritance precompute is insufficient as built

`_describe_inherited_agent_purposes` walks `inspect.getmro(type(obj))[1:]` - the FULL,
linearised MRO, in MRO order, including transitive ancestors.

Phase 1's `CLASS_BASES` records only DIRECT base names, unordered relative to
linearisation. That is not sufficient to reproduce current behaviour. Reproducing it
from a build asset requires either:

- (i) the builder computing the transitive closure and emitting an MRO-ordered chain
  per class - which AST can only approximate, since C3 linearisation depends on the
  full inheritance graph including bases from other modules; or
- (ii) the describer keeping `inspect.getmro` and using the asset ONLY as the
  purpose lookup, replacing `base.__dict__.get(...)` with
  `AGENT_METADATA.get((base.__module__, base.__qualname__))`.

RECOMMENDATION: (ii). It removes the class-attribute dependency - which is the actual
goal - while leaving linearisation to the interpreter, which is the only thing that can
compute it correctly. The owner's "precompute at build time" ruling was made before
this MRO detail was known; (ii) honours its intent (no metadata on classes) without
pretending AST can linearise. `CLASS_BASES` then stays as diagnostic data rather than
the resolution mechanism.

## Before / After

### `_get_ast_helper_access`
BEFORE: reads the class attribute; raises when absent; accepts `{public, private}`.
AFTER: looks up `AGENT_METADATA[(module, qualname)]`; raises when the class is absent
from the asset AND not in `EXEMPT`; accepted value set pending the owner ruling above.

### `_get_agent_purpose`
BEFORE: reads the class attribute; falls back to a generic public string; raises for a
`private` class with no purpose.
AFTER: reads the asset. Fallback and private-raise semantics UNCHANGED. Note the
private-raise has no live subjects today (0 private classes), so it is preserved as
contract, not as behaviour anyone currently depends on.

### `_describe_inherited_agent_purposes`
BEFORE: `inspect.getmro(...)[1:]`, reading each base's class attribute.
AFTER (recommendation ii): identical MRO walk, each base resolved through the asset by
`(module, qualname)`. Output shape, ordering, and skip-on-missing behaviour unchanged.

## State / Failure Deltas
- Missing metadata moves from "attribute absent" to "key absent from asset". Both
  raise; the message must name the class AND say to regenerate, or the failure will
  read as a code bug rather than a stale asset.
- Invalid access values can no longer reach the describer at all - `render()` refuses
  them at build time. This is a strict improvement: the same mistake currently reaches
  production.
- A class present in `EXEMPT` must not raise. Exempt means deliberately not agent-facing,
  which is a valid state, not an error.

## Dependency / Ordering
Repoint (step 6) MUST come after codemod B (step 4) and its regeneration (step 5).
Repointing earlier would read an asset whose values still come from attributes the
codemod is concurrently deleting.

## Validation Expectations
- Describing a `public` class returns the same access and purpose as before, byte-exact.
- Describing an `internal` class behaves per the owner ruling on the blocker.
- `inherited_agent_purposes` is byte-identical for a class with a deep chain -
  `Cleanable` subclasses are the natural probe at 325 descendants.
- A class absent from the asset raises with a regenerate instruction.
- An `EXEMPT` class does not raise.
- NOT RUN by the authoring agent: sandbox is Python 3.10, repo floor is 3.14t.

## Non-Goals
- Changing the generic public fallback string.
- Changing `ClassSurfaceDescription` / `ClassMemberDescription` shapes.
- Resolving the 10 PENDING classes, three of which are this component's own result types.

## Unknowns
- UNKNOWN: the owner ruling on `internal` (blocker above). Everything else is ready.
- UNKNOWN: whether CommandOps reads these attributes off melder classes. Must be
  checked before codemod B deletes them.
