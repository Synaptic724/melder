"""
The 0.2.8235 release-note example, run as written (TASK-2026-10-14-fix_many_child_follows_holder).

Run: PYTHONPATH=<tree>/src python release_example_0_2_8235.py
On 0.2.8234 the first assertion fails (the request scope closed the connection); on 0.2.8235 every assertion holds.
"""
import melder as md


class Connection:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Repository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection


book = md.Spellbook()
book.bind(spell=Connection, existence="many", disposal_method_names=["close"])
book.bind(spell=Repository, existence="unique")
root = book.conjure()

with root.enter_lesser_conduit() as request:
    repository = request.meld("Repository")      # first built inside the request scope

assert not repository.connection.closed          # 0.2.8234: closed when the request scope ended
assert root.meld("Repository") is repository
root.cleanup()
assert repository.connection.closed              # closed with the root that owns the repository
print("release example holds")
