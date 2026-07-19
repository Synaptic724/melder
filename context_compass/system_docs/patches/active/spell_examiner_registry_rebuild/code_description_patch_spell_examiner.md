# code_description_patch_spell_examiner

## Trigger justification
This rebuild changes the active profile-creation control flow and removes a
public runtime middle-state API that no longer matches the requested contract.

## Control-flow description
1. `SpellExaminer.__init__` registers only `general` and `detailed`.
2. `create_profile(target, profile_name, show_dunders, max_repr)` validates the
   requested profile and dispatches through the registry.
3. `create_profile(raw_candidate, "general")` returns a partial
   `SpellGeneralProfile` with binding data only.
4. `Bind` fingerprints and type-checks through `profile.binding_profile`, then
   constructs the `Spell`.
5. `profile.complete_with_spell(spell)` fills the resolution side in place, and
   the same profile object is assigned onto `spell.profile`.
6. `create_profile(..., "detailed")` follows the same two-step lifecycle, with
   `SpellDetailedProfile` inheriting from `SpellGeneralProfile` and adding the
   extra class/callable/member inspection layer on completion.
7. Direct consumers of `spell.profile` normalize `general` / `detailed`
   instead of assuming raw binding-profile or AI-profile storage.

## Validation focus points
- registry initialization
- create_profile dispatch
- bind ownership and reuse of the examiner
- two-step profile completion on the same object
- no helper creators or explicit examiner lock
- no separate general/detailed strategy layer
- consumer normalization through `general` / `detailed`
