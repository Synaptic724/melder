import inspect

class OverloadDispatcher:
    def __init__(self):
        self._registry = {}

    def register(self, func):
        sig = inspect.signature(func)
        param_types = tuple(p.annotation for p in sig.parameters.values())
        self._registry[param_types] = func

    def __call__(self, *args, **kwargs):
        call_types = tuple(type(arg) for arg in args)
        for param_types, func in self._registry.items():
            if len(call_types) != len(param_types):
                continue
            if all(pt == at or pt == inspect._empty or isinstance(at(), pt) for pt, at in zip(param_types, call_types)):
                return func(*args, **kwargs)
        raise TypeError(f"No matching overload for args: {call_types}")