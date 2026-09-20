# Control Flow Patch: Capability survives graph and record boundaries

<!-- BEGIN ENTRY: Value-only publication and rebuild -->
The trigger is cross-component policy propagation: losing False on replay silently permits construction.
Publish from a live Spell after normal structural compilation; copy selected relationships into the
fresh descriptor. Query through current ACL-visible records. Rebuild changed graph data at normal
publication points, never by inserting runtime checks on every successful meld.

Capture reads native Spell.resolvable once. Persistence retains the plain bool. Major-version admission
runs before new payload interpretation. Restore/graft pass the bool to normal binding; constructor
graphs rebuild from those bindings, and identity translation remains the existing loader's responsibility.
On replay failure preserve the existing all-or-nothing cleanup; graft keeps its existing per-member
shortfall contract. No arbitrary object state restoration or custom required-input preflight.
<!-- END ENTRY: Value-only publication and rebuild -->
