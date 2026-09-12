"""Probe spellframe grouping through Melder's real public integration path.

Run from the Melder repository in PowerShell:
    $env:PYTHONPATH = (Resolve-Path src).Path
    py -3.14t experimentation/test_spellframe_type_injection.py -v

Ten scenarios run in both automatic and dynamic mode. Constructor inference,
explicit SpellMap selection, qualified public meld and machine-ID lookup are
kept separate. No compiler or resolver behavior is mocked. The native test-only
Aether reset isolates each case inside this experiment process. System caching
is disabled through frame configuration, matching the native cache tests, so
saved compilation plans cannot contaminate these binding/injection cases.

The file uses unittest so it runs without pytest and can also be collected by
pytest when that runner is available. Application/runtime source is unchanged.
"""

import inspect
import sys
import unittest
from typing import ClassVar, Optional, Union

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError


class Provider:
    """A resource-free dependency with observable behavior for identity checks."""

    def __init__(self) -> None:
        """Initialize the provider's stable value; no external resource is owned."""
        self.value = "ready"

    def read(self) -> str:
        """Return the stable value used to prove that a constructed provider works."""
        return self.value


class UserProvider(Provider):
    """A distinct provider type with an observable userland value."""

    def __init__(self) -> None:
        """Initialize the inherited value contract with a different public result."""
        super().__init__()
        self.value = "userland"


class Consumer:
    """Borrow an injected Provider and use it through its ordinary typed contract."""

    def __init__(self, provider: Provider) -> None:
        """Retain the injected provider without taking ownership of its disposal."""
        self.provider = provider

    def execute(self) -> str:
        """Use the dependency so an unresolved descriptor or missing object fails."""
        return "consumer:" + self.provider.read()


class MappedConsumer(Consumer):
    """Choose the commandops provider explicitly when several providers are bound."""

    def __init__(
        self,
        provider: Union[Provider, SpellMap] = SpellMap(
            spellframe="commandops",
            binding_name="service",
        ),
    ) -> None:
        """Require Melder to replace the descriptor with the selected Provider.

        A direct Python call that leaves the SpellMap default unresolved raises
        TypeError. The injected provider remains borrowed by the consumer.
        """
        if isinstance(provider, SpellMap):
            raise TypeError("MappedConsumer requires its SpellMap to be resolved.")
        super().__init__(provider)


