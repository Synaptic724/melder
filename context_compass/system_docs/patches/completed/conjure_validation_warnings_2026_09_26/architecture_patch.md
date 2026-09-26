# architecture_patch

## Metadata
- Patch ID: conjure_validation_warnings_2026_09_26
- Status: promoted to src_architecture/src_components and archived 2026-09-26T10:12:55Z
- Owner: user (implementation: melder_0)
- Task: TASK-2026-09-26-add-conjure-validation-warnings-flag
- Created: 2026-09-26T09:19:49Z

## Patch Scope and Non-Goals
- Objective: conjure stops logging an unconditional INFO line about unresolved inputs. The public
  `Spellbook.conjure` gains `validation_warnings: bool = False`; with True, conjure logs every Phase-4
  validation warning once, grouped by warning code, at WARNING level through the book logger.
- Non-goals: Phase-6 system-validation diagnostics; changing any warning's code, severity or message;
  adding the flag to Nexus frame creation, crystallizer restore, `_conjure_existing_conduit`
  (upgrade_to_normal) or any other internal conjure route; a configuration property for the flag.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Spellbook Core (conjure) | modify | public keyword, threaded into the creation system | none |
| SpellbookCreationSystem (conjure prep) | modify | report only when asked; all warning codes, grouped | Spellbook conjure |

## Interface and Boundary Deltas
- Public, additive: `Spellbook.conjure(policy="default", dynamic=False, name=None, conduit_logger=None,
  validation_warnings=False)`. Existing positional and keyword calls are unchanged.
- Behavior change (deliberate, owner-requested): default conjure no longer logs
  "Conjure: N unresolved input(s) ...". UnresolvedInputError at meld is unchanged.
- Internal: `SpellbookCreationSystem.__init__` takes `validation_warnings`; the static
  `_prepare_spellbook_for_conjure` takes `validation_warnings: bool = False`.

## Cross-Component Invariants
- The report reads Phase-4 results after the structural phases and before resolution releases them;
  it never changes validity, phase results or conjure success.
- One log event per conjure at most; none when the flag is False or there are no warnings.
- Internal conjure routes never pass True.

## Migration / Rollout Order
1. Creation system: slot, constructor, cleanup, prep keyword, grouped reporter.
2. Spellbook: conjure keyword and docstring, window threading.
3. Tests: default silent, True grouped output, upgrade route silent.
4. Canonical docs, graph descriptors, release note; build assets and LLM bundles.

## Rollback Constraints
- Source-only revert. No cache, record or serialized format is involved.

## Ticket Coverage Matrix
| patch section | ticket | validation |
|---|---|---|
| Public keyword | TASK-2026-09-26-add-conjure-validation-warnings-flag | component: default silent, True logs |
| Grouped reporter | same | unit: grouping, ordering, entry rendering |
| Internal routes silent | same | component: upgrade_to_normal emits no report |

## Evidence
- tickets/tasks/2026-09-26_add_conjure_validation_warnings_flag_task.md (notes)
