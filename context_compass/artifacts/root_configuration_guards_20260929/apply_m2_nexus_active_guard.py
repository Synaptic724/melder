"""M2: Nexus refuses reconfiguration while active, like Crystallizer and MutationResearch (melder_0, 2026-09-29)."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])

CONFIGURE_OLD = '''            - Type-checked: a non-`NexusConfiguration` raises `TypeError`.
            - Replaces any previously installed configuration.

        Args:
            configuration:
                Configuration object to install.

        Threading:
            Applied under the Nexus lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            None.

        Raises:
            RuntimeError: If Nexus has been cleaned.
            TypeError: If `configuration` is not a `NexusConfiguration`.
        """
        self.check_cleaned()
        if not isinstance(configuration, NexusConfiguration):
            raise TypeError("configuration must be a NexusConfiguration.")
        with self._lock:
            self._configuration = configuration
            self._configured = True
'''
CONFIGURE_NEW = '''            - Type-checked: a non-`NexusConfiguration` raises `TypeError`.
            - Replaces any previously installed configuration - but REFUSES while
              Nexus is active (0.2.8210): a live Nexus reads its policy at every
              Rift validation, so a swap would change the rules under existing
              Rifts. Deactivate first; the installed policy is kept until then.
              Crystallizer and MutationResearch refuse the same way.

        Args:
            configuration:
                Configuration object to install.

        Threading:
            Applied under the Nexus lock; the active check and the install are one
            critical section.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            None.

        Raises:
            RuntimeError: If Nexus has been cleaned, or is active.
            TypeError: If `configuration` is not a `NexusConfiguration`.
        """
        self.check_cleaned()
        if not isinstance(configuration, NexusConfiguration):
            raise TypeError("configuration must be a NexusConfiguration.")
        with self._lock:
            if self._activated:
                raise RuntimeError(
                    "Cannot reconfigure Nexus while it is active. Deactivate it first."
                )
            self._configuration = configuration
            self._configured = True
'''

ACTIVATE_OLD = '''        Contract:
            - Optionally replaces the installed configuration before enabling.
            - Finalizes the installed configuration before setting enabled.
            - Does not create a default configuration automatically when none
              is installed.

        Args:
            configuration:
                Optional replacement configuration.

        Returns:
            None.

        Raises:
            RuntimeError:
                If Nexus has no installed configuration.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is not None:
                self._configuration = configuration
                self._configured = True
'''
ACTIVATE_NEW = '''        Contract:
            - Optionally replaces the installed configuration before enabling -
              but not while Nexus is already active (0.2.8210): passing a
              different configuration then raises, exactly as `configure()` does.
              Passing the installed configuration, or none, re-enables as before.
            - Finalizes the installed configuration before setting enabled.
            - Does not create a default configuration automatically when none
              is installed.

        Args:
            configuration:
                Optional replacement configuration.

        Returns:
            None.

        Raises:
            RuntimeError:
                If Nexus has no installed configuration, or it is active and a
                different configuration is supplied.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is not None:
                if self._activated and configuration is not self._configuration:
                    raise RuntimeError(
                        "Cannot reconfigure Nexus while it is active. Deactivate it first."
                    )
                self._configuration = configuration
                self._configured = True
'''

path = ROOT / "nexus/nexus.py"
raw = path.read_bytes()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
for old, new in ((CONFIGURE_OLD, CONFIGURE_NEW), (ACTIVATE_OLD, ACTIVATE_NEW)):
    assert text.count(old) == 1, old[:60]
    text = text.replace(old, new, 1)
path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
print("patched nexus/nexus.py")