class AutomaticSpellframeTests(unittest.TestCase):
    """Exercise public binding/conjure/meld behavior in a fresh automatic world."""

    DYNAMIC: ClassVar[bool] = False

    @staticmethod
    def reset_world() -> None:
        """Use the repository's native test reset and reattach class-level hosts.

        This is process-local test isolation, matching Melder integration tests;
        it does not replace registration, compilation, validation or resolution.
        """
        Aether._reset_singleton_for_tests()
        runtime = Aether()
        Spellbook._aether = runtime
        Conduit._aether = runtime

    def setUp(self) -> None:
        """Create one real book with deterministic phase scheduling for each case."""
        self.reset_world()
        self.book: Spellbook = Spellbook()
        self.book.get_configuration().set_property(
            "phase_scheduler_workers_per_spellbook", 1
        )
        self.book.configure_aether_frame(
            system_state="dynamic" if self.DYNAMIC else None,
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
        self.root: Optional[Conduit] = None

    def tearDown(self) -> None:
        """Attempt root/book cleanup and always reset the process-local world."""
        try:
            if self.root is not None:
                self.root.cleanup()
        finally:
            try:
                self.book.cleanup()
            finally:
                self.reset_world()

    def bind_provider(
        self,
        spellframe: Optional[str] = None,
        binding_name: Optional[str] = None,
    ) -> str:
        """Bind Provider with unique lifetime and return its public machine ID."""
        return self.book.bind(
            spell=Provider,
            existence=Existence.unique,
            permissions="create",
            spellframe=spellframe,
            binding_name=binding_name,
        )

    def bind_distinct_provider_pair(self) -> tuple[str, str]:
        """Bind two distinct types under the same binding name in different frames."""
        commandops_id = self.bind_provider("commandops", "service")
        userland_id = self.book.bind(
            spell=UserProvider,
            existence=Existence.unique,
            permissions="create",
            spellframe="userland",
            binding_name="service",
        )
        return commandops_id, userland_id

    def bind_consumer(self, consumer_type: type[Consumer] = Consumer) -> str:
        """Bind a consumer class and return the ID used to resolve the root object."""
        return self.book.bind(
            spell=consumer_type,
            existence=Existence.many,
            permissions="create",
        )

    def conjure_root(self) -> Conduit:
        """Run real native validation/compilation and retain the root for cleanup."""
        self.root = self.book.conjure(
            name="spellframe_type_injection_experiment",
            dynamic=self.DYNAMIC,
        )
        return self.root

    def test_plain_class_injection_baseline(self) -> None:
        """Unframed constructor injection and direct class lookup share Provider."""
        provider_id = self.bind_provider()
        consumer_id = self.bind_consumer()
        root = self.conjure_root()

        consumer = root.meld(spell_id=consumer_id)
        provider = root.meld(spell_id=provider_id)

        self.assertEqual(consumer.execute(), "consumer:ready")
        self.assertIs(consumer.provider, provider)
        self.assertIs(root.meld(Provider), provider)

    def test_named_framed_provider_still_injects_by_concrete_type(self) -> None:
        """A unique framed/named Provider satisfies an ordinary typed parameter."""
        provider_id = self.bind_provider("commandops", "service")
        consumer_id = self.bind_consumer()
        root = self.conjure_root()

        consumer = root.meld(spell_id=consumer_id)
        provider = root.meld(spellframe="commandops", binding_name="service")

        self.assertEqual(consumer.execute(), "consumer:ready")
        self.assertIs(consumer.provider, provider)
        self.assertIs(provider, root.meld(spell_id=provider_id))

    def test_two_spellframes_do_not_disambiguate_plain_type_injection(self) -> None:
        """Two Provider registrations fail specifically because inference is ambiguous."""
        self.bind_provider("commandops", "service")
        self.bind_provider("userland", "service")
        self.bind_consumer()

        with self.assertRaises(PhaseExecutionError) as raised:
            self.conjure_root()

        errors = raised.exception.errors
        self.assertTrue(
            any("multiple DI candidates" in str(error) for error in errors),
            "Expected an ambiguous-provider error, got: "
            + "; ".join(str(error) for error in errors),
        )

    def test_spellmap_selects_one_provider_across_spellframes(self) -> None:
        """The explicit descriptor chooses commandops and leaves userland distinct."""
        commandops_id = self.bind_provider("commandops", "service")
        userland_id = self.bind_provider("userland", "service")
        consumer_id = self.bind_consumer(MappedConsumer)
        root = self.conjure_root()

        consumer = root.meld(spell_id=consumer_id)
        commandops_provider = root.meld(spell_id=commandops_id)
        userland_provider = root.meld(spell_id=userland_id)

        self.assertEqual(consumer.execute(), "consumer:ready")
        self.assertIs(consumer.provider, commandops_provider)
        self.assertIsNot(consumer.provider, userland_provider)

    def test_spellframe_only_selects_default_binding(self) -> None:
        """Omitting binding_name selects each spellframe's default provider."""
        commandops_id = self.bind_provider(spellframe="commandops")
        userland_id = self.book.bind(
            spell=UserProvider,
            existence=Existence.unique,
            permissions="create",
            spellframe="userland",
        )
        consumer_id = self.bind_consumer()
        root = self.conjure_root()

        commandops_provider = root.meld(spellframe="commandops")
        userland_provider = root.meld(spellframe="userland")
        consumer = root.meld(spell_id=consumer_id)

        self.assertEqual(commandops_provider.read(), "ready")
        self.assertEqual(userland_provider.read(), "userland")
        self.assertIsNot(commandops_provider, userland_provider)
        self.assertIs(commandops_provider, root.meld(spell_id=commandops_id))
        self.assertIs(userland_provider, root.meld(spell_id=userland_id))
        self.assertIs(
            commandops_provider,
            root.meld(spellframe="commandops", binding_name="__default__"),
        )
        self.assertEqual(consumer.execute(), "consumer:ready")
        self.assertIs(consumer.provider, commandops_provider)

    def test_spellframe_only_does_not_guess_named_binding(self) -> None:
        """A missing default is an error even when the frame has one named provider."""
        provider_id = self.bind_provider("commandops", "service")
        root = self.conjure_root()

        with self.assertRaisesRegex(KeyError, "binding='__default__'"):
            root.meld(spellframe="commandops")

        provider = root.meld(spellframe="commandops", binding_name="service")
        self.assertEqual(provider.read(), "ready")
        self.assertIs(provider, root.meld(spell_id=provider_id))

    def test_same_binding_name_across_spellframes_selects_distinct_providers(self) -> None:
        """The frame distinguishes two addresses whose binding name is identical."""
        commandops_id, userland_id = self.bind_distinct_provider_pair()
        root = self.conjure_root()

        commandops_provider = root.meld(spellframe="commandops", binding_name="service")
        userland_provider = root.meld(spellframe="userland", binding_name="service")

        self.assertEqual(commandops_provider.read(), "ready")
        self.assertEqual(userland_provider.read(), "userland")
        self.assertIsNot(commandops_provider, userland_provider)
        self.assertIs(commandops_provider, root.meld(spell_id=commandops_id))
        self.assertIs(userland_provider, root.meld(spell_id=userland_id))

    def test_spellmap_selects_distinct_types_with_same_binding_name(self) -> None:
        """SpellMap selects commandops/service when userland/service also exists."""
        commandops_id, userland_id = self.bind_distinct_provider_pair()
        consumer_id = self.bind_consumer(MappedConsumer)
        root = self.conjure_root()

        consumer = root.meld(spell_id=consumer_id)
        commandops_provider = root.meld(spell_id=commandops_id)
        userland_provider = root.meld(spell_id=userland_id)

        self.assertEqual(consumer.execute(), "consumer:ready")
        self.assertIs(consumer.provider, commandops_provider)
        self.assertIsNot(consumer.provider, userland_provider)
        self.assertEqual(userland_provider.read(), "userland")

    def test_direct_qualified_lookup_needs_no_spellmap(self) -> None:
        """Public frame/binding arguments and spell_id resolve the same live object."""
        provider_id = self.bind_provider("commandops", "service")
        root = self.conjure_root()

        by_address = root.meld(spellframe="commandops", binding_name="service")
        by_id = root.meld(spell_id=provider_id)

        self.assertEqual(by_address.read(), "ready")
        self.assertIs(by_address, by_id)

    def test_direct_class_lookup_does_not_alias_custom_address(self) -> None:
        """Direct class lookup has different addressing semantics from inference."""
        provider_id = self.bind_provider("commandops", "service")
        root = self.conjure_root()
        self.assertEqual(root.meld(spell_id=provider_id).read(), "ready")

        with self.assertRaisesRegex(KeyError, "No spell found"):
            root.meld(Provider)


class DynamicSpellframeTests(AutomaticSpellframeTests):
    """Run the same ten scenarios with dynamic frame posture and native meld gates."""

    DYNAMIC: ClassVar[bool] = True


if __name__ == "__main__":
    print("Python:", sys.version.split()[0], flush=True)
    print("GIL enabled:", sys._is_gil_enabled(), flush=True)
    print("Melder source:", inspect.getfile(Spellbook), flush=True)
    unittest.main(verbosity=2)
