import inspect
import types
from functools import update_wrapper
from threading import RLock
from types import SimpleNamespace
import ulid
from melder.utilities.general_base.cleanable import Cleanable
from typing import Callable, Generic, ParamSpec, TypeVar, Iterable, Union, Optional, Collection, overload, Dict, Tuple, \
    Any, List

P = ParamSpec("P")
R = TypeVar("R")
A = TypeVar("A")
B = TypeVar("B")

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

    __slots__ = Cleanable.__slots__ + ["_func", "_args", "_kwargs", "_signature_cache", "_frozen", "_lock", "_is_async", "_id"]

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
        self._id = str(ulid.ULID())
        normalized = self._normalize_task(func)  # Use helper for validation

        # Check if the normalized function is a coroutine and store the flag.
        self._is_async = inspect.iscoroutinefunction(normalized)

        self._func: Callable[..., R] = update_wrapper(lambda *a, **kw: normalized(*a, **kw), normalized)
        self._args: List = args if args else []
        self._kwargs: Dict = kwargs if kwargs else {}
        self._signature_cache: SimpleNamespace | None = None
        self._frozen: bool = False

    def cleanup(self) -> None:
        """
        Disposes of the Package by orchestrating a resilient and idempotent cleanup.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Phase 1 — components (while holding the lock)
            self._cleanup_components()

        # Phase 2 — core teardown (after releasing the lock)
        self._cleanup_core()



    def _cleanup_components(self) -> None:
        """
        Safely cleans up all internal concurrent collections.
        Runs under the main lock.
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
        Performs the final teardown of remaining references and the lock.
        This must be called outside the main lock's 'with' block.
        """
        # --- Nullify All Component References ---
        self._func = None
        self._args = None
        self._kwargs = None
        self._signature_cache = None

        # --- Final Teardown of the Lock ---
        # The lock for a standard threading.RLock doesn't have a cleanup,
        # but we nullify the reference. This structure is ready for AgenticRLock.
        lock = self._lock
        if lock is not None:
            try:
                if hasattr(lock, 'cleanup'):
                    lock.cleanup()
            except Exception:
                # Per request, pass silently on exceptions
                pass
            finally:
                self._lock = None

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
            func = self._func.__wrapped__

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
            func = self._func.__wrapped__
            args = tuple(self._args)
            kwargs = dict(self._kwargs)

            # 2. Perform cleanup of internal state
            self._cleaned = True
            self._func = None
            self._args.clear()
            self._args = None
            self._kwargs.clear()
            self._kwargs = None
            self._signature_cache = None
            self._lock = None

        # 5. Return the extracted components
        return func, args, kwargs

    def describe(self) -> str:
        """
        Provides a human-readable description of the wrapped callable and its signature.

        Returns:
            A string describing the function's name and parameters.
        """
        with self._lock:
            if self._cleaned or not self._func:
                return "Package(cleaned)"

            func = self._func.__wrapped__
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

    def get_coroutine(self) -> Callable[..., Any]:
        """
        Returns the underlying coroutine function if the Package is async.

        Returns:
            The awaitable coroutine function.

        Raises:
            TypeError: If the wrapped function is not a coroutine.
        """
        if not self._is_async:
            raise TypeError("Package does not contain a coroutine function.")
        return self._func.__wrapped__

    @property
    def __doc__(self):
        """Returns the docstring of the wrapped function."""
        return getattr(self._func, '__doc__')

    @property
    def is_async(self) -> bool:
        """
        Check if the underlying function is async (coroutine). This is for info only.

        Returns:
            True if the original function was a coroutine function.
        """
        target = getattr(self._func, '__wrapped__', self._func)
        return inspect.iscoroutinefunction(target)

    def __or__(self: "Package[P, A]", other: "Package[[A], B]") -> "Package[P, B]":
        """
        Pipe operator: output of this Package becomes input to the next.
        """
        if not isinstance(other, Package):
            raise TypeError("| expects another Package")

        # This correctly calls the underlying function of `other` to bypass
        # its stored arguments, creating a true pipeline.
        def composed_callable(*a, **kw):
            result_of_first = self(*a, **kw)
            return other._func(result_of_first)

        return Package(composed_callable)

    @staticmethod
    def bundle(
            item: Optional[
                Union[Callable[P, R], "Package[P, R]", Iterable[Union[Callable[P, R], "Package[P, R]"]]]
            ]
    ) -> Union["Package[P, R]", List["Package[P, R]"]]:
        """
        Converts the input into a single Pack instance or a ConcurrentList of Pack instances.
        Handles None, single callables, single Pack instances, and iterables of mixed types.

        Args:
            item: The input to "packify". Can be None, a single callable, a single Pack instance,
                  or an iterable containing callables and/or Pack instances.

        Returns:
            A single Package instance if the input was a single callable or Pack.
            A ConcurrentList of Package instances if the input was an iterable.

        Raises:
            TypeError: If the input is None or contains invalid callable types (e.g., async/generator).
        """
        if item is None:
            raise TypeError("Cannot Packify None input.")

        # If it's already a single Pack instance, return it directly
        if isinstance(item, Package):
            return item

        # If it's an iterable (list, tuple, etc.), use Pack.many to process it
        # Note: `Pack.many` already handles if elements within the iterable are already Packs
        if isinstance(item, Iterable) and not isinstance(item, str):
            return Pack._pack_many(item)

        # If it's a single callable (and not already a Package), wrap it in a new Pack
        if callable(item):
            # The Pack constructor itself will validate the callable (sync/async/generator checks)
            return Pack(item)

        # If none of the above, it's an invalid type
        raise TypeError(
            f"Cannot Packify input of type {type(item).__name__}. Expected callable, Package, or iterable thereof.")

    # ───────────────────────── helper for deterministic dual lock ────────────
    @staticmethod
    def _acquire_two(a: "Package", b: "Package"):
        """
        Deterministic ordering helper for dual-lock acquisition.
        Always returns the two Package instances in ascending id() order, so
        every thread grabs multiple Package locks in the same sequence.
        """
        return (a, b) if id(a) <= id(b) else (b, a)


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Package):
            return False

        first, second = Package._acquire_two(self, other)
        with first._lock, second._lock:
            return (
                    self._func.__wrapped__ is other._func.__wrapped__ and
                    tuple(self._args) == tuple(other._args) and
                    dict(self._kwargs) == dict(other._kwargs)
            )


    def __hash__(self) -> int:
        # copy under lock, then compute hash lock-free
        with self._lock:
            f = self._func.__wrapped__
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
        # ── gather args/kwargs atomically ────────────────────────────────
        with self._lock:
            all_args = tuple(self._args) + extra_args
            all_kwargs = {**dict(self._kwargs), **extra_kwargs}

        # ── invoke outside the lock for dead-lock freedom ───────────────
        return self._func(*all_args, **all_kwargs)

    def execute_sync(self, *extra_args: P.args, **extra_kwargs: P.kwargs) -> R:
        """
        Calls the wrapped function synchronously if it is sync.

        This method is a convenience for invoking sync Pack instances.
        It gathers the arguments under the lock, then releases the lock
        before invoking the underlying function to avoid cross-thread
        contention when nested calls occur.

        Returns:
            The return value of the wrapped function.
        """
        # ── invoke outside the lock for dead-lock freedom ───────────────
        if self._is_async:
            raise TypeError("Cannot execute asynchronously wrapped function as sync.")

        # ── gather args/kwargs atomically ────────────────────────────────
        with self._lock:
            all_args = tuple(self._args) + extra_args
            all_kwargs = {**dict(self._kwargs), **extra_kwargs}

        return self._func(*all_args, **all_kwargs)

    async def execute_async(self, *extra_args: P.args, **extra_kwargs: P.kwargs) -> Any:
        """
        Calls the wrapped function as a coroutine if it is async.

        This method is a convenience for invoking async Pack instances.
        It gathers the arguments under the lock, then releases the lock
        before invoking the underlying function to avoid cross-thread
        contention when nested calls occur.

        Returns:
            The coroutine object returned by the wrapped function.
        """
        # ── invoke outside the lock for dead-lock freedom ───────────────
        if not self._is_async:
            raise TypeError("Cannot execute synchronously wrapped function as async.")

        # ── gather args/kwargs atomically ────────────────────────────────
        with self._lock:
            all_args = tuple(self._args) + extra_args
            all_kwargs = {**dict(self._kwargs), **extra_kwargs}

        return await self._func(*all_args, **all_kwargs)


    @staticmethod
    def verify(item_to_check: Any) -> bool:
        """
        A robust, centralized validator for Pack instances and iterables of Packs.

        This utility method provides a single, reliable way to ensure that a given
        object is either a valid Pack or an iterable containing only valid Packs.
        It's designed to be used at the boundaries of your API to enforce the
        "unit of work" contract before processing.

        Args:
            item_to_check (Any):
                The item to validate. Can be a single Pack instance or an
                iterable (e.g., list, tuple) containing Pack objects.

        Returns:
            bool:
                Returns True if the validation succeeds.

        Raises:
            TypeError:
                If the `item_to_check` (or any element within it) is not an
                instance of Pack.
        """
        # First, check if the item is an iterable (but not a string, which is a common edge case).
        # This allows the method to recursively validate collections of tasks.
        if isinstance(item_to_check, Collection) and not isinstance(item_to_check, str):
            for task in item_to_check:
                # Recursively call verify on each item in the collection.
                Pack.verify(task)
            return True

        # If the item is not an iterable, it must be a single Pack instance.
        if isinstance(item_to_check, Package):
            return True

        # If it's neither, it's an invalid type. This provides a clear error message.
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
            result = combo(x)   # ≈ p3(p2(p1(x)))
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
            return task._func.__wrapped__  # allow deeper introspection for equality, etc.
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
        Normalize a single callable, Package, or an iterable of them into a ConcurrentList of Package instances.

        This is used to ensure all tasks are safe, wrapped, and concurrency-ready before use in
        thread-based systems like Group or Conductor.

        Args:
            tasks: A single task or a collection of tasks.

        Returns:
            A ConcurrentList of validated, thread-safe Package instances.

        Raises:
            TypeError: If any task is invalid, None, or an async/coroutine/generator.
        """
        if tasks is None:
            raise TypeError("Tasks input cannot be None.")

        # Handle single callable or Package
        if isinstance(tasks, (Callable, Package)):
            return [Package(Package._normalize_task(tasks))]

        if not isinstance(tasks, Iterable):
            raise TypeError(f"Expected a callable or iterable of callables, got {type(tasks).__name__}")

        result = []
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

    # inside class Package …

    # ───────────────────────────── single item ───────────────────────────── #
    @staticmethod
    def _pack(task: Union[Callable[P, R], "Package[P, R]"]) -> "Package[P, R]":
        """
        Internal mirror of `Pack()`. Ensures any callable or Package becomes a Package safely.
        Preserves identity and avoids double wrapping.
        """
        if isinstance(task, Package):
            return task
        return Pack(task)

    # ──────────────────────────── many items ─────────────────────────────── #
    @staticmethod
    def _pack_many(
            tasks: Union[
                Callable[P, R],
                "Package[P, R]",
                Iterable[Union[Callable[P, R], "Package[P, R]"]]
            ]
    ) -> List["Package[P, R]"]:
        """
        Internal mirror of `Pack()` for batch input. Always returns valid Packages.

        Args:
            tasks: A single task or iterable of tasks.

        Returns:
            ConcurrentList of Package objects.

        Raises:
            TypeError: On invalid input.
        """
        if tasks is None:
            raise TypeError("Tasks input cannot be None.")

        if isinstance(tasks, (Callable, Package)):
            return [Package._pack(tasks)]

        if not isinstance(tasks, Iterable) or isinstance(tasks, str):
            raise TypeError(f"Expected a callable or iterable of callables, got {type(tasks).__name__}")

        result = []
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
            func = self._func.__wrapped__
            # Combine stored args with new args, and stored kwargs with new kwargs
            combined_args = tuple(self._args) + args
            combined_kwargs = {**dict(self._kwargs), **kwargs}
            return Package(func, *combined_args, **combined_kwargs)

    def freeze(self) -> None:
        """
        Prevent any future mutation (via `bind()`).
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
        """Return a thread-safe copy of the stored keyword arguments."""
        with self._lock:
            return self._kwargs

    @property
    def signature(self):
        """
        Return a pseudo-signature object representing bound args.

        Returns:
            SimpleNamespace with `arguments` ConcurrentDict containing arg0, arg1... and kwarg names.
        """
        with self._lock:
            if self._signature_cache is None:
                sig = inspect.signature(self._func.__wrapped__)
                arg_map = {}
                for i, value in enumerate(self._args):
                    arg_map[f"arg{i}"] = value
                arg_map.update(self._kwargs)
                self._signature_cache = types.SimpleNamespace(arguments=arg_map)
            return self._signature_cache


    def __add__(self, other: "Package") -> "Package":
        """
        Add operator: sum results of both packages.

        Example:
            (Pack(f) + Pack(g))(...) == f(...) + g(...)

        Returns:
            A new Package that adds both results.
        """
        if not isinstance(other, Package):
            raise TypeError("+ expects another Package")
        return Package(lambda *a, **kw: self(*a, **kw) + other(*a, **kw))

    def __getattr__(self, item: str):
        """
        Delegate attribute access to the wrapped function.
        """
        try:
            return self._func
        except AttributeError:
            raise AttributeError(item) from None

    def __dir__(self):
        """
        Merge function attributes with class attributes for autocompletion.
        """
        return sorted(
            set(super().__dir__())
            | set(dir(self._func))
            | set(dir(self._func.__wrapped__))
        )

    def __repr__(self) -> str:
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