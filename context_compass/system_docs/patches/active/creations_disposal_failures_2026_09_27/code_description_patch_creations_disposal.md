# Code description patch: Creations._attempt_cleanup and its callers (2026-09-27)

## Trigger
Error semantics change: how many failures one disposal reports and what each carries.

## Control flow
Creations._attempt_cleanup((item, method_names)) -> List[Exception]:
  errors = []
  for name in method_names:                     # declared order
      try: item.__getattribute__(name)()
      except Exception as ex:
          error = RuntimeError(f"Failed to dispose object {_text(item)} using method '{name}': {_text(ex)}")
          error.__cause__ = ex
          errors.append(error)                  # keep going: later methods still run
  return errors
_text(value): str(value), or "<Type object at 0x..; str() raised ErrType>" when str() raises.
Callers: cleanup / clear_all / purge extend one list across entries (order unchanged) and raise one ExceptionGroup
when it is non-empty; refusal raises RuntimeError from errors[0] (one) or from ExceptionGroup(errors) (several).

## Edge and error behaviour
- BaseException (KeyboardInterrupt, SystemExit) is not caught, as before.
- A missing method is an AttributeError failure like any other; later methods still run.
- cleanup keeps its outer guard around the registry walk (a crash in the walk itself is still recorded).

## Invariants and idempotency
- Each declared method is called exactly once per disposal, whatever the earlier methods did.
- cleanup and clear_all stay idempotent; a second call finds nothing to dispose.

## Non-goals
- No retry, no rollback of removal, no logging inside Creations (callers log or raise).

## Validation focus
- Probe objects with two failing methods, a failing `__str__`, and many-bucket members; call counts and group
  contents asserted per path (cleanup, clear_all, purge, refused publication).
