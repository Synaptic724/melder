"""
TIER: intermediate (02)
GOAL: Every link in the fluent chain, one binder reused across
      registrations: existence (explicit and shorthand), permissions,
      spellframe grouping, binding names, and constructor kwargs.
SURFACE EXERCISED: md.SpellBinder full chain, md.Existence, spellframes
"""
import melder as md


class HttpClient:
    def __init__(self, base_url: str = "", timeout: int = 0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def close(self) -> None:
        pass


class RetryPolicy:
    pass


def main() -> None:
    book = md.Spellbook()
    binder = md.SpellBinder(book)

    # one full sentence: frame + name + kwargs + lifecycle + permissions
    binder.bind(HttpClient) \
        .with_existence(md.Existence.unique) \
        .with_permissions("create") \
        .under_spellframe("network") \
        .named("payments-api") \
        .with_kwargs(disposal_method_names=["close"]) \
        .finalize()

    # binder resets after finalize - next sentence starts clean
    binder.bind(RetryPolicy).as_unique_per_conduit().under_spellframe(
        "network").finalize()

    conduit = book.conjure()
    client = conduit.meld(
        spell=HttpClient, spellframe="network", binding_name="payments-api",
        override={"base_url": "https://pay.example", "timeout": 30},
    )
    assert client.base_url == "https://pay.example" and client.timeout == 30
    print("ctor config via override:", client.base_url)
    # NOTE: with_kwargs passes BIND parameters (here: disposal list);
    # Constructor arguments ride override= at meld time.

    child = conduit.create_lesser_conduit()
    policy_root = conduit.meld(spell=RetryPolicy, spellframe="network")
    policy_child = child.meld(spell=RetryPolicy, spellframe="network")
    assert policy_root is not policy_child
    print("per-conduit policy under a spellframe: one per scope")


if __name__ == "__main__":
    main()
