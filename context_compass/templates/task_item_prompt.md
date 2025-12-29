# task_item_prompt

Purpose
- Standardize task creation for context_compass/branch_management/<branch>/work_management/active/tasks.json.

Required fields
- work_id, state, kind, priority
- target_path, ctx_path
- parent_work_id, root_work_id (use null for top-level)
- reason (array of strings)
- lease (null when queued)
- attempts, last_error_ref

Lineage rules
- story items must include parent_work_id.
- tasks may be root or child; set parent_work_id/root_work_id when derived from an epic/story.

Do not include
- Human commentary outside reason[]
- Dynamic timestamps in reason[]

Example
```json
{"work_id":"task_000042","state":"queued","kind":"refresh_file_ctx","priority":90,"target_path":"src/pkg/foo.py","ctx_path":"src/pkg/__foo__.json","parent_work_id":null,"root_work_id":"task_000042","reason":["code_hash_mismatch"],"lease":null,"attempts":0,"last_error_ref":null}
```
