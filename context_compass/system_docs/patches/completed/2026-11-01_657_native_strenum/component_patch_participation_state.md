# ParticipationState canonical value contract

<!-- BEGIN ENTRY: "Participation state and registry row" -->
## Before and after
ParticipationState has four lowercase values for uppercase names. Afterward each value
equals its name exactly. This changes direct .value, str and JSON encoding intentionally.

## Compatibility and identity
Exactly registered/configured/active/inactive remain accepted as legacy raw by-value
tokens and old pickle payloads; their canonical uppercase names are also accepted.
Mixed-case, whitespace and unknown raw values remain invalid. Registry mutation and
filtering continue to require actual ParticipationState members; no bare string or
foreign enum is admitted at these typed APIs.

## Projection and lifecycle
Both registry description paths use the shared row renderer. Preserve their historical
lowercase plain state strings separately from the new enum .value. Only ACTIVE emits;
registered/configured/inactive remain silent. No ownership, locking or cleanup changes.

## Validation
Use the four actual old protocol-4 payloads and prior registry behavior, plus canonical
value/JSON checks, strict unknown and family negatives, and the full participation and
mediator test modules.
<!-- END ENTRY: "Participation state and registry row" -->