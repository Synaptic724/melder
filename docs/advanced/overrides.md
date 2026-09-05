# Target a dependency inside the graph

Prerequisite: [flat overrides](../intermediate/overrides.md). The key in the
`override` mapping expresses how to find a constructor socket below the melded root.

| Form | Example | Match rule |
| --- | --- | --- |
| Exact path | `transport>credentials` | The named socket path |
| Unique wildcard | `*credentials` | Exactly one matching socket |
| Broadcast | `**credentials` | At least one matching socket; apply to all matches |

The wildcard lesson exercises one match, multiple matches, no matches, and overlap.
When a broadcast and exact path name the same socket, the exact path takes precedence.
The complete example keeps its objects `many` so later melds construct clean graphs.

## Targeting and lifetime are separate decisions

The deep-path lesson deliberately uses `unique`. Its override helps construct a
singleton transport, and a later plain meld retrieves that same transport with
the injected credentials still inside it. The substitution lasts as long as the
object it helped create. It is not automatically limited to the duration of a call.

Run both examples: the first demonstrates this lifetime consequence; the second
demonstrates the match grammar and fresh-instance contrast.
