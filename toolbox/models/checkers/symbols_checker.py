"""
Class that checks the symbols
"""

import os
import re
import threading
import time
import urllib.request

from toolbox.app_data import AppData
from toolbox.models.parsers.lib_parser import LibParser


class SymbolsChecker:

    stdout = print

    REFERENCES = {
        "0_new":        "A",
        "bjt":          "Q",
        "cap":          "C",
        "con":          "X",
        "crystal":      "X",
        "dio":          "D",
        "doc":          "DOC",
        "Earth":        "#PWR",
        "fuse":         "F",
        "GND":          "#PWR",
        "GNDA":         "#PWR",
        "ic":           "U",
        "ind":          "L",
        "logo":         "DOC",
        "mec":          "M",
        "mosfet":       "Q",
        "pot":          "P",
        "pptc":         "F",
        "relay":        "K",
        "res":          "R",
        "switch":       "S",
        "test_point":   "TP",
        "Vxx":          "#PWR"
    }
    PART_FIELDS = ["Datasheet", "Extends", "Footprint", "Manufacturer", "Manufacturer_ID", "JLCPCB_ID", "Lily_ID", "Status"]
    MANDATORY_FIELDS = ["Name", "Reference", "Revision", "Value"]
    OPTIONAL_FIELDS_NON_PARTS = ["Datasheet", "Extends", "Footprint"]
    SKIP_EMPTY_CHECK = ["Description"]

    @classmethod
    def run(cls):
        threads = []
        LibParser.stdout = cls.stdout
        cls.stdout("Check library symbols")
        report_messages = []
        symbols = LibParser.get_symbols()
        cls.stdout(f"Checking {len(symbols)} symbols")
        for symbol in symbols:
            for field in symbol:
                if field not in cls.SKIP_EMPTY_CHECK:
                    cls._check_symbol_field_empty(symbol, field, report_messages)
            cls._check_reference(symbol, report_messages)
            cls._check_revision(symbol, report_messages)
            cls._check_value(symbol, report_messages)
            if symbol["Footprint"] != "":
                cls._check_footprint(symbol, report_messages)
            if symbol["Datasheet"] != "":
                cls._check_datasheet(symbol, report_messages, threads)

        n_print = 0
        while True in list(map(lambda x: x.is_alive(), threads)):
            time.sleep(0.1)
            n_print += 1
            if n_print == 5:
                n_running = len(list(filter(lambda x: x.is_alive(), threads)))
                cls.stdout(f"Checking {n_running} URIs")
                n_print = 0
        cls.stdout("Checking URIs done")

        return report_messages

    ############
    # Checkers #
    ############

    @classmethod
    def _check_symbol_field_empty(cls, symbol_data, field_name, report_messages):
        caller = f"({cls.__name__}._check_symbol_field_empty)"
        is_empty = symbol_data[field_name] == ""
        is_part = cls._is_part(symbol_data)

        # Mandatory fields
        # is part and part fields
        should_have_value = (
            (field_name in cls.MANDATORY_FIELDS) or
            (is_part and field_name in cls.PART_FIELDS)
        )

        # Optional fields for no parts, can be empty or not
        if not is_part and field_name in cls.OPTIONAL_FIELDS_NON_PARTS:
            should_have_value = not is_empty

        if is_empty and should_have_value:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"field '{field_name}' is empty {caller}"
            })
        if not is_empty and not should_have_value:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"field '{field_name}' is not empty {caller}"
            })

    @classmethod
    def _check_reference(cls, symbol_data, report_messages):
        caller = f"({cls.__name__}._check_reference)"
        is_correct = False
        # Regular stuff
        for check in cls.REFERENCES:
            if ((symbol_data["Name"] == check or symbol_data["Name"].startswith(f"{check}_")) and
                    symbol_data["Reference"] == cls.REFERENCES[check]):
                is_correct = True
        if not is_correct:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"incorrect reference '{symbol_data["Reference"]}' {caller}"
            })

    @classmethod
    def _check_revision(cls, symbol_data, report_messages):
        caller = f"({cls.__name__}._check_revision)"
        try:
            revision = int(symbol_data["Revision"])
            if revision < 1:
                report_messages.append({
                    "item":    symbol_data["Name"],
                    "message": f"the revision must be greater than zero {caller}"
                })
        except (TypeError, ValueError):
            report_messages.append({
                "item": symbol_data["Name"],
                "message": "the revision must be numeric"
            })

    @classmethod
    def _check_value(cls, symbol_data, report_messages):
        caller = f"({cls.__name__}._check_value)"
        value = symbol_data["Value"].lower()
        if value == "tp":
            value = "test_point"
        if "/" in value:
            value = value.replace("/", "_")

        if value not in symbol_data["Name"].lower():
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"value '{symbol_data["Value"]}' is not correct {caller}"
            })

    @classmethod
    def _check_footprint(cls, symbol_data, report_messages):
        caller = f"({cls.__name__}._check_footprint)"
        parts = symbol_data["Footprint"].split(":")
        if len(parts) != 2:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"footprint invalid"
            })
        else:
            if parts[0] != "lily_footprints":
                report_messages.append({
                    "item": symbol_data["Name"],
                    "message": f"invalid footprint library '{parts[0]}' {caller}"
                })
            else:
                footprint_file = os.path.join(AppData.APP_PATH, f"{parts[0]}.pretty", f"{parts[1]}.kicad_mod")
                if not os.path.isfile(footprint_file):
                    report_messages.append({
                        "item": symbol_data["Name"],
                        "message": f"footprint '{symbol_data["Footprint"]}' does not exist {caller}"
                    })

    @classmethod
    def _check_datasheet(cls, symbol_data, report_messages, threads):
        caller = f"({cls.__name__}._check_datasheet)"
        datasheet = symbol_data["Datasheet"]
        base_uri = "https://lilytronics.github.io/lily_kicad_lib/datasheets/"
        file_path = datasheet.replace(base_uri, f"{AppData.APP_PATH}/docs/datasheets/")
        if not os.path.isfile(file_path):
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"The datasheet file does not exist {file_path} {caller}"
            })
        elif not datasheet.startswith(base_uri):
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"Invalid datasheet URI {datasheet} {caller}"
            })
        else:
            t = threading.Thread(target=cls._check_datasheet_uri,
                                    args=(symbol_data["Name"], datasheet, report_messages))
            t.daemon = True
            t.start()
            threads.append(t)

    ###########
    # Helpers #
    ###########

    @staticmethod
    def _is_part(symbol_data):
        # Has extends
        # Is not a mechanical
        # Is not a test point
        return (
            (symbol_data["Extends"] != "") and
            (not symbol_data["Name"].startswith("mec_")) and
            (not symbol_data["Name"].startswith("test_point_"))
        )

    @classmethod
    def _check_datasheet_uri(cls, symbol_name, uri, report_messages):
        caller = f"({cls.__name__}._check_datasheet)"
        try:
            with urllib.request.urlopen(uri) as response:
                assert response.status == 200
        except (Exception,):
            report_messages.append({
                "item": symbol_name,
                "message": f"Datasheet URI not available {uri} {caller}"
            })


if __name__ == "__main__":

    from toolbox.models.show_messages import show_messages

    show_messages(SymbolsChecker.run())
