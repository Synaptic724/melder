# Melder System Plan

## Core Vocabulary
- `bind()` → register a service into the container
- `create_state()` → create a lifetime boundary ("state")
- `meld()` → resolve (create) a service
- `seal()` → finalize (dispose) a state
- `conduit.meld()` → resolve a service within a state

## Hooks System
- **Prehooks**: before service construction
- **Activation hooks**: during service instantiation (e.g., property injection)
- **Posthooks**: after service is created

## Lifetime Management
- **Unique**: One instance across entire container
- **Unique per Conduit**: One instance per created state
- **Many**: Always a fresh instance when `meld()` is called

## Debugging (Opt-In Feature)
- If `enable_debug_scope_ids=True`, Melder monkeypatches a ScopeID onto services.
- **ScopeID Contents**:
  - `scope_uuid`: UUID of the State that created this service
  - `scope_created_at`: Timestamp when the State was created
  - `object_uuid`: UUID of this service instance
  - `object_created_at`: Timestamp when the service instance was created
- All debugging features are **opt-in only** to preserve default performance.

## Named Bindings
- Allow registering multiple services under the same interface with **names**.
- Syntax:
~~~
  named_bind(name, interface, implementation)
~~~
- Constructor Injection:
  - Support `named_meld("name")` in constructors to resolve the correct version.

## Override Injection (Planned)
- Allow runtime overrides during `meld()` without needing a rebinding:
~~~
  svc = state.meld(UserService, overrides={IDatabase: CustomDatabase})
~~~
- Overrides are temporary and local to the resolution call.

## Scope and State Metadata
- Every State has:
  - UUID (`scope_uuid`)
  - Creation timestamp (`scope_created_at`)
- Every Service has:
  - UUID (`object_uuid`)
  - Creation timestamp (`object_created_at`)
  - Reference to the parent State’s UUID
- Metadata is stored inside an internal `_scope_id` field if debug mode is enabled.

## Diagnostics and Auditing (Planned Future Extensions)
- `state.inspect_live_services()`
  - List all active services inside a State with UUIDs and creation times.
- Optional tools to **dump live scope trees** for debugging giant systems.

## Core Principles
- **Explicit**: Nothing happens by accident; all injections are intentional.
- **Minimal**: No unnecessary complexity or magic.
- **Disciplined**: Services are managed cleanly with lifecycle boundaries.
- **High performance**: No-debug mode has minimal runtime cost.
- **Thread-safe**: Fully safe for concurrent service resolution and scope management.
- **No technical debt**: Every feature is intentional, justified, and minimal.
