# Spellbook transaction comparison compatibility

<!-- BEGIN ENTRY: "Spellbook binding windows and matching transaction forms" -->
## Boundary and behavior
Spellbook owns bind-window state while the frame mediator owns transaction sessions. Before this
repair lowercase bind calls are not recognized against the new uppercase member, so bind close
can raise after registration. Recognize enum members, their exact canonical names and exact
historical lowercase forms at existing bind-entry and close comparisons; other inputs retain
their prior treatment. The original request remains unchanged when sent to the mediator.

## State, failures and validation
Preserve nested-session joins, state preparation and outermost clearing, mismatch refusal,
exception propagation and the existing bind-end success behavior; add no locks or ownership
changes. Verify real bind, nested bind and cross-form close, including a genuinely different
request type. External callers and mixed-case tokens remain unqualified beyond existing rules.
<!-- END ENTRY: "Spellbook binding windows and matching transaction forms" -->
