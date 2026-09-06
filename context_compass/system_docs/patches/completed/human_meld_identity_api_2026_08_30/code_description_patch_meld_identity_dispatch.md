# Code Description Patch: Meld Identity Dispatch

<!-- BEGIN ENTRY: "Public meld dispatch control flow" -->
## Control Flow
For each public facade:

1. Reject `spell is not None and spell_id is not None`.
2. When `spell_id` is provided:
   - set internal positional target to `spell_id`;
   - set internal `spell_name` to `None`.
3. Otherwise, when `spell` is a string:
   - set internal positional target to `None`;
   - set internal `spell_name` to the string.
4. Otherwise:
   - pass the concrete `spell` value unchanged;
   - set internal `spell_name` to `None`.
5. Forward public `override` as internal `spell_override` unchanged.
6. Delegate through the existing dynamic/automatic, spellspace, or capability
   command path.

## Edge and Error Semantics
- Empty strings follow human-name normalization and fail through the existing key lookup.
- A 64-character human name is still a human name; no lexical SHA guessing occurs.
- An invalid explicit SHA fails through the existing ID `KeyError`.
- Binding names and overrides are passed unchanged.
- Unsupported override shapes still fail at the internal runtime boundary.

## Invariants
- No ID request enters `SpellInputUtils`.
- No human string enters `_resolve_spell_by_id` at the public boundary.
- Dynamic tickets and nested spell-index gates remain exactly where they are.
- Internal fast-door entries remain keyed by actual ID strings.
- No internal override symbol, compiled artifact, or cache key is renamed.

## Idempotency and Lifecycle
Dispatch is stateless and allocation-light. It introduces no owned resources or cleanup.

## Explicit Non-Goals
- No compatibility heuristic based on string length, hex shape, or trial resolution.
- No provider/handle abstraction in this patch.
<!-- END ENTRY: "Public meld dispatch control flow" -->
