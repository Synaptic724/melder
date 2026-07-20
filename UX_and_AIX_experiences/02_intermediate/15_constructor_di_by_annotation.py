"""
TIER: intermediate (15)
GOAL: THE DI heart - annotate a constructor parameter with a bound
      class and melder injects it. Dependencies resolve recursively;
      you meld the top and the graph assembles itself.
SURFACE EXERCISED: type-hint constructor DI (SINGLE_BY_ANNOTATION)
"""
import melder as md


class Database:
    def query(self) -> str:
        return "42 rows"


class ReportService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def run(self) -> str:
        return "report over " + self.database.query()


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Database, existence="unique")
    book.bind(spell=ReportService, existence="unique")
    conduit = book.conjure()

    report = conduit.meld(spell=ReportService)
    assert isinstance(report.database, Database)
    print(report.run())
    print("annotated the parameter; melder built the graph")


if __name__ == "__main__":
    main()
