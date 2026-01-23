"""
Class that checks for unused items
"""

import os

from toolbox.app_data import AppData
from toolbox.models.parsers.lib_parser import LibParser


class UnusedItemsChecker:

    stdout = print

    @classmethod
    def run(cls):
        LibParser.stdout = cls.stdout
        cls.stdout("Get library symbols")
        symbols = LibParser.get_symbols()

        report_messages = []

        cls._check_unused_datasheets(symbols,report_messages)

        # cls._check_unused_footprints(report_messages)

        # cls._check_unused_

        return report_messages

    ############
    # Checkers #
    ############

    @classmethod
    def _check_unused_datasheets(cls, symbols, report_messages):
        caller = f"({cls.__name__}._check_unused_datasheets)"
        file_path = f"{AppData.APP_PATH}/docs/datasheets"
        for current_folder, sub_folders, filenames in os.walk(file_path):
            sub_folders.sort()
            filenames.sort()
            for filename in filenames:
                rel_path = os.path.join(current_folder, filename).replace("\\", "/")[len(file_path):]
                matches = list(filter(lambda x: rel_path in x["Datasheet"], symbols))
                if len(matches) == 0:
                    report_messages.append({
                        "item": rel_path,
                        "message": f"Datasheet file is not used in any symbol {caller}"
                    })


if __name__ == "__main__":

    from toolbox.models.show_messages import show_messages

    show_messages(UnusedItemsChecker.run())
