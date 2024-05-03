"""
Checks the library and report the errors
"""

import os

from lib_parser import LibParser


def _log_error(identifier, message):
    print(f"{identifier}: {message}")


def _check_reference(symbol_data):
    is_correct = False
    if ((symbol_data["Name"] == "cap" or symbol_data["Name"].startswith("cap_")) and
            symbol_data["Reference"] == "C"):
        is_correct = True
    if ((symbol_data["Name"] == "dio" or symbol_data["Name"].startswith("dio_")) and
            symbol_data["Reference"] == "D"):
        is_correct = True
    if ((symbol_data["Name"] == "ic" or symbol_data["Name"].startswith("ic_")) and
            symbol_data["Reference"] == "U"):
        is_correct = True
    if ((symbol_data["Name"] == "ind" or symbol_data["Name"].startswith("ind_")) and
            symbol_data["Reference"] == "L"):
        is_correct = True
    if ((symbol_data["Name"] == "mosfet" or symbol_data["Name"].startswith("mosfet_")) and
            symbol_data["Reference"] == "Q"):
        is_correct = True
    if ((symbol_data["Name"] == "res" or symbol_data["Name"].startswith("res_")) and
            symbol_data["Reference"] == "R"):
        is_correct = True
    if ((symbol_data["Name"] == "con" or symbol_data["Name"].startswith("con_")) and
            symbol_data["Reference"] == "X"):
        is_correct = True
    if not is_correct:
        _log_error(symbol_data["Name"], "incorrect reference")


def _check_empty_field(symbol_data, field_name):
    # Ignore fields that are allowed to be empty or have already been checked
    if field_name not in ["Name", "Datasheet", "Description", "Reference", "Revision", "Notes", "Extends"]:
        field_checked = False
        is_empty = False
        is_not_empty = False
        if field_name == "Value":
            field_checked = True
            is_empty = symbol_data[field_name] == ""
        elif field_name in ["Footprint", "Status", "Manufacturer", "Manufacturer_ID",
                          "Lily_ID", "JLCPCB_ID", "JLCPCB_STATUS"]:
            field_checked = True
            if symbol_data["Extends"] == "" or (symbol_data["Value"] == "dnp" and field_name != "Footprint"):
                # Generic symbols
                is_not_empty = symbol_data[field_name] != ""
            else:
                # Parts
                is_empty = symbol_data[field_name] == ""
        if not field_checked:
            _log_error(symbol_data["Name"], f"no is empty check for this field '{field_name}'")
        if is_empty:
            _log_error(symbol_data["Name"], f"field '{field_name}' is empty")
        if is_not_empty:
            _log_error(symbol_data["Name"], f"field '{field_name}' is not empty")


def _check_footprint(symbol_data):
    parts = symbol_data["Footprint"].split(":")
    if len(parts) != 2:
        _log_error(symbol_data["Name"], f"footprint invalid")
    else:
        if parts[0] != "lily_footprints":
            _log_error(symbol_data["Name"], f"invalid footprint library")
        else:
            script_path = os.path.dirname(__file__)
            footprint_file = os.path.abspath(
                os.path.join(script_path, "..", f"{parts[0]}.pretty", f"{parts[1]}.kicad_mod"))
            if not os.path.isfile(footprint_file):
                _log_error(symbol_data["Name"], f"footprint does not exist")


def check_symbols():
    symbols = LibParser.get_symbols()
    for symbol in symbols:
        try:
            revision = int(symbol["Revision"])
            if revision < 1:
                _log_error(symbol["Name"], "the revision must be greater than zero")
        except ValueError:
            _log_error(symbol["Name"], "the revision must be numeric")
        if symbol["Extends"] == "":
            if symbol["Name"] != symbol["Value"]:
                _log_error(symbol["Name"], "the value is not the same as the name")
        _check_reference(symbol)
        for field in symbol:
            _check_empty_field(symbol, field)
        if symbol["Footprint"] != "":
            _check_footprint(symbol)


if __name__ == "__main__":

    check_symbols()
