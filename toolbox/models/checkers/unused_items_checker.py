"""
Class that checks for unused items
"""

import os

from toolbox.app_data import AppData
from toolbox.models.parsers.lib_parser import LibParser


class UnusedItemsChecker:

    stdout = print

    _SKIP_SYMBOLS_UNUSED = ["0_new_symbol", "Earth", "GND", "GNDA", "Vxx", "con_TC2030-IDC_lock", "doc_logo_lilytronics"]
    _SKIP_FOOTPRINTS_UNUSED = ["0_new_footprint", "mec_mouse_bytes"]

    @classmethod
    def run(cls):
        LibParser.stdout = cls.stdout
        symbols = LibParser.get_symbols()
        footprints = LibParser.get_footprints()
        report_messages = []

        cls._check_unused_symbols(symbols, report_messages)
        cls._check_unused_datasheets(symbols, report_messages)
        cls._check_unused_footprints(symbols, footprints, report_messages)
        cls._check_unused_3d_models(footprints, report_messages)
        cls._check_unused_pictures(footprints, report_messages)

        return report_messages

    ############
    # Checkers #
    ############

    @classmethod
    def _check_unused_symbols(cls, symbols, report_messages):
        caller = f"({cls.__name__}._check_unused_datasheets)"
        for symbol in filter(lambda s: s.get("Extends", None) is None and s["Name"] not in cls._SKIP_SYMBOLS_UNUSED, symbols):
            matches = list(filter(lambda x: x.get("Extends", None) == symbol["Name"], symbols))
            if len(matches) == 0:
                report_messages.append({
                    "item": symbol["Name"],
                    "message": f"Symbol is not used in any part {caller}"
                })

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

    @classmethod
    def _check_unused_footprints(cls, symbols, footprints, report_messages):
        caller = f"({cls.__name__}._check_unused_footprints)"
        for footprint in filter(lambda f: f["Name"] not in cls._SKIP_FOOTPRINTS_UNUSED, footprints):
            matches = list(filter(lambda x: x["Footprint"] == f"lily_footprints:{footprint["Name"]}", symbols))
            if len(matches) == 0:
                report_messages.append({
                    "item": footprint["Name"],
                    "message": f"Footprint is not used in any symbol {caller}"
                })

    @classmethod
    def _check_unused_3d_models(cls, footprints, report_messages):
        caller = f"({cls.__name__}._check_unused_3d_models)"
        file_path = f"{AppData.APP_PATH}/3d_models"
        for filename in filter(lambda f: os.path.isfile(os.path.join(file_path, f)), os.listdir(file_path)):
            rel_path = f"../3d_models/{filename}"
            matches = list(filter(lambda x: rel_path == x.get("Model", None), footprints))
            if len(matches) == 0:
                report_messages.append({
                    "item": filename,
                    "message": f"3D model file is not used in any footprint {caller}"
                })

    @classmethod
    def _check_unused_pictures(cls, footprints, report_messages):
        caller = f"({cls.__name__}._check_unused_pictures)"
        file_path = f"{AppData.APP_PATH}/lily_footprints.pretty"
        for filename in filter(lambda f: os.path.isfile(os.path.join(file_path, f)) and f.endswith(".png"), os.listdir(file_path)):
            matches = list(filter(lambda x: filename == f"{x["Name"]}.png", footprints))
            if len(matches) == 0:
                report_messages.append({
                    "item": filename,
                    "message": f"picture is not matching any footprint {caller}"
                })


if __name__ == "__main__":

    from toolbox.models.show_messages import show_messages

    show_messages(UnusedItemsChecker.run())
