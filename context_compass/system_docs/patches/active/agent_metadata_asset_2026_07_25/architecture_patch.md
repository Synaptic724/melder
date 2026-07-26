

# Architecture Patch: Agent metadata moves from class bodies to a harvested build asset

## Metadata
- Patch ID: agent_metadata_asset_2026_07_25
- Ticket: TASK-2026-07-25-agent-metadata-build-asset
- Owner: melder_0
- Status: active
- Created: 2026-07-25T20:50:00Z
- Updated: 2026-07-25T20:50:00Z

## Objective
Stop 370 class bodies from owning `__ast_helper_access__` and `__agent_purpose__`.
Author both facts in class docstrings, harvest them at build time into a generated
asset, and have `ClassSurfaceAstDescriber` read the asset instead of
`type(obj).__dict__`.

## Non-Goals
- Changing WHAT any class's access level or purpose says. This is a relocation; the
  fidelity test asserts every harvested value is byte-identical to today's attribute.
- Touching the `Registration:` docstring section. It answers a different question
  (may this be BOUND as a spell) which the internal-bind manifest now owns.
- Resolving the 10 PENDING classes. They are catalogued deliberately.
- Deciding the fate of `Package`. Owner-parked pending a keep-vs-remove call.

## Why (measured, not asserted)
- 788 marker assignments across 370 files.
- 76,200 characters of prose, ~115 KB resident in class dicts for the life of every
  process.
- Exactly ONE consumer: `ClassSurfaceAstDescriber`, at three call sites.
- The access-value validation currently raises at RUNTIME, from the describer,
  whenever something happens to describe an offending object - potentially in
  production. As a build asset it fails in CI instead.

## The `-OO` question, settled
The sibling epic's docstring proposal was rejected for the REGISTRATION GUARD because
`python -OO` strips docstrings and the guard must work at runtime in any interpreter.
That objection is correct there and VOID here. Measured:

    class attributes under -OO      : present
    docstrings under -OO            : STRIPPED
    ast.get_docstring on SOURCE     : works under -OO

`-OO` strips docstrings from BYTECODE, never from source. The harvester AST-parses
source text at build time and emits the prose as ordinary string data, so no consumer
downstream ever reads a docstring at runtime. This is what lets the two epics compose
instead of conflict.

## Changed Components
| Component | Change |
|---|---|
| `_build_assets/_agent_metadata/` | NEW. Harvester + generated asset. |
| `_build_asset_runner.py` | No change. Discovers the new asset by convention. |
| `ClassSurfaceAstDescriber` | Metadata resolution moves from `__dict__.get` to asset lookup. |
| ~370 class bodies | Markers move into docstrings; 788 assignments deleted. |

## Invariants
- INV-1 FIDELITY. Every harvested `(access, purpose)` equals the value that class
  carried before migration, byte for byte. Pinned by
  `test_harvest_reproduces_every_live_class_attribute_exactly`.
- INV-2 PRECEDENCE. Where both a docstring marker and a legacy attribute exist, the
  DOCSTRING wins. Reversing this would make a migrated class keep emitting its old
  value, so the codemod would appear to do nothing.
- INV-3 THREE STATES. Every class resolves to exactly one of marked / exempt /
  pending. "Deliberately excluded" and "not done yet" must never be indistinguishable
  again - that ambiguity is the defect this patch exists to remove.
- INV-4 EXEMPTION BY PATH. `aether.spellbook.spell_compiler` is exempt wholesale by
  builder rule, not by stamping 173 files. A class inside it may opt back in with an
  explicit marker.
- INV-5 BUILD-TIME VALIDATION. An access value outside
  `{public, internal, private, exempt}` fails `render()`, not a runtime describe call.
- INV-6 DETERMINISM. `render()` is pure; two calls at one version over one tree return
  byte-identical text. `--check` is a byte comparison and depends on this.

## Interface Deltas
Additive:
- `agent_metadata.AGENT_METADATA: Dict[Tuple[str, str], Tuple[str, str]]`
- `agent_metadata.EXEMPT: FrozenSet[Tuple[str, str]]`
- `agent_metadata.PENDING: FrozenSet[Tuple[str, str]]`
- `agent_metadata.CLASS_BASES: Dict[Tuple[str, str], Tuple[str, ...]]`

Removed (phase 2):
- `<class>.__ast_helper_access__`
- `<class>.__agent_purpose__`

BREAKING SURFACE NOTE: these are dunder-named class attributes on public classes.
Anything outside melder reading them directly breaks. No in-repo consumer other than
the describer exists; external consumers are UNKNOWN and this is called out rather
than assumed away.

## Inheritance Resolution (owner ruling)
`ClassSurfaceAstDescriber` builds `inherited_agent_purposes` by walking base classes.
An asset lookup is exact-match and does not inherit - the same tension the internal-bind
manifest hit. Owner chose BUILD-TIME PRECOMPUTATION: the harvester records statically
resolvable base names in `CLASS_BASES`, and the runtime stays a single lookup with no
MRO walk.

ACCEPTED LIMITATION: AST cannot see dynamically created or conditionally imported
bases. Those classes will carry incomplete base chains. The mitigation is to make the
gap NAMED rather than silent - `--check` should report classes whose bases could not be
resolved statically, so the blind spots are visible instead of quietly wrong.

## Migration Order
1. PHASE 1 (DONE, additive): harvester, generated asset, 19 tests. Nothing imports the
   asset, so no runtime path changes and the patch gate does not fire.
2. Codemod A: inject `AGENT_ACCESS:` / `AGENT_PURPOSE:` sections into docstrings from
   the existing attribute values. Idempotent; skips classes already migrated.
3. Regenerate. The asset must be UNCHANGED - dual-source means the harvested values are
   identical whichever side they came from. A diff here is a codemod bug and is the
   cheapest possible detector for one.
4. Codemod B: delete the 788 attribute assignments.
5. Regenerate. Asset unchanged again; all sources now read `docstring`.
6. Repoint `ClassSurfaceAstDescriber` to the asset.
7. Delete the attribute fallback from the harvester.

Steps 3 and 5 are the safety property of the whole plan: the asset is a fixed point
across the migration, so any drift localises to the codemod step that caused it.

## Rollback
- Phase 1: delete `_build_assets/_agent_metadata/`. Purely additive.
- Codemod A: revert; attributes were never removed, so the tree is already correct.
- Codemod B: the highest-risk step. Revert restores the assignments; the asset does not
  change because the docstrings already carry the values.
- Step 6: revert one module. The asset can stay in place, unread.

## Validation Expectations
- `python src/melder/_build_assets/_build_asset_runner.py --check` green.
- `pytest tests/unit/melder/build_assets -q` green.
- Asset byte-identical across steps 3 and 5.
- Owner-run `pytest tests/unit/melder -q` on 3.14t after step 6.
- NOT RUN by the authoring agent: sandbox is Python 3.10, repo floor is 3.14t.

## Ticket Coverage Matrix
| Step | Ticket | Status |
|---|---|---|
| Phase 1 harvester + asset + tests | TASK-2026-07-25-agent-metadata-build-asset | done |
| Codemod A/B | same ticket, phase 2 | blocked on this patch set |
| Describer repoint | same ticket, phase 2 | blocked on component patch |

## Unknowns
- UNKNOWN: whether any consumer OUTSIDE this repository reads
  `__ast_helper_access__` / `__agent_purpose__` off melder classes. CommandOps is the
  obvious candidate and has not been checked. Investigate before step 4.
- UNKNOWN: how many classes have statically unresolvable bases. Quantify during
  codemod A rather than guessing now.
