# Component patch: Phase-1 requirements

<!-- BEGIN ENTRY: "SpellRequirementsFinder ordinary defaults" -->
## Before and after
Before: a class/list annotation remains inferred DI despite an ordinary default; has_default only
contributes to is_optional. Phase 3 then injects a provider or rejects its absence.
After: _classify_parameter returns PLAIN for ordinary defaults before inspecting inferred DI shape.

## Precedence
1. Existing SpellContract default handling.
2. Existing SpellMap default handling.
3. Ordinary has_default -> (PLAIN, True, None, None).
4. Existing no-default annotation inference.

## Data and lifecycle
_build_parameter_requirements continues retaining annotation, default_value, has_default and signature
order. No default value is copied or registered as a provider. Normal Python calling semantics apply.
PLAIN parameters remain metadata sockets and produce no inferred dependency edge.

## Implementation and tests
Target: src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py.
Update the classifier/class contracts and narrowly update tests expecting old default-driven DI.
Validate None, instance, collection, scalar and falsey defaults; preserve explicit descriptors and
no-default DI, including nullable annotations and missing required providers.
<!-- END ENTRY: "SpellRequirementsFinder ordinary defaults" -->
