# Melder Class Responsibilities

## 📦 melder/melder.py
**Melder**
- Public entrypoint for binding, creating states, and resolving services.

## 📦 melder/container/service_container.py
**ServiceContainer**
- Internal storage and retrieval system for registered services and their lifetimes.

## 📦 melder/builder/service_builder.py
**ServiceBuilder**
- Creates actual service instances, injecting dependencies and applying hooks.

## 📦 melder/registry/service_descriptor/service_descriptor.py
**ServiceDescriptor**
- Holds metadata about a service: what it implements, its lifetime, and optional name.

## 📦 melder/registry/service_registry.py
**ServiceRegistry**
- Tracks all registered services and resolves descriptors when requested.

## 📦 melder/registry/service_lifetime/service_lifetime.py
**ServiceLifetime**
- Central constants for known lifetimes (singleton, scoped, transient).

## 📦 melder/scope/scope_manager.py
**ScopeManager**
- Manages a created state (scope), resolves services within the scope, and seals them when done.

## 📦 melder/disposal (planned)
**DisposalManager**
- Manages cleanup of disposable services inside a state when the state is sealed.

## 📦 melder/utilities/object_manager.py
**ObjectManager**
- Handles monkeypatching metadata like ScopeID onto instances during debug mode.

## 📦 melder/validation/validation_system.py
**ValidationSystem**
- Validates service constructors, checks for circular dependencies, and ensures safe service graphs.

## 📦 melder/utilities/directed_acyclic_work_graph.py
**DirectedAcyclicWorkGraph**
- Builds and verifies service dependency graphs to detect cycles at registration time.

## 📦 melder/utilities/interfaces.py
**InjectNamed**
- Special marker used in constructor arguments to request a specific named binding.

---

## 📦 ScopeID Object (monkeypatched debug metadata)
**ScopeID**
- Attaches UUIDs and timestamps to services and their states for lifecycle tracking during debugging.

---

# 🧠 Overall Responsibility Layers

| Layer | Responsibility |
|:---|:---|
| Melder / ScopeManager | Orchestration and public API |
| ServiceContainer / Registry | Service registration and lookup |
| Builder | Instance construction |
| Validation / DAG | Safety checks and correctness |
| Utilities | Debugging, metadata, and helpers |
| Disposal (Planned) | Resource cleanup and lifecycle end management |

