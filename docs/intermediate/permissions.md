# Link, pull, and choose permissions

Prerequisite: [dynamic mode and linking](dynamic-linking.md). A link creates the
relationship between two conduits. The borrower then requests a particular spell
from the conduit that owns it, using `add_spell_to_contract(...)`.

## The caller is the borrower

Keep these roles visible in your code:

1. The owner binds a spell and keeps its returned ID.
2. Both books conjure named conduits in the same dynamic world.
3. The conduits link.
4. The borrower names the owner and spell ID when it pulls the spell.
5. The borrower resolves through its own conduit.

An open link alone does not select the spells to share. The explicit pull is the
boundary where the request names both its target and permissions.

## Match access to the operation

The saved permission lessons compare `create`, `read`, and blocked sharing.
`create` allows construction through the contract; `read` is the more restricted
resolution path. Check whether the provider's instance exists before treating a
read request as permission to construct one. Follow the lesson's reported outcome
and refusal path rather than assuming every permission produces the same result.

Use [SpellContract](late-binding.md) when the object you are constructing declares
a dependency that will arrive over this relationship.
