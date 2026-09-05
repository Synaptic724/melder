# Configure the world before it starts

Prerequisites: [world boundaries](worlds.md) and
[dynamic linking](../intermediate/dynamic-linking.md). A frame's posture decides
which kinds of runtime operations its books may perform. Configure it before the
first conjure settles the world.

The public-door lesson calls `book.configure_aether_frame(system_state="dynamic",
...)` before conjure. A second book in that named frame uses plain `conjure()`;
the example then links the two roots to demonstrate inherited dynamic posture.
Reconfiguration after freeze is shown as a refusal.

## Keep the configuration objects distinct

| Object | Responsibility |
| --- | --- |
| `SpellbookConfiguration` | Book policy, including disposal and scheduler choices |
| `AethericFrameConfiguration` | World posture and eligibility for runtime operations |
| `AetherConfiguration` | Root policy, including automatic logging setup |

The configuration-object and root-builder lessons walk their complete setup
sequences. Follow the terminator for the object you hold; constructing a
configuration is not the same as activating the corresponding subsystem.

Continue to [logging](logging.md) for the explicit post-boot attachment path.
