# Component Patch: CommandSystem

## Before
`CommandSystem` owns the full broad public command vocabulary, including:
- topology mutation
- contract topology queries
- direct spell activation and reuse

That forces static to inherit commands it should never expose.

## After
`CommandSystem` should own:
- shared lifecycle / lock / gate / memory infrastructure
- shared projection/ACL/runtime helper methods
- only the public commands that every room should actually expose

Moved out of the base in this patch:
- `create_lesser_conduit`
- `create_cluster`
- `delete_cluster`
- `join_cluster`
- `leave_cluster`
- `list_clusters`
- `link`
- `sever_link`
- `meld`
- `meld_existing_spell`

## Validation Expectations
- Base supported-method discovery no longer advertises the moved methods.
- No remaining base logic depends on topology-mutation or activation deny sets.
