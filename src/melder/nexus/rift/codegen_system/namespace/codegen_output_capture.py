import builtins
import threading
from typing import Callable, List

from melder.utilities.general_base.cleanable import Cleanable


class CodegenOutputCapture(Cleanable):
    """
    Internal

    Room-owned `print` for one codegen execution, keeping what room code prints for the execution payload.

    Purpose:
        Let an agent see what its code printed. A codegen room whose configuration enables output capture
        (`RiftConfiguration.with_codegen_output_capture`, on by default) puts this object's `capture_print` in place of
        the interpreter's `print` in the request's builtins, so the text room code prints to stdout is kept here and
        returned under `execute_codegen`'s `output` key instead of reaching the host process's stdout (GitHub #337,
        task 2).

    Contract:
        - `capture_print` takes the builtin's signature - `*values, sep=' ', end='\\n', file=None, flush=False` - and
          keeps exactly the text the builtin would have written to stdout: each value's `str`, joined by `sep`, ended
          by `end`, with None meaning the default. A `sep` or `end` that is neither None nor a string raises TypeError
          with the builtin's message, keeping nothing.
        - A `file` that is not None goes to the interpreter's `print` with every argument, as before; only stdout text
          is captured. `flush` has nothing to flush here.
        - At most `limit` characters are kept: the first ones, in print order. Every later character is counted, and
          `output` then ends with one line "[output truncated: N more characters not kept]".

    Threading:
        One `RLock` guards the kept text and both counters, so room code printing from several threads (where its
        profile allows threads) loses no text below the limit and never interleaves inside one print's text.

    Lifecycle / Cleanup:
        Built per request by `CodegenNamespaceBuilder.build` and owned by that request's `CodegenNamespace`, which
        cleans it. `cleanup` is idempotent and drops the kept text; afterwards `capture_print` and `output` raise
        RuntimeError, so a thread room code left printing after its request ended fails rather than writing anywhere.

    Registration:
        MELDER KERNEL - guarded. Built by `CodegenNamespaceBuilder`; never user-constructed or bound.

    Subsystem Context:
        Installed by `CodegenBuiltinsStrategy` into the execute path's builtins only; the materialize path
        (`CodegenNamespaceBuilder.build_builtins`) never captures, because a materialized module's code runs after the
        request that created it has returned. `CodegenExecutor` reads `output` after `exec` returns or raises and
        hands it to `CodegenExecutionResult`.

    System Context:
        A room whose code printed to the host's stdout told its agent nothing: the payload is the agent's only view of
        what happened. Capturing per request, and bounding what is kept, returns that view without letting code that
        prints in a loop grow the host's memory.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Room-owned print that keeps room code's output for the execution payload. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_limit",
        "_kept_chunks",
        "_kept_characters",
        "_dropped_characters",
    ]

    def __init__(self, *, limit: int) -> None:
        """
        Initialize an empty capture.

        Args:
            limit:
                The most characters of printed text this capture keeps; an int of at least 1 (the room's
                `codegen_output_limit`).

        Returns:
            None.

        Raises:
            TypeError:
                If `limit` is not an int, or is a bool.
            ValueError:
                If `limit` is below 1.
        """
        super().__init__()
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an int, not {0}.".format(type(limit).__name__))
        if limit < 1:
            raise ValueError("limit must be at least 1 character, got {0}.".format(limit))
        self._lock: threading.RLock = threading.RLock()
        self._limit: int = limit
        self._kept_chunks: List[str] = []
        self._kept_characters: int = 0
        self._dropped_characters: int = 0

    def cleanup(self) -> None:
        """
        Idempotently drop the kept text and end the capture.

        Contract:
            - Safe to call more than once; later calls return at once.
            - Afterwards `capture_print` and `output` raise RuntimeError.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-read the latch under the lock: another thread may have finished cleanup while this one waited.
            if self.cleaned:
                return
            self._cleaned = True
            self._kept_chunks.clear()
            del self._kept_chunks
            del self._limit
            del self._kept_characters
            del self._dropped_characters
        del self._lock

    def capture_print(
            self,
            *values: object,
            sep: object = " ",
            end: object = "\n",
            file: object = None,
            flush: bool = False,
    ) -> None:
        """
        Keep what `print(*values, sep=sep, end=end)` would have written to stdout, up to the limit.

        Args:
            values:
                The objects room code prints; each is converted with `str`.
            sep:
                The separator between values: a string, or None for a single space.
            end:
                The text after the last value: a string, or None for a newline.
            file:
                None to capture; any other object receives the text through the interpreter's `print`, as the builtin
                would write it.
            flush:
                Passed to the interpreter's `print` with an explicit `file`; nothing to flush when capturing.

        Returns:
            None.

        Raises:
            TypeError:
                If `sep` or `end` is neither None nor a string ("sep must be None or a string, not int"), as the
                builtin raises.
            RuntimeError:
                If the capture has been cleaned (the request that owned it has ended).
        """
        self.check_cleaned()
        if file is not None:
            # Room code's arguments go to the interpreter's print unchanged; it checks them as it always has.
            interpreter_print: Callable[..., None] = builtins.print
            interpreter_print(*values, sep=sep, end=end, file=file, flush=flush)
            return
        separator = self._resolve_print_text("sep", sep, " ")
        ending = self._resolve_print_text("end", end, "\n")
        text = separator.join([str(value) for value in values]) + ending
        with self._lock:
            room_left = self._limit - self._kept_characters
            if room_left <= 0:
                self._dropped_characters += len(text)
                return
            kept_text = text[:room_left]
            self._kept_chunks.append(kept_text)
            self._kept_characters += len(kept_text)
            self._dropped_characters += len(text) - len(kept_text)

    @property
    def output(self) -> str:
        """
        Return the kept text, with one truncation line when text past the limit was dropped.

        Contract:
            - Without drops: exactly the kept text, possibly empty.
            - With drops: the kept text, a newline when it does not already end with one, then
              "[output truncated: N more characters not kept]\\n", N counting every dropped character.

        Returns:
            str: The text for the execution payload's `output` key.

        Raises:
            RuntimeError:
                If the capture has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            kept_text = "".join(self._kept_chunks)
            if self._dropped_characters == 0:
                return kept_text
            line_break = "" if kept_text.endswith("\n") else "\n"
            return "{0}{1}[output truncated: {2} more characters not kept]\n".format(
                kept_text,
                line_break,
                self._dropped_characters,
            )

    @staticmethod
    def _resolve_print_text(keyword: str, value: object, default: str) -> str:
        """
        Resolve one of `print`'s `sep` or `end` arguments the way the builtin does.

        Args:
            keyword:
                "sep" or "end", for the error message.
            value:
                The argument room code passed.
            default:
                The text None stands for.

        Returns:
            str: `value` when it is a string; `default` when it is None.

        Raises:
            TypeError:
                If `value` is neither None nor a string, with the builtin's message.
        """
        if value is None:
            return default
        if isinstance(value, str):
            return value
        raise TypeError(
            "{0} must be None or a string, not {1}".format(keyword, type(value).__name__)
        )
