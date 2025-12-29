# error_record_prompt

Purpose
- Standardize error records stored under context_compass/branch_management/<branch>/state/errors/.

Required fields
- error_id, when, owner_id, category, message, details
- work_id, target_path, ctx_path (null if unknown)

Category enum
- parse_error | permission | lease_conflict | schema_invalid | tool_crash | unknown

Example
```json
{"schema_version":1,"error_id":"err_000001","when":"2025-12-28T00:00:00Z","owner_id":"agent:local","work_id":"task_000042","target_path":"src/pkg/foo.py","ctx_path":"src/pkg/__foo__.json","category":"schema_invalid","message":"ctx failed schema validation","details":{"schema":"file_ctx.schema.json","error_count":2}}
```
