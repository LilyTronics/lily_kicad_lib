"""
Class that checks the symbols
"""

import os
import re
import threading
import time
import urllib.request

from toolbox.app_data import AppData
from toolbox.models.lib_parser import LibParser


class SymbolsChecker:

    stdout = print

    REFERENCES = {
        "bjt":        "Q",
        "cap":        "C",
        "con":        "X",
        "crystal":    "X",
        "dio":        "D",
        "doc":        "DOC",
        "fuse":       "F",
        "ic":         "U",
        "ind":        "L",
        "logo":       "DOC",
        "mec":        "M",
        "mosfet":     "Q",
        "pot":        "P",
        "pptc":       "F",
        "relay":      "K",
        "res":        "R",
        "switch":     "S",
        "test_point": "TP"
    }
    SKIP_FIELDS = ("Name", "Datasheet", "Description", "Reference", "Revision", "Notes", "Extends")
    VALUE_FIELDS = ("Footprint", "Status", "Manufacturer", "Manufacturer_ID", "Lily_ID", "JLCPCB_ID")
    POWER_SYMBOLS = ("GND", "Earth", "GNDA", "Vxx")
    VALUE_QUERY = ["bjt_", "cap_", "con_", "crystal_", "dio_", "fuse_", "ic_", "ind_", "mosfet_", "res_", "pot_",
                   "mec_"]

    @classmethod
    def run(cls):
        threads = []
        LibParser.stdout = cls.stdout
        cls.stdout("Check library symbols")
        caller = f"({cls.__name__}.run)"
        report_messages = []
        symbols = LibParser.get_symbols()
        cls.stdout(f"Checking {len(symbols)} symbols")
        for symbol in symbols:
            try:
                revision = int(symbol["Revision"])
                if revision < 1:
                    report_messages.append({
                        "item":    symbol["Name"],
                        "message": f"the revision must be greater than zero {caller}"
                    })
            except (TypeError, ValueError):
                report_messages.append({
                    "item": symbol["Name"],
                    "message": "the revision must be numeric"
                })
            if symbol["Extends"] == "" and not symbol["Name"].startswith("test_point"):
                if symbol["Name"] != symbol["Value"]:
                    report_messages.append({
                        "item":    symbol["Name"],
                        "message": f"the value is not the same as the name {caller}"
                    })
            cls._check_reference(symbol, report_messages)
            for field in symbol:
                cls._check_symbol_field_empty(symbol, field, report_messages)
            cls._check_value(symbol, report_messages)
            if symbol["Footprint"] != "":
                cls._check_footprint(symbol, report_messages)
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

    @classmethod
    def _check_reference(cls, symbol_data, report_messages):
        caller = f"({cls.__name__}._check_reference)"
        is_correct = False
        # Regular stuff
        for check in cls.REFERENCES:
            if ((symbol_data["Name"] == check or symbol_data["Name"].startswith(f"{check}_")) and
                    symbol_data["Reference"] == cls.REFERENCES[check]):
                is_correct = True
        # Special stuff
        if symbol_data["Name"] in cls.POWER_SYMBOLS and symbol_data["Reference"] == "#PWR":
            is_correct = True
        if not is_correct:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"incorrect reference {caller}"
            })

    @classmethod
    def _check_symbol_field_empty(cls, symbol_data, field_name, report_messages):
        caller = f"({cls.__name__}._check_symbol_field_empty)"
        # Skip special symbols
        no_check = (
            # Cable to PCB connectors, footprint only, no physical component
            (symbol_data["Name"].startswith("con_") and "cable_to_pcb" in symbol_data["Name"]) or
            # Programming cable TC2030, footprint only no physical component
            symbol_data["Name"].startswith("con_TC2030") or
            # Mechanical holes
            symbol_data["Name"].startswith("mec_hole_") or
            # Fiducials
            symbol_data["Name"].startswith("mec_fiducial_")
        )
        # Ignore fields that are allowed to be empty or already have been checked
        if field_name not in cls.SKIP_FIELDS and not no_check:
            field_checked = False
            is_empty = False
            is_not_empty = False
            if field_name == "Value":
                field_checked = True
                is_empty = symbol_data[field_name] == ""
            elif field_name in cls.VALUE_FIELDS:
                field_checked = True
                if ((symbol_data["Name"].startswith("logo_") or symbol_data["Name"].startswith("doc_")) and
                        field_name == "Footprint"):
                    is_empty = symbol_data[field_name] == ""
                elif (symbol_data["Extends"] == "" or
                        (symbol_data["Value"] == "dnp" and field_name != "Footprint") or
                        (symbol_data["Name"].startswith("test_point_") and field_name != "Footprint")):
                    # Generic symbols
                    is_not_empty = symbol_data[field_name] != ""
                else:
                    # Parts
                    is_empty = symbol_data[field_name] == ""
            if not field_checked:
                report_messages.append({
                    "item":    symbol_data["Name"],
                    "message": f"no empty check for this field '{field_name}' {caller}"
                })
            if is_empty:
                report_messages.append({
                    "item": symbol_data["Name"],
                    "message": f"field '{field_name}' is empty {caller}"
                })
            if is_not_empty:
                report_messages.append({
                    "item": symbol_data["Name"],
                    "message": f"field '{field_name}' is not empty {caller}"
                })

    @classmethod
    def _check_value(cls, symbol_data, report_messages):
        caller = f"({cls.__name__}._check_value)"
        expected_value = symbol_data["Name"]
        if "_do_not_populate" in symbol_data["Name"]:
            expected_value = "dnp"
        elif symbol_data["Name"].startswith("test_point_"):
            expected_value = "test_point"
        else:
            for query in cls.VALUE_QUERY:
                if symbol_data["Name"].startswith(query):
                    # Replace spaces and '/' by underscore
                    value = f"_{re.sub(r'[ /]', '_', symbol_data["Value"])}"
                    if value in symbol_data["Name"]:
                        expected_value = symbol_data["Value"]
                    break
            for query in ("ind_bead_", "ind_common_mode_"):
                if symbol_data["Name"].startswith(query):
                    parts = symbol_data["Value"].split("/")
                    for part in parts:
                        if f"_{part}@100MHz_" in symbol_data["Name"] or f"_{part}_" in symbol_data["Name"]:
                            expected_value = symbol_data["Value"]
                            break

        if symbol_data["Value"] != expected_value:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": f"value '{symbol_data["Value"]}' is not correct, expected '{expected_value}' {caller}"
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
        if datasheet == "":
            # Parts must have a datasheet
            if symbol_data["Extends"] != "":
                # Except test point, dnp, mechanical, specials
                if (not symbol_data["Name"].startswith("test_point_") and
                        "_do_not_populate_" not in symbol_data["Name"] and
                        not symbol_data["Name"].startswith("mec_hole_") and
                        not symbol_data["Name"].startswith("mec_fiducial_") and
                        "_cable_to_pcb_" not in symbol_data["Name"]):
                    report_messages.append({
                        "item": symbol_data["Name"],
                        "message": f"No datasheet linked {caller}"
                    })
        else:
            # Datasheet not empty, check file and URI
            base_uri = "https://lilytronics.github.io/lily_kicad_lib/datasheets/"
            file_path = datasheet.replace(base_uri, f"{AppData.APP_PATH}/docs/datasheets/")
            if not os.path.isfile(file_path):
                report_messages.append({
                    "item": symbol_data["Name"],
                    "message": f"The datasheet file does not exist {file_path} {caller}"
                })
            elif not datasheet.startswith("https://lilytronics.github.io/lily_kicad_lib/datasheets/"):
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

    from show_messages import show_messages

    show_messages(SymbolsChecker.run())
