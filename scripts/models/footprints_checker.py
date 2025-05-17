"""
Class that checks the footprints.
"""

import copy
import os

from scripts.models.lib_parser import LibParser


class FootprintsChecker:

    SCRIPT_PATH = os.path.dirname(__file__)
    SKIP_FIELDS = ("Name", "Datasheet", "Description", "Footprint", "Revision", "Attributes", "Reference_F.Fab")
    VALUE_FIELDS = ("Reference", "Value")
    SKIP_FIELDS_VISIBLE = ("Name", "Model")
    MUST_VISIBLE = ("Reference", "Reference_F.Fab")
    FIELD_PROPERTIES = {
        # Field name: (layer, size, thickness)
        "Reference": ("F.SilkS", "1 1", "0.15"),
        "Value": ("F.Fab", "0.5 0.5", "0.1"),
        "Footprint": ("F.Fab", "1.27 1.27", ""),
        "Datasheet": ("F.Fab", "1.27 1.27", ""),
        "Description": ("F.Fab", "1.27 1.27", ""),
        "Revision": ("F.Fab", "0.5 0.5", "0.1"),
        "Reference_F.Fab": ("F.Fab", "0.5 0.5", "0.1"),
    }
    ATTRIBUTES = {
        "board_only": [False, "not in schematic"],
        "exclude_from_pos_files": [False, "exclude from position files"],
        "exclude_from_bom": [False, "exclude from bill of materials"],
        "allow_missing_courtyard": [False, "exempt from courtyard requirement"],
        "dnp": [False, "do not populate"]
    }
    NO_3D_MODEL = ("_dnp", "fiducial_", "logo_", "mec_hole_", "mec_mouse_bytes", "test_point_",
                   "to_be_done")

    @classmethod
    def run(cls):
        caller = f"({cls.__name__}.run)"
        report_messages = []
        footprints = LibParser.get_footprints()
        print(f"Checking {len(footprints)} footprints")
        for footprint in footprints:
            try:
                revision = int(footprint["Revision"]["Value"])
                if revision < 1:
                    report_messages.append({
                        "item": footprint["Name"],
                        "message": f"the revision must be greater than zero {caller}"
                    })
            except (TypeError, ValueError):
                report_messages.append({
                    "item": footprint["Name"],
                    "message": f"the revision must be numeric {caller}"
                })
            for field in footprint:
                cls._check_footprint_field_empty(footprint, field, report_messages)
                cls._check_footprint_field_properties(footprint, field, report_messages)

            if footprint["Name"] != footprint["Value"]["Value"]:
                report_messages.append({
                    "item": footprint["Name"],
                    "message": f"the name is not the same as the value{caller}"
                })
            if footprint["Reference"]["Value"] != "REF**":
                report_messages.append({
                    "item": footprint["Name"],
                    "message": f"the reference value must be 'REF**' {caller}"
                })
            cls._check_footprint_attributes(footprint, report_messages)
            cls._check_3d_model(footprint, report_messages)
        return report_messages

    @classmethod
    def _check_footprint_field_empty(cls, footprint_data, field_name, report_messages):
        caller = f"({cls.__name__}._check_footprint_field_empty)"
        # Ignore fields that are allowed to be empty or have already been checked
        if field_name not in cls.SKIP_FIELDS:
            field_checked = False
            is_empty = False
            is_not_empty = False
            value = footprint_data[field_name]
            if isinstance(value, dict):
                value = value["Value"]
            # Always must contain a value
            if field_name in cls.VALUE_FIELDS:
                field_checked = True
                is_empty = value == ""
            # 3D model depends on the footprint type
            elif field_name == "Model":
                field_checked = True
                # Some footprints must not have a 3D model
                if (footprint_data["Name"].endswith("_dnp") or
                        footprint_data["Name"].startswith("test_point_") or
                        footprint_data["Name"].startswith("fiducial_") or
                        footprint_data["Name"].startswith("logo_") or
                        footprint_data["Name"].startswith("mec_hole") or
                        footprint_data["Name"].startswith("mec_mouse_bytes") or
                        footprint_data["Name"] == "to_be_done"):
                    is_not_empty = value != ""
                else:
                    is_empty = value == ""
            if not field_checked:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"no empty check for this field '{field_name}' {caller}"
                })
            if is_empty:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"field '{field_name}' is empty {caller}"
                })
            if is_not_empty:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"field '{field_name}' is not empty {caller}"
                })

    @classmethod
    def _check_footprint_field_properties(cls, footprint_data, field_name, report_messages):
        caller = f"({cls.__name__}._check_footprint_field_properties)"
        # Check layer, size, thickness of the field
        if field_name not in cls.SKIP_FIELDS_VISIBLE:
            if isinstance(footprint_data[field_name], dict):
                field_checked = [False, False]

                # field_checked[0]: visibility
                expect_visible = field_name in cls.MUST_VISIBLE
                if (footprint_data["Name"].startswith("fiducial_") or
                        footprint_data["Name"].startswith("logo_") or
                        footprint_data["Name"].startswith("mec_")):
                    expect_visible = False
                if footprint_data["Name"].startswith("test_point") and field_name == "Value":
                    expect_visible = True
                field_checked[0] = True
                if not footprint_data[field_name]["Visible"] and expect_visible:
                    report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"field '{field_name}' is not visible {caller}"
                    })
                if footprint_data[field_name]["Visible"] and not expect_visible:
                    report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"field '{field_name}' should not be visible {caller}"
                    })

                properties = copy.deepcopy(cls.FIELD_PROPERTIES)
                if footprint_data["Name"].startswith("test_point_"):
                    properties["Value"] = ("F.SilkS", "1 1", "0.15")
                if field_name in properties:
                    field_checked[1] = True
                    # Layer
                    if footprint_data[field_name]["Layer"] != properties[field_name][0]:
                        report_messages.append({
                            "item": footprint_data["Name"],
                            "message": f"field '{field_name}' should be on layer {properties[field_name][0]} {caller}"
                        })
                    # Size
                    if footprint_data[field_name]["Size"] != properties[field_name][1]:
                        report_messages.append({
                            "item": footprint_data["Name"],
                            "message": f"field '{field_name}' size should be {properties[field_name][1]} {caller}"
                        })
                    # Thickness
                    if footprint_data[field_name]["Thickness"] != properties[field_name][2]:
                        report_messages.append({
                            "item": footprint_data["Name"],
                            "message": f"field '{field_name}' thickness should be {properties[field_name][2]} {caller}"
                        })

                if False in field_checked:
                    report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"not all checks implemented for this field '{field_name}' {caller}"
                    })

    @classmethod
    def _check_footprint_attributes(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_footprint_attributes)"
        attributes = copy.deepcopy(cls.ATTRIBUTES)
        if "through_hole" in footprint_data["Attributes"]:
            attributes["exclude_from_pos_files"][0] = True
        if footprint_data["Name"].endswith("_dnp"):
            attributes["exclude_from_pos_files"][0] = True
            attributes["exclude_from_bom"][0] = True
            attributes["dnp"][0] = True
        if footprint_data["Name"].startswith("fiducial_"):
            attributes["board_only"][0] = True
            attributes["exclude_from_bom"][0] = True
        if footprint_data["Name"].startswith("logo_"):
            attributes["exclude_from_pos_files"][0] = True
            attributes["exclude_from_bom"][0] = True
            attributes["allow_missing_courtyard"][0] = True
        if footprint_data["Name"].startswith("mec_"):
            attributes["board_only"][0] = True
            attributes["exclude_from_pos_files"][0] = True
            attributes["exclude_from_bom"][0] = True
        if footprint_data["Name"].startswith("test_point_"):
            attributes["exclude_from_pos_files"][0] = True
            attributes["exclude_from_bom"][0] = True
        if footprint_data["Name"].startswith("con_") and "cable_to_pcb" in footprint_data["Name"]:
            attributes["exclude_from_bom"][0] = True
        if footprint_data["Name"] == "to_be_done":
            attributes["exclude_from_pos_files"][0] = True
            attributes["exclude_from_bom"][0] = True

        for attribute in attributes:
            if attribute in footprint_data["Attributes"] and not attributes[attribute][0]:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"attribute {attributes[attribute][1]} should not be enabled {caller}"
                })
            elif attribute not in footprint_data["Attributes"] and attributes[attribute][0]:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"attribute {attributes[attribute][1]} should be enabled {caller}"
                })

    @classmethod
    def _check_3d_model(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_3d_model)"
        expect_3d_model = True
        for query in cls.NO_3D_MODEL:
            if ((query.startswith("_") and footprint_data["Name"].endswith(query)) or
                    footprint_data["Name"].startswith(query)):
                expect_3d_model = False
                break

        if expect_3d_model and footprint_data["Model"] == "":
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"no 3D model defined {caller}"
            })
        if not expect_3d_model and footprint_data["Model"] != "":
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"3D model should not be defined {caller}"
            })
        if footprint_data["Model"] != "":
            full_path = os.path.abspath(os.path.join(cls.SCRIPT_PATH, "..", footprint_data["Model"]))
            if not os.path.isfile(full_path):
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"3D model file does not exists {footprint_data["Model"]} {caller}"
                })


if __name__ == "__main__":

    messages = FootprintsChecker.run()
    print(f"{len(messages)} messages")
    for message in messages:
        print(message)
