# Scope-aware purge architecture patch

## Scope and non-goals
Patch id: scope_aware_purge_2026_09_20. Add targeted creation retirement through existing runtime
owners. Do not unbind, recompile, cascade dependencies, redesign supplied objects or use extraction.

## Changed components
| Component | Delta |
| --- | --- |
| Creations and SpellSpace | Native locked retirement and strictly local SpellSpace facade |
| Meld Resolution Runtime | Existing Spell lookup, authority check and target-store discovery |
| Conduit Runtime | Public purge facade mirroring meld's identity selectors |

## Interfaces and boundaries
Conduit/SpellSpace.purge(spell=None, *, spell_id=None, spellframe=None, binding_name=None,
purge_all=True) -> int. True selects all retained target entries; False selects the supplied instance.
Instance input is inspected to obtain its class, then enters existing lookup. Explicit selectors are
the alternative path; no reverse index or automatic qualifier recovery is added. False requires an
instance. No public internal-Spell targeting or runtime Spell import is added. Concrete Meld doors
keep scope policy; Creations.purge(spell, purge_all=..., creation=...) owns locks/removal/disposal only.

## Cross-component invariants
Caller identity cannot be replaced by compilation-root identity. SpellSpace never delegates to
broader stores. Root/leader authority follows the actual store and live Spell owner. Unique
retirement takes Spell lock before store lock; other modes take their selected store lock.
Both maps detach before disposal; no callbacks while holding removal locks. Existing meld is unchanged.

## Migration order
Regressions -> Creations primitive -> Meld routing -> public facades -> docs/descriptors/assets.

## Rollback
Remove the additive API/helpers/tests and regenerate assets. Preserve existing scope and compiler code.

## Validation
Exact scope/refusal matrix, real concurrent construction, duplicate purge, disposal failure/reentry,
falsey/container singleton values, warm reuse and scope pooling. Retain executed logs under the task.

## Ticket coverage
EPIC-2026-09-19-scope-aware-creation-purge -> TASK-2026-09-20-implement-scoped-creation-purge owns all rows.

## Unknowns
No unresolved core scope rule. Purge retires currently registered objects, not existing references or
future concurrent creations. Structural reconfiguration keeps its existing coordination requirement.
