# Book and Bind component patch

## Before
Bind constructs Spell/profile/index. Book attaches application-creation hooks and publishes active or
parked registrations. Bind has cleanup, but Book's core teardown only drops the Bind reference.

## After
- Book exposes add_bind_hooks and clear_bind_hooks; callback sequences live on its own Bind.
- Bind retains one immutable three-stage tuple per operation. Book carries that same tuple to post.
- Registration validates every supplied callback before changing any stage. Append order and duplicate
  registrations are preserved. Clear affects future binds. Current callback sets remain alive locally
  until their in-flight bind ends, including when a callback changes registration itself.
- Pre executes before reflection/construction, after Book transaction admission; activation follows
  construction before profile completion. User callbacks execute outside Bind's construction lock.
- Book invokes post after normal active/inactive publication and before leaving its bind envelope.
- Bind wraps callbacks using existing HookExecutionError and locally tears down unpublished activation
  failures. Collision refusals must not emit post; no new generalized rollback layer is introduced.
- Book explicitly cleans its owned Bind before discarding it. Callbacks are released, never disposed.

## State/concurrency
Hook tuple replacement and marker refresh serialize on Bind's RLock. Read capture retains one immutable
tuple reference. The refresh calls a narrow Book emission seam that acquires no Book registry lock.
Application callbacks are outside Bind's lock; nested binds continue through existing mediator joins.
Book cleanup keeps normal caller responsibility for quiescing active runtime work.

## Validation mapping
Ordering/subjects, add/clear during callback, invalid mixed registrations, per-book/config isolation,
active/staged/post-conjure wrappers, existing creation hooks, captured failed-Spell cleanup, retry,
native refusal and transaction behavior. Existing Bind/Book tests qualify compatible native behavior.
