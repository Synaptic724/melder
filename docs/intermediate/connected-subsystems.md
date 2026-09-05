# Compose platform → services → workflows

Prerequisites: [addressing](../beginner/addresses.md),
[dynamic linking](dynamic-linking.md), and [SpellContract](late-binding.md).
Run saved Intermediate lesson 26 from a checkout, or unpack the complete collection
so its `_dynamic_world.py` helper stays beside the script.

The application has three categories with separate books and owners:

| Category | Owns | Needs from the previous category |
| --- | --- | --- |
| `platform` | `ConfigStore` | Nothing |
| `services` | `ReportService` | `ConfigContract` named `platform` |
| `workflows` | `ReportWorkflow` | `ReportingContract` named `reporting` |

For the first edge, conjure the provider and consumer, link, pull the provider's
spell, and meld the service. Repeat the same five steps for the next edge using
that completed service as the provider's product.

## Read the result

The script asserts that `workflow.service is service`: the resolved service crosses
the second boundary. Its `run()` result combines the workflow, report, and the
region value returned by the platform store. Inspect all three class definitions
in the complete linked example alongside the core operations below.

When applying this pattern, give each root an application owner and end those
owned runtimes explicitly. Keep the [scoped-cleanup pattern](scopes.md) beside the
composition pattern; construction and shutdown are both part of your design.
