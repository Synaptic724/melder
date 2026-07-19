# Contract And Viewer Cache Flow Code Description Patch

## Control Flow
1. resolve current projected frame views
2. compute a stable viewer cache key
3. on cache hit, return a detached viewer clone
4. on miss, build the viewer once, cache it, then return a detached clone
5. invalidate cached viewers on touched descriptor/ACL mutation paths

## Error Semantics
- invalid frame-name inputs still fail fast before cache use
- helper APIs should fail fast on invalid subject keys
