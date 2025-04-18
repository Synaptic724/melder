# Melder Class Outline

## 📦 melder/melder.py
~~~
class Melder:
    def __init__(self, enable_debug_scope_ids: bool = False):
        ...

    def bind(self, service: Type, *, interface: Optional[Type] = None, lifetime: str = "singleton"):
        ...

    def bind_named(self, name: str, interface: Type, implementation: Type, lifetime: str = "singleton"):
        ...

    def create_state(self) -> "ScopeManager":
        ...

    def meld(self, service_type: Type, *, overrides: Optional[Dict[Type, Any]] = None) -> Any:
        ...
~~~

---

## 📦 melder/container/service_container.py
~~~
class ServiceContainer:
    def __init__(self):
        ...

    def register(self, descriptor: "ServiceDescriptor"):
        ...

    def resolve(self, service_type: Type, overrides: Optional[Dict[Type, Any]] = None) -> Any:
        ...
~~~

---

## 📦 melder/builder/service_builder.py
~~~
class ServiceBuilder:
    def __init__(self, container: "ServiceContainer"):
        ...

    def build_instance(self, descriptor: "ServiceDescriptor", overrides: Optional[Dict[Type, Any]] = None) -> Any:
        ...
~~~

---

## 📦 melder/registry/service_descriptor/service_descriptor.py
~~~
class ServiceDescriptor:
    def __init__(self, implementation: Type, interface: Optional[Type], lifetime: str, name: Optional[str] = None):
        ...
~~~

---

## 📦 melder/registry/service_registry.py
~~~
class ServiceRegistry:
    def __init__(self):
        ...

    def register(self, descriptor: "ServiceDescriptor"):
        ...

    def find(self, service_type: Type) -> "ServiceDescriptor":
        ...

    def find_named(self, service_type: Type, name: str) -> "ServiceDescriptor":
        ...
~~~

---

## 📦 melder/registry/service_lifetime/service_lifetime.py
~~~
class ServiceLifetime:
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"
~~~

---

## 📦 melder/scope/scope_manager.py
~~~
class ScopeManager:
    def __init__(self, container: "ServiceContainer", enable_debug_scope_ids: bool = False):
        ...

    def meld(self, service_type: Type, *, overrides: Optional[Dict[Type, Any]] = None) -> Any:
        ...

    def seal(self):
        ...
~~~

---

## 📦 melder/disposal (future)
~~~
class DisposalManager:
    def __init__(self):
        ...

    def register_disposable(self, instance: Any):
        ...

    def dispose_all(self):
        ...
~~~

---

## 📦 melder/utilities/object_manager.py
~~~
class ObjectManager:
    @staticmethod
    def monkeypatch_scope_id(instance: Any, scope_uuid: str):
        ...
~~~

---

## 📦 melder/validation/validation_system.py
~~~
class ValidationSystem:
    @staticmethod
    def validate_constructor_type_hints(cls: Type):
        ...

    @staticmethod
    def validate_no_circular_dependencies(service_graph: "DirectedAcyclicWorkGraph"):
        ...
~~~

---

## 📦 melder/utilities/directed_acyclic_work_graph.py
~~~
class DirectedAcyclicWorkGraph:
    def __init__(self):
        ...

    def add_dependency(self, service: Type, dependency: Type):
        ...

    def detect_cycles(self) -> bool:
        ...
~~~

---

## 📦 melder/utilities/interfaces.py
~~~
class InjectNamed:
    def __init__(self, name: str):
        self.name = name
~~~

---

# ScopeID Object (Monkeypatched Debugging Metadata)
~~~
class ScopeID:
    def __init__(self, scope_uuid: str):
        self.scope_uuid = scope_uuid
        self.scope_created_at = datetime.datetime.now()
        self.object_uuid = uuid.uuid4()
        self.object_created_at = datetime.datetime.now()

    @property
    def uuid(self) -> str:
        return str(self.object_uuid)

    def get_created_at(self) -> datetime.datetime:
        return self.object_created_at
~~~
