# 🗺️ Melder Roadmap

## ✅ Current: v0.1.x (Early Foundations)

- **Minimal Service Registration System:**
  - `register(interface, implementation)`
  - `resolve(interface)` returns instance

- **Basic Lifetimes:**
  - `singleton` services
  - `transient` services

- **Simple Service Container:**
  - Thread-safe registrations
  - No scopes yet
  - Basic disposal support (context managers)

- **Internal Disposable Management:**
  - Services supporting `__enter__`/`__exit__` are auto-managed

---

## 🚧 Upcoming Milestones

### 🛠 v0.2.x: Core Improvements and Resilience

- Add `factory` registrations:
  - Register callables to produce instances dynamically
- Add `instance` registrations:
  - Pre-created object binding
- Basic error handling:
  - Clear exceptions for missing registrations
  - Protect against double registration

### 🧠 v0.3.x: Scoping Support

- Add `Scope` object:
  - `scope.enter()` / `scope.exit()`
  - Services marked as `scoped` are unique per scope
- `ServiceScopeProvider`:
  - Manage and create child scopes
  - Isolate scoped service instances
- Default to `RootScope` if no explicit scope active

### ⚡ v0.4.x: Advanced Lifetimes and Cleanup

- Implement `scoped`, `singleton`, `transient` lifetimes fully
- Scoped services dispose correctly when scope exits
- Add background disposal tracking:
  - Timed disposal cleanup of orphaned services

### 📦 v0.5.x: Quality of Life Enhancements

- Auto-registration decorator:

```bash>
@melder.register(ServiceInterface)
class MyService:
```

- Lazy resolution:
  - Services can optionally be lazy-instantiated on first access
- Small helper utilities:
  - `is_registered(interface)`
  - `try_resolve(interface, default=None)`

### 🕸️ v0.6.x: Dependency Graph Building

- Dependency graph visualization support:
  - See what services depend on others
  - Optional tree-print to console
- Early cycle detection:
  - Protect against circular dependency errors

### 🔥 v0.7.x: Resolution Features

- Support constructor injection:
  - Automatically resolve dependencies by `__init__` signature
- Allow multiple implementations:
  - Resolve all services for an interface
- Support named registrations:
  - Differentiate between multiple services registered under same interface

### 🌐 v0.8.x: Async and Threaded Contexts

- `async` service resolution:
  - `await container.resolve_async(interface)`
- Support `async` service factories
- Scoped context-aware resolution:
  - `with container.create_scope() as scope: ...`

### 📊 v0.9.x: Diagnostics and Instrumentation

- Track registration stats:
  - Service count, resolution count, error rates
- Resolution profiling:
  - Track average service instantiation time
- Optional debug tracing mode:
  - Log service creation, disposal events

---

## 🚀 v1.0.0: Full Production-Ready Release

- Complete API documentation
- Example projects:
  - Console app
  - Web service skeleton
- Add PyPI classifiers for framework compatibility
- Stability + performance benchmarks
- Full GitHub Actions CI/CD for automated release
- Finalized Melder brand and website/docs (optional)

---

## 📅 Release Planning Sketch

| Version | Focus | Notes |
|:---|:---|:---|
| v0.1 | Basic registration and resolution | Singleton and transient support |
| v0.2 | Factories and instance binding | Dynamic creation |
| v0.3 | Scoping support | Scoped lifetimes |
| v0.4 | Advanced cleanup and disposal | Stability for scopes |
| v0.5 | Decorators and helpers | QoL boosts |
| v0.6 | Dependency graphs | Visualization and cycle detection |
| v0.7 | Constructor injection | Autowiring-like behavior |
| v0.8 | Async service resolution | Modern Python compatibility |
| v0.9 | Diagnostics and profiling | Observability for heavy usage |
| v1.0 | Full release polish | Docs, CI, examples |

---

## 📣 Closing Thought

> **Melder is not just a dependency container.  
> It's the bridge that cleanly melds services, systems, and scalability for the next generation of Python applications.**
