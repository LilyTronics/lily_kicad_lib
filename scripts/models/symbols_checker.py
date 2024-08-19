"""
Class that checks the symbols
"""

import os

from scripts.models.lib_parser import LibParser


class SymbolsChecker:

    REFERENCES = {
        "cap":        "C",
        "con":        "X",
        "crystal":    "X",
        "dio":        "D",
        "ic":         "U",
        "ind":        "L",
        "logo":       "DOC",
        "mosfet":     "Q",
        "pot":        "P",
        "pptc":       "F",
        "relay":      "K",
        "res":        "R",
        "test_point": "TP"
    }
    SKIP_FIELDS = ("Name", "Datasheet", "Description", "Reference", "Revision", "Notes", "Extends")
    VALUE_FIELDS = ("Footprint", "Status", "Manufacturer", "Manufacturer_ID", "Lily_ID", "JLCPCB_ID", "JLCPCB_STATUS")

    @classmethod
    def run(cls):
        report_messages = []
        symbols = LibParser.get_symbols()
        print(f"Checking {len(symbols)} symbols")
        for symbol in symbols:
            try:
                revision = int(symbol["Revision"])
                if revision < 1:
                    report_messages.append({
                        "item":    symbol["Name"],
                        "message": "the revision must be greater than zero"
                    })
            except (TypeError, ValueError):
                report_messages.append({
                    "item": symbol["Name"],
                    "message": "the revision must be numeric"
                })
            if symbol["Extends"] == "":
                if symbol["Name"] != symbol["Value"]:
                    report_messages.append({
                        "item":    symbol["Name"],
                        "message": "the value is not the same as the name"
                    })
            cls._check_reference(symbol, report_messages)
            for field in symbol:
                cls._check_symbol_field_empty(symbol, field, report_messages)
            cls._check_value(symbol, report_messages)
            if symbol["Footprint"] != "":
                cls._check_footprint(symbol, report_messages)
        return report_messages

    @classmethod
    def _check_reference(cls, symbol_data, report_messages):
        is_correct = False
        power_symbols = ("GND", "Earth", "GNDA")
        # Regular stuff
        for check in cls.REFERENCES:
            if ((symbol_data["Name"] == check or symbol_data["Name"].startswith(f"{check}_")) and
                    symbol_data["Reference"] == cls.REFERENCES[check]):
                is_correct = True
        # Special stuff
        if symbol_data["Name"] in power_symbols and symbol_data["Reference"] == "#PWR":
            is_correct = True
        if not is_correct:
            report_messages.append({
                "item": symbol_data["Name"],
                "message": "incorrect reference"
            })

    @classmethod
    def _check_symbol_field_empty(cls, symbol_data, field_name, report_messages):
        # Ignore fields that are allowed to be empty or already have been checked
        if field_name not in cls.SKIP_FIELDS:
            field_checked = False
            is_empty = False
            is_not_empty = False
            if field_name == "Value":
                field_checked = True
                is_empty = symbol_data[field_name] == ""
            elif field_name in cls.VALUE_FIELDS:
                field_checked = True
                if symbol_data["Name"].startswith("logo_") and field_name == "Footprint":
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
                    "message": f"no empty check for this field '{field_name}'"
                })
            if is_empty:
                report_messages.append({
                    "item": symbol_data["Name"],
                    "message": f"field '{field_name}' is empty"
                })
            if is_not_empty:
                report_messages.append({
                    "item": symbol_data["Name"],
                    "message": f"field '{field_name}' is not empty"
                })

    @classmethod
    def _check_value(cls, symbol_data, report_messages):
        expected_value = symbol_data["Name"]
        if "_do_not_populate" in symbol_data["Name"]:
            expected_value = "dnp"
        elif symbol_data["Name"].startswith("test_point_"):
            expected_value = "test_point"
        else:
            for query in ("cap_", "crystal_", "dio_", "ic_", "ind_", "mosfet_", "res_"):
                if symbol_data["Name"].startswith(query):
                    value = f"_{symbol_data["Value"].replace("/", "_")}_"
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
                "message": f"value '{symbol_data["Value"]}' is not correct, expected '{expected_value}'"
            })

    @classmethod
    def _check_footprint(cls, symbol_data, report_messages):
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
                    "message": f"invalid footprint library '{parts[0]}'"
                })
            else:
                script_path = os.path.dirname(__file__)
                footprint_file = os.path.abspath(
                    os.path.join(script_path, "..", "..", f"{parts[0]}.pretty", f"{parts[1]}.kicad_mod"))
                if not os.path.isfile(footprint_file):
                    report_messages.append({
                        "item": symbol_data["Name"],
                        "message": f"footprint does not exist"
                    })


if __name__ == "__main__":

    messages = SymbolsChecker.run()
    print(f"{len(messages)} messages")
    for message in messages:
        print(message)
