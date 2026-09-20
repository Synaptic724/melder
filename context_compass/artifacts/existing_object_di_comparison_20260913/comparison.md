# Existing objects in Dishka, Dependency Injector and Autofac

Research date: 2026-09-13. Owner: updater_0.
Task: TASK-2026-09-13-compare-existing-object-ownership-di.
Purpose: inform the deferred existing-object registration/lifecycle epic; no implementation selected.

Scope clarification after owner review: this general comparison is background only. The precise
remaining question is how the same user-created reference is represented when registered again,
resolved through multiple entries and released. Multiple same-type factory examples do not establish
those duplicate-reference identity or cleanup guarantees; they remain unverified across all three.

## Answer to uniqueness and multiplicity

All three support multiple objects of the same type. Their reuse rules concern a selected provider,
registration and scope. The following are different situations:

1. One registration repeatedly returns the same supplied object.
2. Two registrations supply two different objects of the same class.
3. Two service keys refer to the same underlying object.
4. Different scopes receive different objects for the same requested type.

Keep those identity domains separate when using the word unique. A fixed reference does not prohibit
other instances, and a new scope does not clone an object the application supplied explicitly.
The framework-specific mechanisms and evidence follow.

## Autofac

`RegisterInstance(existing)` accepts an already-created value for injection. Its upstream implementation
selects SingleInstance sharing and refuses incompatible lifetime/sharing changes for that registration.
This is one shared supplied value, not a process-wide prohibition on other instances of its type.
[Registration implementation](https://github.com/autofac/Autofac/blob/develop/src/Autofac/RegistrationExtensions.cs#L39-L81).

Multiple registrations can expose one service type. An unqualified single-service request normally
selects the last registration; `PreserveExistingDefaults` changes the default-selection choice.
`IEnumerable<T>` can return all registered services. A registration can expose several service types.
[Registration concepts](https://docs.autofac.org/en/latest/register/registration.html#default-registrations).

Use names or keys to distinguish two supplied loggers explicitly, for example `audit` and `worker`.
The type describes the service; the qualifier chooses the registration.
[Named/keyed services](https://docs.autofac.org/en/latest/advanced/keyed-services.html).

Autofac takes disposal ownership of provided instances by default. `ExternallyOwned()` leaves
disposal with the application. `OnRelease(...)` supports an explicit release callback and replaces
the normal disposal handling for that registration. Scoped sharing and disposal responsibility are
distinct choices.
[Disposal and provided instances](https://docs.autofac.org/en/latest/lifetime/disposal.html#provided-instances).

For constructed providers, SingleInstance shares across descendant scopes; InstancePerLifetimeScope
produces distinct cached instances in separate scopes. These policies describe sharing boundaries.
[Instance scopes](https://docs.autofac.org/en/latest/lifetime/instance-scope.html).

Autofac also has the specific `Owned<T>` relationship. It gives the consumer a value and control of
the child lifetime scope containing it. Disposing the handle ends that scope and releases its
non-shared disposable dependencies. `Func<Owned<T>>` creates repeatable units of work. It is not a
general-purpose API for moving any existing singleton from one owner to another.
[Owned instances](https://docs.autofac.org/en/latest/advanced/owned-instances.html).

## Dishka

Use `from_context(provides=T, scope=...)` to declare externally supplied data, then pass
`context={T: existing}` when entering that scope. A request consumer can require T normally.
Different request scopes can receive different prebuilt T values. Context keys are raw type hints,
not arbitrary name qualifiers or Annotated wrappers.
[from_context](https://dishka.readthedocs.io/en/stable/provider/from_context.html).

Scopes own their dependency caches; repeated retrieval normally reuses the selected value in that
scope. Generator factories supply finalization at scope exit. A context-supplied object does not
acquire an automatic close/cleanup callback merely from being present in context.
[Container lifecycle](https://dishka.readthedocs.io/en/stable/container/index.html),
[provider finalization](https://dishka.readthedocs.io/en/stable/provider/provide.html).

The standard APP/REQUEST hierarchy allows long-lived application dependencies and shorter-lived
request dependencies. A fresh request scope is a distinct cache boundary; external code still
chooses the actual value passed as its context input.
[Scope management](https://dishka.readthedocs.io/en/stable/advanced/scopes.html).

For simultaneous values of the same type within one container, use components to isolate provider
groups, or distinct semantic types such as NewType. Separate component providers can return the
different existing objects they were given; that does not require constructing the value again.
[Components and provider isolation](https://dishka.readthedocs.io/en/stable/advanced/components.html).

Important qualification: the context dictionary is shared across components. Merely declaring
`from_context(T)` in two components does not manufacture two independently named context values.
Use distinguishable inputs/providers when two different T objects are intended.
[Context data](https://dishka.readthedocs.io/en/stable/advanced/context.html).

Current stable docs also provide `collect(T)` to retrieve a list from multiple factories of T.
Without collection, the documented default is last-factory selection; an explicit override removes
the earlier candidates from collection. This is a multiple-provider mechanism, not two duplicate keys
inside one context dictionary.
[Multiple objects of the same type](https://dishka.readthedocs.io/en/stable/advanced/collect.html).

If Dishka should manage an externally acquired resource, a provider can yield that resource and
perform the agreed teardown afterward. The provider's code establishes cleanup responsibility;
returning/caching the object alone is a different contract.
[provide](https://dishka.readthedocs.io/en/stable/provider/provide.html).

## Dependency Injector

`providers.Object(existing)` retains and returns the supplied object. Two Object providers can hold
two different instances of the same class; consumers select the provider explicitly through wiring.
For example, an audit provider can retain logger A while a worker provider retains logger B.
[Object provider](https://python-dependency-injector.ets-labs.org/providers/object.html).

Its source stores the value in `_provides`; the Object provider's deepcopy copies the provider but
preserves the supplied reference. Therefore copying a provider/container arrangement must not be
assumed to clone the application object. Object has no resource-shutdown contract of its own.
[Object implementation](https://github.com/ets-labs/python-dependency-injector/blob/master/src/dependency_injector/providers.pyx#L434-L496).

`providers.List` and `providers.Dict` combine multiple provider results explicitly. Selection is
provider-oriented rather than an implicit global lookup of every object sharing the same Python class.
[List](https://python-dependency-injector.ets-labs.org/providers/list.html),
[Dict](https://python-dependency-injector.ets-labs.org/providers/dict.html).

`Singleton` creates and caches a result for its provider/container. Different container instances
have independent singleton results. Reset clears the reference and leaves further lifecycle to
Python; it is not an automatic call to the object's cleanup method. Thread-local and thread-safe
singleton variants are separate facilities.
[Singleton provider](https://python-dependency-injector.ets-labs.org/providers/singleton.html).

Use `Resource` when initialization and shutdown are part of the provider contract. A context-manager
initializer can acquire/yield the value and close it afterward; resources can be shut down individually
or via the container. Merely returning a value from a plain function initializer does not define a
custom shutdown callback. An already-created object can be supplied through such a lifecycle adapter
when explicit ownership is desired.
[Resource provider](https://python-dependency-injector.ets-labs.org/providers/resource.html).

## Concrete interpretation for the Melder discussion

Illustration, not framework code or an executed test:

```text
audit registration  -> logger A
worker registration -> logger B
```

A and B may have the same class. Reusing A every time audit is requested and B every time worker is
requested gives two stable supplied instances. That differs from pointing both registrations at A,
which gives two lookup paths to one physical object. If every request needs a fresh logger, either
external code supplies a fresh one per scope or a construction provider creates one.

Inference for Melder: requiring a fixed prebuilt registration to use a reuse lifetime can be coherent.
It does not by itself justify a one-instance-per-class restriction. Research must keep these separate:

- Service identity: which requested type/frame/name selects which registration?
- Registration identity: how many providers coexist, and how does default/collection selection work?
- Value identity: do those providers hold one object or several distinct objects?
- Scope/reuse: where is the selected reference visible and retained?
- Cleanup ownership: which party owns the disposal action, independently of reference sharing?
- Validation: how are declared contracts checked? Do not assume all three frameworks perform Melder's
  runtime Protocol member validation; that needs its own comparison.

The comparison supports keeping reference supply and resource lifecycle explicit. It does not select
one universal default: Autofac's provided-instance ownership default differs from the Python Object/
context patterns. Melder's accepted default-disabled configured-disposal flag remains a project choice.

The larger epic should retain experiments for two distinct prebuilt objects of one class; one value
under multiple aliases; providers sharing a supplied value across scopes; and release/transfer behavior
with one designated cleanup owner. These sources do not establish equivalence to Melder's arbitrary
ownership-transfer/rollback operations, so those remain a separate source-and-test investigation.

## Evidence limits

Official documentation was reviewed on 2026-09-13. Autofac pages identify version 9.0.0 and Dependency
Injector pages identify 4.49.1; Dishka links use its stable documentation. Upstream source cross-checks
use moving develop/master branches, so line anchors are navigation aids rather than pinned releases.
A stale cached raw Dishka source response was not used as evidence of current implementation details.

No packages were installed, no external-framework runtime tests were executed, and no Melder source
was changed in this research. Examples above explain documented mechanisms; they are not benchmark
or interoperability evidence. Same-object multi-owner disposal deduplication and arbitrary custody
transfer are deliberately not claimed as guaranteed across these systems.
