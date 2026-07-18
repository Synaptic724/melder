import inspect
import types
from functools import update_wrapper
from threading import RLock
from types import SimpleNamespace

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.ulid_factory import new_ulid
from typing import (
    Callable,
    Generic,
    ParamSpec,
    TypeVar,
    Iterable,
    Union,
    Optional,
    Collection,
    overload,
    Dict,
    Tuple,
    Awaitable,
    Any,
    List,
    TypeGuard,
    ClassVar,
)

P = ParamSpec("P")
R = TypeVar("R")
A = TypeVar("A")
B = TypeVar("B")


def _is_async_callable(
        task: Callable[..., object],
) -> TypeGuard[Callable[..., Awaitable[object]]]:
    """
    Return whether one callable is a coroutine function.

    Args:
        task:
            Candidate callable to classify.

    Returns:
        bool: True when `task` is an `async def` coroutine function.
    """
    return inspect.iscoroutinefunction(task)



class Package(Cleanable, Generic[P, R]):
    """
    A lightweight, thread-safe wrapper around a callable (sync or coroutine).

    Summary
    -------
    - Accepts **sync** callables and **coroutine functions** (async def).
    - **Rejects generator functions**.
    - Calling a Package returns:
        * the callable's return value for sync functions, or
        * a **coroutine object** for async functions (caller is responsible for awaiting
          or scheduling it; this class does not auto-await).
    - Thread-safe: argument binding and access to internal state are protected; invocation
      occurs outside the lock to avoid deadlocks.
    - Stable identity: each instance has a ULID `id`; equality and hashing are based on the
      wrapped callable and bound args/kwargs.
    - Utilities: exposes whether the wrapped target is async (`is_async` / `is_coroutine()`),
      and provides `get_coroutine()` to access the underlying coroutine function when applicable.

    Behavior Details
    ----------------
    - Initialization:
        * Validates the target is callable.
        * Rejects generator functions.
        * Records whether the target is a coroutine function (`inspect.iscoroutinefunction`).
        * Optionally binds initial args/kwargs (curried invocation).
    - Invocation (`__call__`):
        * Snapshots args/kwargs under lock, then invokes the underlying callable
          outside the lock.
        * If the target is async, returns the coroutine object **without** awaiting it.
    - Introspection:
        * `is_async` / `is_coroutine()` reflect whether the target is a coroutine function.
        * `get_coroutine()` returns the coroutine function if and only if the target is async;
          otherwise it raises.
    - Lifecycle:
        * `cleanup()` clears bound references and best-effort cleans any concurrent containers.

    Example:
    --------
    >>> def greet(name, punctuation="!"): return f"Hello, {name}{punctuation}"
    >>> p = Package(greet, "Alice").bind(punctuation=".")
    >>> p()
    'Hello, Alice.'

    >>> q = p.curry("Bob")  # Adds another positional arg (ignored here)
    >>> q()
    'Hello, Alice.'

    >>> composed = p | Package(str.upper)
    >>> composed()
    'HELLO, ALICE.'
    """

    __slots__ = Cleanable.__slots__ + ["_func", "_wrapped_func", "_async_func", "_args", "_kwargs", "_signature_cache", "_frozen", "_lock", "_is_async", "_id"]

    def __init__(self, func: Callable[..., R], *args: Any, **kwargs: Any):
        """
        Create a new Package wrapping the given function and initial arguments.

        Args:
            func: The target callable to wrap.
            *args: Positional arguments to pre-bind.
            **kwargs: Keyword arguments to pre-bind.

        Raises:
            TypeError: If func is not a callable or is a coroutine/generator function.
        """
        super().__init__()
        if isinstance(func, Package):
            raise TypeError("Cannot create a Package from an existing Package instance directly. "
                            "Use .curry() or .bind() on the existing instance if you want to extend it, "
                            "or Pack.many() for collections.")

        self._lock: RLock = RLock()
        self._id = new_ulid()
        normalized = self._normalize_task(func)  # Use helper for validation

        # Check if the normalized function is a coroutine and store the flag.
        self._is_async = inspect.iscoroutinefunction(normalized)
        self._async_func: Optional[Callable[..., Awaitable[object]]] = (
            normalized if _is_async_callable(normalized) else None
        )

        self._wrapped_func: Callable[..., R] = normalized
        self._func: Callable[..., R] = update_wrapper(lambda *a, **kw: normalized(*a, **kw), normalized)
        self._args: List[Any] = list(args) if args else []
        self._kwargs: Dict[str, Any] = dict(kwargs) if kwargs else {}
        self._signature_cache: SimpleNamespace | None = None
        self._frozen: bool = False

    def cleanup(self) -> None:
        """
        Clean owned state in two phases and make the package unusable.

        Contract:
            - Idempotent: repeated calls return immediately.
            - Marks `_cleaned` while the package lock is held before child
              cleanup begins.
            - Performs reference nulling after the lock is released so core
              teardown does not occur inside the locked section.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Phase 1 - components (while holding the lock)
            self._cleanup_components()
        # Phase 2 - core teardown (after releasing the lock)
        self._cleanup_core()



    def _cleanup_components(self) -> None:
        """
        Best-effort clean owned collections while the package lock is held.

        Contract:
            - Calls `cleanup()` only on owned collections that expose it.
            - Swallows cleanup errors deliberately so core teardown still runs.
            - Does not clear references; `_cleanup_core()` performs nulling.
        """
        if self._args is not None and hasattr(self._args, "cleanup"):
            try:
                self._args.cleanup()
            except Exception:
                pass

        if self._kwargs is not None and hasattr(self._kwargs, "cleanup"):
            try:
                self._kwargs.cleanup()
            except Exception:
                pass


    def _cleanup_core(self) -> None:
        """
        Clear remaining owned references after locked cleanup is complete.

        Contract:
            - Must run after `_cleanup_components()` and outside the lock
              context.
            - Nulls wrapped callable, bound arguments, and cached signature
              state.
            - Best-effort cleans a polymorphic lock if it exposes `cleanup()`,
              then always drops the lock reference.
        """
        # --- Nullify All Component References ---
        del self._func
        del self._wrapped_func
        del self._async_func
        del self._args
        del self._kwargs
        del self._signature_cache

        # --- Final Teardown of the Lock ---
        # The lock for a standard threading.RLock doesn't have a cleanup,
        # but we nullify the reference. This structure is ready for AgenticRLock.
        try:
            if hasattr(self._lock, 'cleanup'):
                self._lock.cleanup()
        except Exception:
            # Per request, pass silently on exceptions
            pass
        finally:
            del self._lock

    @property
    def id(self) -> str:
        """
        Returns a unique identifier for this Package instance.
        This is useful for tracking and debugging.

        Returns:
            A string representing the unique ID of the Package.
        """
        return self._id

    def unpack(self) -> Tuple[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]:
        """
        Deconstructs the Package into its core components.

        This method provides a thread-safe way to get a snapshot of the original
        callable, its pre-bound positional arguments, and its pre-bound keyword
        arguments.

        Returns:
            A tuple containing:
            - The original, unwrapped callable function.
            - A tuple of the pre-bound positional arguments.
            - A dictionary of the pre-bound keyword arguments.
        """
        with self._lock:
            # The original function is stored in the __wrapped__ attribute by functools.update_wrapper
            func = self._wrapped_func

            # Return copies to prevent modification of the Package's internal state
            args = tuple(self._args)
            kwargs = dict(self._kwargs)

            return func, args, kwargs

    def unpack_and_cleanup(self) -> Tuple[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]:
        """
        Destructively unpacks the Package and cleans it up in one atomic operation.

        This method retrieves the original callable and its arguments, and then
        immediately disposes of the Package instance, making it unusable for any
        future operations. This is useful for "fire-and-forget" or "use-once"
        scenarios.

        Returns:
            A tuple containing:
            - The original, unwrapped callable function.
            - A tuple of the pre-bound positional arguments.
            - A dictionary of the pre-bound keyword arguments.

        Raises:
            RuntimeError: If the Package has already been cleaned.
        """
        if self._cleaned:
            raise RuntimeError("Cannot unpack and clean a cleaned Package.")
        with self._lock:
            # Double-check inside the lock to prevent race conditions
            if self._cleaned:
                raise RuntimeError("Cannot unpack and clean a cleaned Package.")

            # 1. Get the components to return before cleaning
            func = self._wrapped_func
            args = tuple(self._args)
            kwargs = dict(self._kwargs)

            # 2. Perform cleanup of internal state
            self.cleanup()

        # 5. Return the extracted components
        return func, args, kwargs

    def describe(self) -> str:
        """
        Provides a human-readable description of the wrapped callable and its signature.

        Returns:
            A string describing the function's name and parameters.
        """
        with self._lock:
            if self._cleaned:
                return "Package(cleaned)"

            func = self._wrapped_func
            func_name = getattr(func, '__name__', 'unnamed')
            qual_name = getattr(func, '__qualname__', func_name)

            try:
                sig = inspect.signature(func)
                params_str = str(sig)
            except (ValueError, TypeError):
                params_str = "(uninspectable)"

            if func_name == '<lambda>':
                return f"A lambda function with signature: {params_str}"
            else:
                return f"A callable '{qual_name}' with signature: {params_str}"

    def is_coroutine(self) -> bool:
        """
        Checks if the wrapped callable is a coroutine function.

        Returns:
            bool: True if the wrapped item is a coroutine function, False otherwise.
        """
        return self._is_async

    def __getattribute__(self, name: str) -> object:
        """
        Override doc lookup to always proxy the wrapped callable's docstring.

        Args:
            name:
                Requested attribute name.

        Returns:
            object: Resolved attribute value.
        """
        if name == "__doc__":
            try:
                func = object.__getattribute__(self, "_func")
                doc = getattr(func, "__doc__", "")
                return "" if doc is None else doc
            except Exception:
                return ""
        return super().__getattribute__(name)

    def get_coroutine(self) -> Callable[..., Awaitable[object]]:
        """
        Returns the underlying coroutine function if the Package is async.

        Returns:
            The awaitable coroutine function.

        Raises:
            TypeError: If the wrapped function is not a coroutine.
        """
        async_func = self._async_func
        if async_func is None:
            raise TypeError("Package does not contain a coroutine function.")
        return async_func

    @property
    def is_async(self) -> bool:
        """
        Check if the underlying function is async (coroutine). This is for info only.

        Returns:
            bool: True if the original function was a coroutine function.
        """
        return inspect.iscoroutinefunction(self._wrapped_func)

    def __or__(self: "Package[P, A]", other: "Package[[A], B]") -> "Package[P, B]":
        """
        Compose two packages into a left-to-right pipeline.

        Contract:
            - `self` receives the external call arguments.
            - The result of `self` becomes the sole positional input to
              `other`.
            - The composed package calls `other._func(...)` directly, so
              `other`'s stored bound arguments are intentionally bypassed.
        """
        if not isinstance(other, Package):
            raise TypeError("| expects another Package")

        # This correctly calls the underlying function of `other` to bypass
        # its stored arguments, creating a true pipeline.
        def composed_callable(*a: P.args, **kw: P.kwargs) -> B:
            """
            Compose two packages into a left-to-right pipeline.
            """
            result_of_first: A = self(*a, **kw)
            return other._func(result_of_first)

        return Package(composed_callable)

    @staticmethod
    def bundle(
            item: Optional[
                Union[Callable[P, R], "Package[P, R]", Iterable[Union[Callable[P, R], "Package[P, R]"]]]
            ]
    ) -> Union["Package[P, R]", List["Package[P, R]"]]:
        """
        Normalize one callable/package or an iterable of them into package objects.

        Args:
            item: The input to normalize. Can be one callable, one `Package`,
                or an iterable containing a mix of both.

        Returns:
            Union["Package[P, R]", List["Package[P, R]"]]: Existing package for
            single-package input, new package for single-callable input, or a
            list of package objects for iterable input.

        Raises:
            TypeError: If `item` is `None` or contains invalid callable input.
        """
        if item is None:
            raise TypeError("Cannot Packify None input.")

        # If it is already one package instance, return it directly.
        if isinstance(item, Package):
            return item

        # If it is an iterable, normalize each element into package form.
        if isinstance(item, Iterable) and not isinstance(item, str):
            return Pack._pack_many(item)

        # If it is one callable, wrap it in a new package instance.
        if callable(item):
            # The package constructor performs the callable validation itself.
            return Pack(item)

        # If none of the above matched, the input type is invalid.
        raise TypeError(
            f"Cannot Packify input of type {type(item).__name__}. Expected callable, Package, or iterable thereof.")
    # Deterministic dual-lock ordering helper.
    @staticmethod
    def _acquire_two(a: "Package", b: "Package") -> Tuple["Package", "Package"]:
        """
        Deterministic ordering helper for dual-lock acquisition.
        Always returns the two Package instances in ascending id() order, so
        every thread grabs multiple Package locks in the same sequence.
        """
        return (a, b) if id(a) <= id(b) else (b, a)


    def __eq__(self, other: object) -> bool:
        """
        Return whether two packages wrap the same callable and bound arguments.

        Contract:
            - Compares the unwrapped callable by identity.
            - Compares bound positional and keyword arguments by value.
            - Uses deterministic dual-lock ordering to reduce deadlock risk.
        """
        if not isinstance(other, Package):
            return False

        first, second = Package._acquire_two(self, other)
        with first._lock, second._lock:
            return (
                    self._wrapped_func is other._wrapped_func and
                    tuple(self._args) == tuple(other._args) and
                    dict(self._kwargs) == dict(other._kwargs)
            )


    def __hash__(self) -> int:
        """
        Return a stable hash derived from the wrapped callable and bound arguments.

        Contract:
            - Snapshots the current callable and bound args/kwargs under lock.
            - Hashes the callable by identity and the bound arguments by value.
        """
        # Freeze-on-hash: equality/hash derive from the mutable bindings, so the
        # package is frozen the first time it is hashed to keep its hash and
        # set/dict membership stable for its lifetime (binding mutators then raise).
        with self._lock:
            self._frozen = True
            f = self._wrapped_func
            a = tuple(self._args)
            k = frozenset(self._kwargs.items())
        return hash((id(f), a, k))

    def __call__(self, *extra_args: P.args, **extra_kwargs: P.kwargs) -> R:
        """
        Calls the wrapped function with all stored and extra arguments.
        Gathers the arguments under the lock, then releases the lock
        before invoking the underlying function to avoid cross-thread
        contention when nested calls occur.
        """
        # Snapshot bound args/kwargs under the lock, then invoke lock-free.
        with self._lock:
            all_args = tuple(self._args) + extra_args
            all_kwargs = {**dict(self._kwargs), **extra_kwargs}
        # Invoke outside the lock to avoid deadlocks during nested calls.
        return self._func(*all_args, **all_kwargs)

    def execute_sync(self, *extra_args: P.args, **extra_kwargs: P.kwargs) -> R:
        """
        Calls the wrapped function synchronously if it is sync.

        This method is a convenience for invoking synchronous package objects.
        It gathers the arguments under the lock, then releases the lock
        before invoking the underlying function to avoid cross-thread
        contention when nested calls occur.

        Returns:
            The return value of the wrapped function.

        Raises:
            TypeError: If the wrapped callable is asynchronous.
        """
        # Invoke outside the lock to avoid deadlocks during nested calls.
        if self._is_async:
            raise TypeError("Cannot execute asynchronously wrapped function as sync.")
        # Snapshot bound args/kwargs under the lock, then invoke lock-free.
        with self._lock:
            all_args = tuple(self._args) + extra_args
            all_kwargs = {**dict(self._kwargs), **extra_kwargs}

        return self._func(*all_args, **all_kwargs)

    async def execute_async(self, *extra_args: P.args, **extra_kwargs: P.kwargs) -> Any:
        """
        Calls the wrapped function as a coroutine if it is async.

        This method is a convenience for invoking asynchronous package objects.
        It gathers the arguments under the lock, then releases the lock
        before invoking the underlying function to avoid cross-thread
        contention when nested calls occur.

        Returns:
            The coroutine object returned by the wrapped function.

        Raises:
            TypeError: If the wrapped callable is synchronous.
        """
        # Invoke outside the lock to avoid deadlocks during nested calls.
        async_func = self._async_func
        if async_func is None:
            raise TypeError("Cannot execute synchronously wrapped function as async.")
        # Snapshot bound args/kwargs under the lock, then invoke lock-free.
        with self._lock:
            all_args = tuple(self._args) + extra_args
            all_kwargs = {**dict(self._kwargs), **extra_kwargs}

        return await async_func(*all_args, **all_kwargs)


    @staticmethod
    def verify(item_to_check: Any) -> bool:
        """
        Validate a package or iterable of packages.

        This helper provides one boundary check for APIs that accept either one
        `Package` or a collection of `Package` objects.

        Args:
            item_to_check (Any):
                The item to validate. Can be one `Package` instance or an
                iterable containing package objects.

        Returns:
            bool:
                Returns True if the validation succeeds.

        Raises:
            TypeError:
                If the `item_to_check` (or any element within it) is not an
                instance of `Package`.
        """
        # Strings are excluded so textual input is not treated as a task list.
        if isinstance(item_to_check, Collection) and not isinstance(item_to_check, str):
            for task in item_to_check:
                # Recursively validate each collection member.
                Pack.verify(task)
            return True

        # Non-collection input must be one concrete package instance.
        if isinstance(item_to_check, Package):
            return True

        # Anything else violates the package-or-iterable contract.
        raise TypeError(
            f"Expected a Pack instance or an iterable of Packs, but got "
            f"{type(item_to_check).__name__}."
        )

    @staticmethod
    def merge_many(packs: Iterable["Package[..., Any]"]) -> "Package[..., Any]":
        """
        Pipe a sequence of Packages left-to-right into a single composite Package.

        Example:
            combo = Package.merge_many([p1, p2, p3])
            result = combo(x)   # approximately p3(p2(p1(x)))
        """
        packs_iter = list(packs)
        if not packs_iter:
            raise ValueError("merge_many() requires at least one Package")
        for i, p in enumerate(packs_iter):
            if not isinstance(p, Package):
                raise TypeError(f"Item at index {i} is not a Package: {p!r}")

        def _composed(*a: Any, **kw: Any) -> Any:
            val = packs_iter[0](*a, **kw)
            for p_item in packs_iter[1:]:
                val = p_item(val)
            return val

        return Package(_composed)

    @staticmethod
    def _normalize_task(task: Union[Callable[P, R], "Package[P, R]"]) -> Callable[P, R]:
        """
        Validate a callable or Package. If it's a Package, return its inner function.
        If it's a callable, validate it. No wrapping is done here to avoid recursion.

        Args:
            task: A raw callable or Package.

        Returns:
            A validated callable (either unwrapped or raw).

        Raises:
            TypeError: If task is invalid.
        """
        if task is None:
            raise TypeError("Cannot normalize None as a task.")
        if isinstance(task, Package):
            return task._wrapped_func
        if not callable(task):
            raise TypeError(f"Expected callable, got {type(task).__name__}")
        if inspect.isgeneratorfunction(task):
            raise TypeError(f"Generator functions are not supported: {getattr(task, '__name__', repr(task))}")
        return task

    @staticmethod
    def _normalize_many(
            tasks: Union[Callable[P, R], "Package[P, R]", Iterable[Union[Callable[P, R], "Package[P, R]"]]]
    ) -> List["Package[P, R]"]:
        """
        Normalize one callable/package or an iterable of them into package objects.

        This helper ensures downstream callers receive concrete `Package`
        instances without double-wrapping existing package input.

        Args:
            tasks: A single task or a collection of tasks.

        Returns:
            List["Package[P, R]"]: Validated package objects.

        Raises:
            TypeError: If any task is invalid, None, or an async/coroutine/generator.
        """
        if tasks is None:
            raise TypeError("Tasks input cannot be None.")

        # Single task input still normalizes to a one-element package list.
        # An existing Package is returned as-is so its bound args/kwargs survive;
        # only a raw callable is wrapped. Routing a Package through _normalize_task
        # (which unwraps to the inner callable) would silently drop its bindings.
        if isinstance(tasks, Package):
            return [tasks]
        if callable(tasks):
            return [Package(Package._normalize_task(tasks))]

        if not isinstance(tasks, Iterable):
            raise TypeError(f"Expected a callable or iterable of callables, got {type(tasks).__name__}")

        result: List["Package[P, R]"] = []
        for i, task in enumerate(tasks):
            try:
                if task is None:
                    raise TypeError("Task is None.")
                if not callable(task):
                    raise TypeError(f"Expected callable, got {type(task).__name__}")
                if inspect.isgeneratorfunction(task):
                    raise TypeError(f"Generator functions are not supported: {getattr(task, '__name__', repr(task))}")
                result.append(task if isinstance(task, Package) else Package(task))
            except Exception as e:
                raise TypeError(f"Invalid task at index {i}: {e}") from e

        return result
    # Internal packing helpers.
    # Single-item pack helper.
    @staticmethod
    def _pack(task: Union[Callable[P, R], "Package[P, R]"]) -> "Package[P, R]":
        """
        Return an existing package or wrap one callable in a new package.
        """
        if isinstance(task, Package):
            return task
        return Pack(task)
    # Many-item pack helper.
    @staticmethod
    def _pack_many(
            tasks: Union[
                Callable[P, R],
                "Package[P, R]",
                Iterable[Union[Callable[P, R], "Package[P, R]"]]
            ]
    ) -> List["Package[P, R]"]:
        """
        Normalize batch input into a list of package objects.

        Args:
            tasks: A single task or iterable of tasks.

        Returns:
            List["Package[P, R]"]: Package objects for each accepted task.

        Raises:
            TypeError: On invalid input.
        """
        if tasks is None:
            raise TypeError("Tasks input cannot be None.")

        if isinstance(tasks, Package) or callable(tasks):
            return [Package._pack(tasks)]

        if not isinstance(tasks, Iterable) or isinstance(tasks, str):
            raise TypeError(f"Expected a callable or iterable of callables, got {type(tasks).__name__}")

        result: List["Package[P, R]"] = []
        for i, task in enumerate(tasks):
            try:
                result.append(Package._pack(task))
            except Exception as e:
                raise TypeError(f"Invalid task at index {i}: {e}") from e

        return result

    def bind_args(self, *new_args: Any) -> "Package[P, R]":
        """
        Mutably replace the positional arguments of this Package.

        Args:
            *new_args: New positional arguments to replace the current ones.

        Returns:
            self

        Raises:
            RuntimeError: If the package is frozen.
        """
        with self._lock:
            if self._frozen:
                raise RuntimeError("Package is frozen.")
            self._args.clear()
            self._args.extend(new_args)
            self._signature_cache = None
            return self

    def bind(self, **new_kwargs: Any) -> "Package[P, R]":
        """
        Mutably add or update keyword arguments.

        Args:
            **new_kwargs: Keyword arguments to merge into the package.

        Returns:
            self

        Raises:
            RuntimeError: If the package is frozen.
        """
        with self._lock:
            if new_kwargs:
                if self._frozen:
                    raise RuntimeError("Package is frozen.")
                self._kwargs.update(new_kwargs)
                self._signature_cache = None
            return self

    def override(self, *args: Any, **kwargs: Any) -> "Package[P, R]":
        """
        Mutably override both args and kwargs.
        WARNING: This modifies the original Package!

        Args:
            *args: Positional arguments to set.
            **kwargs: Keyword arguments to merge.

        Returns:
            self

        Raises:
            RuntimeError: If the package is frozen.
        """
        with self._lock:
            if self._frozen:
                raise RuntimeError("Package is frozen.")
            self._args.clear()
            self._args.extend(args)
            self._kwargs.clear()
            self._kwargs.update(kwargs)
            self._signature_cache = None
            return self

    def curry(self, *args: Any, **kwargs: Any) -> "Package[P, R]":
        """
        Create a new Package with additional positional and keyword arguments.

        Args:
            *args: Extra args to append.
            **kwargs: Extra kwargs to merge.

        Returns:
            A new Package with combined arguments.
        """
        with self._lock:
            func = self._wrapped_func
            # Merge new bindings on top of the package's stored arguments.
            combined_args = tuple(self._args) + args
            combined_kwargs = {**dict(self._kwargs), **kwargs}
            return Package(func, *combined_args, **combined_kwargs)

    def freeze(self) -> None:
        """
        Prevent future argument mutation on this package instance.
        """
        with self._lock:
            self._frozen = True

    @property
    def args(self) -> Tuple[Any, ...]:
        """Return the stored positional arguments."""
        with self._lock:
            return tuple(self._args)

    @property
    def kwargs(self) -> Dict:
        """Return a copy of the stored keyword arguments.

        A copy is returned (mirroring `args`) so external mutation cannot
        bypass `bind()`/`freeze()` and leave the cached signature stale.
        """
        with self._lock:
            return dict(self._kwargs)

    @property
    def signature(self) ->  Any:
        """
        Return a pseudo-signature object representing bound args.

        Returns:
            SimpleNamespace: Namespace whose `arguments` mapping contains
            positional placeholders (`arg0`, `arg1`, ...) plus keyword entries.
        """
        with self._lock:
            if self._signature_cache is None:
                sig = inspect.signature(self._wrapped_func)
                arg_map = {}
                for i, value in enumerate(self._args):
                    arg_map[f"arg{i}"] = value
                arg_map.update(self._kwargs)
                self._signature_cache = types.SimpleNamespace(arguments=arg_map)
            return self._signature_cache


    def __add__(self, other: "Package") -> "Package":
        """
        Return a package that adds the results of two package invocations.

        Example:
            (Pack(f) + Pack(g))(...) == f(...) + g(...)

        Returns:
            A new Package that adds both results.
        """
        if not isinstance(other, Package):
            raise TypeError("+ expects another Package")
        return Package(lambda *a, **kw: self(*a, **kw) + other(*a, **kw))

    def __getattr__(self, item: str) -> Callable[..., R]:
        """
        Fallback missing-attribute access to the wrapped callable object.

        This is not a full per-attribute proxy. The current implementation
        returns the wrapped callable reference itself when the package does not
        define `item`.
        """
        # object.__getattribute__ avoids re-entering __getattr__ (no recursion).
        # After cleanup the owned slots (_func, _lock, ...) are deleted, so any
        # access lands here; surface the canonical cleaned-object error.
        try:
            cleaned = object.__getattribute__(self, "_cleaned")
        except AttributeError:
            cleaned = False
        if cleaned:
            raise RuntimeError(f"{type(self).__name__} has already been cleaned. ")
        try:
            return object.__getattribute__(self, "_func")
        except AttributeError:
            raise AttributeError(item) from None

    def __dir__(self) -> List[str]:
        """
        Merge package and wrapped-callable attributes for introspection.
        """
        return sorted(
            set(super().__dir__())
            | set(dir(self._func))
            | set(dir(self._wrapped_func))
        )

    def __repr__(self) -> str:
        """Return a debug-oriented representation of the wrapped callable and bindings."""
        with self._lock:
            func = self._func
            args = self._args
            kwargs = self._kwargs

            if func is None:
                func_name = "None"
            else:
                try:
                    func_name = func.__name__
                except Exception:
                    func_name = type(func).__name__

            args_repr = tuple(args) if args is not None else ()
            kwargs_repr = dict(kwargs) if kwargs is not None else {}

            return f"Package({func_name}, args={args_repr}, kwargs={kwargs_repr})"


# Short alias
Pack = Package

