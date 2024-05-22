"""
Checks the library and report the errors
"""

import os

from lib_parser import LibParser


#############
# Log error #
#############

def _log_error(identifier, message):
    print(f"{identifier}: {message}")


#################
# Symbol checks #
#################

def _check_reference(symbol_data):
    is_correct = False
    checks = (
        ("cap",        "cap_",        "C"),
        ("con",        "con_",        "X"),
        ("crystal",    "crystal_",    "X"),
        ("dio",        "dio_",        "D"),
        ("ic",         "ic_",         "U"),
        ("ind",        "ind_",        "L"),
        ("mosfet",     "mosfet_",     "Q"),
        ("res",        "res_",        "R"),
        ("test_point", "test_point_", "TP")
    )
    power_symbols = ("GND", "Earth", "GNDA")
    # Regular stuff
    for check in checks:
        if ((symbol_data["Name"] == check[0] or symbol_data["Name"].startswith(check[1])) and
                symbol_data["Reference"] == check[2]):
            is_correct = True
    # Special stuff
    if symbol_data["Name"] in power_symbols and symbol_data["Reference"] == "#PWR":
        is_correct = True
    if not is_correct:
        _log_error(symbol_data["Name"], "incorrect reference")


def _check_symbol_field_empty(symbol_data, field_name):
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
            if (symbol_data["Extends"] == "" or
                    (symbol_data["Value"] == "dnp" and field_name != "Footprint") or
                    (symbol_data["Name"].startswith("test_point_") and field_name != "Footprint")):
                # Generic symbols
                is_not_empty = symbol_data[field_name] != ""
            else:
                # Parts
                is_empty = symbol_data[field_name] == ""
        if not field_checked:
            _log_error(symbol_data["Name"], f"no empty check for this field '{field_name}'")
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
    print(f"Checking {len(symbols)} symbols")
    for symbol in symbols:
        try:
            revision = int(symbol["Revision"])
            if revision < 1:
                _log_error(symbol["Name"], "the revision must be greater than zero")
        except (TypeError, ValueError):
            _log_error(symbol["Name"], "the revision must be numeric")
        if symbol["Extends"] == "":
            if symbol["Name"] != symbol["Value"]:
                _log_error(symbol["Name"], "the value is not the same as the name")
        _check_reference(symbol)
        for field in symbol:
            _check_symbol_field_empty(symbol, field)
        if symbol["Footprint"] != "":
            _check_footprint(symbol)


####################
# Footprint checks #
####################

def _check_footprint_field_empty(footprint_data, field_name):
    # Ignore fields that are allowed to be empty or have already been checked
    if field_name not in ["Name", "Datasheet", "Description", "Footprint", "Revision", "Attributes", "Reference_F.Fab"]:
        field_checked = False
        is_empty = False
        is_not_empty = False
        value = footprint_data[field_name]
        if isinstance(value, dict):
            value = value["Value"]
        # Always must contain a value
        if field_name in ["Reference", "Value"]:
            field_checked = True
            is_empty = value == ""
        elif field_name == "Model":
            field_checked = True
            # Some footprints must not have a 3D model
            if (footprint_data["Name"].endswith("_dnp") or
                    footprint_data["Name"].startswith("test_point_") or
                    footprint_data["Name"].startswith("fiducial_") or
                    footprint_data["Name"].startswith("logo_") or
                    footprint_data["Name"].startswith("mec_hole") or
                    footprint_data["Name"].startswith("mec_mouse_bytes")):
                is_not_empty = value != ""
            else:
                is_empty = value == ""
        if not field_checked:
            _log_error(footprint_data["Name"], f"no empty check for this field '{field_name}'")
        if is_empty:
            _log_error(footprint_data["Name"], f"field '{field_name}' is empty")
        if is_not_empty:
            _log_error(footprint_data["Name"], f"field '{field_name}' is not empty")


