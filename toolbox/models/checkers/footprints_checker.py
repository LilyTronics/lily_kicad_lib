"""
Class that checks the footprints.
"""

import copy
import os

from toolbox.app_data import AppData
from toolbox.models.parsers.lib_parser import LibParser


class FootprintsChecker:

    stdout = print

    MANDATORY_FIELDS = ["Name", "Reference", "Reference_F.Fab", "Revision", "Value"]
    OPTIONAL_FIELDS = ["Attributes", "Datasheet", "Description", "Footprint", "Model", "Pin_1_mark"]
    ATTRIBUTES = {
        "board_only": [False, "not in schematic"],
        "exclude_from_pos_files": [False, "exclude from position files"],
        "exclude_from_bom": [False, "exclude from bill of materials"],
        "allow_missing_courtyard": [False, "exempt from courtyard requirement"],
        "dnp": [False, "do not populate"]
    }
    FIELD_PROPERTIES = {
        # Field name: (layer, size, thickness)
        "Reference":        {"Layer": "F.SilkS", "Size": "0.8 0.8",   "Thickness": "0.16", "Visible": True},
        "Reference_F.Fab":  {"Layer": "F.Fab",   "Size": "0.5 0.5",   "Thickness": "0.1",  "Visible": True},
        "Pin_1_mark":       {"Layer": "F.SilkS", "Size": "0.8 0.8",   "Thickness": "0.16", "Visible": True},
        "Value":            {"Layer": "F.Fab",   "Size": "0.5 0.5",   "Thickness": "0.1",  "Visible": False},
        "Datasheet":        {"Layer": "F.Fab",   "Size": "1.27 1.27", "Thickness": "0.15", "Visible": False},
        "Description":      {"Layer": "F.Fab",   "Size": "1.27 1.27", "Thickness": "0.15", "Visible": False},
        "Revision":         {"Layer": "F.Fab",   "Size": "0.5 0.5",   "Thickness": "0.1",  "Visible": False}
    }
    SKIP_PROPERTIES_FIELDS = ["Name", "Attributes", "Footprint", "Model"]
    NO_3D_MODEL = ["0_new_footprint", "doc_idc_area_", "doc_logo_", "fiducial_", "mec_hole_", "mec_mouse_bytes",
                   "test_point_"]
    NO_IMAGE = ["0_new_footprint", "con_coax_rg_174_cable_to_pcb_", "con_spring_probe_pad", "doc_", "fiducial_",
                "mec_hole", "mec_mouse_bytes", "test_point_"]

    @classmethod
    def run(cls):
        cls.stdout("Check library footprints")
        report_messages = []
        footprints = LibParser.get_footprints()
        cls.stdout(f"Checking {len(footprints)} footprints")
        for footprint in footprints:
            for field in footprint:
                cls._check_footprint_field_empty(footprint, field, report_messages)
                cls._check_footprint_field_properties(footprint, field, report_messages)
            cls._check_footprint_reference(footprint, report_messages)
            cls._check_footprint_value(footprint, report_messages)
            cls._check_footprint_revision(footprint, show_messages)
            cls._check_footprint_attributes(footprint, report_messages)
            cls._check_3d_model(footprint, report_messages)
            cls._check_image(footprint, report_messages)
        return report_messages

    ############
    # Checkers #
    ############

    @classmethod
    def _check_footprint_field_empty(cls, footprint_data, field_name, report_messages):
        caller = f"({cls.__name__}._check_footprint_field_empty)"
        value = footprint_data[field_name]
        # Value can be string, dictionary or list
        if isinstance(value, dict):
            value = value["Value"]
        elif isinstance(value, list):
            value = "" if len(value) == 0 else str(value)
        is_empty = value == ""

        if field_name not in cls.MANDATORY_FIELDS and field_name not in cls.OPTIONAL_FIELDS:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"field '{field_name}' has no empty check {caller}"
            })

        # Mandatory fields
        should_have_value = (
            (field_name in cls.MANDATORY_FIELDS)
        )

        if field_name in cls.OPTIONAL_FIELDS:
            should_have_value = not is_empty

        if is_empty and should_have_value:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"field '{field_name}' is empty {caller}"
            })
        if not is_empty and not should_have_value:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"field '{field_name}' is not empty {caller}"
            })

    @classmethod
    def _check_footprint_field_properties(cls, footprint_data, field_name, report_messages):
        caller = f"({cls.__name__}._check_footprint_field_properties)"
        if field_name not in cls.FIELD_PROPERTIES and field_name not in cls.SKIP_PROPERTIES_FIELDS:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"no properties check for '{field_name}' {caller}"
            })

        if field_name in cls.FIELD_PROPERTIES:
            footprint_props = copy.deepcopy(footprint_data[field_name])
            if isinstance(footprint_props, dict):
                footprint_props.pop("Value")
                expected_props = copy.deepcopy(cls.FIELD_PROPERTIES[field_name])

                # Properties in the field, not in the expected properties
                diff = list(set(footprint_props.keys()) - set(expected_props.keys()))
                if len(diff) > 0:
                    report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"field '{field_name}' has properties that are not in properties to check: {", ".join(diff)} {caller}"
                    })
                # Properties in the expected properties, not in the field
                diff = list(set(expected_props.keys()) - set(footprint_props.keys()))
                if len(diff) > 0:
                    report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"field '{field_name}' is missing properties that are in properties to check: {", ".join(diff)} {caller}"
                    })

                # Some values depend on field and or footprint
                if field_name in ["Datasheet", "Description"]:
                    # Thickness not always defined (using default value)
                    if footprint_props["Thickness"] == "":
                        footprint_props["Thickness"] = expected_props["Thickness"]

                if field_name == "Reference" and (
                    footprint_data["Name"].startswith("doc_") or
                    footprint_data["Name"].startswith("fiducial_") or
                    footprint_data["Name"].startswith("mec_") or
                    footprint_data["Name"].startswith("test_point_")):
                    # For some footprints the reference is not visible
                    expected_props["Visible"] = False

                if field_name == "Value" and footprint_data["Name"].startswith("test_point_"):
                    # The value for test points have same properties as reference
                    expected_props = copy.deepcopy(cls.FIELD_PROPERTIES["Reference"])

                for prop in expected_props:
                    expected = expected_props[prop]
                    value = footprint_props[prop]
                    if value != expected:
                        report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"field '{field_name}' propert '{prop}' has invalid value '{value}' expected '{expected} {caller}"
                    })

            # Pin 1 mark is not mandatory
            elif (field_name != "Pin_1_mark"):
                    report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"no properties for '{field_name}' {caller}"
                })

    @classmethod
    def _check_footprint_reference(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_footprint_reference)"
        if footprint_data["Reference"]["Value"] != "REF**":
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"the reference value must be 'REF**' {caller}"
            })

    @classmethod
    def _check_footprint_value(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_footprint_value)"
        if footprint_data["Name"] != footprint_data["Value"]["Value"]:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"the name is not the same as the value{caller}"
            })

    @classmethod
    def _check_footprint_revision(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_footprint_revision)"
        try:
            revision = int(footprint_data["Revision"]["Value"])
            if revision < 1:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"the revision must be greater than zero {caller}"
                })
        except (TypeError, ValueError):
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"the revision must be numeric {caller}"
            })

    @classmethod
    def _check_footprint_attributes(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_footprint_attributes)"
        if footprint_data["Name"].startswith("doc_"):
            if "smd" in footprint_data["Attributes"] or "through_hole" in footprint_data["Attributes"]:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"footprint type must be unspecified {caller}"
                })
        else:
            if "smd" not in footprint_data["Attributes"] and "through_hole" not in footprint_data["Attributes"]:
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"footprint type must be SMD or through hole {caller}"
                })
        if footprint_data["Name"].endswith("_th") and "through_hole" not in footprint_data["Attributes"]:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"footprint should be set to through hole {caller}"
            })

        attributes = copy.deepcopy(cls.ATTRIBUTES)

        is_through_hole = "through_hole" in footprint_data["Attributes"]
        is_test_point = footprint_data["Name"].startswith("test_point_")
        is_mec_hole = footprint_data["Name"].startswith("mec_hole_")
        is_fiducial = footprint_data["Name"].startswith("fiducial_")
        is_mouse_bytes = footprint_data["Name"].startswith("mec_mouse_bytes")
        is_doc_footprint = footprint_data["Name"].startswith("doc_")
        is_footprint_only = (
            (footprint_data["Name"].startswith("con_tc2030_")) or
            ("cable_to_pcb" in footprint_data["Name"])
        )

        # Not in schematics
        attributes["board_only"][0] = is_mouse_bytes

        # Not in position files
        attributes["exclude_from_pos_files"][0] = (is_through_hole or is_test_point or is_doc_footprint or
                                                    is_footprint_only)

        # Not in BOM
        attributes["exclude_from_bom"][0] = (is_test_point or is_mec_hole or is_fiducial or is_mouse_bytes or
                                                is_doc_footprint or is_footprint_only)

        # Excempt from courtyard requirement
        attributes["allow_missing_courtyard"][0] = is_doc_footprint

        # Do not populate, no footprints using this attribute

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
        should_have_model = True
        has_model = footprint_data["Model"] != ""

        for query in cls.NO_3D_MODEL:
            if footprint_data["Name"].startswith(query):
                should_have_model = False

        if not has_model and should_have_model:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"no 3D model defined {caller}"
            })

        if has_model and not should_have_model:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"3D model should not be defined {caller}"
            })

        if has_model:
            if not footprint_data["Model"].startswith("../3d_models/"):
                report_messages.append({
                    "item": footprint_data["Name"],
                    "message": f"3D model folder must start with '../3d_models/' {caller}"
                })
            else:
                full_path = os.path.abspath(os.path.join(AppData.APP_PATH, "3d_models", footprint_data["Model"]))
                if not os.path.isfile(full_path):
                    report_messages.append({
                        "item": footprint_data["Name"],
                        "message": f"3D model file does not exists {footprint_data["Model"]} {caller}"
                    })

    @classmethod
    def _check_image(cls, footprint_data, report_messages):
        caller = f"({cls.__name__}._check_image)"
        should_have_image = True
        full_path = f"{os.path.join(AppData.APP_PATH, "lily_footprints.pretty", footprint_data["Name"])}.png"
        has_image = os.path.isfile(full_path)

        for query in cls.NO_IMAGE:
            if footprint_data["Name"].startswith(query):
                should_have_image = False

        if not has_image and should_have_image:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"no image file found {caller}"
            })

        if has_image and not should_have_image:
            report_messages.append({
                "item": footprint_data["Name"],
                "message": f"an image file is found while it should not be {caller}"
            })


if __name__ == "__main__":

    from toolbox.models.show_messages import show_messages

    show_messages(FootprintsChecker.run())
