# Frame Viewer Multi-View Flow Code Description Patch

## Control Flow
1. start from the already attached projected views
2. reuse deterministic frame/link ordering from the existing helper surface
3. group, filter, count, or summarize from that derived link list
4. return detached results

## Error Semantics
- invalid `source_kind` filters fail fast
- missing frame lookups continue to fail fast through existing `get_view(...)`

## Non-Goals
- no fuzzy matching
- no update subscriptions
- no repository/cache behavior