def _check_footprint_field_properties(footprint_data, field_name):
    # Check layer, size, thickness of the field
    if field_name not in ["Name", "Model"]:
        if isinstance(footprint_data[field_name], dict):
            field_checked = [False, False]

            # field_checked[0]: visibility
            expect_visible = field_name in ["Reference", "Reference_F.Fab"]
            if (footprint_data["Name"].startswith("fiducial_") or
                    footprint_data["Name"].startswith("logo_") or
                    footprint_data["Name"].startswith("mec_")):
                expect_visible = False
            if footprint_data["Name"].startswith("test_point") and field_name == "Value":
                expect_visible = True
            field_checked[0] = True
            if not footprint_data[field_name]["Visible"] and expect_visible:
                _log_error(footprint_data["Name"], f"field '{field_name}' is not visible")
            if footprint_data[field_name]["Visible"] and not expect_visible:
                _log_error(footprint_data["Name"], f"field '{field_name}' should not be visible")

            property_to_checks = {
                # Field name: (layer, size, thickness)
                "Reference": ("F.SilkS", "1 1", "0.15"),
                "Value": ("F.Fab", "0.5 0.5", "0.1"),
                "Footprint": ("F.Fab", "1.27 1.27", ""),
                "Datasheet": ("F.Fab", "1.27 1.27", ""),
                "Description": ("F.Fab", "1.27 1.27", ""),
                "Revision": ("F.Fab", "0.5 0.5", "0.1"),
                "Reference_F.Fab": ("F.Fab", "0.5 0.5", "0.1"),
            }
            if footprint_data["Name"].startswith("test_point_"):
                property_to_checks["Value"] = ("F.SilkS", "1 1", "0.15")
            if field_name in property_to_checks:
                field_checked[1] = True
                # Layer
                if footprint_data[field_name]["Layer"] != property_to_checks[field_name][0]:
                    _log_error(footprint_data["Name"],
                               f"field '{field_name}' should be on layer {property_to_checks[field_name][0]}")
                # Size
                if footprint_data[field_name]["Size"] != property_to_checks[field_name][1]:
                    _log_error(footprint_data["Name"],
                               f"field '{field_name}' size should be {property_to_checks[field_name][1]}")
                # Thickness
                if footprint_data[field_name]["Thickness"] != property_to_checks[field_name][2]:
                    _log_error(footprint_data["Name"],
                               f"field '{field_name}' thickness should be {property_to_checks[field_name][2]}")

            if False in field_checked:
                _log_error(footprint_data["Name"], f"not all checks implemented for this field '{field_name}'")


def _check_footprint_attributes(footprint_data):
    # Default we expect no attributes to be enabled
    expected_attributes = {
        "board_only": [False, "not in schematic"],
        "exclude_from_pos_files": [False, "exclude from position files"],
        "exclude_from_bom": [False, "exclude from bill of materials"],
        "allow_missing_courtyard": [False, "exempt from courtyard requirement"],
        "dnp": [False, "do not populate"]
    }

    if "through_hole" in footprint_data["Attributes"]:
        expected_attributes["exclude_from_pos_files"][0] = True
    if footprint_data["Name"].endswith("_dnp"):
        expected_attributes["exclude_from_pos_files"][0] = True
        expected_attributes["exclude_from_bom"][0] = True
        expected_attributes["dnp"][0] = True
    if footprint_data["Name"].startswith("fiducial_"):
        expected_attributes["board_only"][0] = True
        expected_attributes["exclude_from_bom"][0] = True
    if footprint_data["Name"].startswith("logo_"):
        expected_attributes["board_only"][0] = True
        expected_attributes["exclude_from_pos_files"][0] = True
        expected_attributes["exclude_from_bom"][0] = True
        expected_attributes["allow_missing_courtyard"][0] = True
    if footprint_data["Name"].startswith("mec_"):
        expected_attributes["board_only"][0] = True
        expected_attributes["exclude_from_pos_files"][0] = True
        expected_attributes["exclude_from_bom"][0] = True
    if footprint_data["Name"].startswith("test_point_"):
        expected_attributes["exclude_from_pos_files"][0] = True
        expected_attributes["exclude_from_bom"][0] = True

    for attribute in expected_attributes:
        if attribute in footprint_data["Attributes"] and not expected_attributes[attribute][0]:
            _log_error(footprint_data["Name"], f"attribute {expected_attributes[attribute][1]} should not be enabled")
        elif attribute not in footprint_data["Attributes"] and expected_attributes[attribute][0]:
            _log_error(footprint_data["Name"], f"attribute {expected_attributes[attribute][1]} should be enabled")


def _check_3d_model(footprint_data):
    expect_3d_model = (
        not footprint_data["Name"].endswith("_dnp") and
        not footprint_data["Name"].startswith("fiducial_") and
        not footprint_data["Name"].startswith("logo_") and
        not footprint_data["Name"].startswith("mec_hole") and
        not footprint_data["Name"].startswith("mec_mouse_bytes") and
        not footprint_data["Name"].startswith("test_point_")
    )
    if expect_3d_model and footprint_data["Model"] == "":
        _log_error(footprint_data["Name"], f"no 3D model defined")
    if not expect_3d_model and footprint_data["Model"] != "":
        _log_error(footprint_data["Name"], f"3D model should not be defined")
    if footprint_data["Model"] != "" and not os.path.isfile(footprint_data["Model"]):
        _log_error(footprint_data["Name"], f"3D model file does not exists")


def check_footprints():
    footprints = LibParser.get_footprints()
    print(f"Checking {len(footprints)} footprints")
    for footprint in footprints:
        try:
            revision = int(footprint["Revision"]["Value"])
            if revision < 1:
                _log_error(footprint["Name"], "the revision must be greater than zero")
        except (TypeError, ValueError):
            _log_error(footprint["Name"], "the revision must be numeric")

        for field in footprint:
            _check_footprint_field_empty(footprint, field)
            _check_footprint_field_properties(footprint, field)

        if footprint["Name"] != footprint["Value"]["Value"]:
            _log_error(footprint["Name"], "the name is not the same as the value")

        if footprint["Reference"]["Value"] != "REF**":
            _log_error(footprint["Name"], "the reference value must be 'REF**'")

        _check_footprint_attributes(footprint)
        _check_3d_model(footprint)


if __name__ == "__main__":

    check_symbols()
    check_footprints()
