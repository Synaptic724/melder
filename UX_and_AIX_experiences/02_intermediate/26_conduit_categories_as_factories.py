"""
TIER: intermediate (26)
GOAL: Conduit CATEGORIES are your factory layer. Instead of writing an
      abstract factory in front of your scopes, NAME conduits after the
      resolution ideas your app already has - "platform", "services",
      "workflows" - and late-bind the dependencies BETWEEN categories
      with SpellContract sockets.
      ORDER OF OPERATIONS IS THE LAW (owner ruling 2026-07-20). Per
      dependency edge, in this exact order:
        1) conjure the PROVIDER conduit
        2) conjure the CONSUMER conduit (the SpellContract side)
        3) link() - only AFTER both conduits are built
        4) the consumer pulls the provider spell into the contract
        5) meld AFTER the fact - completing the late binding for that
           world's products
      Assemble the chain edge by edge, in dependency order. No factory
      objects exist anywhere - the conduit NAMES are the factory types.
      THE ARC: this is beginner lesson 25 one level UP. Spellframes
      categorize spells WITHIN one world; conduits categorize WORLDS -
      each category gains an OWNER, and permissions + contracts + links
      set the resolution conditions at the category boundary.
SURFACE EXERCISED: md.SpellContract, link, add_spell_to_contract,
                   named category conduits
"""
import sys
from pathlib import Path
from typing import Protocol

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class ConfigContract(Protocol):
    def get(self, key: str) -> str: ...


class ReportingContract(Protocol):
    def report(self) -> str: ...


class ConfigStore:
    """Owned by the "platform" category."""

    def get(self, key: str) -> str:
        return f"{key}-from-platform"


class ReportService:
    """Owned by "services". Its config is a LATE-BOUND hole: the socket
    names the contract identity; the provider arrives across the link."""

    def __init__(
        self,
        config: ConfigContract = md.SpellContract(
            spellframe=ConfigContract, binding_name="platform",
        ),
    ) -> None:
        self.config = config

    def report(self) -> str:
        return f"report({self.config.get('region')})"


class ReportWorkflow:
    """Owned by "workflows". Same idea one level up: it wants whatever
    satisfies the reporting contract, wherever that conduit lives."""

    def __init__(
        self,
        service: ReportingContract = md.SpellContract(
            spellframe=ReportingContract, binding_name="reporting",
        ),
    ) -> None:
        self.service = service

    def run(self) -> str:
        return f"workflow -> {self.service.report()}"


def main() -> None:
    # One book per CATEGORY - each book is that category's recipe list.
    platform_book = dynamic_spellbook()
    config_id = platform_book.bind(
        spell=ConfigStore, existence="unique",
        spellframe=ConfigContract, binding_name="platform",
    )
    services_book = dynamic_spellbook()
    service_id = services_book.bind(
        spell=ReportService, existence="unique",
        spellframe=ReportingContract, binding_name="reporting",
    )
    workflows_book = dynamic_spellbook()
    workflow_id = workflows_book.bind(spell=ReportWorkflow, existence="unique")

    # ---- EDGE 1: platform feeds services ----
    platform = platform_book.conjure(dynamic=True, name="platform")  # 1) provider
    services = services_book.conjure(dynamic=True, name="services")  # 2) consumer
    platform.link(services)                                          # 3) link AFTER both
    services.add_spell_to_contract(                                  # 4) pull
        spell_id=config_id, conduit=platform, permissions="create",
    )
    service = services.meld(spell=service_id)                        # 5) meld after the fact

    # ---- EDGE 2: services feeds workflows (same cycle, one level up) ----
    workflows = workflows_book.conjure(dynamic=True, name="workflows")
    services.link(workflows)
    workflows.add_spell_to_contract(
        spell_id=service_id, conduit=services, permissions="create",
    )
    workflow = workflows.meld(spell=workflow_id)

    assert workflow.service is service  # the finished product crossed the edge
    print("category chain resolved:", workflow.run())
    print("factory types were just conduit names:",
          platform.name, "->", services.name, "->", workflows.name)


if __name__ == "__main__":
    main()
