import inspect
from typing import Callable, Any, Tuple, Type, Dict, Optional
from melder.utilities.interfaces import ISeal
from melder.utilities.concurrent_dictionary import ConcurrentDict

class OverloadDispatcher(ISeal):
    """
    A simple overload dispatcher that allows for function overloading based on argument types.
    """
    __slots__ = ISeal.__slots__ + ['_registry']
    def __init__(self):
        super().__init__()
        self._registry = ConcurrentDict()

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

    def seal(self):
        """
        Seal the dispatcher to prevent further modifications.
        """
        if self._sealed:
            return
        self._sealed = True
        self._registry.clear()