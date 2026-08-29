# Projection Cache Flow Code Description Patch

## Control Flow
1. resolve descriptor and current ACL configuration
2. compute cache key
3. if cached, return a detached clone
4. otherwise compile and project once, cache that canonical projection, then
   return a detached clone
5. invalidate cache entries when touched descriptor or ACL mutation paths run

## Error Semantics
- cache lookup must not hide descriptor/ACL errors
- clone operations should fail fast if the cached projection is invalid
