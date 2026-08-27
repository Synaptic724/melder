# component_patch_spell_profile_consumers

## Component purpose and boundary in current architecture
The direct `.profile` consumers are the small runtime surfaces that currently
assume `spell.profile` is either binding-profile-shaped or `SpellAIProfile`:
- `spellbook_creation_system.py`
- spell-crafter validation strategies
- `FrameDescriptorManager`

## Before/after behavior summary
- Before:
  - creation-system disposal discovery only understands `ClassBindingProfile`
  - validation strategies assume raw binding-profile types on `.profile`
  - Nexus publish special-cases only `SpellAIProfile` and otherwise treats
    `.profile` as the binding profile, reading `spell.resolution_profile`
    separately
- After:
  - these consumers normalize `SpellGeneralProfile` and `SpellDetailedProfile`
  - binding data is read through the general profile
  - resolution data is read through the general profile or the detailed profile
  - detailed-profile special-casing replaces AI-profile naming

## Validation expectations
- creation-system disposal discovery still finds class disposal methods through
  the normalized binding profile
- validation strategies still reject missing/mismatched existing-creation and
  callable targets through normalized binding-profile access
- Nexus publish stores binding, resolution, and detailed-profile data from the
  new normalized profile shapes
