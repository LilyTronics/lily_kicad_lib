"""
Checks the library and report the errors
"""

from models.symbols_checker import SymbolsChecker
from models.footprints_checker import FootprintsChecker


def check_library(messages):
    SymbolsChecker.run(messages)
    FootprintsChecker.run(messages)


if __name__ == "__main__":

    report_messages = []
    check_library(report_messages)
    for message in report_messages:
        print(message["item"], message["message"])
    print(f"{len(report_messages)} messages")
